# Arena run `cfc-v3-ab-pool` — fast mode

Started 2026-11-06T19:21:31 · seed `cfc3` · scheme ab · 800 tables · 52682 hands · 11.8 s

Command: `ab bot bots/cap-floor-count-v3 --all --tables 400 --seed cfc3 --agent Claude(cap-floor-count-agent) --name cfc-v3-ab-pool --question v3 = v2 postflop + preflop cap vs bot v0 (pool field)`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cap-floor-count-v3` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 400 | 12.62 | 14.28 | +1.65 | ±2.19 | 0.139 | 115 / 195 / 90 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~1906.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **v0-nowar** | 800 | 800 | 18.09 | 1.23 | 3.51 | 57% | 14% | 0.0000 | 0 | 0 | 0 | 0.019 | 0.472 | 3.98 | 0 |
| 2 | **cap-floor-count-v3** | 400 | 400 | 14.28 | 1.75 | 3.96 | 44% | 12% | 0.0000 | 0 | 0 | 0 | 0.020 | 2.104 | 6.38 | 0 |
| 3 | **bot** | 400 | 400 | 12.62 | 1.82 | 4.55 | 36% | 14% | 0.0000 | 0 | 0 | 0 | 0.019 | 0.338 | 3.70 | 0 |
| 4 | **keep-made-plus-draw-v2** | 800 | 800 | 12.21 | 1.27 | 4.55 | 35% | 14% | 0.0000 | 0 | 0 | 0 | 0.019 | 0.717 | 4.53 | 0 |
| 5 | **icm-pushfold** | 800 | 800 | 11.70 | 1.16 | 4.38 | 38% | 9% | 0.0000 | 0 | 0 | 0 | 0.032 | 2.019 | 5.98 | 0 |
| 6 | **cap-floor-count-v2** | 800 | 800 | 11.65 | 1.25 | 4.66 | 34% | 13% | 0.0000 | 0 | 0 | 0 | 0.018 | 1.825 | 4.24 | 0 |
| 7 | **keep-made-plus-draw** | 800 | 800 | 11.07 | 1.21 | 4.83 | 33% | 12% | 0.0000 | 0 | 0 | 0 | 0.019 | 1.190 | 3.66 | 0 |
| 8 | **v0-baseline** | 800 | 800 | 11.01 | 1.24 | 4.77 | 31% | 13% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.828 | 4.38 | 0 |
| 9 | **cap-floor-count** | 800 | 800 | 10.81 | 1.20 | 4.87 | 32% | 12% | 0.0000 | 0 | 0 | 0 | 0.019 | 1.631 | 6.33 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| v0-nowar | 14% | 24% | 20% | 15% | 10% | 8% | 5% | 5% |
| cap-floor-count-v3 | 12% | 18% | 14% | 18% | 12% | 11% | 8% | 6% |
| bot | 14% | 10% | 12% | 10% | 14% | 14% | 14% | 12% |
| keep-made-plus-draw-v2 | 14% | 10% | 10% | 14% | 13% | 12% | 14% | 12% |
| icm-pushfold | 9% | 15% | 14% | 14% | 16% | 13% | 10% | 9% |
| cap-floor-count-v2 | 13% | 11% | 10% | 11% | 14% | 15% | 17% | 10% |
| keep-made-plus-draw | 12% | 10% | 11% | 12% | 9% | 14% | 14% | 18% |
| v0-baseline | 13% | 7% | 11% | 10% | 16% | 15% | 15% | 13% |
| cap-floor-count | 12% | 9% | 11% | 10% | 12% | 14% | 16% | 16% |

## Head-to-head (row finished above column: wins-ties-losses)

| | v0-nowar | cap-floor-count-v3 | bot | keep-made-plus-draw-v2 | icm-pushfold | cap-floor-count-v2 | keep-made-plus-draw | v0-baseline | cap-floor-count |
|---|---|---|---|---|---|---|---|---|---|
| **v0-nowar** | · | 225-2-173 | 254-3-143 | 507-1-292 | 489-4-307 | 501-5-294 | 515-4-281 | 533-2-265 | 544-1-255 |
| **cap-floor-count-v3** | 173-2-225 | · | 0-0-0 | 227-2-171 | 220-2-178 | 237-4-159 | 251-2-147 | 244-3-153 | 247-1-152 |
| **bot** | 143-3-254 | 0-0-0 | · | 202-3-195 | 181-3-216 | 208-2-190 | 213-3-184 | 205-5-190 | 203-4-193 |
| **keep-made-plus-draw-v2** | 292-1-507 | 171-2-227 | 195-3-202 | · | 386-3-411 | 403-3-394 | 420-4-376 | 420-6-374 | 451-1-348 |
| **icm-pushfold** | 307-4-489 | 178-2-220 | 216-3-181 | 411-3-386 | · | 426-5-369 | 452-6-342 | 442-4-354 | 432-2-366 |
| **cap-floor-count-v2** | 294-5-501 | 159-4-237 | 190-2-208 | 394-3-403 | 369-5-426 | · | 418-4-378 | 396-8-396 | 419-5-376 |
| **keep-made-plus-draw** | 281-4-515 | 147-2-251 | 184-3-213 | 376-4-420 | 342-6-452 | 378-4-418 | · | 394-12-394 | 391-6-403 |
| **v0-baseline** | 265-2-533 | 153-3-244 | 190-5-205 | 374-6-420 | 354-4-442 | 396-8-396 | 394-12-394 | · | 409-12-379 |
| **cap-floor-count** | 255-1-544 | 152-1-247 | 193-4-203 | 348-1-451 | 366-2-432 | 376-5-419 | 403-6-391 | 379-12-409 | · |

Files: `arena/results/20261106-192131-cfc-v3-ab-pool-dffd` (tables.jsonl, seats.csv, summary.json, run.json).
