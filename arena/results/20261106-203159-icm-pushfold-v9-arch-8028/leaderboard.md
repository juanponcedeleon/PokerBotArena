# Arena run `icm-pushfold-v9-arch` — fast mode

Started 2026-11-06T20:31:59 · seed `icm6` · scheme ab · 804 tables · 103904 hands · 53.5 s

Command: `ab bot bots/icm-pushfold-v9 --field v0-baseline check_or_fold arch-folder arch-shover arch-station --tables 400 --seed icm6 --name icm-pushfold-v9-arch --agent Claude (icm-pushfold agent) --question v9 vs bot (cap-floor-count-v6) in the archetype field --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `icm-pushfold-v9` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 331 | 22.54 | 20.69 | -1.85 | ±2.22 | 0.103 | 89 / 128 / 114 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~1626.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **bot** | 331 | 536 | 21.39 | 1.83 | 3.38 | 54% | 30% | 0.0002 | 11 | 0 | 0 | 0.029 | 0.392 | 140.37 | 0 |
| 2 | **icm-pushfold-v9** | 331 | 536 | 20.09 | 1.82 | 3.49 | 52% | 28% | 0.0011 | 68 | 0 | 0 | 0.076 | 15.574 | 181.42 | 164 |
| 3 | **arch-folder** | 684 | 1072 | 18.51 | 0.97 | 3.20 | 62% | 9% | 0.0001 | 19 | 0 | 0 | 0.012 | 0.128 | 156.81 | 0 |
| 4 | **v0-baseline** | 682 | 1072 | 17.04 | 1.35 | 3.97 | 39% | 29% | 0.0002 | 21 | 0 | 0 | 0.020 | 0.256 | 161.80 | 0 |
| 5 | **check_or_fold** | 664 | 1072 | 13.80 | 0.73 | 3.34 | 59% | 0% | 0.0000 | 4 | 0 | 0 | 0.004 | 0.020 | 167.59 | 0 |
| 6 | **arch-shover** | 684 | 1072 | 3.76 | 0.78 | 5.73 | 8% | 7% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.032 | 1.49 | 0 |
| 7 | **arch-station** | 678 | 1072 | 1.16 | 0.36 | 5.94 | 4% | 1% | 0.0001 | 4 | 0 | 0 | 0.006 | 0.052 | 145.33 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| bot | 30% | 17% | 8% | 9% | 14% | 13% | 8% | 1% |
| icm-pushfold-v9 | 28% | 12% | 12% | 10% | 14% | 15% | 7% | 1% |
| arch-folder | 9% | 34% | 19% | 14% | 15% | 7% | 2% | 0% |
| v0-baseline | 29% | 5% | 5% | 9% | 20% | 19% | 10% | 2% |
| check_or_fold | 0% | 21% | 38% | 30% | 9% | 2% | 0% | 0% |
| arch-shover | 7% | 0% | 1% | 7% | 18% | 31% | 26% | 10% |
| arch-station | 1% | 1% | 2% | 11% | 17% | 31% | 27% | 10% |

## Head-to-head (row finished above column: wins-ties-losses)

| | bot | icm-pushfold-v9 | arch-folder | v0-baseline | check_or_fold | arch-shover | arch-station |
|---|---|---|---|---|---|---|---|
| **bot** | · | 0-0-0 | 175-0-103 | 143-0-130 | 187-0-78 | 220-17-38 | 229-10-31 |
| **icm-pushfold-v9** | 0-0-0 | · | 155-0-123 | 146-0-127 | 177-0-88 | 234-10-31 | 242-6-22 |
| **arch-folder** | 103-0-175 | 123-0-155 | · | 272-0-298 | 361-0-195 | 506-0-70 | 544-0-26 |
| **v0-baseline** | 130-0-143 | 127-0-146 | 298-0-272 | · | 312-0-242 | 450-9-113 | 475-13-82 |
| **check_or_fold** | 78-0-187 | 88-0-177 | 195-0-361 | 242-0-312 | · | 487-0-69 | 543-0-7 |
| **arch-shover** | 38-17-220 | 31-10-234 | 70-0-506 | 113-9-450 | 69-0-487 | · | 234-78-264 |
| **arch-station** | 31-10-229 | 22-6-242 | 26-0-544 | 82-13-475 | 7-0-543 | 264-78-234 | · |

Files: `arena/results/20261106-203159-icm-pushfold-v9-arch-8028` (tables.jsonl, seats.csv, summary.json, run.json).
