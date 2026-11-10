# Arena run `sweep5-push10` — fast mode

Started 2026-11-06T19:43:53 · seed `icm3` · scheme ab · 600 tables · 74013 hands · 16.7 s

Command: `ab bot push10=C:/Users/jmast/AppData/Local/Temp/claude/04c107a8decee1b5/25a692ee-2090-4ef1-9245-05a399ac0560/scratchpad/sweep5/push10 --tables 300 --seed icm3 --no-experiment-log --name sweep5-push10 --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `push10` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 296 | 20.77 | 21.35 | +0.58 | ±0.55 | 0.036 | 30 / 252 / 14 | **push10 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~88.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **push10** | 296 | 800 | 19.57 | 1.58 | 3.65 | 45% | 32% | 0.0000 | 3 | 0 | 0 | 0.079 | 3.003 | 1170.68 | 164 |
| 2 | **bot** | 296 | 800 | 18.94 | 1.59 | 3.71 | 43% | 32% | 0.0000 | 0 | 0 | 0 | 0.019 | 0.964 | 8.67 | 0 |
| 3 | **check_or_fold** | 592 | 1600 | 15.56 | 0.62 | 3.25 | 63% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.101 | 25.67 | 0 |
| 4 | **min_raiser** | 590 | 1600 | 2.69 | 0.54 | 6.04 | 6% | 5% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.159 | 10.17 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| push10 | 32% | 8% | 5% | 11% | 17% | 16% | 9% | 2% |
| bot | 32% | 6% | 4% | 11% | 19% | 16% | 9% | 2% |
| check_or_fold | 0% | 30% | 33% | 23% | 12% | 3% | 0% | 0% |
| min_raiser | 5% | 0% | 0% | 5% | 17% | 29% | 30% | 14% |

## Head-to-head (row finished above column: wins-ties-losses)

| | push10 | bot | check_or_fold | min_raiser |
|---|---|---|---|---|
| **push10** | · | 0-0-0 | 258-0-34 | 254-0-37 |
| **bot** | 0-0-0 | · | 258-0-34 | 255-0-36 |
| **check_or_fold** | 34-0-258 | 34-0-258 | · | 504-0-78 |
| **min_raiser** | 37-0-254 | 36-0-255 | 78-0-504 | · |

Files: `arena/results/20261106-194353-sweep5-push10-ca6d` (tables.jsonl, seats.csv, summary.json, run.json).
