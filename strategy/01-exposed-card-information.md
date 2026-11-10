# 01 — The exposed card: caps, counting, and policy inversion

Owner: Claude (main)   Last updated: 2026-11-06
Calculators: `calc/d_reveal_tables.py` (caps), `calc/h_policy_inversion.py` (posteriors), `calc/g_timing.py` (cost).

The agent-output we started from got the core right: **the exposed card bounds the hand**. This file turns that
into four concrete, testable strategies and adds the one the agent missed: inverting the opponent's *policy*.

---

### S1.1 Cap every live opponent, every street
Status: PROVEN   Evidence: MATH + LOCAL (arena, `bots/cap-floor-count-v4b`)   Owner: Claude (cap-floor-count agent)   Last updated: 2026-11-06

**Claim.** For each live opponent compute `cap = max over unseen h of rank(E_opp, h, board)`. If our made
hand beats the cap, we hold the nuts against that opponent and should play for maximum value. If their
cap is one pair and they keep betting, they are bluffing or value-betting one pair; respond accordingly.

**When.** Every postflop decision; strongest on unpaired, non-3-flush boards (78% of flops, ~35% of rivers).

**Numbers.** From [[00-game-model]] §2.3: a missing exposed card on Q♠7♦2♣ gives 0 of 48 hidden cards that make
two pair or better. On K♥8♦8♣ an exposed K is two pair or better 100% of the time (44 two pair, 4 full house).

**Cost.** 45 evaluations ≈ 20 µs per opponent (`calc/g_timing.py`). Fits in 1 ms for all opponents.

**Risks.** None; this is arithmetic. The only error source is forgetting dead cards (folded players' exposures)
when counting the unseen set.

---

### S1.2 Never pay off a visible domination
Status: PROVEN   Evidence: MATH + LOCAL (arena, `bots/cap-floor-count-v4b`)   Owner: Claude (cap-floor-count agent)   Last updated: 2026-11-06

**Claim.** When the board pairs an opponent's exposed card, they hold trips at minimum (two pair+ on a paired
board becomes trips/full house). When the board shows three of their exposed suit and they bet, weight flush
heavily (9 of 45 hidden cards, ~20% prior, higher after aggression). When their *minimum* hand beats our
*maximum* hand, fold regardless of pot odds.

**Mechanism.** Their exposed card plus the board defines a floor as well as a cap. The floor is public.

**Implementation.** `floor = min over unseen h of rank(E_opp, h, board)`; compare with our actual hand.
Also 45 evaluations.

---

### S1.3 River hidden-card counting
Status: PROVEN with the action-conditioned prior; the **uniform prior is REJECTED**   Evidence: LOCAL (arena)   Owner: Claude (cap-floor-count agent)   Last updated: 2026-11-06

**Arena result (2026-11-06, `bots/cap-floor-count*`, paired A/Bs, pool field, log in [[08-experiments]]):**

| version | prior on the hidden card | vs hero | diff ±95% | p |
|---|---|---|---|---|
| v1 | uniform | bot v0 | **−1.71 ±1.21** | 0.006 |
| v3 | bettor = made hand, weight 0.75 | v0-nowar | −0.56 ±0.92 | 0.23 |
| v4b | bettor = made hand (0.9; 1.0 after a raise; 0.5 if they bet earlier), ≥0.75-pot bet or repeated aggression = two pair+ (0.8), call margin 0.05, one-pair gate p_best ≥ 0.75 | v0-nowar | **+1.93 ±0.89** | <0.001 |
| v4b | same | current submission, new seed/field | **+1.46 ±1.04** | 0.006 |

The uniform prior pays off value bets (v1 folded postflop 10% vs 21% for v0 and won 41% vs 48% of its showdowns). The count
is only correct once the hidden card is weighted by what the opponent's bet means; the "refinement" below is the whole strategy.

**Claim.** On the river, the fraction of unseen cards h for which (E_opp, h, board) beats us is our exact
loss probability under a uniform prior. Calling is correct iff that fraction is below pot odds
`bet / (pot + 2·bet)` (heads-up). Multiway: multiply survival across opponents assuming independence (slightly
wrong because they share the unseen pool; acceptable).

**Refinement.** Replace the uniform prior with the policy-inverted posterior (S1.4) and with an action-based
weight (opponents who bet the river hold the top of their range more often; calibrate from
[[05-opponent-modeling]] stats).

**Cost.** 20 µs per opponent.

---

### S1.4 Policy inversion: the exposed card reveals the hidden card *through the opponent's rule*
Status: PROMISING   Evidence: MATH (posteriors computed), needs LOCAL   Owner: Claude   Last updated: 2026-11-06

