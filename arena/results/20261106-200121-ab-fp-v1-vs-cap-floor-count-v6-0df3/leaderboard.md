# Arena run `ab-fp-v1-vs-cap-floor-count-v6` — fast mode

Started 2026-11-06T20:01:21 · seed `fp1c` · scheme ab · 2004 tables · 253610 hands · 49.2 s

Command: `ab cap-floor-count-v6 fp-v1 --tables 1000 --seed fp1c --agent Claude (keep-rule agent, branching out) --question fp-v1 vs cap-floor-count-v6 in the kit field (min_raiser + check_or_fold), robustness --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `fp-v1` replaces `cap-floor-count-v6` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 986 | 23.21 | 24.93 | +1.71 | ±0.96 | 0.000 | 409 / 370 / 207 | **fp-v1 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~912.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-v1** | 986 | 2672 | 23.44 | 0.81 | 3.22 | 59% | 31% | 0.0000 | 8 | 0 | 0 | 0.023 | 0.677 | 192.88 | 0 |
| 2 | **cap-floor-count-v6** | 986 | 2672 | 21.22 | 0.86 | 3.51 | 50% | 33% | 0.0000 | 7 | 0 | 0 | 0.016 | 1.399 | 169.19 | 0 |
| 3 | **check_or_fold** | 1978 | 5344 | 12.11 | 0.33 | 3.58 | 51% | 0% | 0.0000 | 1 | 0 | 0 | 0.003 | 0.040 | 155.74 | 0 |
| 4 | **min_raiser** | 1960 | 5344 | 3.06 | 0.31 | 6.07 | 7% | 5% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.085 | 15.86 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-v1 | 31% | 22% | 6% | 7% | 12% | 13% | 7% | 2% |
| cap-floor-count-v6 | 33% | 13% | 3% | 8% | 17% | 16% | 8% | 2% |
| check_or_fold | 0% | 19% | 32% | 27% | 16% | 5% | 1% | 0% |
| min_raiser | 5% | 1% | 1% | 4% | 13% | 28% | 33% | 14% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-v1 | cap-floor-count-v6 | check_or_fold | min_raiser |
|---|---|---|---|---|
| **fp-v1** | · | 0-0-0 | 869-0-104 | 808-0-156 |
| **cap-floor-count-v6** | 0-0-0 | · | 885-0-88 | 870-0-94 |
| **check_or_fold** | 104-0-869 | 88-0-885 | · | 1594-0-340 |
| **min_raiser** | 156-0-808 | 94-0-870 | 340-0-1594 | · |

Files: `arena/results/20261106-200121-ab-fp-v1-vs-cap-floor-count-v6-0df3` (tables.jsonl, seats.csv, summary.json, run.json).
