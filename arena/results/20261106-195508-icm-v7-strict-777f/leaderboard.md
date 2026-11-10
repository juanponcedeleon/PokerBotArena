# Arena run `icm-v7-strict` — strict mode

Started 2026-11-06T19:55:08 · seed `s1` · scheme league · 12 tables · 2013 hands · 58.0 s

Command: `league bots/icm-pushfold-v7 check_or_fold min_raiser --mode strict --tables 12 --seed s1 --no-experiment-log --name icm-v7-strict --quiet`

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **icm-pushfold-v7** | 12 | 32 | 23.12 | 8.11 | 3.22 | 56% | 34% | 0.0008 | 4 | 0 | 0 | 0.792 | 14.026 | 43.91 | 164 |
| 2 | **check_or_fold** | 12 | 32 | 12.81 | 4.60 | 3.50 | 53% | 0% | 0.0000 | 0 | 0 | 0 | 0.593 | 13.369 | 18.61 | 0 |
| 3 | **min_raiser** | 12 | 32 | 1.56 | 3.19 | 6.22 | 3% | 3% | 0.0000 | 0 | 0 | 0 | 0.623 | 10.516 | 26.26 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| icm-pushfold-v7 | 34% | 16% | 6% | 9% | 12% | 16% | 6% | 0% |
| check_or_fold | 0% | 22% | 31% | 28% | 12% | 6% | 0% | 0% |
| min_raiser | 3% | 0% | 0% | 0% | 12% | 47% | 25% | 12% |

## Head-to-head (row finished above column: wins-ties-losses)

| | icm-pushfold-v7 | check_or_fold | min_raiser |
|---|---|---|---|
| **icm-pushfold-v7** | · | 12-0-0 | 11-0-1 |
| **check_or_fold** | 0-0-12 | · | 11-0-1 |
| **min_raiser** | 1-0-11 | 1-0-11 | · |

Files: `arena/results/20261106-195508-icm-v7-strict-777f` (tables.jsonl, seats.csv, summary.json, run.json).
