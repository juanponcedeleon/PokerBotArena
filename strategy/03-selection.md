# 03 — Selection: which two to keep, which one to expose

Owner: Claude (main)   Last updated: 2026-11-06
Calculators: `calc/c_selection_policies.py` (keep rule), `calc/d_reveal_tables.py` + `calc/h_policy_inversion.py` (exposure).

Selection is one decision with two parts. **Keep** is a pure equity problem and is solved well by a cheap rule.
**Expose** is a signalling problem whose value depends on whether opponents read exposures at all.

---

### S3.1 Keep rule: made hand + draw bonus
Status: PROVEN   Evidence: SIM (20,000 deals, common random numbers) + LOCAL (arena A/B, 2000 paired tables)   Owner: Claude   Last updated: 2026-11-06

Hero picks 2 of 3 after the flop by each policy; three opponents keep their made-hand-best pair; everyone sees the
river. Metric = hero's pot share (fair share 25%).

| keep policy | pot share | cost |
|---|---|---|
| oracle (knows the river; upper bound) | 31.8% | impossible |
| Monte Carlo equity, 200 runouts | 26.5% | ~7 ms, too slow |
| Monte Carlo equity, 40 runouts | 26.2% | ~1.4 ms, too slow |
| **made hand + flush-draw/open-ender bonus** | **26.1%** | 3 evaluations + suit/rank checks ≈ 5 µs |
| made hand only (3 evaluations) | 25.1% | 1 µs |
| keep the two highest cards | 21.6% | |
| engine fallback: keep first two dealt | 18.3% | what a timing-out bot gets |

**Claim.** Evaluate the three 2-card subsets on the flop with eval7; add a bonus worth about a pair for a
4-flush and a little less for an open-ended straight draw; keep the best. This captures 96% of what a slow
Monte Carlo achieves and is 8 points of pot share better than the fallback, 4.5 better than "keep high cards".

**Arena result (2026-11-06, Claude keep-rule agent).** `bots/keep-made-plus-draw` = `bot/agent.py` v0 with only
the keep rule changed (made hand → made hand + draw bonus). Paired A/B, challenger replaces v0 in the same seats:

| field | pairs | seed | diff (pts/table) | 95% CI | p | run |
|---|---|---|---|---|---|---|
| min_raiser + check_or_fold | 394 | s31a | −0.02 | ±0.28 | 0.87 | `arena/results/20261106-190518-…` |
| v0-baseline copies (flop-heavy) | 400 | s31b | +0.21 | ±0.33 | 0.22 | `arena/results/20261106-190706-…` |
| v0-baseline copies (flop-heavy) | **2000** | s31c | **+0.16** | **±0.14** | **0.022** | `arena/results/20261106-190743-…` |

The rules disagree on 5.2% of flops (3.3% keep a 4-flush over a weaker made hand, 2.1% an open-ender), so the
per-table effect is small by construction; against the kit examples v0's fate is decided preflop (all-in
in hand-1 min-raise wars) and the keep decision never gets to matter (379/394 pairs identical). Positive
and significant where flops are actually seen. Details in [08-experiments](08-experiments.md).

**Why the gap to oracle is not a target.** Oracle sees the river. The achievable ceiling is the 200-runout MC at
26.5%; our rule is within 0.4%.

**Tuned weights (v2, 2026-11-06, `calc/i_keep_weights.py`, 50,000 deals, CRN, pot share vs N made-hand opponents).**
Features per 2-card subset: 4-flush with both kept cards suited (fd), 4-flush with one kept card on a monotone
board (fd1), open-ender (oesd), gutshot (gut), each overcard when the subset has no pair (over). Millions in
eval7 value space (one pair = 16.8M):

| N opponents | fair share | made only | v1 (10,10,8,0,0) | **v2 best (fd, fd1, oesd, gut, over)** | v2 share |
|---|---|---|---|---|---|
| 1 | 50.0% | 49.69% | 50.47% | (15, 15, 8, 2, 0) | **50.76%** |
| 3 | 25.0% | 24.62% | 25.59% | (20, 15, 8, 4, 0) | **26.24%** |
| 6 | 14.3% | 14.03% | 14.91% | (20, 15, 16, 4, 2) | **15.67%** |

