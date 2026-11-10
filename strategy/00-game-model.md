# 00 — Game model: the rules turned into structural facts

Owner: Claude (main)   Last updated: 2026-11-06
Sources: `starter-kit/RULES.md`, `starter-kit/README.md`, engine source
`starter-kit/sdk/engine/src/poker_engine/variants/flop_discard_reveal.py`, calculators in `calc/`.

## 1. Rules that matter (distilled)

| Rule | Consequence for strategy |
|---|---|
| 3 hole cards, hold'em betting | Preflop ranges are 3-card ranges; everyone flops better than in hold'em |
| After the flop, before flop betting, **everyone simultaneously** discards 1 and exposes 1 of the 2 kept | We cannot react to others' exposures when choosing; we *can* use preflop action |
| Exposed card stays public for the rest of the hand, **even after its owner folds** | Folded players' exposed cards are known dead cards for outs counting |
| Showdown = best 5 of board + 2 kept (0, 1 or 2 hole cards) | Hold'em-style, not Omaha. Board-plays-everything is possible |
| Everyone at showdown reveals both kept cards, no mucking | We learn each opponent's (exposed, hidden) pair every showdown → their selection policy is learnable |
| The discard is never revealed | We never learn what they threw away; policy inference must marginalize over it |
| Winner by folds does not show the hidden card | Bluffs stay secret; only showdowns teach |
| All-in players also select; all-in hands are hidden until the river | No early information from all-in runouts |
| Failed selection → discard the **last-dealt** card, expose the **first-dealt** | A timing-out bot exposes a uniformly random card from a random kept pair (see [[01]]) |
| Selection costs nothing, same time limit (1 ms) | Selection quality is free equity; it just has to be fast |
| 8 players, 2,000 chips, blinds up every 20 hands, 250-hand cap, places pay 50/30/20, ICM at cap | It is a turbo sit-and-go. ICM survival premium dominates mid-game. See [[06-tournament-icm]] |
| Payouts may be a random split of 100 per table | Read `state.config.payouts`, never hardcode 50/30/20 |
| 1 ms per decision, 100 ms time bank per table, ≤16 KB memory, stateless agent | Precompute everything; see [[09-engineering-constraints]] |

Side prizes (do not affect points): *Empty Bluffer* = win without showdown after exposing a 2–5 and raising
after the reveal; *Shover* = bet/raise all in; *Calling Station* = highest call share. Engine check for Empty
Bluffer is literally `shown_card[0] in "2345"` and the winner is in the post-reveal raisers set.

## 2. Structural facts with numbers

### 2.1 Three cards flop much better than two (`calc/a_flop_hits.py`, exact enumeration)

