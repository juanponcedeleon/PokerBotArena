# Arena run `sweep-prem0.30` — fast mode

Started 2026-11-06T19:30:54 · seed `icm2` · scheme ab · 600 tables · 74307 hands · 11.9 s

Command: `ab bot prem0.30=C:/Users/jmast/AppData/Local/Temp/claude/04c107a8decee1b5/25a692ee-2090-4ef1-9245-05a399ac0560/scratchpad/sweep/prem0.30 --tables 300 --seed icm2 --no-experiment-log --name sweep-prem0.30 --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `prem0.30` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 297 | 19.83 | 15.48 | -4.35 | ±1.85 | 0.000 | 47 / 144 / 106 | **bot is better** |

Pairs needed to resolve a 1-point difference at this variance: ~1012.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **bot** | 297 | 800 | 18.59 | 1.58 | 3.71 | 42% | 32% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.210 | 25.50 | 0 |
| 2 | **check_or_fold** | 592 | 1600 | 15.95 | 0.62 | 3.22 | 64% | 0% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.032 | 4.28 | 0 |
| 3 | **prem0.30** | 297 | 800 | 14.69 | 1.48 | 4.10 | 35% | 24% | 0.0000 | 0 | 0 | 0 | 0.076 | 0.896 | 25.97 | 164 |
| 4 | **min_raiser** | 594 | 1600 | 4.91 | 0.72 | 5.83 | 10% | 10% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.063 | 0.74 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| bot | 32% | 6% | 5% | 12% | 20% | 17% | 8% | 2% |
| check_or_fold | 0% | 32% | 32% | 22% | 11% | 3% | 0% | 0% |
| prem0.30 | 24% | 5% | 5% | 13% | 20% | 21% | 9% | 2% |
| min_raiser | 10% | 0% | 1% | 4% | 11% | 31% | 35% | 9% |

## Head-to-head (row finished above column: wins-ties-losses)

| | bot | check_or_fold | prem0.30 | min_raiser |
|---|---|---|---|---|
| **bot** | · | 251-0-42 | 0-0-0 | 251-0-43 |
| **check_or_fold** | 42-0-251 | · | 99-0-194 | 434-0-152 |
| **prem0.30** | 0-0-0 | 194-0-99 | · | 190-0-104 |
| **min_raiser** | 43-0-251 | 152-0-434 | 104-0-190 | · |

Files: `arena/results/20261106-193054-sweep-prem0.30-032c` (tables.jsonl, seats.csv, summary.json, run.json).
