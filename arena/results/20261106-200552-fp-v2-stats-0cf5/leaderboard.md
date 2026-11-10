# Arena run `fp-v2-stats` — fast mode

Started 2026-11-06T20:05:52 · seed `fpstats` · scheme league · 301 tables · 39039 hands · 36.8 s

Command: `league fp-v2 cap-floor-count-v6 v0-nowar arch-folder arch-shover arch-station check_or_fold --tables 300 --seed fpstats --log --name fp-v2-stats --agent Claude (keep-rule agent, branching out) --question Behaviour stats of fp-v2 vs the pool (logged league, 300 tables) for the next iteration --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-v2** | 225 | 344 | 19.85 | 2.24 | 3.51 | 52% | 26% | 0.0000 | 0 | 0 | 0 | 0.035 | 13.302 | 33.56 | 0 |
| 2 | **cap-floor-count-v6** | 217 | 344 | 19.13 | 2.31 | 3.66 | 47% | 28% | 0.0001 | 4 | 0 | 0 | 0.024 | 15.468 | 25.06 | 0 |
| 3 | **arch-folder** | 216 | 344 | 16.63 | 1.64 | 3.38 | 58% | 5% | 0.0000 | 0 | 0 | 0 | 0.015 | 11.926 | 19.17 | 0 |
| 4 | **check_or_fold** | 225 | 344 | 13.46 | 1.26 | 3.39 | 58% | 0% | 0.0000 | 0 | 0 | 0 | 0.005 | 8.082 | 17.38 | 0 |
| 5 | **v0-nowar** | 215 | 344 | 13.24 | 2.11 | 4.28 | 35% | 19% | 0.0000 | 0 | 0 | 0 | 0.024 | 12.453 | 18.96 | 0 |
| 6 | **arch-shover** | 225 | 344 | 4.00 | 1.42 | 5.90 | 9% | 8% | 0.0000 | 0 | 0 | 0 | 0.005 | 11.545 | 15.26 | 0 |
| 7 | **arch-station** | 228 | 344 | 1.19 | 0.68 | 6.14 | 5% | 1% | 0.0000 | 0 | 0 | 0 | 0.007 | 11.906 | 14.45 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-v2 | 26% | 16% | 10% | 12% | 14% | 12% | 8% | 2% |
| cap-floor-count-v6 | 28% | 13% | 7% | 11% | 15% | 15% | 8% | 3% |
| arch-folder | 5% | 34% | 19% | 16% | 15% | 9% | 2% | 0% |
| check_or_fold | 0% | 18% | 41% | 30% | 9% | 2% | 1% | 0% |
| v0-nowar | 19% | 6% | 9% | 11% | 21% | 19% | 9% | 5% |
| arch-shover | 8% | 0% | 1% | 6% | 14% | 29% | 27% | 15% |
| arch-station | 1% | 1% | 3% | 8% | 15% | 28% | 29% | 16% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-v2 | cap-floor-count-v6 | arch-folder | check_or_fold | v0-nowar | arch-shover | arch-station |
|---|---|---|---|---|---|---|---|
| **fp-v2** | · | 69-1-91 | 88-0-68 | 95-0-64 | 91-2-63 | 143-6-25 | 143-5-17 |
| **cap-floor-count-v6** | 91-1-69 | · | 86-0-67 | 107-0-52 | 91-0-59 | 129-4-26 | 146-3-8 |
| **arch-folder** | 68-0-88 | 67-0-86 | · | 91-0-66 | 89-0-59 | 134-0-20 | 157-0-8 |
| **check_or_fold** | 64-0-95 | 52-0-107 | 66-0-91 | · | 78-0-73 | 150-0-18 | 157-0-5 |
| **v0-nowar** | 63-2-91 | 59-0-91 | 59-0-89 | 73-0-78 | · | 125-7-26 | 126-7-24 |
| **arch-shover** | 25-6-143 | 26-4-129 | 20-0-134 | 18-0-150 | 26-7-125 | · | 64-26-75 |
| **arch-station** | 17-5-143 | 8-3-146 | 8-0-157 | 5-0-157 | 24-7-126 | 75-26-64 | · |

Files: `arena/results/20261106-200552-fp-v2-stats-0cf5` (tables.jsonl, seats.csv, summary.json, run.json).
