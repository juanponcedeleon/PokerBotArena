# Arena run `cfc-v2-ab-pool` — fast mode

Started 2026-11-06T19:19:05 · seed `cfc2` · scheme ab · 804 tables · 44960 hands · 15.1 s

Command: `ab bot bots/cap-floor-count-v2 --all --tables 400 --seed cfc2 --log --name cfc-v2-ab-pool --agent Claude (cap-floor-count agent) --question v2: count conditioned on street aggression (alpha 0.75/0.90), v0-level value betting; vs bot v0 in pool field`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cap-floor-count-v2` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 329 | 11.34 | 11.00 | -0.34 | ±1.43 | 0.637 | 61 / 204 / 64 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~673.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **keep-made-plus-draw** | 674 | 1072 | 14.46 | 1.17 | 4.36 | 40% | 18% | 0.0000 | 0 | 0 | 0 | 0.021 | 0.585 | 66.05 | 0 |
| 2 | **cap-floor-count** | 652 | 1072 | 12.56 | 1.08 | 4.46 | 37% | 13% | 0.0000 | 0 | 0 | 0 | 0.021 | 1.048 | 64.17 | 0 |
| 3 | **keep-made-plus-draw-v2** | 676 | 1072 | 12.55 | 1.08 | 4.49 | 37% | 13% | 0.0000 | 0 | 0 | 0 | 0.021 | 0.543 | 32.00 | 0 |
| 4 | **icm-pushfold** | 690 | 1072 | 12.27 | 0.98 | 4.36 | 41% | 8% | 0.0000 | 0 | 0 | 0 | 0.035 | 9.623 | 66.60 | 0 |
| 5 | **v0-baseline** | 668 | 1072 | 11.85 | 1.04 | 4.55 | 36% | 11% | 0.0000 | 0 | 0 | 0 | 0.021 | 0.333 | 18.46 | 0 |
| 6 | **bot** | 329 | 536 | 11.57 | 1.51 | 4.65 | 34% | 13% | 0.0000 | 0 | 0 | 0 | 0.021 | 0.411 | 38.56 | 0 |
| 7 | **cap-floor-count-v2** | 329 | 536 | 11.08 | 1.47 | 4.66 | 33% | 11% | 0.0000 | 0 | 0 | 0 | 0.021 | 1.311 | 43.27 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| keep-made-plus-draw | 18% | 10% | 12% | 10% | 12% | 13% | 13% | 11% |
| cap-floor-count | 13% | 12% | 12% | 14% | 12% | 12% | 15% | 10% |
| keep-made-plus-draw-v2 | 13% | 11% | 13% | 13% | 11% | 14% | 14% | 11% |
| icm-pushfold | 8% | 18% | 15% | 13% | 13% | 12% | 12% | 9% |
| v0-baseline | 11% | 14% | 11% | 13% | 14% | 12% | 13% | 12% |
| bot | 13% | 9% | 12% | 13% | 13% | 13% | 15% | 12% |
| cap-floor-count-v2 | 11% | 11% | 11% | 13% | 13% | 14% | 16% | 11% |

## Head-to-head (row finished above column: wins-ties-losses)

| | keep-made-plus-draw | cap-floor-count | keep-made-plus-draw-v2 | icm-pushfold | v0-baseline | bot | cap-floor-count-v2 |
|---|---|---|---|---|---|---|---|
| **keep-made-plus-draw** | · | 271-0-263 | 301-0-253 | 323-0-253 | 279-0-265 | 152-0-119 | 153-0-118 |
| **cap-floor-count** | 263-0-271 | · | 272-2-268 | 295-0-261 | 283-0-251 | 128-2-129 | 128-2-129 |
| **keep-made-plus-draw-v2** | 253-0-301 | 268-2-272 | · | 288-0-280 | 290-2-262 | 146-0-130 | 151-0-125 |
| **icm-pushfold** | 253-0-323 | 261-0-295 | 280-0-288 | · | 296-0-264 | 153-0-128 | 150-1-130 |
| **v0-baseline** | 265-0-279 | 251-0-283 | 262-2-290 | 264-0-296 | · | 148-0-120 | 148-1-119 |
| **bot** | 119-0-152 | 129-2-128 | 130-0-146 | 128-0-153 | 120-0-148 | · | 0-0-0 |
| **cap-floor-count-v2** | 118-0-153 | 129-2-128 | 125-0-151 | 130-1-150 | 119-1-148 | 0-0-0 | · |

Files: `arena/results/20261106-191905-cfc-v2-ab-pool-886b` (tables.jsonl, seats.csv, summary.json, run.json).
