"""`python -m evolve <command>` — see evolve/README.md.

  hoist [FAMILY...]        (re)build evolve/templates/<family> from the family heads in bots/
  verify FAMILY            prove the template with its defaults plays identically to its parent
  run FAMILY               evolve one family: train, validate, held-out arena A/B, promote
  coevolve                 all families in rounds, each against the others' latest champions
  families                 list the families and their parents
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from evolve import ga
from evolve.hoist import CURRENT, FAMILIES, TEMPLATES, build_all


def add_ga_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--population", type=int, default=8, help="genomes per generation incl. 2 elites (default 8)")
    parser.add_argument("--generations", type=int, default=6)
    parser.add_argument("--tables", type=int, default=200, help="paired tables per candidate per generation (default 200)")
    parser.add_argument("--validation-tables", type=int, default=500)
    parser.add_argument("--test-tables", type=int, default=1000, help="pairs in the held-out arena A/B (default 1000)")
    parser.add_argument("--seed", default=None)
    parser.add_argument("--mutation-rate", type=float, default=0.35, help="probability each gene mutates in a child (default 0.35)")
    parser.add_argument("--workers", type=int, default=None, help="fast-runner worker processes (default cores-1)")
    parser.add_argument("--agent", default="Claude (evolve)", help="who ran it, for strategy/08-experiments.md")
    parser.add_argument("--promote-p", type=float, default=0.05, help="held-out p-value needed to write bots/<head>-evoN (default 0.05)")
    parser.add_argument("--no-promote", action="store_true", help="never write to bots/")


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(prog="python -m evolve", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    hoist = commands.add_parser("hoist", help="Build templates from the family heads.")
    hoist.add_argument("families", nargs="*")

    verify = commands.add_parser("verify", help="Template defaults == parent on shared tables?")
    verify.add_argument("family")
    verify.add_argument("--hero", default=None)
    verify.add_argument("--tables", type=int, default=40)
    verify.add_argument("--workers", type=int, default=None)

    run = commands.add_parser("run", help="Evolve one family.")
    run.add_argument("family")
    run.add_argument("--hero", default=None, help="starting bot (default: the family's parent; an evolved bot continues from its genome)")
    run.add_argument("--field", nargs="*", default=None, help="opponents (default: v0-baseline check_or_fold min_raiser)")
    add_ga_arguments(run)

    co = commands.add_parser("coevolve", help="All families, in rounds.")
    co.add_argument("--families", nargs="*", default=list(CURRENT))
    co.add_argument("--rounds", type=int, default=1)
    co.add_argument("--base-field", nargs="*", default=None, help="always-present opponents (default: v0-baseline check_or_fold min_raiser)")
    co.add_argument("--resume", type=Path, default=None, help="state.json of an interrupted co-evolution")
    add_ga_arguments(co)

    commands.add_parser("families", help="List families.")

    args = parser.parse_args()
    if args.command == "families":
        for name, fam in FAMILIES.items():
            built = (TEMPLATES / name / "evolve.json").is_file()
            print(f"{name:<22} parent bots/{fam.parent:<22} {len(fam.genes):>3} genes  {'template built' if built else 'not built'}  {fam.strategy}")
        return
    if args.command == "hoist":
        for path in build_all(args.families or None):
            print(f"built {path.relative_to(path.parents[2]).as_posix()}")
        return
    if args.command == "verify":
        ok = ga.verify(args.family, hero=args.hero, tables=args.tables, workers=args.workers)
        sys.exit(0 if ok else 1)
    ga_kwargs = dict(
        population=args.population, generations=args.generations, tables=args.tables, validation_tables=args.validation_tables,
        test_tables=args.test_tables, seed=args.seed, mutation_rate=args.mutation_rate, workers=args.workers, agent=args.agent,
        promote_p=args.promote_p, promote=not args.no_promote,
    )
    if args.command == "run":
        report = ga.run_family(args.family, hero=args.hero, field=args.field, **ga_kwargs)
        print(f"{args.family}: {report.get('verdict')}; promoted: {report.get('promoted')}; report: {report['work']}/report.json")
        return
    if args.command == "coevolve":
        from evolve.coevolve import coevolve

        coevolve(args.families, rounds=args.rounds, base_field=args.base_field, state_file=args.resume, **ga_kwargs)


if __name__ == "__main__":
    main()
