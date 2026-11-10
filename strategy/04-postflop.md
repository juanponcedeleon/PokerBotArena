# 04 — Postflop: betting with public information

Owner: Claude (main)   Last updated: 2026-11-06
Inputs: [[01-exposed-card-information]] (caps, counting), [[00-game-model]] §2.2 (showdown values).

Postflop in this game is **enumeration + a betting policy**. Every opponent is one hidden card from a set we
can list. The strategies below are ordered by how much of the decision they decide.

---

### S4.1 Beat the cap → bet for maximum value
Status: PROVEN   Evidence: MATH + LOCAL (arena, `bots/cap-floor-count-v4b`, see [[01-exposed-card-information]] S1.3 table)   Owner: Claude (cap-floor-count agent)   Last updated: 2026-11-06

If our made hand beats `cap(opponent)` (their best possible hand, [[01]] S1.1), we cannot lose to them. Bet
the size that maximizes expected calls given their type (calling stations: pot or more; folders: a third pot
and let them bluff-catch). Multiway: the pot-size bet is right against the union of caps when we beat *every*
cap. Do not slow-play: there is no risk, only the risk of giving a free card to someone whose cap can rise
(paired turn, third suit card).

Typical triggers: our two pair vs. an opponent who exposed a blank on an unpaired flop (their cap = one pair);
our trips vs. anyone whose exposure misses a paired board; our flush vs. an off-suit exposure on a 3-flush board.

---

### S4.2 Never call below the floor
Status: PROVEN   Evidence: MATH + LOCAL (arena, `bots/cap-floor-count-v4b`, see [[01-exposed-card-information]] S1.3 table)   Owner: Claude (cap-floor-count agent)   Last updated: 2026-11-06

If `floor(opponent)` (their worst possible hand) beats our hand, fold to any bet. Board pairs their exposed
card: trips minimum. Board shows their exposed rank twice: quads-or-full-house minimum. Check what the floor is
before calling anything on a paired turn or river.

---

### S4.3 River bluff-catching by counting
Status: PROVEN only with the bettor-weighted count (uniform prior REJECTED: −1.71 ±1.21, p=0.006)   Evidence: LOCAL (arena, numbers in [[01-exposed-card-information]] S1.3)   Owner: Claude (cap-floor-count agent)   Last updated: 2026-11-06

`lose = #{h ∈ unseen : rank(E, h, board) > ours} / |unseen|`, weighted by the inverted-policy posterior when
available. Call iff `1 − lose ≥ bet / (pot + 2·bet)` adjusted by the opponent's bluff frequency (from
[[05-opponent-modeling]]): multiply the "beats us" mass by their observed value-bet ratio and the "loses" mass
by their bluff ratio. Against a bot that never bluffs (most simple bots), `lose` alone decides. Against the
`min_raiser` example that always raises, `lose` is irrelevant: the raise carries no information, so call with
any hand above the median of the hidden-card distribution.

Cost: 20 µs per opponent.

---

### S4.4 One-pair discipline
Status: PROVEN   Evidence: SIM (`calc/f_showdown_value.py`) + LOCAL (arena: value-betting one pair only at p_best ≥ 0.75 is +0.64 over the 0.60 gate, v4b vs v4a, same seed/field; each vs v0-nowar +1.93 / +1.29)   Owner: Claude (cap-floor-count agent)   Last updated: 2026-11-06

One pair wins 22% of heads-up all-see-river showdowns and 7% four-way. Policy:
- Bet one pair for value only when the opponent is capped at a worse pair or at high card (their exposure misses
  the board and is lower than our pair) or when the opponent is a known station.
- Otherwise one pair is a bluff-catcher: check, call small bets when the count says so, fold to large river bets
  from capped-but-uncapped-later opponents who show aggression.
- Top pair with a hidden kicker vs an opponent whose exposed card pairs the same rank: compare kickers via
  enumeration; do not assume we are ahead.

---

