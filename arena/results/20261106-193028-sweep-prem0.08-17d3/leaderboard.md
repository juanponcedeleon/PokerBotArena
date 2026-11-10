# Arena run `sweep-prem0.08` — fast mode

Started 2026-11-06T19:30:28 · seed `icm2` · scheme ab · 600 tables · 68476 hands · 12.0 s

Command: `ab bot prem0.08=C:/Users/jmast/AppData/Local/Temp/claude/04c107a8decee1b5/25a692ee-2090-4ef1-9245-05a399ac0560/scratchpad/sweep/prem0.08 --tables 300 --seed icm2 --no-experiment-log --name sweep-prem0.08 --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `prem0.08` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 297 | 19.83 | 15.76 | -4.07 | ±1.82 | 0.000 | 43 / 152 / 102 | **bot is better** |

Pairs needed to resolve a 1-point difference at this variance: ~977.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **bot** | 297 | 800 | 18.59 | 1.58 | 3.71 | 42% | 32% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.220 | 16.20 | 0 |
| 2 | **check_or_fold** | 592 | 1600 | 16.29 | 0.62 | 3.19 | 65% | 0% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.057 | 11.59 | 0 |
| 3 | **prem0.08** | 297 | 800 | 14.85 | 1.51 | 4.09 | 34% | 26% | 0.0000 | 0 | 0 | 0 | 0.077 | 1.516 | 44.68 | 164 |
| 4 | **min_raiser** | 594 | 1600 | 4.49 | 0.70 | 5.80 | 9% | 9% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.095 | 1.46 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| bot | 32% | 6% | 5% | 12% | 20% | 17% | 8% | 2% |
| check_or_fold | 0% | 33% | 32% | 22% | 10% | 3% | 0% | 0% |
| prem0.08 | 26% | 3% | 5% | 13% | 21% | 21% | 9% | 2% |
| min_raiser | 9% | 0% | 0% | 5% | 13% | 35% | 29% | 9% |

## Head-to-head (row finished above column: wins-ties-losses)

| | bot | check_or_fold | prem0.08 | min_raiser |
|---|---|---|---|---|
| **bot** | · | 251-0-42 | 0-0-0 | 251-0-43 |
| **check_or_fold** | 42-0-251 | · | 88-0-205 | 447-0-139 |
| **prem0.08** | 0-0-0 | 205-0-88 | · | 203-0-91 |
| **min_raiser** | 43-0-251 | 139-0-447 | 91-0-203 | · |

Files: `arena/results/20261106-193028-sweep-prem0.08-17d3` (tables.jsonl, seats.csv, summary.json, run.json).
