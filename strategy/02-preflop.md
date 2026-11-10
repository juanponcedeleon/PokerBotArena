# 02 — Preflop: 3-card hand classes and ranges

Owner: Claude (main)   Last updated: 2026-11-06
Calculators: `calc/b_preflop_classes.py` → `calc/results/b_preflop_classes.csv` (all 1,755 classes),
`calc/b_summarize.py` → `calc/results/b_preflop_summary.md` (tables below).

## Method and caveats

- Every 3-card class (13 trips, 156 pair+kicker rainbow, 156 pair+kicker with the kicker suited to one pair
  card, 286 rainbow, 3 × 286 two-suited variants, 286 three-suited) = 1,755 classes covering all 22,100 deals.
- 1,500 all-in-preflop runouts per class vs 1, 3 and 7 random opponents; everyone keeps the oracle-best 2 of 3
  at the river. Oracle is optimistic for everyone equally; **the ranking is reliable, the absolute values are
  upper bounds.**
- Standard error ≈ ±1.3% on heads-up equity, ±0.9% 8-way. Neighbouring rows in the top-40 are statistically
  tied. Treat the table as tiers, not an exact order. Rerun with more trials before building shove tables.

## Headline results

### Average equity by structure

| structure | classes | vs 1 | vs 3 | vs 7 | fair share: 50 / 25 / 12.5 |
|---|---|---|---|---|---|
| pair + kicker suited to a pair card | 156 | 59.5% | 31.5% | 16.8% | best |
| pair + kicker rainbow | 156 | 57.4% | 28.2% | 13.8% | |
| two suited (top two) | 286 | 49.3% | 25.4% | 13.4% | |
| two suited (top + bottom) | 286 | 49.4% | 25.5% | 13.3% | |
| two suited (bottom two) | 286 | 49.2% | 25.2% | 12.7% | |
| three suited | 286 | 48.0% | 24.1% | 12.4% | **not better than two suited** |
| rainbow, no pair | 286 | 46.8% | 22.0% | 10.1% | |
| trips | 13 | 49.0% | 19.4% | 7.4% | **worst structure** |

### What the third card is worth (selected classes, percentile is 8-way among the 1,755 classes)

| hand | vs 1 | vs 3 | vs 7 | percentile | lesson |
|---|---|---|---|---|---|
| AAKs | 73.9% | 46.2% | 23.4% | top 1% | pair + live suited kicker is the premium |
| AAKr | 73.3% | 42.6% | 20.4% | top 3% | |
| AA2r | 73.4% | 44.3% | 20.6% | top 2% | the kicker barely matters heads-up |
| AAA | 70.8% | 37.1% | 14.1% | top 31% | pocket trips are a *weak* AA: one ace left |
| KKK | 66.4% | 31.9% | 12.9% | top 45% | |
| QQQ | 62.6% | 29.5% | 10.1% | top 81% | |
| 888 | 50.0% | 16.6% | 6.2% | top 99% | low trips are among the worst hands dealt |
| 88As | 61.2% | 31.8% | 16.8% | top 11% | mid pair + suited ace plays well multiway |
| 88Ar | 61.7% | 28.6% | 12.1% | top 56% | same hand rainbow: 8-way equity drops a third |
| 882r | 52.0% | 21.1% | 10.2% | top 81% | pair + dangler is a weak pair |
| AKQsss | 57.8% | 33.0% | 18.7% | top 5% | best unpaired hand |
| AKQr | 57.9% | 32.9% | 16.2% | top 13% | |
| KQJsss | 59.7% | 33.8% | 18.8% | top 5% | |
| JT9sss | 53.8% | 29.6% | 17.1% | top 9% | connected three-suited: good 8-way, mediocre heads-up |
| JT9r | 51.4% | 27.6% | 16.3% | top 13% | |
| AK2r | 53.0% | 25.5% | 11.7% | top 60% | the dangler turns AK into an average hand |
| A72r | 45.7% | 20.4% | 8.4% | top 94% | ace-rag-rag is junk |
| 765sss | 43.2% | 22.9% | 12.4% | top 51% | small suited connectors: fold heads-up, ok multiway cheap |
| 732r | 33.3% | 12.8% | 5.1% | bottom | |

### Hand strength as percentiles of *dealt* hands (frequency-weighted, heads-up equity)

| at least this strong | HU equity | % of deals |
|---|---|---|
| KKQr | 71% | top 2% |
| JJ8s | 66% | top 5% |
| AK7 with AK suited | 59% | top 10% |
| QT8 with Q8 suited | 57% | top 15% |
| QJ9 rainbow | 55% | top 20% |
| JT8 with JT suited | 54% | top 25% |
| AT2 with A2 suited | 53% | top 30% |
| JT9 rainbow | 51% | top 40% |
| 976 with 97 suited | 49% | top 50% |
| Q73 with Q3 suited | 45% | top 75% |

