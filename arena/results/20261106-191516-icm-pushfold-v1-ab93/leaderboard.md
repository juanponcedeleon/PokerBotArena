# Arena run `icm-pushfold-v1` — fast mode

Started 2026-11-06T19:15:16 · seed `icm1` · scheme ab · 804 tables · 78845 hands · 15.4 s

Command: `ab bot bots/icm-pushfold --tables 400 --seed icm1 --name icm-pushfold-v1 --agent Claude (icm-pushfold agent) --question Does ICM push/fold (06 S6.1-S6.3 tables) beat v0 preflop, all else equal?`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `icm-pushfold` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 397 | 17.29 | 14.90 | -2.39 | ±0.94 | 0.000 | 29 / 302 / 66 | **bot is better** |

Pairs needed to resolve a 1-point difference at this variance: ~351.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 794 | 2144 | 17.21 | 0.52 | 3.08 | 69% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.066 | 8.72 | 0 |
| 2 | **bot** | 397 | 1072 | 15.98 | 1.36 | 3.98 | 35% | 30% | 0.0000 | 0 | 0 | 0 | 0.020 | 0.360 | 25.79 | 0 |
| 3 | **icm-pushfold** | 397 | 1072 | 14.19 | 1.30 | 4.16 | 32% | 25% | 0.0000 | 0 | 0 | 0 | 0.031 | 1.950 | 70.50 | 0 |
| 4 | **min_raiser** | 792 | 2144 | 5.20 | 0.64 | 5.39 | 12% | 10% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.144 | 13.73 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 35% | 33% | 22% | 8% | 2% | 0% | 0% |
| bot | 30% | 1% | 3% | 14% | 21% | 20% | 9% | 2% |
| icm-pushfold | 25% | 3% | 4% | 14% | 22% | 21% | 9% | 2% |
| min_raiser | 10% | 0% | 2% | 6% | 25% | 31% | 20% | 6% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | bot | icm-pushfold | min_raiser |
|---|---|---|---|---|
| **check_or_fold** | · | 76-0-316 | 124-1-267 | 570-0-212 |
| **bot** | 316-0-76 | · | 0-0-0 | 314-0-77 |
| **icm-pushfold** | 267-1-124 | 0-0-0 | · | 263-0-128 |
| **min_raiser** | 212-0-570 | 77-0-314 | 128-0-263 | · |

Files: `arena/results/20261106-191516-icm-pushfold-v1-ab93` (tables.jsonl, seats.csv, summary.json, run.json).
