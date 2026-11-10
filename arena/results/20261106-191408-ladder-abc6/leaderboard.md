# Arena run `ladder` — fast mode

Started 2026-11-06T19:14:08 · seed `9ff1d0e0` · scheme league · 203 tables · 15888 hands · 6.6 s

Command: `watch --interval 30 --tables 200 --agent arena-watch --question auto-ladder-on-bots-change`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 149 | 232 | 23.19 | 1.26 | 2.57 | 88% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.196 | 4.34 | 0 |
| 2 | **keep-made-plus-draw** | 149 | 232 | 14.78 | 2.65 | 4.09 | 39% | 22% | 0.0000 | 0 | 0 | 0 | 0.019 | 0.471 | 6.80 | 0 |
| 3 | **icm-pushfold** | 146 | 232 | 13.28 | 2.45 | 4.22 | 37% | 16% | 0.0000 | 0 | 0 | 0 | 0.029 | 2.630 | 26.73 | 0 |
| 4 | **v0-baseline** | 151 | 232 | 12.93 | 2.54 | 4.38 | 34% | 19% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.342 | 4.14 | 0 |
| 5 | **bot** | 150 | 232 | 11.81 | 2.43 | 4.43 | 32% | 16% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.189 | 20.53 | 0 |
| 6 | **cap-floor-count** | 152 | 232 | 10.65 | 2.38 | 4.61 | 29% | 15% | 0.0000 | 0 | 0 | 0 | 0.020 | 0.962 | 37.99 | 0 |
| 7 | **min_raiser** | 148 | 232 | 0.86 | 0.70 | 6.47 | 3% | 1% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.240 | 0.73 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 56% | 32% | 11% | 1% | 0% | 0% | 0% |
| keep-made-plus-draw | 22% | 6% | 12% | 15% | 17% | 15% | 10% | 5% |
| icm-pushfold | 16% | 12% | 9% | 14% | 17% | 16% | 12% | 4% |
| v0-baseline | 19% | 5% | 11% | 12% | 19% | 16% | 13% | 6% |
| bot | 16% | 6% | 11% | 18% | 14% | 16% | 12% | 8% |
| cap-floor-count | 15% | 3% | 10% | 15% | 18% | 16% | 17% | 6% |
| min_raiser | 1% | 0% | 2% | 3% | 12% | 26% | 34% | 21% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | keep-made-plus-draw | icm-pushfold | v0-baseline | bot | cap-floor-count | min_raiser |
|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 59-0-46 | 76-0-28 | 75-0-29 | 77-0-32 | 78-0-28 | 102-0-2 |
| **keep-made-plus-draw** | 46-0-59 | · | 53-0-51 | 60-0-46 | 52-1-54 | 66-1-41 | 88-5-8 |
| **icm-pushfold** | 28-0-76 | 51-0-53 | · | 68-0-44 | 57-0-46 | 63-0-47 | 88-2-8 |
| **v0-baseline** | 29-0-75 | 46-0-60 | 44-0-68 | · | 53-1-53 | 61-1-44 | 93-4-10 |
| **bot** | 32-0-77 | 54-1-52 | 46-0-57 | 53-1-53 | · | 57-2-53 | 92-3-11 |
| **cap-floor-count** | 28-0-78 | 41-1-66 | 47-0-63 | 44-1-61 | 53-2-57 | · | 91-4-16 |
| **min_raiser** | 2-0-102 | 8-5-88 | 8-2-88 | 10-4-93 | 11-3-92 | 16-4-91 | · |

Files: `arena/results/20261106-191408-ladder-abc6` (tables.jsonl, seats.csv, summary.json, run.json).
