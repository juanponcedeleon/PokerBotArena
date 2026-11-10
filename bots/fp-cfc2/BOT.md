# fp-cfc2

Owner: Claude (cap-floor-count agent)   Created: 2026-11-07   Parent: `bots/fp-v3` (another agent's bot, the live submission)

## Hypothesis

fp-v3's tiered postflop is already as good as the full cap/floor/count module (`bots/fp-cfc`: −0.75 ±1.00). But two
pieces of that module are not judgment, they are arithmetic, and fp-v3's tiers ignore them:

- **Beat every cap** (01 S1.1 / 04 S4.1): if our hand beats the best hand any live opponent can hold given their
  exposed card, play it as tier 4 (bet 0.65 pot, raise bets) instead of tier 3's call/fold. Applied on the river, or
  earlier with two pair or better.
- **Below a floor** (01 S1.2 / 04 S4.2): if some opponent's *worst* possible hand beats ours, fold any river bet and
  never value-bet on earlier streets (tier capped at 2, so draws are still priced).

Everything else is fp-v3 byte for byte (percentile preflop, keep rule v2, non-pairing exposure, ICM-tight all-in
calls). Cost ≈ 20 µs per live opponent; GC tuning from cap-floor-count-v5 included.

## Results

| hero | field | pairs | seed | fp-cfc2 − hero | 95% CI | p | better / tied / worse |
|---|---|---|---|---|---|---|---|
| fp-v3 | v0-baseline, check_or_fold, arch-folder, arch-shover, arch-station, cap-floor-count-v6 | 1180 | fpcfc2 | **+1.10** | ±0.44 | <0.001 | 104 / 1033 / 43 |
| fp-v3 | v0-baseline, cap-floor-count-v6, keep-made-plus-draw-v2, arch-shover, min_raiser, check_or_fold | 1197 | fpcfc3 | **+0.82** | ±0.35 | <0.001 | 83 / 1071 / 43 |

`arena check`: 5,074 decisions, 0 failures, p50 0.024 ms, p99 0.164 ms. Both runs 0 failures; confirmation run p99 0.436 ms in a full 8-worker A/B. **Recommended final upload.**

Ship `agent.py` + `data/preflop_classes.csv`.
