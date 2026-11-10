# nowar-keep-v2

**Parents:** `bots/v0-nowar` (the current submission, `bot/`) + the select block of `bots/keep-made-plus-draw-v2`.
The only difference from v0-nowar is `select()` and its helpers (`M`, `WEIGHTS`, `weights_for`, `draw_bonus`):
strategy/03-selection.md S3.1 (tuned keep rule) + S3.3 (weights by live opponents). Preflop, postflop and the
exposure rule are byte-identical to v0-nowar.

**Hypothesis:** the keep rule's +0.29 ±0.20 pts/table over v0 (2000 pairs, flop-heavy field) carries over to the
v0-nowar base, which reaches more flops than v0 did.

**Promote (replace `bot/`) if** the paired A/B vs `bot` (= v0-nowar) over >= 2000 pairs in the flop-heavy field
shows a positive difference with the 95% CI excluding zero and zero failures. **Demote if** the CI excludes zero
on the negative side. Requested by the headmaster session, 2026-11-06.

## Results

| comparison | field | pairs | seed | diff (pts/table) | 95% CI | p |
|---|---|---|---|---|---|---|
| nowar-keep-v2 - bot (v0-nowar) | v0-baseline copies | 2000 | s31f | +0.02 | ±0.18 | 0.80 |
| nowar-keep-v2 - bot (v0-nowar) | v0-nowar copies | 2000 | s31g | +0.03 | ±0.23 | 0.79 |

Verdict: **not promoted** (tie in both fields). The keep rule's measurable value on this base is inside ±0.2
pts/table. Zero failures, p99 0.049 ms, no memory. Details in strategy/08-experiments.md (2026-11-06).
