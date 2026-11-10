# icm-pushfold-v3 — v2 + survival premium

**Status: superseded.** Parent: `bots/icm-pushfold-v2`. Living summary: `bots/icm-pushfold-v7/BOT.md`.

Adds `PREMIUM`: the edge over folding required before committing a stack = PREMIUM × ICM(fold) × (n − 2)/6
(n players remaining), × (1 + 0.5 per extra committed player). Rationale: ICM assumes equal skill; in a field
of simple bots that bust each other, folding is worth more than ICM(fold).

Sweep (300 pairs, seed icm2, vs `bot` = v0-nowar): PREMIUM 0.08 → −4.07 ± 1.82; 0.15 → −4.36 ± 1.82;
0.30 → −4.35 ± 1.85. The premium alone did not fix the deep-stack leak (see v4).
