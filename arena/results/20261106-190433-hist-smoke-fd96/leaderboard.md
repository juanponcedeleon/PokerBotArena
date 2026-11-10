# Arena run `hist-smoke` — fast mode

Started 2026-11-06T19:04:33 · seed `h1` · scheme league · 6 tables · 564 hands · 1.4 s

Command: `league bot min_raiser check_or_fold --tables 6 --seed h1 --history bot --name hist-smoke --no-experiment-log --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 6 | 16 | 17.50 | 6.88 | 3.19 | 69% | 0% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.010 | 0.07 | 0 |
| 2 | **bot** | 5 | 16 | 10.62 | 10.74 | 4.44 | 25% | 19% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.055 | 0.10 | 0 |
| 3 | **min_raiser** | 6 | 16 | 9.38 | 10.74 | 5.25 | 19% | 19% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.012 | 0.02 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 38% | 31% | 12% | 12% | 6% | 0% | 0% |
| bot | 19% | 0% | 6% | 19% | 12% | 38% | 6% | 0% |
| min_raiser | 19% | 0% | 0% | 6% | 12% | 19% | 44% | 0% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | bot | min_raiser |
|---|---|---|---|
| **check_or_fold** | · | 2-0-3 | 3-0-3 |
| **bot** | 3-0-2 | · | 3-0-2 |
| **min_raiser** | 3-0-3 | 2-0-3 | · |

Files: `arena/results/20261106-190433-hist-smoke-fd96` (tables.jsonl, seats.csv, summary.json, run.json).
