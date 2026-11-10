# Strategy library — Bay Area (Crazy Pineapple, one card exposed)

This folder is the team's shared memory about *what wins*. Read `../CLAUDE.md` for conventions (status tags,
evidence levels, claiming sections, append-only experiment log).

## Files

| file | what is in it |
|---|---|
| [00-game-model.md](00-game-model.md) | rules distilled into structural facts with numbers: flop hits, showdown values, caps, the clock |
| [01-exposed-card-information.md](01-exposed-card-information.md) | cap, floor, hidden-card counting, policy inversion, dead cards |
| [02-preflop.md](02-preflop.md) | 3-card hand class equities, tiers, proposed ranges |
| [03-selection.md](03-selection.md) | keep rule (proven) and exposure rules (candidates) |
| [04-postflop.md](04-postflop.md) | value vs caps, floors, bluff-catching math, one-pair discipline, scare cards, archetypes |
| [05-opponent-modeling.md](05-opponent-modeling.md) | observable signals, per-seat stats, rule inference, population priors |
| [06-tournament-icm.md](06-tournament-icm.md) | blind timeline, ICM break-evens, push/fold plan, bubble play |
| [07-anti-patterns.md](07-anti-patterns.md) | what loses and the number that proves it |
| [08-experiments.md](08-experiments.md) | append-only log of every calculation and A/B |
| [09-engineering-constraints.md](09-engineering-constraints.md) | what fits in 1 ms; memory format; testing checklist |
| [_template.md](_template.md) | copy for a new strategy entry |

Calculators live in `../calc/`; their outputs in `../calc/results/`.

## Scoreboard

Ranked by expected impact on points per table. The real field is now known (practice round bd8406dc, 123 teams,
see 05 S5.3): mean 13.0 pts/table, top-10 play VPIP 34% / PFR 26% / see 18% of flops. **Real results outrank arena
results; arena paired A/B outranks ladders.** Headmaster verdicts live in `08-experiments.md` ("Decision (headmaster)").

**Submission status (2026-11-07T04:59Z):** `bot/` = `bots/fp-cfc2` (upload 6a60c397 `fp-cfc2.zip`; fp-v3 = 74bac11f, fp-v2 = fc4bac3f). Chain: v0 (practice round, 8.67 pts, rank 99/123) → v0-nowar (+5.33 ±2.02 vs v0) → cap-floor-count-v6 (+2.85 ±1.09 vs v0-nowar) → fp-v2 (+2.2…+4.1 vs v6 in three fields) → fp-v3 (+1.26 ±0.83 vs fp-v2; +2.54 ±0.91 vs v6). → fp-cfc2 (+1.10 ±0.44 and +0.82 ±0.35 vs fp-v3). **Final for the round (upload 6a60c397).** icm-pushfold-v9 lost the deciding experiment (fp-v2 +4.29 ±1.45); fp-v4/v4b rejected (07 A25). A/B against `bot` = against fp-cfc2.

