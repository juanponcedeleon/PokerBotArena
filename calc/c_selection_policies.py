"""How much does the keep/discard choice matter, and how good are cheap heuristics?

Hero gets 3 random cards and a random flop, picks 2 cards with a policy, then the turn/river
run out versus 3 opponents who each keep their 'made hand' best pair (cheap, realistic).
Metric: hero's showdown equity share. Same deals for every policy (common random numbers).
"""
import random
import sys
import time

import eval7

from common import CARDS, PAIRS3, made_hand_choice

TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
rng = random.Random(7)


def pol_oracle(hole, flop, rest, board5):
    best, bi = -1, None
    for i, j in PAIRS3:
        v = eval7.evaluate([hole[i], hole[j]] + board5)
        if v > best:
            best, bi = v, (i, j)
    return bi


def pol_made(hole, flop, rest, board5):
    return made_hand_choice(hole, flop)


def pol_high(hole, flop, rest, board5):
    order = sorted(range(3), key=lambda k: -hole[k].rank)
    return tuple(sorted(order[:2]))


def pol_fallback(hole, flop, rest, board5):
    return (0, 1)  # discard last dealt, keep first two


def make_pol_mc(k):
    def pol(hole, flop, rest, board5):
        # equity vs one random 2-card hand over k runouts, for each pair
        best, bi = -1, None
        samples = [rng.sample(rest, 4) for _ in range(k)]
        for i, j in PAIRS3:
            mine = [hole[i], hole[j]]
            s = 0.0
            for smp in samples:
                b = flop + smp[:2]
                hv = eval7.evaluate(mine + b)
                ov = eval7.evaluate(smp[2:] + b)
                s += 1.0 if hv > ov else (0.5 if hv == ov else 0.0)
            if s > best:
                best, bi = s, (i, j)
        return bi
    return pol


def make_pol_madeplus(w_fd=1, w_oesd=1):
    """Made hand, with a bump for flush draws / open-enders: cheap 1 ms style heuristic."""
    def pol(hole, flop, rest, board5):
        best, bi = -1, None
        for i, j in PAIRS3:
            cards = [hole[i], hole[j]] + flop
            v = eval7.evaluate(cards)
            cat = eval7.handtype(v)
            score = v
            suits = [x.suit for x in cards]
            if any(suits.count(s) == 4 for s in set(suits)):
                score += w_fd * 10_000_000  # roughly: treat as a pair-ish hand
            rs = set(x.rank for x in cards)
            if 12 in rs:
                rs.add(-1)
            if any(all(r in rs for r in range(lo, lo + 4)) for lo in range(0, 9)):
                score += w_oesd * 8_000_000
            if score > best:
                best, bi = score, (i, j)
        return bi
    return pol


POLICIES = {
    "oracle (river knowledge; upper bound)": pol_oracle,
    "MC equity, 200 runouts (too slow for 1 ms)": make_pol_mc(200),
    "MC equity, 40 runouts": make_pol_mc(40),
    "made hand + draw bonus (cheap)": make_pol_madeplus(),
    "made hand only (3 evals)": pol_made,
    "keep two highest cards": pol_high,
    "fallback: keep first two dealt": pol_fallback,
}

if __name__ == "__main__":
    t0 = time.time()
    deals = []
    for _ in range(TRIALS):
        d = rng.sample(CARDS, 3 + 9 + 5)
        deals.append(d)
    totals = {k: 0.0 for k in POLICIES}
    agree_made_vs_oracle = 0
    agree_mc_vs_oracle = 0
    for d in deals:
        hole = d[:3]
        opps = [d[3 + 3 * k:6 + 3 * k] for k in range(3)]
        board5 = d[12:]
        flop = board5[:3]
        rest = [x for x in CARDS if x not in hole and x not in flop]
        opp_vals = []
        for o in opps:
            i, j = made_hand_choice(o, flop)
            opp_vals.append(eval7.evaluate([o[i], o[j]] + board5))
        m = max(opp_vals)
        choices = {}
        for name, pol in POLICIES.items():
            i, j = pol(hole, flop, rest, board5)
            choices[name] = (i, j)
            hv = eval7.evaluate([hole[i], hole[j]] + board5)
            if hv > m:
                totals[name] += 1.0
            elif hv == m:
                totals[name] += 1.0 / (1 + opp_vals.count(m))
        agree_made_vs_oracle += choices["made hand only (3 evals)"] == choices["oracle (river knowledge; upper bound)"]
        agree_mc_vs_oracle += choices["MC equity, 200 runouts (too slow for 1 ms)"] == choices["oracle (river knowledge; upper bound)"]
    print(f"{TRIALS} deals, hero vs 3 made-hand opponents, {time.time() - t0:.0f}s")
    print(f"{'policy':48s} equity")
    for name, s in totals.items():
        print(f"{name:48s} {s / TRIALS:6.1%}")
    print(f"\nmade-hand choice == oracle choice: {agree_made_vs_oracle / TRIALS:.1%}")
    print(f"MC-200 choice == oracle choice:   {agree_mc_vs_oracle / TRIALS:.1%}")
