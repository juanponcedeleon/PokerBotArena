# Arena run `cfc-v7-steal-vs-v6` — fast mode

Started 2026-11-06T20:01:41 · seed `cfc9` · scheme ab · 3206 tables · 316145 hands · 154.8 s

Command: `ab bots/cap-floor-count-v6 bots/cfc-v7-steal --field keep-made-plus-draw-v2 v0-baseline icm-pushfold cap-floor-count-v5 min_raiser check_or_fold --tables 1600 --seed cfc9 --agent Claude(cap-floor-count-agent) --log --name cfc-v7-steal-vs-v6 --question memory exploits (05 S5.4): steal from tight folders + probe never-bettors vs v6`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cfc-v7-steal` replaces `cap-floor-count-v6` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1175 | 17.18 | 17.14 | -0.03 | ±0.17 | 0.717 | 21 / 1129 / 25 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~36.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 2366 | 3664 | 19.70 | 0.35 | 2.86 | 80% | 0% | 0.0000 | 3 | 0 | 0 | 0.005 | 0.265 | 192.53 | 0 |
| 2 | **cap-floor-count-v6** | 1175 | 1832 | 16.75 | 0.90 | 3.69 | 48% | 19% | 0.0001 | 15 | 0 | 0 | 0.021 | 15.432 | 166.97 | 0 |
| 3 | **cfc-v7-steal** | 1175 | 1832 | 16.75 | 0.90 | 3.69 | 48% | 19% | 0.0003 | 49 | 0 | 0 | 0.060 | 17.604 | 253.25 | 100 |
| 4 | **cap-floor-count-v5** | 2338 | 3664 | 16.04 | 0.66 | 3.85 | 43% | 21% | 0.0001 | 40 | 0 | 0 | 0.022 | 15.138 | 199.75 | 0 |
| 5 | **keep-made-plus-draw-v2** | 2356 | 3664 | 11.99 | 0.63 | 4.66 | 30% | 18% | 0.0000 | 15 | 0 | 0 | 0.021 | 13.972 | 438.85 | 0 |
| 6 | **v0-baseline** | 2390 | 3664 | 11.64 | 0.62 | 4.63 | 30% | 16% | 0.0001 | 16 | 0 | 0 | 0.020 | 12.975 | 234.33 | 0 |
| 7 | **icm-pushfold** | 2358 | 3664 | 9.92 | 0.56 | 4.76 | 28% | 12% | 0.0003 | 72 | 0 | 0 | 0.034 | 17.294 | 446.91 | 0 |
| 8 | **min_raiser** | 2388 | 3664 | 1.45 | 0.25 | 6.57 | 4% | 2% | 0.0000 | 2 | 0 | 0 | 0.005 | 6.565 | 167.61 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 38% | 42% | 17% | 3% | 0% | 0% | 0% |
| cap-floor-count-v6 | 19% | 16% | 13% | 15% | 15% | 13% | 7% | 2% |
| cfc-v7-steal | 19% | 16% | 13% | 15% | 15% | 13% | 7% | 2% |
| cap-floor-count-v5 | 21% | 13% | 10% | 15% | 17% | 13% | 9% | 3% |
| keep-made-plus-draw-v2 | 18% | 6% | 7% | 11% | 15% | 18% | 17% | 9% |
| v0-baseline | 16% | 7% | 7% | 13% | 15% | 16% | 18% | 8% |
| icm-pushfold | 12% | 8% | 8% | 13% | 16% | 18% | 17% | 8% |
| min_raiser | 2% | 1% | 1% | 4% | 9% | 20% | 35% | 28% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | cap-floor-count-v6 | cfc-v7-steal | cap-floor-count-v5 | keep-made-plus-draw-v2 | v0-baseline | icm-pushfold | min_raiser |
|---|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 444-0-392 | 444-0-392 | 945-0-729 | 1112-0-604 | 1151-0-565 | 1203-0-467 | 1644-0-64 |
| **cap-floor-count-v6** | 392-0-444 | · | 0-0-0 | 407-0-417 | 479-1-344 | 527-1-327 | 549-0-287 | 821-4-33 |
| **cfc-v7-steal** | 392-0-444 | 0-0-0 | · | 405-0-419 | 479-1-344 | 527-1-327 | 551-0-285 | 822-4-32 |
| **cap-floor-count-v5** | 729-0-945 | 417-0-407 | 419-0-405 | · | 1015-2-649 | 1000-2-686 | 1023-0-633 | 1581-0-103 |
| **keep-made-plus-draw-v2** | 604-0-1112 | 344-1-479 | 344-1-479 | 649-2-1015 | · | 819-16-843 | 929-2-767 | 1390-32-252 |
| **v0-baseline** | 565-0-1151 | 327-1-527 | 327-1-527 | 686-2-1000 | 843-16-819 | · | 897-4-821 | 1402-26-328 |
| **icm-pushfold** | 467-0-1203 | 287-0-549 | 285-0-551 | 633-0-1023 | 767-2-929 | 821-4-897 | · | 1355-22-309 |
| **min_raiser** | 64-0-1644 | 33-4-821 | 32-4-822 | 103-0-1581 | 252-32-1390 | 328-26-1402 | 309-22-1355 | · |

Files: `arena/results/20261106-200141-cfc-v7-steal-vs-v6-b662` (tables.jsonl, seats.csv, summary.json, run.json).
