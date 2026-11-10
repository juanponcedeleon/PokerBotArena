"""Exact: given a flop and one exposed card, what can the hidden card make?
Observer knows only board (3) + exposed card (1): 48 hidden candidates.
From the hero's seat subtract your own 3 cards (usually 45 candidates)."""
import eval7

from common import CARDS, CAT_ORDER, c, cat


def dist(board, exposed):
    hidden = [x for x in CARDS if x not in board and x != exposed]
    counts = {}
    for h in hidden:
        k = cat(eval7.evaluate([exposed, h] + board))
        counts[k] = counts.get(k, 0) + 1
    return counts, len(hidden)


def fmt(counts):
    return "  ".join(f"{k}:{v}" for k, v in
                     sorted(counts.items(), key=lambda kv: -CAT_ORDER.index(kv[0])))


def best_possible(board, exposed):
    hidden = [x for x in CARDS if x not in board and x != exposed]
    return cat(max(eval7.evaluate([exposed, h] + board) for h in hidden))


boards = {
    "Dry rainbow  Qs 7d 2c": [c('Qs'), c('7d'), c('2c')],
    "Two-tone connected  Js Ts 4d": [c('Js'), c('Ts'), c('4d')],
    "Paired  Kh 8d 8c": [c('Kh'), c('8d'), c('8c')],
    "Monotone  9h 6h 2h": [c('9h'), c('6h'), c('2h')],
}
exposures = {
    "Dry rainbow  Qs 7d 2c": ["Qh", "7h", "2h", "Ah", "Kh", "9h", "4h"],
    "Two-tone connected  Js Ts 4d": ["Jh", "Th", "4h", "Ah", "Kh", "Qh", "9h", "Qs", "9s", "As", "7s", "2c"],
    "Paired  Kh 8d 8c": ["8s", "Kd", "Ad", "Qd", "4d"],
    "Monotone  9h 6h 2h": ["9d", "Ah", "Kh", "4h", "Ad", "Kd", "3d", "7d"],
}
for name, board in boards.items():
    print("=" * 100)
    print(name)
    for e in exposures[name]:
        ex = c(e)
        counts, n = dist(board, ex)
        geq2p = sum(v for k, v in counts.items() if CAT_ORDER.index(k) >= 2)
        print(f"  show {e}: best possible = {best_possible(board, ex):14s} "
              f"P(>=2pair)={geq2p / n:5.1%}   {fmt(counts)}")

print("=" * 100)
print("River Qs 7d 2c Th 4s (unpaired, no flush)")
board = [c('Qs'), c('7d'), c('2c'), c('Th'), c('4s')]
for e in ["Qh", "Ah", "9h", "Jh", "3h"]:
    counts, n = dist(board, c(e))
    geq2p = sum(v for k, v in counts.items() if CAT_ORDER.index(k) >= 2)
    print(f"  show {e}: best possible = {best_possible(board, c(e)):14s} "
          f"P(>=2pair)={geq2p / n:5.1%}   {fmt(counts)}")

# How often is the board itself paired / flush-possible by the river (the cases where the cap breaks)?
import itertools, random
rng = random.Random(3)
paired = flush3 = straight_heavy = 0
N = 100000
for _ in range(N):
    b = rng.sample(CARDS, 5)
    ranks = [x.rank for x in b]
    suits = [x.suit for x in b]
    if len(set(ranks)) < 5:
        paired += 1
    if max(suits.count(s) for s in set(suits)) >= 3:
        flush3 += 1
print("=" * 100)
print(f"Random 5-card boards: paired {paired / N:.1%}, 3+ of a suit {flush3 / N:.1%}  "
      f"(when neither, an exposed card that misses the board caps the hand at one pair)")
