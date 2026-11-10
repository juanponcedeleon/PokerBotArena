# fp-v3

`bots/fp-v2` + ICM-tight deep all-in calls: at >= 25 BB, a call costing >= 45% of our stack needs eq_vs1 >= pot odds + 0.16 and a top-8% class. Motivation: in the logged league (`arena/results/*fp-v2-stats*`) 57 of fp-v2's 110 level-1/2 busts were calls of all-ins with median class percentile 0.90, 36 of them against the shover archetype. Everything else identical to fp-v2. Results in strategy/08-experiments.md.

## Results (2026-11-06)

| hero | field | pairs | seed | fp-v3 - hero | 95% CI | p |
|---|---|---|---|---|---|---|
| fp-v2 | v0-baseline, check_or_fold, arch-folder, arch-shover, arch-station, cap-floor-count-v6 | 740 | fp3a | **+1.26** | ±0.83 | 0.003 |
| cap-floor-count-v6 (upload) | min_raiser + check_or_fold | 989 | fp3b | **+2.54** | ±0.91 | <0.001 |

`arena check fp-v3`: 8,631 decisions, 0 failures. **Current best of the fp family; upload candidate.** Ship `agent.py` + `data/preflop_classes.csv`.
