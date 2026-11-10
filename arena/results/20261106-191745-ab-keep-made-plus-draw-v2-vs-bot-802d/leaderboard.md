# Arena run `ab-keep-made-plus-draw-v2-vs-bot` — fast mode

Started 2026-11-06T19:17:45 · seed `s31c` · scheme ab · 4000 tables · 214836 hands · 62.7 s

Command: `ab bot keep-made-plus-draw-v2 --field v0-baseline --tables 2000 --seed s31c --agent Claude (keep-rule agent) --question v2 vs bot v0, flop-heavy field v0-baseline, same seed as the v1 run (s31c) --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `keep-made-plus-draw-v2` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 2000 | 12.41 | 12.70 | +0.29 | ±0.20 | 0.004 | 304 / 1447 / 249 | **keep-made-plus-draw-v2 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~78.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **keep-made-plus-draw-v2** | 2000 | 8000 | 12.70 | 0.39 | 4.44 | 38% | 13% | 0.0000 | 5 | 0 | 0 | 0.021 | 6.501 | 101.98 | 0 |
| 2 | **v0-baseline** | 4000 | 16000 | 12.44 | 0.28 | 4.49 | 37% | 12% | 0.0000 | 0 | 0 | 0 | 0.021 | 2.793 | 98.43 | 0 |
| 3 | **bot** | 2000 | 8000 | 12.41 | 0.39 | 4.46 | 37% | 13% | 0.0000 | 0 | 0 | 0 | 0.021 | 2.549 | 82.69 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| keep-made-plus-draw-v2 | 13% | 12% | 13% | 13% | 13% | 13% | 13% | 10% |
| v0-baseline | 12% | 13% | 12% | 12% | 12% | 13% | 14% | 11% |
| bot | 13% | 12% | 13% | 13% | 13% | 13% | 13% | 10% |

## Head-to-head (row finished above column: wins-ties-losses)

| | keep-made-plus-draw-v2 | v0-baseline | bot |
|---|---|---|---|
| **keep-made-plus-draw-v2** | · | 1035-0-965 | 0-0-0 |
| **v0-baseline** | 965-0-1035 | · | 997-0-1003 |
| **bot** | 0-0-0 | 1003-0-997 | · |

Files: `arena/results/20261106-191745-ab-keep-made-plus-draw-v2-vs-bot-802d` (tables.jsonl, seats.csv, summary.json, run.json).
