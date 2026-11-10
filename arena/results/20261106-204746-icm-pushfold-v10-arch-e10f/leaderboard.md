# Arena run `icm-pushfold-v10-arch` — fast mode

Started 2026-11-06T20:47:46 · seed `icm7` · scheme ab · 804 tables · 108981 hands · 35.4 s

Command: `ab bot bots/icm-pushfold-v10 --field v0-baseline check_or_fold arch-folder arch-shover arch-station --tables 400 --seed icm7 --name icm-pushfold-v10-arch --agent Claude (icm-pushfold agent) --question v10 = fp-v3 (bot/) + ICM short-stack module, archetype field --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `icm-pushfold-v10` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 328 | 23.87 | 22.90 | -0.97 | ±1.04 | 0.068 | 43 / 221 / 64 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~355.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **bot** | 328 | 536 | 22.88 | 1.80 | 3.18 | 59% | 31% | 0.0000 | 0 | 0 | 0 | 0.037 | 11.058 | 30.38 | 0 |
| 2 | **icm-pushfold-v10** | 328 | 536 | 22.00 | 1.68 | 3.19 | 62% | 24% | 0.0003 | 18 | 0 | 0 | 0.107 | 13.358 | 52.02 | 164 |
| 3 | **arch-folder** | 658 | 1072 | 18.12 | 1.04 | 3.30 | 58% | 12% | 0.0000 | 0 | 0 | 0 | 0.016 | 7.862 | 25.82 | 0 |
| 4 | **v0-baseline** | 650 | 1072 | 16.43 | 1.33 | 4.02 | 38% | 28% | 0.0000 | 0 | 0 | 0 | 0.025 | 10.280 | 53.36 | 0 |
| 5 | **check_or_fold** | 660 | 1072 | 13.11 | 0.72 | 3.42 | 57% | 0% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.322 | 27.59 | 0 |
| 6 | **arch-shover** | 638 | 1072 | 3.74 | 0.77 | 5.83 | 9% | 7% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.175 | 21.17 | 0 |
| 7 | **arch-station** | 670 | 1072 | 1.16 | 0.37 | 5.93 | 5% | 1% | 0.0000 | 0 | 0 | 0 | 0.007 | 0.327 | 26.78 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| bot | 31% | 19% | 10% | 10% | 13% | 10% | 6% | 1% |
| icm-pushfold-v10 | 24% | 23% | 15% | 10% | 11% | 10% | 6% | 1% |
| arch-folder | 12% | 30% | 17% | 17% | 13% | 8% | 3% | 1% |
| v0-baseline | 28% | 5% | 5% | 9% | 21% | 19% | 11% | 2% |
| check_or_fold | 0% | 18% | 39% | 30% | 11% | 2% | 0% | 0% |
| arch-shover | 7% | 0% | 2% | 5% | 15% | 32% | 28% | 11% |
| arch-station | 1% | 0% | 3% | 8% | 20% | 31% | 25% | 10% |

## Head-to-head (row finished above column: wins-ties-losses)

| | bot | icm-pushfold-v10 | arch-folder | v0-baseline | check_or_fold | arch-shover | arch-station |
|---|---|---|---|---|---|---|---|
| **bot** | · | 0-0-0 | 178-0-84 | 140-0-121 | 187-0-76 | 229-3-29 | 243-2-22 |
| **icm-pushfold-v10** | 0-0-0 | · | 147-0-115 | 130-0-131 | 195-0-68 | 228-3-30 | 245-2-20 |
| **arch-folder** | 84-0-178 | 115-0-147 | · | 250-2-272 | 341-0-185 | 440-0-66 | 510-0-30 |
| **v0-baseline** | 121-0-140 | 131-0-130 | 272-2-250 | · | 288-0-232 | 410-18-78 | 420-22-90 |
| **check_or_fold** | 76-0-187 | 68-0-195 | 185-0-341 | 232-0-288 | · | 441-0-71 | 534-0-10 |
| **arch-shover** | 29-3-229 | 30-3-228 | 66-0-440 | 78-18-410 | 71-0-441 | · | 204-60-256 |
| **arch-station** | 22-2-243 | 20-2-245 | 30-0-510 | 90-22-420 | 10-0-534 | 256-60-204 | · |

Files: `arena/results/20261106-204746-icm-pushfold-v10-arch-e10f` (tables.jsonl, seats.csv, summary.json, run.json).
