"""Blind schedule pressure and ICM arithmetic for the 8-max SNG format."""
BLINDS = [(10, 20), (20, 40), (30, 60), (50, 100), (80, 160), (125, 250), (200, 400),
          (300, 600), (500, 1000), (800, 1600), (1200, 2400), (2000, 4000)]
TOTAL = 16000
print("hands      blinds       avg stack (BB) with 8 / 6 / 4 / 3 players left")
for lvl in range(12):
    lo, hi = 1 + 20 * lvl, 20 * (lvl + 1)
    sb, bb = BLINDS[lvl]
    row = f"{lo:3d}-{hi:3d}   {sb:5d}/{bb:<5d}   "
    for n in (8, 6, 4, 3):
        row += f"{TOTAL / n / bb:6.1f} "
    print(row)
print("level 12 (2000/4000) repeats until the 250-hand cap")


def icm(stacks, payouts):
    """Malmuth-Harville ICM. Returns list of equities."""
    n = len(stacks)
    payouts = list(payouts) + [0] * (n - len(payouts))

    def rec(remaining, prize_idx):
        eq = {p: 0.0 for p in remaining}
        if prize_idx >= len(payouts) or payouts[prize_idx] == 0 or not remaining:
            return eq
        tot = sum(stacks[p] for p in remaining)
        if tot == 0:
            return eq
        for p in remaining:
            if stacks[p] <= 0:
                continue
            pr = stacks[p] / tot
            eq[p] += pr * payouts[prize_idx]
            sub = rec([q for q in remaining if q != p], prize_idx + 1)
            for q, v in sub.items():
                eq[q] += pr * v
        return eq

    r = rec(list(range(n)), 0)
    return [r[i] for i in range(n)]


pay = (50, 30, 20)
base = icm([2000] * 8, pay)[0]
print(f"\nICM, 8 x 2000, payouts 50/30/20: each player = {base:.2f} pts")
dbl = icm([4000] + [2000] * 6, pay)[0]
print(f"Double up on hand 1 (4000 vs six 2000s): {dbl:.2f} pts  (x{dbl / base:.3f}, not x2)")
print(f"Bust = 0. Break-even win% for a full-stack flip on hand 1: {base / dbl:.1%}  (chip-EV says 50%)")

cases = [
    ("8 left, equal 2000, I shove/call for full stacks", [2000] * 8),
    ("6 left, equal 2667, flip for stacks", [2667] * 6),
    ("4 left (bubble), equal 4000, flip for stacks", [4000] * 4),
    ("4 left, I'm short 2000 vs 4667s, flip vs one", [2000, 4667, 4667, 4666]),
    ("4 left, I'm big 7000, flip vs a 3000", [7000, 3000, 3000, 3000]),
    ("3 left (all paid), equal 5333, flip", [5333, 5333, 5334]),
    ("5 left, I'm big 6000 vs short 1500", [6000, 1500, 2833, 2833, 2834]),
]
print("\nBreak-even equity to put stacks in vs seat 1 (chip-EV break-even is 50%):")
for desc, stacks in cases:
    me = 0
    cur = icm(stacks, pay)[me]
    amt = min(stacks[me], stacks[1])
    win_st = stacks[:]
    win_st[me] += amt
    win_st[1] -= amt
    lose_st = stacks[:]
    lose_st[me] -= amt
    lose_st[1] += amt
    w = icm(win_st, pay)[me]
    l = icm(lose_st, pay)[me]
    be = (cur - l) / (w - l)
    print(f"  {desc:52s} now {cur:5.2f}  win {w:5.2f}  lose {l:5.2f}  break-even {be:5.1%}")

print("\nHand cap: at hand 250 survivors split remaining points by ICM (chip share matters, not place).")
for stacks in ([8000, 4000, 2000, 2000], [6000, 6000, 4000], [10000, 3000, 3000]):
    print(f"  stacks {stacks} -> {[round(x, 1) for x in icm(stacks, pay)]}")
