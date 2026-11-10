# Arena run `icm-pushfold-v8` — fast mode

Started 2026-11-06T19:53:02 · seed `icm1` · scheme ab · 804 tables · 107755 hands · 36.5 s

Command: `ab bot bots/icm-pushfold-v8 --tables 400 --seed icm1 --name icm-pushfold-v8 --agent Claude (icm-pushfold agent) --question v8 = v7 with PUSH 18 / RESHOVE 22 / PREMIUM 0.50 (both sweep winners combined) vs bot (v0-nowar) --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `icm-pushfold-v8` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 397 | 19.71 | 20.56 | +0.86 | ±0.63 | 0.007 | 75 / 293 / 29 | **icm-pushfold-v8 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~155.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **icm-pushfold-v8** | 397 | 1072 | 19.48 | 1.33 | 3.63 | 47% | 30% | 0.0004 | 63 | 0 | 0 | 0.062 | 19.176 | 52.47 | 164 |
| 2 | **bot** | 397 | 1072 | 18.28 | 1.36 | 3.78 | 42% | 31% | 0.0000 | 0 | 0 | 0 | 0.019 | 1.291 | 31.13 | 0 |
| 3 | **check_or_fold** | 794 | 2144 | 14.88 | 0.54 | 3.30 | 60% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.173 | 49.55 | 0 |
| 4 | **min_raiser** | 792 | 2144 | 3.74 | 0.55 | 5.98 | 8% | 7% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.477 | 51.34 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| icm-pushfold-v8 | 30% | 11% | 7% | 10% | 16% | 16% | 8% | 1% |
| bot | 31% | 7% | 4% | 11% | 19% | 18% | 9% | 2% |
| check_or_fold | 0% | 29% | 31% | 25% | 12% | 3% | 0% | 0% |
| min_raiser | 7% | 0% | 1% | 3% | 12% | 32% | 32% | 12% |

## Head-to-head (row finished above column: wins-ties-losses)

| | icm-pushfold-v8 | bot | check_or_fold | min_raiser |
|---|---|---|---|---|
| **icm-pushfold-v8** | · | 0-0-0 | 325-0-67 | 316-0-75 |
| **bot** | 0-0-0 | · | 329-0-63 | 325-0-66 |
| **check_or_fold** | 67-0-325 | 63-0-329 | · | 629-0-153 |
| **min_raiser** | 75-0-316 | 66-0-325 | 153-0-629 | · |

Files: `arena/results/20261106-195302-icm-pushfold-v8-2138` (tables.jsonl, seats.csv, summary.json, run.json).
