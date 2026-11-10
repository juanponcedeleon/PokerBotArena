# Arena run `ab-keep-made-plus-draw-v2-vs-keep-made-plus-draw` — fast mode

Started 2026-11-06T19:22:31 · seed `s31e` · scheme ab · 2002 tables · 143626 hands · 45.0 s

Command: `ab keep-made-plus-draw keep-made-plus-draw-v2 --all --tables 1000 --seed s31e --agent Claude (keep-rule agent) --question v2 vs v1 in the mixed pool field (--all: every bots/ entry), robustness check after a noisy league --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `keep-made-plus-draw-v2` replaces `keep-made-plus-draw` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 742 | 11.89 | 11.78 | -0.11 | ±0.38 | 0.550 | 19 / 700 / 23 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~105.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **v0-nowar** | 1460 | 2288 | 15.62 | 0.75 | 3.83 | 48% | 14% | 0.0000 | 0 | 0 | 0 | 0.022 | 9.307 | 43.97 | 0 |
| 2 | **cap-floor-count-v3** | 1472 | 2288 | 14.09 | 0.72 | 4.04 | 45% | 11% | 0.0000 | 0 | 0 | 0 | 0.022 | 12.792 | 35.96 | 0 |
| 3 | **icm-pushfold** | 1466 | 2288 | 12.57 | 0.72 | 4.50 | 39% | 11% | 0.0000 | 4 | 0 | 0 | 0.036 | 14.151 | 65.77 | 0 |
| 4 | **keep-made-plus-draw** | 742 | 1144 | 12.12 | 1.07 | 4.64 | 34% | 14% | 0.0000 | 2 | 0 | 0 | 0.022 | 10.436 | 45.99 | 0 |
| 5 | **v0-baseline** | 1464 | 2288 | 12.12 | 0.75 | 4.69 | 34% | 14% | 0.0000 | 0 | 0 | 0 | 0.022 | 5.368 | 32.25 | 0 |
| 6 | **keep-made-plus-draw-v2** | 742 | 1144 | 12.06 | 1.07 | 4.63 | 34% | 14% | 0.0000 | 0 | 0 | 0 | 0.022 | 8.887 | 28.23 | 0 |
| 7 | **cap-floor-count-v2** | 1482 | 2288 | 11.34 | 0.73 | 4.73 | 33% | 13% | 0.0000 | 0 | 0 | 0 | 0.021 | 12.809 | 34.12 | 0 |
| 8 | **cap-floor-count** | 1450 | 2288 | 9.66 | 0.68 | 4.95 | 29% | 10% | 0.0000 | 0 | 0 | 0 | 0.022 | 11.947 | 31.27 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| v0-nowar | 14% | 18% | 17% | 16% | 12% | 11% | 7% | 5% |
| cap-floor-count-v3 | 11% | 18% | 16% | 16% | 13% | 9% | 10% | 7% |
| icm-pushfold | 11% | 15% | 13% | 12% | 12% | 13% | 11% | 14% |
| keep-made-plus-draw | 14% | 10% | 10% | 11% | 13% | 14% | 15% | 13% |
| v0-baseline | 14% | 10% | 11% | 10% | 13% | 12% | 15% | 15% |
| keep-made-plus-draw-v2 | 14% | 10% | 9% | 11% | 13% | 14% | 15% | 12% |
| cap-floor-count-v2 | 13% | 9% | 11% | 11% | 12% | 15% | 15% | 13% |
| cap-floor-count | 10% | 9% | 10% | 11% | 13% | 16% | 18% | 14% |

## Head-to-head (row finished above column: wins-ties-losses)

| | v0-nowar | cap-floor-count-v3 | icm-pushfold | keep-made-plus-draw | v0-baseline | keep-made-plus-draw-v2 | cap-floor-count-v2 | cap-floor-count |
|---|---|---|---|---|---|---|---|---|
| **v0-nowar** | · | 547-0-491 | 565-2-469 | 321-0-203 | 632-0-418 | 318-0-206 | 641-0-403 | 645-0-353 |
| **cap-floor-count-v3** | 491-0-547 | · | 556-0-472 | 287-1-240 | 575-2-473 | 288-1-239 | 623-2-431 | 636-4-380 |
| **icm-pushfold** | 469-2-565 | 472-0-556 | · | 278-2-247 | 503-0-515 | 279-1-247 | 546-6-512 | 605-4-431 |
| **keep-made-plus-draw** | 203-0-321 | 240-1-287 | 247-2-278 | · | 258-0-263 | 0-0-0 | 268-1-259 | 281-1-237 |
| **v0-baseline** | 418-0-632 | 473-2-575 | 515-0-503 | 263-0-258 | · | 264-0-257 | 537-0-521 | 567-2-461 |
| **keep-made-plus-draw-v2** | 206-0-318 | 239-1-288 | 247-1-279 | 0-0-0 | 257-0-264 | · | 266-1-261 | 276-1-242 |
| **cap-floor-count-v2** | 403-0-641 | 431-2-623 | 512-6-546 | 259-1-268 | 521-0-537 | 261-1-266 | · | 514-8-490 |
| **cap-floor-count** | 353-0-645 | 380-4-636 | 431-4-605 | 237-1-281 | 461-2-567 | 242-1-276 | 490-8-514 | · |

Files: `arena/results/20261106-192231-ab-keep-made-plus-draw-v2-vs-keep-made-plus-draw-52b2` (tables.jsonl, seats.csv, summary.json, run.json).
