# Arena run `cfc-v1-ab-pool` — fast mode

Started 2026-11-06T19:15:42 · seed `cfc2` · scheme ab · 800 tables · 45895 hands · 12.2 s

Command: `ab bot bots/cap-floor-count --all --tables 400 --seed cfc2 --log --name cfc-v1-ab-pool --agent Claude (cap-floor-count agent) --question cap/floor/count vs bot v0 in the full pool field (bots/ + examples)`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cap-floor-count` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 400 | 12.04 | 10.32 | -1.71 | ±1.21 | 0.006 | 97 / 178 / 125 | **bot is better** |

Pairs needed to resolve a 1-point difference at this variance: ~580.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **keep-made-plus-draw** | 800 | 1600 | 14.41 | 0.93 | 4.32 | 42% | 16% | 0.0000 | 0 | 0 | 0 | 0.019 | 0.364 | 36.91 | 0 |
| 2 | **v0-baseline** | 800 | 1600 | 12.38 | 0.90 | 4.52 | 36% | 14% | 0.0000 | 0 | 0 | 0 | 0.019 | 0.383 | 32.81 | 0 |
| 3 | **bot** | 400 | 800 | 12.04 | 1.20 | 4.52 | 37% | 11% | 0.0000 | 0 | 0 | 0 | 0.019 | 0.401 | 24.79 | 0 |
| 4 | **icm-pushfold** | 800 | 1600 | 12.03 | 0.83 | 4.45 | 38% | 9% | 0.0000 | 0 | 0 | 0 | 0.032 | 2.668 | 39.30 | 0 |
| 5 | **cap-floor-count** | 400 | 800 | 10.32 | 1.17 | 4.75 | 31% | 10% | 0.0000 | 0 | 0 | 0 | 0.020 | 1.490 | 43.20 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| keep-made-plus-draw | 16% | 12% | 14% | 11% | 11% | 11% | 13% | 11% |
| v0-baseline | 14% | 11% | 11% | 12% | 14% | 14% | 14% | 10% |
| bot | 11% | 12% | 14% | 14% | 12% | 11% | 14% | 12% |
| icm-pushfold | 9% | 16% | 13% | 13% | 12% | 14% | 12% | 10% |
| cap-floor-count | 10% | 10% | 11% | 13% | 15% | 14% | 15% | 13% |

## Head-to-head (row finished above column: wins-ties-losses)

| | keep-made-plus-draw | v0-baseline | bot | icm-pushfold | cap-floor-count |
|---|---|---|---|---|---|
| **keep-made-plus-draw** | · | 421-0-379 | 219-0-181 | 447-0-353 | 238-0-162 |
| **v0-baseline** | 379-0-421 | · | 201-0-199 | 414-2-384 | 227-0-173 |
| **bot** | 181-0-219 | 199-0-201 | · | 191-0-209 | 0-0-0 |
| **icm-pushfold** | 353-0-447 | 384-2-414 | 209-0-191 | · | 220-1-179 |
| **cap-floor-count** | 162-0-238 | 173-0-227 | 0-0-0 | 179-1-220 | · |

Files: `arena/results/20261106-191542-cfc-v1-ab-pool-3dd9` (tables.jsonl, seats.csv, summary.json, run.json).
