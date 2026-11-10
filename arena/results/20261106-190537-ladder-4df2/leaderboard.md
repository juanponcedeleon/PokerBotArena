# Arena run `ladder` — fast mode

Started 2026-11-06T19:05:37 · seed `ladder0` · scheme league · 120 tables · 10981 hands · ? s

Command: `ladder --tables 120 --seed ladder0 --agent Claude(infra) --question first ladder: v0 bot vs kit examples --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 120 | 240 | 24.54 | 0.75 | 2.53 | 98% | 0% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.095 | 7.31 | 0 |
| 2 | **keep-made-plus-draw** | 120 | 240 | 12.50 | 2.74 | 4.17 | 25% | 25% | 0.0000 | 0 | 0 | 0 | 0.023 | 0.391 | 6.52 | 0 |
| 3 | **bot** | 120 | 240 | 11.08 | 2.63 | 4.22 | 22% | 22% | 0.0000 | 0 | 0 | 0 | 0.023 | 0.564 | 4.39 | 0 |
| 4 | **min_raiser** | 120 | 240 | 1.88 | 1.21 | 6.16 | 4% | 4% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.085 | 2.02 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 49% | 50% | 2% | 0% | 0% | 0% | 0% |
| keep-made-plus-draw | 25% | 0% | 0% | 18% | 27% | 24% | 6% | 0% |
| bot | 22% | 1% | 0% | 27% | 22% | 20% | 9% | 0% |
| min_raiser | 4% | 0% | 0% | 4% | 12% | 28% | 48% | 3% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | keep-made-plus-draw | bot | min_raiser |
|---|---|---|---|---|
| **check_or_fold** | · | 60-0-60 | 68-0-52 | 111-0-9 |
| **keep-made-plus-draw** | 60-0-60 | · | 65-0-55 | 99-3-18 |
| **bot** | 52-0-68 | 55-0-65 | · | 105-1-14 |
| **min_raiser** | 9-0-111 | 18-3-99 | 14-1-105 | · |

Files: `arena/results/20261106-190537-ladder-4df2` (tables.jsonl, seats.csv, summary.json, run.json).
