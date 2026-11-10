# Arena run `strict-shards` — strict mode

Started 2026-11-06T19:07:00 · seed `s3` · scheme league · 12 tables · 1190 hands · 17.9 s

Command: `league bot min_raiser check_or_fold --tables 12 --seed s3 --mode strict --name strict-shards --no-experiment-log --quiet`

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **bot** | 12 | 32 | 17.19 | 8.70 | 3.91 | 34% | 34% | 0.0007 | 2 | 0 | 0 | 0.579 | 14.021 | 63.74 | 0 |
| 2 | **check_or_fold** | 12 | 32 | 16.88 | 4.71 | 3.12 | 66% | 0% | 0.0004 | 1 | 1 | 0 | 0.541 | 15.909 | 349.00 | 0 |
| 3 | **min_raiser** | 12 | 32 | 3.44 | 3.73 | 5.31 | 12% | 3% | 0.0000 | 0 | 0 | 0 | 0.605 | 10.781 | 11.21 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| bot | 34% | 0% | 0% | 19% | 12% | 22% | 12% | 0% |
| check_or_fold | 0% | 38% | 28% | 22% | 9% | 3% | 0% | 0% |
| min_raiser | 3% | 0% | 9% | 22% | 19% | 22% | 12% | 12% |

## Head-to-head (row finished above column: wins-ties-losses)

| | bot | check_or_fold | min_raiser |
|---|---|---|---|
| **bot** | · | 11-0-1 | 11-0-1 |
| **check_or_fold** | 1-0-11 | · | 11-0-1 |
| **min_raiser** | 1-0-11 | 1-0-11 | · |

## Bot errors (first occurrence per table; untrusted text)

```
check_or_fold: The bot stopped responding.
```

Files: `arena/results/20261106-190700-strict-shards-1878` (tables.jsonl, seats.csv, summary.json, run.json).
