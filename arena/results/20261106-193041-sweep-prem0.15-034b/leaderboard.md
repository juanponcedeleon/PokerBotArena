# Arena run `sweep-prem0.15` — fast mode

Started 2026-11-06T19:30:41 · seed `icm2` · scheme ab · 600 tables · 71648 hands · 11.6 s

Command: `ab bot prem0.15=C:/Users/jmast/AppData/Local/Temp/claude/04c107a8decee1b5/25a692ee-2090-4ef1-9245-05a399ac0560/scratchpad/sweep/prem0.15 --tables 300 --seed icm2 --no-experiment-log --name sweep-prem0.15 --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `prem0.15` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 297 | 19.83 | 15.47 | -4.36 | ±1.82 | 0.000 | 39 / 156 / 102 | **bot is better** |

Pairs needed to resolve a 1-point difference at this variance: ~976.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **bot** | 297 | 800 | 18.59 | 1.58 | 3.71 | 42% | 32% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.194 | 1.36 | 0 |
| 2 | **check_or_fold** | 592 | 1600 | 16.29 | 0.62 | 3.19 | 65% | 0% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.057 | 4.73 | 0 |
| 3 | **prem0.15** | 297 | 800 | 14.61 | 1.50 | 4.11 | 34% | 25% | 0.0000 | 0 | 0 | 0 | 0.075 | 1.057 | 31.11 | 164 |
| 4 | **min_raiser** | 594 | 1600 | 4.61 | 0.70 | 5.82 | 10% | 9% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.081 | 6.27 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| bot | 32% | 6% | 5% | 12% | 20% | 17% | 8% | 2% |
| check_or_fold | 0% | 33% | 32% | 21% | 10% | 3% | 0% | 0% |
| prem0.15 | 25% | 3% | 5% | 13% | 21% | 21% | 9% | 2% |
| min_raiser | 9% | 0% | 0% | 4% | 12% | 34% | 31% | 9% |

## Head-to-head (row finished above column: wins-ties-losses)

| | bot | check_or_fold | prem0.15 | min_raiser |
|---|---|---|---|---|
| **bot** | · | 251-0-42 | 0-0-0 | 251-0-43 |
| **check_or_fold** | 42-0-251 | · | 92-0-201 | 443-0-143 |
| **prem0.15** | 0-0-0 | 201-0-92 | · | 199-0-95 |
| **min_raiser** | 43-0-251 | 143-0-443 | 95-0-199 | · |

Files: `arena/results/20261106-193041-sweep-prem0.15-034b` (tables.jsonl, seats.csv, summary.json, run.json).
