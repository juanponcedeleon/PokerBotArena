# Arena run `decide-v9-vs-fp2` — fast mode

Started 2026-11-06T20:30:10 · seed `decide1` · scheme ab · 2004 tables · 263589 hands · 104.7 s

Command: `ab bots/icm-pushfold-v9 bots/fp-v2 --field v0-baseline check_or_fold arch-folder arch-shover arch-station --tables 1000 --seed decide1 --name decide-v9-vs-fp2 --agent Claude (icm-pushfold agent) --question Deciding experiment (README #0): fp-v2 replaces icm-pushfold-v9 in the archetype field --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `fp-v2` replaces `icm-pushfold-v9` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 819 | 19.80 | 24.10 | +4.29 | ±1.45 | 0.000 | 329 / 289 / 201 | **fp-v2 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~1725.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-v2** | 819 | 1336 | 23.08 | 1.17 | 3.20 | 58% | 33% | 0.0000 | 5 | 0 | 0 | 0.032 | 18.174 | 276.57 | 0 |
| 2 | **icm-pushfold-v9** | 819 | 1336 | 19.46 | 1.11 | 3.44 | 53% | 24% | 0.0005 | 79 | 0 | 0 | 0.085 | 19.702 | 291.97 | 164 |
| 3 | **arch-folder** | 1634 | 2672 | 18.15 | 0.62 | 3.28 | 61% | 9% | 0.0000 | 4 | 0 | 0 | 0.013 | 0.377 | 246.54 | 0 |
| 4 | **v0-baseline** | 1664 | 2672 | 17.18 | 0.85 | 4.01 | 39% | 29% | 0.0000 | 12 | 0 | 0 | 0.021 | 10.173 | 266.48 | 0 |
| 5 | **check_or_fold** | 1642 | 2672 | 13.48 | 0.46 | 3.36 | 58% | 0% | 0.0000 | 2 | 0 | 0 | 0.004 | 0.053 | 203.52 | 0 |
| 6 | **arch-shover** | 1642 | 2672 | 3.77 | 0.49 | 5.75 | 9% | 7% | 0.0000 | 1 | 0 | 0 | 0.003 | 0.122 | 156.14 | 0 |
| 7 | **arch-station** | 1638 | 2672 | 1.14 | 0.22 | 5.85 | 5% | 1% | 0.0000 | 1 | 0 | 0 | 0.006 | 0.103 | 242.09 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-v2 | 33% | 16% | 8% | 9% | 15% | 13% | 5% | 1% |
| icm-pushfold-v9 | 24% | 17% | 12% | 12% | 15% | 13% | 6% | 1% |
| arch-folder | 9% | 32% | 19% | 15% | 14% | 8% | 2% | 1% |
| v0-baseline | 29% | 6% | 4% | 10% | 16% | 20% | 11% | 4% |
| check_or_fold | 0% | 20% | 38% | 31% | 10% | 2% | 0% | 0% |
| arch-shover | 7% | 0% | 1% | 7% | 18% | 30% | 25% | 11% |
| arch-station | 1% | 1% | 3% | 10% | 22% | 31% | 23% | 10% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-v2 | icm-pushfold-v9 | arch-folder | v0-baseline | check_or_fold | arch-shover | arch-station |
|---|---|---|---|---|---|---|---|
| **fp-v2** | · | 0-0-0 | 445-0-205 | 367-4-293 | 482-0-179 | 549-18-90 | 580-23-52 |
| **icm-pushfold-v9** | 0-0-0 | · | 304-0-346 | 335-0-329 | 407-1-253 | 566-10-81 | 605-11-39 |
| **arch-folder** | 205-0-445 | 346-0-304 | · | 589-0-753 | 879-0-427 | 1150-0-160 | 1263-0-51 |
| **v0-baseline** | 293-4-367 | 329-0-335 | 753-0-589 | · | 774-0-576 | 1065-27-240 | 1111-51-166 |
| **check_or_fold** | 179-0-482 | 253-1-407 | 427-0-879 | 576-0-774 | · | 1161-0-155 | 1296-0-20 |
| **arch-shover** | 90-18-549 | 81-10-566 | 160-0-1150 | 240-27-1065 | 155-0-1161 | · | 493-204-627 |
| **arch-station** | 52-23-580 | 39-11-605 | 51-0-1263 | 166-51-1111 | 20-0-1296 | 627-204-493 | · |

Files: `arena/results/20261106-203010-decide-v9-vs-fp2-0156` (tables.jsonl, seats.csv, summary.json, run.json).
