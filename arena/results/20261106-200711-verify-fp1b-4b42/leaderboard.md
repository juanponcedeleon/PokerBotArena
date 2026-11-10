# Arena run `verify-fp1b` — fast mode

Started 2026-11-06T20:07:11 · seed `fp1b` · scheme ab · 2004 tables · 253184 hands · 90.6 s

Command: `ab cap-floor-count-v6 fp-v1 --field v0-baseline check_or_fold arch-folder arch-shover arch-station --tables 1000 --seed fp1b --name verify-fp1b --agent Claude (headmaster) --question verify keep-rule agent's fp-v1 vs cap-floor-count-v6 result, same seed fp1b --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `fp-v1` replaces `cap-floor-count-v6` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 824 | 21.16 | 23.36 | +2.20 | ±1.60 | 0.007 | 299 / 317 / 208 | **fp-v1 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~2093.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-v1** | 824 | 1336 | 22.63 | 1.18 | 3.27 | 56% | 34% | 0.0001 | 13 | 0 | 0 | 0.036 | 19.232 | 87.39 | 0 |
| 2 | **cap-floor-count-v6** | 824 | 1336 | 20.43 | 1.20 | 3.47 | 49% | 32% | 0.0001 | 13 | 0 | 0 | 0.024 | 19.721 | 41.35 | 0 |
| 3 | **arch-folder** | 1670 | 2672 | 17.31 | 0.60 | 3.31 | 59% | 7% | 0.0000 | 0 | 0 | 0 | 0.015 | 12.857 | 51.30 | 0 |
| 4 | **v0-baseline** | 1686 | 2672 | 16.61 | 0.84 | 3.99 | 39% | 28% | 0.0000 | 1 | 0 | 0 | 0.024 | 17.017 | 46.91 | 0 |
| 5 | **check_or_fold** | 1688 | 2672 | 14.55 | 0.45 | 3.29 | 62% | 0% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.162 | 35.73 | 0 |
| 6 | **arch-shover** | 1646 | 2672 | 3.62 | 0.48 | 5.77 | 8% | 7% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.231 | 18.58 | 0 |
| 7 | **arch-station** | 1646 | 2672 | 1.38 | 0.25 | 5.87 | 5% | 1% | 0.0000 | 0 | 0 | 0 | 0.007 | 0.424 | 34.69 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-v1 | 34% | 14% | 8% | 10% | 13% | 13% | 7% | 1% |
| cap-floor-count-v6 | 32% | 9% | 8% | 13% | 16% | 14% | 7% | 1% |
| arch-folder | 7% | 35% | 18% | 16% | 14% | 8% | 2% | 0% |
| v0-baseline | 28% | 6% | 5% | 11% | 19% | 19% | 10% | 3% |
| check_or_fold | 0% | 21% | 41% | 27% | 9% | 1% | 0% | 0% |
| arch-shover | 7% | 0% | 1% | 6% | 20% | 29% | 27% | 10% |
| arch-station | 1% | 1% | 3% | 8% | 21% | 31% | 24% | 10% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-v1 | cap-floor-count-v6 | arch-folder | v0-baseline | check_or_fold | arch-shover | arch-station |
|---|---|---|---|---|---|---|---|
| **fp-v1** | · | 0-0-0 | 438-1-232 | 376-3-302 | 469-0-212 | 539-33-95 | 582-22-67 |
| **cap-floor-count-v6** | 0-0-0 | · | 406-0-265 | 370-1-310 | 422-0-259 | 571-12-84 | 619-9-43 |
| **arch-folder** | 232-1-438 | 265-0-406 | · | 654-0-726 | 887-0-495 | 1190-2-164 | 1258-5-83 |
| **v0-baseline** | 302-3-376 | 310-1-370 | 726-0-654 | · | 766-0-642 | 1087-47-228 | 1139-41-196 |
| **check_or_fold** | 212-0-469 | 259-0-422 | 495-0-887 | 642-0-766 | · | 1192-0-158 | 1322-0-36 |
| **arch-shover** | 95-33-539 | 84-12-571 | 164-2-1190 | 228-47-1087 | 158-0-1192 | · | 474-225-625 |
| **arch-station** | 67-22-582 | 43-9-619 | 83-5-1258 | 196-41-1139 | 36-0-1322 | 625-225-474 | · |

Files: `arena/results/20261106-200711-verify-fp1b-4b42` (tables.jsonl, seats.csv, summary.json, run.json).
