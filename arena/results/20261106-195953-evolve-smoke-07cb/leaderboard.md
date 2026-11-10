# Arena run `evolve-smoke` — fast mode

Started 2026-11-06T19:59:53 · seed `smoke:test` · scheme ab · 32 tables · 3144 hands · 6.4 s

Command: ``

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `v0-nowar-evo-smoke` replaces `v0-nowar` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 16 | 12.19 | 12.19 | +0.00 | ±0.00 | - | 0 / 16 / 0 | no significant difference |

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 32 | 64 | 21.25 | 2.33 | 2.75 | 88% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.031 | 9.28 | 0 |
| 2 | **v0-baseline** | 32 | 64 | 13.44 | 5.47 | 4.16 | 28% | 25% | 0.0000 | 0 | 0 | 0 | 0.017 | 9.944 | 12.26 | 0 |
| 3 | **v0-nowar** | 16 | 32 | 12.19 | 7.37 | 4.22 | 28% | 19% | 0.0000 | 0 | 0 | 0 | 0.019 | 7.953 | 14.33 | 0 |
| 4 | **v0-nowar-evo-smoke** | 16 | 32 | 12.19 | 7.37 | 4.22 | 28% | 19% | 0.0000 | 0 | 0 | 0 | 0.019 | 8.164 | 9.54 | 0 |
| 5 | **min_raiser** | 32 | 64 | 3.12 | 3.05 | 6.09 | 6% | 6% | 0.0000 | 0 | 0 | 0 | 0.004 | 8.116 | 9.80 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 38% | 50% | 12% | 0% | 0% | 0% | 0% |
| v0-baseline | 25% | 3% | 0% | 19% | 22% | 19% | 12% | 0% |
| v0-nowar | 19% | 9% | 0% | 12% | 28% | 25% | 6% | 0% |
| v0-nowar-evo-smoke | 19% | 9% | 0% | 12% | 28% | 25% | 6% | 0% |
| min_raiser | 6% | 0% | 0% | 6% | 9% | 28% | 38% | 12% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | v0-baseline | v0-nowar | v0-nowar-evo-smoke | min_raiser |
|---|---|---|---|---|---|
| **check_or_fold** | · | 14-0-18 | 7-0-9 | 7-0-9 | 28-0-4 |
| **v0-baseline** | 18-0-14 | · | 9-0-7 | 9-0-7 | 22-0-10 |
| **v0-nowar** | 9-0-7 | 7-0-9 | · | 0-0-0 | 14-0-2 |
| **v0-nowar-evo-smoke** | 9-0-7 | 7-0-9 | 0-0-0 | · | 14-0-2 |
| **min_raiser** | 4-0-28 | 10-0-22 | 2-0-14 | 2-0-14 | · |

Files: `arena/results/20261106-195953-evolve-smoke-07cb` (tables.jsonl, seats.csv, summary.json, run.json).
