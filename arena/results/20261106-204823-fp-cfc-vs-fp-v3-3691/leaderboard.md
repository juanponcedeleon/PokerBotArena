# Arena run `fp-cfc-vs-fp-v3` — fast mode

Started 2026-11-06T20:48:23 · seed `fpcfc1` · scheme ab · 3206 tables · 414071 hands · 150.3 s

Command: `ab bots/fp-v3 bots/fp-cfc --field v0-baseline check_or_fold arch-folder arch-shover arch-station cap-floor-count-v6 --tables 1600 --seed fpcfc1 --agent Claude(cap-floor-count-agent) --name fp-cfc-vs-fp-v3 --question end-all hybrid: fp-v3 preflop/select/ICM + cap-floor-count-v6 postflop vs fp-v3 (archetype field)`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `fp-cfc` replaces `fp-v3` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 1148 | 22.15 | 21.39 | -0.75 | ±1.00 | 0.139 | 278 / 551 / 319 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~1141.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-v3** | 1148 | 1832 | 21.52 | 0.95 | 3.26 | 58% | 27% | 0.0001 | 20 | 0 | 0 | 0.035 | 18.330 | 178.26 | 0 |
| 2 | **fp-cfc** | 1148 | 1832 | 20.59 | 0.97 | 3.33 | 53% | 28% | 0.0003 | 52 | 0 | 0 | 0.035 | 19.432 | 175.58 | 0 |
| 3 | **cap-floor-count-v6** | 2350 | 3664 | 18.40 | 0.70 | 3.70 | 46% | 26% | 0.0001 | 52 | 0 | 0 | 0.022 | 19.583 | 227.41 | 0 |
| 4 | **arch-folder** | 2348 | 3664 | 16.42 | 0.51 | 3.46 | 57% | 6% | 0.0000 | 10 | 0 | 0 | 0.015 | 12.073 | 158.17 | 0 |
| 5 | **v0-baseline** | 2316 | 3664 | 14.17 | 0.68 | 4.32 | 34% | 23% | 0.0001 | 29 | 0 | 0 | 0.023 | 16.487 | 245.64 | 0 |
| 6 | **check_or_fold** | 2342 | 3664 | 13.80 | 0.38 | 3.34 | 60% | 0% | 0.0000 | 2 | 0 | 0 | 0.005 | 0.144 | 139.48 | 0 |
| 7 | **arch-shover** | 2336 | 3664 | 2.69 | 0.35 | 6.09 | 6% | 5% | 0.0000 | 1 | 0 | 0 | 0.004 | 0.459 | 145.54 | 0 |
| 8 | **arch-station** | 2392 | 3664 | 0.97 | 0.18 | 6.20 | 4% | 1% | 0.0000 | 2 | 0 | 0 | 0.007 | 0.825 | 129.10 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-v3 | 27% | 20% | 12% | 11% | 14% | 11% | 5% | 1% |
| fp-cfc | 28% | 16% | 10% | 14% | 14% | 12% | 5% | 1% |
| cap-floor-count-v6 | 26% | 12% | 8% | 12% | 16% | 14% | 8% | 3% |
| arch-folder | 6% | 33% | 18% | 15% | 14% | 10% | 4% | 1% |
| v0-baseline | 23% | 6% | 6% | 10% | 18% | 19% | 15% | 4% |
| check_or_fold | 0% | 19% | 41% | 30% | 9% | 1% | 0% | 0% |
| arch-shover | 5% | 0% | 1% | 4% | 15% | 29% | 29% | 17% |
| arch-station | 1% | 1% | 2% | 6% | 17% | 28% | 29% | 17% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-v3 | fp-cfc | cap-floor-count-v6 | arch-folder | v0-baseline | check_or_fold | arch-shover | arch-station |
|---|---|---|---|---|---|---|---|---|
| **fp-v3** | · | 0-0-0 | 428-1-377 | 538-0-281 | 467-2-326 | 561-0-250 | 740-10-63 | 763-4-53 |
| **fp-cfc** | 0-0-0 | · | 434-1-371 | 511-0-308 | 461-2-332 | 542-0-269 | 736-10-67 | 787-3-30 |
| **cap-floor-count-v6** | 377-1-428 | 371-1-434 | · | 898-0-774 | 906-6-714 | 943-0-717 | 1422-22-188 | 1598-14-96 |
| **arch-folder** | 281-0-538 | 308-0-511 | 774-0-898 | · | 913-0-721 | 986-0-652 | 1510-0-150 | 1636-0-76 |
| **v0-baseline** | 326-2-467 | 332-2-461 | 714-6-906 | 721-0-913 | · | 786-0-850 | 1347-47-258 | 1418-51-239 |
| **check_or_fold** | 250-0-561 | 269-0-542 | 717-0-943 | 652-0-986 | 850-0-786 | · | 1522-0-130 | 1685-0-29 |
| **arch-shover** | 63-10-740 | 67-10-736 | 188-22-1422 | 150-0-1510 | 258-47-1347 | 130-0-1522 | · | 624-248-808 |
| **arch-station** | 53-4-763 | 30-3-787 | 96-14-1598 | 76-0-1636 | 239-51-1418 | 29-0-1685 | 808-248-624 | · |

Files: `arena/results/20261106-204823-fp-cfc-vs-fp-v3-3691` (tables.jsonl, seats.csv, summary.json, run.json).
