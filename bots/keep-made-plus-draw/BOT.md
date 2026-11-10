# keep-made-plus-draw (v1 of the keep-rule family — superseded by `keep-made-plus-draw-v2`)

**Strategy implemented:** `strategy/03-selection.md` S3.1 — *Keep rule: made hand + draw bonus*.

**Parent:** `bot/agent.py` v0 as of 2026-11-06. The only change is in `select()`: each of the three 2-card
subsets is scored by `eval7.evaluate(flop + pair) + draw_bonus(flop + pair)`, where a 4-flush adds
10,000,000 (≈ 0.6 of a pair step in eval7's value space) and four consecutive ranks (open-ended straight
draw, 2345…TJQK) add 8,000,000. These are the exact weights of policy "made hand + draw bonus" in
`calc/c_selection_policies.py` (26.1% pot share vs 25.1% for made hand only, 20,000 deals). The exposure
rule (show the lower kept card), preflop and postflop code are byte-identical to v0 so an A/B isolates the
keep rule.

**Hypothesis:** keeping a strong draw over a weak made hand on the flop is worth +1 pot-share point per
flop seen (SIM). In a sit-and-go that should translate into a small positive points-per-table difference
against the same bot without the bonus.

**Promote if** the paired A/B against `bot` (v0) shows a positive difference with the 95% CI excluding
zero. **Demote if** the CI excludes zero on the negative side; **shelve** (status stays SIM-only) if it is
indistinguishable from zero after 2000+ pairs.

## Results (details in `strategy/08-experiments.md`, 2026-11-06)

| field | pairs | diff vs v0 (pts/table) | 95% CI | p |
|---|---|---|---|---|
| min_raiser + check_or_fold | 394 | −0.02 | ±0.28 | 0.87 (379 pairs identical) |
| v0-baseline copies | 400 | +0.21 | ±0.33 | 0.22 |
| v0-baseline copies | 2000 | **+0.16** | **±0.14** | **0.022** |

Verdict: **promoted** — PROVEN with SIM + LOCAL evidence. The effect is small because the two rules
disagree on only 5.2% of flops and because v0 rarely reaches a flop against the kit examples (its fate is
decided in hand-1 min-raise wars). Timing: p50 0.022 ms, p99 < 0.8 ms in fast mode, 0 failures over
6,951 + 10,400 decisions. Memory: none.

## Family log (best version first)

| version | directory | change | best A/B result | status |
|---|---|---|---|---|
| **v2** | `bots/keep-made-plus-draw-v2` | tuned weights, scaled by live opponents | +0.29 ±0.20 vs v0 (p=0.004) | **current best** (see its BOT.md) |
| v1 | `bots/keep-made-plus-draw` | S3.1 keep rule | +0.16 ±0.14 vs v0, flop-heavy field | superseded by v2 |

Later versions of this family live in sibling directories `bots/keep-made-plus-draw-v<N>/`; this table is
the single place that says which one is best. Never edit a version that has arena results.