### S4.5 Bluffing: credentials and targets
Status: PROMISING   Evidence: MATH (ranges) + needs LOCAL   Owner: unclaimed

Bluff when all three hold:
1. **Credential.** Our exposure makes a hand that beats their likely holding plausible: our exposed card pairs
   the board, or is an overcard that could be top pair, or is the suit of a 3-flush board.
2. **Target is weak and capped.** Their exposure misses the board (cap = one pair) and they have shown no
   strength; or they are a bot with a high fold-to-bet rate.
3. **Not a station.** Fold-to-bet rate above ~40% at the current street (default prior until measured: assume
   bots fold a lot to large bets postflop, the two examples do: check_or_fold folds to any bet).

Never bluff someone whose floor beats our best possible hand (they will not fold what cannot lose), nor
multiway into two uncapped exposures.

Sizing: against bots, size bluffs to the opponent's fold threshold, not to balance. Learn the threshold
(fold-to-half-pot vs fold-to-pot) per seat.

---

### S4.6 Scare cards work both ways
Status: PROVEN (logic)   Evidence: MATH   Owner: Claude

- Turn/river pairs **our** exposed card: everyone sees "trips possible" (2 of 45 hidden cards make it, but the
  fear is public). This is the best bluff card in the game; barrel.
- Turn/river pairs **their** exposed card: their floor is trips. Fold without a boat or better unless the count
  says otherwise (it will not).
- Third suit card lands, we exposed that suit: our hidden card is the suit 9/45 ≈ 20% a priori, but the threat
  is credible. Barrel against capped opponents.
- Third suit card lands, they exposed off-suit: they cannot have the flush with only 3 on board. Keep value
  betting pairs and two pair.

---

### S4.7 Draws: count real outs
Status: PROVEN (logic)   Evidence: MATH   Owner: Claude

Outs are exact: unseen = 52 − board − our 3 (including the discard) − every exposed card at the table. A flush
draw with two of our suit exposed elsewhere has 7 outs out of ~41 unseen, not 9 of 47. Use the exact fraction
against pot odds and implied odds; implied odds are high against stations and nil against folders.

---

### S4.8 Multiway pots
Status: PROMISING   Evidence: SIM (showdown distribution)   Owner: unclaimed

Three-card hands mean more players continue to the flop. In 4-way all-see-river showdowns two pair wins only
29% and one pair 7%. In multiway pots: value-bet two pair only against caps; check one pair; semi-bluff nut
draws, not weak draws; fold medium hands to two bets. The exposed cards tell us which opponents are capped,
so "multiway" is really "how many uncapped opponents".

---

### S4.9 Betting policy vs bot archetypes
Status: UNTESTED   Evidence: needs LOCAL   Owner: unclaimed

| archetype | detect by | exploit |
|---|---|---|
| check-or-fold (never bets, folds to bets) | zero bets/raises over N decisions | bet every street with any hand; never call anything they bet (they never bet) |
| min-raiser (always min-raises) | raise frequency ≈ 100%, always min | raises carry no information; call down with median+ hands; value-bet big; never bluff |
| calling station | high call share | value-bet thin and big; no bluffs |
| tight-passive | low VPIP, low aggression | steal blinds relentlessly; fold to their raises |
| maniac | high aggression all streets | call down with top-of-range; let them bluff |
| exposure-reader | folds correctly when we show strength, attacks our caps | randomize exposure (R1); use caps against them |

---

## Decision pipeline per street (target < 300 µs)

1. Build `unseen` (dead-card accounting).
2. Our hand rank `ours = evaluate(kept + board)`.
3. For each live opponent: enumerate hidden cards → `cap`, `floor`, `lose_frac`, posterior weights if a policy
   is identified. (20 µs each on the river; on flop/turn use the made-hand distribution and outs, not runouts.)
4. Classify situation: beat-all-caps / below-a-floor / contested.
5. Choose action by situation and archetype table; size by stack depth and opponent fold thresholds.
6. Clamp to legal actions; update memory counters.
