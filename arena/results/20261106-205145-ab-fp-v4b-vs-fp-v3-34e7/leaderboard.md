# Arena run `ab-fp-v4b-vs-fp-v3` — fast mode

Started 2026-11-06T20:51:45 · seed `fp4c` · scheme ab · 2002 tables · 251261 hands · 41.1 s

Command: `ab fp-v3 fp-v4b --field v0-baseline check_or_fold arch-folder arch-shover arch-station cap-floor-count-v6 --tables 1000 --seed fp4c --agent Claude (keep-rule agent, branching out) --question fp-v4b (HU/3-handed ranges + bubble margin, no cap awareness) vs fp-v3, archetype field + cfc-v6 --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `fp-v4b` replaces `fp-v3` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 745 | 22.53 | 20.69 | -1.83 | ±1.30 | 0.006 | 160 / 376 / 209 | **fp-v3 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~1264.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-v3** | 745 | 1144 | 21.67 | 1.20 | 3.28 | 58% | 27% | 0.0000 | 0 | 0 | 0 | 0.031 | 0.515 | 72.91 | 0 |
| 2 | **fp-v4b** | 745 | 1144 | 19.97 | 1.25 | 3.47 | 51% | 28% | 0.0000 | 0 | 0 | 0 | 0.034 | 0.577 | 58.51 | 0 |
| 3 | **cap-floor-count-v6** | 1464 | 2288 | 18.42 | 0.89 | 3.69 | 46% | 27% | 0.0000 | 1 | 0 | 0 | 0.020 | 0.777 | 81.17 | 0 |
| 4 | **arch-folder** | 1496 | 2288 | 15.69 | 0.64 | 3.51 | 54% | 6% | 0.0000 | 0 | 0 | 0 | 0.013 | 0.164 | 62.79 | 0 |
| 5 | **check_or_fold** | 1482 | 2288 | 14.63 | 0.48 | 3.29 | 63% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.029 | 3.68 | 0 |
| 6 | **v0-baseline** | 1518 | 2288 | 13.91 | 0.84 | 4.31 | 35% | 21% | 0.0000 | 0 | 0 | 0 | 0.021 | 0.343 | 57.31 | 0 |
| 7 | **arch-shover** | 1476 | 2288 | 2.77 | 0.45 | 6.04 | 7% | 5% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.047 | 2.08 | 0 |
| 8 | **arch-station** | 1452 | 2288 | 1.26 | 0.27 | 6.08 | 4% | 1% | 0.0000 | 0 | 0 | 0 | 0.006 | 0.079 | 3.08 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-v3 | 27% | 19% | 12% | 11% | 13% | 11% | 6% | 2% |
| fp-v4b | 28% | 14% | 9% | 13% | 15% | 13% | 7% | 2% |
| cap-floor-count-v6 | 27% | 11% | 7% | 13% | 16% | 14% | 9% | 2% |
| arch-folder | 5% | 32% | 17% | 17% | 15% | 9% | 4% | 1% |
| check_or_fold | 0% | 20% | 43% | 26% | 9% | 1% | 0% | 0% |
| v0-baseline | 21% | 7% | 7% | 11% | 17% | 20% | 13% | 5% |
| arch-shover | 5% | 0% | 1% | 7% | 14% | 27% | 30% | 16% |
| arch-station | 1% | 1% | 3% | 9% | 17% | 28% | 26% | 16% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-v3 | fp-v4b | cap-floor-count-v6 | arch-folder | check_or_fold | v0-baseline | arch-shover | arch-station |
|---|---|---|---|---|---|---|---|---|
| **fp-v3** | · | 0-0-0 | 271-2-255 | 357-0-185 | 365-0-170 | 343-0-203 | 475-7-56 | 476-7-37 |
| **fp-v4b** | 0-0-0 | · | 269-2-257 | 329-0-213 | 317-0-218 | 332-0-214 | 453-7-78 | 476-7-37 |
| **cap-floor-count-v6** | 255-2-271 | 257-2-269 | · | 606-0-452 | 615-0-451 | 620-6-462 | 903-18-111 | 952-12-68 |
| **arch-folder** | 185-0-357 | 213-0-329 | 452-0-606 | · | 607-0-455 | 597-6-493 | 972-4-90 | 1006-2-64 |
| **check_or_fold** | 170-0-365 | 218-0-317 | 451-0-615 | 455-0-607 | · | 643-0-437 | 975-0-101 | 996-0-34 |
| **v0-baseline** | 203-0-343 | 214-0-332 | 462-6-620 | 493-6-597 | 437-0-643 | · | 880-28-170 | 898-22-156 |
| **arch-shover** | 56-7-475 | 78-7-453 | 111-18-903 | 90-4-972 | 101-0-975 | 170-28-880 | · | 406-158-468 |
| **arch-station** | 37-7-476 | 37-7-476 | 68-12-952 | 64-2-1006 | 34-0-996 | 156-22-898 | 468-158-406 | · |

Files: `arena/results/20261106-205145-ab-fp-v4b-vs-fp-v3-34e7` (tables.jsonl, seats.csv, summary.json, run.json).
