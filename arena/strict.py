"""Strict runner: bots in separate processes through the SDK's BotPool, exactly as
`poker-agent play` and the competition host run them.

- Two shared copies per bot directory (`python -m poker_agent_sdk.guest DIR`), requests one at
  a time per copy, deadline measured by the host from sending the request to reading the
  reply: 1 ms + 2 ms delivery allowance + whatever is left of the 100 ms table bank.
- A bot that is late, crashes, or returns garbage plays the passive action; memory is cut to
  the table's limit by the guest.
- One event loop measures every deadline, so at most `concurrency` tables run at once (the
  CLI uses 8). Several shards in separate processes multiply throughput but add CPU
  contention; keep shards <= cores / 4 when timing matters.

Linux only (the SDK uses process groups and a POSIX environment). On Windows,
`python -m arena ... --mode strict` re-launches itself inside WSL with starter-kit/.venv-wsl.
"""

from __future__ import annotations

import asyncio
import contextvars
import os
import sys
from collections.abc import Callable, Iterable, Iterator
from multiprocessing import Pool
from pathlib import Path
from time import perf_counter
from typing import Any

from poker_agent_protocol.game import GameState
from poker_agent_protocol.process import BotPool
from poker_agent_protocol.runner import BotError, BotTimeout, Reply
from poker_engine.play import play_table
from poker_engine.scoring import table_places, table_points
from poker_engine.table import SitAndGo, TableRules
from poker_engine.variant import load_variant

from arena.outcome import TableOutcome, bust_hands_from_log, make_rules, seat_outcomes
from arena.plan import TableSpec, base_label


# The seat whose decision is in flight in the current asyncio task: the request timer below
# appends to its list. Waiting for a free copy or a process start is not decision time.
_CURRENT_SEAT: contextvars.ContextVar["TimedSeat | None"] = contextvars.ContextVar(
    "arena_seat", default=None
)


def instrument(pool: BotPool) -> None:
    """Record the host-measured time of every request (send -> reply read), the same number
    the SDK charges against the deadline, per seat."""
    for process in pool.processes:
        original = process._request

        async def timed(state: bytes, memory: bytes, *, budget_ms: float, _original=original) -> Any:
            seat = _CURRENT_SEAT.get()
            started = perf_counter()
            try:
                reply, new_memory, elapsed_ms = await _original(state, memory, budget_ms=budget_ms)
            except BaseException:
                if seat is not None:
                    seat.latencies.append((perf_counter() - started) * 1000)
                raise
            if seat is not None:
                seat.latencies.append(elapsed_ms)
            return reply, new_memory, elapsed_ms

        process._request = timed  # type: ignore[method-assign]


class TimedSeat:
    """A Bot for one seat that records what the host measured about each decision."""

    def __init__(self, pool: BotPool) -> None:
        self.pool = pool
        self.latencies: list[float] = []
        self.timeouts = 0
        self.errors = 0
        self.mem_max = 0

    async def act(self, state: GameState, memory: bytes) -> Reply:
        token = _CURRENT_SEAT.set(self)
        try:
            reply = await self.pool.act(state, memory)
        except BotTimeout:
            self.timeouts += 1
            raise
        except BotError:
            self.errors += 1
            raise
        finally:
            _CURRENT_SEAT.reset(token)
        self.mem_max = max(self.mem_max, len(reply.memory))
        return reply


async def play_spec(
    spec: TableSpec, pools: dict[str, BotPool], rules: TableRules, variant: Any, keep_log: bool
) -> TableOutcome:
    started = perf_counter()
    table = SitAndGo(rules=rules, variant=variant, table_id=spec.table_id, seed=spec.seed)
    seats = [TimedSeat(pools[base_label(copy)]) for copy in spec.seats]
    result = await play_table(table, seats)
    points = table_points(result, table.payouts)
    places = table_places(result)
    players = rules.players
    timeouts = [s.timeouts for s in seats]
    errors = [s.errors for s in seats]
    failures = list(result.failures)
    illegal = [max(0, f - t - e) for f, t, e in zip(failures, timeouts, errors, strict=True)]
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
            decisions=list(result.decisions),
            failures=failures,
            timeouts=timeouts,
            errors=errors,
            illegal=illegal,
            truncated=[0] * players,
            latencies=[s.latencies for s in seats],
            mem_max=[s.mem_max for s in seats],
            final_stacks=list(result.final_stacks),
            bust_hands=bust_hands_from_log(table.log, players),
        ),
        mode="strict",
        wall_ms=(perf_counter() - started) * 1000,
        log=table.log if keep_log else None,
    )