**Claim.** Bots choose what to expose by a rule. Given a hypothesized rule, enumerate all (hidden, discard)
pairs from the 48 unseen cards (2,256 ordered combos), keep those for which the rule would produce the observed
exposure, and read off the posterior over the hidden card. Deterministic rules collapse the posterior.

**Numbers** (`calc/h_policy_inversion.py`; opponent keeps the made-hand-best pair, exposure rule varies):

Flop Q♠7♦2♣, opponent exposes **Q♥**:

| assumed rule | P(pair) | P(two pair) | P(trips) | combos consistent |
|---|---|---|---|---|
| uniform / fallback | 83.3% | 12.5% | 4.2% | 2256 |
| show higher kept card | 61.3% | 28.1% | 10.6% | 887 |
| show lower kept card | 74.3% | 0% | 25.7% | 366 |
| show the card that misses the board | **0%** | **72.6%** | **27.4%** | 343 |
| show the card that pairs the board | 70.4% | 21.5% | 8.1% | 1159 |

Flop Q♠7♦2♣, opponent exposes **2♥**:

| assumed rule | P(pair) | P(two pair) | P(trips) |
|---|---|---|---|
| show higher kept card | 0% | 0% | **100%** |
| show lower kept card | 68.3% | 22.8% | 8.9% |
| show the card that misses the board | 0% | 0% | **100%** |
| show the card that pairs the board | 88.5% | 0% | 11.5% |

Flop Q♠7♦2♣, opponent exposes **A♥**: under "show lower kept card" the hidden card must rank at least as
high as an ace, so it is another ace: pocket aces 100% (141 combos). Under "show higher kept card" the hidden
card is anything lower: 45% pair, 55% high card.

**Why it is powerful here and not in normal poker.** The showdown rule forces every caller to reveal both kept
cards, so we observe (flop, exposed, hidden) triples for every opponent who reaches showdown. Each triple is
consistent or inconsistent with each candidate rule. Five candidate rules, a handful of showdowns, and the rule
is identified. The "combos consistent" column doubles as the likelihood of each rule given the exposure,
so even without showdowns we can update on which rule they use.

**Candidate rule library** (extend as we see real bots): show_high, show_low, show_blank, show_pair,
fallback (first dealt), show_higher_suit_cover, random. Also the *keep* rule may differ (made hand vs.
highest two vs. first two dealt); test keep rules against showdowns too.

**Cost.** Full inversion = 2,256 × 3 evaluations ≈ 3.6 ms: too slow inside 1 ms. Two workarounds:
(a) the consequences of each rule are mostly *logical* (e.g. "show_blank + exposed card pairs board ⇒ hidden card
also pairs board") and can be hardcoded without evaluations; (b) spread the work: compute once per hand after the
reveal, store the compressed posterior (45 bytes per opponent) in memory, reuse on later streets.

**Risks.** A randomizing opponent defeats inversion; the uniform prior remains correct for them. Mis-identifying
the rule is worse than using the uniform prior, so require a likelihood ratio before trusting a rule.

---

### S1.5 Dead-card accounting
Status: PROVEN (logic)   Evidence: MATH   Owner: Claude   Last updated: 2026-11-06

**Claim.** Every exposed card, including those of players who folded, is dead. With 7 opponents exposing, 13 of
52 cards are known after the flop. Outs and hidden-card enumerations must use the true unseen set, which
shrinks by one per opponent. A flush draw with two of the suit exposed around the table has 7 outs, not 9.

**Implementation.** Maintain `unseen = deck − board − my 3 − all shown_cards`. `state.seats[].shown_cards`
persists for folded seats per RULES.md.

---

### S1.6 Your own exposure is a signal you choose
Status: see [[03-selection]]

The same inversion applies to us. Any deterministic rule we use is learnable and then exploitable by
strong opponents; against weak bots that never read exposures the choice only matters through the
mechanical effects (cap, draw visibility, improvement visibility). The exposure-rule analysis lives in
[[03-selection]] so selection and exposure are decided together.

---

## Quick reference: what an exposure means on the flop (uniform prior, 48 unseen)

| exposed card relative to flop | best possible | P(two pair+) |
|---|---|---|
| pairs an unpaired flop | trips | 16.7% |
| misses an unpaired, non-monotone flop | one pair | 0% |
| suited with a monotone flop | flush | 18.8% (flush 9/48) |
| misses a monotone flop (off-suit) | one pair | 0% |
| the paired rank on a paired flop | quads | 100% (trips+) |
| the unpaired rank on a paired flop | full house | 100% (two pair+) |
| misses a paired flop | trips | 16.7% |
