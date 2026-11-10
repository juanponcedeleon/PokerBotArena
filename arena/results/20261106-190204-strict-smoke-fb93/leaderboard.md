# Arena run `strict-smoke` — strict mode

Started 2026-11-06T19:02:04 · seed `s1` · scheme league · 6 tables · 581 hands · 4.3 s

Command: `league bot min_raiser check_or_fold --tables 6 --seed s1 --mode strict --name strict-smoke --no-experiment-log`

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 6 | 16 | 17.50 | 6.88 | 3.06 | 69% | 0% | 0.0000 | 0 | 0 | 0 | 1.398 | 16.814 | 469.76 | 0 |
| 2 | **bot** | 6 | 16 | 16.04 | 12.61 | 3.94 | 44% | 31% | 0.0000 | 0 | 0 | 0 | 1.796 | 764.688 | 787.08 | 0 |
| 3 | **min_raiser** | 6 | 16 | 3.96 | 6.59 | 4.81 | 31% | 6% | 0.0000 | 0 | 0 | 0 | 1.300 | 448.018 | 480.03 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 38% | 31% | 19% | 12% | 0% | 0% | 0% |
| bot | 31% | 0% | 12% | 6% | 12% | 25% | 12% | 0% |
| min_raiser | 6% | 0% | 25% | 6% | 25% | 12% | 25% | 0% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | bot | min_raiser |
|---|---|---|---|
| **check_or_fold** | · | 1-0-5 | 5-0-1 |
| **bot** | 5-0-1 | · | 5-0-1 |
| **min_raiser** | 1-0-5 | 1-0-5 | · |

Files: `arena/results/20261106-190204-strict-smoke-fb93` (tables.jsonl, seats.csv, summary.json, run.json).
