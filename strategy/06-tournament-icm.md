# 06 — Tournament structure: blind clock, ICM, push/fold

Owner: Claude (main)   Last updated: 2026-11-06 (push/fold sections: Claude, icm-pushfold agent)
Calculators: `calc/e_tournament.py` (Malmuth-Harville ICM, blind table), `calc/i_pushfold_tables.py` (hand-vs-range equity, Nash shove/call grid).

## The clock

8 players × 2,000 = 16,000 chips. Blinds rise every 20 hands. Average stack in big blinds:

| hands | blinds | 8 left | 6 left | 4 left | 3 left | game phase |
|---|---|---|---|---|---|---|
| 1–20 | 10/20 | 100 | 133 | 200 | 267 | deep: postflop skill, exploit, avoid flips |
| 21–40 | 20/40 | 50 | 67 | 100 | 133 | deep |
| 41–60 | 30/60 | 33 | 44 | 67 | 89 | medium |
| 61–80 | 50/100 | 20 | 27 | 40 | 53 | steal/re-steal; 3-bet shoves appear |
| 81–100 | 80/160 | 12.5 | 17 | 25 | 33 | push/fold begins for average stacks |
| 101–120 | 125/250 | 8 | 11 | 16 | 21 | push/fold |
| 121–140 | 200/400 | 5 | 7 | 10 | 13 | shove any two... three |
| 141–160 | 300/600 | 3.3 | 4.4 | 6.7 | 8.9 | crapshoot |
| 161–250 | 500/1000 → 2000/4000 | <2 | | | | tables end here; cap rarely reached |

Expect most of the points to be decided between hands 60 and 140. **Deep-stack edge has ~60 hands to work; push/fold
quality has ~60 hands too, with far bigger pots.** Both matter; push/fold is cheaper to get exactly right.

## ICM: chips are not points

Payouts 50/30/20 (always read `state.config.payouts`; a round may use a random split). Equity by Malmuth-Harville.

| situation | equity now | win | lose | break-even equity to put stacks in | chip-EV says |
|---|---|---|---|---|---|
| hand 1, 8 × 2000, flip for full stacks | 12.50 | 22.50 | 0 | **55.6%** | 50% |
| 6 left, equal 2667 | 16.67 | 28.67 | 0 | 58.1% | 50% |
| 4 left (bubble), equal 4000 | 25.00 | 38.33 | 0 | **65.2%** | 50% |
| 4 left, I am short (2000 vs 4667s), vs one of them | 15.21 | 25.40 | 0 | 59.9% | 50% |
| 4 left, I am big (7000) vs a 3000 | 34.60 | 41.63 | 25.70 | 55.8% | 50% |
| 3 left (all paid), equal 5333 | 33.33 | 43.33 | 0 | **76.9%** | 50% |
| 5 left, big (6000) vs short (1500) | 31.02 | 35.83 | 25.60 | 52.9% | 50% |

Reading the table:
- Doubling on hand 1 is worth ×1.8, not ×2. A 52/48 edge for stacks is a **losing** play in points.
- The bubble (4 left) needs 65% to call off an equal stack. Nobody has 65% preflop in a 3-card game without
  a big pair vs. a dominated hand, so: **at 4-handed equal stacks, calling all-ins is almost always wrong;
  shoving first is right** (the shover only needs fold equity plus the chance the caller is wrong).
- Once in the money (3 left), the 50/30/20 structure still makes a flip for stacks need 77%. Play for 1st
  by stealing, not by flipping.
- Big stack vs. short stack: break-even drops toward 53–56%. **The chip leader should attack shorts,
  mid-stacks should fold around them.** Classic SNG dynamics apply.

Points at the 250-hand cap are the ICM split, so chip share, not place, counts there; irrelevant in practice (blinds end tables first).

---

### S6.1 Phase-aware aggression schedule
Status: PROMISING (field-dependent)   Evidence: LOCAL (arena A/B; +2.2 in the kit field twice, −1.9 ±2.2 n.s. in the archetype field)   Owner: Claude (icm-pushfold agent)   Last updated: 2026-11-07

