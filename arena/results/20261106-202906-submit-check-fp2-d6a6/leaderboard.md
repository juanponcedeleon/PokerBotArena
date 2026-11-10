# Arena run `submit-check-fp2` — fast mode

Started 2026-11-06T20:29:06 · seed `submit-fp2-1` · scheme league · 200 tables · 30193 hands · 5.5 s

Command: `league bot cap-floor-count-v6 check_or_fold arch-folder --tables 200 --seed submit-fp2-1 --name submit-check-fp2 --agent Claude (headmaster) --question pre-submission check: bot = fp-v2 copy, zero failures required --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **bot** | 200 | 400 | 18.30 | 2.12 | 4.17 | 46% | 26% | 0.0000 | 0 | 0 | 0 | 0.027 | 0.660 | 6.16 | 0 |
| 2 | **arch-folder** | 200 | 400 | 12.70 | 1.54 | 4.45 | 43% | 5% | 0.0000 | 0 | 0 | 0 | 0.011 | 0.137 | 2.51 | 0 |
| 3 | **cap-floor-count-v6** | 200 | 400 | 11.28 | 1.95 | 5.49 | 26% | 19% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.451 | 10.48 | 0 |
| 4 | **check_or_fold** | 200 | 400 | 7.72 | 1.06 | 3.89 | 35% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.070 | 1.37 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| bot | 26% | 12% | 8% | 4% | 8% | 14% | 16% | 10% |
| arch-folder | 5% | 27% | 11% | 6% | 10% | 19% | 13% | 9% |
| cap-floor-count-v6 | 19% | 4% | 4% | 2% | 8% | 12% | 21% | 30% |
| check_or_fold | 0% | 7% | 28% | 38% | 23% | 4% | 0% | 0% |

## Head-to-head (row finished above column: wins-ties-losses)

| | bot | arch-folder | cap-floor-count-v6 | check_or_fold |
|---|---|---|---|---|
| **bot** | · | 138-0-62 | 119-0-81 | 151-0-49 |
| **arch-folder** | 62-0-138 | · | 105-0-95 | 138-0-62 |
| **cap-floor-count-v6** | 81-0-119 | 95-0-105 | · | 99-0-101 |
| **check_or_fold** | 49-0-151 | 62-0-138 | 101-0-99 | · |

Files: `arena/results/20261106-202906-submit-check-fp2-d6a6` (tables.jsonl, seats.csv, summary.json, run.json).
