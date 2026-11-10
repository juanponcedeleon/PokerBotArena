# Arena run `cfc-v7-expose-vs-v6` — fast mode

Started 2026-11-06T20:00:40 · seed `cfc9` · scheme ab · 3206 tables · 316731 hands · 53.9 s

Command: `ab bots/cap-floor-count-v6 bots/cfc-v7-expose --field keep-made-plus-draw-v2 v0-baseline icm-pushfold cap-floor-count-v5 min_raiser check_or_fold --tables 1600 --seed cfc9 --agent Claude(cap-floor-count-agent) --name cfc-v7-expose-vs-v6 --question exposure rule A/B (03 S3.2): hide-strength/show-high vs v6 show-low, field includes a reader (v5)`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cfc-v7-expose` replaces `cap-floor-count-v6` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1175 | 17.20 | 17.31 | +0.10 | ±0.48 | 0.676 | 120 / 942 / 113 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~271.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 2366 | 3664 | 19.92 | 0.35 | 2.85 | 80% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.065 | 62.52 | 0 |
| 2 | **cfc-v7-expose** | 1175 | 1832 | 16.97 | 0.91 | 3.68 | 48% | 20% | 0.0000 | 0 | 0 | 0 | 0.018 | 1.516 | 99.14 | 0 |
| 3 | **cap-floor-count-v6** | 1175 | 1832 | 16.75 | 0.90 | 3.69 | 48% | 19% | 0.0000 | 2 | 0 | 0 | 0.017 | 1.103 | 119.06 | 0 |
| 4 | **cap-floor-count-v5** | 2338 | 3664 | 15.81 | 0.65 | 3.87 | 43% | 20% | 0.0000 | 2 | 0 | 0 | 0.017 | 1.460 | 117.57 | 0 |
| 5 | **keep-made-plus-draw-v2** | 2356 | 3664 | 12.07 | 0.63 | 4.65 | 30% | 18% | 0.0000 | 1 | 0 | 0 | 0.017 | 0.852 | 93.15 | 0 |
| 6 | **v0-baseline** | 2390 | 3664 | 11.61 | 0.62 | 4.63 | 30% | 16% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.397 | 100.73 | 0 |
| 7 | **icm-pushfold** | 2358 | 3664 | 9.80 | 0.56 | 4.78 | 28% | 12% | 0.0000 | 0 | 0 | 0 | 0.028 | 1.869 | 101.03 | 0 |
| 8 | **min_raiser** | 2388 | 3664 | 1.44 | 0.25 | 6.57 | 4% | 2% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.109 | 84.19 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 39% | 41% | 17% | 3% | 0% | 0% | 0% |
| cfc-v7-expose | 20% | 16% | 12% | 16% | 15% | 12% | 7% | 2% |
| cap-floor-count-v6 | 19% | 16% | 13% | 15% | 15% | 13% | 7% | 2% |
| cap-floor-count-v5 | 20% | 13% | 10% | 15% | 17% | 13% | 9% | 3% |
| keep-made-plus-draw-v2 | 18% | 6% | 7% | 11% | 15% | 18% | 17% | 9% |
| v0-baseline | 16% | 6% | 7% | 13% | 15% | 16% | 18% | 8% |
| icm-pushfold | 12% | 7% | 9% | 13% | 16% | 18% | 17% | 8% |
| min_raiser | 2% | 1% | 1% | 4% | 9% | 20% | 35% | 28% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | cfc-v7-expose | cap-floor-count-v6 | cap-floor-count-v5 | keep-made-plus-draw-v2 | v0-baseline | icm-pushfold | min_raiser |
|---|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 438-0-398 | 445-0-391 | 955-0-719 | 1115-0-601 | 1155-0-561 | 1217-0-453 | 1644-0-64 |
| **cfc-v7-expose** | 398-0-438 | · | 0-0-0 | 422-0-402 | 476-1-347 | 521-1-333 | 563-0-273 | 823-4-31 |
| **cap-floor-count-v6** | 391-0-445 | 0-0-0 | · | 407-0-417 | 479-1-344 | 530-1-324 | 550-0-286 | 822-4-32 |
| **cap-floor-count-v5** | 719-0-955 | 402-0-422 | 417-0-407 | · | 1010-1-655 | 1006-2-680 | 1028-0-628 | 1582-0-102 |
| **keep-made-plus-draw-v2** | 601-0-1115 | 347-1-476 | 344-1-479 | 655-1-1010 | · | 817-16-845 | 933-2-763 | 1390-32-252 |
| **v0-baseline** | 561-0-1155 | 333-1-521 | 324-1-530 | 680-2-1006 | 845-16-817 | · | 905-4-813 | 1402-26-328 |
| **icm-pushfold** | 453-0-1217 | 273-0-563 | 286-0-550 | 628-0-1028 | 763-2-933 | 813-4-905 | · | 1354-22-310 |
| **min_raiser** | 64-0-1644 | 31-4-823 | 32-4-822 | 102-0-1582 | 252-32-1390 | 328-26-1402 | 310-22-1354 | · |

Files: `arena/results/20261106-200040-cfc-v7-expose-vs-v6-ff33` (tables.jsonl, seats.csv, summary.json, run.json).
