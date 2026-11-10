# Arena run `sweep-prem030-log` — fast mode

Started 2026-11-06T19:32:45 · seed `icm2` · scheme ab · 240 tables · 29515 hands · 7.0 s

Command: `ab bot prem0.30=C:/Users/jmast/AppData/Local/Temp/claude/04c107a8decee1b5/25a692ee-2090-4ef1-9245-05a399ac0560/scratchpad/sweep/prem0.30 --tables 120 --seed icm2 --log --no-experiment-log --name sweep-prem030-log --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `prem0.30` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 119 | 19.26 | 14.86 | -4.40 | ±2.81 | 0.002 | 21 / 57 / 41 | **bot is better** |

Pairs needed to resolve a 1-point difference at this variance: ~919.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **bot** | 119 | 320 | 18.00 | 2.52 | 3.75 | 41% | 32% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.186 | 9.41 | 0 |
| 2 | **check_or_fold** | 236 | 640 | 16.12 | 0.98 | 3.22 | 65% | 0% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.038 | 10.28 | 0 |
| 3 | **prem0.30** | 119 | 320 | 14.31 | 2.32 | 4.11 | 34% | 23% | 0.0000 | 0 | 0 | 0 | 0.073 | 2.591 | 26.05 | 164 |
| 4 | **min_raiser** | 240 | 640 | 5.22 | 1.18 | 5.83 | 11% | 10% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.059 | 2.56 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| bot | 32% | 4% | 5% | 13% | 21% | 16% | 8% | 2% |
| check_or_fold | 0% | 32% | 32% | 21% | 11% | 3% | 1% | 0% |
| prem0.30 | 23% | 6% | 5% | 13% | 21% | 21% | 8% | 2% |
| min_raiser | 10% | 0% | 0% | 3% | 9% | 35% | 33% | 9% |

## Head-to-head (row finished above column: wins-ties-losses)

| | bot | check_or_fold | prem0.30 | min_raiser |
|---|---|---|---|---|
| **bot** | · | 100-0-17 | 0-0-0 | 101-0-18 |
| **check_or_fold** | 17-0-100 | · | 43-0-74 | 171-0-65 |
| **prem0.30** | 0-0-0 | 74-0-43 | · | 74-0-45 |
| **min_raiser** | 18-0-101 | 65-0-171 | 45-0-74 | · |

Files: `arena/results/20261106-193245-sweep-prem030-log-ae26` (tables.jsonl, seats.csv, summary.json, run.json).
