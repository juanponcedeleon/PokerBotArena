# Arena run `submit-check-nowar` — fast mode

Started 2026-11-06T19:22:23 · seed `submit-nowar-1` · scheme league · 200 tables · 19738 hands · 4.9 s

Command: `league bot v0-baseline check_or_fold min_raiser --tables 200 --seed submit-nowar-1 --name submit-check-nowar --agent Claude (headmaster) --question pre-submission check: bot = v0-nowar copy, zero failures required --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 200 | 400 | 22.48 | 0.83 | 2.67 | 91% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.033 | 2.06 | 0 |
| 2 | **v0-baseline** | 200 | 400 | 13.28 | 2.14 | 4.45 | 28% | 25% | 0.0000 | 0 | 0 | 0 | 0.020 | 0.313 | 3.44 | 0 |
| 3 | **bot** | 200 | 400 | 12.75 | 2.05 | 3.84 | 28% | 22% | 0.0000 | 0 | 0 | 0 | 0.021 | 0.151 | 2.92 | 0 |
| 4 | **min_raiser** | 200 | 400 | 1.50 | 0.84 | 6.63 | 3% | 3% | 0.0000 | 0 | 0 | 0 | 0.005 | 0.088 | 0.91 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 42% | 49% | 8% | 0% | 0% | 0% | 0% |
| v0-baseline | 25% | 2% | 0% | 10% | 17% | 28% | 17% | 0% |
| bot | 22% | 6% | 1% | 30% | 26% | 14% | 3% | 0% |
| min_raiser | 3% | 0% | 0% | 2% | 7% | 17% | 54% | 18% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | v0-baseline | bot | min_raiser |
|---|---|---|---|---|
| **check_or_fold** | · | 91-0-109 | 100-0-100 | 188-0-12 |
| **v0-baseline** | 109-0-91 | · | 101-0-99 | 163-0-37 |
| **bot** | 100-0-100 | 99-0-101 | · | 188-0-12 |
| **min_raiser** | 12-0-188 | 37-0-163 | 12-0-188 | · |

Files: `arena/results/20261106-192223-submit-check-nowar-f202` (tables.jsonl, seats.csv, summary.json, run.json).
