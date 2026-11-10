# Arena run `cfc-v6-vs-bot` — fast mode

Started 2026-11-06T19:42:14 · seed `cfc8` · scheme ab · 3206 tables · 283657 hands · 60.4 s

Command: `ab bot bots/cap-floor-count-v6 --field keep-made-plus-draw keep-made-plus-draw-v2 v0-baseline icm-pushfold min_raiser check_or_fold --tables 1600 --seed cfc8 --agent Claude(cap-floor-count-agent) --question total gain of v6 (cap/floor/count postflop + no class-1 limps) vs the current submission bot --name cfc-v6-vs-bot`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cap-floor-count-v6` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1179 | 15.06 | 17.91 | +2.85 | ±1.09 | 0.000 | 397 / 530 / 252 | **cap-floor-count-v6 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~1404.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 2372 | 3664 | 22.16 | 0.32 | 2.67 | 86% | 0% | 0.0000 | 2 | 0 | 0 | 0.004 | 0.097 | 157.94 | 0 |
| 2 | **cap-floor-count-v6** | 1179 | 1832 | 17.49 | 0.91 | 3.58 | 49% | 20% | 0.0001 | 10 | 0 | 0 | 0.018 | 2.905 | 155.82 | 0 |
| 3 | **bot** | 1179 | 1832 | 14.69 | 0.88 | 3.85 | 42% | 17% | 0.0000 | 8 | 0 | 0 | 0.018 | 0.926 | 162.79 | 0 |
| 4 | **v0-baseline** | 2332 | 3664 | 12.77 | 0.64 | 4.42 | 33% | 19% | 0.0000 | 5 | 0 | 0 | 0.017 | 1.063 | 211.52 | 0 |
| 5 | **keep-made-plus-draw-v2** | 2362 | 3664 | 12.46 | 0.64 | 4.47 | 32% | 19% | 0.0001 | 17 | 0 | 0 | 0.017 | 1.212 | 168.93 | 0 |
| 6 | **keep-made-plus-draw** | 2364 | 3664 | 11.91 | 0.62 | 4.56 | 31% | 17% | 0.0001 | 16 | 0 | 0 | 0.018 | 1.214 | 203.19 | 0 |
| 7 | **icm-pushfold** | 2376 | 3664 | 10.25 | 0.56 | 4.63 | 30% | 12% | 0.0001 | 26 | 0 | 0 | 0.029 | 5.556 | 167.72 | 0 |
| 8 | **min_raiser** | 2340 | 3664 | 1.86 | 0.28 | 6.38 | 5% | 3% | 0.0000 | 1 | 0 | 0 | 0.004 | 0.099 | 124.34 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 49% | 37% | 12% | 2% | 0% | 0% | 0% |
| cap-floor-count-v6 | 20% | 17% | 12% | 17% | 15% | 11% | 6% | 2% |
| bot | 17% | 12% | 14% | 20% | 16% | 12% | 7% | 3% |
| v0-baseline | 19% | 6% | 9% | 13% | 16% | 17% | 14% | 6% |
| keep-made-plus-draw-v2 | 19% | 5% | 8% | 13% | 17% | 17% | 15% | 6% |
| keep-made-plus-draw | 17% | 5% | 9% | 13% | 16% | 17% | 14% | 8% |
| icm-pushfold | 12% | 8% | 10% | 14% | 17% | 18% | 15% | 7% |
| min_raiser | 3% | 1% | 2% | 5% | 10% | 24% | 33% | 23% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | cap-floor-count-v6 | bot | v0-baseline | keep-made-plus-draw-v2 | keep-made-plus-draw | icm-pushfold | min_raiser |
|---|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 437-0-411 | 562-0-286 | 1093-0-573 | 1129-0-589 | 1173-0-503 | 1272-0-438 | 1595-0-73 |
| **cap-floor-count-v6** | 411-0-437 | · | 0-0-0 | 492-0-337 | 521-0-327 | 529-1-311 | 573-1-265 | 781-8-44 |
| **bot** | 286-0-562 | 0-0-0 | · | 473-0-356 | 486-1-361 | 514-0-327 | 510-0-329 | 766-7-60 |
| **v0-baseline** | 573-0-1093 | 337-0-492 | 356-0-473 | · | 843-20-781 | 883-8-777 | 897-2-779 | 1380-32-260 |
| **keep-made-plus-draw-v2** | 589-0-1129 | 327-0-521 | 361-1-486 | 781-20-843 | · | 859-2-827 | 899-4-789 | 1369-51-258 |
| **keep-made-plus-draw** | 503-0-1173 | 311-1-529 | 327-0-514 | 777-8-883 | 827-2-859 | · | 887-8-815 | 1395-30-253 |
| **icm-pushfold** | 438-0-1272 | 265-1-573 | 329-0-510 | 779-2-897 | 789-4-899 | 815-8-887 | · | 1357-28-295 |
| **min_raiser** | 73-0-1595 | 44-8-781 | 60-7-766 | 260-32-1380 | 258-51-1369 | 253-30-1395 | 295-28-1357 | · |

Files: `arena/results/20261106-194214-cfc-v6-vs-bot-ce7b` (tables.jsonl, seats.csv, summary.json, run.json).
