# Arena run `ladder` — fast mode

Started 2026-11-06T19:12:25 · seed `159b1b60` · scheme league · 203 tables · 15535 hands · 3.6 s

Command: `watch --interval 30 --tables 200 --agent arena-watch --question auto-ladder-on-bots-change`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 152 | 232 | 23.49 | 1.25 | 2.54 | 88% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.061 | 13.47 | 0 |
| 2 | **bot** | 146 | 232 | 13.58 | 2.66 | 4.46 | 34% | 22% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.217 | 7.44 | 0 |
| 3 | **v0-baseline** | 158 | 232 | 12.97 | 2.46 | 4.25 | 37% | 17% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.328 | 17.55 | 0 |
| 4 | **cap-floor-count** | 150 | 232 | 12.33 | 2.52 | 4.46 | 32% | 18% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.493 | 38.50 | 0 |
| 5 | **keep-made-plus-draw** | 157 | 232 | 11.90 | 2.39 | 4.38 | 34% | 15% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.669 | 3.50 | 0 |
| 6 | **icm-pushfold** | 152 | 232 | 11.55 | 2.35 | 4.43 | 33% | 14% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.306 | 2.29 | 0 |
| 7 | **min_raiser** | 149 | 232 | 1.68 | 1.09 | 6.19 | 4% | 3% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.063 | 0.92 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 58% | 30% | 11% | 1% | 0% | 0% | 0% |
| bot | 22% | 3% | 9% | 12% | 14% | 16% | 14% | 9% |
| v0-baseline | 17% | 6% | 14% | 19% | 11% | 16% | 11% | 6% |
| cap-floor-count | 18% | 6% | 9% | 13% | 18% | 15% | 14% | 7% |
| keep-made-plus-draw | 15% | 6% | 13% | 12% | 22% | 16% | 13% | 4% |
| icm-pushfold | 14% | 8% | 11% | 14% | 19% | 15% | 13% | 6% |
| min_raiser | 3% | 0% | 1% | 7% | 15% | 30% | 23% | 21% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | bot | v0-baseline | cap-floor-count | keep-made-plus-draw | icm-pushfold | min_raiser |
|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 65-0-42 | 80-0-36 | 79-0-31 | 84-0-32 | 87-0-22 | 102-0-4 |
| **bot** | 42-0-65 | · | 52-2-57 | 63-0-43 | 60-2-50 | 60-0-49 | 74-2-23 |
| **v0-baseline** | 36-0-80 | 57-2-52 | · | 58-1-57 | 69-0-53 | 57-1-57 | 97-4-13 |
| **cap-floor-count** | 31-0-79 | 43-0-63 | 57-1-58 | · | 54-0-55 | 56-0-49 | 98-1-13 |
| **keep-made-plus-draw** | 32-0-84 | 50-2-60 | 53-0-69 | 55-0-54 | · | 53-0-62 | 97-2-13 |
| **icm-pushfold** | 22-0-87 | 49-0-60 | 57-1-57 | 49-0-56 | 62-0-53 | · | 87-4-20 |
| **min_raiser** | 4-0-102 | 23-2-74 | 13-4-97 | 13-1-98 | 13-2-97 | 20-4-87 | · |

Files: `arena/results/20261106-191225-ladder-0fbc` (tables.jsonl, seats.csv, summary.json, run.json).
