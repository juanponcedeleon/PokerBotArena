# Arena run `ladder` — fast mode

Started 2026-11-06T19:11:00 · seed `004b01db` · scheme league · 201 tables · 16322 hands · 21.2 s

Command: `watch --interval 30 --tables 200 --agent arena-watch --question auto-ladder-on-bots-change`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 176 | 268 | 24.78 | 0.96 | 2.46 | 94% | 0% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.078 | 89.76 | 0 |
| 2 | **v0-baseline** | 159 | 268 | 13.62 | 2.39 | 4.18 | 37% | 20% | 0.0000 | 1 | 0 | 0 | 0.021 | 0.904 | 144.98 | 0 |
| 3 | **keep-made-plus-draw** | 176 | 268 | 13.02 | 2.47 | 4.29 | 31% | 21% | 0.0003 | 6 | 0 | 0 | 0.021 | 1.116 | 162.41 | 0 |
| 4 | **bot** | 166 | 268 | 12.16 | 2.33 | 4.41 | 32% | 18% | 0.0000 | 0 | 0 | 0 | 0.021 | 0.421 | 96.63 | 0 |
| 5 | **cap-floor-count** | 167 | 268 | 10.71 | 2.22 | 4.44 | 29% | 16% | 0.0004 | 7 | 0 | 0 | 0.021 | 57.314 | 172.78 | 0 |
| 6 | **min_raiser** | 163 | 268 | 0.71 | 0.61 | 6.33 | 2% | 1% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.186 | 1.05 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 60% | 33% | 6% | 0% | 0% | 0% | 0% |
| v0-baseline | 20% | 4% | 13% | 17% | 17% | 13% | 12% | 5% |
| keep-made-plus-draw | 21% | 4% | 6% | 19% | 17% | 17% | 9% | 7% |
| bot | 18% | 5% | 10% | 14% | 19% | 16% | 13% | 6% |
| cap-floor-count | 16% | 2% | 12% | 18% | 20% | 16% | 13% | 4% |
| min_raiser | 1% | 0% | 1% | 4% | 13% | 34% | 30% | 16% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | v0-baseline | keep-made-plus-draw | bot | cap-floor-count | min_raiser |
|---|---|---|---|---|---|---|
| **check_or_fold** | · | 83-0-51 | 103-0-51 | 103-0-42 | 105-0-40 | 137-0-1 |
| **v0-baseline** | 51-0-83 | · | 75-0-63 | 73-2-56 | 66-1-60 | 113-4-13 |
| **keep-made-plus-draw** | 51-0-103 | 63-0-75 | · | 76-1-64 | 74-1-69 | 119-6-14 |
| **bot** | 42-0-103 | 56-2-73 | 64-1-76 | · | 73-2-60 | 113-8-12 |
| **cap-floor-count** | 40-0-105 | 60-1-66 | 69-1-74 | 60-2-73 | · | 116-2-13 |
| **min_raiser** | 1-0-137 | 13-4-113 | 14-6-119 | 12-8-113 | 13-2-116 | · |

Files: `arena/results/20261106-191100-ladder-fef9` (tables.jsonl, seats.csv, summary.json, run.json).