async def run_async(
    specs: list[TableSpec],
    bots: dict[str, Path],
    *,
    rules: TableRules,
    concurrency: int = 8,
    keep_log: bool = False,
    progress: Callable[[int, int], None] | None = None,
) -> list[TableOutcome]:
    variant = load_variant(rules.variant)
    pools = {
        label: BotPool(
            [sys.executable, "-m", "poker_agent_sdk.guest", str(path)], copies=2, cwd=str(path)
        )
        for label, path in bots.items()
    }
    for pool in pools.values():
        instrument(pool)
    running = asyncio.Semaphore(concurrency)
    outcomes: list[TableOutcome] = []

    async def one(spec: TableSpec) -> None:
        async with running:
            outcome = await play_spec(spec, pools, rules, variant, keep_log)
        outcomes.append(outcome)
        if progress:
            progress(len(outcomes), len(specs))

    tasks = [asyncio.create_task(one(spec)) for spec in specs]
    try:
        await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        for pool in pools.values():
            await pool.stop()
    # Bot stderr and the host's reasons for failures, attached to every table of that bot.
    notes: dict[str, list[str]] = {}
    for label, pool in pools.items():
        texts = []
        for process in getattr(pool, "processes", []):
            texts += process.take_errors()
            if process.logs:
                texts.append("stderr: " + process.logs.decode(errors="replace")[-600:])
        if texts:
            notes[label] = texts
    if notes:
        for outcome in outcomes:
            labels = {seat.label for seat in outcome.seats}
            outcome.bot_errors = [f"{label}: {t}" for label in labels for t in notes.get(label, [])]
    return outcomes


def _shard(args: tuple[list[TableSpec], dict[str, Path], TableRules, int, bool]) -> list[TableOutcome]:
    specs, bots, rules, concurrency, keep_log = args
    return asyncio.run(run_async(specs, bots, rules=rules, concurrency=concurrency, keep_log=keep_log))


def default_shards() -> int:
    return max(1, min(4, (os.cpu_count() or 4) // 4))


def run(
    specs: Iterable[TableSpec],
    bots: dict[str, Path],
    *,
    rules: TableRules | None = None,
    concurrency: int = 1,
    shards: int | None = None,
    keep_log: bool = False,
    progress: Callable[[int, int], None] | None = None,
) -> Iterator[TableOutcome]:
    """`concurrency` tables share one event loop (default 1: the loop is idle while a bot
    thinks, so the measured time is the bot's own plus pipe/JSON, as on the platform; the kit's
    `poker-agent play` uses 8 and its measurements include the engine's work for the other
    seven tables). `shards` independent processes multiply throughput."""
    if sys.platform == "win32":
        raise RuntimeError(
            "The strict runner needs Linux (WSL). Run `python -m arena ... --mode strict` and it "
            "will re-launch itself in WSL, or run it from WSL with starter-kit/.venv-wsl."
        )
    specs = list(specs)
    rules = rules or make_rules()
    shards = shards or default_shards()
    if shards <= 1 or len(specs) < 2:
        yield from asyncio.run(
            run_async(specs, bots, rules=rules, concurrency=concurrency, keep_log=keep_log, progress=progress)
        )
        return
    chunks = [specs[i::shards] for i in range(shards) if specs[i::shards]]
    done = 0
    with Pool(len(chunks)) as pool:
        for outcomes in pool.imap_unordered(
            _shard, [(chunk, bots, rules, concurrency, keep_log) for chunk in chunks]
        ):
            done += len(outcomes)
            if progress:
                progress(done, len(specs))
            yield from outcomes
