# Arena run `ab-fp-v1-vs-bot` — fast mode

Started 2026-11-06T19:59:30 · seed `fp1a` · scheme ab · 2004 tables · 254964 hands · 33.9 s

Command: `ab bot fp-v1 --field v0-baseline check_or_fold arch-folder arch-shover arch-station --tables 1000 --seed fp1a --agent Claude (keep-rule agent, branching out) --question fp-v1 (first-principles bot) vs bot (v0-nowar) in a realistic archetype field --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `fp-v1` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 818 | 21.47 | 23.83 | +2.37 | ±1.49 | 0.002 | 283 / 337 / 198 | **fp-v1 is better** |

Pairs needed to resolve a 1-point difference at this variance: ~1808.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-v1** | 818 | 1336 | 22.99 | 1.17 | 3.22 | 58% | 33% | 0.0000 | 0 | 0 | 0 | 0.025 | 0.355 | 49.91 | 0 |
| 2 | **bot** | 818 | 1336 | 20.33 | 1.20 | 3.47 | 49% | 32% | 0.0000 | 1 | 0 | 0 | 0.016 | 0.777 | 46.00 | 0 |
| 3 | **arch-folder** | 1642 | 2672 | 17.49 | 0.62 | 3.30 | 59% | 8% | 0.0000 | 0 | 0 | 0 | 0.011 | 0.128 | 17.54 | 0 |
| 4 | **v0-baseline** | 1676 | 2672 | 16.72 | 0.84 | 3.97 | 39% | 28% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.183 | 41.57 | 0 |
| 5 | **check_or_fold** | 1650 | 2672 | 14.42 | 0.46 | 3.29 | 62% | 0% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.035 | 14.66 | 0 |
| 6 | **arch-shover** | 1638 | 2672 | 3.42 | 0.47 | 5.76 | 8% | 7% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.060 | 8.31 | 0 |
| 7 | **arch-station** | 1666 | 2672 | 1.28 | 0.22 | 5.89 | 5% | 0% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.070 | 23.27 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-v1 | 33% | 16% | 9% | 9% | 13% | 14% | 5% | 1% |
| bot | 32% | 10% | 7% | 13% | 16% | 15% | 6% | 1% |
| arch-folder | 8% | 34% | 17% | 16% | 15% | 8% | 2% | 0% |
| v0-baseline | 28% | 6% | 6% | 10% | 19% | 18% | 11% | 2% |
| check_or_fold | 0% | 21% | 40% | 28% | 8% | 2% | 0% | 0% |
| arch-shover | 7% | 0% | 1% | 7% | 19% | 31% | 23% | 12% |
| arch-station | 0% | 1% | 4% | 9% | 20% | 32% | 24% | 11% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-v1 | bot | arch-folder | v0-baseline | check_or_fold | arch-shover | arch-station |
|---|---|---|---|---|---|---|---|
| **fp-v1** | · | 0-0-0 | 436-1-208 | 370-0-307 | 473-0-191 | 555-34-71 | 585-19-59 |
| **bot** | 0-0-0 | · | 382-0-263 | 367-0-310 | 412-0-252 | 577-13-70 | 613-6-44 |
| **arch-folder** | 208-1-436 | 263-0-382 | · | 618-2-724 | 860-0-480 | 1157-4-153 | 1255-4-73 |
| **v0-baseline** | 307-0-370 | 310-0-367 | 724-2-618 | · | 736-0-620 | 1095-46-203 | 1166-32-182 |
| **check_or_fold** | 191-0-473 | 252-0-412 | 480-0-860 | 620-0-736 | · | 1154-0-154 | 1318-0-26 |
| **arch-shover** | 71-34-555 | 70-13-577 | 153-4-1157 | 203-46-1095 | 154-0-1154 | · | 472-227-635 |
| **arch-station** | 59-19-585 | 44-6-613 | 73-4-1255 | 182-32-1166 | 26-0-1318 | 635-227-472 | · |

Files: `arena/results/20261106-195930-ab-fp-v1-vs-bot-e9f0` (tables.jsonl, seats.csv, summary.json, run.json).
