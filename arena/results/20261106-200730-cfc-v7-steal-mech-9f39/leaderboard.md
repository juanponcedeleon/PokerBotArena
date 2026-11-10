# Arena run `cfc-v7-steal-mech` — fast mode

Started 2026-11-06T20:07:30 · seed `cfc10` · scheme ab · 624 tables · 81736 hands · ? s

Command: `ab bots/cap-floor-count-v6 bots/cfc-v7-steal --field check_or_fold --tables 800 --seed cfc10 --log --agent Claude(cap-floor-count-agent) --name cfc-v7-steal-mech --question mechanism test: steal/probe exploits vs v6 in a field of pure folders (check_or_fold only)`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cfc-v7-steal` replaces `cap-floor-count-v6` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 309 | 15.55 | 16.26 | +0.71 | ±0.43 | 0.001 | 67 / 214 / 28 | **cfc-v7-steal is better** |

Pairs needed to resolve a 1-point difference at this variance: ~58.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **cfc-v7-steal** | 312 | 1248 | 16.30 | 1.21 | 4.96 | 38% | 25% | 0.0010 | 134 | 0 | 0 | 0.065 | 25.422 | 102.46 | 100 |
| 2 | **cap-floor-count-v6** | 312 | 1248 | 15.54 | 1.21 | 5.05 | 36% | 25% | 0.0001 | 12 | 0 | 0 | 0.022 | 23.029 | 66.56 | 0 |
| 3 | **check_or_fold** | 624 | 2496 | 9.08 | 0.47 | 3.99 | 38% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.798 | 42.24 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| cfc-v7-steal | 25% | 12% | 1% | 1% | 1% | 12% | 24% | 25% |
| cap-floor-count-v6 | 25% | 9% | 2% | 1% | 1% | 13% | 24% | 25% |
| check_or_fold | 0% | 14% | 24% | 24% | 24% | 13% | 1% | 0% |

## Head-to-head (row finished above column: wins-ties-losses)

| | cfc-v7-steal | cap-floor-count-v6 | check_or_fold |
|---|---|---|---|
| **cfc-v7-steal** | · | 0-0-0 | 312-0-0 |
| **cap-floor-count-v6** | 0-0-0 | · | 312-0-0 |
| **check_or_fold** | 0-0-312 | 0-0-312 | · |

Files: `arena/results/20261106-200730-cfc-v7-steal-mech-9f39` (tables.jsonl, seats.csv, summary.json, run.json).
