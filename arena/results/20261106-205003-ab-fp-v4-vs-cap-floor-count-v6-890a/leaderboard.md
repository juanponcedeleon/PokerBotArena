# Arena run `ab-fp-v4-vs-cap-floor-count-v6` — fast mode

Started 2026-11-06T20:50:03 · seed `fp4b` · scheme ab · 2004 tables · 235072 hands · 69.5 s

Command: `ab cap-floor-count-v6 fp-v4 --tables 1000 --seed fp4b --agent Claude (keep-rule agent, branching out) --question fp-v4 vs cap-floor-count-v6 (upload), kit field --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `fp-v4` replaces `cap-floor-count-v6` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 982 | 23.56 | 24.06 | +0.50 | ±0.84 | 0.246 | 243 / 506 / 233 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~698.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-v4** | 982 | 2672 | 21.75 | 0.86 | 3.39 | 51% | 34% | 0.0002 | 51 | 0 | 0 | 0.032 | 8.666 | 247.68 | 0 |
| 2 | **cap-floor-count-v6** | 982 | 2672 | 21.46 | 0.86 | 3.44 | 51% | 34% | 0.0001 | 32 | 0 | 0 | 0.020 | 8.268 | 161.51 | 0 |
| 3 | **check_or_fold** | 1966 | 5344 | 13.89 | 0.34 | 3.41 | 57% | 0% | 0.0000 | 4 | 0 | 0 | 0.004 | 0.035 | 125.40 | 0 |
| 4 | **min_raiser** | 1972 | 5344 | 2.00 | 0.26 | 6.23 | 4% | 4% | 0.0000 | 9 | 0 | 0 | 0.005 | 0.122 | 149.56 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-v4 | 34% | 13% | 4% | 10% | 15% | 15% | 7% | 1% |
| cap-floor-count-v6 | 34% | 13% | 4% | 10% | 15% | 15% | 7% | 1% |
| check_or_fold | 0% | 25% | 33% | 25% | 13% | 4% | 1% | 0% |
| min_raiser | 4% | 0% | 1% | 3% | 14% | 30% | 35% | 14% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-v4 | cap-floor-count-v6 | check_or_fold | min_raiser |
|---|---|---|---|---|
| **fp-v4** | · | 0-0-0 | 889-0-74 | 892-0-74 |
| **cap-floor-count-v6** | 0-0-0 | · | 882-0-81 | 880-0-86 |
| **check_or_fold** | 74-0-889 | 81-0-882 | · | 1731-0-203 |
| **min_raiser** | 74-0-892 | 86-0-880 | 203-0-1731 | · |

Files: `arena/results/20261106-205003-ab-fp-v4-vs-cap-floor-count-v6-890a` (tables.jsonl, seats.csv, summary.json, run.json).
