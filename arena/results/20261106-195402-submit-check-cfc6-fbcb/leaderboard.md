# Arena run `submit-check-cfc6` — fast mode

Started 2026-11-06T19:54:02 · seed `submit-cfc6-1` · scheme league · 200 tables · 23415 hands · 20.0 s

Command: `league bot v0-nowar check_or_fold min_raiser --tables 200 --seed submit-cfc6-1 --name submit-check-cfc6 --agent Claude (headmaster) --question pre-submission check: bot = cap-floor-count-v6 copy, zero failures required --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **bot** | 200 | 400 | 18.02 | 2.07 | 3.69 | 46% | 24% | 0.0002 | 8 | 0 | 0 | 0.019 | 5.029 | 139.20 | 0 |
| 2 | **v0-nowar** | 200 | 400 | 15.65 | 2.10 | 3.96 | 38% | 24% | 0.0001 | 3 | 0 | 0 | 0.020 | 2.222 | 160.63 | 0 |
| 3 | **check_or_fold** | 200 | 400 | 15.00 | 1.17 | 3.21 | 64% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.158 | 49.86 | 0 |
| 4 | **min_raiser** | 200 | 400 | 1.32 | 0.78 | 7.02 | 3% | 2% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.890 | 4.94 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| bot | 24% | 18% | 4% | 9% | 20% | 18% | 8% | 0% |
| v0-nowar | 24% | 10% | 4% | 11% | 21% | 22% | 9% | 0% |
| check_or_fold | 0% | 22% | 42% | 30% | 6% | 0% | 0% | 0% |
| min_raiser | 2% | 0% | 0% | 1% | 3% | 11% | 45% | 38% |

## Head-to-head (row finished above column: wins-ties-losses)

| | bot | v0-nowar | check_or_fold | min_raiser |
|---|---|---|---|---|
| **bot** | · | 100-0-100 | 142-0-58 | 188-0-12 |
| **v0-nowar** | 100-0-100 | · | 129-0-71 | 183-0-17 |
| **check_or_fold** | 58-0-142 | 71-0-129 | · | 189-0-11 |
| **min_raiser** | 12-0-188 | 17-0-183 | 11-0-189 | · |

Files: `arena/results/20261106-195402-submit-check-cfc6-fbcb` (tables.jsonl, seats.csv, summary.json, run.json).
