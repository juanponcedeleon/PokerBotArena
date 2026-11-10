# Arena run `ladder` — fast mode

Started 2026-11-06T19:18:19 · seed `12c4e81d` · scheme league · 207 tables · 15129 hands · 23.9 s

Command: `watch --interval 30 --tables 200 --agent arena-watch --question auto-ladder-on-bots-change`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 123 | 184 | 24.67 | 1.25 | 2.46 | 92% | 0% | 0.0000 | 0 | 0 | 0 | 0.006 | 0.149 | 16.22 | 0 |
| 2 | **v0-baseline** | 135 | 184 | 14.73 | 2.89 | 4.21 | 40% | 19% | 0.0000 | 0 | 0 | 0 | 0.024 | 12.319 | 22.30 | 0 |
| 3 | **cap-floor-count-v2** | 126 | 184 | 13.91 | 2.91 | 4.25 | 37% | 20% | 0.0002 | 2 | 0 | 0 | 0.025 | 19.448 | 24.25 | 0 |
| 4 | **keep-made-plus-draw** | 130 | 184 | 12.66 | 2.74 | 4.45 | 36% | 16% | 0.0000 | 0 | 0 | 0 | 0.025 | 19.036 | 48.16 | 0 |
| 5 | **icm-pushfold** | 132 | 184 | 11.52 | 2.58 | 4.28 | 34% | 12% | 0.0017 | 21 | 0 | 0 | 0.040 | 21.868 | 40.35 | 0 |
| 6 | **bot** | 130 | 184 | 11.36 | 2.71 | 4.55 | 31% | 15% | 0.0000 | 0 | 0 | 0 | 0.024 | 13.223 | 20.98 | 0 |
| 7 | **cap-floor-count** | 126 | 184 | 10.98 | 2.77 | 4.69 | 28% | 17% | 0.0003 | 3 | 0 | 0 | 0.024 | 15.139 | 33.13 | 0 |
| 8 | **keep-made-plus-draw-v2** | 136 | 184 | 10.98 | 2.49 | 4.45 | 34% | 11% | 0.0001 | 1 | 0 | 0 | 0.024 | 14.677 | 37.68 | 0 |
| 9 | **min_raiser** | 133 | 184 | 1.68 | 1.18 | 6.33 | 5% | 2% | 0.0000 | 0 | 0 | 0 | 0.006 | 0.210 | 14.18 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 63% | 29% | 8% | 1% | 0% | 0% | 0% |
| v0-baseline | 19% | 10% | 11% | 10% | 13% | 17% | 15% | 4% |
| cap-floor-count-v2 | 20% | 7% | 11% | 15% | 16% | 13% | 12% | 7% |
| keep-made-plus-draw | 16% | 8% | 12% | 14% | 12% | 16% | 14% | 9% |
| icm-pushfold | 12% | 9% | 12% | 20% | 16% | 15% | 10% | 5% |
| bot | 15% | 6% | 10% | 16% | 15% | 14% | 18% | 7% |
| cap-floor-count | 17% | 3% | 9% | 11% | 21% | 15% | 18% | 7% |
| keep-made-plus-draw-v2 | 11% | 7% | 16% | 16% | 12% | 21% | 12% | 5% |
| min_raiser | 2% | 1% | 2% | 4% | 15% | 21% | 34% | 21% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | v0-baseline | cap-floor-count-v2 | keep-made-plus-draw | icm-pushfold | bot | cap-floor-count | keep-made-plus-draw-v2 | min_raiser |
|---|---|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 53-0-25 | 53-0-21 | 58-0-17 | 64-0-16 | 50-0-14 | 54-0-19 | 61-0-14 | 71-0-2 |
| **v0-baseline** | 25-0-53 | · | 36-1-43 | 47-2-37 | 33-0-45 | 49-1-36 | 41-1-35 | 53-0-28 | 69-3-12 |
| **cap-floor-count-v2** | 21-0-53 | 43-1-36 | · | 42-0-36 | 47-0-34 | 37-1-34 | 39-1-32 | 44-0-37 | 67-3-7 |
| **keep-made-plus-draw** | 17-0-58 | 37-2-47 | 36-0-42 | · | 44-0-34 | 46-1-37 | 40-1-36 | 47-0-32 | 63-1-12 |
| **icm-pushfold** | 16-0-64 | 45-0-33 | 34-0-47 | 34-0-44 | · | 40-0-35 | 53-0-30 | 45-0-42 | 71-1-10 |
| **bot** | 14-0-50 | 36-1-49 | 34-1-37 | 37-1-46 | 35-0-40 | · | 39-0-39 | 36-1-48 | 58-6-12 |
| **cap-floor-count** | 19-0-54 | 35-1-41 | 32-1-39 | 36-1-40 | 30-0-53 | 39-0-39 | · | 38-1-39 | 54-5-12 |
| **keep-made-plus-draw-v2** | 14-0-61 | 28-0-53 | 37-0-44 | 32-0-47 | 42-0-45 | 48-1-36 | 39-1-38 | · | 71-4-10 |
| **min_raiser** | 2-0-71 | 12-3-69 | 7-3-67 | 12-1-63 | 10-1-71 | 12-6-58 | 12-5-54 | 10-4-71 | · |

Files: `arena/results/20261106-191819-ladder-c741` (tables.jsonl, seats.csv, summary.json, run.json).
