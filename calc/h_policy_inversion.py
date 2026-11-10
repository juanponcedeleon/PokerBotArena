"""Policy inversion: if we assume HOW an opponent picks and exposes, their exposed card tells us
far more than the uniform 'any of 48 hidden cards' prior.

For a flop and an exposed card E, enumerate every (hidden, discard) pair from the 48 unseen
cards (1128 combos). Keep the combos where the assumed policy, given the 3-card hand
{E, hidden, discard}, would keep {E, hidden} and expose E. The surviving hidden cards are the
posterior. Compare with the uniform prior.

Policies tested (keep = made-hand best pair; expose rule varies):
  show_high   : expose the higher-ranked kept card
  show_low    : expose the lower-ranked kept card
  show_blank  : expose the kept card that does NOT pair the board (if exactly one does), else high
  show_pair   : expose the kept card that DOES pair the board, else high
  fallback    : keep first two dealt, expose first dealt (order unknown -> any kept card equally)
"""
import itertools

import eval7

from common import CARDS, CAT_ORDER, PAIRS3, c, cat


def keep_made(hand3, flop):
    best, bi = -1, None
    for i, j in PAIRS3:
        v = eval7.evaluate([hand3[i], hand3[j]] + flop)
        if v > best:
            best, bi = v, (i, j)
    return [hand3[bi[0]], hand3[bi[1]]]


def pairs_board(card, flop):
    return any(card.rank == b.rank for b in flop)


def expose(kept, flop, rule):
    a, b = kept
    if rule == "show_high":
        return a if a.rank >= b.rank else b
    if rule == "show_low":
        return a if a.rank <= b.rank else b
    pa, pb = pairs_board(a, flop), pairs_board(b, flop)
    if rule == "show_blank":
        if pa != pb:
            return b if pa else a
        return a if a.rank >= b.rank else b
    if rule == "show_pair":
        if pa != pb:
            return a if pa else b
        return a if a.rank >= b.rank else b
    raise ValueError(rule)


def posterior(flop, E, rule):
    unseen = [x for x in CARDS if x not in flop and x != E]
    post = {}
    weight = 0.0
    for hidden, discard in itertools.permutations(unseen, 2):
        hand3 = [E, hidden, discard]
        if rule == "fallback":
            # unknown deal order: all 3 kept-pairs equally likely, each kept card exposed w.p. 1/2
            # -> P(keep {E,hidden} and expose E) is the same for every (hidden,discard): uniform.
            w = 1.0
            kept = [E, hidden]
        else:
            kept = keep_made(hand3, flop)
            if E not in kept:
                continue
            other = kept[0] if kept[1] == E else kept[1]
            if other != hidden:
                continue
            if expose(kept, flop, rule) != E:
                continue
            w = 1.0
        k = cat(eval7.evaluate([E, hidden] + flop))
        post[k] = post.get(k, 0.0) + w
        weight += w
    return {k: v / weight for k, v in post.items()}, weight


def show(flop, E):
    print(f"\nflop {' '.join(map(str, flop))}   opponent exposes {E}")
    print(f"  {'policy':12s} " + " ".join(f"{k[:8]:>9s}" for k in CAT_ORDER[:6]) + "   combos")
    for rule in ("fallback", "show_high", "show_low", "show_blank", "show_pair"):
        post, w = posterior(flop, E, rule)
        print(f"  {rule:12s} " + " ".join(f"{post.get(k, 0):9.1%}" for k in CAT_ORDER[:6]) + f"   {int(w)}")


if __name__ == "__main__":
    f1 = [c('Qs'), c('7d'), c('2c')]
    show(f1, c('Qh'))
    show(f1, c('Ah'))
    show(f1, c('9h'))
    show(f1, c('2h'))
    f2 = [c('Js'), c('Ts'), c('4d')]
    show(f2, c('Jh'))
    show(f2, c('Kh'))
    show(f2, c('Qs'))
    f3 = [c('Kh'), c('8d'), c('8c')]
    show(f3, c('Kd'))
    show(f3, c('Ad'))
