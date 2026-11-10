# 05 — Opponent modeling

Owner: Claude (main)   Last updated: 2026-11-06

## What we can observe

| signal | source | per hand |
|---|---|---|
| preflop/postflop actions with sizes | `state.events`, `state.history` | every hand |
| exposed card of every player who saw the flop | `reveal` events / `seats[].shown_cards` | every flop |
| both kept cards of everyone at showdown (no mucking) | `show` events | every showdown |
| who timed out | not visible live (only in our own hand-history downloads) | — |
| stack sizes | `seats[].stack` | every turn |

Seats are anonymized per table and memory resets per table, so every model is learned within ≤250 hands and
usually within ~100 useful ones. Use Bayesian counters with priors from the population (hardcoded from hand-history
downloads of earlier rounds, which is allowed: files shipped with the bot).

## Per-seat statistics worth their bytes

| stat | bytes | used for |
|---|---|---|
| hands dealt, hands VPIP, hands PFR | 3 × uint16 | opening range width → preflop adjustments |
| 3-bet count, fold-to-3-bet count | 2 × uint16 | steal/re-steal decisions |
| c-bet count, fold-to-c-bet count | 2 × uint16 | bluff targeting |
| bets/raises postflop, calls postflop, folds postflop | 3 × uint16 | aggression, station detection |
| shoves, calls of shoves | 2 × uint16 | push/fold calibration |
| showdowns seen | uint16 | confidence |
| exposure-rule consistency counts (5 rules) | 5 × uint8 | policy inversion ([[01]] S1.4) |
| keep-rule consistency counts (3 rules) | 3 × uint8 | policy inversion |
| last-seen stack | uint16 | bust/rebuy detection (none here; sanity) |

≈ 40 bytes per seat, 320 bytes per table. Far below the 16 KB; leaves room for a per-hand posterior cache.

---

### S5.1 Infer the exposure rule from showdowns
Status: PROMISING   Evidence: MATH   Owner: unclaimed

For every opponent showdown we observe (flop, exposed E, hidden H). For each candidate rule r, compute whether
r applied to kept {E, H} on that flop would expose E. Increment `consistent[r]` or mark inconsistent. After k
showdowns, a deterministic rule has consistent = k. Also update on *exposure alone* using the "combos
consistent" likelihoods from `calc/h_policy_inversion.py` (how many of the 2,256 (hidden, discard) combos
would produce this exposure under each rule).

Candidate rules: show_high, show_low, show_blank (non-pairing), show_pair, fallback/random. Keep rules:
made-hand-best, highest-two, first-two-dealt (fallback). Note fallback bots show the *first-dealt* card: from
our side that is indistinguishable from random, and their kept pair is random too, so their hands are weaker
than their exposure suggests (they keep junk 2/3 of the time when a better pair existed).

Payoff: on Q72 a show_blank bot exposing the Q has two pair+ 100%; a show_high bot exposing the 2 has trips
100%. These are folds and value-bets nobody else at the table will make correctly.

---

### S5.2 Archetype classification in the first 20 hands
Status: UNTESTED   Evidence: needs LOCAL   Owner: unclaimed

Simple thresholds on VPIP/PFR/aggression after 15–20 hands classify the example bots instantly
(check_or_fold: VPIP≈0 by raise, never bets; min_raiser: PFR≈100%, always min). Real opponents will be
mixtures; use the stats continuously rather than a hard label, with the archetype table in [[04-postflop]] S4.9
as the exploit map.

---

### S5.3 Population priors from hand histories
Status: PROMISING (pipeline works; priors below)   Evidence: LIVE (practice round bd8406dc, 10,405 tables, 148 entries)   Owner: Claude (headmaster)   Last updated: 2026-11-06

After each tournament round, download the hand history, run `starter-kit/hand-history/read.py`-style analysis
to measure: population VPIP/PFR, fold-to-c-bet, how often each exposure rule is consistent, how many bots use
the fallback selection, shove/call frequencies by stack. Ship the resulting priors in `bot/data/`. This is the
feedback loop of the whole project; build the pipeline before round 1.

**Practice round bd8406dc (downloaded 2026-11-07T03:10Z, played by v0).** Pipeline: `python -m arena stats
<download>` → `calc/results/practice-20261107-population.md` (one row per team, 123 teams played); hero view by a
stdlib script following `starter-kit/hand-history/read.py`. Numbers are medians across teams unless noted.

