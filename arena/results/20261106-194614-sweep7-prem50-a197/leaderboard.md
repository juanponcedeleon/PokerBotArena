# Arena run `sweep7-prem50` — fast mode

Started 2026-11-06T19:46:14 · seed `icm3` · scheme ab · 600 tables · 80932 hands · 20.9 s

Command: `ab bot prem50=C:/Users/jmast/AppData/Local/Temp/claude/04c107a8decee1b5/25a692ee-2090-4ef1-9245-05a399ac0560/scratchpad/sweep7/prem50 --tables 300 --seed icm3 --no-experiment-log --name sweep7-prem50 --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `prem50` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 296 | 20.77 | 22.29 | +1.52 | ±0.65 | 0.000 | 58 / 223 / 15 | **prem50 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~124.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **prem50** | 296 | 800 | 20.62 | 1.56 | 3.53 | 50% | 32% | 0.0000 | 0 | 0 | 0 | 0.057 | 1.686 | 8.33 | 164 |
| 2 | **bot** | 296 | 800 | 18.94 | 1.59 | 3.71 | 43% | 32% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.587 | 6.53 | 0 |
| 3 | **check_or_fold** | 592 | 1600 | 14.96 | 0.62 | 3.31 | 61% | 0% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.058 | 22.79 | 0 |
| 4 | **min_raiser** | 590 | 1600 | 2.76 | 0.55 | 6.04 | 6% | 5% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.120 | 3.09 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| prem50 | 32% | 11% | 6% | 10% | 15% | 15% | 8% | 2% |
| bot | 32% | 6% | 4% | 11% | 19% | 16% | 9% | 2% |
| check_or_fold | 0% | 29% | 32% | 23% | 12% | 3% | 0% | 0% |
| min_raiser | 5% | 0% | 0% | 5% | 17% | 29% | 30% | 14% |

## Head-to-head (row finished above column: wins-ties-losses)

| | prem50 | bot | check_or_fold | min_raiser |
|---|---|---|---|---|
| **prem50** | · | 0-0-0 | 260-0-32 | 252-0-39 |
| **bot** | 0-0-0 | · | 258-0-34 | 255-0-36 |
| **check_or_fold** | 32-0-260 | 34-0-258 | · | 501-0-81 |
| **min_raiser** | 39-0-252 | 36-0-255 | 81-0-501 | · |

Files: `arena/results/20261106-194614-sweep7-prem50-a197` (tables.jsonl, seats.csv, summary.json, run.json).