Pairs are 13 × 12 × 6 × 2 + 13 × 4 = 1,924 of 22,100 deals (8.7%) with a kicker, plus trips 0.2%. So roughly:
**the top 9% of deals are pairs, and almost every pair beats almost every non-pair.** Below pairs, three high
cards and three connected/suited cards form the next 15%.

---

### S2.1 Percentile-based opening ranges
Status: UNTESTED   Evidence: SIM (ranking only)   Owner: unclaimed

**Claim.** Open-raise by percentile of the heads-up/4-way class table, tightening with players behind. Proposal
to test (8-handed, >25 BB):

| position | open | roughly |
|---|---|---|
| UTG / UTG+1 | top 10% | all pairs; AKx suited; AKQ, AKJ, KQJ-type three-broadway |
| MP / HJ | top 15% | + three broadway rainbow, A-x-x two-suited with two broadways |
| CO | top 22% | + suited connected trios JT9s, T98s, suited pair-less Ax-broadway |
| BTN | top 32% | + most two-suited connected hands, Kxx with two suited |
| SB (vs BB only) | top 28% | |
| BB | defend by price; 3-bet top 6% | |

**Why not wider.** Everyone flops a pair ~59% of the time, so a marginal hand's pair is dominated far more often
than in hold'em; and one pair rarely wins at showdown ([[00-game-model]] §2.2). Hands that make two pair, trips,
straights and flushes (pairs, suited connectors, three broadway) are the ones to open.

**Needs.** A local A/B of 10/15/22/32 against 8/12/18/26 and 12/18/26/38.

---

### S2.2 Pairs are the value 3-betting range; trips are not
Status: PROVEN (SIM ranking)   Evidence: SIM   Owner: Claude

**Claim.** 3-bet for value with TT+ (any kicker) and AA/KK/QQ-with-suited-kicker; flat or fold small pairs
multiway unless cheap. Pocket trips: treat AAA/KKK as a medium pair (top 31–45%), never as a monster; QQQ and
below are near-folds in early position. Also: never shove preflop with 888-type trips thinking "I have three
of them" (bottom 1% 8-way).

---

### S2.3 Suited kicker bonus
Status: PROVEN (SIM)   Evidence: SIM   Owner: Claude

A kicker suited to a pair card adds ~2% heads-up and ~3% 8-way equity to any pair (88As top 11% vs 88Ar top
56%). Multiway, prefer calling with pair+suited kicker and 3-betting with pair+suited ace; rainbow pair+dangler
is a 3-bet-or-fold hand (pair value only).

---

### S2.4 Danglers make hands average
Status: PROVEN (SIM)   Evidence: SIM   Owner: Claude

AK2r is top 60%; AKQr is top 13%. The third card has to *work*: pair the others, be suited to one of them, or
connect. Unconnected rainbow trios are the bottom third of all deals regardless of one high card.

---

### S2.5 Preflop all-in equity lookup (feeds push/fold)
Status: PROVEN   Evidence: SIM (`calc/i_pushfold_tables.py`, 3,000 runouts per cell, ±0.9 %)   Owner: Claude (icm-pushfold agent)   Last updated: 2026-11-06

**Done.** `calc/results/i_hand_vs_range.csv`: every class vs a caller drawn from the top X % of dealt hands,
X in {2,5,8,12,16,20,25,30,40,50,65,80,100}, plus the eq-vs-3 / eq-vs-7 random columns. Selected rows
(`calc/results/i_pushfold_tables.md` has more):

| hand | pct | vs top 5 % | vs top 20 % | vs top 50 % | vs any |
|---|---|---|---|---|---|
| AAKs | 0.6 | 0.75 | 0.77 | 0.74 | 0.74 |
| KKK | 4.5 | 0.48 | 0.60 | 0.65 | 0.68 |
| 88As | 7.5 | 0.37 | 0.48 | 0.56 | 0.63 |
| AKQr | 12.0 | 0.40 | 0.52 | 0.57 | 0.58 |
| JT9sss | 26.5 | 0.30 | 0.41 | 0.48 | 0.53 |
| 732r | 99.9 | 0.23 | 0.29 | 0.31 | 0.34 |

Used by `bots/icm-pushfold-v7` (06 S6.1/S6.2). Open: a hand-vs-two-ranges table for multiway all-ins.

The class table gives us each 3-card hand's equity vs 1 random hand. For push/fold we need equity vs a
*calling range* (top X%), which the current script does not compute. Next step: a hand-vs-range script that
samples the caller's hand from the top X% of classes (frequency-weighted) and produces `eq(hand, X)` for
X ∈ {5, 10, 15, 20, 30, 50, 100}. Then solve S6.2 in [[06-tournament-icm]].

---

## Implementation notes
- Map any 3 cards to a class key: sort ranks descending; detect pair/trips; suit pattern = which pairs of
  positions share a suit (for a pair, "kicker suited to a pair card" is a single pattern). Dictionary of 1,755
  entries → (eq1, eq3, eq7, percentile). Lookup cost: microseconds.
- Rerun `b_preflop_classes.py 6000` (≈5 min) before shipping tables to halve the noise.
