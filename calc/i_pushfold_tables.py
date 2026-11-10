"""Push/fold tables for 3-card hands (strategy/02 S2.5 -> strategy/06 S6.2).

Part A: hand-vs-range equity. For every one of the 1,755 three-card classes, Monte Carlo
equity all-in preflop against ONE opponent whose three cards are drawn uniformly from the
top X% of dealt hands (ranked by heads-up equity from results/b_preflop_classes.csv,
frequency-weighted over the 22,100 deals), both sides keeping the oracle-best 2 of 3 at the
river (same optimistic-for-both convention as b_preflop_classes.py; the ordering is what
matters, and heads-up the optimism cancels).

    results/i_hand_vs_range.csv   label, freq, pct, eq@2, eq@5, ... eq@100

Part B: chip-EV shove/call equilibrium (single-caller approximation, no antes, pot 1.5 BB,
shover not in the blinds). For effective stack S (BB) and N players left to act, iterate
    callers: call iff eq(h, shove range Y) >= S / (2S + 1.5)
    shover : shove iff (1-c)^N * 1.5 + (1 - (1-c)^N) * (eq(h, X) * (2S + 1.5) - S) >= 0
to a fixed point (Y*, X*) in dealt-percentiles.

    results/i_pushfold_nash.csv   S, N, shove_pct, call_pct
    results/i_pushfold_tables.md  human-readable summary

The bot (bots/icm-pushfold) loads both CSVs and does the ICM arithmetic at decision time.

Usage: starter-kit/.venv/Scripts/python.exe calc/i_pushfold_tables.py [TRIALS] [--nash-only]
TRIALS default 3000 (~1 min on 16 cores). Run from calc/ or the repo root.
"""
import csv
import zlib
import os
import random
import sys
import time
from itertools import combinations
from multiprocessing import Pool

import eval7

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
RANKS = "23456789TJQKA"
SUITS = "cdhs"
RVAL = {r: i for i, r in enumerate(RANKS)}
CARD_STR = [r + s for r in RANKS for s in SUITS]
CARD_OBJ = {s: eval7.Card(s) for s in CARD_STR}
PAIRS3 = ((0, 1), (0, 2), (1, 2))
X_GRID = (2, 5, 8, 12, 16, 20, 25, 30, 40, 50, 65, 80, 100)
TRIALS = 3000
for a in sys.argv[1:]:
    if a.isdigit():
        TRIALS = int(a)
NASH_ONLY = "--nash-only" in sys.argv


def class_key(cards):
    """Label of a concrete 3-card hand, matching results/b_preflop_classes.csv."""
    rs = sorted(((RVAL[c[0]], c[1]) for c in cards), key=lambda x: -x[0])
    r = [x[0] for x in rs]
    s = [x[1] for x in rs]
    if r[0] == r[1] == r[2]:
        return RANKS[r[0]] * 3
    if r[0] == r[1]:
        return RANKS[r[0]] * 2 + RANKS[r[2]] + ("s" if s[2] in (s[0], s[1]) else "r")
    if r[1] == r[2]:
        return RANKS[r[1]] * 2 + RANKS[r[0]] + ("s" if s[0] in (s[1], s[2]) else "r")
    a, b, d = RANKS[r[0]], RANKS[r[1]], RANKS[r[2]]
    if s[0] == s[1] == s[2]:
        return a + b + d + "sss"
    if s[0] == s[1]:
        return f"{a}{b}{d}-{a}{b}s"
    if s[0] == s[2]:
        return f"{a}{b}{d}-{a}{d}s"
    if s[1] == s[2]:
        return f"{a}{b}{d}-{b}{d}s"
    return a + b + d + "r"


def class_freq(label):
    """Number of the 22,100 deals in this class."""
    if label.endswith("sss"):
        return 4
    if "-" in label:
        return 12
    if len(label) == 3:
        return 4  # trips
    if label[0] == label[1]:
        return 12  # pair + kicker, suited or rainbow: 12 each
    return 24  # rainbow unpaired


