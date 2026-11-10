# evolve — evolutionary tuning of the bot pool, scored in the arena

`evolve/` tunes the numeric constants of a strategy family (open sizes, call thresholds, equity gates,
draw weights, ICM margins...) with a genetic algorithm whose fitness is **paired arena points against
the other families**. It started from the user's `evol.py` (kept verbatim in `evolve/upstream/evol.py`,
written for one specific agent and the `poker-agent play` CLI) and was generalized to every bot in
`bots/` and to the arena's in-process runner. Nothing here is shipped with a bot.

```sh
PY=starter-kit/.venv/Scripts/python.exe          # from PokerBot/
$PY -m evolve families                           # the families and their parents in bots/
$PY -m evolve hoist                              # (re)build evolve/templates/<family>/ from the parents
$PY -m evolve verify cap-floor-count-v6          # template with defaults == parent? (must say IDENTICAL)
$PY -m evolve run cap-floor-count-v6             # tune one family (train -> validate -> held-out arena A/B -> promote)
$PY -m evolve coevolve --rounds 2                # every family, each against the others' latest champions
$PY -m evolve coevolve --resume evolve/runs/coevolve-<stamp>.json   # continue an interrupted session
```

## How it works

1. **Template** (`hoist.py`). A family head in `bots/` (e.g. `cap-floor-count-v6`) is copied to
   `evolve/templates/<family>/agent.py` with its strategy literals hoisted into a `TUNABLES` block of
   module-level constants; `evolve.json` lists each gene's default, bounds and int flag, plus ordering
   constraints (`RAISE_EQ >= VALUE_BET_EQ`). Hoisting is a list of exact text substitutions with expected
   counts, so a parent that changed fails loudly. Genes declared `None` take the parent's current literal.
   `verify` plays the template against its parent on shared tables and requires **every** paired
   difference to be exactly zero before anything is tuned.
2. **Fitness** (`fitness.py`). One generation is one *multi-arm paired run*: a league plan with the parent
   (hero) in the field, plus a copy of every table per candidate in which the candidate sits in the hero's
   seats. Same seed, same cards, same button; fitness = mean (candidate − parent) points per table. The
   decision clock is recorded but not enforced during training (the machine is shared); any error or
   illegal action rejects a candidate.
3. **GA** (`genome.py`, `ga.py`). Population 8, two elites, uniform crossover, per-gene Gaussian mutation
   (rate 0.35, step 16 % → 5 % of the gene's range over the generations), repair into bounds. Each generation
   uses a fresh seed. Each generation's winner and the starting genome are **validated** on an unseen seed
   with more tables; the best is **tested** in a real `arena ab` run (clock enforced, logged to
   `strategy/08-experiments.md`, visible on the dashboard) on another unseen seed. Selection never sees the
   test number.
4. **Promotion.** Held-out difference > 0 with p < 0.05 and no failure regression → the genome is written to
   `bots/<head>-evoN/` (agent.py with only the literals changed, `parameters.json`, `BOT.md` with the gene
   table and every number). Otherwise the candidate stays under `evolve/runs/<stamp>-<family>/best/` and the
   report says why.
5. **Co-evolution** (`coevolve.py`). Rounds over the families; family F is tuned against the other families'
   current champions + the base field (`v0-baseline`, `check_or_fold`, `min_raiser`). A promoted bot becomes
   its family's champion for every later run. State after each family in `evolve/runs/coevolve-<stamp>.json`.

## Families

| family | parent | genes | what the genes cover |
|---|---|---|---|
| `v0-nowar` | `bots/v0-nowar` | 20 | preflop sizes/thresholds (capped war), v0 postflop sizes/thresholds, exposure probability |
| `nowar-keep-v2` | `bots/nowar-keep-v2` | 35 | the above + 15 keep-rule draw weights (3 opponent buckets × 5 features) |
| `cap-floor-count-v6` | `bots/cap-floor-count-v6` | 29 | preflop (no limp) + every cap/floor/count tunable (equity gates, call margin, aggression weights, bet sizes, one-pair gate) |
| `icm-pushfold-v7` | `bots/icm-pushfold-v7` | 29 | push/reshove stacks, margins, survival premium, Nash prior weight, deep preflop, v0 postflop |

Every template also gets `EXPOSE_LOW_PROB` (strategy/03 S3.2): 1.0 = always expose the weaker kept card
(the v0 rule); lower values expose the stronger card with a per-hand deterministic roll (crc32 of our
cards + flop), so the bot stays stateless and tables replay identically.

## Reading a run

`evolve/runs/<stamp>-<family>/` holds `experiment.json` (hero/field fingerprints, seeds, gene bounds),
`identity.json`, `generation_N.json` (every candidate: genome, paired diff ± CI, errors, latency),
`validation.json`, `report.json` (selected genome, held-out A/B block, verdict) and `candidates/<id>/`
(complete bot directories). The held-out A/B is also an ordinary arena run under `arena/results/`.

Rules of thumb: a ±95 % of about 2.5 pts at 200 paired tables means training ranks are noisy; that is why
selection happens on validation seeds and the claim on a separate test. An "improved" verdict is one field
and one seed; promote on the scoreboard only after a second field agrees and a strict-mode run shows no
timeouts (arena/README.md).
