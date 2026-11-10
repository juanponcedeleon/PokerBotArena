"""Exact enumeration: what 3 hole cards flop versus 2 hole cards (best 2 of 3 kept)."""
import itertools

import eval7

from common import CARDS, CAT_ORDER, PAIRS3, c, cat


def has_oesd(cards):
    rs = set(x.rank for x in cards)
    if 12 in rs:
        rs.add(-1)  # ace low
    for lo in range(0, 9):  # lo..lo+3 with both ends open => lo-1>=-1 and lo+4<=12
        if all(r in rs for r in range(lo, lo + 4)):
            return True
    return False


def flop_stats(hole, three=True):
    rest = [x for x in CARDS if x not in hole]
    n = 0
    pair_plus = two_pair_plus = trips_plus = fd = oesd = 0
    for flop in itertools.combinations(rest, 3):
        flop = list(flop)
        n += 1
        subsets = PAIRS3 if three else [(0, 1)]
        best = -1
        any_fd = any_oesd = False
        for i, j in subsets:
            cards = [hole[i], hole[j]] + flop
            v = eval7.evaluate(cards)
            if v > best:
                best = v
            suits = [x.suit for x in cards]
            if any(suits.count(s) == 4 for s in set(suits)):
                any_fd = True
            if has_oesd(cards):
                any_oesd = True
        idx = CAT_ORDER.index(cat(best))
        pair_plus += idx >= 1
        two_pair_plus += idx >= 2
        trips_plus += idx >= 3
        fd += any_fd
        oesd += any_oesd
    return pair_plus / n, two_pair_plus / n, trips_plus / n, fd / n, oesd / n


tests = [
    ("A K Q rainbow (3)", [c('As'), c('Kd'), c('Qh')], True),
    ("A K offsuit (2, hold'em)", [c('As'), c('Kd')], False),
    ("J T 9 suited (3)", [c('Js'), c('Ts'), c('9s')], True),
    ("J T suited (2)", [c('Js'), c('Ts')], False),
    ("8 8 A rainbow (3)", [c('8s'), c('8d'), c('Ah')], True),
    ("8 8 (2)", [c('8s'), c('8d')], False),
    ("A A A (3, trips)", [c('As'), c('Ad'), c('Ah')], True),
    ("A A (2)", [c('As'), c('Ad')], False),
    ("K 7 2 rainbow (3)", [c('Ks'), c('7d'), c('2h')], True),
    ("K 7 offsuit (2)", [c('Ks'), c('7d')], False),
    ("7 6 5 suited (3)", [c('7s'), c('6s'), c('5s')], True),
    ("Q J 7, QJ suited (3)", [c('Qs'), c('Js'), c('7d')], True),
    ("random-ish 9 5 2 rainbow (3)", [c('9s'), c('5d'), c('2h')], True),
]
print(f"{'hand':32s} {'pair+':>7s} {'2pair+':>7s} {'trips+':>7s} {'FD':>6s} {'OESD':>6s}")
for name, hole, three in tests:
    p1, p2, p3, f, o = flop_stats(hole, three)
    print(f"{name:32s} {p1:7.1%} {p2:7.1%} {p3:7.1%} {f:6.1%} {o:6.1%}")
