# Arena run `nowar-ab-pool` — fast mode

Started 2026-11-06T19:21:19 · seed `cfc3` · scheme ab · 800 tables · 52714 hands · 10.9 s

Command: `ab bot bots/v0-nowar --all --tables 400 --seed cfc3 --agent Claude(cap-floor-count-agent) --name nowar-ab-pool --question Does capping the preflop 3-bet escalation alone beat bot v0 (pool field)?`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `v0-nowar` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 400 | 12.15 | 17.48 | +5.33 | ±2.02 | 0.000 | 132 / 215 / 53 | **v0-nowar is better** |

Pairs needed to resolve a 1-point difference at this variance: ~1625.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **v0-nowar** | 400 | 400 | 17.48 | 1.87 | 3.73 | 52% | 18% | 0.0000 | 0 | 0 | 0 | 0.019 | 0.280 | 10.99 | 0 |
| 2 | **cap-floor-count-v3** | 800 | 800 | 14.12 | 1.18 | 3.89 | 47% | 10% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.747 | 11.57 | 0 |
| 3 | **keep-made-plus-draw** | 800 | 800 | 13.65 | 1.33 | 4.50 | 38% | 16% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.415 | 7.04 | 0 |
| 4 | **keep-made-plus-draw-v2** | 800 | 800 | 12.28 | 1.26 | 4.63 | 36% | 14% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.467 | 4.44 | 0 |
| 5 | **bot** | 400 | 400 | 12.15 | 1.78 | 4.59 | 35% | 13% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.252 | 3.62 | 0 |
| 6 | **icm-pushfold** | 800 | 800 | 11.76 | 1.18 | 4.54 | 37% | 10% | 0.0000 | 0 | 0 | 0 | 0.031 | 1.339 | 8.79 | 0 |
| 7 | **v0-baseline** | 800 | 800 | 11.71 | 1.22 | 4.62 | 35% | 12% | 0.0000 | 0 | 0 | 0 | 0.017 | 0.348 | 10.00 | 0 |
| 8 | **cap-floor-count-v2** | 800 | 800 | 11.06 | 1.21 | 4.71 | 33% | 11% | 0.0000 | 0 | 0 | 0 | 0.017 | 1.083 | 31.78 | 0 |
| 9 | **cap-floor-count** | 800 | 800 | 10.60 | 1.20 | 4.78 | 31% | 11% | 0.0000 | 0 | 0 | 0 | 0.018 | 0.741 | 12.15 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| v0-nowar | 18% | 19% | 16% | 13% | 10% | 12% | 8% | 5% |
| cap-floor-count-v3 | 10% | 17% | 19% | 17% | 14% | 10% | 7% | 5% |
| keep-made-plus-draw | 16% | 12% | 10% | 10% | 12% | 15% | 12% | 14% |
| keep-made-plus-draw-v2 | 14% | 10% | 12% | 11% | 12% | 13% | 16% | 12% |
| bot | 13% | 11% | 11% | 12% | 13% | 14% | 14% | 13% |
| icm-pushfold | 10% | 14% | 13% | 13% | 11% | 16% | 10% | 13% |
| v0-baseline | 12% | 12% | 11% | 12% | 14% | 12% | 16% | 12% |
| cap-floor-count-v2 | 11% | 11% | 11% | 12% | 15% | 12% | 16% | 12% |
| cap-floor-count | 11% | 9% | 10% | 13% | 14% | 12% | 16% | 14% |

## Head-to-head (row finished above column: wins-ties-losses)

| | v0-nowar | cap-floor-count-v3 | keep-made-plus-draw | keep-made-plus-draw-v2 | bot | icm-pushfold | v0-baseline | cap-floor-count-v2 | cap-floor-count |
|---|---|---|---|---|---|---|---|---|---|
| **v0-nowar** | · | 204-3-193 | 232-2-166 | 258-1-141 | 0-0-0 | 245-2-153 | 240-2-158 | 252-2-146 | 261-3-136 |
| **cap-floor-count-v3** | 193-3-204 | · | 458-6-336 | 475-0-325 | 243-3-154 | 467-2-331 | 465-2-333 | 477-2-321 | 483-6-311 |
| **keep-made-plus-draw** | 166-2-232 | 336-6-458 | · | 415-8-377 | 201-3-196 | 407-2-391 | 396-0-404 | 415-3-382 | 438-0-362 |
| **keep-made-plus-draw-v2** | 141-1-258 | 325-0-475 | 377-8-415 | · | 208-5-187 | 382-6-412 | 401-5-394 | 406-7-387 | 410-16-374 |
| **bot** | 0-0-0 | 154-3-243 | 196-3-201 | 187-5-208 | · | 194-4-202 | 193-3-204 | 205-2-193 | 206-7-187 |
| **icm-pushfold** | 153-2-245 | 331-2-467 | 391-2-407 | 412-6-382 | 202-4-194 | · | 418-5-377 | 415-3-382 | 418-5-377 |
| **v0-baseline** | 158-2-240 | 333-2-465 | 404-0-396 | 394-5-401 | 204-3-193 | 377-5-418 | · | 422-9-369 | 384-6-410 |
| **cap-floor-count-v2** | 146-2-252 | 321-2-477 | 382-3-415 | 387-7-406 | 193-2-205 | 382-3-415 | 369-9-422 | · | 423-4-373 |
| **cap-floor-count** | 136-3-261 | 311-6-483 | 362-0-438 | 374-16-410 | 187-7-206 | 377-5-418 | 410-6-384 | 373-4-423 | · |

Files: `arena/results/20261106-192119-nowar-ab-pool-ebc0` (tables.jsonl, seats.csv, summary.json, run.json).
