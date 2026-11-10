# Arena run `icm-pushfold-v7-rerun` — fast mode

Started 2026-11-06T19:51:28 · seed `icm1` · scheme ab · 804 tables · 104578 hands · 34.4 s

Command: `ab bot bots/icm-pushfold-v7 --tables 400 --seed icm1 --name icm-pushfold-v7-rerun --agent Claude (icm-pushfold agent) --question v7 rerun (first run lost a worker to MemoryError at import): PUSH 15 / RESHOVE 18 / PREMIUM 0.30 vs bot (v0-nowar) --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `icm-pushfold-v7` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 397 | 19.71 | 20.52 | +0.82 | ±0.56 | 0.004 | 60 / 308 / 29 | **icm-pushfold-v7 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~123.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **icm-pushfold-v7** | 397 | 1072 | 19.33 | 1.33 | 3.65 | 47% | 30% | 0.0001 | 19 | 0 | 0 | 0.060 | 13.935 | 71.62 | 164 |
| 2 | **bot** | 397 | 1072 | 18.28 | 1.36 | 3.78 | 42% | 31% | 0.0000 | 0 | 0 | 0 | 0.019 | 1.417 | 46.75 | 0 |
| 3 | **check_or_fold** | 794 | 2144 | 15.00 | 0.54 | 3.29 | 60% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.144 | 21.03 | 0 |
| 4 | **min_raiser** | 792 | 2144 | 3.69 | 0.54 | 5.98 | 8% | 7% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.333 | 27.56 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| icm-pushfold-v7 | 30% | 9% | 7% | 10% | 16% | 17% | 9% | 2% |
| bot | 31% | 7% | 4% | 11% | 19% | 18% | 9% | 2% |
| check_or_fold | 0% | 29% | 31% | 24% | 12% | 3% | 0% | 0% |
| min_raiser | 7% | 0% | 1% | 3% | 12% | 32% | 32% | 12% |

## Head-to-head (row finished above column: wins-ties-losses)

| | icm-pushfold-v7 | bot | check_or_fold | min_raiser |
|---|---|---|---|---|
| **icm-pushfold-v7** | · | 0-0-0 | 327-0-65 | 318-0-73 |
| **bot** | 0-0-0 | · | 329-0-63 | 325-0-66 |
| **check_or_fold** | 65-0-327 | 63-0-329 | · | 631-0-151 |
| **min_raiser** | 73-0-318 | 66-0-325 | 151-0-631 | · |

Files: `arena/results/20261106-195128-icm-pushfold-v7-rerun-4417` (tables.jsonl, seats.csv, summary.json, run.json).
