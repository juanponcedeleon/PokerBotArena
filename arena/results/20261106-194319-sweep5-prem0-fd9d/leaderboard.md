# Arena run `sweep5-prem0` — fast mode

Started 2026-11-06T19:43:19 · seed `icm3` · scheme ab · 600 tables · 60611 hands · 11.9 s

Command: `ab bot prem0=C:/Users/jmast/AppData/Local/Temp/claude/04c107a8decee1b5/25a692ee-2090-4ef1-9245-05a399ac0560/scratchpad/sweep5/prem0 --tables 300 --seed icm3 --no-experiment-log --name sweep5-prem0 --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `prem0` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 296 | 20.77 | 21.16 | +0.39 | ±0.52 | 0.141 | 27 / 249 / 20 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~80.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **prem0** | 296 | 800 | 19.32 | 1.58 | 3.68 | 44% | 32% | 0.0000 | 1 | 0 | 0 | 0.073 | 0.711 | 1017.26 | 164 |
| 2 | **bot** | 296 | 800 | 18.94 | 1.59 | 3.71 | 43% | 32% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.162 | 29.01 | 0 |
| 3 | **check_or_fold** | 592 | 1600 | 15.65 | 0.62 | 3.24 | 63% | 0% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.051 | 12.41 | 0 |
| 4 | **min_raiser** | 590 | 1600 | 2.72 | 0.55 | 6.04 | 6% | 5% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.067 | 2.68 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| prem0 | 32% | 8% | 4% | 11% | 18% | 17% | 9% | 2% |
| bot | 32% | 6% | 4% | 11% | 19% | 16% | 9% | 2% |
| check_or_fold | 0% | 30% | 33% | 23% | 11% | 2% | 0% | 0% |
| min_raiser | 5% | 0% | 0% | 5% | 17% | 29% | 30% | 14% |

## Head-to-head (row finished above column: wins-ties-losses)

| | prem0 | bot | check_or_fold | min_raiser |
|---|---|---|---|---|
| **prem0** | · | 0-0-0 | 260-0-32 | 253-0-38 |
| **bot** | 0-0-0 | · | 258-0-34 | 255-0-36 |
| **check_or_fold** | 32-0-260 | 34-0-258 | · | 503-0-79 |
| **min_raiser** | 38-0-253 | 36-0-255 | 79-0-503 | · |

Files: `arena/results/20261106-194319-sweep5-prem0-fd9d` (tables.jsonl, seats.csv, summary.json, run.json).
