# Arena run `cfc-v8-position-vs-v6` — fast mode

Started 2026-11-06T20:29:34 · seed `cfc11` · scheme ab · 3206 tables · 309536 hands · 148.0 s

Command: `ab bots/cap-floor-count-v6 bots/cfc-v8-position --field keep-made-plus-draw-v2 v0-baseline icm-pushfold cap-floor-count-v5 min_raiser check_or_fold --tables 1600 --seed cfc11 --log --agent Claude(cap-floor-count-agent) --name cfc-v8-position-vs-v6 --question position-aware opening (class 1 opens from the last 2 seats when folded to) vs v6`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cfc-v8-position` replaces `cap-floor-count-v6` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1199 | 17.15 | 17.38 | +0.23 | ±0.51 | 0.373 | 126 / 957 / 116 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~311.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 2360 | 3664 | 20.13 | 0.35 | 2.83 | 81% | 0% | 0.0000 | 9 | 0 | 0 | 0.004 | 0.108 | 260.78 | 0 |
| 2 | **cfc-v8-position** | 1199 | 1832 | 16.92 | 0.92 | 3.73 | 47% | 20% | 0.0003 | 52 | 0 | 0 | 0.020 | 18.982 | 289.50 | 0 |
| 3 | **cap-floor-count-v6** | 1199 | 1832 | 16.86 | 0.91 | 3.72 | 47% | 19% | 0.0003 | 48 | 0 | 0 | 0.019 | 19.686 | 312.35 | 0 |
| 4 | **cap-floor-count-v5** | 2342 | 3664 | 14.99 | 0.64 | 3.96 | 41% | 19% | 0.0003 | 141 | 0 | 0 | 0.019 | 19.320 | 340.14 | 0 |
| 5 | **keep-made-plus-draw-v2** | 2356 | 3664 | 12.42 | 0.63 | 4.55 | 32% | 18% | 0.0001 | 38 | 0 | 0 | 0.019 | 17.226 | 347.40 | 0 |
| 6 | **v0-baseline** | 2326 | 3664 | 11.97 | 0.63 | 4.62 | 30% | 18% | 0.0001 | 21 | 0 | 0 | 0.018 | 12.109 | 260.52 | 0 |
| 7 | **icm-pushfold** | 2326 | 3664 | 9.85 | 0.56 | 4.73 | 28% | 12% | 0.0008 | 222 | 0 | 0 | 0.031 | 22.093 | 314.55 | 0 |
| 8 | **min_raiser** | 2328 | 3664 | 1.25 | 0.23 | 6.57 | 4% | 2% | 0.0000 | 2 | 0 | 0 | 0.004 | 0.263 | 272.25 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 39% | 42% | 16% | 3% | 0% | 0% | 0% |
| cfc-v8-position | 20% | 15% | 12% | 15% | 15% | 12% | 8% | 3% |
| cap-floor-count-v6 | 19% | 16% | 11% | 15% | 15% | 12% | 8% | 3% |
| cap-floor-count-v5 | 19% | 11% | 11% | 15% | 17% | 14% | 9% | 3% |
| keep-made-plus-draw-v2 | 18% | 6% | 8% | 11% | 16% | 17% | 17% | 8% |
| v0-baseline | 18% | 6% | 6% | 12% | 16% | 18% | 15% | 9% |
| icm-pushfold | 12% | 8% | 8% | 14% | 16% | 18% | 16% | 8% |
| min_raiser | 2% | 0% | 2% | 4% | 8% | 23% | 34% | 27% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | cfc-v8-position | cap-floor-count-v6 | cap-floor-count-v5 | keep-made-plus-draw-v2 | v0-baseline | icm-pushfold | min_raiser |
|---|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 464-0-397 | 460-0-401 | 965-0-723 | 1093-0-587 | 1083-0-581 | 1202-0-448 | 1615-0-55 |
| **cfc-v8-position** | 397-0-464 | · | 0-0-0 | 465-0-374 | 502-1-351 | 498-1-339 | 542-0-304 | 815-2-39 |
| **cap-floor-count-v6** | 401-0-460 | 0-0-0 | · | 450-0-389 | 500-1-353 | 493-1-344 | 535-0-311 | 818-2-36 |
| **cap-floor-count-v5** | 723-0-965 | 374-0-465 | 389-0-450 | · | 1008-0-670 | 968-6-670 | 1015-0-635 | 1553-6-73 |
| **keep-made-plus-draw-v2** | 587-0-1093 | 351-1-502 | 353-1-500 | 670-0-1008 | · | 824-10-814 | 847-10-775 | 1337-24-293 |
| **v0-baseline** | 581-0-1083 | 339-1-498 | 344-1-493 | 670-6-968 | 814-10-824 | · | 884-0-724 | 1324-32-272 |
| **icm-pushfold** | 448-0-1202 | 304-0-542 | 311-0-535 | 635-0-1015 | 775-10-847 | 724-0-884 | · | 1391-12-249 |
| **min_raiser** | 55-0-1615 | 39-2-815 | 36-2-818 | 73-6-1553 | 293-24-1337 | 272-32-1324 | 249-12-1391 | · |

Files: `arena/results/20261106-202934-cfc-v8-position-vs-v6-3b84` (tables.jsonl, seats.csv, summary.json, run.json).
