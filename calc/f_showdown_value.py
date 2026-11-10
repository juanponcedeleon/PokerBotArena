"""What wins at showdown when everyone keeps their best 2 of 3? Compare with 2-card hold'em.
N players all see the river (no folding), oracle selection. Distribution of the WINNING hand
category and the probability that one pair / top pair is good."""
import random
import sys

import eval7

from common import CARDS, CAT_ORDER, oracle_best

TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 30000
rng = random.Random(11)


def run(nplayers, holes):
    win_cat = {k: 0 for k in CAT_ORDER}
    pair_or_worse_wins = 0
    for _ in range(TRIALS):
        d = rng.sample(CARDS, nplayers * holes + 5)
        board = d[-5:]
        vals = []
        for k in range(nplayers):
            h = d[holes * k:holes * (k + 1)]
            if holes == 3:
                vals.append(oracle_best(h, board))
            else:
                vals.append(eval7.evaluate(h + board))
        w = max(vals)
        k = eval7.handtype(w)
        win_cat[k] += 1
        if CAT_ORDER.index(k) <= 1:
            pair_or_worse_wins += 1
    return win_cat, pair_or_worse_wins / TRIALS


print(f"{TRIALS} runouts each. Winning hand category at an all-see-river showdown.")
print(f"{'players':>7s} {'cards':>5s} | " + " ".join(f"{k[:7]:>7s}" for k in CAT_ORDER) + " | P(win with <=1 pair)")
for holes in (2, 3):
    for n in (2, 3, 4, 6, 8):
        wc, p1 = run(n, holes)
        row = " ".join(f"{wc[k] / TRIALS:7.1%}" for k in CAT_ORDER)
        print(f"{n:7d} {holes:5d} | {row} | {p1:6.1%}")
