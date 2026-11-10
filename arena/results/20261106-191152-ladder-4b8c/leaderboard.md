# Arena run `ladder` — fast mode

Started 2026-11-06T19:11:52 · seed `8acea25d` · scheme league · 203 tables · 15226 hands · 3.5 s

Command: `watch --interval 30 --tables 200 --agent arena-watch --question auto-ladder-on-bots-change`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 151 | 232 | 23.75 | 1.20 | 2.54 | 90% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.049 | 2.86 | 0 |
| 2 | **keep-made-plus-draw** | 149 | 232 | 13.66 | 2.57 | 4.22 | 37% | 19% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.162 | 7.70 | 0 |
| 3 | **icm-pushfold** | 159 | 232 | 12.84 | 2.45 | 4.27 | 36% | 16% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.216 | 4.67 | 0 |
| 4 | **cap-floor-count** | 151 | 232 | 12.37 | 2.54 | 4.39 | 32% | 19% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.407 | 13.32 | 0 |
| 5 | **v0-baseline** | 153 | 232 | 12.07 | 2.41 | 4.46 | 34% | 16% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.382 | 9.10 | 0 |
| 6 | **bot** | 143 | 232 | 10.65 | 2.38 | 4.57 | 29% | 15% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.238 | 2.26 | 0 |
| 7 | **min_raiser** | 152 | 232 | 2.16 | 1.21 | 6.20 | 6% | 3% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.030 | 0.33 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 58% | 31% | 8% | 2% | 0% | 0% | 0% |
| keep-made-plus-draw | 19% | 5% | 12% | 16% | 15% | 13% | 15% | 4% |
| icm-pushfold | 16% | 9% | 11% | 15% | 17% | 16% | 10% | 6% |
| cap-floor-count | 19% | 4% | 9% | 15% | 17% | 19% | 12% | 5% |
| v0-baseline | 16% | 6% | 12% | 13% | 16% | 16% | 13% | 7% |
| bot | 15% | 3% | 10% | 16% | 18% | 18% | 15% | 6% |
| min_raiser | 3% | 1% | 1% | 7% | 9% | 31% | 29% | 19% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | keep-made-plus-draw | icm-pushfold | cap-floor-count | v0-baseline | bot | min_raiser |
|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 73-0-33 | 83-0-31 | 72-0-37 | 79-0-32 | 74-0-28 | 105-0-4 |
| **keep-made-plus-draw** | 33-0-73 | · | 58-1-53 | 60-0-47 | 55-1-54 | 55-2-46 | 97-2-14 |
| **icm-pushfold** | 31-0-83 | 53-1-58 | · | 53-1-57 | 58-1-57 | 54-0-54 | 97-3-19 |
| **cap-floor-count** | 37-0-72 | 47-0-60 | 57-1-53 | · | 57-0-56 | 52-0-51 | 96-1-10 |
| **v0-baseline** | 32-0-79 | 54-1-55 | 57-1-58 | 56-0-57 | · | 50-0-53 | 84-6-18 |
| **bot** | 28-0-74 | 46-2-55 | 54-0-54 | 51-0-52 | 53-0-50 | · | 80-5-19 |
| **min_raiser** | 4-0-105 | 14-2-97 | 19-3-97 | 10-1-96 | 18-6-84 | 19-5-80 | · |

Files: `arena/results/20261106-191152-ladder-4b8c` (tables.jsonl, seats.csv, summary.json, run.json).
