# Arena run `ab-fp-v3-vs-fp-v2` — fast mode

Started 2026-11-06T20:30:16 · seed `fp3a` · scheme ab · 2002 tables · 260682 hands · 61.2 s

Command: `ab fp-v2 fp-v3 --field v0-baseline check_or_fold arch-folder arch-shover arch-station cap-floor-count-v6 --tables 1000 --seed fp3a --agent Claude (keep-rule agent, branching out) --question fp-v3 (ICM-tight deep all-in calls) vs fp-v2, archetype field + cfc-v6 --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `fp-v3` replaces `fp-v2` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 740 | 20.75 | 22.01 | +1.26 | ±0.83 | 0.003 | 90 / 596 / 54 | **fp-v3 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~511.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-v3** | 740 | 1144 | 21.32 | 1.20 | 3.26 | 57% | 26% | 0.0001 | 17 | 0 | 0 | 0.029 | 14.180 | 358.61 | 0 |
| 2 | **fp-v2** | 740 | 1144 | 20.34 | 1.21 | 3.41 | 54% | 26% | 0.0001 | 13 | 0 | 0 | 0.029 | 16.518 | 210.05 | 0 |
| 3 | **cap-floor-count-v6** | 1494 | 2288 | 18.19 | 0.89 | 3.76 | 46% | 27% | 0.0001 | 17 | 0 | 0 | 0.019 | 18.279 | 285.22 | 0 |
| 4 | **arch-folder** | 1468 | 2288 | 16.71 | 0.64 | 3.39 | 58% | 6% | 0.0000 | 4 | 0 | 0 | 0.012 | 0.337 | 289.10 | 0 |
| 5 | **v0-baseline** | 1502 | 2288 | 14.20 | 0.87 | 4.31 | 34% | 23% | 0.0000 | 6 | 0 | 0 | 0.019 | 2.077 | 264.62 | 0 |
| 6 | **check_or_fold** | 1488 | 2288 | 13.45 | 0.49 | 3.39 | 58% | 0% | 0.0000 | 2 | 0 | 0 | 0.004 | 0.043 | 259.89 | 0 |
| 7 | **arch-shover** | 1446 | 2288 | 2.65 | 0.44 | 6.01 | 7% | 5% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.054 | 26.26 | 0 |
| 8 | **arch-station** | 1446 | 2288 | 1.47 | 0.27 | 6.02 | 6% | 1% | 0.0000 | 3 | 0 | 0 | 0.006 | 0.131 | 297.55 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-v3 | 26% | 20% | 11% | 12% | 14% | 10% | 6% | 1% |
| fp-v2 | 26% | 18% | 9% | 12% | 14% | 12% | 6% | 2% |
| cap-floor-count-v6 | 27% | 10% | 8% | 11% | 15% | 17% | 8% | 3% |
| arch-folder | 6% | 33% | 19% | 16% | 14% | 9% | 3% | 0% |
| v0-baseline | 23% | 6% | 5% | 11% | 19% | 17% | 14% | 5% |
| check_or_fold | 0% | 18% | 41% | 30% | 9% | 2% | 0% | 0% |
| arch-shover | 5% | 0% | 2% | 7% | 14% | 30% | 28% | 15% |
| arch-station | 1% | 1% | 4% | 8% | 16% | 30% | 27% | 14% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-v3 | fp-v2 | cap-floor-count-v6 | arch-folder | v0-baseline | check_or_fold | arch-shover | arch-station |
|---|---|---|---|---|---|---|---|---|
| **fp-v3** | · | 0-0-0 | 295-0-248 | 338-0-193 | 324-1-218 | 361-0-168 | 472-6-44 | 477-5-34 |
| **fp-v2** | 0-0-0 | · | 281-1-261 | 328-0-203 | 315-2-226 | 340-0-189 | 433-21-68 | 454-16-46 |
| **cap-floor-count-v6** | 248-0-295 | 261-1-281 | · | 517-0-539 | 591-2-485 | 594-0-480 | 938-20-104 | 964-18-76 |
| **arch-folder** | 193-0-338 | 203-0-328 | 539-0-517 | · | 611-2-477 | 669-0-385 | 938-4-88 | 951-4-61 |
| **v0-baseline** | 218-1-324 | 226-2-315 | 485-2-591 | 477-2-611 | · | 512-0-566 | 839-34-147 | 872-28-148 |
| **check_or_fold** | 168-0-361 | 189-0-340 | 480-0-594 | 385-0-669 | 566-0-512 | · | 943-0-89 | 1027-0-21 |
| **arch-shover** | 44-6-472 | 68-21-433 | 104-20-938 | 88-4-938 | 147-34-839 | 89-0-943 | · | 334-157-527 |
| **arch-station** | 34-5-477 | 46-16-454 | 76-18-964 | 61-4-951 | 148-28-872 | 21-0-1027 | 527-157-334 | · |

Files: `arena/results/20261106-203016-ab-fp-v3-vs-fp-v2-9067` (tables.jsonl, seats.csv, summary.json, run.json).
