# Arena run `ab-keep-made-plus-draw-vs-bot` — fast mode

Started 2026-11-06T19:07:06 · seed `s31b` · scheme ab · 800 tables · 43645 hands · 13.4 s

Command: `ab bot keep-made-plus-draw --field v0-baseline --tables 400 --seed s31b --agent Claude (keep-rule agent) --question S3.1 keep rule vs bot v0 in a flop-heavy field (all other seats = v0-baseline copies) --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `keep-made-plus-draw` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 400 | 12.68 | 12.88 | +0.21 | ±0.33 | 0.221 | 37 / 334 / 29 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~44.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **keep-made-plus-draw** | 400 | 1600 | 12.88 | 0.89 | 4.46 | 38% | 13% | 0.0000 | 0 | 0 | 0 | 0.022 | 0.789 | 22.33 | 0 |
| 2 | **bot** | 400 | 1600 | 12.68 | 0.89 | 4.48 | 38% | 13% | 0.0000 | 0 | 0 | 0 | 0.021 | 0.894 | 20.10 | 0 |
| 3 | **v0-baseline** | 800 | 3200 | 12.22 | 0.61 | 4.47 | 37% | 12% | 0.0000 | 0 | 0 | 0 | 0.022 | 1.054 | 43.70 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| keep-made-plus-draw | 13% | 12% | 13% | 12% | 12% | 12% | 14% | 11% |
| bot | 13% | 11% | 13% | 12% | 12% | 12% | 14% | 11% |
| v0-baseline | 12% | 13% | 12% | 13% | 13% | 14% | 13% | 10% |

## Head-to-head (row finished above column: wins-ties-losses)

| | keep-made-plus-draw | bot | v0-baseline |
|---|---|---|---|
| **keep-made-plus-draw** | · | 0-0-0 | 214-0-186 |
| **bot** | 0-0-0 | · | 213-0-187 |
| **v0-baseline** | 186-0-214 | 187-0-213 | · |

Files: `arena/results/20261106-190706-ab-keep-made-plus-draw-vs-bot-a2b7` (tables.jsonl, seats.csv, summary.json, run.json).
