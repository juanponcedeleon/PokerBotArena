"""Build evolution templates from the family heads in `bots/`.

A template is `evolve/templates/<family>/` holding `agent.py` (the parent with its strategy
literals hoisted into a TUNABLES block of module-level constants, defaults byte-identical in
behaviour) plus `evolve.json` (the genes: default, bounds, int flag, constraints) and any data
files the parent reads. Templates are generated, never hand-edited: `python -m evolve hoist`
rebuilds them all; `python -m evolve verify <family>` proves the defaults play identically to
the parent on shared tables.

Each family lists text substitutions with the exact number of occurrences expected, so a parent
whose code drifted fails loudly instead of silently tuning the wrong thing.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATES = REPO / "evolve" / "templates"
POOL = REPO / "bots"


@dataclass(frozen=True)
class Gene:
    default: float | None  # None: read the parent's current literal at build time
    low: float
    high: float
    int_valued: bool = False
    note: str = ""

    def to_json(self) -> dict:
        data = {"default": self.default, "min": self.low, "max": self.high}
        if self.int_valued:
            data["int"] = True
        if self.note:
            data["note"] = self.note
        return data


@dataclass
class Family:
    name: str
    parent: str  # directory under bots/
    strategy: str  # one line: which strategy entries the parent implements
    genes: dict[str, Gene]
    substitutions: list[tuple[str, str, int]]  # (old, new, expected count)
    constraints: list[tuple[str, str, str]] = field(default_factory=list)  # (a, ">=", b)
    tunables_comment: str = ""


# ---------------------------------------------------------------------------------------------
# Shared pieces (the v0 code every family inherits)
# ---------------------------------------------------------------------------------------------

EXPOSE_FUNCTION = '''
def expose_index(cards, board, a, b):
    """Which kept card to expose: the weaker (lower rank) with probability EXPOSE_LOW_PROB, the
    stronger otherwise. Deterministic per hand (crc32 of our cards + the flop) so the bot stays
    stateless and a table replays identically; 1.0 = always the weaker card (the v0 rule R-show-low)."""
    low = a if RVAL[cards[a][0]] <= RVAL[cards[b][0]] else b
    if EXPOSE_LOW_PROB >= 1.0:
        return low
    high = b if low == a else a
    roll = (zlib.crc32("".join(cards).encode() + "".join(board).encode()) % 10000) / 10000.0
    return low if roll < EXPOSE_LOW_PROB else high


def select('''

SELECT_SUBS = [
    ("def select(", EXPOSE_FUNCTION, 1),
    (
        "    reveal = a if RVAL[cards[a][0]] <= RVAL[cards[b][0]] else b\n",
        "    reveal = expose_index(cards, board, a, b)\n",
        1,
    ),
]

EXPOSE_GENES = {
    "EXPOSE_LOW_PROB": Gene(1.0, 0.0, 1.0, note="P(expose the weaker kept card); strategy/03 S3.2"),
}

# Preflop, the v0-nowar version (3-bet war capped).
NOWAR_PREFLOP_SUBS = [
    ("    if stack_bb <= 12:\n", "    if stack_bb <= PUSHFOLD_BB:\n", 1),
    (
        "        if cls >= 2 or (cls == 1 and stack_bb <= 6 and not raised):\n",
        "        if cls >= 2 or (cls == 1 and stack_bb <= PUSH_MARGINAL_BB and not raised):\n",
        1,
    ),
    (
        "            return _raise(state, max(3 * to_call, 3 * bb) + me.bet)\n",
        "            return _raise(state, max(THREEBET_MULT * to_call, OPEN_PREMIUM_BB * bb) + me.bet)\n",
        1,
    ),
    ("            return _raise(state, 3 * bb)\n", "            return _raise(state, OPEN_PREMIUM_BB * bb)\n", 1),
    (
        "        if pair >= RVAL[\"T\"] and to_call <= 0.3 * (me.stack + me.bet):\n",
        "        if pair >= RVAL[\"T\"] and to_call <= CALL_MID_PAIR_FRAC * (me.stack + me.bet):\n",
        1,
    ),
    (
        "        if pair >= RVAL[\"7\"] and to_call <= 0.12 * (me.stack + me.bet):\n",
        "        if pair >= RVAL[\"7\"] and to_call <= CALL_LOW_PAIR_FRAC * (me.stack + me.bet):\n",
        1,
    ),
    ("            return _raise(state, 2.5 * bb)\n", "            return _raise(state, OPEN_GOOD_BB * bb)\n", 1),
    (
        "        if to_call <= 6 * bb and n_raises == 1:\n",
        "        if to_call <= CALL_GOOD_MAX_BB * bb and n_raises == 1:\n",
        1,
    ),
    (
        "        if to_call <= bb and not raised:\n",
        "        if to_call <= LIMP_MARGINAL_BB * bb and not raised:\n",
        1,
    ),
]

NOWAR_PREFLOP_GENES = {
    "PUSHFOLD_BB": Gene(12.0, 6.0, 20.0, note="push/fold at or below this many BB"),
    "PUSH_MARGINAL_BB": Gene(6.0, 2.0, 12.0, note="class-1 hands shove unopened at or below this"),
    "OPEN_PREMIUM_BB": Gene(3.0, 2.0, 5.0, note="open size (BB) with class 3; also the 3-bet floor"),
    "OPEN_GOOD_BB": Gene(2.5, 2.0, 4.5, note="open size (BB) with class 2"),
    "THREEBET_MULT": Gene(3.0, 2.2, 5.0, note="3-bet to this multiple of the amount to call"),
    "CALL_GOOD_MAX_BB": Gene(6.0, 2.0, 14.0, note="class 2 calls a single open up to this many BB"),
    "CALL_MID_PAIR_FRAC": Gene(0.30, 0.05, 0.70, note="TT-JJ call a 3-bet up to this share of stack"),
    "CALL_LOW_PAIR_FRAC": Gene(0.12, 0.0, 0.40, note="77-99 call a 3-bet up to this share of stack"),
    "LIMP_MARGINAL_BB": Gene(1.0, 0.0, 3.0, note="class 1 limps when to_call <= this * bb"),
}

NOWAR_PREFLOP_NOLIMP_SUBS = [s for s in NOWAR_PREFLOP_SUBS if "LIMP_MARGINAL_BB" not in s[1]]
NOWAR_PREFLOP_NOLIMP_GENES = {k: v for k, v in NOWAR_PREFLOP_GENES.items() if k != "LIMP_MARGINAL_BB"}

# Postflop, the v0 version.
V0_POSTFLOP_SUBS = [
    ("            return _raise(state, 0.7 * pot + me.bet)\n", "            return _raise(state, STRONG_BET_POT * pot + me.bet)\n", 1),
    ("        if v >= TRIPS or to_call <= pot:\n", "        if v >= TRIPS or to_call <= STRONG_CALL_POT * pot:\n", 1),
    (
        "            return _raise(state, 2.5 * to_call + me.bet + 0.5 * pot)\n",
        "            return _raise(state, RAISE_MULT * to_call + me.bet + RAISE_POT_ADD * pot)\n",
        1,
    ),
    (
        "    if medium:\n        if to_call == 0:\n            return _raise(state, 0.5 * pot + me.bet)\n",
        "    if medium:\n        if to_call == 0:\n            return _raise(state, MEDIUM_BET_POT * pot + me.bet)\n",
        1,
    ),
    ("        if to_call <= 0.6 * pot:\n", "        if to_call <= MEDIUM_CALL_POT * pot:\n", 1),
    ("        if to_call <= 0.3 * pot:\n", "        if to_call <= WEAK_CALL_POT * pot:\n", 1),
    ("        if fd and to_call <= 0.35 * pot:\n", "        if fd and to_call <= FD_CALL_POT * pot:\n", 1),
    (
        "        if raised and len(board) == 3 and max(hole_ranks) >= RVAL[\"J\"]:\n            return _raise(state, 0.5 * pot + me.bet)\n",
        "        if raised and len(board) == 3 and max(hole_ranks) >= CBET_MIN_RANK:\n            return _raise(state, CBET_POT * pot + me.bet)\n",
        1,
    ),
]

V0_POSTFLOP_GENES = {
    "STRONG_BET_POT": Gene(0.7, 0.3, 1.5, note="bet size (pot fraction) with two pair+"),
    "STRONG_CALL_POT": Gene(1.0, 0.3, 3.0, note="two pair raises a bet up to this * pot, calls above"),
    "RAISE_MULT": Gene(2.5, 2.0, 4.0, note="raise = this * to_call + RAISE_POT_ADD * pot"),
    "RAISE_POT_ADD": Gene(0.5, 0.0, 1.2),
    "MEDIUM_BET_POT": Gene(0.5, 0.2, 1.0, note="bet size with top pair"),
    "MEDIUM_CALL_POT": Gene(0.6, 0.1, 1.5, note="top pair calls up to this * pot"),
    "WEAK_CALL_POT": Gene(0.3, 0.0, 1.0, note="any pair calls up to this * pot"),
    "FD_CALL_POT": Gene(0.35, 0.0, 1.0, note="flush draw calls up to this * pot"),
    "CBET_POT": Gene(0.5, 0.25, 1.0, note="continuation bet size"),
    "CBET_MIN_RANK": Gene(9, 5, 13, int_valued=True, note="c-bet needs a hole card of this rank (9 = J, 13 = never)"),
}

# The keep-rule weights (keep-made-plus-draw-v2 / nowar-keep-v2), in units of M = 1,000,000.
KEEP_SUBS = [
    (
        "    1: (15 * M, 15 * M, 8 * M, 2 * M, 0),",
        "    1: (W1_FD * M, W1_FD1 * M, W1_OESD * M, W1_GUT * M, W1_OVER * M),",
        1,
    ),
    (
        "    3: (20 * M, 15 * M, 8 * M, 4 * M, 0),",
        "    3: (W3_FD * M, W3_FD1 * M, W3_OESD * M, W3_GUT * M, W3_OVER * M),",
        1,
    ),
    (
        "    6: (20 * M, 15 * M, 16 * M, 4 * M, 2 * M),",
        "    6: (W6_FD * M, W6_FD1 * M, W6_OESD * M, W6_GUT * M, W6_OVER * M),",
        1,
    ),
]

KEEP_GENES = {}
for _bucket, _vals in ((1, (15, 15, 8, 2, 0)), (3, (20, 15, 8, 4, 0)), (6, (20, 15, 16, 4, 2))):
    for _name, _v, _hi in zip(("FD", "FD1", "OESD", "GUT", "OVER"), _vals, (40, 40, 30, 15, 8), strict=True):
        KEEP_GENES[f"W{_bucket}_{_name}"] = Gene(
            float(_v), 0.0, float(_hi),
            note=f"draw bonus (M units) for {_name} with {'<=2' if _bucket == 1 else '3-4' if _bucket == 3 else '>=5'} live opponents",
        )

# cap-floor-count-v4b: hoisted literals (its existing module constants are genes as they are).
CFC_SUBS = [
    (
        "    if eq >= VALUE_BET_EQ and (ours >= TWO_PAIR or p_best >= 0.75):",
        "    if eq >= VALUE_BET_EQ and (ours >= TWO_PAIR or p_best >= ONE_PAIR_PBEST):",
        1,
    ),
    (
        "        return _raise(state, 2.5 * to_call + me.bet + 0.6 * pot)\n",
        "        return _raise(state, NUTS_RAISE_MULT * to_call + me.bet + NUTS_RAISE_POT * pot)\n",
        1,
    ),
    (
        "            return _raise(state, 2.5 * to_call + me.bet + 0.5 * pot)\n",
        "            return _raise(state, RAISE_MULT * to_call + me.bet + RAISE_POT_ADD * pot)\n",
        1,
    ),
    (
        "    if raised and street == 3 and max(hole_ranks) >= RVAL[\"J\"] and ours < PAIR:\n        return _raise(state, 0.5 * pot + me.bet)\n",
        "    if raised and street == 3 and max(hole_ranks) >= CBET_MIN_RANK and ours < PAIR:\n        return _raise(state, CBET_POT * pot + me.bet)\n",
        1,
    ),
    (
        "                beta = min(BETA_MAX, max(0.0, (bet_frac - 0.35) / 0.4 * BETA_MAX))",
        "                beta = min(BETA_MAX, max(0.0, (bet_frac - BETA_START) / BETA_SPAN * BETA_MAX))",
        1,
    ),
]

CFC_EXISTING_GENES = {
    "OUTS_MULT_FLOP": Gene(1.9, 0.8, 3.0),
    "OUTS_MULT_TURN": Gene(1.0, 0.4, 2.0),
    "VALUE_BET_EQ": Gene(0.60, 0.40, 0.85),
    "RAISE_EQ": Gene(0.78, 0.55, 0.97),
    "NUTS_BET_POT": Gene(0.80, 0.30, 1.50),
    "VALUE_BET_POT": Gene(0.60, 0.25, 1.20),
    "CALL_MARGIN": Gene(0.05, -0.05, 0.25),
    "AGGR_ALPHA": Gene(0.90, 0.0, 1.0),
    "AGGR_ALPHA_EARLIER": Gene(0.50, 0.0, 1.0),
    "BETA_MAX": Gene(0.80, 0.0, 1.0),
    "AGGR_ALPHA_RAISE": Gene(1.00, 0.0, 1.0),
}

CFC_HOISTED_GENES = {
    "ONE_PAIR_PBEST": Gene(0.75, 0.40, 0.98, note="one pair is value-bet only when P(best) is at least this"),
    "NUTS_RAISE_MULT": Gene(2.5, 2.0, 4.0, note="raise when we beat every cap"),
    "NUTS_RAISE_POT": Gene(0.6, 0.0, 1.5),
    "RAISE_MULT": Gene(2.5, 2.0, 4.0, note="raise with eq >= RAISE_EQ"),
    "RAISE_POT_ADD": Gene(0.5, 0.0, 1.2),
    "CBET_POT": Gene(0.5, 0.25, 1.0),
    "CBET_MIN_RANK": Gene(9, 5, 13, int_valued=True),
    "BETA_START": Gene(0.35, 0.10, 0.70, note="bet (pot fraction) where the big-bet weight starts"),
    "BETA_SPAN": Gene(0.40, 0.10, 1.00, note="pot fraction over which it reaches BETA_MAX"),
}

# icm-pushfold-v3: existing module constants are genes; the deep v0 preflop literals are hoisted.
ICM_SUBS = [
    (
        "        return _raise(state, max(3 * to_call, 3 * bb) + me.bet)\n",
        "        return _raise(state, max(THREEBET_MULT * to_call, OPEN_PREMIUM_BB * bb) + me.bet)\n",
        1,
    ),
    ("            return _raise(state, 3 * bb)\n", "            return _raise(state, OPEN_PREMIUM_BB * bb)\n", 1),
    ("            return _raise(state, 2.5 * bb)\n", "            return _raise(state, OPEN_GOOD_BB * bb)\n", 1),
    ("        if cls == 1 and to_call <= bb:\n", "        if cls == 1 and to_call <= LIMP_MARGINAL_BB * bb:\n", 1),
    ("        if to_call <= 6 * bb:\n", "        if to_call <= CALL_GOOD_MAX_BB * bb:\n", 1),
    (
        "            if ev >= SHOVE_MARGIN + _premium(spot, spot.fold_pts(winner)) * 0.5:\n",
        "            if ev >= SHOVE_MARGIN + _premium(spot, spot.fold_pts(winner)) * PREMIUM_UNOPENED_SCALE:\n",
        1,
    ),
]

ICM_NOWAR_SUBS = [
    (
        "            return _raise(state, max(3 * to_call, 3 * bb) + me.bet)\n",
        "            return _raise(state, max(THREEBET_MULT * to_call, OPEN_PREMIUM_BB * bb) + me.bet)\n",
        1,
    ),
    ("            return _raise(state, 3 * bb)\n", "            return _raise(state, OPEN_PREMIUM_BB * bb)\n", 1),
    ("            return _raise(state, 2.5 * bb)\n", "            return _raise(state, OPEN_GOOD_BB * bb)\n", 1),
    ("        if cls == 1 and to_call <= bb:\n", "        if cls == 1 and to_call <= LIMP_MARGINAL_BB * bb:\n", 1),
    (
        "        if pair >= RVAL[\"T\"] and to_call <= 0.3 * (me.stack + me.bet):\n",
        "        if pair >= RVAL[\"T\"] and to_call <= CALL_MID_PAIR_FRAC * (me.stack + me.bet):\n",
        1,
    ),
    (
        "        if pair >= RVAL[\"7\"] and to_call <= 0.12 * (me.stack + me.bet):\n",
        "        if pair >= RVAL[\"7\"] and to_call <= CALL_LOW_PAIR_FRAC * (me.stack + me.bet):\n",
        1,
    ),
    (
        "        if to_call <= 6 * bb and n_raises == 1:\n",
        "        if to_call <= CALL_GOOD_MAX_BB * bb and n_raises == 1:\n",
        1,
    ),
    (
        "            if ev >= SHOVE_MARGIN + _premium(spot, spot.fold_pts(winner)) * 0.5:\n",
        "            if ev >= SHOVE_MARGIN + _premium(spot, spot.fold_pts(winner)) * PREMIUM_UNOPENED_SCALE:\n",
        1,
    ),
]

ICM_NOWAR_HOISTED_GENES = {
    "PREMIUM_UNOPENED_SCALE": Gene(0.5, 0.0, 1.5, note="share of the survival premium charged on an unopened shove"),
    "OPEN_PREMIUM_BB": Gene(3.0, 2.0, 5.0, note="deep: open size with class 3"),
    "OPEN_GOOD_BB": Gene(2.5, 2.0, 4.5, note="deep: open size with class 2"),
    "THREEBET_MULT": Gene(3.0, 2.2, 5.0, note="deep: 3-bet multiple (capped war, v0-nowar)"),
    "CALL_GOOD_MAX_BB": Gene(6.0, 2.0, 14.0),
    "CALL_MID_PAIR_FRAC": Gene(0.30, 0.05, 0.70),
    "CALL_LOW_PAIR_FRAC": Gene(0.12, 0.0, 0.40),
    "LIMP_MARGINAL_BB": Gene(1.0, 0.0, 3.0),
}

ICM_EXISTING_GENES = {
    "PUSH_MAX": Gene(None, 6.0, 22.0),
    "RESHOVE_MAX": Gene(None, 6.0, 28.0),
    "ALLIN_FRACTION": Gene(0.6, 0.3, 0.95),
    "COMMITTED": Gene(0.3, 0.1, 0.7),
    "OPEN_RANGE": Gene(25.0, 8.0, 60.0),
    "PRIOR_HANDS": Gene(10.0, 1.0, 50.0),
    "SHOVE_MARGIN": Gene(0.0, -1.5, 4.0),
    "CALL_MARGIN": Gene(0.0, -1.5, 4.0),
    "PREMIUM": Gene(None, 0.0, 0.6),
    "MULTIWAY_PREMIUM": Gene(0.5, 0.0, 2.0),
}

ICM_HOISTED_GENES = {
    "PREMIUM_UNOPENED_SCALE": Gene(0.5, 0.0, 1.5, note="share of the survival premium charged on an unopened shove"),
    "OPEN_PREMIUM_BB": Gene(3.0, 2.0, 5.0, note="deep: open size with class 3"),
    "OPEN_GOOD_BB": Gene(2.5, 2.0, 4.5, note="deep: open size with class 2"),
    "THREEBET_MULT": Gene(3.0, 2.2, 5.0, note="deep: 3-bet multiple (uncapped v0 war in this parent)"),
    "CALL_GOOD_MAX_BB": Gene(6.0, 2.0, 14.0),
    "LIMP_MARGINAL_BB": Gene(1.0, 0.0, 3.0),
}


def _v0_family(name: str, parent: str, strategy: str, extra_genes: dict[str, Gene], extra_subs: list, constraints=()) -> Family:
    genes = {**NOWAR_PREFLOP_GENES, **V0_POSTFLOP_GENES, **EXPOSE_GENES, **extra_genes}
    subs = NOWAR_PREFLOP_SUBS + V0_POSTFLOP_SUBS + SELECT_SUBS + extra_subs
    return Family(name, parent, strategy, genes, subs, list(constraints))


FAMILIES: dict[str, Family] = {
    "v0-nowar": _v0_family(
        "v0-nowar", "v0-nowar",
        "the former submission (strategy/02 S2.1 capped 3-bet escalation, 07 A20; v0 heuristics everywhere else)",
        {}, [],
    ),
    "nowar-keep-v2": _v0_family(
        "nowar-keep-v2", "nowar-keep-v2",
        "v0-nowar + keep rule with tuned, opponent-scaled draw bonuses (strategy/03 S3.1 + S3.3)",
        KEEP_GENES, KEEP_SUBS,
    ),
    "cap-floor-count-v6": Family(
        "cap-floor-count-v6", "cap-floor-count-v6",
        "cap / floor / count postflop (strategy/01 S1.1-S1.3, S1.5; 04 S4.1-S4.4) on the v0-nowar preflop without marginal limps; the submission since 2026-11-07",
        {**NOWAR_PREFLOP_NOLIMP_GENES, **EXPOSE_GENES, **CFC_EXISTING_GENES, **CFC_HOISTED_GENES},
        NOWAR_PREFLOP_NOLIMP_SUBS + SELECT_SUBS + CFC_SUBS,
        [("RAISE_EQ", ">=", "VALUE_BET_EQ")],
    ),
    "icm-pushfold-v7": Family(
        "icm-pushfold-v7", "icm-pushfold-v7",
        "ICM push/fold with Nash tables, per-seat frequencies and survival premium (strategy/06 S6.1-S6.3, 02 S2.5) on the v0-nowar deep game",
        {**ICM_EXISTING_GENES, **ICM_NOWAR_HOISTED_GENES, **V0_POSTFLOP_GENES, **EXPOSE_GENES},
        ICM_NOWAR_SUBS + V0_POSTFLOP_SUBS + SELECT_SUBS,
        [("RESHOVE_MAX", ">=", "PUSH_MAX")],
    ),
    # Earlier heads, kept so an old run can be reproduced: python -m evolve hoist cap-floor-count-v4b
    "cap-floor-count-v4b": Family(
        "cap-floor-count-v4b", "cap-floor-count-v4b",
        "cap / floor / count postflop (strategy/01 S1.1-S1.3, S1.5; 04 S4.1-S4.4) on the v0-nowar preflop",
        {**NOWAR_PREFLOP_GENES, **EXPOSE_GENES, **CFC_EXISTING_GENES, **CFC_HOISTED_GENES},
        NOWAR_PREFLOP_SUBS + SELECT_SUBS + CFC_SUBS,
        [("RAISE_EQ", ">=", "VALUE_BET_EQ")],
    ),
    "icm-pushfold-v3": Family(
        "icm-pushfold-v3", "icm-pushfold-v3",
        "ICM push/fold with Nash tables and per-seat frequencies (strategy/06 S6.1-S6.3, 02 S2.5) on v0 deep play (uncapped war)",
        {**ICM_EXISTING_GENES, **ICM_HOISTED_GENES, **V0_POSTFLOP_GENES, **EXPOSE_GENES},
        ICM_SUBS + V0_POSTFLOP_SUBS + SELECT_SUBS,
        [("RESHOVE_MAX", ">=", "PUSH_MAX")],
    ),
}

CURRENT = ["v0-nowar", "nowar-keep-v2", "cap-floor-count-v6", "icm-pushfold-v7"]  # what `coevolve` tunes by default


# ---------------------------------------------------------------------------------------------
# Building
# ---------------------------------------------------------------------------------------------

def _literal(gene: Gene) -> str:
    return str(int(round(gene.default))) if gene.int_valued else repr(float(gene.default))


def tunables_block(family: Family, existing: set[str]) -> str:
    """Module-level constants for every gene the parent did not already define."""
    lines = [
        "",
        "# --- TUNABLES (evolve/): every constant in this block is a gene. Defaults reproduce",
        f"#     bots/{family.parent} decision for decision (python -m evolve verify {family.name}).",
    ]
    width = max(len(n) for n in family.genes)
    for name, gene in family.genes.items():
        if name in existing:
            continue
        comment = f"  # {gene.note}" if gene.note else ""
        lines.append(f"{name:<{width}} = {_literal(gene)}{comment}")
    lines.append("")
    return "\n".join(lines)


def module_constants(source: str) -> set[str]:
    import ast

    tree = ast.parse(source)
    names = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            names.add(node.targets[0].id)
    return names


def hoist_source(family: Family, source: str) -> str:
    for old, new, count in family.substitutions:
        found = source.count(old)
        if found != count:
            raise ValueError(
                f"{family.name}: expected {count} occurrence(s) of {old!r} in bots/{family.parent}/agent.py, found {found}. "
                "The parent changed; update evolve/hoist.py."
            )
        source = source.replace(old, new)

    existing = module_constants(source)
    for name in family.genes:
        if name in existing:
            continue
        if name + " " in source or name + "=" in source:
            pass  # used by a substitution; defined by the block below
    anchor = "STRAIGHT = 4 << 24\n"
    if source.count(anchor) != 1:
        raise ValueError(f"{family.name}: anchor {anchor!r} not found exactly once.")
    source = source.replace(anchor, anchor + tunables_block(family, existing))

    # zlib for the exposure roll.
    lines = source.split("\n")
    first_import = next(i for i, line in enumerate(lines) if line.startswith("import ") or line.startswith("from "))
    lines.insert(first_import, "import zlib")
    source = "\n".join(lines)

    # Provenance at the top of the module docstring.
    if not source.startswith('"""'):
        raise ValueError(f"{family.name}: parent has no module docstring.")
    header = (
        f'"""{family.name} evolution template - generated by evolve/hoist.py from bots/{family.parent}.\n'
        "The TUNABLES block holds the genes; every other line is the parent's. Do not edit by hand.\n\n"
        "Parent docstring follows.\n"
    )
    source = header + source[3:]

    # Every gene must now be defined exactly once at module level and referenced somewhere.
    final = module_constants(source)
    for name in family.genes:
        if name not in final:
            raise ValueError(f"{family.name}: gene {name} is not a module-level constant after hoisting.")
        if source.count(name) < 2:
            raise ValueError(f"{family.name}: gene {name} is defined but never used.")
    compile(source, f"<{family.name} template>", "exec")
    return source


