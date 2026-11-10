# Arena run `cfc-v3-vs-nowar` — fast mode

Started 2026-11-06T19:21:45 · seed `cfc3` · scheme ab · 812 tables · 51968 hands · 13.7 s

Command: `ab bots/v0-nowar bots/cap-floor-count-v3 --all --tables 400 --seed cfc3 --agent Claude(cap-floor-count-agent) --name cfc-v3-vs-nowar --question postflop module isolated: v3 vs v0-nowar (same preflop), pool field`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `cap-floor-count-v3` replaces `v0-nowar` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 294 | 17.05 | 16.38 | -0.67 | ±1.62 | 0.417 | 66 / 150 / 78 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~767.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **v0-nowar** | 294 | 464 | 17.05 | 1.62 | 3.65 | 55% | 13% | 0.0000 | 0 | 0 | 0 | 0.021 | 0.301 | 25.82 | 0 |
| 2 | **cap-floor-count-v3** | 294 | 464 | 16.36 | 1.67 | 3.74 | 51% | 15% | 0.0000 | 0 | 0 | 0 | 0.022 | 1.461 | 36.87 | 0 |
| 3 | **keep-made-plus-draw** | 610 | 928 | 12.70 | 1.17 | 4.48 | 38% | 14% | 0.0000 | 0 | 0 | 0 | 0.021 | 0.761 | 32.12 | 0 |
| 4 | **keep-made-plus-draw-v2** | 600 | 928 | 12.26 | 1.15 | 4.64 | 36% | 12% | 0.0000 | 0 | 0 | 0 | 0.021 | 0.751 | 47.22 | 0 |
| 5 | **cap-floor-count-v2** | 586 | 928 | 12.05 | 1.16 | 4.61 | 35% | 13% | 0.0000 | 0 | 0 | 0 | 0.020 | 1.979 | 55.36 | 0 |
| 6 | **cap-floor-count** | 616 | 928 | 11.55 | 1.18 | 4.72 | 32% | 14% | 0.0000 | 0 | 0 | 0 | 0.021 | 1.324 | 46.99 | 0 |
| 7 | **v0-baseline** | 624 | 928 | 11.45 | 1.12 | 4.65 | 34% | 11% | 0.0000 | 0 | 0 | 0 | 0.021 | 0.567 | 35.18 | 0 |
| 8 | **icm-pushfold** | 590 | 928 | 10.78 | 1.06 | 4.60 | 34% | 9% | 0.0000 | 0 | 0 | 0 | 0.034 | 2.464 | 35.44 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| v0-nowar | 13% | 21% | 20% | 15% | 10% | 9% | 6% | 5% |
| cap-floor-count-v3 | 15% | 17% | 19% | 16% | 11% | 9% | 7% | 5% |
| keep-made-plus-draw | 14% | 11% | 13% | 12% | 13% | 12% | 15% | 10% |
| keep-made-plus-draw-v2 | 12% | 12% | 12% | 9% | 13% | 15% | 13% | 14% |
| cap-floor-count-v2 | 13% | 10% | 12% | 11% | 12% | 14% | 15% | 12% |
| cap-floor-count | 14% | 9% | 9% | 11% | 13% | 16% | 16% | 12% |
| v0-baseline | 11% | 12% | 11% | 14% | 11% | 11% | 16% | 13% |
| icm-pushfold | 9% | 14% | 11% | 15% | 14% | 13% | 10% | 14% |

## Head-to-head (row finished above column: wins-ties-losses)

| | v0-nowar | cap-floor-count-v3 | keep-made-plus-draw | keep-made-plus-draw-v2 | cap-floor-count-v2 | cap-floor-count | v0-baseline | icm-pushfold |
|---|---|---|---|---|---|---|---|---|
| **v0-nowar** | · | 0-0-0 | 131-0-88 | 121-0-85 | 122-1-83 | 135-0-87 | 144-0-79 | 133-0-74 |
| **cap-floor-count-v3** | 0-0-0 | · | 130-0-89 | 121-1-84 | 123-1-82 | 139-0-83 | 143-0-80 | 118-0-89 |
| **keep-made-plus-draw** | 88-0-131 | 89-0-130 | · | 210-0-222 | 244-0-182 | 245-0-203 | 232-0-240 | 240-0-194 |
| **keep-made-plus-draw-v2** | 85-0-121 | 84-1-121 | 222-0-210 | · | 209-1-200 | 223-3-218 | 209-2-237 | 225-2-191 |
| **cap-floor-count-v2** | 83-1-122 | 82-1-123 | 182-0-244 | 200-1-209 | · | 229-2-185 | 246-0-194 | 215-0-201 |
| **cap-floor-count** | 87-0-135 | 83-0-139 | 203-0-245 | 218-3-223 | 185-2-229 | · | 227-0-237 | 209-2-223 |
| **v0-baseline** | 79-0-144 | 80-0-143 | 240-0-232 | 237-2-209 | 194-0-246 | 237-0-227 | · | 234-0-194 |
| **icm-pushfold** | 74-0-133 | 89-0-118 | 194-0-240 | 191-2-225 | 201-0-215 | 223-2-209 | 194-0-234 | · |

Files: `arena/results/20261106-192145-cfc-v3-vs-nowar-8e6e` (tables.jsonl, seats.csv, summary.json, run.json).
