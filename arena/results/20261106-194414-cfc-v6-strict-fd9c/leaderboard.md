# Arena run `cfc-v6-strict` — strict mode

Started 2026-11-06T19:44:14 · seed `strict1` · scheme league · 32 tables · 3812 hands · 11.6 s

Command: `league bots/cap-floor-count-v6 bots/v0-nowar min_raiser check_or_fold --mode strict --tables 32 --seed strict1 --name cfc-v6-strict --agent Claude(cap-floor-count-agent) --question strict-mode timing of v6: timeouts, p99`

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **cap-floor-count-v6** | 32 | 64 | 18.44 | 5.29 | 3.61 | 47% | 23% | 0.0002 | 1 | 1 | 0 | 0.319 | 5.747 | 697.23 | 0 |
| 2 | **v0-nowar** | 32 | 64 | 15.62 | 5.47 | 4.06 | 36% | 25% | 0.0002 | 1 | 1 | 0 | 0.316 | 10.930 | 648.28 | 0 |
| 3 | **check_or_fold** | 32 | 64 | 15.16 | 2.92 | 3.17 | 66% | 0% | 0.0000 | 0 | 0 | 0 | 0.292 | 9.791 | 51.62 | 0 |
| 4 | **min_raiser** | 32 | 64 | 0.78 | 1.56 | 7.00 | 2% | 2% | 0.0003 | 1 | 0 | 0 | 0.335 | 4.533 | 798.23 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| cap-floor-count-v6 | 23% | 20% | 3% | 12% | 14% | 19% | 8% | 0% |
| v0-nowar | 25% | 9% | 2% | 5% | 28% | 20% | 11% | 0% |
| check_or_fold | 0% | 20% | 45% | 31% | 3% | 0% | 0% | 0% |
| min_raiser | 2% | 0% | 0% | 2% | 5% | 14% | 41% | 38% |

## Head-to-head (row finished above column: wins-ties-losses)

| | cap-floor-count-v6 | v0-nowar | check_or_fold | min_raiser |
|---|---|---|---|---|
| **cap-floor-count-v6** | · | 15-0-17 | 22-0-10 | 31-0-1 |
| **v0-nowar** | 17-0-15 | · | 22-0-10 | 29-0-3 |
| **check_or_fold** | 10-0-22 | 10-0-22 | · | 31-0-1 |
| **min_raiser** | 1-0-31 | 3-0-29 | 1-0-31 | · |

## Bot errors (first occurrence per table; untrusted text)

```
cap-floor-count-v6: The bot stopped responding.
```
```
v0-nowar: The bot stopped responding.
```

Files: `arena/results/20261106-194414-cfc-v6-strict-fd9c` (tables.jsonl, seats.csv, summary.json, run.json).
