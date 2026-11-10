# Arena run `icm-pushfold-v4` — fast mode

Started 2026-11-06T19:34:21 · seed `icm1` · scheme ab · 804 tables · 100165 hands · 36.9 s

Command: `ab bot bots/icm-pushfold-v4 --tables 400 --seed icm1 --log --name icm-pushfold-v4 --agent Claude (icm-pushfold agent) --question v4: ICM push/fold only when the stack at risk is <=16 BB; deep all-ins back to v0 logic; survival premium 0.15 --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `icm-pushfold-v4` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 397 | 19.71 | 17.71 | -2.00 | ±1.32 | 0.003 | 61 / 223 / 113 | **bot is better** |

Pairs needed to resolve a 1-point difference at this variance: ~692.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **bot** | 397 | 1072 | 18.28 | 1.36 | 3.78 | 42% | 31% | 0.0000 | 6 | 0 | 0 | 0.018 | 0.289 | 227.51 | 0 |
| 2 | **icm-pushfold-v4** | 397 | 1072 | 16.48 | 1.36 | 3.93 | 36% | 30% | 0.0002 | 17 | 0 | 0 | 0.077 | 9.212 | 212.71 | 164 |
| 3 | **check_or_fold** | 794 | 2144 | 16.31 | 0.53 | 3.17 | 65% | 0% | 0.0000 | 1 | 0 | 0 | 0.004 | 0.037 | 174.24 | 0 |
| 4 | **min_raiser** | 792 | 2144 | 3.81 | 0.55 | 5.72 | 9% | 7% | 0.0000 | 1 | 0 | 0 | 0.004 | 0.056 | 131.32 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| bot | 31% | 7% | 4% | 11% | 19% | 18% | 9% | 2% |
| icm-pushfold-v4 | 30% | 3% | 4% | 13% | 21% | 19% | 9% | 2% |
| check_or_fold | 0% | 33% | 33% | 23% | 10% | 2% | 0% | 0% |
| min_raiser | 7% | 0% | 2% | 5% | 20% | 32% | 25% | 9% |

## Head-to-head (row finished above column: wins-ties-losses)

| | bot | icm-pushfold-v4 | check_or_fold | min_raiser |
|---|---|---|---|---|
| **bot** | · | 0-0-0 | 329-0-63 | 325-0-66 |
| **icm-pushfold-v4** | 0-0-0 | · | 316-0-76 | 314-0-77 |
| **check_or_fold** | 63-0-329 | 76-0-316 | · | 629-0-153 |
| **min_raiser** | 66-0-325 | 77-0-314 | 153-0-629 | · |

Files: `arena/results/20261106-193421-icm-pushfold-v4-3905` (tables.jsonl, seats.csv, summary.json, run.json).