def spec_json(family: Family) -> dict:
    return {
        "family": family.name,
        "parent": f"bots/{family.parent}",
        "strategy": family.strategy,
        "generated_by": "evolve/hoist.py",
        "parameters": {name: gene.to_json() for name, gene in family.genes.items()},
        "constraints": [list(c) for c in family.constraints],
    }


def resolve_defaults(family: Family, source: str) -> Family:
    """Genes declared with default None take the literal the parent currently assigns."""
    import ast
    from dataclasses import replace

    literals: dict[str, float] = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                literals[node.targets[0].id] = float(ast.literal_eval(node.value))
            except (ValueError, TypeError, SyntaxError):
                pass
    genes = {}
    for name, gene in family.genes.items():
        if gene.default is None:
            if name not in literals:
                raise ValueError(f"{family.name}: gene {name} has no default and bots/{family.parent} does not assign it a literal.")
            gene = replace(gene, default=literals[name])
        genes[name] = gene
    return replace(family, genes=genes)


def build(family: Family, *, out_dir: Path | None = None) -> Path:
    parent_dir = POOL / family.parent
    source = (parent_dir / "agent.py").read_text(encoding="utf-8")
    family = resolve_defaults(family, source)
    hoisted = hoist_source(family, source)
    out = out_dir or (TEMPLATES / family.name)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for item in parent_dir.iterdir():
        if item.name in ("agent.py", "__pycache__", "BOT.md"):
            continue
        if item.is_dir():
            shutil.copytree(item, out / item.name, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(item, out / item.name)
    (out / "agent.py").write_text(hoisted, encoding="utf-8", newline="\n")
    (out / "evolve.json").write_text(json.dumps(spec_json(family), indent=2) + "\n", encoding="utf-8")
    return out


def build_all(names: list[str] | None = None) -> list[Path]:
    return [build(FAMILIES[name]) for name in (names or CURRENT)]
