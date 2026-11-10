# Arena run `ab-nowar-keep-v2-vs-bot` — fast mode

Started 2026-11-06T19:34:46 · seed `s31g` · scheme ab · 4000 tables · 441749 hands · 79.8 s

Command: `ab bot nowar-keep-v2 --field v0-nowar --tables 2000 --seed s31g --agent Claude (keep-rule agent) --question nowar-keep-v2 vs bot (= v0-nowar), field = v0-nowar copies (self-play of the submission), 2000 pairs --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `nowar-keep-v2` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 2000 | 12.37 | 12.40 | +0.03 | ±0.23 | 0.793 | 405 / 1202 / 393 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~109.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **v0-nowar** | 4000 | 16000 | 12.61 | 0.28 | 4.48 | 38% | 13% | 0.0000 | 0 | 0 | 0 | 0.015 | 0.214 | 61.92 | 0 |
| 2 | **nowar-keep-v2** | 2000 | 8000 | 12.40 | 0.39 | 4.50 | 37% | 12% | 0.0000 | 1 | 0 | 0 | 0.015 | 0.304 | 147.51 | 0 |
| 3 | **bot** | 2000 | 8000 | 12.37 | 0.39 | 4.51 | 37% | 12% | 0.0000 | 0 | 0 | 0 | 0.015 | 0.197 | 67.40 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| v0-nowar | 13% | 12% | 13% | 12% | 13% | 13% | 13% | 12% |
| nowar-keep-v2 | 12% | 13% | 13% | 13% | 13% | 12% | 13% | 12% |
| bot | 12% | 13% | 12% | 13% | 12% | 12% | 13% | 12% |

## Head-to-head (row finished above column: wins-ties-losses)

| | v0-nowar | nowar-keep-v2 | bot |
|---|---|---|---|
| **v0-nowar** | · | 1017-0-983 | 1014-0-986 |
| **nowar-keep-v2** | 983-0-1017 | · | 0-0-0 |
| **bot** | 986-0-1014 | 0-0-0 | · |

Files: `arena/results/20261106-193446-ab-nowar-keep-v2-vs-bot-6f60` (tables.jsonl, seats.csv, summary.json, run.json).