| hand | pair+ on flop | two pair+ | trips+ | flush draw | open-ender |
|---|---|---|---|---|---|
| A K Q rainbow (3 cards) | 58.7% | 12.5% | 3.6% | 3.6% | 3.8% |
| A K offsuit (2 cards, hold'em) | 46.4% | 6.0% | 2.0% | 2.2% | 0.3% |
| J T 9 suited (3) | 59.7% | 15.1% | 6.2% | 9.5% | 21.5% |
| J T suited (2) | 48.2% | 7.8% | 3.8% | 10.9% | 10.4% |
| 8 8 A rainbow (3) | 100% | 28.4% | 13.0% | 3.6% | 1.4% |
| 8 8 (2) | 100% | 28.2% | 12.0% | 2.2% | 1.3% |
| A A A (3, trips) | 100% | 23.6% | 6.4% | 3.6% | 0% |
| A A (2) | 100% | 28.2% | 12.0% | 2.2% | 0% |
| K 7 2 rainbow (3) | 58.3% | 11.4% | 2.5% | 3.6% | 2.1% |
| 9 5 2 rainbow (3, junk) | 59.4% | 12.5% | 3.5% | 3.6% | 5.6% |

Takeaways:
- Any three unpaired cards flop a pair ~59% of the time (vs ~46% for two). **Junk flops pairs as often as AKQ**; what differs is pair *quality* and two-pair/trips frequency.
- Three suited cards give *fewer* flush draws than two suited (9.5% vs 10.9%): the third suited card is a blocker to your own suit. Three suited is not a flush hand, it is a flexibility hand.
- Pocket trips (AAA) are strictly worse than AA for making sets (6.4% vs 12%) and two pair+ (23.6% vs 28.2%). One ace left in the deck.
- A pair + kicker is roughly a pair; the kicker adds flexibility, not flop hits.

### 2.2 Showdown hands are much stronger (`calc/f_showdown_value.py`, 30k runouts, everyone sees the river, oracle keep)

Winning hand category at showdown:

| players | cards | high card | pair | two pair | trips | straight | flush | full house+ | **P(≤ one pair wins)** |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 2 (hold'em) | 5.8% | 36.9% | 31.6% | 7.5% | 7.8% | 5.2% | 5.4% | **42.6%** |
| 2 | 3 (this game) | 1.0% | 20.9% | 36.2% | 8.8% | 13.6% | 9.7% | 9.8% | **21.9%** |
| 4 | 2 | 0.6% | 24.1% | 33.9% | 11.1% | 12.9% | 8.3% | 9.1% | 24.7% |
| 4 | 3 | 0.0% | 7.4% | 28.9% | 11.9% | 20.0% | 14.5% | 17.4% | **7.4%** |
| 8 | 3 | 0.0% | 0.9% | 14.2% | 12.2% | 25.5% | 20.1% | 27.2% | 0.9% |

Oracle keep (choosing with river knowledge) inflates these a little, but the direction is unambiguous:
**one pair is a bluff-catcher, not a value hand**, even heads-up. Straights and flushes are twice as common as in hold'em. Hands that win are two pair and better.

### 2.3 The exposed card caps a hand (`calc/d_reveal_tables.py`, exact)

Observer sees the flop and one exposed card E; the hidden card is one of 48 (45 from a player's seat).

| flop | E | best possible hand | P(≥ two pair) | hidden-card breakdown |
|---|---|---|---|---|
| Q♠7♦2♣ | Q (pairs board) | trips | 16.7% | trips 2, two pair 6, pair 40 |
| Q♠7♦2♣ | A, K, 9, 4 (misses) | **one pair** | **0%** | pair 12, high card 36 |
| J♠T♠4♦ | J | trips | 16.7% | trips 2, two pair 6, pair 40 |
| J♠T♠4♦ | Q♠, 9♠, A♠, K (misses) | **one pair** | 0% | pair 12, high card 36 (draws not counted) |
| K♥8♦8♣ (paired) | 8 | quads | 100% | quads 1, full house 3, trips 44 |
| K♥8♦8♣ | K | full house | 100% | full house 4, two pair 44 |
| K♥8♦8♣ | A (misses) | trips | 16.7% | trips 2, two pair 6, pair 40 |
| 9♥6♥2♥ (monotone) | A♥ (suit) | flush | 18.8% | flush 9, pair 12, high card 27 |
| 9♥6♥2♥ | A♦ (misses) | one pair | 0% | pair 12, high card 36 |

Rule: **an exposed card that neither pairs the board nor shares a 3-flush suit caps its owner at one pair on the flop.** On the river Q♠7♦2♣T♥4♠, a Q exposed is 30% two pair+ (12 of 46), any miss is still capped at one pair.

How often does the cap hold? Flops: 17.1% paired, 5.2% monotone → ~78% of flops cap a missing exposed card at one pair. Rivers: 49.1% paired, 37.2% have 3+ of a suit (`calc/d_reveal_tables.py`) → on roughly a third of rivers the hard cap is still "one pair", on paired boards it is "trips", on 3-flush boards it is "flush only if E is that suit, else one pair/trips".

The cap is cheap to compute live: `max(eval7.evaluate([E, h] + board) for h in unseen)` is 45 evaluations ≈ 20 µs.

### 2.4 Tournament clock (`calc/e_tournament.py`)

| hands | blinds | avg stack (BB) with 8 / 6 / 4 / 3 players |
|---|---|---|
| 1–20 | 10/20 | 100 / 133 / 200 / 267 |
| 21–40 | 20/40 | 50 / 67 / 100 / 133 |
| 41–60 | 30/60 | 33 / 44 / 67 / 89 |
| 61–80 | 50/100 | 20 / 27 / 40 / 53 |
| 81–100 | 80/160 | 12.5 / 17 / 25 / 33 |
| 101–120 | 125/250 | 8 / 11 / 16 / 21 |
| 121–140 | 200/400 | 5 / 7 / 10 / 13 |
| 141–160 | 300/600 | 3.3 / 4.4 / 6.7 / 8.9 |
| 161+ | 500/1000 and up | all-in every hand |

Deep-stack poker lasts ~60 hands. Hands 60–100 are a 12–20 BB stealing game. From hand ~100 it is push/fold. The 250-hand cap is practically never reached; tables end by blinds. ICM details in [[06-tournament-icm]].

## 3. Who knows what (information structure)

| information | you | each opponent | everyone |
|---|---|---|---|
| your 3 dealt cards, your discard | ✓ | ✗ | ✗ |
| your exposed card | ✓ | ✓ | ✓ |
| your hidden card | ✓ | ✗ until showdown | ✗ |
| opponents' exposed cards, including folded players' | ✓ | ✓ | ✓ |
| preflop action of every player | ✓ | ✓ | ✓ |
| which card a player exposed given their 3 cards (their *policy*) | learnable from showdowns | learnable | learnable |

From your seat, after the flop with k opponents still in, unknown cards = 52 − 3 (board) − 3 (yours) − k (exposed) − (folded players' exposed cards). Each live opponent's hidden card is one of those. **Hand reading is enumeration, not range guessing.**

## 4. What this implies at the highest level

1. Selection quality is free equity every hand you see a flop (~59% of flops give a pair; choosing *which* pair/draw is the skill). See [[03-selection]].
2. Showdown value is inflated: tighten call-downs with one pair, widen value bets with two pair+. See [[04-postflop]].
3. The exposed card is a hard constraint, not a tell. Compute caps and hidden-card counts live. See [[01-exposed-card-information]].
4. Opponents' exposures leak their *policy* within a few showdowns; deterministic bots leak a lot. See [[05-opponent-modeling]].
5. The clock turns the game into push/fold by hand 100; ICM makes early coin flips losing. See [[06-tournament-icm]].
