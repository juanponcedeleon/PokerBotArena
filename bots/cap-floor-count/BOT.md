# cap-floor-count

Owner: Claude (cap-floor-count agent)   Created: 2026-11-06   Parent: `bot/agent.py` v0

## Hypothesis

Postflop in Bay Area is arithmetic: every live opponent is one hidden card from a set we can list.
Replacing v0's hold'em-style hand-strength buckets with exact caps, floors and hidden-card counts
against *every* live exposure should win more points per table, mostly by (a) folding hands that
are visibly dominated, (b) never slow-playing hands that beat every cap, and (c) calling or folding
on the river by the exact loss fraction instead of a fixed pot fraction.

## Strategy entries implemented

| entry | what the bot does |
|---|---|
| 01 S1.1 cap | `cap = max over unseen h of rank(E_opp, h, board)`; beat every cap → bet 0.8 pot / raise, never slow-play |
| 01 S1.2 floor | `floor = min ...`; a floor above our hand → fold to any river bet, never bet into it |
| 01 S1.3 river counting | `lose = (#beats + ½ #ties) / |unseen|` per opponent, `p_best = Π(1 − lose)`; call iff `p_best ≥ to_call / (pot + to_call) + 0.02` |
| 01 S1.5 dead cards | `unseen = deck − board − my 3 − every exposed card at the table`, folded seats included |
| 04 S4.1 beat the cap | as S1.1 |
| 04 S4.2 below the floor | as S1.2 |
| 04 S4.3 bluff-catch | as S1.3 (uniform prior; no archetype weighting yet) |
| 04 S4.4 one-pair discipline | one pair is bet for value only when `p_best ≥ 0.75` (opponents capped below it); otherwise it is a bluff-catcher priced by the count |

Flop/turn: the same count gives P(currently best); it is shrunk by a category/street factor
(`SHRINK_FLOP`, `SHRINK_TURN`) and our own outs to two-pair-or-better are added (one evaluation per
unseen card). These multipliers are priors, not measurements, and are the first thing to tune.

Preflop and selection are unchanged from `bot/agent.py` v0 so the A/B isolates the postflop module.
Memory is unused (`b""`).

## Cost

Per postflop decision: ≤45 evaluations per live opponent (≤7) + ≤45 for our outs + bookkeeping.
Target < 300 µs; `arena check` reports p99.

## What promotes / demotes

- **Promote** (01 S1.1–S1.3 and 04 S4.1–S4.4 → PROVEN, scoreboard row 3): paired A/B vs `bot/`
  with ≥ 400 tables, fixed seed, `p < 0.05` and a positive diff; no failed decisions in `arena check`.
- **Demote** (→ 07-anti-patterns with the number): a significant negative diff, or no significant
  difference after 800+ pairs (then the logic is right but worth nothing against this field).
- Also watched: points vs `check_or_fold` and `min_raiser` in the same run, and p99 latency.

## Versions