def representative(label):
    """Concrete cards for a class label (inverse of class_key)."""
    if len(label) == 3:
        a = label[0]
        return [a + "s", a + "h", a + "d"]
    if "-" in label:
        trio, suited = label.split("-")
        a, b, d = trio
        hi, lo = suited[0], suited[1]
        out = []
        for x in (a, b, d):
            out.append(x + ("s" if x in (hi, lo) else ("h" if x == a else ("d" if x == b else "c"))))
        return out
    if label.endswith("sss"):
        return [x + "s" for x in label[:3]]
    if label[0] == label[1]:
        p, k, kind = label[0], label[2], label[3]
        return [p + "s", p + "h", k + ("s" if kind == "s" else "d")]
    a, b, d = label[:3]
    return [a + "s", b + "h", d + "d"]


def load_classes():
    rows = []
    with open(os.path.join(RES, "b_preflop_classes.csv"), newline="") as f:
        for row in csv.DictReader(f):
            rows.append((row["label"], float(row["eq_vs1"]), float(row["eq_vs7"])))
    # Ranking for "top X%": heads-up equity, frequency-weighted over deals.
    rows.sort(key=lambda t: -t[1])
    total = sum(class_freq(l) for l, _, _ in rows)
    assert total == 22100, total
    pct = {}
    cum = 0
    for label, eq1, _ in rows:
        f = class_freq(label)
        pct[label] = 100.0 * (cum + f / 2) / total  # midpoint percentile of dealt hands
        cum += f
    return [l for l, _, _ in rows], pct


def oracle_best(hole, board):
    b = -1
    for i, j in PAIRS3:
        v = eval7.evaluate([hole[i], hole[j]] + board)
        if v > b:
            b = v
    return b


def hero_row(args):
    label, pct = args
    rng = random.Random(zlib.crc32(label.encode()) ^ 2026)
    hero_s = representative(label)
    assert class_key(hero_s) == label, (label, hero_s)
    hero = [CARD_OBJ[c] for c in hero_s]
    rest = [c for c in CARD_STR if c not in hero_s]
    # Every possible caller hand from the remaining 49 cards, with its percentile.
    combos = []
    for trio in combinations(rest, 3):
        combos.append((pct[class_key(trio)], trio))
    combos.sort()
    out = [label, class_freq(label), round(pct[label], 3)]
    rest_set = set(rest)
    for X in X_GRID:
        pool = [t for p, t in combos if p <= X]
        if not pool:  # tiny X: take the best available
            pool = [combos[0][1]]
        wins = 0.0
        for _ in range(TRIALS):
            cs = pool[rng.randrange(len(pool))]
            deck = list(rest_set.difference(cs))
            board_s = rng.sample(deck, 5)
            board = [CARD_OBJ[c] for c in board_s]
            h = oracle_best(hero, board)
            o = oracle_best([CARD_OBJ[c] for c in cs], board)
            if h > o:
                wins += 1.0
            elif h == o:
                wins += 0.5
        out.append(round(wins / TRIALS, 4))
    return out