**Arena result.** `bots/icm-pushfold-v7` = `bot/` (v0-nowar) with the <= 15 BB-effective phase replaced by
table-driven ICM push/fold (S6.2) plus per-seat call/raise rates: **+0.82 ±0.56 pts/table vs bot
(p = 0.004, 60 better / 308 tied / 29 worse, seed icm1, field min_raiser + check_or_fold)**; `08-experiments.md`
2026-11-06 "v7 rerun". **Grafted onto `cap-floor-count-v6` (the active submission) as `bots/icm-pushfold-v9`: +2.33 ±0.58 vs that bot (p < 0.001, 116 / 251 / 30, 0 failures for either bot, seed icm1, 397 pairs).** The deep phase (> 18 BB effective) is left to the base bot: v2–v4 showed that ICM
arithmetic at deep stacks, even with a survival premium, calls raise-war all-ins with top-17 % hands and busts in
level 1 twice as often as the base (474 deep all-in calls vs 52 in 397 tables) → A24 in [[07-anti-patterns]].
**Archetype field (v0-baseline, check_or_fold, arch-folder, arch-shover, arch-station — the field shaped like the practice round):** v9 vs cap-floor-count-v6 −1.85 ±2.22 (n.s., 331 pairs, seed icm6); and fp-v2 beats v9 by +4.29 ±1.45 (819 pairs). So the module's gain is specific to the kit field (a 100 % caller and a 100 % folder, where per-seat call rates are worth a lot) and does not show against tight folders, shovers and stations. `bots/icm-pushfold-v10` = fp-v3 (live bot) + module: archetype field −0.97 ±1.04 (p=0.068, 328 pairs), kit field +1.27 ±0.78 (p=0.001, 397 pairs) — same pattern; **not promoted, fp-v3 stays.** The module is worth shipping only if the real field's hand histories (05 S5.3) show a population of stations and pure folders at short stacks.
The real tournament field (05 S5.3: median bust hand 24) makes the deep phase the bigger lever; this entry only
covers the short-stack phase.

**Claim.** Switch strategy by effective stack in BB (not by hand number): >30 BB small-ball with strict
no-flip rule (need ≥56% to commit stacks early); 15–30 BB steal-oriented, 3-bet/fold; ≤12 BB
push/fold with ICM-adjusted ranges; ≤5 BB shove any hand above the bottom third from any position.

**Risks.** Mis-estimating opponents' calling ranges; pure Nash assumes rational callers, while bot
callers are often far too tight (check_or_fold-type) or too loose (calling stations). Track call-vs-shove rates per seat.

---

### S6.2 Push/fold ranges for 3-card hands
Status: PROVEN (tables SIM; bot LOCAL via S6.1)   Evidence: SIM + LOCAL   Owner: Claude (icm-pushfold agent)   Last updated: 2026-11-06

**Built.** `calc/i_pushfold_tables.py` → `calc/results/i_hand_vs_range.csv` (1,755 classes × equity vs the
top {2,5,8,12,16,20,25,30,40,50,65,80,100} % of dealt hands, 3,000 runouts each, ±0.9 %; plus eq vs 3 / 7 random
opponents) and `calc/results/i_pushfold_nash.csv` / `i_pushfold_tables.md` (chip-EV shove/call fixed point,
single-caller approximation, pot 1.5 BB, by effective stack S and players behind N). Selected cells, shove % / call %:

| S vs N | 1 | 2 | 3 | 5 | 7 |
|---|---|---|---|---|---|
| 5 BB | 89 / 74 | 69 / 60 | 57 / 52 | 42 / 38 | 31 / 27 |
| 8 BB | 80 / 56 | 54 / 37 | 40 / 27 | 25 / 16 | 17 / 11 |
| 10 BB | 73 / 48 | 48 / 30 | 35 / 20 | 21 / 12 | 15 / 8 |
| 13 BB | 68 / 39 | 42 / 22 | 28 / 14 | 17 / 9 | 11 / 5 |
| 16 BB | 61 / 33 | 36 / 17 | 24 / 12 | 14 / 6 | 7 / 4 |

