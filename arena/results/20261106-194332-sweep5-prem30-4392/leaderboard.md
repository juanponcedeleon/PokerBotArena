# Arena run `sweep5-prem30` — fast mode

Started 2026-11-06T19:43:32 · seed `icm3` · scheme ab · 600 tables · 78583 hands · 16.2 s

Command: `ab bot prem30=C:/Users/jmast/AppData/Local/Temp/claude/04c107a8decee1b5/25a692ee-2090-4ef1-9245-05a399ac0560/scratchpad/sweep5/prem30 --tables 300 --seed icm3 --no-experiment-log --name sweep5-prem30 --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `prem30` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 296 | 20.77 | 22.17 | +1.40 | ±0.63 | 0.000 | 55 / 224 / 17 | **prem30 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~116.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **prem30** | 296 | 800 | 20.45 | 1.56 | 3.55 | 49% | 32% | 0.0000 | 3 | 0 | 0 | 0.078 | 9.689 | 122.60 | 164 |
| 2 | **bot** | 296 | 800 | 18.94 | 1.59 | 3.71 | 43% | 32% | 0.0000 | 0 | 0 | 0 | 0.018 | 2.651 | 63.45 | 0 |
| 3 | **check_or_fold** | 592 | 1600 | 15.06 | 0.62 | 3.30 | 61% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.073 | 40.24 | 0 |
| 4 | **min_raiser** | 590 | 1600 | 2.74 | 0.55 | 6.04 | 6% | 5% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.180 | 9.81 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| prem30 | 32% | 10% | 6% | 10% | 16% | 15% | 9% | 2% |
| bot | 32% | 6% | 4% | 11% | 19% | 16% | 9% | 2% |
| check_or_fold | 0% | 29% | 32% | 23% | 12% | 3% | 0% | 0% |
| min_raiser | 5% | 0% | 0% | 5% | 17% | 29% | 30% | 14% |

## Head-to-head (row finished above column: wins-ties-losses)

| | prem30 | bot | check_or_fold | min_raiser |
|---|---|---|---|---|
| **prem30** | · | 0-0-0 | 259-0-33 | 253-0-38 |
| **bot** | 0-0-0 | · | 258-0-34 | 255-0-36 |
| **check_or_fold** | 33-0-259 | 34-0-258 | · | 501-0-81 |
| **min_raiser** | 38-0-253 | 36-0-255 | 81-0-501 | · |

Files: `arena/results/20261106-194332-sweep5-prem30-4392` (tables.jsonl, seats.csv, summary.json, run.json).