def part_a():
    labels, pct = load_classes()
    t0 = time.time()
    print(f"Part A: {len(labels)} classes x {len(X_GRID)} ranges x {TRIALS} trials", flush=True)
    with Pool(max(1, os.cpu_count() - 1)) as p:
        rows = p.map(hero_row, [(l, pct) for l in labels], chunksize=8)
    path = os.path.join(RES, "i_hand_vs_range.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["label", "freq", "pct"] + [f"eq@{x}" for x in X_GRID])
        for r in rows:
            w.writerow(r)
    print(f"wrote {path} in {time.time() - t0:.0f}s", flush=True)


def join_multiway():
    """Append eq_vs3 / eq_vs7 (random opponents, from b_preflop_classes.csv) to i_hand_vs_range.csv
    so a bot can scale heads-up range equity to multiway all-ins."""
    multi = {}
    with open(os.path.join(RES, "b_preflop_classes.csv"), newline="") as f:
        for row in csv.DictReader(f):
            multi[row["label"]] = (row["eq_vs3"], row["eq_vs7"])
    path = os.path.join(RES, "i_hand_vs_range.csv")
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    head = rows[0]
    if "eq_vs3" in head:
        return
    head += ["eq_vs3", "eq_vs7"]
    for r in rows[1:]:
        r += list(multi[r[0]])
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print("joined eq_vs3/eq_vs7 into", path)


# ---------------------------------------------------------------- Part B: Nash in chip EV

def load_hvr():
    rows = []
    with open(os.path.join(RES, "i_hand_vs_range.csv"), newline="") as f:
        for row in csv.DictReader(f):
            rows.append((row["label"], int(row["freq"]), float(row["pct"]),
                         [float(row[f"eq@{x}"]) for x in X_GRID]))
    return rows


def eq_at(eqs, Y):
    """Linear interpolation of eq vs top-Y% on the X grid."""
    if Y <= X_GRID[0]:
        return eqs[0]
    if Y >= X_GRID[-1]:
        return eqs[-1]
    for i in range(1, len(X_GRID)):
        if Y <= X_GRID[i]:
            x0, x1 = X_GRID[i - 1], X_GRID[i]
            t = (Y - x0) / (x1 - x0)
            return eqs[i - 1] + t * (eqs[i] - eqs[i - 1])
    return eqs[-1]


def nash(rows, S, N, iters=60):
    total = sum(r[1] for r in rows)
    Y = 100.0
    X = 100.0
    for _ in range(iters):
        need_call = S / (2 * S + 1.5)
        Xn = 100.0 * sum(r[1] for r in rows if eq_at(r[3], Y) >= need_call) / total
        X = 0.5 * X + 0.5 * Xn
        c = X / 100.0
        pf = (1 - c) ** N
        Yn = 100.0 * sum(
            r[1] for r in rows
            if pf * 1.5 + (1 - pf) * (eq_at(r[3], X) * (2 * S + 1.5) - S) >= 0) / total
        Y = 0.5 * Y + 0.5 * Yn
    return Y, X


def part_b():
    rows = load_hvr()
    S_grid = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 25, 30]
    out = []
    for S in S_grid:
        for N in range(1, 8):
            Y, X = nash(rows, S, N)
            out.append((S, N, round(Y, 2), round(X, 2)))
    path = os.path.join(RES, "i_pushfold_nash.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["S", "N", "shove_pct", "call_pct"])
        w.writerows(out)
    # Markdown summary
    md = [
        "# Push/fold tables for 3-card hands (chip EV, single-caller approximation)",
        "",
        f"Source: `calc/i_pushfold_tables.py` ({TRIALS} trials per class per range). Percentiles are of dealt hands,",
        "ranked by heads-up equity (`b_preflop_classes.csv`). S = effective stack in BB, N = players left to act,",
        "pot = 1.5 BB, shover not in the blinds. Cell = shove % / call % at the fixed point.",
        "",
        "| S \\ N | " + " | ".join(str(n) for n in range(1, 8)) + " |",
        "|---|" + "---|" * 7,
    ]
    for S in S_grid:
        cells = [f"{y:.0f} / {x:.0f}" for (s, n, y, x) in out if s == S]
        md.append(f"| {S} | " + " | ".join(cells) + " |")
    md += ["", "## Heads-up equity vs calling ranges, selected hands", "",
           "| hand | pct | " + " | ".join(f"vs top {x}%" for x in X_GRID) + " |",
           "|---|---|" + "---|" * len(X_GRID)]
    want = ["AAKs", "AAKr", "AAA", "KKK", "88As", "882r", "22Ar", "AKQsss", "AKQr", "JT9sss", "AK2r",
            "A72r", "765sss", "KQ2r", "QJ9r", "T98-T9s", "732r"]
    by = {r[0]: r for r in rows}
    for w_ in want:
        if w_ in by:
            r = by[w_]
            md.append(f"| {r[0]} | {r[2]:.1f} | " + " | ".join(f"{e:.3f}" for e in r[3]) + " |")
    mdp = os.path.join(RES, "i_pushfold_tables.md")
    with open(mdp, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(f"wrote {path} and {mdp}")
    for line in md[6:6 + 2 + len(S_grid)]:
        print(line)


if __name__ == "__main__":
    if not NASH_ONLY:
        part_a()
    join_multiway()
    part_b()
