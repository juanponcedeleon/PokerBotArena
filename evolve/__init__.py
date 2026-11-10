"""PokerBot evolve: evolutionary parameter tuning of the bots in `bots/`, scored in the arena.

Nothing here is shipped with a bot. The idea comes from the user's `evol.py` (kept verbatim in
`evolve/upstream/evol.py`); this package generalizes it to every strategy family in the pool:

* `hoist`    turns a bot into a *template*: its strategy constants become module-level
             tunables with byte-identical defaults, listed with bounds in `evolve.json`.
* `genome`   genomes (one value per tunable), mutation, crossover, repair, rendering a
             candidate `agent.py` by rewriting only the tunables' literals (comments survive).
* `fitness`  in-process arena evaluation on paired tables: every candidate of a generation
             takes the parent's seats in the same dealt tables, so a generation is one
             multi-arm A/B, not a pile of independent noisy leagues.
* `ga`       the loop: train -> validate on fresh seeds -> held-out paired A/B vs the parent
             (recorded by the arena and appended to strategy/08-experiments.md) -> promote
             to `bots/<parent>-evoN` when the held-out difference is positive.
* `coevolve` rounds over all families; each family is tuned against the latest champions of
             the others, so the field it optimizes against is the one it will meet.

See evolve/README.md.
"""

__all__ = ["hoist", "genome", "fitness", "ga", "coevolve"]
