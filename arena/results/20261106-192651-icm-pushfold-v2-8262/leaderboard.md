# Arena run `icm-pushfold-v2` — fast mode

Started 2026-11-06T19:26:51 · seed `icm1` · scheme ab · 804 tables · 79723 hands · 44.1 s

Command: `ab bot bots/icm-pushfold-v2 --tables 400 --seed icm1 --log --name icm-pushfold-v2 --agent Claude (icm-pushfold agent) --question v2: call-not-isolate fix, committed callers, per-seat call/raise rates in memory; vs v0 preflop`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `icm-pushfold-v2` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 397 | 19.71 | 14.72 | -4.99 | ±1.49 | 0.000 | 50 / 198 / 149 | **bot is better** |

Pairs needed to resolve a 1-point difference at this variance: ~877.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **bot** | 397 | 1072 | 18.28 | 1.36 | 3.78 | 42% | 31% | 0.0000 | 2 | 0 | 0 | 0.019 | 12.785 | 145.82 | 0 |
| 2 | **check_or_fold** | 794 | 2144 | 16.35 | 0.53 | 3.16 | 65% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.206 | 70.72 | 0 |
| 3 | **icm-pushfold-v2** | 397 | 1072 | 14.05 | 1.29 | 4.18 | 32% | 25% | 0.0008 | 76 | 0 | 0 | 0.080 | 28.727 | 139.24 | 164 |
| 4 | **min_raiser** | 792 | 2144 | 4.98 | 0.63 | 5.69 | 11% | 10% | 0.0000 | 0 | 0 | 0 | 0.004 | 10.396 | 47.28 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| bot | 31% | 7% | 4% | 11% | 19% | 18% | 9% | 2% |
| check_or_fold | 0% | 33% | 33% | 23% | 10% | 2% | 0% | 0% |
| icm-pushfold-v2 | 25% | 3% | 4% | 14% | 22% | 21% | 10% | 2% |
| min_raiser | 10% | 0% | 1% | 4% | 17% | 32% | 27% | 9% |

## Head-to-head (row finished above column: wins-ties-losses)

| | bot | check_or_fold | icm-pushfold-v2 | min_raiser |
|---|---|---|---|---|
| **bot** | · | 329-0-63 | 0-0-0 | 325-0-66 |
| **check_or_fold** | 63-0-329 | · | 127-0-265 | 577-0-205 |
| **icm-pushfold-v2** | 0-0-0 | 265-0-127 | · | 260-0-131 |
| **min_raiser** | 66-0-325 | 205-0-577 | 131-0-260 | · |

Files: `arena/results/20261106-192651-icm-pushfold-v2-8262` (tables.jsonl, seats.csv, summary.json, run.json).
