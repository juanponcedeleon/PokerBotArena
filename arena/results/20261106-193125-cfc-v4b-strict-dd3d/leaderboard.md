# Arena run `cfc-v4b-strict` — strict mode

Started 2026-11-06T19:31:25 · seed `strict1` · scheme league · 32 tables · 3309 hands · 13.9 s

Command: `league bots/cap-floor-count-v4b bots/v0-nowar min_raiser check_or_fold --mode strict --tables 32 --seed strict1 --name cfc-v4b-strict --agent Claude(cap-floor-count-agent) --question strict-mode timing of v4b (real pipe/JSON overhead): any timeouts?`

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 32 | 64 | 20.16 | 2.58 | 2.81 | 83% | 0% | 0.0000 | 0 | 0 | 0 | 0.262 | 1.543 | 44.70 | 0 |
| 2 | **cap-floor-count-v4b** | 32 | 64 | 15.78 | 5.54 | 3.86 | 36% | 27% | 0.0000 | 0 | 0 | 0 | 0.278 | 2.034 | 5.22 | 0 |
| 3 | **v0-nowar** | 32 | 64 | 13.28 | 5.29 | 4.19 | 30% | 22% | 0.0000 | 0 | 0 | 0 | 0.271 | 4.373 | 10.49 | 0 |
| 4 | **min_raiser** | 32 | 64 | 0.78 | 1.56 | 6.98 | 2% | 2% | 0.0000 | 0 | 0 | 0 | 0.255 | 3.152 | 10.81 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 36% | 47% | 17% | 0% | 0% | 0% | 0% |
| cap-floor-count-v4b | 27% | 6% | 3% | 19% | 17% | 20% | 8% | 0% |
| v0-nowar | 22% | 8% | 0% | 12% | 27% | 20% | 11% | 0% |
| min_raiser | 2% | 0% | 0% | 2% | 6% | 12% | 41% | 38% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | cap-floor-count-v4b | v0-nowar | min_raiser |
|---|---|---|---|---|
| **check_or_fold** | · | 13-0-19 | 13-0-19 | 31-0-1 |
| **cap-floor-count-v4b** | 19-0-13 | · | 17-0-15 | 31-0-1 |
| **v0-nowar** | 19-0-13 | 15-0-17 | · | 28-0-4 |
| **min_raiser** | 1-0-31 | 1-0-31 | 4-0-28 | · |

Files: `arena/results/20261106-193125-cfc-v4b-strict-dd3d` (tables.jsonl, seats.csv, summary.json, run.json).
