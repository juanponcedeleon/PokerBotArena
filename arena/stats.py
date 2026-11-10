"""Statistics over table outcomes: means with confidence intervals, paired A/B tests,
head-to-head records. Points per table is the competition's metric, so everything is in
points per table (a seat at a table is one observation; fillers are excluded)."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Iterable
from typing import Any

from arena.outcome import TableOutcome

try:  # scipy is in the competition requirements, but the arena should not die without it.
    from scipy import stats as _scipy_stats
except Exception:  # noqa: BLE001
    _scipy_stats = None


def t_critical(df: int, confidence: float = 0.95) -> float:
    if df < 1:
        return float("nan")
    if _scipy_stats is not None:
        return float(_scipy_stats.t.ppf(0.5 + confidence / 2, df))
    return 1.96 if df >= 30 else {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57}.get(df, 2.1)


def summary(values: list[float]) -> dict[str, float | int]:
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": float("nan"), "sd": float("nan"), "se": float("nan"), "ci95": float("nan")}
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1) if n > 1 else 0.0
    sd = math.sqrt(var)
    se = sd / math.sqrt(n) if n > 1 else float("nan")
    ci = t_critical(n - 1) * se if n > 1 else float("nan")
    return {"n": n, "mean": mean, "sd": sd, "se": se, "ci95": ci}


def paired(a: list[float], b: list[float]) -> dict[str, Any]:
    """Paired comparison of b against a (same tables). Positive mean_diff favors b."""
    if len(a) != len(b):
        raise ValueError("Paired samples must have the same length.")
    diffs = [y - x for x, y in zip(a, b, strict=True)]
    s = summary(diffs)
    n = s["n"]
    wins = sum(d > 1e-9 for d in diffs)
    losses = sum(d < -1e-9 for d in diffs)
    ties = n - wins - losses
    t_stat = s["mean"] / s["se"] if n > 1 and s["se"] > 0 else float("nan")
    if _scipy_stats is not None and n > 1 and not math.isnan(t_stat):
        p_value = float(2 * _scipy_stats.t.sf(abs(t_stat), n - 1))
    else:
        p_value = float("nan")
    return {
        "n": n,
        "mean_diff": s["mean"],
        "se": s["se"],
        "ci95": s["ci95"],
        "t": t_stat,
        "p_value": p_value,
        "b_better_tables": wins,
        "a_better_tables": losses,
        "tied_tables": ties,
    }


def required_tables(sd: float, detectable_diff: float, confidence: float = 0.95) -> int:
    """How many paired tables separate a difference of `detectable_diff` points with the given
    confidence, at the observed standard deviation of the paired difference."""
    if detectable_diff <= 0 or sd <= 0:
        return 0
    z = 1.96 if confidence == 0.95 else t_critical(10_000, confidence)
    return math.ceil((z * sd / detectable_diff) ** 2)


def aggregate(outcomes: Iterable[TableOutcome]) -> dict[str, dict[str, Any]]:
    """Per base label, across all its scoring seats."""
    rows: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "points": [],
            "places": Counter(),
            "tables": 0,
            "seats": 0,
            "decisions": 0,
            "failures": 0,
            "timeouts": 0,
            "errors": 0,
            "illegal": 0,
            "truncated": 0,
            "lat_p50": [],
            "lat_p99": [],
            "lat_max": 0.0,
            "mem_max": 0,
            "bust_hands": [],
            "survived": 0,
            "hands": [],
        }
    )
    for outcome in outcomes:
        seen: set[str] = set()
        for seat in outcome.seats:
            row = rows[seat.label]
            if seat.label not in seen:
                row["tables"] += 1
                seen.add(seat.label)
            row["seats"] += 1
            row["decisions"] += seat.decisions
            row["failures"] += seat.failures
            row["timeouts"] += seat.timeouts
            row["errors"] += seat.errors
            row["illegal"] += seat.illegal
            row["truncated"] += seat.truncated
            if seat.lat_p50_ms is not None:
                row["lat_p50"].append(seat.lat_p50_ms)
            if seat.lat_p99_ms is not None:
                row["lat_p99"].append(seat.lat_p99_ms)
            if seat.lat_max_ms is not None:
                row["lat_max"] = max(row["lat_max"], seat.lat_max_ms)
            row["mem_max"] = max(row["mem_max"], seat.mem_max_bytes)
            if seat.filler:
                continue
            row["points"].append(seat.points)
            row["places"][seat.place] += 1
            row["hands"].append(outcome.hands)
            if seat.bust_hand is None:
                row["survived"] += 1
            else:
                row["bust_hands"].append(seat.bust_hand)
    result = {}
    for label, row in rows.items():
        s = summary(row["points"])
        places = row["places"]
        total_places = sum(places.values()) or 1
        p50s = sorted(row["lat_p50"])
        p99s = sorted(row["lat_p99"])
        result[label] = {
            "label": label,
            "tables": row["tables"],
            "seats": len(row["points"]),
            "avg_points": s["mean"],
            "ci95": s["ci95"],
            "sd": s["sd"],
            "avg_place": sum(p * c for p, c in places.items()) / total_places,
            "place_share": {place: places[place] / total_places for place in sorted(places)},
            "top3_share": sum(c for p, c in places.items() if p <= 3) / total_places,
            "decisions": row["decisions"],
            "failures": row["failures"],
            "timeouts": row["timeouts"],
            "errors": row["errors"],
            "illegal": row["illegal"],
            "truncated": row["truncated"],
            "failure_rate": row["failures"] / row["decisions"] if row["decisions"] else 0.0,
            "lat_p50_ms": p50s[len(p50s) // 2] if p50s else None,
            "lat_p99_ms": p99s[int(0.99 * (len(p99s) - 1))] if p99s else None,
            "lat_max_ms": row["lat_max"] if p50s else None,
            "mem_max_bytes": row["mem_max"],
            "avg_bust_hand": (sum(row["bust_hands"]) / len(row["bust_hands"])) if row["bust_hands"] else None,
            "survived_share": row["survived"] / len(row["points"]) if row["points"] else 0.0,
        }
    return result


def head_to_head(outcomes: Iterable[TableOutcome]) -> dict[str, dict[str, list[int]]]:
    """record[a][b] = [a above b, tied, a below b] over tables where both sat (scoring seats).
    Seats of the same bot at one table are compared by best place on each side."""
    record: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    for outcome in outcomes:
        best: dict[str, int] = {}
        for seat in outcome.seats:
            if seat.filler:
                continue
            best[seat.label] = min(best.get(seat.label, 99), seat.place)
        labels = sorted(best)
        for i, a in enumerate(labels):
            for b in labels[i + 1 :]:
                if best[a] < best[b]:
                    record[a][b][0] += 1
                    record[b][a][2] += 1
                elif best[a] > best[b]:
                    record[a][b][2] += 1
                    record[b][a][0] += 1
                else:
                    record[a][b][1] += 1
                    record[b][a][1] += 1
    return {a: dict(row) for a, row in record.items()}


def ab_comparison(outcomes: Iterable[TableOutcome], hero: str, challenger: str) -> dict[str, Any]:
    """Paired points of the challenger (arm B) against the hero (arm A), per table pair. A side's
    points at a table are the mean over its seats, so several copies still count as one pair."""
    by_pair: dict[tuple[int, int], dict[str, list[float]]] = defaultdict(lambda: {"A": [], "B": []})
    for outcome in outcomes:
        if outcome.arm not in ("A", "B"):
            continue
        wanted = hero if outcome.arm == "A" else challenger
        pts = [s.points for s in outcome.seats if s.label == wanted and not s.filler]
        if pts:
            by_pair[(outcome.iteration, outcome.number)][outcome.arm].append(sum(pts) / len(pts))
    a, b = [], []
    for key in sorted(by_pair):
        sides = by_pair[key]
        if sides["A"] and sides["B"]:
            a.append(sides["A"][0])
            b.append(sides["B"][0])
    result = paired(a, b)
    result.update(
        {
            "hero": hero,
            "challenger": challenger,
            "hero_avg_points": summary(a)["mean"] if a else float("nan"),
            "challenger_avg_points": summary(b)["mean"] if b else float("nan"),
            "tables_for_1pt": required_tables(summary([y - x for x, y in zip(a, b)])["sd"], 1.0) if len(a) > 1 else None,
        }
    )
    return result
