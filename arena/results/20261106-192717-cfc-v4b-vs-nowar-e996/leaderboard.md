# Arena run `cfc-v4b-vs-nowar` — fast mode

Started 2026-11-06T19:27:17 · seed `cfc4` · scheme ab · 3206 tables · 211429 hands · 44.3 s

Command: `ab bots/v0-nowar bots/cap-floor-count-v4b --field keep-made-plus-draw keep-made-plus-draw-v2 v0-baseline icm-pushfold cap-floor-count cap-floor-count-v2 --tables 1600 --seed cfc4 --agent Claude(cap-floor-count-agent) --name cfc-v4b-vs-nowar --question v4b (v4a + strict one-pair value gate) vs v0-nowar, same field+seed`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cap-floor-count-v4b` replaces `v0-nowar` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1154 | 16.41 | 18.34 | +1.93 | ±0.89 | 0.000 | 389 / 480 / 285 | **cap-floor-count-v4b is better** |

Pairs needed to resolve a 1-point difference at this variance: ~919.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **cap-floor-count-v4b** | 1154 | 1832 | 17.67 | 0.83 | 3.59 | 55% | 15% | 0.0000 | 0 | 0 | 0 | 0.018 | 1.619 | 15.76 | 0 |
| 2 | **v0-nowar** | 1154 | 1832 | 16.43 | 0.82 | 3.73 | 52% | 14% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.384 | 35.46 | 0 |
| 3 | **keep-made-plus-draw-v2** | 2320 | 3664 | 12.81 | 0.60 | 4.51 | 37% | 14% | 0.0000 | 0 | 0 | 0 | 0.017 | 1.040 | 27.18 | 0 |
| 4 | **v0-baseline** | 2342 | 3664 | 12.37 | 0.59 | 4.60 | 36% | 14% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.489 | 41.01 | 0 |
| 5 | **keep-made-plus-draw** | 2370 | 3664 | 12.09 | 0.59 | 4.55 | 35% | 13% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.646 | 16.84 | 0 |
| 6 | **icm-pushfold** | 2350 | 3664 | 11.38 | 0.53 | 4.49 | 36% | 8% | 0.0000 | 0 | 0 | 0 | 0.028 | 2.366 | 29.27 | 0 |
| 7 | **cap-floor-count-v2** | 2346 | 3664 | 11.18 | 0.57 | 4.74 | 33% | 12% | 0.0000 | 0 | 0 | 0 | 0.016 | 2.022 | 34.45 | 0 |
| 8 | **cap-floor-count** | 2298 | 3664 | 10.61 | 0.56 | 4.79 | 31% | 11% | 0.0000 | 0 | 0 | 0 | 0.017 | 2.165 | 27.01 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| cap-floor-count-v4b | 15% | 21% | 19% | 15% | 11% | 9% | 6% | 5% |
| v0-nowar | 14% | 19% | 19% | 15% | 12% | 9% | 7% | 5% |
| keep-made-plus-draw-v2 | 14% | 10% | 12% | 13% | 12% | 12% | 13% | 13% |
| v0-baseline | 14% | 11% | 11% | 11% | 12% | 14% | 15% | 12% |
| keep-made-plus-draw | 13% | 11% | 11% | 14% | 12% | 13% | 15% | 12% |
| icm-pushfold | 8% | 16% | 12% | 13% | 14% | 15% | 13% | 9% |
| cap-floor-count-v2 | 12% | 10% | 11% | 11% | 14% | 14% | 15% | 13% |
| cap-floor-count | 11% | 10% | 10% | 12% | 13% | 15% | 16% | 13% |

## Head-to-head (row finished above column: wins-ties-losses)

| | cap-floor-count-v4b | v0-nowar | keep-made-plus-draw-v2 | v0-baseline | keep-made-plus-draw | icm-pushfold | cap-floor-count-v2 | cap-floor-count |
|---|---|---|---|---|---|---|---|---|
| **cap-floor-count-v4b** | · | 0-0-0 | 491-1-301 | 504-0-310 | 517-2-306 | 521-1-293 | 520-3-290 | 527-0-275 |
| **v0-nowar** | 0-0-0 | · | 463-0-330 | 466-0-348 | 498-0-327 | 507-1-307 | 500-1-312 | 505-0-297 |
| **keep-made-plus-draw-v2** | 301-1-491 | 330-0-463 | · | 829-6-805 | 824-12-816 | 869-3-800 | 910-4-756 | 848-2-762 |
| **v0-baseline** | 310-0-504 | 348-0-466 | 805-6-829 | · | 863-4-821 | 818-4-830 | 868-8-806 | 842-5-773 |
| **keep-made-plus-draw** | 306-2-517 | 327-0-498 | 816-12-824 | 821-4-863 | · | 815-2-859 | 892-6-814 | 862-0-790 |
| **icm-pushfold** | 293-1-521 | 307-1-507 | 800-3-869 | 830-4-818 | 859-2-815 | · | 860-6-776 | 861-2-767 |
| **cap-floor-count-v2** | 290-3-520 | 312-1-500 | 756-4-910 | 806-8-868 | 814-6-892 | 776-6-860 | · | 832-0-786 |
| **cap-floor-count** | 275-0-527 | 297-0-505 | 762-2-848 | 773-5-842 | 790-0-862 | 767-2-861 | 786-0-832 | · |

Files: `arena/results/20261106-192717-cfc-v4b-vs-nowar-e996` (tables.jsonl, seats.csv, summary.json, run.json).
