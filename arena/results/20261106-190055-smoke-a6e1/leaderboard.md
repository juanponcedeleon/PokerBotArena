# Arena run `smoke` — fast mode

Started 2026-11-06T19:00:55 · seed `t1` · scheme league · 24 tables · 2314 hands · 2.5 s

Command: `league bot min_raiser check_or_fold --tables 24 --seed t1 --log --history bot --name smoke --agent Claude(infra) --question arena smoke test`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 24 | 64 | 18.44 | 2.99 | 2.94 | 73% | 0% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.039 | 0.23 | 0 |
| 2 | **bot** | 24 | 64 | 14.38 | 5.65 | 4.08 | 30% | 28% | 0.0000 | 0 | 0 | 0 | 0.024 | 0.330 | 1.16 | 0 |
| 3 | **min_raiser** | 24 | 64 | 4.69 | 3.67 | 5.69 | 9% | 9% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.127 | 0.13 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 38% | 36% | 22% | 5% | 0% | 0% | 0% |
| bot | 28% | 0% | 2% | 14% | 25% | 25% | 6% | 0% |
| min_raiser | 9% | 0% | 0% | 8% | 11% | 38% | 27% | 8% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | bot | min_raiser |
|---|---|---|---|
| **check_or_fold** | · | 6-0-18 | 18-0-6 |
| **bot** | 18-0-6 | · | 18-0-6 |
| **min_raiser** | 6-0-18 | 6-0-18 | · |

Files: `arena/results/20261106-190055-smoke-a6e1` (tables.jsonl, seats.csv, summary.json, run.json).
