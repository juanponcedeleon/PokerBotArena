# Arena run `cfc-v4a-vs-nowar` — fast mode

Started 2026-11-06T19:26:20 · seed `cfc4` · scheme ab · 3206 tables · 209184 hands · 50.4 s

Command: `ab bots/v0-nowar bots/cap-floor-count-v4a --field keep-made-plus-draw keep-made-plus-draw-v2 v0-baseline icm-pushfold cap-floor-count cap-floor-count-v2 --tables 1600 --seed cfc4 --agent Claude(cap-floor-count-agent) --name cfc-v4a-vs-nowar --question v4a (bet-size/persistence-aware count, margin 0.05) vs v0-nowar, same field+seed as cfc-v3-vs-nowar-big`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cap-floor-count-v4a` replaces `v0-nowar` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1154 | 16.41 | 17.69 | +1.29 | ±0.89 | 0.004 | 365 / 494 / 295 | **cap-floor-count-v4a is better** |

Pairs needed to resolve a 1-point difference at this variance: ~908.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **cap-floor-count-v4a** | 1154 | 1832 | 17.21 | 0.83 | 3.66 | 54% | 15% | 0.0000 | 5 | 0 | 0 | 0.019 | 11.172 | 70.41 | 0 |
| 2 | **v0-nowar** | 1154 | 1832 | 16.43 | 0.82 | 3.73 | 52% | 14% | 0.0000 | 2 | 0 | 0 | 0.018 | 4.646 | 85.72 | 0 |
| 3 | **keep-made-plus-draw-v2** | 2320 | 3664 | 12.78 | 0.60 | 4.51 | 37% | 14% | 0.0000 | 1 | 0 | 0 | 0.017 | 9.781 | 80.28 | 0 |
| 4 | **v0-baseline** | 2342 | 3664 | 12.37 | 0.59 | 4.60 | 36% | 14% | 0.0000 | 1 | 0 | 0 | 0.017 | 1.959 | 106.99 | 0 |
| 5 | **keep-made-plus-draw** | 2370 | 3664 | 12.33 | 0.59 | 4.53 | 36% | 14% | 0.0000 | 0 | 0 | 0 | 0.018 | 2.250 | 61.10 | 0 |
| 6 | **icm-pushfold** | 2350 | 3664 | 11.44 | 0.53 | 4.48 | 37% | 8% | 0.0001 | 17 | 0 | 0 | 0.029 | 12.208 | 103.55 | 0 |
| 7 | **cap-floor-count-v2** | 2346 | 3664 | 11.17 | 0.57 | 4.74 | 33% | 12% | 0.0000 | 5 | 0 | 0 | 0.017 | 9.367 | 46.94 | 0 |
| 8 | **cap-floor-count** | 2298 | 3664 | 10.59 | 0.56 | 4.78 | 31% | 11% | 0.0000 | 7 | 0 | 0 | 0.018 | 9.481 | 145.35 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| cap-floor-count-v4a | 15% | 20% | 19% | 14% | 11% | 9% | 6% | 5% |
| v0-nowar | 14% | 19% | 19% | 15% | 12% | 9% | 7% | 5% |
| keep-made-plus-draw-v2 | 14% | 11% | 12% | 13% | 12% | 12% | 13% | 13% |
| v0-baseline | 14% | 11% | 11% | 11% | 12% | 14% | 15% | 12% |
| keep-made-plus-draw | 14% | 11% | 11% | 13% | 12% | 12% | 15% | 12% |
| icm-pushfold | 8% | 15% | 13% | 13% | 14% | 15% | 13% | 9% |
| cap-floor-count-v2 | 12% | 10% | 11% | 11% | 14% | 14% | 15% | 13% |
| cap-floor-count | 11% | 10% | 10% | 12% | 13% | 15% | 16% | 13% |

## Head-to-head (row finished above column: wins-ties-losses)

| | cap-floor-count-v4a | v0-nowar | keep-made-plus-draw-v2 | v0-baseline | keep-made-plus-draw | icm-pushfold | cap-floor-count-v2 | cap-floor-count |
|---|---|---|---|---|---|---|---|---|
| **cap-floor-count-v4a** | · | 0-0-0 | 485-1-307 | 494-0-320 | 492-2-331 | 514-1-300 | 514-3-296 | 526-0-276 |
| **v0-nowar** | 0-0-0 | · | 463-0-330 | 466-0-348 | 498-0-327 | 507-1-307 | 500-1-312 | 505-0-297 |
| **keep-made-plus-draw-v2** | 307-1-485 | 330-0-463 | · | 828-6-806 | 823-12-817 | 874-3-795 | 913-4-753 | 847-2-763 |
| **v0-baseline** | 320-0-494 | 348-0-466 | 806-6-828 | · | 850-4-834 | 817-4-831 | 872-8-802 | 845-5-770 |
| **keep-made-plus-draw** | 331-2-492 | 327-0-498 | 817-12-823 | 834-4-850 | · | 816-2-858 | 894-6-812 | 863-0-789 |
| **icm-pushfold** | 300-1-514 | 307-1-507 | 795-3-874 | 831-4-817 | 858-2-816 | · | 865-6-771 | 858-2-770 |
| **cap-floor-count-v2** | 296-3-514 | 312-1-500 | 753-4-913 | 802-8-872 | 812-6-894 | 771-6-865 | · | 835-0-783 |
| **cap-floor-count** | 276-0-526 | 297-0-505 | 763-2-847 | 770-5-845 | 789-0-863 | 770-2-858 | 783-0-835 | · |

Files: `arena/results/20261106-192620-cfc-v4a-vs-nowar-a33b` (tables.jsonl, seats.csv, summary.json, run.json).
