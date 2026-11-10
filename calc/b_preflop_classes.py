"""Monte Carlo equity of every 3-card starting hand class, all-in preflop, everyone keeps the
oracle-best 2 of 3 at the river. Equity vs 1, 3 and 7 random opponents from the same deals.
Oracle selection is optimistic for everyone equally, so the RANKING is what matters.

Writes results/b_preflop_classes.csv. ~10 min at TRIALS=1500.
"""
import csv
import random
import sys
import time

import eval7

from common import CARDS, PAIRS3, RANKS, SUITS, c, oracle_best

TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
rng = random.Random(2026)


def classes():
    """Yield (label, structure, concrete 3 cards)."""
    out = []
    R = RANKS[::-1]  # A..2
    for i, a in enumerate(R):
        # trips
        out.append((f"{a}{a}{a}", "trips", [c(a + 's'), c(a + 'h'), c(a + 'd')]))
        for j, b in enumerate(R):
            if b == a:
                continue
            # pair of a + kicker b
            out.append((f"{a}{a}{b}r", "pair+kicker", [c(a + 's'), c(a + 'h'), c(b + 'd')]))
            out.append((f"{a}{a}{b}s", "pair+kicker suited", [c(a + 's'), c(a + 'h'), c(b + 's')]))
        for j in range(i + 1, 13):
            for k in range(j + 1, 13):
                b, d = R[j], R[k]
                out.append((f"{a}{b}{d}r", "rainbow", [c(a + 's'), c(b + 'h'), c(d + 'd')]))
                out.append((f"{a}{b}{d}-{a}{b}s", "two suited (top two)", [c(a + 's'), c(b + 's'), c(d + 'd')]))
                out.append((f"{a}{b}{d}-{a}{d}s", "two suited (top+bottom)", [c(a + 's'), c(b + 'h'), c(d + 's')]))
                out.append((f"{a}{b}{d}-{b}{d}s", "two suited (bottom two)", [c(a + 'h'), c(b + 's'), c(d + 's')]))
                out.append((f"{a}{b}{d}sss", "three suited", [c(a + 's'), c(b + 's'), c(d + 's')]))
    return out


def simulate(hole):
    rest = [x for x in CARDS if x not in hole]
    eq = [0.0, 0.0, 0.0]  # vs 1, 3, 7
    for _ in range(TRIALS):
        deal = rng.sample(rest, 21 + 5)
        board = deal[21:]
        hero = oracle_best(hole, board)
        opps = [oracle_best(deal[3 * k:3 * k + 3], board) for k in range(7)]
        for idx, n in enumerate((1, 3, 7)):
            vals = opps[:n]
            m = max(vals)
            if hero > m:
                eq[idx] += 1.0
            elif hero == m:
                eq[idx] += 1.0 / (1 + vals.count(m))
    return [e / TRIALS for e in eq]


if __name__ == "__main__":
    cls = classes()
    print(f"{len(cls)} classes x {TRIALS} trials", flush=True)
    t0 = time.time()
    with open("results/b_preflop_classes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["label", "structure", "eq_vs1", "eq_vs3", "eq_vs7", "trials"])
        for n, (label, struct, hole) in enumerate(cls):
            e = simulate(hole)
            w.writerow([label, struct, f"{e[0]:.4f}", f"{e[1]:.4f}", f"{e[2]:.4f}", TRIALS])
            if n % 100 == 0:
                print(f"{n}/{len(cls)} {time.time() - t0:.0f}s {label} {e}", flush=True)
    print("done", time.time() - t0)
