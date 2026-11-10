"""Fitness in the arena: paired, in-process, many candidates per run.

A *multi-arm plan* starts from a league plan with the parent (hero) in a field, then for every
candidate adds a copy of each table in which the candidate sits in exactly the hero's seats.
All arms of a table share its seed, so cards, button and payouts are identical until a decision
differs: the ranking inside a generation is a paired comparison, which needs far fewer tables
than independent leagues. The fast runner (arena.fast) plays everything on all cores.

Training runs with the decision clock recorded but not enforced: the machine is shared with
other arena runs and the time limit would add noise that has nothing to do with strategy. A
candidate with any error or illegal action is rejected regardless of its points.
"""

from __future__ import annotations

import math
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from arena import fast
from arena.bots import BotRef
from arena.outcome import TableOutcome, make_rules
from arena.plan import Plan, TableSpec, base_label, copy_index, copy_label, league_plan


def multi_arm_plan(hero: str, field_labels: list[str], candidates: list[str], *, seed: str, tables: int, players: int = 8) -> Plan:
    labels = [hero] + [label for label in field_labels if label != hero]
    base = league_plan(labels, seed=seed, tables=tables, players=players)
    plan = Plan("multi-arm", seed, players, labels + list(candidates), hero=hero)
    for spec in base.tables:
        plan.tables.append(TableSpec(spec.iteration, spec.number, spec.seed, spec.seats, spec.fillers, "A"))
        for k, candidate in enumerate(candidates):
            swapped = tuple(copy_label(candidate, copy_index(c)) if base_label(c) == hero else c for c in spec.seats)
            plan.tables.append(TableSpec(spec.iteration, spec.number, spec.seed, swapped, spec.fillers, f"c{k}"))
    return plan


@dataclass
class ArmStats:
    label: str
    tables: int = 0
    seats: int = 0
    points: list[float] = field(default_factory=list)  # per table: mean over the arm's seats
    failures: int = 0
    timeouts: int = 0
    errors: int = 0
    illegal: int = 0
    decisions: int = 0
    lat_p99: list[float] = field(default_factory=list)
    lat_max: float = 0.0
    mem_max: int = 0
    bot_errors: list[str] = field(default_factory=list)

    @property
    def mean(self) -> float:
        return statistics.fmean(self.points) if self.points else float("nan")

    @property
    def ci95(self) -> float:
        if len(self.points) < 2:
            return float("nan")
        return 1.96 * statistics.stdev(self.points) / math.sqrt(len(self.points))

    @property
    def healthy(self) -> bool:
        return self.errors == 0 and self.illegal == 0 and not self.bot_errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label, "tables": self.tables, "seats": self.seats, "mean_points": self.mean,
            "ci95": self.ci95, "failures": self.failures, "timeouts": self.timeouts, "errors": self.errors,
            "illegal": self.illegal, "decisions": self.decisions,
            "lat_p99_ms": statistics.median(self.lat_p99) if self.lat_p99 else None, "lat_max_ms": self.lat_max,
            "mem_max_bytes": self.mem_max, "healthy": self.healthy, "bot_errors": self.bot_errors[:3],
        }


@dataclass
class PairedResult:
    hero: str
    arms: dict[str, ArmStats]
    diffs: dict[str, list[float]]  # candidate -> per-table (candidate - hero)
    elapsed_s: float

    def diff_mean(self, label: str) -> float:
        d = self.diffs.get(label) or []
        return statistics.fmean(d) if d else float("nan")

    def diff_ci95(self, label: str) -> float:
        d = self.diffs.get(label) or []
        return 1.96 * statistics.stdev(d) / math.sqrt(len(d)) if len(d) > 1 else float("nan")

    def to_dict(self) -> dict[str, Any]:
        return {
            "hero": self.hero, "elapsed_s": round(self.elapsed_s, 1),
            "arms": {label: arm.to_dict() for label, arm in self.arms.items()},
            "paired_diff": {label: {"mean": self.diff_mean(label), "ci95": self.diff_ci95(label), "n": len(d)} for label, d in self.diffs.items()},
        }


def evaluate_arms(
    hero: BotRef,
    field_refs: list[BotRef],
    candidates: dict[str, Path],
    *,
    seed: str,
    tables: int,
    workers: int | None = None,
    enforce_time: bool = False,
    progress: bool = True,
) -> PairedResult:
    """Play the multi-arm plan; return per-arm points and per-table paired differences."""
    plan = multi_arm_plan(hero.label, [f.label for f in field_refs], list(candidates), seed=seed, tables=tables)
    paths = {hero.label: hero.path, **{f.label: f.path for f in field_refs}, **candidates}
    rules = make_rules()
    started = time.time()
    arms = {label: ArmStats(label) for label in [hero.label] + list(candidates)}
    by_table: dict[tuple[int, int], dict[str, float]] = {}
    total = len(plan.tables)
    last = [0.0]

    def show(done: int, n: int) -> None:
        now = time.time()
        if progress and (done == n or now - last[0] > 3):
            last[0] = now
            print(f"\r    {done}/{n} tables", end="" if done < n else "\n", file=sys.stderr, flush=True)

    for outcome in fast.run(plan.tables, paths, rules=rules, workers=workers, enforce_time=enforce_time, progress=show):
        _absorb(outcome, arms, by_table)
    diffs: dict[str, list[float]] = {label: [] for label in candidates}
    for key, row in by_table.items():
        if hero.label not in row:
            continue
        for label in candidates:
            if label in row:
                diffs[label].append(row[label] - row[hero.label])
    return PairedResult(hero.label, arms, diffs, time.time() - started)


def _absorb(outcome: TableOutcome, arms: dict[str, ArmStats], by_table: dict[tuple[int, int], dict[str, float]]) -> None:
    label = None
    pts = []
    for seat in outcome.seats:
        if seat.label not in arms:
            continue
        label = seat.label
        arm = arms[label]
        arm.seats += 1
        arm.failures += seat.failures
        arm.timeouts += seat.timeouts
        arm.errors += seat.errors
        arm.illegal += seat.illegal
        arm.decisions += seat.decisions
        if seat.lat_p99_ms is not None:
            arm.lat_p99.append(seat.lat_p99_ms)
        if seat.lat_max_ms is not None:
            arm.lat_max = max(arm.lat_max, seat.lat_max_ms)
        arm.mem_max = max(arm.mem_max, seat.mem_max_bytes)
        pts.append(seat.points)
    if label is None:
        return
    arm = arms[label]
    arm.tables += 1
    mean = statistics.fmean(pts)
    arm.points.append(mean)
    for text in outcome.bot_errors:
        if text.startswith(label):
            arm.bot_errors.append(text)
    by_table.setdefault((outcome.iteration, outcome.number), {})[label] = mean


def identical(result: PairedResult, label: str) -> bool:
    """True when the candidate's paired differences are all exactly zero (same decisions)."""
    d = result.diffs.get(label) or []
    return bool(d) and all(x == 0.0 for x in d)
