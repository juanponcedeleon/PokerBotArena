# Arena run `cfc-v6-vs-v5` — fast mode

Started 2026-11-06T19:39:08 · seed `cfc6` · scheme ab · 3206 tables · 290654 hands · 62.7 s

Command: `ab bots/cap-floor-count-v5 bots/cap-floor-count-v6 --field keep-made-plus-draw keep-made-plus-draw-v2 v0-baseline icm-pushfold min_raiser check_or_fold --tables 1600 --seed cfc6 --log --agent Claude(cap-floor-count-agent) --question v6 (v5 without class-1 limps, VPIP ~61% -> ~40%) vs v5: does preflop tightening add to the postflop module? --name cfc-v6-vs-v5`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cap-floor-count-v6` replaces `cap-floor-count-v5` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1176 | 18.46 | 19.25 | +0.79 | ±0.79 | 0.050 | 235 / 760 / 181 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~731.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 2360 | 3664 | 21.46 | 0.34 | 2.72 | 84% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.084 | 59.44 | 0 |
| 2 | **cap-floor-count-v6** | 1176 | 1832 | 18.55 | 0.92 | 3.49 | 52% | 21% | 0.0000 | 0 | 0 | 0 | 0.019 | 3.152 | 31.05 | 0 |
| 3 | **cap-floor-count-v5** | 1176 | 1832 | 17.83 | 0.93 | 3.59 | 49% | 23% | 0.0000 | 0 | 0 | 0 | 0.019 | 2.806 | 33.72 | 0 |
| 4 | **keep-made-plus-draw-v2** | 2356 | 3664 | 12.47 | 0.64 | 4.51 | 32% | 18% | 0.0000 | 0 | 0 | 0 | 0.018 | 2.129 | 78.22 | 0 |
| 5 | **v0-baseline** | 2396 | 3664 | 11.98 | 0.63 | 4.54 | 30% | 18% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.967 | 24.89 | 0 |
| 6 | **keep-made-plus-draw** | 2370 | 3664 | 11.35 | 0.61 | 4.57 | 30% | 16% | 0.0000 | 0 | 0 | 0 | 0.018 | 1.972 | 27.76 | 0 |
| 7 | **icm-pushfold** | 2352 | 3664 | 10.63 | 0.57 | 4.57 | 31% | 12% | 0.0000 | 0 | 0 | 0 | 0.029 | 4.974 | 36.79 | 0 |
| 8 | **min_raiser** | 2342 | 3664 | 1.42 | 0.24 | 6.40 | 4% | 2% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.366 | 10.40 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 47% | 38% | 13% | 2% | 0% | 0% | 0% |
| cap-floor-count-v6 | 21% | 17% | 13% | 15% | 15% | 10% | 6% | 2% |
| cap-floor-count-v5 | 23% | 13% | 13% | 17% | 15% | 10% | 7% | 3% |
| keep-made-plus-draw-v2 | 18% | 6% | 8% | 13% | 15% | 18% | 14% | 8% |
| v0-baseline | 18% | 5% | 7% | 13% | 16% | 19% | 14% | 8% |
| keep-made-plus-draw | 16% | 6% | 9% | 13% | 18% | 16% | 15% | 7% |
| icm-pushfold | 12% | 8% | 11% | 15% | 17% | 17% | 14% | 7% |
| min_raiser | 2% | 1% | 2% | 5% | 11% | 24% | 32% | 23% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | cap-floor-count-v6 | cap-floor-count-v5 | keep-made-plus-draw-v2 | v0-baseline | keep-made-plus-draw | icm-pushfold | min_raiser |
|---|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 420-0-419 | 452-0-387 | 1144-0-538 | 1160-0-560 | 1165-0-511 | 1218-0-450 | 1602-0-60 |
| **cap-floor-count-v6** | 419-0-420 | · | 0-0-0 | 525-1-315 | 554-1-285 | 554-0-296 | 531-0-296 | 802-1-31 |
| **cap-floor-count-v5** | 387-0-452 | 0-0-0 | · | 523-1-317 | 540-1-299 | 550-0-300 | 538-0-289 | 796-1-37 |
| **keep-made-plus-draw-v2** | 538-0-1144 | 315-1-525 | 317-1-523 | · | 849-7-838 | 883-8-801 | 886-2-802 | 1358-48-256 |
| **v0-baseline** | 560-0-1160 | 285-1-554 | 299-1-540 | 838-7-849 | · | 862-12-850 | 905-2-809 | 1401-46-273 |
| **keep-made-plus-draw** | 511-0-1165 | 296-0-554 | 300-0-550 | 801-8-883 | 850-12-862 | · | 834-0-842 | 1382-50-264 |
| **icm-pushfold** | 450-0-1218 | 296-0-531 | 289-0-538 | 802-2-886 | 809-2-905 | 842-0-834 | · | 1419-16-233 |
| **min_raiser** | 60-0-1602 | 31-1-802 | 37-1-796 | 256-48-1358 | 273-46-1401 | 264-50-1382 | 233-16-1419 | · |

Files: `arena/results/20261106-193908-cfc-v6-vs-v5-65b6` (tables.jsonl, seats.csv, summary.json, run.json).
