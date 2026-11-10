# Arena run `sweep5-push15` — fast mode

Started 2026-11-06T19:42:46 · seed `icm3` · scheme ab · 600 tables · 74994 hands · 31.1 s

Command: `ab bot push15=C:/Users/jmast/AppData/Local/Temp/claude/04c107a8decee1b5/25a692ee-2090-4ef1-9245-05a399ac0560/scratchpad/sweep5/push15 --tables 300 --seed icm3 --no-experiment-log --name sweep5-push15 --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `push15` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 296 | 20.77 | 22.34 | +1.57 | ±0.67 | 0.000 | 52 / 230 / 14 | **push15 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~131.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **push15** | 296 | 800 | 20.49 | 1.57 | 3.54 | 48% | 32% | 0.0006 | 62 | 0 | 0 | 0.077 | 4.387 | 214.80 | 164 |
| 2 | **bot** | 296 | 800 | 18.94 | 1.59 | 3.71 | 43% | 32% | 0.0001 | 14 | 0 | 0 | 0.018 | 0.326 | 217.10 | 0 |
| 3 | **check_or_fold** | 592 | 1600 | 15.11 | 0.62 | 3.30 | 61% | 0% | 0.0000 | 6 | 0 | 0 | 0.004 | 0.050 | 138.55 | 0 |
| 4 | **min_raiser** | 590 | 1600 | 2.67 | 0.54 | 6.05 | 6% | 5% | 0.0000 | 2 | 0 | 0 | 0.004 | 0.074 | 136.42 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| push15 | 32% | 10% | 6% | 10% | 17% | 15% | 8% | 2% |
| bot | 32% | 6% | 4% | 11% | 19% | 16% | 9% | 2% |
| check_or_fold | 0% | 29% | 32% | 23% | 12% | 3% | 0% | 0% |
| min_raiser | 5% | 0% | 0% | 5% | 17% | 29% | 29% | 14% |

## Head-to-head (row finished above column: wins-ties-losses)

| | push15 | bot | check_or_fold | min_raiser |
|---|---|---|---|---|
| **push15** | · | 0-0-0 | 262-0-30 | 255-0-36 |
| **bot** | 0-0-0 | · | 258-0-34 | 255-0-36 |
| **check_or_fold** | 30-0-262 | 34-0-258 | · | 504-0-78 |
| **min_raiser** | 36-0-255 | 36-0-255 | 78-0-504 | · |

Files: `arena/results/20261106-194246-sweep5-push15-b625` (tables.jsonl, seats.csv, summary.json, run.json).
