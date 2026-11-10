# Arena run `strict-smoke2` — strict mode

Started 2026-11-06T19:05:14 · seed `s2` · scheme league · 6 tables · 624 hands · 11.7 s

Command: `league bot min_raiser check_or_fold --tables 6 --seed s2 --mode strict --name strict-smoke2 --no-experiment-log`

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **bot** | 6 | 16 | 20.62 | 13.12 | 3.69 | 44% | 38% | 0.0530 | 90 | 0 | 0 | 1.675 | 32.671 | 77.26 | 0 |
| 2 | **check_or_fold** | 6 | 16 | 16.88 | 6.66 | 3.12 | 69% | 0% | 0.0023 | 5 | 0 | 0 | 1.416 | 17.553 | 76.44 | 0 |
| 3 | **min_raiser** | 6 | 16 | 0.00 | 0.00 | 5.50 | 0% | 0% | 0.0000 | 0 | 0 | 0 | 1.391 | 17.665 | 35.01 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| bot | 38% | 6% | 0% | 12% | 12% | 12% | 19% | 0% |
| check_or_fold | 0% | 31% | 38% | 19% | 12% | 0% | 0% | 0% |
| min_raiser | 0% | 0% | 0% | 6% | 50% | 38% | 0% | 6% |

## Head-to-head (row finished above column: wins-ties-losses)

| | bot | check_or_fold | min_raiser |
|---|---|---|---|
| **bot** | · | 6-0-0 | 6-0-0 |
| **check_or_fold** | 0-0-6 | · | 6-0-0 |
| **min_raiser** | 0-0-6 | 0-0-6 | · |

Files: `arena/results/20261106-190514-strict-smoke2-3130` (tables.jsonl, seats.csv, summary.json, run.json).
