"""Fast runner: bots imported in-process, one table per task across all CPU cores.

What is faithful to the competition
- The engine, variant, seating, blinds, hand cap, payouts and ICM scoring are the real ones.
- Each decision is timed with `perf_counter_ns`. Time beyond `decision_ms` plus the 2 ms
  delivery allowance is taken from the seat's 100 ms time bank; when the bank cannot cover it
  the decision is a timeout: the passive action is played, memory is not updated, and the
  events are delivered again next turn (the engine's own rule).
- Memory is cut to `config.memory_bytes`; a wrong return type or an exception is a failure that
  plays the passive action and keeps the old memory, as the guest process does.
- A bot directory is imported once per worker process and one `Agent` instance answers every
  table in that worker, like the two shared copies in production. A bot that leaks state
  through globals will therefore see the same symptoms it would see on the platform.

What is not
- No pipe, no JSON encoding of the state: measured latency is lower than the host sees in
  strict mode (by roughly 0.1-0.4 ms per decision for large states). A bot that is near the
  limit here will time out there. Use `arena.strict` before trusting timing.
- All cores are busy, so latency has more jitter than on an idle machine. `--decision-ms 0`
  turns enforcement off (latency is still recorded) when only strategy is under test.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import traceback
from collections.abc import Callable, Iterable, Iterator
from multiprocessing import Pool
from pathlib import Path
from time import perf_counter, perf_counter_ns
from typing import Any

from poker_agent_protocol.game import Action, GameState
from poker_engine.scoring import table_places, table_points
from poker_engine.table import SitAndGo, TableRules
from poker_engine.variant import load_variant

from arena.outcome import (
    GRACE_MS,
    TableOutcome,
    bust_hands_from_log,
    make_rules,
    percentile,
    seat_outcomes,
)
from arena.plan import TableSpec, base_label

ERROR_CHARS = 600

# Worker-process state (set by _init). Bots are stateless, so sharing one Agent per bot across
# the worker's tables mirrors production, where two copies serve every table.
_AGENTS: dict[str, Any] = {}
_LOAD_ERRORS: dict[str, str] = {}
_RULES: TableRules | None = None
_VARIANT: Any = None
_ENFORCE = True
_KEEP_LOG = False
_KEEP_LATENCIES = False  # Only the in-process latency probe wants raw samples.


def load_agent(label: str, bot_dir: Path) -> Any:
    """Import `bot_dir/agent.py` under a private module name, with the bot's own directory on
    sys.path only while it imports, so bots with same-named helper modules do not collide."""
    before = set(sys.modules)
    sys.path.insert(0, str(bot_dir))
    try:
        spec = importlib.util.spec_from_file_location(f"arena_bot_{label}", bot_dir / "agent.py")
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(bot_dir))
        # Helper modules the bot imported stay referenced from its namespace; dropping them from
        # sys.modules lets the next bot import its own module of the same name.
        for name in set(sys.modules) - before:
            module_file = getattr(sys.modules.get(name), "__file__", None) or ""
            if module_file and Path(module_file).resolve().is_relative_to(bot_dir):
                if name != spec.name:
                    del sys.modules[name]
    return module.Agent()


def _init(bots: dict[str, str], rules: TableRules, enforce: bool, keep_log: bool) -> None:
    global _RULES, _VARIANT, _ENFORCE, _KEEP_LOG
    _RULES, _ENFORCE, _KEEP_LOG = rules, enforce, keep_log
    _VARIANT = load_variant(rules.variant)
    for label, path in bots.items():
        try:
            _AGENTS[label] = load_agent(label, Path(path))
        except BaseException:  # noqa: BLE001 - report, play passively, never kill the run.
            _LOAD_ERRORS[label] = traceback.format_exc()[-ERROR_CHARS:]


def _validated(result: Any) -> tuple[Action, bytes]:
    if not isinstance(result, tuple) or len(result) != 2:
        raise TypeError("act must return a pair: (action, memory).")
    action, memory = result
    if not isinstance(action, Action):
        raise TypeError(f"act must return an Action, not {type(action).__name__}.")
    if not isinstance(memory, bytes | bytearray | memoryview):
        raise TypeError(f"Memory must be bytes, not {type(memory).__name__}.")
    return action, bytes(memory)


def play_spec(spec: TableSpec) -> TableOutcome:
    """Play one table in this worker. Mirrors poker_engine.play._play plus the host's timing
    and memory rules from poker_agent_protocol.process / poker_agent_sdk.guest."""
    assert _RULES is not None
    rules = _RULES
    players = rules.players
    started = perf_counter()
    table = SitAndGo(rules=rules, variant=_VARIANT, table_id=spec.table_id, seed=spec.seed)
    agents = [_AGENTS.get(base_label(copy)) for copy in spec.seats]
    memory = [b""] * players
    decisions = [0] * players
    failures = [0] * players
    timeouts = [0] * players
    errors = [0] * players
    illegal = [0] * players
    truncated = [0] * players
    mem_max = [0] * players
    latencies: list[list[float]] = [[] for _ in range(players)]
    bot_errors: list[str] = []
    reported: set[int] = set()
    free_ms = rules.decision_ms + GRACE_MS
    limit = rules.memory_bytes

    while (state := table.decision()) is not None:
        seat = state.seat
        decisions[seat] += 1
        agent = agents[seat]
        action: Action | None = None
        answered = False
        bank_ms = 0.0
        if agent is None:
            errors[seat] += 1
        else:
            t0 = perf_counter_ns()
            try:
                result = agent.act(state, memory[seat])
                elapsed = (perf_counter_ns() - t0) / 1e6
                action, new_memory = _validated(result)
            except BaseException as error:  # noqa: BLE001 - a bot's failure is its own.
                elapsed = (perf_counter_ns() - t0) / 1e6
                latencies[seat].append(elapsed)
                errors[seat] += 1
                if seat not in reported:
                    reported.add(seat)
                    bot_errors.append(
                        f"{spec.seats[seat]} hand {state.hand_number}: "
                        + "".join(traceback.format_exception(error))[-ERROR_CHARS:]
                    )
            else:
                latencies[seat].append(elapsed)
                over = max(0.0, elapsed - free_ms)
                if _ENFORCE and over > state.time_bank_ms:
                    # A late reply is ignored: passive action, memory unchanged, bank emptied.
                    timeouts[seat] += 1
                    bank_ms = state.time_bank_ms
                    action = None
                else:
                    bank_ms = min(state.time_bank_ms, over) if _ENFORCE else 0.0
                    answered = True
                    if len(new_memory) > limit:
                        truncated[seat] += 1
                        new_memory = new_memory[:limit]
                    memory[seat] = new_memory
                    mem_max[seat] = max(mem_max[seat], len(new_memory))
        legal = table.apply(action, answered=answered, bank_ms=bank_ms)
        if not legal:
            failures[seat] += 1
            if answered and action is not None:
                illegal[seat] += 1

    result = table.result(tuple(failures), tuple(decisions))
    points = table_points(result, table.payouts)
    places = table_places(result)
    bust_hands = bust_hands_from_log(table.log, players)
    for label, text in _LOAD_ERRORS.items():
        if any(base_label(copy) == label for copy in spec.seats):
            bot_errors.append(f"{label} could not load: {text}")
    return TableOutcome(
        table_id=spec.table_id,
        iteration=spec.iteration,
        number=spec.number,
        arm=spec.arm,
        seed=spec.seed,
        hands=result.hands_played,
        payouts=list(table.payouts),
        seats=seat_outcomes(
            spec,
            points=points,
            places=places,
            decisions=decisions,
            failures=failures,
            timeouts=timeouts,
            errors=errors,
            illegal=illegal,
            truncated=truncated,
            latencies=latencies,
            mem_max=mem_max,
            final_stacks=list(result.final_stacks),
            bust_hands=bust_hands,
        ),
        mode="fast",
        wall_ms=(perf_counter() - started) * 1000,
        bot_errors=bot_errors,
        log=table.log if _KEEP_LOG else None,
        latencies=latencies if _KEEP_LATENCIES else None,
    )


def default_workers() -> int:
    return max(1, (os.cpu_count() or 2) - 1)


def run(
    specs: Iterable[TableSpec],
    bots: dict[str, Path],
    *,
    rules: TableRules | None = None,
    workers: int | None = None,
    enforce_time: bool = True,
    keep_log: bool = False,
    progress: Callable[[int, int], None] | None = None,
) -> Iterator[TableOutcome]:
    """Play every spec, yielding outcomes as they finish (unordered)."""
    specs = list(specs)
    rules = rules or make_rules()
    workers = workers or default_workers()
    bot_paths = {label: str(path) for label, path in bots.items()}
    done = 0
    if workers <= 1:
        _init(bot_paths, rules, enforce_time, keep_log)
        for spec in specs:
            outcome = play_spec(spec)
            done += 1
            if progress:
                progress(done, len(specs))
            yield outcome
        return
    with Pool(
        min(workers, len(specs)), initializer=_init, initargs=(bot_paths, rules, enforce_time, keep_log)
    ) as pool:
        for outcome in pool.imap_unordered(play_spec, specs, chunksize=1):
            done += 1
            if progress:
                progress(done, len(specs))
            yield outcome


def latency_probe(bot: Path, *, tables: int = 4, seed: str = "probe") -> dict[str, Any]:
    """Per-decision latency of one bot in self-play, for `arena check`. Runs in this process,
    on an otherwise idle machine, so it is the bot's own cost, not scheduling noise."""
    from arena.plan import league_plan

    global _KEEP_LATENCIES
    rules = make_rules()
    plan = league_plan(["probe"], seed=seed, tables=tables, players=rules.players)
    all_latencies: list[float] = []
    mem = 0
    failures = 0
    decisions = 0
    _KEEP_LATENCIES = True
    try:
        for outcome in run(plan.tables, {"probe": bot}, rules=rules, workers=1, enforce_time=True):
            for seat in outcome.seats:
                failures += seat.failures
                decisions += seat.decisions
                mem = max(mem, seat.mem_max_bytes)
            for samples in outcome.latencies or []:
                all_latencies += samples
    finally:
        _KEEP_LATENCIES = False
    all_latencies.sort()
    return {
        "decisions": decisions,
        "failures": failures,
        "p50_ms": round(percentile(all_latencies, 0.5), 4),
        "p90_ms": round(percentile(all_latencies, 0.9), 4),
        "p99_ms": round(percentile(all_latencies, 0.99), 4),
        "max_ms": round(all_latencies[-1], 4) if all_latencies else 0.0,
        "over_1ms_share": round(sum(x > 1.0 for x in all_latencies) / max(1, len(all_latencies)), 4),
        "mem_max_bytes": mem,
    }