| group | pts/table | VPIP | PFR | 3-bet | saw flop | post agg | post fold | WTSD | W$SD | shove/100 | call share | expose higher | expose pairing card |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top 10 | 22.1 | 34.5% | 26% | 2% | 18% | 38.5% | 19% | 37% | 56% | 6.3 | 10% | 25.5% | 0.5% |
| top 30 | 18.4 | 25% | 22.5% | 2% | 14.5% | 37.5% | 16.5% | 43% | 55% | 5.6 | 7.5% | 23.5% | 1% |
| all 123 | 13.3 | 26% | 19% | 2% | 15% | 32% | 14.5% | 47% | 50% | 4.2 | 9% | 21% | 13% |
| bottom 30 | 7.6 | 35.5% | 14.5% | 3% | 25.5% | 24% | 17% | 47.5% | 45% | 2.8 | 13% | 17% | 50% |
| **room 705 (v0)** | **8.67** | 66% | 31% | 7% | 35% | 35% | 19% | 41% | 46% | 3.6 | 24% | 0% | 58% |

Field facts worth designing for (same file):

- **Field mean 13.0 pts/table**; only 1 of 10,000 tables reached the 250-hand cap, so ICM-at-cap play is irrelevant
  this round. Our median bust was hand 24; 40% of our busts were in blind level 1.
- **Correlation of points with stats across teams:** VPIP −0.37, flops seen −0.47, WTSD −0.41, call share −0.38,
  shove rate −0.36, exposing a 2–5 −0.45, postflop aggression +0.27. Tight, aggressive, not calling, not showing low.
- **Archetypes present:** 4 teams with VPIP ≥ 90% and shove/100 > 50 (pure shovers, 0.9–2.0 pts); 19 teams with
  VPIP ≤ 15% (tight folders, 14–19 pts); 18 teams expose the higher card 0% of the time (deterministic show-low,
  like v0) and 1 team ≥ 90% (show-high). 3-betting is rare everywhere (median 2%).
- **Exposure:** the top 10 almost never expose the card that paired the flop (0.5%); the bottom 30 do it half the
  time. v0's show-low rule does it 58% of the time → [[07-anti-patterns]] A23, open question in [[README]].
- **Our leak by hand type (470,703 hands):** showdown losses −43.7M chips over 35,624 hands against +40.0M won over
  30,740; preflop folds −12.5M (blinds); flop folds −7.6M. Net negative in levels 1–3, positive from level 4 on.

Next: ship these as priors in `bot/data/` (per-archetype thresholds) and re-run after every round.

---

### S5.4 Exploits ranked by expected value against a bot field
Status: UNTESTED   Evidence: reasoning   Owner: unclaimed

1. **Steal from folders.** Many bots fold too much postflop. Fold-to-bet rate above 50% → bet every flop we
   see heads-up regardless of cards.
2. **Value-town stations.** Call share above 40% → never bluff them; bet two pair+ for pot; bet top pair for
   half pot against caps.
3. **Invert deterministic exposures.** S5.1; strongest edge against mid-quality bots that implement a fixed
   "show the X" rule.
4. **Punish fallback selectors.** Their kept pair is random, so their post-flop hands are weak; c-bet and
   barrel them, call down lighter.
5. **Shove on ICM-unaware callers / exploit ICM-aware folders.** Track calls-of-shoves; a bot that calls shoves
   with 30% of hands at the bubble is giving away points to a tight shover; a bot that never calls is giving
   away blinds.

**Arena note (cap-floor-count agent, 2026-11-07).** `bots/cfc-v7-steal` (100-byte per-seat struct: hands, VPIP, postflop decisions/bets/folds; steal 2.5 bb from any class ≥ 1 when every seat still to act is a ≥12-hand folder with VPIP ≤ 20%; probe-bet half pot into a lone opponent with ≥ 8 postflop decisions and 0 bets): pool field −0.03 ±0.17 (exploits never fire); pure check_or_fold field **+0.71 ±0.43, p=0.001** (309 pairs). The plumbing costs ~40 µs and 100 bytes; the exploit pays only at folder-heavy tables. Status: PROMISING for a folder-heavy real field (19/123 teams VPIP ≤ 15%), not a submission.
