# 09 — Engineering constraints: what fits in 1 ms

Owner: Claude (main)   Last updated: 2026-11-06
Calculator: `calc/g_timing.py` (this Windows machine; the competition machine may differ, assume ±2×).

## Measured costs

| operation | cost | fits in 1 ms? |
|---|---|---|
| `eval7.evaluate` on 7 cards | ~540 ns | ~1,860 per ms |
| `eval7.evaluate` on 5 cards | ~270 ns | |
| enumerate 45 hidden cards for one opponent, river (cap, floor, beat-count) | ~20 µs | yes, all 7 opponents ≈ 140 µs |
| 45 hidden × 100 runouts on the flop (equity vs one opponent) | ~7 ms | **no** |
| full policy inversion (2,256 combos × 3 evals) | ~3.6 ms | **no**, do it logically or cache |
| JSON round trip of a 2.4 KB memory dict | ~70 µs | yes, but 7% of budget; prefer `struct` |
| 3 evaluations to pick the made-hand-best pair at selection | ~1 µs | trivially |

Rule of thumb: **budget 300 µs of real work**, leave the rest for interpreter overhead, state parsing and
jitter. The platform measures from its side.

## Design consequences

1. **Precompute at import.** Preflop class table (1,755 classes → equity vs 1/3/7, percentile), shove/call
   thresholds by BB and players, flop-texture lookups. Import time is not budgeted; keep data files small
   (<5 MB) so the upload check and cold start stay fast.
2. **Exact enumeration, not Monte Carlo, inside `act`.** River: enumerate the hidden card per opponent (45).
   Turn: 45 hidden × 44 rivers = 1,980 evaluations per opponent ≈ 1.1 ms: too slow for all opponents, feasible
   for a single live opponent if nothing else runs; otherwise use outs-based approximations. Flop: no
   enumeration; use made-hand category + draw flags + opponent cap.
3. **Memory format.** Fixed-width `struct` per seat (seat index is anonymized per table but stable within it):
   counts of hands, VPIP, PFR, cbets, folds-to-cbet, shoves, calls-of-shoves, showdowns seen, and a
   5-slot histogram of exposure-rule consistency. ~40 bytes × 8 seats + a header ≈ 400 bytes. Parse
   defensively: wrong length → start fresh.
4. **Never throw.** Wrap `act` in try/except returning a legal passive action; an exception is a check/fold,
   and a timeout also loses the time bank.
5. **Selection phase is a separate branch.** `state.phase == "select"` → compute keep pair and exposure,
   return `Action("select", cards=(discard_idx, reveal_idx))`. Must also be under 1 ms.
6. **Legal actions only.** `state.can(kind)` and clamp raise amounts into `[min_amount, max_amount]`.
7. **Numba is available** if a custom evaluator or batch equity becomes necessary; JIT compile at import with a
   throwaway call. eval7 is already C and is fast enough for enumeration-scale work.

## Testing checklist (Build phase)

- `poker-agent check bot/agent.py` passes.
- Microbenchmark: 10,000 synthetic `act` calls, p99 < 500 µs.
- `poker-agent play` 200+ tables vs examples: zero failed decisions.
- Memory never exceeds 16 KB; truncated memory does not crash.
