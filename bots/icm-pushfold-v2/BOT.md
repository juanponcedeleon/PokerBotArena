# icm-pushfold-v2 — v1 + call-not-isolate, committed callers, per-seat call/raise rates in memory

**Status: superseded (lost).** Parent: `bots/icm-pushfold`. Living summary: `bots/icm-pushfold-v7/BOT.md`.

Changes vs v1: calling an all-in is a call; opponents with ≥ 30 % of their stack in (or all-in) count as callers
with multiway equity (eq vs 1/3/7 columns); each seat's preflop raise rate and continue-vs-raise rate are
learned from `state.events` (164-byte struct memory) and blended with the Nash prior (weight 10 decisions).

Result: `ab bot bots/icm-pushfold-v2 --tables 400 --seed icm1 --log`: **−4.99 ± 1.49 (p < 0.001)**.
NOTE: between v1 and v2 the baseline `bot/` changed from v0 to `v0-nowar` (19:22), which caps v0's deep
3-bet war. v2–v4 still carried the *old* v0 deep-stack preflop, so most of this loss is the baseline's
deep-stack fix, not the push/fold (first-divergence analysis in `strategy/08-experiments.md`).
Own leak found anyway: at > 25 BB the ICM call criterion took raise-war all-ins with top-17 % hands
(474 deep all-in calls vs 52 for the baseline; level-1 busts 535 vs 268).
