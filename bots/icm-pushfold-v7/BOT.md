# icm-pushfold-v7 — the ICM push/fold module on v0-nowar (family reference; v9 is the best bot)

**Status: WON vs `bot` (v0-nowar, the submission as of 19:22).** Parent: `bots/icm-pushfold-v6` (same code,
retuned). Successors: `v8` (wider parameters, statistical tie), **`v9` (same module on `cap-floor-count-v6`,
+2.33 ±0.58 vs the current submission — the family's best bot, see its BOT.md).**

## What it is
`bot/agent.py` as of 2026-11-06 19:22 (v0-nowar) with the short-stack preflop replaced:
- **Unopened pot, ≤ 15 BB effective:** shove iff
  `P(no call)·ICM(me+pot) + P(call)·[eq·ICM(win) + (1−eq)·ICM(lose)] ≥ ICM(fold) + premium`.
  Callers' call probability = Nash call % for (S, N) (`data/pushfold_nash.csv`) blended with the seat's observed
  continue-vs-raise rate (10-decision prior); eq from `data/hand_vs_range.csv` vs the implied range.
- **Facing a raise/all-in where the stack at risk ≤ 18 BB:** call (never re-shove over an all-in) or re-shove
  by the same arithmetic; the shover's range = Nash shove % blended with their observed raise frequency;
  committed players (≥ 30 % of stack in) count as callers with multiway equity (eq vs 1/3/7 columns).
- **Survival premium** 0.30 × ICM(fold) × (players−2)/6, ×1.5 per extra committed player (06 S6.5).
- **Deeper:** v0-nowar, byte for byte. Select and postflop: v0.
- ICM = Malmuth-Harville, numba-compiled at import (2.6 µs; pure-Python/numpy fallback). Memory: 164-byte
  struct (per seat: dealt, raises, faced-raise, continued, faced-all-in, called-all-in, stack), parsed defensively.

## Strategy entries
`strategy/06-tournament-icm.md` S6.1, S6.2, S6.3, S6.5; `strategy/02-preflop.md` S2.5. Tables: `calc/i_pushfold_tables.py`.

## Results (arena fast mode, field min_raiser + check_or_fold unless stated)
| run | pairs | diff vs bot | p | better/tied/worse | notes |
|---|---|---|---|---|---|
| v5 (13 BB / premium 0.15) seed icm1 | 397 | +0.65 ±0.48 | 0.008 | 52/320/25 | 165 timeouts under contention |
| **v7 rerun, seed icm1** | 397 | **+0.82 ±0.56** | **0.004** | 60/308/29 | 0 errors, 19 timeouts (p99 13.9 ms, machine shared) |
| v8 (18 BB / premium 0.50) seed icm1 | 397 | +0.86 ±0.63 | 0.007 | 75/293/29 | tie with v7; 63 timeouts |
| v7 vs bot, whole pool as field, seed icm4 | 95 | −3.60 ±4.03 | 0.08 | 24/39/32 | too few pairs; inconclusive |
| v9 (module on cap-floor-count-v6) vs that bot, seed icm1 | 397 | +2.33 ±0.58 | <0.001 | 116/251/30 | 0 errors, 0 timeouts |

Sweeps (300 pairs, seed icm3, vs v0-nowar): PUSH 10/13/15/18 → +0.58 / +0.65* / +1.57 / +1.69;
PREMIUM 0 / 0.15* / 0.30 / 0.50 → +0.39 (ns) / +0.65* / +1.40 / +1.52 (* = seed icm1, 397 pairs).

Isolated `arena check`: p50 0.045 ms, p99 0.23 ms, max 0.41 ms, memory 164 B, 0 failures. Strict mode (WSL,
machine loaded): p50 0.79 ms vs 0.59 for check_or_fold — pipe overhead, not the bot.

## Promote / demote
Promote the module when it beats the current `bot/` on ≥ 400 pairs with p < 0.05 and no more failed decisions
than the hero in the same run (headmaster rule) — done by v9. Demote if a clean run shows timeouts the base does
not have, or if the real-field hand histories show shoves called far more often than the blended estimate.

## Lessons (family)
1. ICM arithmetic at deep stacks in a maniac field is a leak (v2–v4): it calls raise-war all-ins with top-17 %
   hands. Keep the module short-stack only. (07 A24)
2. Calling a short all-in must be a call, not an isolation shove (v1 bug).
3. Players already committed to the pot call; model them as callers with multiway equity.
4. `bot/` changes without notice (v0 → v0-nowar → cap-floor-count-v6 in one evening); rebase before every A/B.
5. Fast-runner timeouts track machine load (4 agents' arenas at once); compare with the hero's count in the same
   run and check p99 in isolation.
