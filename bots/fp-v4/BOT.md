# fp-v4

fp-v3 + heads-up/3-handed ranges (button opens top 70%, BB defends top 55%), bubble call margin +0.06, cap awareness from exposed cards (opponent whose exposed card cannot pair an unpaired board or make a flush/straight is capped at one pair: top pair bets/calls bigger, HU air stabs), HU position bug fixed. See agent.py docstring and strategy/08-experiments.md for results.

**REJECTED 2026-11-06:** −1.56 ±1.31 vs fp-v3 (p=0.019), archetype field + cfc-v6, ~740 pairs. The heads-up / 3-handed loosening loses against this field. Do not use; fp-v3 remains the best.
