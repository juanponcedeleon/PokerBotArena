# Arena run `icm-pushfold-v9` — fast mode

Started 2026-11-06T19:58:59 · seed `icm1` · scheme ab · 804 tables · 116767 hands · 23.8 s

Command: `ab bot bots/icm-pushfold-v9 --tables 400 --seed icm1 --name icm-pushfold-v9 --agent Claude (icm-pushfold agent) --question v9 = cap-floor-count-v6 (bot/ as of 19:53) + icm-pushfold-v7 short-stack module; vs bot --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `icm-pushfold-v9` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 397 | 22.70 | 25.03 | +2.33 | ±0.58 | 0.000 | 116 / 251 / 30 | **icm-pushfold-v9 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~134.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **icm-pushfold-v9** | 397 | 1072 | 23.59 | 1.30 | 3.23 | 59% | 33% | 0.0000 | 0 | 0 | 0 | 0.068 | 0.888 | 4.80 | 164 |
| 2 | **bot** | 397 | 1072 | 21.10 | 1.37 | 3.52 | 49% | 34% | 0.0000 | 0 | 0 | 0 | 0.016 | 0.733 | 4.30 | 0 |
| 3 | **check_or_fold** | 794 | 2144 | 12.97 | 0.53 | 3.49 | 54% | 0% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.026 | 3.09 | 0 |
| 4 | **min_raiser** | 792 | 2144 | 2.19 | 0.42 | 6.12 | 5% | 4% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.048 | 1.19 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| icm-pushfold-v9 | 33% | 18% | 8% | 6% | 12% | 13% | 8% | 1% |
| bot | 34% | 12% | 3% | 9% | 16% | 16% | 9% | 1% |
| check_or_fold | 0% | 23% | 31% | 27% | 15% | 4% | 1% | 0% |
| min_raiser | 4% | 0% | 1% | 4% | 13% | 33% | 32% | 13% |

## Head-to-head (row finished above column: wins-ties-losses)

| | icm-pushfold-v9 | bot | check_or_fold | min_raiser |
|---|---|---|---|---|
| **icm-pushfold-v9** | · | 0-0-0 | 358-0-34 | 352-0-39 |
| **bot** | 0-0-0 | · | 358-0-34 | 356-0-35 |
| **check_or_fold** | 34-0-358 | 34-0-358 | · | 693-0-89 |
| **min_raiser** | 39-0-352 | 35-0-356 | 89-0-693 | · |

Files: `arena/results/20261106-195859-icm-pushfold-v9-0fab` (tables.jsonl, seats.csv, summary.json, run.json).
