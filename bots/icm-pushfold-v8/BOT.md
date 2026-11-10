# icm-pushfold-v8 — v7 with PUSH_MAX 18 / RESHOVE_MAX 22 / PREMIUM 0.50

**Status: tie with v7 (not promoted).** Parent: `bots/icm-pushfold-v7` (family reference); best bot: `bots/icm-pushfold-v9`.

Both sweep winners combined (push18 +1.69 ±0.68 and prem50 +1.52 ±0.65 on seed icm3, 300 pairs each).
Result on the family's reference seed, `ab bot bots/icm-pushfold-v8 --tables 400 --seed icm1` (bot = v0-nowar):
**+0.86 ±0.63 (p = 0.007), 75 better / 293 tied / 29 worse**, 0 errors — statistically the same as v7's
+0.82 ±0.56, with 63 timeouts vs 19 under similar machine load (a wider zone means more ICM decisions).
v7's parameters (15 / 18 / 0.30) were kept for v9.
