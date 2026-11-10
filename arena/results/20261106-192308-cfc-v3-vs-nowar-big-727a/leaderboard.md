# Arena run `cfc-v3-vs-nowar-big` — fast mode

Started 2026-11-06T19:23:08 · seed `cfc4` · scheme ab · 3206 tables · 205443 hands · 75.6 s

Command: `ab bots/v0-nowar bots/cap-floor-count-v3 --all --tables 1600 --seed cfc4 --log --agent Claude(cap-floor-count-agent) --name cfc-v3-vs-nowar-big --question postflop module isolated at 1600 pairs with hand log: where does v3 leak vs v0-nowar?`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cap-floor-count-v3` replaces `v0-nowar` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1154 | 16.46 | 15.90 | -0.56 | ±0.92 | 0.233 | 300 / 517 / 337 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~976.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **v0-nowar** | 1154 | 1832 | 16.03 | 0.81 | 3.74 | 51% | 12% | 0.0000 | 0 | 0 | 0 | 0.022 | 1.190 | 72.94 | 0 |
| 2 | **cap-floor-count-v3** | 1154 | 1832 | 15.68 | 0.82 | 3.83 | 49% | 13% | 0.0000 | 7 | 0 | 0 | 0.022 | 3.431 | 195.61 | 0 |
| 3 | **keep-made-plus-draw-v2** | 2298 | 3664 | 12.92 | 0.60 | 4.48 | 37% | 15% | 0.0000 | 3 | 0 | 0 | 0.022 | 2.148 | 148.02 | 0 |
| 4 | **v0-baseline** | 2346 | 3664 | 12.52 | 0.59 | 4.57 | 37% | 14% | 0.0000 | 1 | 0 | 0 | 0.021 | 1.197 | 141.60 | 0 |
| 5 | **keep-made-plus-draw** | 2350 | 3664 | 12.39 | 0.59 | 4.55 | 36% | 14% | 0.0000 | 3 | 0 | 0 | 0.022 | 1.439 | 147.79 | 0 |
| 6 | **cap-floor-count-v2** | 2320 | 3664 | 11.87 | 0.59 | 4.66 | 34% | 14% | 0.0000 | 10 | 0 | 0 | 0.021 | 3.405 | 185.28 | 0 |
| 7 | **icm-pushfold** | 2342 | 3664 | 11.39 | 0.54 | 4.52 | 37% | 9% | 0.0000 | 10 | 0 | 0 | 0.036 | 4.312 | 156.49 | 0 |
| 8 | **cap-floor-count** | 2370 | 3664 | 10.55 | 0.55 | 4.75 | 32% | 10% | 0.0000 | 2 | 0 | 0 | 0.021 | 3.364 | 166.76 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| v0-nowar | 12% | 22% | 17% | 16% | 11% | 9% | 7% | 5% |
| cap-floor-count-v3 | 13% | 19% | 17% | 15% | 12% | 11% | 8% | 5% |
| keep-made-plus-draw-v2 | 15% | 11% | 12% | 12% | 13% | 13% | 13% | 12% |
| v0-baseline | 14% | 11% | 12% | 12% | 12% | 12% | 15% | 13% |
| keep-made-plus-draw | 14% | 11% | 11% | 12% | 13% | 14% | 15% | 11% |
| cap-floor-count-v2 | 14% | 10% | 11% | 11% | 13% | 14% | 15% | 13% |
| icm-pushfold | 9% | 14% | 13% | 14% | 13% | 13% | 13% | 10% |
| cap-floor-count | 10% | 10% | 11% | 12% | 13% | 14% | 16% | 12% |

## Head-to-head (row finished above column: wins-ties-losses)

| | v0-nowar | cap-floor-count-v3 | keep-made-plus-draw-v2 | v0-baseline | keep-made-plus-draw | cap-floor-count-v2 | icm-pushfold | cap-floor-count |
|---|---|---|---|---|---|---|---|---|
| **v0-nowar** | · | 0-0-0 | 441-1-360 | 485-0-328 | 475-1-339 | 490-1-302 | 488-0-326 | 527-0-298 |
| **cap-floor-count-v3** | 0-0-0 | · | 441-0-361 | 464-5-344 | 459-1-355 | 459-1-333 | 487-0-327 | 531-2-292 |
| **keep-made-plus-draw-v2** | 360-1-441 | 361-0-441 | · | 847-2-769 | 835-0-795 | 843-6-763 | 862-4-754 | 903-2-747 |
| **v0-baseline** | 328-0-485 | 344-5-464 | 769-2-847 | · | 805-6-831 | 836-4-830 | 893-2-787 | 904-8-800 |
| **keep-made-plus-draw** | 339-1-475 | 355-1-459 | 795-0-835 | 831-6-805 | · | 828-10-834 | 841-8-803 | 931-8-737 |
| **cap-floor-count-v2** | 302-1-490 | 333-1-459 | 763-6-843 | 830-4-836 | 834-10-828 | · | 803-5-832 | 868-20-764 |
| **icm-pushfold** | 326-0-488 | 327-0-487 | 754-4-862 | 787-2-893 | 803-8-841 | 832-5-803 | · | 898-4-786 |
| **cap-floor-count** | 298-0-527 | 292-2-531 | 747-2-903 | 800-8-904 | 737-8-931 | 764-20-868 | 786-4-898 | · |

Files: `arena/results/20261106-192308-cfc-v3-vs-nowar-big-727a` (tables.jsonl, seats.csv, summary.json, run.json).
