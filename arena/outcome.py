"""What one played table produced, in a form both runners emit and every report reads."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from poker_engine.table import DEFAULT_BLINDS, TableRules

from arena.plan import TableSpec, base_label

VARIANT = "flop_discard_reveal"
GRACE_MS = 2.0  # BotProcess.grace_ms: delivery allowance beyond the decision limit.


def make_rules(
    *,
    players: int = 8,
    decision_ms: int = 1,
    time_bank_ms: int = 100,
    hand_cap: int = 250,
    random_payouts: bool = False,
    memory_bytes: int = 64 * 1024,
) -> TableRules:
    """The competition's table rules. `random_payouts` draws each table's split of 100 points
    from wide ranges (a stress test for `state.config.payouts` handling: the organizers may
    give tables their own split in some rounds; the real ranges are not published)."""
    payouts = ((20, 80), (10, 50), (1, 40)) if random_payouts else ((50, 50), (30, 30), (20, 20))
    return TableRules(
        variant=VARIANT,
        players=players,
        starting_stack=2000,
        blinds=DEFAULT_BLINDS,
        hands_per_level=20,
        hand_cap=hand_cap,
        payouts=payouts,
        payout_total=100 if random_payouts else None,
        decision_ms=max(1, decision_ms),
        time_bank_ms=time_bank_ms,
        memory_bytes=memory_bytes,
    )


@dataclass(slots=True)
class SeatOutcome:
    seat: int
    copy: str  # e.g. "tight#1"
    label: str  # base label, "tight"
    filler: bool
    points: float
    place: int
    decisions: int
    failures: int  # Timeouts + errors + illegal actions (what poker-agent play reports).
    timeouts: int = 0
    errors: int = 0
    illegal: int = 0
    truncated: int = 0  # Decisions whose memory was longer than the limit and got cut.
    lat_p50_ms: float | None = None  # Decision latency as the host measured it.
    lat_p99_ms: float | None = None
    lat_max_ms: float | None = None
    mem_max_bytes: int = 0
    bust_hand: int | None = None  # Hand number on which the seat busted, None if it survived.
    final_stack: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TableOutcome:
    table_id: str
    iteration: int
    number: int
    arm: str
    seed: str
    hands: int
    payouts: list[int]
    seats: list[SeatOutcome]
    mode: str  # "fast" or "strict"
    wall_ms: float = 0.0
    bot_errors: list[str] = field(default_factory=list)  # Tracebacks etc., untrusted text.
    log: list[dict[str, Any]] | None = None  # The engine's full hand log, when kept.
    latencies: list[list[float]] | None = None  # Raw per-seat samples; never serialized.

    def to_dict(self, *, with_log: bool = True) -> dict[str, Any]:
        data = {
            "table_id": self.table_id,
            "iteration": self.iteration,
            "number": self.number,
            "arm": self.arm,
            "seed": self.seed,
            "hands": self.hands,
            "payouts": self.payouts,
            "mode": self.mode,
            "wall_ms": round(self.wall_ms, 1),
            "bot_errors": self.bot_errors,
            "seats": [seat.to_dict() for seat in self.seats],
        }
        if with_log and self.log is not None:
            data["log"] = self.log
        return data

    @staticmethod
    def from_dict(data: dict[str, Any]) -> TableOutcome:
        return TableOutcome(
            table_id=data["table_id"],
            iteration=data["iteration"],
            number=data["number"],
            arm=data.get("arm", ""),
            seed=data["seed"],
            hands=data["hands"],
            payouts=list(data["payouts"]),
            seats=[SeatOutcome(**seat) for seat in data["seats"]],
            mode=data.get("mode", "?"),
            wall_ms=data.get("wall_ms", 0.0),
            bot_errors=list(data.get("bot_errors", [])),
            log=data.get("log"),
        )

    def raw_table(self, spec: TableSpec | None = None) -> dict[str, Any] | None:
        """The table in the organizers' log shape (every card, sealed choices), the input of
        `poker_engine.history.public_view` and of arena.history_stats."""
        if self.log is None:
            return None
        return {
            "variant": VARIANT,
            "iteration": self.iteration,
            "table": self.number,
            "arm": self.arm,
            "seats": [seat.copy for seat in self.seats],
            "labels": [seat.label for seat in self.seats],
            "fillers": [seat.filler for seat in self.seats],
            "payouts": self.payouts,
            "hands": self.log,
        }


def percentile(sorted_values: list[float], share: float) -> float:
    if not sorted_values:
        return 0.0
    index = min(len(sorted_values) - 1, max(0, round(share * (len(sorted_values) - 1))))
    return sorted_values[index]


def seat_outcomes(
    spec: TableSpec,
    *,
    points: list[float],
    places: list[int],
    decisions: list[int],
    failures: list[int],
    timeouts: list[int],
    errors: list[int],
    illegal: list[int],
    truncated: list[int],
    latencies: list[list[float]],
    mem_max: list[int],
    final_stacks: list[int],
    bust_hands: list[int | None],
) -> list[SeatOutcome]:
    out = []
    for seat, copy in enumerate(spec.seats):
        lat = sorted(latencies[seat])
        out.append(
            SeatOutcome(
                seat=seat,
                copy=copy,
                label=base_label(copy),
                filler=spec.fillers[seat],
                points=round(points[seat], 4),
                place=places[seat],
                decisions=decisions[seat],
                failures=failures[seat],
                timeouts=timeouts[seat],
                errors=errors[seat],
                illegal=illegal[seat],
                truncated=truncated[seat],
                lat_p50_ms=round(percentile(lat, 0.5), 4) if lat else None,
                lat_p99_ms=round(percentile(lat, 0.99), 4) if lat else None,
                lat_max_ms=round(lat[-1], 4) if lat else None,
                mem_max_bytes=mem_max[seat],
                bust_hand=bust_hands[seat],
                final_stack=final_stacks[seat],
            )
        )
    return out


def bust_hands_from_log(log: list[dict[str, Any]], players: int) -> list[int | None]:
    busts: list[int | None] = [None] * players
    for record in log:
        for seat, (before, after) in enumerate(
            zip(record["stacks_before"], record["stacks_after"], strict=True)
        ):
            if before > 0 and after == 0 and busts[seat] is None:
                busts[seat] = record["hand"]
    return busts
