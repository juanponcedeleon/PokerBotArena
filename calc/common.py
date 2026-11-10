"""Shared helpers for offline calculators. Run with starter-kit/.venv (eval7 installed)."""
import eval7

RANKS = '23456789TJQKA'
SUITS = 'cdhs'
CARDS = [eval7.Card(r + s) for r in RANKS for s in SUITS]
CAT_ORDER = ['High Card', 'Pair', 'Two Pair', 'Trips', 'Straight', 'Flush',
             'Full House', 'Quads', 'Straight Flush']
PAIRS3 = ((0, 1), (0, 2), (1, 2))


def c(s):
    return eval7.Card(s)


def oracle_best(hole3, board5):
    """Best value over the three 2-card subsets (perfect-foresight selection)."""
    b = -1
    for i, j in PAIRS3:
        v = eval7.evaluate([hole3[i], hole3[j]] + board5)
        if v > b:
            b = v
    return b


def made_hand_choice(hole3, flop):
    """Index pair maximizing the current 5-card hand on the flop."""
    best, bi = -1, None
    for i, j in PAIRS3:
        v = eval7.evaluate([hole3[i], hole3[j]] + flop)
        if v > best:
            best, bi = v, (i, j)
    return bi


def cat(v):
    return eval7.handtype(v)


def cat_idx(v):
    return CAT_ORDER.index(eval7.handtype(v))
