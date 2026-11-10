# Arena run `cfc-v6-strict2` — strict mode

Started 2026-11-06T19:50:34 · seed `strict2` · scheme league · 32 tables · 3873 hands · 26.9 s

Command: `league bots/cap-floor-count-v6 bots/v0-nowar min_raiser check_or_fold --mode strict --tables 32 --seed strict2 --name cfc-v6-strict2 --agent Claude(cap-floor-count-agent) --question strict-mode timing of v6, rerun after a machine-wide stall contaminated cfc-v6-strict`

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **cap-floor-count-v6** | 32 | 64 | 19.53 | 5.64 | 3.58 | 45% | 30% | 0.0000 | 0 | 0 | 0 | 0.613 | 11.955 | 28.36 | 0 |
| 2 | **check_or_fold** | 32 | 64 | 15.78 | 2.84 | 3.12 | 69% | 0% | 0.0000 | 0 | 0 | 0 | 0.557 | 15.720 | 20.53 | 0 |
| 3 | **v0-nowar** | 32 | 64 | 14.69 | 5.19 | 4.11 | 36% | 20% | 0.0000 | 0 | 0 | 0 | 0.584 | 15.060 | 29.49 | 0 |
| 4 | **min_raiser** | 32 | 64 | 0.00 | 0.00 | 7.05 | 0% | 0% | 0.0000 | 0 | 0 | 0 | 0.592 | 17.360 | 26.15 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| cap-floor-count-v6 | 30% | 16% | 0% | 11% | 19% | 16% | 9% | 0% |
| check_or_fold | 0% | 20% | 48% | 30% | 2% | 0% | 0% | 0% |
| v0-nowar | 20% | 14% | 2% | 8% | 27% | 14% | 16% | 0% |
| min_raiser | 0% | 0% | 0% | 2% | 3% | 20% | 39% | 36% |

## Head-to-head (row finished above column: wins-ties-losses)

| | cap-floor-count-v6 | check_or_fold | v0-nowar | min_raiser |
|---|---|---|---|---|
| **cap-floor-count-v6** | · | 26-0-6 | 19-0-13 | 31-0-1 |
| **check_or_fold** | 6-0-26 | · | 11-0-21 | 32-0-0 |
| **v0-nowar** | 13-0-19 | 21-0-11 | · | 32-0-0 |
| **min_raiser** | 1-0-31 | 0-0-32 | 0-0-32 | · |

Files: `arena/results/20261106-195034-cfc-v6-strict2-5ede` (tables.jsonl, seats.csv, summary.json, run.json).
