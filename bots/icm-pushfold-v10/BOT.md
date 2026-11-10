# icm-pushfold-v10 — fp-v3 (the live bot) + the ICM push/fold short-stack module

Parents: `bots/fp-v3` (= `bot/` since 2026-11-07 04:34Z; owned by the keep-rule agent, copied not edited) and
`bots/icm-pushfold-v7` (module; family history there). Built by `merge_v10.py` (session scratchpad): fp-v3's
`preflop` is renamed `preflop_deep`; the module's `preflop(state, stats)` handles unopened pots at ≤ 15 BB effective
and raised pots where the stack at risk is ≤ 18 BB, and hands everything else to `preflop_deep`. `Agent`/`decide`
carry the 164-byte per-seat memory. Everything else (percentile preflop, keep rule v2 + non-pairing exposure,
tiered postflop, GC tuning) is fp-v3 byte for byte, so an A/B against `bot` isolates the module.

## Hypothesis
The module added +2.2 to cap-floor-count-v6 in the kit field (two seeds) but nothing measurable in the archetype
field (−1.85 ±2.22 n.s.), and fp-v2 beat that bot by +4.29. The question is whether the module still adds anything
on top of a base whose own short-stack rule (`SHOVE_PCT` by players behind at ≤ 10 BB, pot-odds all-in calls) is
already percentile-driven.

## Checks
`arena check bots/icm-pushfold-v10 --tables 6`: 7,331 decisions, 0 failures, p50 0.054 ms, p99 0.25 ms, max 0.72 ms,
memory 164 B. No-try/except probe (12 tables, 14,367 decisions): 0 exceptions.

## Results
See `strategy/08-experiments.md` entries "icm-pushfold-v10-arch" (archetype field, seed icm7) and
"icm-pushfold-v10-kit" (kit field, seed icm1); summary below is filled in from them.

| field | pairs | diff vs fp-v3 | 95 % CI | p | better / tied / worse | failures (v10 / bot) |
|---|---|---|---|---|---|---|
| archetype (v0-baseline, check_or_fold, arch-folder, arch-shover, arch-station), seed icm7 | 328 | **−0.97** | ±1.04 | 0.068 | 43 / 221 / 64 | 18 timeouts / 0 (loaded machine) |
| kit (min_raiser, check_or_fold), seed icm1 | 397 | **+1.27** | ±0.78 | 0.001 | 131 / 214 / 52 | 95 timeouts / 0 (loaded machine) |

**Verdict: not promoted.** Same pattern as v9: the module wins against the kit examples (a 100 % caller and a 100 %
folder, where learned per-seat call rates pay) and does not win against the practice-round archetypes, which is the
field that matters. fp-v3 stays the submission. The module's value is field-specific; shelved unless the real
hand histories show a field of stations and folders.

## Promote / demote
Promote (candidate for `bot/`) only if it beats fp-v3 in the archetype field with p < 0.05 and no more failures than
the hero. Otherwise fp-v3 stays and the module is shelved as kit-field-specific (06 S6.1 PROMISING, field-dependent).
