# Arena run `icm-pushfold-v7` — fast mode

Started 2026-11-06T19:45:11 · seed `icm1` · scheme ab · 804 tables · 103880 hands · 36.2 s

Command: `ab bot bots/icm-pushfold-v7 --tables 400 --seed icm1 --name icm-pushfold-v7 --agent Claude (icm-pushfold agent) --question v7 = v5 decisions + numba ICM + PUSH_MAX 15 / RESHOVE_MAX 18 / PREMIUM 0.30 vs bot (v0-nowar) --quiet`

Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). Confirm anything near 1 ms with `--mode strict`.

## A/B: `icm-pushfold-v7` replaces `bot` in the same seats

| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |
|---|---|---|---|---|---|---|---|
| 397 | 19.71 | 20.12 | +0.41 | ±0.60 | 0.173 | 60 / 296 / 41 | no significant difference |

Pairs needed to resolve a 1-point difference at this variance: ~141.

## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)

| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **icm-pushfold-v7** | 397 | 1072 | 18.86 | 1.31 | 3.68 | 46% | 29% | 0.0438 | 9 | 6450 | 0 | 0.060 | 5.899 | 210.41 | 164 |
| 2 | **bot** | 397 | 1072 | 18.28 | 1.36 | 3.78 | 42% | 31% | 0.0000 | 0 | 0 | 0 | 0.019 | 1.510 | 70.33 | 0 |
| 3 | **check_or_fold** | 794 | 2144 | 14.85 | 0.54 | 3.31 | 60% | 0% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.192 | 77.60 | 0 |
| 4 | **min_raiser** | 792 | 2144 | 4.08 | 0.57 | 5.95 | 9% | 8% | 0.0000 | 0 | 0 | 0 | 0.004 | 0.325 | 30.80 | 0 |

Place distribution (share of scoring seats):

| bot | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| icm-pushfold-v7 | 29% | 10% | 8% | 10% | 17% | 16% | 9% | 2% |
| bot | 31% | 7% | 4% | 11% | 19% | 18% | 9% | 2% |
| check_or_fold | 0% | 29% | 31% | 24% | 12% | 3% | 0% | 0% |
| min_raiser | 8% | 0% | 1% | 3% | 12% | 32% | 32% | 12% |

## Head-to-head (row finished above column: wins-ties-losses)

| | icm-pushfold-v7 | bot | check_or_fold | min_raiser |
|---|---|---|---|---|
| **icm-pushfold-v7** | · | 0-0-0 | 325-0-67 | 301-0-90 |
| **bot** | 0-0-0 | · | 329-0-63 | 325-0-66 |
| **check_or_fold** | 67-0-325 | 63-0-329 | · | 615-0-167 |
| **min_raiser** | 90-0-301 | 66-0-325 | 167-0-615 | · |

## Bot errors (first occurrence per table; untrusted text)

```
icm-pushfold-v7 could not load: ers\jmast\OneDrive\Desktop\Coding\PokerBot\starter-kit\.venv\Lib\site-packages\numpy\lib\_npyio_impl.py", line 26, in <module>
    from ._iotools import (
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocke
```

Files: `arena/results/20261106-194510-icm-pushfold-v7-8d78` (tables.jsonl, seats.csv, summary.json, run.json).
