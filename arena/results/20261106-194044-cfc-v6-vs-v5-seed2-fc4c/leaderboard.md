# Arena run `cfc-v6-vs-v5-seed2` — fast mode

Started 2026-11-06T19:40:44 · seed `cfc7` · scheme ab · 3206 tables · 287536 hands · 56.2 s

Command: `ab bots/cap-floor-count-v5 bots/cap-floor-count-v6 --field keep-made-plus-draw keep-made-plus-draw-v2 v0-baseline icm-pushfold min_raiser check_or_fold --tables 1600 --seed cfc7 --agent Claude(cap-floor-count-agent) --question v6 vs v5, second seed (first run +0.79 +-0.79, p=0.050) --name cfc-v6-vs-v5-seed2`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cap-floor-count-v6` replaces `cap-floor-count-v5` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1163 | 17.32 | 18.24 | +0.92 | ±0.78 | 0.021 | 227 / 766 / 170 | **cap-floor-count-v6 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~712.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 2378 | 3664 | 21.90 | 0.33 | 2.69 | 86% | 0% | 0.0000 | 1 | 0 | 0 | 0.004 | 0.124 | 167.26 | 0 |
| 2 | **cap-floor-count-v6** | 1163 | 1832 | 17.76 | 0.91 | 3.58 | 50% | 21% | 0.0000 | 9 | 0 | 0 | 0.018 | 2.783 | 204.05 | 0 |
| 3 | **cap-floor-count-v5** | 1163 | 1832 | 16.99 | 0.91 | 3.66 | 47% | 20% | 0.0000 | 9 | 0 | 0 | 0.019 | 4.093 | 181.51 | 0 |
| 4 | **keep-made-plus-draw-v2** | 2370 | 3664 | 12.80 | 0.64 | 4.42 | 33% | 19% | 0.0000 | 8 | 0 | 0 | 0.018 | 1.683 | 218.18 | 0 |
| 5 | **keep-made-plus-draw** | 2348 | 3664 | 11.60 | 0.62 | 4.54 | 30% | 17% | 0.0000 | 0 | 0 | 0 | 0.018 | 1.164 | 48.54 | 0 |
| 6 | **v0-baseline** | 2326 | 3664 | 11.40 | 0.62 | 4.62 | 29% | 17% | 0.0000 | 1 | 0 | 0 | 0.017 | 1.157 | 139.19 | 0 |
| 7 | **icm-pushfold** | 2428 | 3664 | 10.47 | 0.57 | 4.59 | 30% | 12% | 0.0001 | 19 | 0 | 0 | 0.029 | 4.282 | 200.25 | 0 |
| 8 | **min_raiser** | 2350 | 3664 | 1.95 | 0.28 | 6.36 | 6% | 3% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.132 | 32.81 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 48% | 38% | 13% | 2% | 0% | 0% | 0% |
| cap-floor-count-v6 | 21% | 16% | 13% | 16% | 15% | 10% | 7% | 3% |
| cap-floor-count-v5 | 20% | 15% | 12% | 17% | 16% | 11% | 6% | 3% |
| keep-made-plus-draw-v2 | 19% | 4% | 10% | 14% | 15% | 18% | 14% | 7% |
| keep-made-plus-draw | 17% | 6% | 8% | 14% | 17% | 17% | 15% | 7% |
| v0-baseline | 17% | 5% | 8% | 13% | 17% | 17% | 15% | 8% |
| icm-pushfold | 12% | 8% | 9% | 14% | 18% | 17% | 15% | 6% |
| min_raiser | 3% | 1% | 3% | 4% | 11% | 22% | 35% | 22% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | cap-floor-count-v6 | cap-floor-count-v5 | keep-made-plus-draw-v2 | keep-made-plus-draw | v0-baseline | icm-pushfold | min_raiser |
|---|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 454-0-392 | 473-0-373 | 1106-0-604 | 1175-0-519 | 1146-0-516 | 1298-0-444 | 1621-0-73 |
| **cap-floor-count-v6** | 392-0-454 | · | 0-0-0 | 492-0-333 | 523-1-298 | 517-1-297 | 579-0-280 | 779-3-47 |
| **cap-floor-count-v5** | 373-0-473 | 0-0-0 | · | 476-0-349 | 509-1-312 | 512-1-302 | 558-0-301 | 778-3-48 |
| **keep-made-plus-draw-v2** | 604-0-1106 | 333-0-492 | 349-0-476 | · | 882-12-824 | 864-10-798 | 877-6-839 | 1422-20-244 |
| **keep-made-plus-draw** | 519-0-1175 | 298-1-523 | 312-1-509 | 824-12-882 | · | 837-6-807 | 926-2-808 | 1380-44-226 |
| **v0-baseline** | 516-0-1146 | 297-1-517 | 302-1-512 | 798-10-864 | 807-6-837 | · | 864-0-878 | 1332-48-246 |
| **icm-pushfold** | 444-0-1298 | 280-0-579 | 301-0-558 | 839-6-877 | 808-2-926 | 878-0-864 | · | 1378-26-346 |
| **min_raiser** | 73-0-1621 | 47-3-779 | 48-3-778 | 244-20-1422 | 226-44-1380 | 246-48-1332 | 346-26-1378 | · |

Files: `arena/results/20261106-194044-cfc-v6-vs-v5-seed2-fc4c` (tables.jsonl, seats.csv, summary.json, run.json).
