# fp-v1 — first-principles bot (candidate)

**Owner:** Claude (keep-rule agent, branching out), 2026-11-06.  **Status: superseded by `bots/fp-v3` (same design + GC tuning + ICM-tight deep all-in calls).**

## Why this design (first principles + the practice round)

The practice round (`calc/j_practice_deepdive.py` → `calc/results/j_practice_deepdive.md`, 10,405 tables, 123 teams)
says what wins in this field:

| what the top 10 do | top 10 | all | v0 (us, 8.7 pts) |
|---|---|---|---|
| VPIP / open-raise per hand / limp | 38% / 26% / 2% | 33% / 17% / 5% | 75% / 26% / 27% |
| open size | 2.5 BB | 2.5 BB | 2.5 BB |
| 3-bet, 4-bet+ per hand | 3%, 0% | 3%, 1% | 6%, 3% |
| shove per hand at <= 7 BB / 7-12 BB | 31% / 30% | 15% / 18% | 52% / 39% |
| call an all-in at <= 7 BB / > 40 BB | 19% / 17% | 10% / 18% | 42% / 28% |
| c-bet flop, bet size 0.4-0.7 pot | 74%, 48% | 61%, 62% | 68%, 66% |
| fold facing a bet / raise facing a bet | 55% / 6% | 46% / 11% | 57% / 17% |
| busts in level 1, bust hand median | 10%, 79 | 23%, 61 | 46%, 23 |
| expose the higher kept card | 28% | 20% | 0% |

Points come from surviving to the top 3; the winners avoid variance early (no limp-calls, no wars, fold to raises
without two pair+), c-bet relentlessly heads-up with half-pot bets, push/fold correctly when short, and call all-ins
far less often than we did.

## What the bot does

- **Preflop by equity percentile.** `data/preflop_classes.csv` (= `calc/results/b_preflop_classes.csv`) gives every
  3-card class its all-in equity vs 1/3/7; percentiles are weighted by how often the class is dealt. Open-raise
  2.5 BB (+1 BB per limper) with the top X% by position (X = 12% with 7 behind … 34% on the button; 8% wider
  3-handed or less). Never limp. 3-bet the top 3%; call opens with the top 15% if cheap (<= 10% of stack and
  <= 6 BB), top 7% up to 18% of stack. Facing a 3-bet: shove the top 1.2%, call the top 6% if <= 15% of stack, else fold.
  **<= 10 BB: push/fold** (shove the top 20–60% by position; wider at <= 5 BB). Call an all-in only if heads-up
  equity >= pot odds + ICM margin (0.10 deep, 0.06 at 15–30 BB, 0.03 short or when cheap).
- **Select:** keep rule v2 (03 S3.1 + S3.3); expose a card that does not pair the board (lower first), 20% deterministic mix.
- **Postflop by tier.** 4 = two pair with both hole cards or better: bet 65% pot, raise, call all-ins. 3 = top pair,
  overpair, weak two pair: bet 55% pot, call bets <= 65% pot heads-up (45% multiway, 50%/35% on the river), never
  call off more than 30% of the stack with one pair unless short; shove when short. 2 = weak pair or flush
  draw/open-ender: c-bet heads-up as the aggressor, call draws at price (40% pot flop, 28% turn), weak pairs only
  cheap. 1 = air: c-bet the flop heads-up as the aggressor if no opponent exposed a board-pairing card, otherwise
  check/fold. An opponent whose exposed card pairs the board above our pair demotes our one pair.
- Stateless, no memory; one CSV read at import; <= 3 `eval7.evaluate` calls per decision.

## Results (paired A/B, challenger replaces hero in the same seats; `strategy/08-experiments.md` 2026-11-06)

| hero | field | pairs | seed | fp-v1 − hero | 95% CI | p |
|---|---|---|---|---|---|---|
| bot (v0-nowar) | v0-baseline, check_or_fold, arch-folder, arch-shover, arch-station | 818 | fp1a | **+2.37** | ±1.49 | 0.002 |
| cap-floor-count-v6 (upload) | same archetype field | 824 | fp1b | **+2.20** | ±1.60 | 0.007 |
| cap-floor-count-v6 | min_raiser + check_or_fold (kit field) | 986 | fp1c | **+1.71** | ±0.96 | <0.001 |
| cap-floor-count-v6 | v0-nowar, cap-floor-count-v5, arch-folder copies (strong field) | 1000 | fp1d | **+4.13** | ±1.06 | <0.001 |

`arena check fp-v1 --tables 20`: 16,791 decisions, 0 failures, p50 0.019 ms, p99 0.109 ms, max 19 ms (GC tail;
fp-v2 adds `gc.freeze()` + a high threshold as cap-floor-count-v6 does). Memory 0 bytes.

**Promote if** it beats the current upload in >= 3 fields with CIs excluding zero (done). **Demote if** a later
version beats it by a CI excluding zero, or a strict-mode run shows timeouts.

## Family log (best first)

| version | directory | change | result | status |
|---|---|---|---|---|
| **v3** | `bots/fp-v3` | v2 + deep all-in calls need eq >= pot odds + 0.16 and top-8% class | +1.26 ±0.83 vs fp-v2; +2.54 ±0.91 vs cap-floor-count-v6 (kit field) | **current best — upload candidate** |
| v4, v4b | `bots/fp-v4`, `bots/fp-v4b` | HU/3-handed loosening (+ cap awareness in v4) | −1.56 / −1.83 vs fp-v3 | rejected |
| v2 | `bots/fp-v2` | v1 + gc.freeze/threshold (max latency 19 -> 4 ms) | identical play to v1 | superseded |
| v1 | `bots/fp-v1` | first-principles design | +1.7 to +4.1 vs cap-floor-count-v6 in 3 fields | superseded |

Ideas queued for v2+: GC tuning; opponent-count-aware c-bet; exposure-aware bluff-catching (cap/floor from
cap-floor-count); per-seat stats in memory (fold-to-cbet, shove frequency) for archetype exploits (05 S5.4).
