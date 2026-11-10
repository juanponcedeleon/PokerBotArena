# Arena run `ladder` — fast mode

Started 2026-11-06T19:13:29 · seed `47ad7e74` · scheme league · 203 tables · 18961 hands · 8.2 s

Command: `watch --interval 30 --tables 200 --agent arena-watch --question auto-ladder-on-bots-change`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **check_or_fold** | 148 | 232 | 18.41 | 1.64 | 3.00 | 70% | 0% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.038 | 0.43 | 0 |
| 2 | **icm-pushfold** | 151 | 232 | 17.97 | 1.55 | 3.03 | 72% | 0% | 1.0000 | 0 | 30166 | 0 | - | - | - | 0 |
| 3 | **keep-made-plus-draw** | 157 | 232 | 14.35 | 2.83 | 4.31 | 32% | 26% | 0.0000 | 0 | 0 | 0 | 0.013 | 0.357 | 13.81 | 0 |
| 4 | **v0-baseline** | 149 | 232 | 13.92 | 2.69 | 4.43 | 34% | 22% | 0.0000 | 0 | 0 | 0 | 0.012 | 0.204 | 10.78 | 0 |
| 5 | **bot** | 143 | 232 | 10.56 | 2.55 | 4.72 | 24% | 19% | 0.0000 | 0 | 0 | 0 | 0.012 | 0.179 | 35.17 | 0 |
| 6 | **cap-floor-count** | 151 | 232 | 10.43 | 2.50 | 4.95 | 25% | 18% | 0.0000 | 0 | 0 | 0 | 0.015 | 0.439 | 28.41 | 0 |
| 7 | **min_raiser** | 147 | 232 | 1.85 | 1.11 | 6.42 | 5% | 3% | 0.0000 | 0 | 0 | 0 | 0.003 | 0.058 | 0.17 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| check_or_fold | 0% | 44% | 27% | 18% | 9% | 2% | 0% | 0% |
| icm-pushfold | 0% | 36% | 36% | 19% | 8% | 1% | 0% | 0% |
| keep-made-plus-draw | 26% | 2% | 4% | 17% | 15% | 14% | 16% | 6% |
| v0-baseline | 22% | 3% | 9% | 7% | 18% | 18% | 18% | 5% |
| bot | 19% | 0% | 5% | 15% | 17% | 22% | 16% | 6% |
| cap-floor-count | 18% | 2% | 5% | 11% | 13% | 21% | 19% | 11% |
| min_raiser | 3% | 0% | 2% | 3% | 9% | 28% | 32% | 23% |

## Head-to-head (row finished above column: wins-ties-losses)

| | check_or_fold | icm-pushfold | keep-made-plus-draw | v0-baseline | bot | cap-floor-count | min_raiser |
|---|---|---|---|---|---|---|---|
| **check_or_fold** | · | 65-0-44 | 64-0-46 | 64-0-41 | 75-0-30 | 75-0-33 | 97-0-3 |
| **icm-pushfold** | 44-0-65 | · | 69-0-46 | 69-0-36 | 68-0-31 | 72-0-35 | 100-0-6 |
| **keep-made-plus-draw** | 46-0-64 | 46-0-69 | · | 55-0-55 | 58-0-51 | 71-2-42 | 93-4-16 |
| **v0-baseline** | 41-0-64 | 36-0-69 | 55-0-55 | · | 53-0-45 | 58-0-49 | 87-3-15 |
| **bot** | 30-0-75 | 31-0-68 | 51-0-58 | 45-0-53 | · | 52-0-49 | 84-3-13 |
| **cap-floor-count** | 33-0-75 | 35-0-72 | 42-2-71 | 49-0-58 | 49-0-52 | · | 85-3-17 |
| **min_raiser** | 3-0-97 | 6-0-100 | 16-4-93 | 15-3-87 | 13-3-84 | 17-3-85 | · |

## Bot errors (first occurrence per table; untrusted text)

```
icm-pushfold could not load: erBot\bots\icm-pushfold\agent.py", line 73, in <module>
    HVR = _load_hvr()                 # label -> (pct of dealt hands, eq vs top-X% for X in X_GRID)
          ^^^^^^^^^^^
  File "C:\Users\jmast\OneDrive\Desktop\Coding\PokerBot\bots\icm-pushfold\agent.py", line 56, in _load_hvr
    with open(os.path.join(_HERE, "data", "hand_vs_range.csv"), newline="") as f:
```

Files: `arena/results/20261106-191329-ladder-38b5` (tables.jsonl, seats.csv, summary.json, run.json).
