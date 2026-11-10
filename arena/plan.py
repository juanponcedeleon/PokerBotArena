"""Tournament plans: which bots sit at which table, with which seed.

A plan is a list of `TableSpec`s. Both runners (fast, strict) consume the same plans, so a
result from one can be reproduced in the other with the same seed. Seating uses the engine's
own `seat_iteration`, the function the competition uses to seat a round.

Schemes
-------
league   Every entry gets the same number of seats in every iteration. With n bots and p seats
         per table there are lcm(n, p)/p tables per iteration and each bot has lcm(n, p)/n
         seats in it, so nothing is a filler and every seat scores. A table can hold two seats
         of the same bot when n < p (self-play), exactly as `poker-agent play` does when a
         folder is repeated.
ab       A league plan with `hero` in the field, mirrored: in the "B" copy of every table the
         challenger sits in every seat the hero had. Tables are paired by (iteration, number)
         and share their seed, so cards, button and payouts are identical until the two bots'
         actions diverge. Paired differences cut variance by a large factor.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any

from poker_engine.seating import seat_iteration
from poker_engine.table import table_seed

PLAYERS = 8


def copy_label(label: str, index: int) -> str:
    return f"{label}#{index}"


def base_label(copy: str) -> str:
    return copy.rsplit("#", 1)[0]


def copy_index(copy: str) -> int:
    return int(copy.rsplit("#", 1)[1])


@dataclass(frozen=True, slots=True)
class TableSpec:
    iteration: int
    number: int
    seed: str
    seats: tuple[str, ...]  # Seat copies, e.g. "tight#0"; base_label() strips the copy.
    fillers: tuple[bool, ...]
    arm: str = ""  # "" for a plain table, "A"/"B" for the two sides of an A/B pair.

    @property
    def table_id(self) -> str:
        return f"{self.iteration}-{self.number}{self.arm}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> TableSpec:
        return TableSpec(
            data["iteration"],
            data["number"],
            data["seed"],
            tuple(data["seats"]),
            tuple(data["fillers"]),
            data.get("arm", ""),
        )


@dataclass(slots=True)
class Plan:
    scheme: str
    seed: str
    players: int
    labels: list[str]  # Base labels taking part.
    tables: list[TableSpec] = field(default_factory=list)
    hero: str | None = None
    challenger: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "scheme": self.scheme,
            "seed": self.seed,
            "players": self.players,
            "labels": self.labels,
            "hero": self.hero,
            "challenger": self.challenger,
            "tables": [t.to_dict() for t in self.tables],
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Plan:
        return Plan(
            data["scheme"],
            data["seed"],
            data["players"],
            list(data["labels"]),
            [TableSpec.from_dict(t) for t in data["tables"]],
            data.get("hero"),
            data.get("challenger"),
        )


def seat_copies(labels: list[str], players: int) -> list[str]:
    """Enough copies of each label that the field divides into full tables evenly."""
    if len(set(labels)) != len(labels):
        raise ValueError("Labels must be distinct.")
    if not labels:
        raise ValueError("Give at least one bot.")
    if len(labels) == 1:  # Self-play: one bot fills the whole table.
        return [copy_label(labels[0], i) for i in range(players)]
    total = math.lcm(len(labels), players)
    per_bot = total // len(labels)
    return [copy_label(label, i) for label in labels for i in range(per_bot)]


def league_tables(
    copies: list[str], *, seed: str, iteration: int, players: int, arm: str = ""
) -> list[TableSpec]:
    specs = []
    seating = seat_iteration(copies, seed=seed, iteration=iteration, table_size=players)
    for number, table in enumerate(seating):
        specs.append(
            TableSpec(
                iteration=iteration,
                number=number,
                seed=table_seed(seed, iteration, number),
                seats=tuple(seat.entry for seat in table),
                fillers=tuple(seat.filler for seat in table),
                arm=arm,
            )
        )
    return specs


def league_plan(labels: list[str], *, seed: str, tables: int, players: int = PLAYERS) -> Plan:
    """At least `tables` tables, in whole iterations."""
    copies = seat_copies(labels, players)
    per_iteration = len(copies) // players
    iterations = max(1, math.ceil(tables / per_iteration))
    plan = Plan("league", seed, players, list(labels))
    for iteration in range(iterations):
        plan.tables += league_tables(copies, seed=seed, iteration=iteration, players=players)
    return plan


def ab_plan(
    hero: str,
    challenger: str,
    field_labels: list[str],
    *,
    seed: str,
    tables: int,
    players: int = PLAYERS,
) -> Plan:
    """Paired tables: arm A has the hero in the field, arm B has the challenger in exactly the
    hero's seats. `tables` counts pairs. The challenger must not already be in the field."""
    if challenger in field_labels or challenger == hero:
        raise ValueError("The challenger replaces the hero, so it cannot also be in the field.")
    labels = [hero] + [label for label in field_labels if label != hero]
    base = league_plan(labels, seed=seed, tables=tables, players=players)
    plan = Plan("ab", seed, players, labels + [challenger], hero=hero, challenger=challenger)
    for spec in base.tables:
        plan.tables.append(
            TableSpec(spec.iteration, spec.number, spec.seed, spec.seats, spec.fillers, "A")
        )
        swapped = tuple(
            copy_label(challenger, copy_index(copy)) if base_label(copy) == hero else copy
            for copy in spec.seats
        )
        plan.tables.append(
            TableSpec(spec.iteration, spec.number, spec.seed, swapped, spec.fillers, "B")
        )
    return plan
