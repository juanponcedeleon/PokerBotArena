# keep-made-plus-draw-v2 — **current best of the keep-rule family**

**Strategy implemented:** `strategy/03-selection.md` S3.1 (keep rule, *tuned* weights) + S3.3 (weights scaled
by the number of live opponents).

**Parent:** `bots/keep-made-plus-draw` (v1), itself `bot/agent.py` v0 with only `select()` changed. v2 changes
only the bonus function and the weights:

| live opponents | fd (both kept suited) | fd1 (monotone board) | open-ender | gutshot | per overcard (no pair) |
|---|---|---|---|---|---|
| <=2 | 15M | 15M | 8M | 2M | 0 |
| 3-4 | 20M | 15M | 8M | 4M | 0 |
| >=5 | 20M | 15M | 16M | 4M | 2M |

(eval7 value space; one pair = 16.8M.) Weights from `calc/i_keep_weights.py` (50,000 deals, grid search per
opponent count; `calc/results/i_keep_weights.txt`). Live opponents = seats with status `active` or `all_in`
other than ours at selection time. Preflop, postflop and the exposure rule are byte-identical to v0.

**Hypothesis:** the v1 weights were a first guess; tuned, opponent-aware weights capture more of the gap to the
Monte-Carlo ceiling (offline: +0.65 pot-share points over v1 at 3 opponents).

**Promote if** v2 >= v1 in the arena and v2 > v0 with CI excluding zero. **Demote if** v2 < v1 with CI excluding zero.

## Results (2026-11-06, details in `strategy/08-experiments.md`)

| comparison | field | pairs | seed | diff (pts/table) | 95% CI | p |
|---|---|---|---|---|---|---|
| v2 - v1 | v0-baseline copies | 2000 | s31d | +0.03 | ±0.13 | 0.64 (1724 pairs identical) |
| v2 - v0 (`bot`) | v0-baseline copies | 2000 | s31c | **+0.29** | **±0.20** | **0.004** |
| v1 - v0 (`bot`), same seed | v0-baseline copies | 2000 | s31c | +0.16 | ±0.14 | 0.022 |

Verdict: **promoted to family best.** Not separable from v1 in the arena (both change ~5% of flops), strictly
better offline at every opponent count, no downside, same cost (p50 0.007 ms, p99 0.046 ms, 0 failures in
6,661 check decisions; no memory).

## Family log (best version first)

| version | directory | change | best A/B result | status |
|---|---|---|---|---|
| **v2** | `bots/keep-made-plus-draw-v2` | tuned weights, scaled by live opponents (S3.1 + S3.3) | +0.29 ±0.20 vs v0 (p=0.004) | **current best - port to `bot/`** |
| v1 | `bots/keep-made-plus-draw` | S3.1 keep rule, calc weights (10, 10, 8) | +0.16 ±0.14 vs v0 (p=0.022) | superseded |

To port into a submission: copy the block from `M = 1_000_000` through the end of `select()` into the target
`agent.py`. It has no data files and no state. Never edit a version that has arena results; add `-v3`.