Heads-up at 10 BB the shover goes with 73 % of hands: the 3-card game is flatter than hold'em (one pair rarely
wins, every hand has draws), so push/fold ranges are much wider than hold'em intuition. How the bot uses them:
callers' call % is the Nash prior blended with the seat's observed continue-vs-raise rate (10-decision prior);
the shove decision is `P(no call)·ICM(me+pot) + P(call)·[eq·ICM(win) + (1−eq)·ICM(lose)] >= ICM(fold) + premium`
with Malmuth-Harville ICM on the live stacks (numba, 2.6 µs per call) and `state.config.payouts`.

**Plan.** Use `calc/results/b_preflop_classes.csv` (heads-up equity of every 3-card class with oracle
selection) as the hand-strength order. For each (stack in BB, players behind, ICM factor) solve the
shove-or-fold equilibrium against a caller who calls with the top X% of classes, iterating X to the Nash
fixed point. Deliverable: a shove-threshold table indexed by percentile, loaded by the bot at import.

**Caveat.** Preflop all-ins still go through selection at the flop; both players pick after seeing the flop,
so "all-in equity" is the oracle-ish 3-vs-3 equity, not hold'em 2-vs-2. Our class table already models that.

---

### S6.3 Bubble play: fold to aggression, be the aggressor
Status: PROVEN (logic)   Evidence: MATH   Owner: Claude

With 4–5 left and similar stacks, the break-even to call off is 60–65%. Open-shove wide against players
who respect ICM (they must fold almost everything), fold to shoves unless we hold the top ~5% of classes or
the shover is a maniac. Against a short stack who must shove any two, call wider (our break-even is near 53%).

---

### S6.5 Survival premium on top of ICM
Status: PROMISING   Evidence: LOCAL (parameter sweep, 300 pairs per cell)   Owner: Claude (icm-pushfold agent)   Last updated: 2026-11-06

ICM assumes equal skill. In a field of simple bots that bust each other, folding is worth more than ICM(fold), so
the bot requires an edge of `PREMIUM × ICM(fold) × (players − 2)/6` (× 1.5 per extra committed player) before
committing a short stack. Sweep vs `bot` (v0-nowar), seed icm3, 300 pairs, everything else as v7:
PREMIUM 0 → +0.39 ±0.52 (ns); 0.15 → +0.65 ±0.48 (seed icm1); 0.30 → +1.40 ±0.63; 0.50 → +1.52 ±0.65.
Push/fold zone: PUSH_MAX 10 → +0.58, 13 → +0.65 (icm1), 15 → +1.57 ±0.67, 18 → +1.69 ±0.68. Both trends are
within each other's error bars at the top; v7 ships 15 / 0.30, v8 tests 18 / 0.50. Open: the premium is a
field-dependent fudge; measure it against the real field's hand histories (05 S5.3).

---

### S6.4 Survival vs. accumulation: the 50/30/20 structure favors accumulation more than a 50/30/20 *cash* SNG does
Status: UNTESTED   Evidence: needs SIM   Owner: unclaimed

The tournament score is the sum of points over many tables. Points are linear, so maximizing expected points
per table is the goal and ICM is the right model. But ICM equal to 12.5 per seat means an 8th place is 0 and 1st
is 50; a strategy that takes 3rd often (20) versus one that takes 1st sometimes should be compared by expected
points, not by survival. Needs a local-tournament A/B between a "ladder" bot and an "accumulate" bot.

---

## Open items
- ~~Build S6.2 shove tables~~ done (`calc/i_pushfold_tables.py`).
- ~~Calibrate fold equity~~ done per seat at runtime (observed continue-vs-raise and raise rates in memory, S6.1 bot);
  still open: population priors from real hand histories (05 S5.3) instead of the Nash prior.
- Multiway all-in equity is a scaling heuristic (eq vs 1 → vs 3 / vs 7 columns); an exact hand-vs-two-ranges table would be better.
- Check `state.config.payouts` variability in sample histories (`hand-history/CASES.md`: `varying_payouts`).
