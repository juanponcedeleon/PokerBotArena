# Arena run `ab-fp-v4-vs-fp-v3` — fast mode

Started 2026-11-06T20:48:02 · seed `fp4a` · scheme ab · 2002 tables · 250432 hands · 94.7 s

Command: `ab fp-v3 fp-v4 --field v0-baseline check_or_fold arch-folder arch-shover arch-station cap-floor-count-v6 --tables 1000 --seed fp4a --agent Claude (keep-rule agent, branching out) --question fp-v4 (HU/3-handed ranges, bubble margin, cap awareness) vs fp-v3, archetype field + cfc-v6 --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `fp-v4` replaces `fp-v3` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 735 | 23.12 | 21.55 | -1.56 | ±1.31 | 0.019 | 154 / 379 / 202 | **fp-v3 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~1258.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-v3** | 735 | 1144 | 21.97 | 1.21 | 3.23 | 59% | 28% | 0.0001 | 13 | 0 | 0 | 0.036 | 18.282 | 59.90 | 0 |
| 2 | **fp-v4** | 735 | 1144 | 20.65 | 1.28 | 3.43 | 51% | 31% | 0.0001 | 17 | 0 | 0 | 0.040 | 18.450 | 54.46 | 0 |
| 3 | **cap-floor-count-v6** | 1464 | 2288 | 17.59 | 0.87 | 3.79 | 44% | 25% | 0.0001 | 33 | 0 | 0 | 0.024 | 19.839 | 56.12 | 0 |
| 4 | **arch-folder** | 1496 | 2288 | 17.10 | 0.65 | 3.36 | 59% | 7% | 0.0000 | 2 | 0 | 0 | 0.016 | 14.171 | 39.37 | 0 |
| 5 | **check_or_fold** | 1472 | 2288 | 14.13 | 0.49 | 3.32 | 61% | 0% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.136 | 25.98 | 0 |
| 6 | **v0-baseline** | 1452 | 2288 | 13.65 | 0.84 | 4.33 | 33% | 21% | 0.0000 | 2 | 0 | 0 | 0.024 | 16.284 | 43.00 | 0 |
| 7 | **arch-shover** | 1452 | 2288 | 2.43 | 0.43 | 6.08 | 6% | 4% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.339 | 36.24 | 0 |
| 8 | **arch-station** | 1482 | 2288 | 1.29 | 0.26 | 6.07 | 5% | 1% | 0.0000 | 0 | 0 | 0 | 0.007 | 10.146 | 53.25 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-v3 | 28% | 17% | 13% | 11% | 13% | 10% | 5% | 1% |
| fp-v4 | 31% | 10% | 10% | 13% | 16% | 11% | 7% | 2% |
| cap-floor-count-v6 | 25% | 12% | 7% | 12% | 17% | 15% | 9% | 3% |
| arch-folder | 6% | 34% | 18% | 16% | 12% | 9% | 3% | 1% |
| check_or_fold | 0% | 20% | 41% | 28% | 10% | 1% | 0% | 0% |
| v0-baseline | 21% | 7% | 6% | 11% | 18% | 20% | 13% | 5% |
| arch-shover | 4% | 0% | 1% | 6% | 14% | 31% | 29% | 15% |
| arch-station | 1% | 1% | 3% | 8% | 17% | 27% | 28% | 15% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-v3 | fp-v4 | cap-floor-count-v6 | arch-folder | check_or_fold | v0-baseline | arch-shover | arch-station |
|---|---|---|---|---|---|---|---|---|
| **fp-v3** | · | 0-0-0 | 283-1-235 | 340-0-191 | 363-0-165 | 319-1-192 | 470-5-41 | 495-5-30 |
| **fp-v4** | 0-0-0 | · | 301-1-217 | 327-0-204 | 322-0-206 | 320-1-191 | 458-5-53 | 496-5-29 |
| **cap-floor-count-v6** | 235-1-283 | 217-1-301 | · | 569-0-517 | 551-0-479 | 562-2-476 | 878-24-116 | 966-20-76 |
| **arch-folder** | 191-0-340 | 204-0-327 | 517-0-569 | · | 681-0-405 | 595-2-441 | 971-2-79 | 996-4-60 |
| **check_or_fold** | 165-0-363 | 206-0-322 | 479-0-551 | 405-0-681 | · | 572-0-486 | 948-0-82 | 1029-0-25 |
| **v0-baseline** | 192-1-319 | 191-1-320 | 476-2-562 | 441-2-595 | 486-0-572 | · | 832-46-138 | 841-22-157 |
| **arch-shover** | 41-5-470 | 53-5-458 | 116-24-878 | 79-2-971 | 82-0-948 | 138-46-832 | · | 348-156-534 |
| **arch-station** | 30-5-495 | 29-5-496 | 76-20-966 | 60-4-996 | 25-0-1029 | 157-22-841 | 534-156-348 | · |

Files: `arena/results/20261106-204802-ab-fp-v4-vs-fp-v3-594f` (tables.jsonl, seats.csv, summary.json, run.json).
