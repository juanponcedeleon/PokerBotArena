# icm-pushfold-v5 — v4 rebased on `bot/` = v0-nowar

**Status: WON vs baseline; superseded by v6/v7 (same decisions, faster / retuned).**
Parent: `bots/icm-pushfold-v4` + `bots/v0-nowar` preflop. Living summary: `bots/icm-pushfold-v7/BOT.md`.

Deep-stack preflop (> 16 BB effective) is now byte-for-byte v0-nowar (3-bet war capped); ICM push/fold with
per-seat rates handles unopened pots at ≤ 13 BB effective and all-ins where the stack at risk is ≤ 16 BB.

Result: `ab bot bots/icm-pushfold-v5 --tables 400 --seed icm1 --log`:
**+0.65 ± 0.48 pts/table (p = 0.008), 52 better / 320 tied / 25 worse.**
Caveat: 165 timeouts (0.11 % of decisions) under heavy machine contention; p99 0.56 ms in isolation,
~70 % of decision time in ICM (4 calls × 45–60 µs) → v6.
