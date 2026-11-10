# Arena run `ab-keep-made-plus-draw-v2-vs-keep-made-plus-draw` — fast mode

Started 2026-11-06T19:16:59 · seed `s31d` · scheme ab · 4000 tables · 214203 hands · 43.5 s

Command: `ab keep-made-plus-draw keep-made-plus-draw-v2 --field v0-baseline --tables 2000 --seed s31d --agent Claude (keep-rule agent) --question v2 (tuned, opponent-scaled keep weights; S3.1+S3.3) vs v1 (S3.1), flop-heavy field v0-baseline --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `keep-made-plus-draw-v2` replaces `keep-made-plus-draw` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 2000 | 12.44 | 12.47 | +0.03 | ±0.13 | 0.644 | 139 / 1724 / 137 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~36.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **v0-baseline** | 4000 | 16000 | 12.55 | 0.28 | 4.46 | 38% | 13% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.385 | 36.38 | 0 |
| 2 | **keep-made-plus-draw-v2** | 2000 | 8000 | 12.47 | 0.39 | 4.47 | 38% | 12% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.577 | 30.77 | 0 |
| 3 | **keep-made-plus-draw** | 2000 | 8000 | 12.44 | 0.39 | 4.48 | 37% | 12% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.435 | 31.54 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| v0-baseline | 13% | 12% | 13% | 12% | 13% | 13% | 14% | 10% |
| keep-made-plus-draw-v2 | 12% | 13% | 12% | 12% | 13% | 13% | 14% | 10% |
| keep-made-plus-draw | 12% | 13% | 12% | 13% | 13% | 13% | 14% | 10% |

## Head-to-head (row finished above column: wins-ties-losses)

| | v0-baseline | keep-made-plus-draw-v2 | keep-made-plus-draw |
|---|---|---|---|
| **v0-baseline** | · | 1018-0-982 | 1009-0-991 |
| **keep-made-plus-draw-v2** | 982-0-1018 | · | 0-0-0 |
| **keep-made-plus-draw** | 991-0-1009 | 0-0-0 | · |

Files: `arena/results/20261106-191659-ab-keep-made-plus-draw-v2-vs-keep-made-plus-draw-6714` (tables.jsonl, seats.csv, summary.json, run.json).
