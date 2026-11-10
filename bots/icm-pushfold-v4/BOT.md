# icm-pushfold-v4 — v3 with the ICM machinery restricted to short stacks

**Status: superseded.** Parent: `bots/icm-pushfold-v3`. Living summary: `bots/icm-pushfold-v7/BOT.md`.

The ICM shove/call arithmetic now runs only when the stack at risk is short: our effective stack ≤ 16 BB, or
the shover's ≤ 16 BB with nobody else committed. Deeper all-ins fall back to the base bot's preflop logic.

Result: `ab bot bots/icm-pushfold-v4 --tables 400 --seed icm1 --log`: **−2.00 ± 1.32 (p = 0.003)**.
First-divergence analysis of the 397 pairs: every first difference was a deep (> 25 BB), early (hand ≤ 20)
preflop decision where the baseline folded and v4 called/raised — i.e. the *old v0* deep logic v4 still carried
versus the baseline's new `v0-nowar` cap. The push/fold part never diverged first. → rebase (v5).
