# Arena run `ab-keep-made-plus-draw-vs-bot` — fast mode

Started 2026-11-06T19:05:18 · seed `s31a` · scheme ab · 804 tables · 76810 hands · 18.5 s

Command: `ab bot keep-made-plus-draw --tables 400 --seed s31a --agent Claude (keep-rule agent) --question S3.1 keep rule (made hand + draw bonus) vs bot v0 (made hand only), field min_raiser + check_or_fold --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `keep-made-plus-draw` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 394 | 17.14 | 17.11 | -0.02 | ±0.28 | 0.873 | 5 / 379 / 10 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~30.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 788 | 2144 | 17.36 | 0.53 | 3.08 | 69% | 0% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.092 | 16.72 | 0 |
| 2 | **bot** | 394 | 1072 | 15.91 | 1.36 | 4.02 | 35% | 30% | 0.0000 | 0 | 0 | 0 | 0.023 | 0.964 | 22.35 | 0 |
| 3 | **keep-made-plus-draw** | 394 | 1072 | 15.87 | 1.36 | 4.02 | 35% | 30% | 0.0000 | 0 | 0 | 0 | 0.023 | 0.587 | 30.23 | 0 |
| 4 | **min_raiser** | 794 | 2144 | 4.25 | 0.58 | 5.40 | 10% | 8% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.152 | 49.37 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 36% | 33% | 21% | 8% | 2% | 0% | 0% |
| bot | 30% | 1% | 4% | 13% | 21% | 20% | 10% | 2% |
| keep-made-plus-draw | 30% | 1% | 4% | 13% | 21% | 19% | 10% | 1% |
| min_raiser | 8% | 0% | 2% | 10% | 26% | 27% | 21% | 6% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | bot | keep-made-plus-draw | min_raiser |
|---|---|---|---|---|
| **check_or_fold** | · | 76-0-310 | 76-0-310 | 610-0-168 |
| **bot** | 310-0-76 | · | 0-0-0 | 312-0-77 |
| **keep-made-plus-draw** | 310-0-76 | 0-0-0 | · | 312-0-77 |
| **min_raiser** | 168-0-610 | 77-0-312 | 77-0-312 | · |

Files: `arena/results/20261106-190518-ab-keep-made-plus-draw-vs-bot-08eb` (tables.jsonl, seats.csv, summary.json, run.json).
