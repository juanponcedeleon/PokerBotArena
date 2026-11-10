"""Co-evolution: tune every family in rounds, each against the latest champions of the others.

Round r, family F: hero = F's current champion (its parent in round 1, or the bot promoted in an
earlier round), field = the other families' champions + the base field (v0-baseline,
check_or_fold, min_raiser). A family whose run is promoted replaces its champion for every later
run, so later families tune against the stronger field, and the next round re-tunes everyone
against the new equilibrium. State is saved after every family so an interrupted session can be
resumed with `--resume <state.json>`.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from arena.bots import REPO

from evolve import ga
from evolve.genome import Template, save_json
from evolve.hoist import FAMILIES, TEMPLATES


def coevolve(
    families: list[str],
    *,
    rounds: int = 1,
    base_field: list[str] | None = None,
    state_file: Path | None = None,
    **ga_kwargs: Any,
) -> dict[str, Any]:
    base_field = base_field or list(ga.DEFAULT_FIELD)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    state_file = state_file or (ga.RUNS / f"coevolve-{stamp}.json")
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
    else:
        state = {
            "started": datetime.now().isoformat(timespec="seconds"), "families": families, "rounds": rounds, "base_field": base_field,
            "champions": {f: Template.load(TEMPLATES / f).parent for f in families}, "runs": [], "done": [],
        }
    for r in range(rounds):
        for family in families:
            key = f"{r + 1}:{family}"
            if key in state["done"]:
                continue
            hero = state["champions"][family]
            field = [state["champions"][f] for f in families if f != family] + base_field
            seed = f"{ga_kwargs.get('seed') or stamp}:r{r + 1}:{family}"
            kwargs = {k: v for k, v in ga_kwargs.items() if k != "seed"}
            t0 = time.time()
            try:
                report = ga.run_family(family, hero=hero, field=field, seed=seed, **kwargs)
            except SystemExit as error:  # a family's failure must not stop the others
                report = {"family": family, "hero": hero, "field": field, "seed": seed, "verdict": f"ABORTED: {error}"}
                print(f"  {family}: {report['verdict']}", file=sys.stderr, flush=True)
            report["round"] = r + 1
            report["elapsed_s"] = round(time.time() - t0)
            if report.get("promoted"):
                state["champions"][family] = report["promoted"]
            state["runs"].append(report)
            state["done"].append(key)
            save_json(state_file, state)
    state["finished"] = datetime.now().isoformat(timespec="seconds")
    save_json(state_file, state)
    print_summary(state)
    return state


def print_summary(state: dict[str, Any]) -> None:
    print("\n=== co-evolution summary ===", file=sys.stderr)
    print(f"{'round':>5} {'family':<22} {'hero':<28} {'validation':>11} {'held-out':>18} {'p':>6}  verdict", file=sys.stderr)
    for run in state["runs"]:
        ab = run.get("test") or {}
        val = run.get("validation_diff")
        held = f"{ab['mean_diff']:+.2f} ±{ab['ci95']:.2f}" if ab else "-"
        p = f"{ab['p_value']:.3f}" if ab else "-"
        print(f"{run.get('round', '-'):>5} {run['family']:<22} {str(run['hero']).split('/')[-1]:<28} {(f'{val:+.2f}' if isinstance(val, float) else '-'):>11} {held:>18} {p:>6}  {run.get('verdict')}", file=sys.stderr)
    print("champions: " + ", ".join(f"{f}={c}" for f, c in state["champions"].items()), file=sys.stderr)
    print(f"state: {Path(state.get('state_file', '')).as_posix() if state.get('state_file') else ''}", file=sys.stderr)
