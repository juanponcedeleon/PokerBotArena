# Arena run `gate-fp3` — fast mode

Started 2026-11-06T20:32:51 · seed `gate-fp3-1` · scheme league · 200 tables · 27974 hands · 5.1 s

Command: `league bots/fp-v3 bot arch-folder arch-shover --tables 200 --seed gate-fp3-1 --name gate-fp3 --agent Claude (headmaster) --question uncontended failure/latency gate for fp-v3 next to fp-v2 (bot) --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **fp-v3** | 200 | 400 | 20.05 | 2.01 | 3.33 | 55% | 25% | 0.0000 | 0 | 0 | 0 | 0.026 | 0.345 | 8.51 | 0 |
| 2 | **bot** | 200 | 400 | 16.10 | 1.99 | 3.99 | 44% | 21% | 0.0000 | 0 | 0 | 0 | 0.027 | 0.207 | 4.07 | 0 |
| 3 | **arch-folder** | 200 | 400 | 12.00 | 1.31 | 3.71 | 47% | 1% | 0.0000 | 0 | 0 | 0 | 0.012 | 0.140 | 1.71 | 0 |
| 4 | **arch-shover** | 200 | 400 | 1.85 | 0.91 | 6.58 | 4% | 4% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.039 | 0.24 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| fp-v3 | 25% | 16% | 14% | 14% | 12% | 13% | 5% | 0% |
| bot | 21% | 11% | 12% | 12% | 11% | 16% | 17% | 0% |
| arch-folder | 1% | 22% | 24% | 20% | 22% | 10% | 0% | 0% |
| arch-shover | 4% | 0% | 0% | 3% | 7% | 20% | 42% | 24% |

## Head-to-head (row finished above column: wins-ties-losses)

| | fp-v3 | bot | arch-folder | arch-shover |
|---|---|---|---|---|
| **fp-v3** | · | 113-0-87 | 143-0-57 | 182-0-18 |
| **bot** | 87-0-113 | · | 130-0-70 | 169-0-31 |
| **arch-folder** | 57-0-143 | 70-0-130 | · | 186-0-14 |
| **arch-shover** | 18-0-182 | 31-0-169 | 14-0-186 | · |

Files: `arena/results/20261106-203251-gate-fp3-d3d2` (tables.jsonl, seats.csv, summary.json, run.json).
