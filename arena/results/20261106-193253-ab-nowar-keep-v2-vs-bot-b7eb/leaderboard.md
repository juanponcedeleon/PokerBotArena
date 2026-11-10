# Arena run `ab-nowar-keep-v2-vs-bot` — fast mode

Started 2026-11-06T19:32:53 · seed `s31f` · scheme ab · 4000 tables · 349969 hands · 73.5 s

Command: `ab bot nowar-keep-v2 --field v0-baseline --tables 2000 --seed s31f --agent Claude (keep-rule agent) --question nowar-keep-v2 (v0-nowar + keep v2 select) vs bot (= v0-nowar), flop-heavy field v0-baseline, 2000 pairs (headmaster request) --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `nowar-keep-v2` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 2000 | 14.93 | 14.95 | +0.02 | ±0.18 | 0.802 | 297 / 1408 / 295 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~63.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **nowar-keep-v2** | 2000 | 8000 | 14.95 | 0.40 | 3.95 | 46% | 14% | 0.0000 | 4 | 0 | 0 | 0.016 | 1.796 | 49.01 | 0 |
| 2 | **bot** | 2000 | 8000 | 14.93 | 0.40 | 3.95 | 46% | 14% | 0.0000 | 2 | 0 | 0 | 0.016 | 0.822 | 52.10 | 0 |
| 3 | **v0-baseline** | 4000 | 16000 | 10.06 | 0.27 | 5.02 | 29% | 11% | 0.0000 | 0 | 0 | 0 | 0.016 | 0.749 | 46.41 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| nowar-keep-v2 | 14% | 16% | 16% | 15% | 13% | 11% | 8% | 6% |
| bot | 14% | 16% | 16% | 15% | 13% | 11% | 8% | 6% |
| v0-baseline | 11% | 9% | 9% | 10% | 12% | 14% | 18% | 17% |

## Head-to-head (row finished above column: wins-ties-losses)

| | nowar-keep-v2 | bot | v0-baseline |
|---|---|---|---|
| **nowar-keep-v2** | · | 0-0-0 | 1082-0-918 |
| **bot** | 0-0-0 | · | 1088-0-912 |
| **v0-baseline** | 918-0-1082 | 912-0-1088 | · |

Files: `arena/results/20261106-193253-ab-nowar-keep-v2-vs-bot-b7eb` (tables.jsonl, seats.csv, summary.json, run.json).
