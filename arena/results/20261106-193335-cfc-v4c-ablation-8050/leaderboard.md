# Arena run `cfc-v4c-ablation` — fast mode

Started 2026-11-06T19:33:35 · seed `cfc4` · scheme ab · 3206 tables · 202902 hands · 60.4 s

Command: `ab bots/v0-nowar bots/cap-floor-count-v4c --field keep-made-plus-draw keep-made-plus-draw-v2 v0-baseline icm-pushfold cap-floor-count cap-floor-count-v2 --tables 1600 --seed cfc4 --agent Claude(cap-floor-count-agent) --name cfc-v4c-ablation --question ablation owed to headmaster: v3 + call margin 0.05 only (no bet-size-aware count) vs v0-nowar, same seed/field as v3/v4a/v4b runs`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cap-floor-count-v4c` replaces `v0-nowar` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1154 | 16.42 | 15.26 | -1.16 | ±0.87 | 0.009 | 284 / 516 / 354 | **v0-nowar is better** |

Pairs needed to resolve a 1-point difference at this variance: ~876.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **v0-nowar** | 1154 | 1832 | 16.45 | 0.82 | 3.73 | 52% | 14% | 0.0000 | 1 | 0 | 0 | 0.018 | 6.386 | 81.76 | 0 |
| 2 | **cap-floor-count-v4c** | 1154 | 1832 | 15.12 | 0.81 | 3.88 | 48% | 12% | 0.0000 | 4 | 0 | 0 | 0.019 | 20.448 | 156.59 | 0 |
| 3 | **keep-made-plus-draw-v2** | 2320 | 3664 | 13.01 | 0.60 | 4.49 | 38% | 14% | 0.0000 | 2 | 0 | 0 | 0.018 | 2.193 | 156.04 | 0 |
| 4 | **keep-made-plus-draw** | 2370 | 3664 | 12.51 | 0.59 | 4.51 | 36% | 14% | 0.0000 | 0 | 0 | 0 | 0.018 | 7.300 | 74.44 | 0 |
| 5 | **v0-baseline** | 2342 | 3664 | 12.45 | 0.59 | 4.59 | 36% | 14% | 0.0000 | 1 | 0 | 0 | 0.018 | 1.354 | 73.42 | 0 |
| 6 | **icm-pushfold** | 2350 | 3664 | 11.61 | 0.54 | 4.46 | 37% | 9% | 0.0002 | 46 | 0 | 0 | 0.029 | 20.942 | 92.55 | 0 |
| 7 | **cap-floor-count-v2** | 2346 | 3664 | 11.39 | 0.57 | 4.72 | 33% | 12% | 0.0000 | 2 | 0 | 0 | 0.017 | 18.465 | 127.21 | 0 |
| 8 | **cap-floor-count** | 2298 | 3664 | 10.75 | 0.56 | 4.77 | 32% | 11% | 0.0000 | 9 | 0 | 0 | 0.018 | 16.128 | 121.86 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| v0-nowar | 14% | 19% | 19% | 15% | 12% | 9% | 7% | 5% |
| cap-floor-count-v4c | 12% | 18% | 18% | 16% | 12% | 11% | 7% | 6% |
| keep-made-plus-draw-v2 | 14% | 11% | 13% | 12% | 12% | 12% | 13% | 13% |
| keep-made-plus-draw | 14% | 11% | 11% | 13% | 12% | 12% | 15% | 11% |
| v0-baseline | 14% | 11% | 11% | 11% | 12% | 14% | 15% | 12% |
| icm-pushfold | 9% | 16% | 13% | 13% | 14% | 14% | 13% | 9% |
| cap-floor-count-v2 | 12% | 10% | 11% | 11% | 13% | 14% | 15% | 13% |
| cap-floor-count | 11% | 10% | 11% | 12% | 13% | 15% | 16% | 13% |

## Head-to-head (row finished above column: wins-ties-losses)

| | v0-nowar | cap-floor-count-v4c | keep-made-plus-draw-v2 | keep-made-plus-draw | v0-baseline | icm-pushfold | cap-floor-count-v2 | cap-floor-count |
|---|---|---|---|---|---|---|---|---|
| **v0-nowar** | · | 0-0-0 | 463-0-330 | 498-0-327 | 466-0-348 | 507-1-307 | 500-1-312 | 506-0-296 |
| **cap-floor-count-v4c** | 0-0-0 | · | 447-2-344 | 466-2-357 | 454-0-360 | 477-1-337 | 476-4-333 | 491-0-311 |
| **keep-made-plus-draw-v2** | 330-0-463 | 344-2-447 | · | 819-12-821 | 827-6-807 | 879-3-790 | 909-4-757 | 853-2-757 |
| **keep-made-plus-draw** | 327-0-498 | 357-2-466 | 821-12-819 | · | 835-4-849 | 813-2-861 | 904-6-802 | 864-0-788 |
| **v0-baseline** | 348-0-466 | 360-0-454 | 807-6-827 | 849-4-835 | · | 810-4-838 | 859-8-815 | 845-5-770 |
| **icm-pushfold** | 307-1-507 | 337-1-477 | 790-3-879 | 861-2-813 | 838-4-810 | · | 859-6-777 | 859-2-769 |
| **cap-floor-count-v2** | 312-1-500 | 333-4-476 | 757-4-909 | 802-6-904 | 815-8-859 | 777-6-859 | · | 833-0-785 |
| **cap-floor-count** | 296-0-506 | 311-0-491 | 757-2-853 | 788-0-864 | 770-5-845 | 769-2-859 | 785-0-833 | · |

Files: `arena/results/20261106-193335-cfc-v4c-ablation-8050` (tables.jsonl, seats.csv, summary.json, run.json).
