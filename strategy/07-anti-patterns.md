# 07 — Anti-patterns: what loses, with evidence

Owner: Claude (main); A20–A23 Claude (headmaster)   Last updated: 2026-11-06
Rejected or demoted strategies land here with the number that killed them. Never delete entries.

| # | anti-pattern | why it loses | evidence |
|---|---|---|---|
| A1 | Letting selection time out / using the fallback keep | Keeps a random pair: 18.3% pot share vs 26.1% for the cheap rule, 4-way | `calc/c_selection_policies.py` |
| A2 | Keeping the two highest cards | 21.6% vs 26.1% | same |
| A3 | Any deterministic exposure rule against a reading opponent | "show blank" + pairing exposure = two pair+ 100%; "show high" + exposing a 2 on Q72 = trips 100% | `calc/h_policy_inversion.py` |
| A4 | Treating pocket trips as a monster | AAA is top 31% (one ace left; 6.4% to flop a set vs 12% for AA); 888 is bottom 1% 8-way | `calc/b_preflop_classes.py`, `calc/a_flop_hits.py` |
| A5 | Valuing three suited cards for the flush | 9.5% flush draws vs 10.9% for two suited; three suited ≈ two suited in equity | `calc/a_flop_hits.py`, `calc/b_preflop_classes.py` |
| A6 | Playing a high card with two danglers (A72r, K72r) | top 94–99% percentile; junk flops a pair as often as AKQ, the pair is just worse | `calc/b_preflop_classes.py`, `calc/a_flop_hits.py` |
| A7 | Calling down with one pair | Wins 22% of heads-up all-see-river showdowns, 7% four-way (hold'em: 43% / 25%) | `calc/f_showdown_value.py` |
| A8 | Over-respecting a board-pairing exposure | 40 of 48 hidden cards are a bare pair (83%) under a uniform prior | `calc/d_reveal_tables.py` |
| A9 | Paying off a floor (board pairs their exposed card) | Their minimum hand is trips; our maximum may be two pair | `calc/d_reveal_tables.py` |
| A10 | Bluffing an opponent whose exposure already beats our possible hands | Their floor > our cap; a reading bot never folds | logic |
| A11 | Taking 50/50 flips for stacks early | ICM break-even is 55.6% on hand 1, 65% on the bubble, 77% three-handed | `calc/e_tournament.py` |
| A12 | Playing deep-stack poker at 10 BB | By hand 100 the average stack is 8 BB; the game is push/fold | `calc/e_tournament.py` |
| A13 | Hardcoding 50/30/20 payouts | A round may give each table a random split; read `state.config.payouts` | README.md |
| A14 | Monte Carlo inside `act` | 45 hidden × 100 runouts ≈ 7 ms; the budget is 1 ms | `calc/g_timing.py` |
| A15 | JSON blobs of several KB in memory | 2.4 KB JSON round trip ≈ 70 µs, 7% of the budget; use `struct` | `calc/g_timing.py` |
| A16 | Counting outs from 47 unseen cards | Every exposed card (including folded players') is dead; use the true unseen set | RULES.md |
| A17 | Omaha-style thinking ("must use both") | Rules are hold'em style: 0, 1 or 2 hole cards | RULES.md |
| A18 | Chasing the Empty Bluffer prize with a worse keep | Side prize only; selection equity is worth far more | logic |
| A19 | Treating the agent-output's exposure heuristics as proven | They are plausible against readers and near-irrelevant against non-readers; untested either way | [[03-selection]] S3.2 |
| A20 | Unlimited preflop re-raising with "premium" 3-card classes (v0's 3× re-raise loop) | Two copies escalate to all-in at 100 BB on hand 1; 59% of pool seats bust in blind level 1; real practice round: 40% of our busts in level 1, 4.9% on hand 1, rank 99/123. Capping it: +5.33 ±2.02 pts/table (p<0.001, 400 pairs) | `strategy/08-experiments.md` 2026-11-06 cfc-v1-ab-pool, nowar-ab-pool, practice round |
| A21 | Uniform prior over the opponent's hidden card when they *bet* (cap-floor-count v1) | Pays off value bets: folds postflop 10% vs 21%, W$SD 41% vs 48%; −1.71 ±1.21 pts/table vs v0 (p=0.006, 400 pairs). Condition the count on the bettor's action | `strategy/08-experiments.md` 2026-11-06 cfc-v1-ab-pool |
| A22 | 66% VPIP in an 8-max field | Real field: points correlate −0.37 with VPIP and −0.47 with flops seen per hand; v0 (VPIP 66%, saw flop 35%) scored 8.67 vs field mean 13.0; top-10 median VPIP 34%, saw flop 18% | `calc/results/practice-20261107-population.md` |
| A23 | Exposing the card that paired the flop (v0 show-low does it 58% of the time) | Real field: top-10 teams expose the pairing card 0.5% of the time, bottom-30 teams 50%; correlation with points −0.45 for exposing 2–5. Correlation, not yet causation: run the A/B (03 S3.2) | `calc/results/practice-20261107-population.md` |
| A24 | Replacing v0's preflop with ICM push/fold tables at every stack depth (`bots/icm-pushfold` v1/v2) | v1 −2.39 ±0.94 (p<0.001), v2 −4.99 ±1.49 with 76 failed decisions, vs v0 in the kit field; real round: median bust hand 24, 1 table in 10,000 reached the cap — the push/fold phase is rarely reached. Tables stay valid (06 S6.2, MATH); the bots lost | `strategy/08-experiments.md` 2026-11-06 icm-pushfold-v1, icm-pushfold-v2 |
| A25 | Loosening ranges short-handed (HU / 3-handed opens) on top of fp-v3 | fp-v4 −1.56 ±1.31 (p=0.019) and fp-v4b −1.83 ±1.30 (p=0.006) vs fp-v3 in the archetype field; the short-handed loosening is what loses, cap awareness changed nothing | `strategy/08-experiments.md` 2026-11-07 fp-v4, fp-v4b |
