# Arena run `icm-pushfold-v5` — fast mode

Started 2026-11-06T19:41:10 · seed `icm1` · scheme ab · 804 tables · 98927 hands · 49.8 s

Command: `ab bot bots/icm-pushfold-v5 --tables 400 --seed icm1 --log --name icm-pushfold-v5 --agent Claude (icm-pushfold agent) --question v5: rebased on v0-nowar (bot/ as of 19:22); ICM push/fold + per-seat rates only where the stack at risk is <=16 BB --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `icm-pushfold-v5` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 397 | 19.71 | 20.36 | +0.65 | ±0.48 | 0.008 | 52 / 320 / 25 | **icm-pushfold-v5 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~91.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **icm-pushfold-v5** | 397 | 1072 | 19.10 | 1.35 | 3.69 | 45% | 31% | 0.0011 | 165 | 0 | 0 | 0.077 | 25.523 | 403.07 | 164 |
| 2 | **bot** | 397 | 1072 | 18.28 | 1.36 | 3.78 | 42% | 31% | 0.0000 | 6 | 0 | 0 | 0.018 | 11.570 | 244.46 | 0 |
| 3 | **check_or_fold** | 794 | 2144 | 15.20 | 0.54 | 3.26 | 61% | 0% | 0.0000 | 4 | 0 | 0 | 0.004 | 0.082 | 162.02 | 0 |
| 4 | **min_raiser** | 792 | 2144 | 3.61 | 0.54 | 5.99 | 8% | 7% | 0.0000 | 1 | 0 | 0 | 0.004 | 0.200 | 105.41 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| icm-pushfold-v5 | 31% | 9% | 5% | 10% | 18% | 17% | 8% | 2% |
| bot | 31% | 7% | 4% | 11% | 19% | 18% | 9% | 2% |
| check_or_fold | 0% | 29% | 32% | 25% | 11% | 2% | 0% | 0% |
| min_raiser | 7% | 0% | 1% | 3% | 12% | 32% | 32% | 12% |

## Head-to-head (row finished above column: wins-ties-losses)

| | icm-pushfold-v5 | bot | check_or_fold | min_raiser |
|---|---|---|---|---|
| **icm-pushfold-v5** | · | 0-0-0 | 332-0-60 | 322-0-69 |
| **bot** | 0-0-0 | · | 329-0-63 | 325-0-66 |
| **check_or_fold** | 60-0-332 | 63-0-329 | · | 634-0-148 |
| **min_raiser** | 69-0-322 | 66-0-325 | 148-0-634 | · |

Files: `arena/results/20261106-194110-icm-pushfold-v5-a8e3` (tables.jsonl, seats.csv, summary.json, run.json).
