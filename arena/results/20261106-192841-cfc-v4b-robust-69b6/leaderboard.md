# Arena run `cfc-v4b-robust` — fast mode

Started 2026-11-06T19:28:41 · seed `cfc5` · scheme ab · 3206 tables · 272567 hands · 53.0 s

Command: `ab bots/v0-nowar bots/cap-floor-count-v4b --field keep-made-plus-draw keep-made-plus-draw-v2 v0-baseline icm-pushfold min_raiser check_or_fold --tables 1600 --seed cfc5 --agent Claude(cap-floor-count-agent) --name cfc-v4b-robust --question robustness: v4b vs v0-nowar, field without my own older versions, new seed`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cap-floor-count-v4b` replaces `v0-nowar` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1167 | 15.54 | 16.99 | +1.46 | ±1.04 | 0.006 | 327 / 594 / 246 | **cap-floor-count-v4b is better** |

Pairs needed to resolve a 1-point difference at this variance: ~1256.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 2326 | 3664 | 22.31 | 0.32 | 2.66 | 86% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.227 | 18.85 | 0 |
| 2 | **cap-floor-count-v4b** | 1167 | 1832 | 16.57 | 0.93 | 3.70 | 45% | 21% | 0.0000 | 0 | 0 | 0 | 0.019 | 2.713 | 67.20 | 0 |
| 3 | **v0-nowar** | 1167 | 1832 | 15.17 | 0.89 | 3.78 | 43% | 18% | 0.0000 | 0 | 0 | 0 | 0.018 | 1.387 | 36.13 | 0 |
| 4 | **keep-made-plus-draw-v2** | 2328 | 3664 | 12.84 | 0.64 | 4.42 | 33% | 19% | 0.0000 | 0 | 0 | 0 | 0.018 | 1.691 | 32.07 | 0 |
| 5 | **keep-made-plus-draw** | 2314 | 3664 | 12.64 | 0.63 | 4.49 | 33% | 18% | 0.0000 | 0 | 0 | 0 | 0.018 | 1.640 | 63.66 | 0 |
| 6 | **v0-baseline** | 2364 | 3664 | 11.76 | 0.62 | 4.54 | 31% | 17% | 0.0000 | 1 | 0 | 0 | 0.017 | 1.238 | 24.23 | 0 |
| 7 | **icm-pushfold** | 2338 | 3664 | 10.15 | 0.56 | 4.58 | 30% | 11% | 0.0000 | 1 | 0 | 0 | 0.029 | 3.498 | 124.37 | 0 |
| 8 | **min_raiser** | 2390 | 3664 | 1.92 | 0.29 | 6.41 | 5% | 3% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.249 | 6.30 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 51% | 36% | 11% | 2% | 0% | 0% | 0% |
| cap-floor-count-v4b | 21% | 12% | 12% | 18% | 16% | 11% | 7% | 3% |
| v0-nowar | 18% | 12% | 13% | 21% | 16% | 10% | 7% | 3% |
| keep-made-plus-draw-v2 | 19% | 6% | 9% | 12% | 17% | 17% | 14% | 6% |
| keep-made-plus-draw | 18% | 5% | 10% | 11% | 16% | 18% | 14% | 8% |
| v0-baseline | 17% | 6% | 8% | 14% | 15% | 18% | 16% | 7% |
| icm-pushfold | 11% | 7% | 11% | 15% | 18% | 17% | 14% | 6% |
| min_raiser | 3% | 0% | 2% | 5% | 9% | 24% | 33% | 24% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | cap-floor-count-v4b | v0-nowar | keep-made-plus-draw-v2 | keep-made-plus-draw | v0-baseline | icm-pushfold | min_raiser |
|---|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 466-0-345 | 492-0-319 | 1076-0-580 | 1087-0-529 | 1168-0-486 | 1257-0-401 | 1590-0-80 |
| **cap-floor-count-v4b** | 345-0-466 | · | 0-0-0 | 497-0-318 | 491-0-316 | 537-0-312 | 513-1-312 | 807-2-31 |
| **v0-nowar** | 319-0-492 | 0-0-0 | · | 474-0-341 | 483-0-324 | 511-0-338 | 506-0-320 | 791-1-48 |
| **keep-made-plus-draw-v2** | 580-0-1076 | 318-0-497 | 341-0-474 | · | 801-14-793 | 862-0-816 | 881-4-761 | 1374-50-264 |
| **keep-made-plus-draw** | 529-0-1087 | 316-0-491 | 324-0-483 | 793-14-801 | · | 845-16-791 | 873-6-757 | 1396-42-232 |
| **v0-baseline** | 486-0-1168 | 312-0-537 | 338-0-511 | 816-0-862 | 791-16-845 | · | 839-0-823 | 1397-40-251 |
| **icm-pushfold** | 401-0-1257 | 312-1-513 | 320-0-506 | 761-4-881 | 757-6-873 | 823-0-839 | · | 1408-18-278 |
| **min_raiser** | 80-0-1590 | 31-2-807 | 48-1-791 | 264-50-1374 | 232-42-1396 | 251-40-1397 | 278-18-1408 | · |

Files: `arena/results/20261106-192841-cfc-v4b-robust-69b6` (tables.jsonl, seats.csv, summary.json, run.json).
