# icm-pushfold-v9 — BEST of the family: cap-floor-count-v6 + the ICM push/fold module

**Status: WON vs `bot` (= cap-floor-count-v6, the active submission as of 2026-11-06 19:53). Candidate for `bot/`.**
Parents: `bots/cap-floor-count-v6` (owned by the cap-floor-count agent; copied, not edited) and
`bots/icm-pushfold-v7` (the module; family history there).

## Result
`ab bot bots/icm-pushfold-v9 --tables 400 --seed icm1` (field min_raiser + check_or_fold, fast mode):

| pairs | hero (bot) | v9 | diff | 95 % CI | p | better / tied / worse | failures |
|---|---|---|---|---|---|---|---|
| 397 | 22.70 | 25.03 | **+2.33** | ±0.58 | < 0.001 | 116 / 251 / 30 | 0 errors, 0 timeouts (both bots) |

Place distribution: v9 top-3 59 % vs 49 %, average place 3.23 vs 3.52. Latency (`arena check`, 6 tables):
p50 0.094 ms, p99 0.97 ms, max 7.9 ms — the parent's cap/floor/count enumeration dominates (bot p99 0.73 ms in
the same A/B run; v9 0.89 ms). Memory 164 bytes.

## What differs from cap-floor-count-v6 (only `preflop()` + memory bookkeeping)
- **Unopened pot, ≤ 15 BB effective:** shove iff
  `P(no call)·ICM(me+pot) + P(call)·[eq·ICM(win) + (1−eq)·ICM(lose)] ≥ ICM(fold) + premium`, callers' call
  probability = Nash call % (`data/pushfold_nash.csv`) blended with the seat's observed continue-vs-raise rate
  (10-decision prior), eq from `data/hand_vs_range.csv` vs the implied range.
- **Facing a raise / all-in where the stack at risk ≤ 18 BB:** call (never re-shove over an all-in) or re-shove by
  the same arithmetic; shover's range = Nash shove % blended with their observed raise rate; committed players
  (≥ 30 % of stack in) count as callers with multiway equity.
- **Survival premium** 0.30 × ICM(fold) × (players − 2)/6, × 1.5 per extra committed player (06 S6.5).
- Deeper preflop (3-bet war capped, no class-1 limps), selection and postflop: cap-floor-count-v6 byte for byte.
- ICM: Malmuth-Harville, numba-compiled at import (2.6 µs/call), pure-Python/numpy fallback. Memory: 164-byte
  struct (per seat: dealt, raises, faced raise, continued, faced all-in, called all-in, stack), parsed defensively.

## Strategy entries
`strategy/06-tournament-icm.md` S6.1, S6.2, S6.3, S6.5; `strategy/02-preflop.md` S2.5; tables `calc/i_pushfold_tables.py`.

## Promote / demote
Promote (copy to `bot/`, upload) — it beats the current submission on 397 pairs at p < 0.001 with no failures.
Demote if a run against the real field's population (05 S5.3 priors) shows shoves called far more often than the
blended estimate, or if strict-mode timing on a quiet machine shows timeouts the parent does not have.

## Build
`merge_v9.py` (session scratchpad; the recipe): take the parent's `agent.py`, add the module's imports
(`csv`, `os`, `struct`, `numpy`, `icm as icm_generic`), insert the tables/ICM/memory blocks before `class Agent`,
replace `Agent`, `decide` and `preflop`, rename the module's margins to `PF_SHOVE_MARGIN` / `PF_CALL_MARGIN`
(the parent's postflop has its own `CALL_MARGIN`), copy `data/`. To rebase onto a newer `bot/`, repeat.
