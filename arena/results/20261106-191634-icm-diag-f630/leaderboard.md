# Arena run `icm-diag` — fast mode

Started 2026-11-06T19:16:34 · seed `icm1` · scheme ab · 204 tables · 19950 hands · 5.7 s

Command: `ab bot bots/icm-pushfold --tables 100 --seed icm1 --log --no-experiment-log --name icm-diag --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `icm-pushfold` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 101 | 17.87 | 14.36 | -3.51 | ±2.18 | 0.002 | 5 / 72 / 24 | **bot is better** |

Pairs needed to resolve a 1-point difference at this variance: ~470.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 202 | 544 | 17.05 | 1.05 | 3.11 | 68% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.073 | 9.49 | 0 |
| 2 | **bot** | 101 | 272 | 16.25 | 2.74 | 4.00 | 35% | 31% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.187 | 3.26 | 0 |
| 3 | **icm-pushfold** | 101 | 272 | 13.47 | 2.54 | 4.21 | 31% | 24% | 0.0000 | 0 | 0 | 0 | 0.029 | 2.235 | 27.41 | 0 |
| 4 | **min_raiser** | 202 | 544 | 5.59 | 1.30 | 5.41 | 14% | 10% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.101 | 7.57 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 35% | 33% | 21% | 8% | 2% | 0% | 0% |
| bot | 31% | 2% | 2% | 14% | 21% | 19% | 8% | 3% |
| icm-pushfold | 24% | 3% | 4% | 15% | 22% | 21% | 9% | 3% |
| min_raiser | 10% | 0% | 3% | 2% | 27% | 30% | 20% | 7% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | bot | icm-pushfold | min_raiser |
|---|---|---|---|---|
| **check_or_fold** | · | 18-0-82 | 34-1-65 | 144-0-56 |
| **bot** | 82-0-18 | · | 0-0-0 | 82-0-18 |
| **icm-pushfold** | 65-1-34 | 0-0-0 | · | 63-0-37 |
| **min_raiser** | 56-0-144 | 18-0-82 | 37-0-63 | · |

Files: `arena/results/20261106-191634-icm-diag-f630` (tables.jsonl, seats.csv, summary.json, run.json).
