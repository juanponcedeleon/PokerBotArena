# Arena run `sweep7-push18` — fast mode

Started 2026-11-06T19:45:50 · seed `icm3` · scheme ab · 600 tables · 79522 hands · 22.4 s

Command: `ab bot push18=C:/Users/jmast/AppData/Local/Temp/claude/04c107a8decee1b5/25a692ee-2090-4ef1-9245-05a399ac0560/scratchpad/sweep7/push18 --tables 300 --seed icm3 --no-experiment-log --name sweep7-push18 --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `push18` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 296 | 20.77 | 22.46 | +1.69 | ±0.68 | 0.000 | 66 / 210 / 20 | **push18 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~138.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **push18** | 296 | 800 | 20.80 | 1.55 | 3.51 | 50% | 32% | 0.0000 | 0 | 0 | 0 | 0.060 | 2.506 | 28.53 | 164 |
| 2 | **bot** | 296 | 800 | 18.94 | 1.59 | 3.71 | 43% | 32% | 0.0000 | 0 | 0 | 0 | 0.019 | 0.729 | 15.40 | 0 |
| 3 | **check_or_fold** | 592 | 1600 | 14.83 | 0.62 | 3.33 | 60% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.100 | 16.52 | 0 |
| 4 | **min_raiser** | 590 | 1600 | 2.80 | 0.55 | 6.03 | 6% | 5% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.210 | 6.13 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| push18 | 32% | 12% | 6% | 10% | 15% | 15% | 8% | 2% |
| bot | 32% | 6% | 4% | 11% | 19% | 16% | 9% | 2% |
| check_or_fold | 0% | 28% | 32% | 23% | 12% | 3% | 0% | 0% |
| min_raiser | 5% | 0% | 0% | 5% | 17% | 29% | 30% | 14% |

## Head-to-head (row finished above column: wins-ties-losses)

| | push18 | bot | check_or_fold | min_raiser |
|---|---|---|---|---|
| **push18** | · | 0-0-0 | 260-0-32 | 251-0-40 |
| **bot** | 0-0-0 | · | 258-0-34 | 255-0-36 |
| **check_or_fold** | 32-0-260 | 34-0-258 | · | 500-0-82 |
| **min_raiser** | 40-0-251 | 36-0-255 | 82-0-500 | · |

Files: `arena/results/20261106-194550-sweep7-push18-42b7` (tables.jsonl, seats.csv, summary.json, run.json).
