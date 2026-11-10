# icm-pushfold (v1) — ICM push/fold with precomputed 3-card shove tables

**Status: superseded (lost).** Family: v1 → v2 → v3 → v4 → v5 → v6 → v7 (see each `bots/icm-pushfold-vN/BOT.md`).
Best version of the family: see `bots/icm-pushfold-v7/BOT.md` (the family's living summary is kept there).

## Hypothesis
Most points move in the push/fold phase (hand ~80 onwards, average stack ≤ 12 BB). Replacing v0's
class-threshold shove rule ("class ≥ 2 shoves at ≤ 12 BB") with Nash-derived 3-card shove/call tables and
ICM arithmetic on the live stacks should win points at the same postflop play.

## Strategy entries implemented
- `strategy/06-tournament-icm.md` S6.1 (phase by effective stack), S6.2 (push/fold tables), S6.3 (bubble)
- `strategy/02-preflop.md` S2.5 (hand-vs-range equity lookup) — tables from `calc/i_pushfold_tables.py`
- Base: `bot/agent.py` v0 as of 2026-11-06 19:00 (select + postflop untouched)

## Data
- `data/hand_vs_range.csv` — 1,755 classes × equity vs the top {2,5,8,12,16,20,25,30,40,50,65,80,100}% of
  dealt hands (3,000 runouts each, both sides oracle-keep) = `calc/results/i_hand_vs_range.csv`
- `data/pushfold_nash.csv` — chip-EV shove/call fixed point by (effective stack S, players behind N)

## Result (arena, fast mode)
`ab bot bots/icm-pushfold --tables 400 --seed icm1` (field min_raiser, check_or_fold):
**−2.39 ± 0.94 pts/table (p < 0.001), 29 better / 302 tied / 66 worse.** Demote.

## Why it lost (diagnosed from `--log`)
1. Bug: when calling a short all-in it re-shoved its whole stack to "isolate", then got called by a third
   player (`arena/results/20261106-191634-icm-diag-f630`, pair it0 t0 hand 6).
2. Players already committed to the pot were not counted as callers; multiway all-ins were valued heads-up.
3. Nash callers assumed; the field has a 100 % caller (min_raiser) and a 100 % folder (check_or_fold).
