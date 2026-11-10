# Arena run `ab-smoke` — fast mode

Started 2026-11-06T19:01:36 · seed `ab1` · scheme ab · 24 tables · 2230 hands · 2.1 s

Command: `ab bot bot --tables 12 --seed ab1 --name ab-smoke --no-experiment-log --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `bot@B` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 12 | 14.03 | 14.03 | +0.00 | ±0.00 | - | 0 / 12 / 0 | no significant difference |

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 24 | 64 | 17.50 | 3.15 | 3.06 | 69% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.023 | 0.56 | 0 |
| 2 | **bot** | 12 | 32 | 14.17 | 8.21 | 4.16 | 31% | 28% | 0.0000 | 0 | 0 | 0 | 0.023 | 0.216 | 0.41 | 0 |
| 3 | **bot@B** | 12 | 32 | 14.17 | 8.21 | 4.16 | 31% | 28% | 0.0000 | 0 | 0 | 0 | 0.023 | 0.096 | 0.17 | 0 |
| 4 | **min_raiser** | 24 | 64 | 5.83 | 3.69 | 4.78 | 28% | 9% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.091 | 0.41 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 38% | 31% | 19% | 12% | 0% | 0% | 0% |
| bot | 28% | 0% | 3% | 16% | 19% | 22% | 9% | 3% |
| bot@B | 28% | 0% | 3% | 16% | 19% | 22% | 9% | 3% |
| min_raiser | 9% | 0% | 19% | 25% | 6% | 9% | 25% | 6% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | bot | bot@B | min_raiser |
|---|---|---|---|---|
| **check_or_fold** | · | 3-0-9 | 3-0-9 | 18-0-6 |
| **bot** | 9-0-3 | · | 0-0-0 | 9-0-3 |
| **bot@B** | 9-0-3 | 0-0-0 | · | 9-0-3 |
| **min_raiser** | 6-0-18 | 3-0-9 | 3-0-9 | · |

Files: `arena/results/20261106-190136-ab-smoke-d0cc` (tables.jsonl, seats.csv, summary.json, run.json).