| rank | strategy | file | status | evidence | expected impact | why |
|---|---|---|---|---|---|---|
| 0 | Cap the preflop re-raise escalation (no 3-bet wars at 100 BB) | 07 A20, 02 S2.1 | PROVEN | LOCAL (arena A/B) + LIVE (leak confirmed) | very high | v0-nowar +5.33 ±2.02 vs v0 (400 pairs, p<0.001, seed cfc3); real round: 40% of our busts in level 1. Now the submission |
| 1 | Keep rule: made hand + draw bonus (tuned weights) | 03 S3.1 | PROVEN | SIM + LOCAL | high (small per table) | +8 pot-share points over the fallback; arena: v2 +0.29 ±0.20 pts/table vs made-hand-only in a flop-heavy field (2000 pairs, p=0.004), nil vs kit examples where v0 busts preflop; best version `bots/keep-made-plus-draw-v2` |
| 2 | ICM-aware push/fold with phase schedule | 06 S6.1, S6.2, S6.5 | PROMISING (field-dependent; shelved) | LOCAL | low–medium | module (≤ 15 BB eff., per-seat call/raise rates, survival premium 0.30) wins only in the kit field: on cap-floor-count-v6 +2.33/+2.21 ±0.6 (2 seeds), on fp-v3 (`icm-pushfold-v10`) +1.27 ±0.78; in the archetype field −1.85 ±2.22 and −0.97 ±1.04 (n.s.). fp-v3 stays. Tables (02 S2.5, 06 S6.2) remain valid. Deep-stack ICM calls REJECTED (07 A24) |
| 3 | Cap / floor / count against every live opponent | 01 S1.1–S1.3, 04 S4.1–S4.3 | PROVEN (arena, action-conditioned count) | MATH + LOCAL | high | v1 lost −1.71 ±1.21 (uniform prior, 07 A21); **v4b (action-conditioned count + one-pair gate) +1.93 ±0.89 vs v0-nowar (1154 pairs, p<0.001, 0 failures)**. Next pick candidate once its latency tail is cleared (8–10 failures in a contended ladder, 7 for v3 in its own run) |
| 4 | Preflop percentile ranges (pairs first, no trips, no danglers) | 02 S2.1–S2.4 | PROVEN | SIM + LIVE (field) + LOCAL (`bots/fp-v1`) | very high | real field: points correlate −0.37 with VPIP, −0.47 with flops seen; v0 plays 66% VPIP vs 34% for the top 10 (07 A22). The biggest unbuilt lever |
| 5 | One-pair discipline | 04 S4.4 | PROVEN | SIM | high | one pair wins 22% HU showdowns; stops the biggest leak |
| 6 | Archetype exploits (folders, stations, min-raisers) | 04 S4.9, 05 S5.2, S5.4 | UNTESTED (null so far) | reasoning + LOCAL (null) | medium vs weak field | cfc-v7-steal (steal from folders, probe never-bettors) −0.03 ±0.17 vs v6 (1175 pairs, 96% tied): the triggers almost never fire in our field. Needs the arch-* field and looser triggers |
| 7 | Policy inversion of opponents' exposures | 01 S1.4, 05 S5.1 | PROMISING | MATH | medium–high | 100%-certain reads against deterministic bots; needs rule identification to be reliable |
| 8 | Bubble play: shove first, call tight | 06 S6.3 | PROVEN (logic) | MATH | medium | 65% break-even to call at 4-handed equal stacks |
| 9 | Scare-card barrels (board pairs our exposure) | 04 S4.6 | PROVEN (logic) | MATH | medium | the most credible bluff in the game; cost nothing to add |
| 10 | Exposure rule R1 (plan-driven, randomized) | 03 S3.2 | UNTESTED vs readers; NULL vs this field | MATH + LOCAL (null) | low | A/B done: cfc-v7-expose (hide strength / show high) vs v6 show-low = +0.10 ±0.48 (1175 pairs, p=0.68) even with a reader in the field. The real-field correlation (07 A23) is a sophistication proxy, not a cause |
| 11 | Dead-card accounting | 01 S1.5, 04 S4.7 | PROVEN (logic) | MATH | low–medium | exact outs; small but free |
| 12 | Population priors from hand-history downloads | 05 S5.3 | PROMISING | LIVE (practice round, 123 teams) | compounding | pipeline works (`arena stats`); priors table in 05 S5.3; not yet consumed by any bot |
| 13 | Keep rule adjusted to opponent count | 03 S3.3 | UNTESTED | none | low | refinement of #1 |
| 14 | Empty Bluffer side prize | 03 S3.2 | UNTESTED | logic | none for points | only when free |

## How to use this library

- **Before building a feature:** find its row; if UNTESTED, write the experiment first (see 08).
- **After an experiment:** append to 08, update the entry's status and the scoreboard row, move rejects to 07.
- **Before changing a status to PROVEN:** quote the number and the script in the entry.
- **When you disagree with an entry:** add a dated note under it; do not silently rewrite.

## Open questions (highest value first)

Headmaster direction, 2026-11-06 19:25 (evidence in 08, "Decision (headmaster)" lines):

0. **Deciding experiment, run it first:** `arena ab bots/icm-pushfold-v9 bots/fp-v2 --field v0-baseline check_or_fold arch-folder arch-shover arch-station --tables 1000` with zero failures, plus uncontended `arena check` and a strict run for both. Both beat the live bot (cap-floor-count-v6): fp-v1/v2 by +1.7…+4.1 in three fields, icm-pushfold-v9 by +2.33 ±0.58 in the kit field. Then try fp-v2 + the v9 short-stack module as a new directory.
1. **The decisive experiment:** build `bots/<name>` = v0-nowar + a preflop range at the real top-10's shape
   (VPIP ~34%, PFR ~26%, 3-bet ~2%, see 18% of flops; 02 S2.1 percentiles) and A/B it **against `bot`** (now v0-nowar)
   with `--field v0-baseline check_or_fold min_raiser` plus at least one shover archetype, ≥ 400 pairs, zero
   failures. This targets the real leak (8.67 pts, 40% of busts in level 1, 66% VPIP).
2. Combine the proven pieces only via a new bot directory and an A/B: v0-nowar + keep rule v2 (`bots/keep-made-plus-draw-v2`
   select block). Expected +0.3; worth doing but not worth a submission on its own.
3. Fix `bots/icm-pushfold` failed decisions (21 in ladder c741) and give it a paired A/B vs `bot`; until then it is
   disqualified. Re-evaluate cap-floor-count v3 only with a hero that survives level 1.
4. Exposure A/B (03 S3.2): show-low vs show-high vs randomized, same bot otherwise, 2000 pairs in a flop-heavy field.
   Real-field correlation (07 A23) says show-low/pairing exposure is what losers do; prove or kill it.
5. Hand-vs-calling-range equities for 3-card classes → Nash push/fold tables (02 S2.5, 06 S6.2) — still valuable
   for levels 4+, where v0 is already chip-positive.
6. Fast flop/turn equity approximation vs true equity (unchanged).

Stop / do not pursue right now: cap-floor-count v1 (rejected, 07 A21); any bot family whose latest ladder shows
failed decisions; timing claims from watcher ladders or strict mode on this laptop (use the build box).
