# Arena run `cfc-v1-ab` — fast mode

Started 2026-11-06T19:12:43 · seed `cfc1` · scheme ab · 804 tables · 77490 hands · 14.7 s

Command: `ab bot bots/cap-floor-count --tables 400 --seed cfc1 --name cfc-v1-ab --agent Claude (cap-floor-count agent) --question Does cap/floor/count postflop (01 S1.1-S1.3, 04 S4.1-S4.4) beat bot v0 postflop?`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cap-floor-count` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 397 | 18.11 | 18.52 | +0.41 | ±0.46 | 0.080 | 15 / 373 / 9 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~84.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 788 | 2144 | 17.25 | 0.53 | 3.10 | 68% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.063 | 33.57 | 0 |
| 2 | **cap-floor-count** | 397 | 1072 | 16.75 | 1.37 | 3.93 | 37% | 31% | 0.0000 | 0 | 0 | 0 | 0.020 | 1.044 | 39.35 | 0 |
| 3 | **bot** | 397 | 1072 | 16.52 | 1.37 | 3.94 | 36% | 31% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.367 | 46.47 | 0 |
| 4 | **min_raiser** | 784 | 2144 | 3.61 | 0.53 | 5.49 | 9% | 7% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.166 | 16.81 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 36% | 32% | 21% | 8% | 3% | 0% | 0% |
| cap-floor-count | 31% | 1% | 5% | 13% | 21% | 17% | 10% | 2% |
| bot | 31% | 1% | 5% | 14% | 20% | 18% | 10% | 2% |
| min_raiser | 7% | 0% | 2% | 11% | 20% | 33% | 22% | 5% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | cap-floor-count | bot | min_raiser |
|---|---|---|---|---|
| **check_or_fold** | · | 62-0-327 | 68-0-321 | 628-0-140 |
| **cap-floor-count** | 327-0-62 | · | 0-0-0 | 325-0-62 |
| **bot** | 321-0-68 | 0-0-0 | · | 319-0-68 |
| **min_raiser** | 140-0-628 | 62-0-325 | 68-0-319 | · |

Files: `arena/results/20261106-191243-cfc-v1-ab-687b` (tables.jsonl, seats.csv, summary.json, run.json).
