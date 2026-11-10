# Arena run `icm-pushfold-v10-kit` — fast mode

Started 2026-11-06T20:48:48 · seed `icm1` · scheme ab · 804 tables · 118105 hands · 92.8 s

Command: `ab bot bots/icm-pushfold-v10 --tables 400 --seed icm1 --name icm-pushfold-v10-kit --agent Claude (icm-pushfold agent) --question v10 = fp-v3 + ICM short-stack module, kit field --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `icm-pushfold-v10` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 397 | 24.37 | 25.65 | +1.27 | ±0.78 | 0.001 | 131 / 214 / 52 | **icm-pushfold-v10 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~240.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **icm-pushfold-v10** | 397 | 1072 | 24.66 | 1.18 | 2.99 | 68% | 28% | 0.0006 | 95 | 0 | 0 | 0.105 | 22.260 | 264.95 | 164 |
| 2 | **bot** | 397 | 1072 | 22.92 | 1.27 | 3.26 | 58% | 30% | 0.0000 | 0 | 0 | 0 | 0.031 | 19.872 | 32.87 | 0 |
| 3 | **check_or_fold** | 794 | 2144 | 9.11 | 0.49 | 3.92 | 39% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.111 | 42.61 | 0 |
| 4 | **min_raiser** | 792 | 2144 | 4.60 | 0.60 | 6.01 | 10% | 8% | 0.0000 | 1 | 0 | 0 | 0.005 | 0.977 | 249.60 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| icm-pushfold-v10 | 28% | 26% | 13% | 7% | 9% | 8% | 6% | 1% |
| bot | 30% | 22% | 6% | 7% | 12% | 13% | 7% | 1% |
| check_or_fold | 0% | 12% | 27% | 29% | 21% | 9% | 2% | 0% |
| min_raiser | 8% | 1% | 1% | 2% | 9% | 31% | 33% | 15% |

## Head-to-head (row finished above column: wins-ties-losses)

| | icm-pushfold-v10 | bot | check_or_fold | min_raiser |
|---|---|---|---|---|
| **icm-pushfold-v10** | · | 0-0-0 | 351-0-41 | 296-0-95 |
| **bot** | 0-0-0 | · | 343-0-49 | 318-0-73 |
| **check_or_fold** | 41-0-351 | 49-0-343 | · | 581-0-201 |
| **min_raiser** | 95-0-296 | 73-0-318 | 201-0-581 | · |

Files: `arena/results/20261106-204848-icm-pushfold-v10-kit-a414` (tables.jsonl, seats.csv, summary.json, run.json).
