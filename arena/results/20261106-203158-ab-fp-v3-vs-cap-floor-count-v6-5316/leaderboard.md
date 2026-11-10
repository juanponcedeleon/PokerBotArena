# Arena run `ab-fp-v3-vs-cap-floor-count-v6` — fast mode

Started 2026-11-06T20:31:58 · seed `fp3b` · scheme ab · 2004 tables · 252233 hands · 49.4 s

Command: `ab cap-floor-count-v6 fp-v3 --tables 1000 --seed fp3b --agent Claude (keep-rule agent, branching out) --question fp-v3 vs cap-floor-count-v6 (upload) in the kit field, final confirmation --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `fp-v3` replaces `cap-floor-count-v6` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 989 | 22.67 | 25.21 | +2.54 | ±0.91 | 0.000 | 437 / 373 / 179 | **fp-v3 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~814.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-v3** | 989 | 2672 | 23.69 | 0.80 | 3.19 | 61% | 31% | 0.0001 | 25 | 0 | 0 | 0.025 | 0.389 | 164.38 | 0 |
| 2 | **cap-floor-count-v6** | 989 | 2672 | 20.82 | 0.86 | 3.53 | 49% | 33% | 0.0001 | 30 | 0 | 0 | 0.017 | 0.515 | 163.77 | 0 |
| 3 | **check_or_fold** | 1960 | 5344 | 12.10 | 0.33 | 3.59 | 51% | 0% | 0.0000 | 7 | 0 | 0 | 0.003 | 0.023 | 156.15 | 0 |
| 4 | **min_raiser** | 1968 | 5344 | 3.15 | 0.31 | 6.06 | 7% | 5% | 0.0000 | 2 | 0 | 0 | 0.004 | 0.075 | 130.43 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-v3 | 31% | 23% | 7% | 6% | 12% | 13% | 7% | 1% |
| cap-floor-count-v6 | 33% | 12% | 4% | 9% | 16% | 15% | 9% | 2% |
| check_or_fold | 0% | 19% | 31% | 27% | 16% | 5% | 1% | 0% |
| min_raiser | 5% | 1% | 1% | 3% | 14% | 30% | 32% | 14% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-v3 | cap-floor-count-v6 | check_or_fold | min_raiser |
|---|---|---|---|---|
| **fp-v3** | · | 0-0-0 | 865-0-102 | 810-0-161 |
| **cap-floor-count-v6** | 0-0-0 | · | 870-0-97 | 866-0-105 |
| **check_or_fold** | 102-0-865 | 97-0-870 | · | 1582-0-342 |
| **min_raiser** | 161-0-810 | 105-0-866 | 342-0-1582 | · |

Files: `arena/results/20261106-203158-ab-fp-v3-vs-cap-floor-count-v6-5316` (tables.jsonl, seats.csv, summary.json, run.json).
