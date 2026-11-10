# Arena run `ladder` — fast mode

Started 2026-11-06T19:19:54 · seed `e08b1593` · scheme league · 207 tables · 15072 hands · 5.2 s

Command: `watch --interval 30 --tables 200 --agent arena-watch --question auto-ladder-on-bots-change`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 139 | 184 | 26.03 | 1.00 | 2.36 | 96% | 0% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.240 | 18.50 | 0 |
| 2 | **keep-made-plus-draw-v2** | 127 | 184 | 14.08 | 2.78 | 4.10 | 41% | 17% | 0.0000 | 0 | 0 | 0 | 0.021 | 1.095 | 5.71 | 0 |
| 3 | **cap-floor-count-v2** | 132 | 184 | 13.21 | 2.81 | 4.31 | 36% | 17% | 0.0000 | 0 | 0 | 0 | 0.022 | 2.958 | 3.99 | 0 |
| 4 | **v0-baseline** | 132 | 184 | 13.15 | 2.87 | 4.34 | 35% | 18% | 0.0000 | 0 | 0 | 0 | 0.021 | 2.407 | 3.58 | 0 |
| 5 | **keep-made-plus-draw** | 132 | 184 | 12.50 | 2.85 | 4.37 | 33% | 18% | 0.0000 | 0 | 0 | 0 | 0.021 | 1.456 | 3.55 | 0 |
| 6 | **bot** | 127 | 184 | 11.20 | 2.61 | 4.64 | 33% | 14% | 0.0000 | 0 | 0 | 0 | 0.021 | 1.431 | 3.44 | 0 |
| 7 | **cap-floor-count** | 134 | 184 | 10.98 | 2.64 | 4.59 | 31% | 14% | 0.0000 | 0 | 0 | 0 | 0.022 | 2.580 | 5.01 | 0 |
| 8 | **icm-pushfold** | 132 | 184 | 8.64 | 2.35 | 4.65 | 26% | 9% | 0.0000 | 0 | 0 | 0 | 0.035 | 2.716 | 13.85 | 0 |
| 9 | **min_raiser** | 134 | 184 | 2.72 | 1.54 | 6.42 | 7% | 4% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.412 | 2.12 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 68% | 28% | 4% | 0% | 0% | 0% | 0% |
| keep-made-plus-draw-v2 | 17% | 6% | 18% | 15% | 14% | 14% | 11% | 4% |
| cap-floor-count-v2 | 17% | 10% | 9% | 14% | 17% | 13% | 11% | 8% |
| v0-baseline | 18% | 7% | 10% | 12% | 20% | 15% | 11% | 8% |
| keep-made-plus-draw | 18% | 6% | 9% | 18% | 14% | 14% | 17% | 5% |
| bot | 14% | 3% | 16% | 14% | 15% | 13% | 14% | 11% |
| cap-floor-count | 14% | 5% | 11% | 15% | 15% | 16% | 16% | 7% |
| icm-pushfold | 9% | 8% | 9% | 18% | 16% | 24% | 11% | 4% |
| min_raiser | 4% | 0% | 3% | 3% | 9% | 17% | 39% | 24% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | keep-made-plus-draw-v2 | cap-floor-count-v2 | v0-baseline | keep-made-plus-draw | bot | cap-floor-count | icm-pushfold | min_raiser |
|---|---|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 58-0-21 | 57-0-23 | 61-0-25 | 55-0-26 | 64-0-17 | 62-0-20 | 72-0-13 | 83-0-5 |
| **keep-made-plus-draw-v2** | 21-0-58 | · | 51-0-35 | 40-0-33 | 39-0-38 | 39-0-31 | 50-0-27 | 41-1-27 | 66-2-10 |
| **cap-floor-count-v2** | 23-0-57 | 35-0-51 | · | 39-2-37 | 39-0-40 | 41-0-33 | 39-2-40 | 49-0-37 | 67-2-10 |
| **v0-baseline** | 25-0-61 | 33-0-40 | 37-2-39 | · | 40-1-45 | 41-0-40 | 43-0-36 | 46-0-35 | 70-3-8 |
| **keep-made-plus-draw** | 26-0-55 | 38-0-39 | 40-0-39 | 45-1-40 | · | 41-0-38 | 45-0-38 | 44-0-36 | 67-4-12 |
| **bot** | 17-0-64 | 31-0-39 | 33-0-41 | 40-0-41 | 38-0-41 | · | 38-0-38 | 45-0-34 | 60-4-11 |
| **cap-floor-count** | 20-0-62 | 27-0-50 | 40-2-39 | 36-0-43 | 38-0-45 | 38-0-38 | · | 43-0-46 | 70-2-15 |
| **icm-pushfold** | 13-0-72 | 27-1-41 | 37-0-49 | 35-0-46 | 36-0-44 | 34-0-45 | 46-0-43 | · | 63-4-9 |
| **min_raiser** | 5-0-83 | 10-2-66 | 10-2-67 | 8-3-70 | 12-4-67 | 11-4-60 | 15-2-70 | 9-4-63 | · |

Files: `arena/results/20261106-191954-ladder-757d` (tables.jsonl, seats.csv, summary.json, run.json).
