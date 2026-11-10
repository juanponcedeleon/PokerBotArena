"""Tune the S3.1 keep score: made hand + weighted draw features, by number of opponents.

Same harness idea as c_selection_policies.py (hero 3 cards, random flop, opponents keep their
made-hand-best pair, everyone sees the river, metric = hero pot share, common random numbers),
but every candidate weight vector is scored from one set of precomputed per-deal features, so a
whole grid costs seconds. Opponent count is varied (1, 3, 6) to test strategy/03 S3.3.

Features per 2-card subset on the flop (5 cards):
  made   eval7 value of the 5 cards
  fd     4 cards of one suit, both kept cards in the suit (2-tone board)
  fd1    4 cards of one suit, only one kept card in it (monotone board: weaker, shared draw)
  oesd   four consecutive distinct ranks (2345..TJQK)
  gut    four distinct ranks inside a 5-rank window, not an oesd (incl. A-high/A-low)
  over   number of kept cards above every board card when the subset makes no pair+

Usage: .venv/Scripts/python.exe calc/i_keep_weights.py [deals]   (writes calc/results/i_keep_weights.txt)
Owner: Claude (keep-rule agent), 2026-11-06.
"""
import itertools
import random
import sys
import time
from pathlib import Path

import eval7

sys.path.insert(0, str(Path(__file__).parent))
from common import CARDS, PAIRS3, made_hand_choice  # noqa: E402

DEALS = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
OPP_COUNTS = (1, 3, 6)
M = 1_000_000
PAIR = 1 << 24


def features(cards):
    v = eval7.evaluate(cards)
    suits = [c.suit for c in cards]
    kept = cards[3:]
    fd = fd1 = 0
    for s in set(suits):
        if suits.count(s) == 4:
            if kept[0].suit == s and kept[1].suit == s:
                fd = 1
            else:
                fd1 = 1
    ranks = set(c.rank for c in cards)
    ext = set(ranks)
    if 12 in ranks:
        ext.add(-1)
    oesd = int(any(all(r in ext for r in range(lo, lo + 4)) for lo in range(0, 9)))
    gut = 0
    if not oesd:
        for lo in range(-1, 9):  # windows A2345 .. TJQKA
            if sum(1 for r in range(lo, lo + 5) if r in ext) >= 4:
                gut = 1
                break
    over = 0
    if v < PAIR:
        top = max(c.rank for c in cards[:3])
        over = sum(1 for c in kept if c.rank > top)
    return v, fd, fd1, oesd, gut, over


def main():
    rng = random.Random(11)
    t0 = time.time()
    need = 3 + 3 * max(OPP_COUNTS) + 5
    deals = []
    for _ in range(DEALS):
        d = rng.sample(CARDS, need)
        hole, board5 = d[:3], d[-5:]
        flop = board5[:3]
        feats, river = [], []
        for i, j in PAIRS3:
            feats.append(features(flop + [hole[i], hole[j]]))
            river.append(eval7.evaluate([hole[i], hole[j]] + board5))
        opp_vals = []
        for k in range(max(OPP_COUNTS)):
            o = d[3 + 3 * k:6 + 3 * k]
            a, b = made_hand_choice(o, flop)
            opp_vals.append(eval7.evaluate([o[a], o[b]] + board5))
        deals.append((feats, river, opp_vals))
    print(f"{DEALS} deals prepared in {time.time() - t0:.0f}s")

    def share(weights, n_opp):
        w_fd, w_fd1, w_oesd, w_gut, w_over = weights
        total = 0.0
        for feats, river, opp_vals in deals:
            best, bi = -1, 0
            for idx, (v, fd, fd1, oesd, gut, over) in enumerate(feats):
                s = v + w_fd * fd + w_fd1 * fd1 + w_oesd * oesd + w_gut * gut + w_over * over
                if s > best:
                    best, bi = s, idx
            ov = opp_vals[:n_opp]
            m = max(ov)
            hv = river[bi]
            if hv > m:
                total += 1.0
            elif hv == m:
                total += 1.0 / (1 + ov.count(m))
        return total / DEALS

    lines = []
    def out(s=""):
        print(s)
        lines.append(s)

    out(f"{DEALS} deals, hero keep policy vs N made-hand opponents, pot share (fair share = 1/(N+1))")
    base = (0, 0, 0, 0, 0)
    v1 = (10 * M, 10 * M, 8 * M, 0, 0)
    out(f"\n{'weights (fd, fd1, oesd, gut, over) in millions':50s} " + " ".join(f"N={n:<6d}" for n in OPP_COUNTS))
    for name, w in (("made hand only", base), ("v1: fd=fd1=10, oesd=8", v1)):
        out(f"{name:50s} " + " ".join(f"{share(w, n):6.2%} " for n in OPP_COUNTS))

    # grid search, per opponent count
    grid_fd = [0, 5, 10, 15, 20, 30]
    grid_fd1 = [0, 5, 10, 15]
    grid_oesd = [0, 4, 8, 12, 16]
    grid_gut = [0, 2, 4]
    grid_over = [0, 2, 4]
    for n in OPP_COUNTS:
        results = []
        for w in itertools.product(grid_fd, grid_fd1, grid_oesd, grid_gut, grid_over):
            results.append((share(tuple(x * M for x in w), n), w))
        results.sort(reverse=True)
        out(f"\nN={n}: top 8 weight vectors (fd, fd1, oesd, gut, over)")
        for s, w in results[:8]:
            out(f"  {str(w):28s} {s:6.2%}")
        out(f"  v1 (10,10,8,0,0) at N={n}: {share(v1, n):6.2%};  made only: {share(base, n):6.2%}")
    out(f"\n{time.time() - t0:.0f}s total")
    Path(__file__).parent.joinpath("results", "i_keep_weights.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
