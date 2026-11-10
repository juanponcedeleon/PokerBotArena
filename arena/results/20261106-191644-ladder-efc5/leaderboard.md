# Arena run `ladder` — fast mode

Started 2026-11-06T19:16:44 · seed `98816119` · scheme league · 200 tables · 16564 hands · 4.2 s

Command: `watch --interval 30 --tables 200 --agent arena-watch --question auto-ladder-on-bots-change`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 200 | 200 | 28.60 | 0.49 | 2.14 | 100% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.053 | 0.65 | 0 |
| 2 | **keep-made-plus-draw-v2** | 200 | 200 | 15.70 | 2.88 | 4.04 | 42% | 24% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.231 | 2.17 | 0 |
| 3 | **bot** | 200 | 200 | 12.20 | 2.60 | 4.36 | 36% | 16% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.138 | 0.36 | 0 |
| 4 | **v0-baseline** | 200 | 200 | 12.05 | 2.65 | 4.29 | 34% | 17% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.176 | 0.94 | 0 |
| 5 | **cap-floor-count** | 200 | 200 | 11.20 | 2.59 | 4.59 | 31% | 16% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.275 | 8.00 | 0 |
| 6 | **icm-pushfold** | 200 | 200 | 10.20 | 2.43 | 4.38 | 30% | 12% | 0.0000 | 0 | 0 | 0 | 0.029 | 0.951 | 3.23 | 0 |
| 7 | **keep-made-plus-draw** | 200 | 200 | 9.25 | 2.45 | 4.67 | 25% | 14% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.249 | 0.66 | 0 |
| 8 | **min_raiser** | 200 | 200 | 0.80 | 0.77 | 7.03 | 2% | 1% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.037 | 0.08 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 86% | 14% | 0% | 0% | 0% | 0% | 0% |
| keep-made-plus-draw-v2 | 24% | 2% | 18% | 16% | 10% | 14% | 14% | 4% |
| bot | 16% | 2% | 18% | 11% | 20% | 18% | 12% | 3% |
| v0-baseline | 17% | 2% | 14% | 20% | 18% | 10% | 16% | 3% |
| cap-floor-count | 16% | 2% | 13% | 14% | 14% | 20% | 17% | 5% |
| icm-pushfold | 12% | 4% | 13% | 22% | 15% | 20% | 12% | 2% |
| keep-made-plus-draw | 14% | 2% | 10% | 16% | 19% | 22% | 16% | 2% |
| min_raiser | 1% | 0% | 2% | 4% | 6% | 11% | 29% | 48% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | keep-made-plus-draw-v2 | bot | v0-baseline | cap-floor-count | icm-pushfold | keep-made-plus-draw | min_raiser |
|---|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 150-0-50 | 164-0-36 | 161-0-39 | 164-0-36 | 166-0-34 | 169-0-31 | 198-0-2 |
| **keep-made-plus-draw-v2** | 50-0-150 | · | 111-3-86 | 102-1-97 | 112-1-87 | 115-2-83 | 115-1-84 | 168-11-21 |
| **bot** | 36-0-164 | 86-3-111 | · | 96-2-102 | 107-4-89 | 102-1-97 | 106-2-92 | 169-14-17 |
| **v0-baseline** | 39-0-161 | 97-1-102 | 102-2-96 | · | 106-4-90 | 100-1-99 | 114-1-85 | 166-9-25 |
| **cap-floor-count** | 36-0-164 | 87-1-112 | 89-4-107 | 90-4-106 | · | 90-4-106 | 99-3-98 | 160-14-26 |
| **icm-pushfold** | 34-0-166 | 83-2-115 | 97-1-102 | 99-1-100 | 106-4-90 | · | 110-5-85 | 175-6-19 |
| **keep-made-plus-draw** | 31-0-169 | 84-1-115 | 92-2-106 | 85-1-114 | 98-3-99 | 85-5-110 | · | 169-9-22 |
| **min_raiser** | 2-0-198 | 21-11-168 | 17-14-169 | 25-9-166 | 26-14-160 | 19-6-175 | 22-9-169 | · |

Files: `arena/results/20261106-191644-ladder-efc5` (tables.jsonl, seats.csv, summary.json, run.json).
