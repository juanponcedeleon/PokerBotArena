# Arena run `ab-fp-v1-vs-cap-floor-count-v6` — fast mode

Started 2026-11-06T20:02:17 · seed `fp1d` · scheme ab · 2000 tables · 274035 hands · 63.6 s

Command: `ab cap-floor-count-v6 fp-v1 --field v0-nowar cap-floor-count-v5 arch-folder --tables 1000 --seed fp1d --agent Claude (keep-rule agent, branching out) --question fp-v1 vs cap-floor-count-v6 in a strong field (v0-nowar, cfc-v5, arch-folder copies), robustness --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `fp-v1` replaces `cap-floor-count-v6` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1000 | 12.54 | 16.67 | +4.13 | ±1.06 | 0.000 | 470 / 245 / 285 | **fp-v1 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~1124.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-v1** | 1000 | 2000 | 16.67 | 0.85 | 3.84 | 48% | 18% | 0.0000 | 3 | 0 | 0 | 0.029 | 10.979 | 591.50 | 0 |
| 2 | **arch-folder** | 2000 | 4000 | 14.19 | 0.47 | 3.87 | 52% | 4% | 0.0000 | 1 | 0 | 0 | 0.012 | 0.797 | 245.19 | 0 |
| 3 | **cap-floor-count-v6** | 1000 | 2000 | 12.54 | 0.83 | 4.56 | 34% | 16% | 0.0000 | 0 | 0 | 0 | 0.018 | 11.872 | 52.72 | 0 |
| 4 | **cap-floor-count-v5** | 2000 | 4000 | 10.85 | 0.57 | 4.92 | 29% | 15% | 0.0000 | 2 | 0 | 0 | 0.019 | 12.006 | 136.78 | 0 |
| 5 | **v0-nowar** | 2000 | 4000 | 10.37 | 0.56 | 5.00 | 28% | 14% | 0.0000 | 0 | 0 | 0 | 0.019 | 10.112 | 49.99 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-v1 | 18% | 15% | 14% | 14% | 14% | 9% | 8% | 7% |
| arch-folder | 4% | 26% | 21% | 16% | 11% | 9% | 8% | 5% |
| cap-floor-count-v6 | 16% | 9% | 9% | 12% | 14% | 14% | 14% | 12% |
| cap-floor-count-v5 | 15% | 6% | 9% | 11% | 13% | 15% | 15% | 17% |
| v0-nowar | 14% | 6% | 8% | 11% | 12% | 15% | 17% | 17% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-v1 | arch-folder | cap-floor-count-v6 | cap-floor-count-v5 | v0-nowar |
|---|---|---|---|---|---|
| **fp-v1** | · | 638-0-362 | 0-0-0 | 628-0-372 | 620-0-380 |
| **arch-folder** | 362-0-638 | · | 513-0-487 | 1139-0-861 | 1168-0-832 |
| **cap-floor-count-v6** | 0-0-0 | 487-0-513 | · | 536-0-464 | 533-1-466 |
| **cap-floor-count-v5** | 372-0-628 | 861-0-1139 | 464-0-536 | · | 1027-0-973 |
| **v0-nowar** | 380-0-620 | 832-0-1168 | 466-1-533 | 973-0-1027 | · |

Files: `arena/results/20261106-200217-ab-fp-v1-vs-cap-floor-count-v6-82dc` (tables.jsonl, seats.csv, summary.json, run.json).