The optimum moves with N (draws and overcards are worth more multiway), so S3.3 is real offline.
`bots/keep-made-plus-draw-v2` switches the weight vector on the number of live opponents at selection time
(≤2 / 3–4 / ≥5). Arena: v2 − v0 = **+0.29 ±0.20** (p=0.004, 2000 pairs, seed s31c, flop-heavy field);
v2 − v1 = +0.03 ±0.13 (not separable). **v2 is the family's best version.**

**Note 2026-11-06 (later, keep-rule agent).** On the submission base `v0-nowar` (`bots/nowar-keep-v2` = v0-nowar + the v2 select
block) the gain is not measurable: +0.02 ±0.18 (field v0-baseline) and +0.03 ±0.23 (field v0-nowar copies), 2000 pairs each.
Expected impact on points per table should be read as **low**: the rule changes ~5% of flops and a tighter preflop
bot sees fewer flops. The rule is still correct and free; it is just not where the points are.

**Refinements to test** (each is a one-line change in `c_selection_policies.py`):
1. Scale the draw bonus by live outs (subtract exposed/dead cards: unknown at selection time since exposure is
   simultaneous, but preflop folders' cards are not exposed anyway; nothing to subtract yet).
2. Number of opponents: heads-up a made pair should outrank a draw; 4-way a nut draw should outrank bottom pair.
   Test by varying the opponent count in the script.
3. Pair quality: eval7 already ranks kickers; add a small penalty for bottom pair vs. an overcard-plus-gutshot combo.
4. Future-exposure awareness: between two near-equal keeps prefer the one whose exposure plan (S3.2) is better.

**Keep-vs-expose interaction.** Made hand + draw bonus can prefer a two-card combo that forces a bad exposure
(e.g. both cards blanks). That is fine: equity first, signalling second.

---

### S3.2 Exposure rule
Status: UNTESTED (candidates analysed)   Evidence: MATH for mechanics   Owner: unclaimed

Mechanical effects of exposing card E (independent of opponents' modelling):

| effect | expose the board-pairing card | expose the blank | note |
|---|---|---|---|
| public cap on us | uncapped (17% two pair+ prior) | capped at one pair publicly | from `d_reveal_tables` |
| credibility to bluff later | high; an A/K blank is also credible as top pair later | none on dry boards | |
| getting paid with a real hand | opponents fear two pair+; fewer calls | opponents see "max one pair"; worse pairs and bluffs attack us | |
| our improvement visibility | turn pairs E → everyone sees trips threat | hidden card improves invisibly | |
| flush draws | both kept cards are the suit: forced to show the suit | n/a | |
| straight draws | hide the connector whose improvement we want paid | | |

The signalling layer (from `h_policy_inversion`): any **deterministic** exposure rule is invertible by a reading
opponent. Examples against us: a "show the blank" rule exposing a board-pairing card tells a reader we have two
pair+ 100%; a "show the higher card" rule exposing a 2 on Q72 tells them we have trips 100%.

**Candidate rules to A/B in local play** (ranked by our prior):

| rule | expected vs non-reading bots | expected vs reading bots | notes |
|---|---|---|---|
| R1 **plan-driven, randomized**: with a value hand expose the card that keeps our public range weakest among exposures consistent with it (usually the blank/lower card); with a bluff plan expose the scariest card; mix 20–30% the other way | neutral | good: P(strength \| exposure) stays near prior | the agent-output's proposal, formalized |
| R2 always expose the board-pairing card ("look strong") | small plus: more folds when we c-bet | exploitable: readers call our c-bets knowing 83% bare pair, and our blanks reveal we have nothing | |
| R3 always expose the blank ("look weak", trap) | small plus vs aggressive bots that attack caps | exploitable: our pairing exposure = two pair+ 100% | |
| R4 expose higher kept card | neutral | exploitable | simple baseline |
| R5 uniform random of the two kept | neutral | unexploitable, zero mechanical optimisation | control arm |
| R6 fallback (first dealt) | same as R5 | same | what we get if we time out |

**Case rules carried over from the agent output, assessed:**
- *Two pair: show the lower pair card.* Both exposures leave us uncapped with identical public distributions
  (trips 2 / two pair 6 / pair 40). The lower card invites top-pair hands to bet into us; the higher card
  gets more folds. Choose by plan (R1). UNTESTED.
- *Flush draw: you must show a suited card.* True. Show the lower suited card when hoping to get paid (hides the
  nut flush), the higher when planning to barrel (threatens the nut flush). UNTESTED.
- *AQ on Q72: show the A, not the Q.* Showing the A caps us at one pair publicly but the hidden Q is top pair,
  and an A on the turn is a public two-pair threat. Showing the Q is uncapped and the hidden A is invisible.
  Against bots that do not read, this choice is nearly irrelevant; against readers R1 says mix.
- *Set: show the suit that reveals least.* Marginal; apply only as a tiebreak.
- *Expose a 2–5 and bet* (Empty Bluffer side prize). Costs nothing when the 2–5 is a kept blank we would
  expose anyway and we plan to c-bet. Never keep a worse pair of cards for it.

**Measurement plan.** Two local bots identical except for exposure rule, vs a third bot that implements policy
inversion (S1.4) and a fourth that ignores exposures. Points per table over 500+ tables. This is the first
experiment to run once a bot skeleton exists.

---

**Arena note (cap-floor-count agent, 2026-11-07).** `bots/cfc-v7-expose` (never expose the card that pairs the flop or shares a two-flush suit; otherwise show the higher card) vs `cap-floor-count-v6` (show-low), 1175 pairs, field with one exposure reader: **+0.10 ±0.48, p=0.68, 942 tables tied**. The exposure rule does not move points against this field; the real-field correlation (top-10 never expose the pairing card) is a proxy for bot quality, not a cause. Status unchanged (UNTESTED vs a reading field).

### S3.3 Adjust keep to the number of opponents
Status: PROMISING   Evidence: SIM (`calc/i_keep_weights.py`, 50,000 deals)   Owner: Claude (keep-rule agent)   Last updated: 2026-11-06

Hypothesis: heads-up, any pair beats a draw; 4-way, nut draws beat weak pairs (one pair wins 7% of 4-way
all-see-river showdowns). The keep score should weight draws by the number of players still in.

Result: confirmed offline, direction as hypothesized but milder than "any pair beats a draw". The best
flush-draw weight is 15M heads-up vs 20M at 3+ opponents; the open-ender weight doubles (8M → 16M) and
overcards start to count (2M each) at 6 opponents; table in S3.1. Using the N=3 vector everywhere costs
about 0.1 pot-share point at N=1 and N=6, so the switch is cheap insurance rather than a big win. Implemented
in `bots/keep-made-plus-draw-v2` (live opponents = seats with status active/all_in). The arena could not
separate v2 from v1 (+0.03 ±0.13 over 2000 pairs) because the two agree on >86% of tables; stays PROMISING
until a larger or more flop-heavy run resolves it.

---

### S3.4 The discard is private information too
Status: PROVEN (logic)   Evidence: MATH   Owner: Claude

Our discard is a dead card nobody else knows. When it pairs the board, every opponent's set/two-pair count is
lower than they think and lower than our own enumeration must use; when it is of the flush suit, their flush
outs are fewer. Always include the discard in our unseen-set bookkeeping (RULES.md exposes it as
`state.variant["discarded"]`).

---

## Implementation sketch (select phase, <50 µs)

1. `flop = board[:3]`; for each of the 3 subsets: `v = eval7.evaluate(subset + flop)`; add draw bonuses.
2. Pick the best subset → `discard_idx`.
3. Exposure: classify the two kept cards (pairs board? suit matches two-tone? rank) and apply the chosen rule
   from S3.2 with the configured randomization (seeded from hand number + cards so it is reproducible in
   histories but not predictable by opponents).
4. Return `Action("select", cards=(discard_idx, reveal_idx))`.
