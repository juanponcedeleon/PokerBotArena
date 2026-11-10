# Arena run `fp-cfc2-vs-fp-v3` — fast mode

Started 2026-11-06T20:52:16 · seed `fpcfc2` · scheme ab · 3206 tables · 419534 hands · 72.0 s

Command: `ab bots/fp-v3 bots/fp-cfc2 --field v0-baseline check_or_fold arch-folder arch-shover arch-station cap-floor-count-v6 --tables 1600 --seed fpcfc2 --agent Claude(cap-floor-count-agent) --name fp-cfc2-vs-fp-v3 --question fp-v3 + certain-math cap/floor overrides only (beat all caps -> value; below floor -> never pay off) vs fp-v3`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `fp-cfc2` replaces `fp-v3` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1180 | 21.63 | 22.73 | +1.10 | ±0.44 | 0.000 | 104 / 1033 / 43 | **fp-cfc2 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~230.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-cfc2** | 1180 | 1832 | 22.03 | 0.95 | 3.21 | 59% | 28% | 0.0000 | 0 | 0 | 0 | 0.030 | 0.501 | 68.14 | 0 |
| 2 | **fp-v3** | 1180 | 1832 | 20.96 | 0.95 | 3.33 | 56% | 26% | 0.0000 | 0 | 0 | 0 | 0.030 | 0.462 | 69.07 | 0 |
| 3 | **cap-floor-count-v6** | 2360 | 3664 | 18.51 | 0.70 | 3.72 | 46% | 27% | 0.0000 | 1 | 0 | 0 | 0.020 | 0.610 | 67.22 | 0 |
| 4 | **arch-folder** | 2338 | 3664 | 16.31 | 0.51 | 3.49 | 56% | 6% | 0.0000 | 0 | 0 | 0 | 0.013 | 0.142 | 67.91 | 0 |
| 5 | **v0-baseline** | 2344 | 3664 | 14.22 | 0.67 | 4.31 | 35% | 22% | 0.0000 | 0 | 0 | 0 | 0.020 | 0.289 | 37.38 | 0 |
| 6 | **check_or_fold** | 2382 | 3664 | 13.43 | 0.39 | 3.37 | 58% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.026 | 21.75 | 0 |
| 7 | **arch-shover** | 2370 | 3664 | 2.48 | 0.33 | 6.12 | 6% | 4% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.065 | 4.83 | 0 |
| 8 | **arch-station** | 2358 | 3664 | 1.06 | 0.18 | 6.06 | 4% | 1% | 0.0000 | 0 | 0 | 0 | 0.006 | 0.076 | 47.77 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-cfc2 | 28% | 20% | 11% | 11% | 13% | 10% | 5% | 2% |
| fp-v3 | 26% | 19% | 10% | 11% | 15% | 11% | 6% | 2% |
| cap-floor-count-v6 | 27% | 11% | 8% | 12% | 16% | 15% | 9% | 3% |
| arch-folder | 6% | 31% | 19% | 15% | 15% | 10% | 4% | 1% |
| v0-baseline | 22% | 7% | 6% | 10% | 17% | 19% | 14% | 4% |
| check_or_fold | 0% | 18% | 40% | 31% | 10% | 1% | 0% | 0% |
| arch-shover | 4% | 0% | 2% | 6% | 13% | 27% | 31% | 16% |
| arch-station | 1% | 1% | 3% | 10% | 16% | 28% | 27% | 15% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-cfc2 | fp-v3 | cap-floor-count-v6 | arch-folder | v0-baseline | check_or_fold | arch-shover | arch-station |
|---|---|---|---|---|---|---|---|---|
| **fp-cfc2** | · | 0-0-0 | 445-0-396 | 556-0-290 | 495-2-336 | 591-0-252 | 778-10-73 | 760-12-54 |
| **fp-v3** | 0-0-0 | · | 430-0-411 | 540-0-306 | 477-2-354 | 561-0-282 | 778-10-73 | 753-12-61 |
| **cap-floor-count-v6** | 396-0-445 | 411-0-430 | · | 896-2-772 | 933-4-733 | 1007-0-709 | 1497-40-159 | 1523-16-135 |
| **arch-folder** | 290-0-556 | 306-0-540 | 772-2-896 | · | 907-0-747 | 1020-0-656 | 1533-2-137 | 1584-4-88 |
| **v0-baseline** | 336-2-495 | 354-2-477 | 733-4-933 | 747-0-907 | · | 793-0-899 | 1348-60-254 | 1417-34-241 |
| **check_or_fold** | 252-0-591 | 282-0-561 | 709-0-1007 | 656-0-1020 | 899-0-793 | · | 1565-0-133 | 1685-0-27 |
| **arch-shover** | 73-10-778 | 73-10-778 | 159-40-1497 | 137-2-1533 | 254-60-1348 | 133-0-1565 | · | 548-242-902 |
| **arch-station** | 54-12-760 | 61-12-753 | 135-16-1523 | 88-4-1584 | 241-34-1417 | 27-0-1685 | 902-242-548 | · |

Files: `arena/results/20261106-205216-fp-cfc2-vs-fp-v3-5aa5` (tables.jsonl, seats.csv, summary.json, run.json).