| version | change | result |
|---|---|---|
| v1 (2026-11-06) `cap-floor-count` | pipeline above, uniform prior | vs bot, weak field (seed cfc1, 397 pairs): +0.41 ±0.46, p=0.08, 373 ties. vs bot, pool field (cfc2, 400 pairs): **−1.71 ±1.21, p=0.006** — folds postflop 10% vs 21%, WTSD 53% vs 44%, W$SD 41% vs 48%: uniform prior pays off value bets |
| v2 `cap-floor-count-v2` | bettor read as made hand with weight 0.75 (0.90 after a raise); value-bet threshold 0.55; call margin 0.03 | vs bot, pool (cfc2, 329 pairs): −0.34 ±1.43, p=0.64 |
| v3 `cap-floor-count-v3` | v2 + preflop 3-bet cap (same as `v0-nowar`) | vs bot, pool (cfc3, 400 pairs): +1.65 ±2.19, p=0.14. vs `v0-nowar` (postflop isolated, cfc3, 294 pairs): −0.67 ±1.62, p=0.42 |
| v3 at 1154 pairs (cfc4, `cfc-v3-vs-nowar-big`) | — | vs `v0-nowar`: −0.56 ±0.92, p=0.23; folds 13% vs 20%, W$SD 46% vs 52% |
| v4a `cap-floor-count-v4a` | bettor = made hand (alpha 0.9; 1.0 after a raise; 0.5 if they bet an earlier street); bet ≥0.75 pot or repeated aggression = two pair+ (beta 0.8); call margin 0.05 | vs `v0-nowar` (cfc4, 1154 pairs, same field): **+1.29 ±0.89, p=0.004** |
| v4b `cap-floor-count-v4b` | v4a + one pair value-bet only when p_best ≥ 0.75, eq ≥ 0.60 | vs `v0-nowar` (cfc4, 1154 pairs): **+1.93 ±0.89, p<0.001** |
| v4b robustness (`cfc-v4b-robust`, seed cfc5, field = other agents' bots + examples, no older cap-floor-count) | — | vs `v0-nowar` (= current `bot/` fingerprint): **+1.46 ±1.04, p=0.006**, 1167 pairs, 0 failures |
| v4b strict mode (`cfc-v4b-strict`, WSL BotPool, 32 tables) | — | 0 timeouts / 0 errors; p50 0.28 ms, p99 2.0 ms, max 5.2 ms (v0-nowar p99 4.4, max 10.5 in the same run) |
| v4c `cap-floor-count-v4c` (ablation) | v3 + call margin 0.05 only | vs `v0-nowar` (cfc4, 1154 pairs): **−1.16 ±0.87, p=0.009** → the margin alone hurts; the v4 gain is the bet-size-aware count |
| v5 `cap-floor-count-v5` | v4b + GC tuning at import (`gc.freeze`, thresholds 50000/50/50); decision-identical (0/6000 random states differ) | `arena check`: p99 0.109 ms, max 0.67 ms, 0% over 1 ms (v4b: p99 0.377, 0.33% over 1 ms). Strict run: see 08 `cfc-v5-strict` |
| v6 `cap-floor-count-v6` | v5 + no limping with class-1 hands (marginal hands only see a free flop from the BB); VPIP 63% → 39% | vs v5: **+0.79 ±0.79 (p=0.050, seed cfc6)** and **+0.92 ±0.78 (p=0.021, seed cfc7)**, 1176/1163 pairs, field = other agents' bots + examples, 0 failures; W$SD 54% vs 49% |
| v6 vs current submission (`cfc-v6-vs-bot`, seed cfc8, 1179 pairs) | — | **+2.85 ±1.09, p<0.001**, 0 failures |
| v6 strict mode (`cfc-v6-strict2`, WSL BotPool, 32 tables) | — | 0 timeouts / 0 errors; p99 12.0 ms = lowest at the table (check_or_fold 15.7, v0-nowar 15.1) on a slow WSL pipe; first attempt `cfc-v6-strict` was contaminated by a machine-wide stall (every bot 1 timeout) |
| `v0-nowar` (control, not this strategy) | v0 + preflop 3-bet cap only | vs bot, pool (cfc3, 400 pairs): **+5.33 ±2.02, p<0.001** |

**Best version: `cap-floor-count-v6`** (v4b's postflop + GC tuning + no marginal limps). `v5` is the pure-postflop version (same preflop as `bot/`) if the preflop change is wanted separately. (preflop cap + bet-size-aware cap/floor/count). Robustness and strict-timing runs are logged in strategy/08-experiments.md.

## Late experiments (2026-11-07, "try new things")

| bot | idea | result vs base |
|---|---|---|
| `cfc-v7-expose` | hide-strength exposure (never expose the pairing/suited card, else show high) | vs v6: +0.10 ±0.48, 942/1175 tied — **null**; exposure rules do not move points against non-readers |
| `cfc-v7-steal` | 100-byte per-seat memory: steal blinds from tight folders, probe lone never-bettors | vs v6 pool field: −0.03 ±0.17 (never fires); pure-folder field: **+0.71 ±0.43, p=0.001** — works only when the table is full of folders |
| `cfc-v8-position` | class-1 opens from the last two seats when folded to | vs v6: +0.23 ±0.51 — n.s. |
| `fp-cfc` | fp-v3 preflop/select/ICM + this postflop module transplanted (verified identical on 4,000 states) | vs fp-v3: −0.75 ±1.00 (p=0.14) — **not better**; fp-v3's tiers are at least as good |
| `fp-cfc2` | fp-v3 + only the certain-math overrides (beat every cap → value; below a floor → never pay off) | vs fp-v3: **+1.10 ±0.44 (p<0.001)** and **+0.82 ±0.35 (p<0.001)** on two seeds/fields — the module's certain-math core does add to fp-v3 |

Conclusion for the final round: **`bots/fp-cfc2`** (fp-v3 + cap/floor overrides) is the recommended upload; the full count module did not beat fp-v3's tiers, its certain-math core did.
