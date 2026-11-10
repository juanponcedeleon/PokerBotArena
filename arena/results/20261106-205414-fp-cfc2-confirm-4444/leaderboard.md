# Arena run `fp-cfc2-confirm` — fast mode

Started 2026-11-06T20:54:14 · seed `fpcfc3` · scheme ab · 3206 tables · 356385 hands · 49.9 s

Command: `ab bots/fp-v3 bots/fp-cfc2 --field v0-baseline cap-floor-count-v6 keep-made-plus-draw-v2 arch-shover min_raiser check_or_fold --tables 1600 --seed fpcfc3 --agent Claude(cap-floor-count-agent) --name fp-cfc2-confirm --question confirmation of fp-cfc2 (+1.10 vs fp-v3) on a second seed and field`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `fp-cfc2` replaces `fp-v3` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1197 | 22.40 | 23.22 | +0.82 | ±0.35 | 0.000 | 83 / 1071 / 43 | **fp-cfc2 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~150.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-cfc2** | 1197 | 1832 | 22.43 | 0.86 | 2.99 | 65% | 21% | 0.0000 | 0 | 0 | 0 | 0.029 | 0.436 | 8.98 | 0 |
| 2 | **fp-v3** | 1197 | 1832 | 21.66 | 0.87 | 3.07 | 63% | 21% | 0.0000 | 0 | 0 | 0 | 0.029 | 0.326 | 6.16 | 0 |
| 3 | **cap-floor-count-v6** | 2380 | 3664 | 17.37 | 0.67 | 3.63 | 46% | 23% | 0.0000 | 0 | 0 | 0 | 0.019 | 0.481 | 14.63 | 0 |
| 4 | **check_or_fold** | 2340 | 3664 | 17.21 | 0.37 | 3.06 | 72% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.030 | 14.56 | 0 |
| 5 | **v0-baseline** | 2344 | 3664 | 13.28 | 0.65 | 4.25 | 34% | 19% | 0.0000 | 0 | 0 | 0 | 0.019 | 0.241 | 7.16 | 0 |
| 6 | **keep-made-plus-draw-v2** | 2300 | 3664 | 13.13 | 0.65 | 4.28 | 33% | 19% | 0.0000 | 0 | 0 | 0 | 0.019 | 0.304 | 3.92 | 0 |
| 7 | **arch-shover** | 2364 | 3664 | 2.51 | 0.32 | 5.89 | 7% | 3% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.072 | 0.52 | 0 |
| 8 | **min_raiser** | 2354 | 3664 | 1.95 | 0.28 | 5.94 | 6% | 2% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.048 | 1.77 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-cfc2 | 21% | 30% | 13% | 12% | 13% | 7% | 3% | 0% |
| fp-v3 | 21% | 29% | 13% | 12% | 14% | 8% | 3% | 0% |
| cap-floor-count-v6 | 23% | 13% | 10% | 16% | 16% | 13% | 7% | 2% |
| check_or_fold | 0% | 28% | 45% | 23% | 5% | 0% | 0% | 0% |
| v0-baseline | 19% | 7% | 7% | 14% | 19% | 18% | 11% | 4% |
| keep-made-plus-draw-v2 | 19% | 7% | 7% | 14% | 18% | 19% | 12% | 3% |
| arch-shover | 3% | 1% | 3% | 7% | 18% | 28% | 26% | 13% |
| min_raiser | 2% | 1% | 3% | 7% | 17% | 31% | 29% | 10% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-cfc2 | fp-v3 | cap-floor-count-v6 | check_or_fold | v0-baseline | keep-made-plus-draw-v2 | arch-shover | min_raiser |
|---|---|---|---|---|---|---|---|---|
| **fp-cfc2** | · | 0-0-0 | 498-1-376 | 579-0-266 | 540-1-322 | 542-1-281 | 773-10-65 | 803-7-43 |
| **fp-v3** | 0-0-0 | · | 485-1-389 | 554-0-291 | 533-1-329 | 529-1-294 | 773-10-65 | 798-7-48 |
| **cap-floor-count-v6** | 376-1-498 | 389-1-485 | · | 851-0-825 | 982-4-722 | 936-12-716 | 1486-18-208 | 1572-34-106 |
| **check_or_fold** | 266-0-579 | 291-0-554 | 825-0-851 | · | 923-0-701 | 964-0-648 | 1562-0-114 | 1614-0-80 |
| **v0-baseline** | 322-1-540 | 329-1-533 | 722-4-982 | 701-0-923 | · | 797-12-819 | 1386-32-256 | 1350-44-282 |
| **keep-made-plus-draw-v2** | 281-1-542 | 294-1-529 | 716-12-936 | 648-0-964 | 819-12-797 | · | 1322-46-278 | 1276-46-270 |
| **arch-shover** | 65-10-773 | 65-10-773 | 208-18-1486 | 114-0-1562 | 256-32-1386 | 278-46-1322 | · | 656-344-696 |
| **min_raiser** | 43-7-803 | 48-7-798 | 106-34-1572 | 80-0-1614 | 282-44-1350 | 270-46-1276 | 696-344-656 | · |

Files: `arena/results/20261106-205414-fp-cfc2-confirm-4444` (tables.jsonl, seats.csv, summary.json, run.json).
