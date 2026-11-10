# Arena run `icm-pushfold-v9-seed2` — fast mode

Started 2026-11-06T20:28:32 · seed `icm5` · scheme ab · 804 tables · 115901 hands · 21.8 s

Command: `ab bot bots/icm-pushfold-v9 --tables 400 --seed icm5 --name icm-pushfold-v9-seed2 --agent Claude (icm-pushfold agent) --question v9 confirmation on a second seed (icm5) --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `icm-pushfold-v9` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 397 | 22.84 | 25.05 | +2.21 | ±0.59 | 0.000 | 127 / 238 / 32 | **icm-pushfold-v9 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~139.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **icm-pushfold-v9** | 397 | 1072 | 23.31 | 1.28 | 3.22 | 60% | 32% | 0.0000 | 0 | 0 | 0 | 0.086 | 1.959 | 31.60 | 164 |
| 2 | **bot** | 397 | 1072 | 20.86 | 1.35 | 3.54 | 49% | 33% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.968 | 9.94 | 0 |
| 3 | **check_or_fold** | 786 | 2144 | 12.66 | 0.54 | 3.53 | 52% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.052 | 4.90 | 0 |
| 4 | **min_raiser** | 782 | 2144 | 2.76 | 0.47 | 6.07 | 6% | 5% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.234 | 4.26 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| icm-pushfold-v9 | 32% | 17% | 11% | 7% | 13% | 12% | 6% | 2% |
| bot | 33% | 12% | 5% | 7% | 18% | 16% | 7% | 2% |
| check_or_fold | 0% | 23% | 29% | 27% | 15% | 5% | 1% | 0% |
| min_raiser | 5% | 0% | 0% | 4% | 13% | 32% | 32% | 12% |

## Head-to-head (row finished above column: wins-ties-losses)

| | icm-pushfold-v9 | bot | check_or_fold | min_raiser |
|---|---|---|---|---|
| **icm-pushfold-v9** | · | 0-0-0 | 343-0-45 | 332-0-54 |
| **bot** | 0-0-0 | · | 346-0-42 | 340-0-46 |
| **check_or_fold** | 45-0-343 | 42-0-346 | · | 649-0-115 |
| **min_raiser** | 54-0-332 | 46-0-340 | 115-0-649 | · |

Files: `arena/results/20261106-202832-icm-pushfold-v9-seed2-6df2` (tables.jsonl, seats.csv, summary.json, run.json).
