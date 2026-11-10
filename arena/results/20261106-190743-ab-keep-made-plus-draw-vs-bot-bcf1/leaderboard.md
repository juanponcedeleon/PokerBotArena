# Arena run `ab-keep-made-plus-draw-vs-bot` — fast mode

Started 2026-11-06T19:07:43 · seed `s31c` · scheme ab · 4000 tables · 215293 hands · 48.4 s

Command: `ab bot keep-made-plus-draw --field v0-baseline --tables 2000 --seed s31c --agent Claude (keep-rule agent) --question S3.1 keep rule vs bot v0, flop-heavy field (v0-baseline), 2000 pairs for power --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `keep-made-plus-draw` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 2000 | 12.41 | 12.58 | +0.16 | ±0.14 | 0.022 | 183 / 1663 / 154 | **keep-made-plus-draw is better** |

Pairs needed to resolve a 1-point difference at this variance: ~40.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **keep-made-plus-draw** | 2000 | 8000 | 12.58 | 0.39 | 4.45 | 38% | 13% | 0.0000 | 0 | 0 | 0 | 0.021 | 0.468 | 31.89 | 0 |
| 2 | **v0-baseline** | 4000 | 16000 | 12.51 | 0.28 | 4.48 | 38% | 12% | 0.0000 | 0 | 0 | 0 | 0.020 | 0.505 | 44.65 | 0 |
| 3 | **bot** | 2000 | 8000 | 12.41 | 0.39 | 4.46 | 37% | 13% | 0.0000 | 0 | 0 | 0 | 0.020 | 0.492 | 52.06 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| keep-made-plus-draw | 13% | 12% | 13% | 13% | 13% | 13% | 13% | 10% |
| v0-baseline | 12% | 13% | 12% | 12% | 12% | 13% | 14% | 11% |
| bot | 13% | 12% | 13% | 13% | 13% | 13% | 13% | 10% |

## Head-to-head (row finished above column: wins-ties-losses)

| | keep-made-plus-draw | v0-baseline | bot |
|---|---|---|---|
| **keep-made-plus-draw** | · | 1019-0-981 | 0-0-0 |
| **v0-baseline** | 981-0-1019 | · | 997-0-1003 |
| **bot** | 0-0-0 | 1003-0-997 | · |

Files: `arena/results/20261106-190743-ab-keep-made-plus-draw-vs-bot-bcf1` (tables.jsonl, seats.csv, summary.json, run.json).
