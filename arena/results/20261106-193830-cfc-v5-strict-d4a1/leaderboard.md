# Arena run `cfc-v5-strict` — strict mode

Started 2026-11-06T19:38:30 · seed `strict1` · scheme league · 32 tables · 3309 hands · 7.6 s

Command: `league bots/cap-floor-count-v5 bots/v0-nowar min_raiser check_or_fold --mode strict --tables 32 --seed strict1 --name cfc-v5-strict --agent Claude(cap-floor-count-agent) --question strict-mode timing of v5 (= v4b + GC tuning): timeouts, p99`

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 32 | 64 | 20.16 | 2.58 | 2.81 | 83% | 0% | 0.0000 | 0 | 0 | 0 | 0.271 | 1.190 | 45.66 | 0 |
| 2 | **cap-floor-count-v5** | 32 | 64 | 15.78 | 5.54 | 3.86 | 36% | 27% | 0.0000 | 0 | 0 | 0 | 0.290 | 0.916 | 1.59 | 0 |
| 3 | **v0-nowar** | 32 | 64 | 13.28 | 5.29 | 4.19 | 30% | 22% | 0.0000 | 0 | 0 | 0 | 0.282 | 1.240 | 3.92 | 0 |
| 4 | **min_raiser** | 32 | 64 | 0.78 | 1.56 | 6.98 | 2% | 2% | 0.0000 | 0 | 0 | 0 | 0.255 | 2.144 | 3.16 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 36% | 47% | 17% | 0% | 0% | 0% | 0% |
| cap-floor-count-v5 | 27% | 6% | 3% | 19% | 17% | 20% | 8% | 0% |
| v0-nowar | 22% | 8% | 0% | 12% | 27% | 20% | 11% | 0% |
| min_raiser | 2% | 0% | 0% | 2% | 6% | 12% | 41% | 38% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | cap-floor-count-v5 | v0-nowar | min_raiser |
|---|---|---|---|---|
| **check_or_fold** | · | 13-0-19 | 13-0-19 | 31-0-1 |
| **cap-floor-count-v5** | 19-0-13 | · | 17-0-15 | 31-0-1 |
| **v0-nowar** | 19-0-13 | 15-0-17 | · | 28-0-4 |
| **min_raiser** | 1-0-31 | 1-0-31 | 4-0-28 | · |

Files: `arena/results/20261106-193830-cfc-v5-strict-d4a1` (tables.jsonl, seats.csv, summary.json, run.json).
