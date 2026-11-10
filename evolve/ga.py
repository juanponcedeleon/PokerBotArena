"""The evolutionary loop for one family: train, validate, test held-out, promote.

Protocol (adapted from the user's evol.py, re-based on the arena):

1. identity   The template with the starting genome must play *identically* to the starting bot on
              shared tables (every paired difference exactly 0) or the run aborts: a hoisting bug
              would otherwise be "tuned".
2. train      G generations. Each generation plays one multi-arm paired run on a fresh seed:
              the parent (hero) and every candidate sit in the same seats of the same tables.
              Fitness = mean paired difference vs the parent. Any error/illegal action rejects a
              candidate. The two best survive as elites; children are crossover + mutation.
3. validate   Each generation's winner plus the starting genome replay on an unseen seed with more
              tables; the best becomes the selected candidate (never chosen on training seeds).
4. test       The selected candidate meets the parent in a real arena A/B (`arena ab` machinery,
              decision clock enforced, logged to strategy/08-experiments.md) on another unseen
              seed. Selection never looks at this number.
5. promote    If the held-out difference is positive and p is below the threshold, the candidate
              becomes `bots/<family-head>-evoN` with a BOT.md that states the genes, the field,
              and every number above. Otherwise the run stays under evolve/runs/ and says so.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from arena import bots as botlib
from arena.bots import REPO, BotRef
from arena.plan import ab_plan

from evolve.fitness import PairedResult, evaluate_arms, identical
from evolve.genome import Genome, Template, genome_id, make_population, save_json
from evolve.hoist import TEMPLATES

RUNS = REPO / "evolve" / "runs"
BAD = -1_000_000.0
DEFAULT_FIELD = ["v0-baseline", "check_or_fold", "min_raiser"]


def log(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def fmt(x: float | None, d: int = 2, sign: bool = True) -> str:
    if x is None or x != x:
        return "-"
    return f"{x:+.{d}f}" if sign else f"{x:.{d}f}"


def load_start(template: Template, hero: BotRef) -> Genome:
    """The genome the hero plays: its parameters.json when it is an evolved bot, else defaults."""
    params = hero.path / "parameters.json"
    if params.is_file():
        data = json.loads(params.read_text(encoding="utf-8"))
        if data.get("family") != template.family:
            raise SystemExit(f"{hero.path} was evolved from family {data.get('family')!r}, not {template.family!r}.")
        return template.repair({k: float(v) for k, v in data["parameters"].items()})
    return template.defaults()


def next_evo_name(head: str) -> str:
    taken = {p.name for p in botlib.POOL_DIR.iterdir()} if botlib.POOL_DIR.is_dir() else set()
    n = 1
    while f"{head}-evo{n}" in taken:
        n += 1
    return f"{head}-evo{n}"


def recorded_ab(hero: BotRef, challenger: BotRef, field: list[BotRef], *, seed: str, tables: int, name: str, agent: str, question: str, workers: int | None, record: bool = True) -> dict[str, Any]:
    """A real `arena ab` run (results dir, experiment-log entry, dashboard), returning its A/B block."""
    from arena.__main__ import run_plan

    args = argparse.Namespace(
        players=8, decision_ms=1, hand_cap=250, random_payouts=False, mode="fast", log=False, history=None,
        quiet=True, workers=workers, no_experiment_log=not record, agent=agent, question=question,
    )
    refs = botlib.unique_labels([hero, challenger] + field)
    hero, challenger, field = refs[0], refs[1], refs[2:]
    plan = ab_plan(hero.label, challenger.label, [f.label for f in field], seed=seed, tables=tables)
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        run_dir = run_plan(args, refs, plan, name)
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    ab = dict(summary.get("ab") or {})
    ab["run_dir"] = run_dir.relative_to(REPO).as_posix()
    ab["ranking"] = [{"label": r["label"], "avg_points": r["avg_points"], "ci95": r["ci95"], "failures": r["failures"]} for r in summary["ranking"]]
    return ab


def print_generation(result: PairedResult, ranked: list[dict[str, Any]], template: Template) -> None:
    log(f"    {'#':>2} {'genome':<12} {'diff':>7} {'±95%':>6} {'pts':>6} {'err':>4} {'p99ms':>6}  changed genes")
    for i, row in enumerate(ranked, 1):
        arm = result.arms.get(row["label"])
        changes = template.changed_genes(row["genome"])
        text = ", ".join(f"{k}={v[1]:g}" for k, v in list(changes.items())[:6])
        if len(changes) > 6:
            text += f" (+{len(changes) - 6})"
        status = fmt(row["fitness"]) if row["healthy"] else "REJECT"
        p99 = arm.to_dict()["lat_p99_ms"] if arm else None
        log(f"    {i:>2} {row['id']:<12} {status:>7} {fmt(row['ci95'], 2, sign=False):>6} {fmt(row['points'], 2, sign=False):>6} "
            f"{(arm.errors + arm.illegal) if arm else 0:>4} {('%.2f' % p99) if p99 is not None else '-':>6}  {text}")


def run_family(
    family: str,
    *,
    hero: str | None = None,
    field: list[str] | None = None,
    population: int = 8,
    generations: int = 6,
    tables: int = 200,
    validation_tables: int = 500,
    test_tables: int = 1000,
    seed: str | None = None,
    mutation_rate: float = 0.35,
    workers: int | None = None,
    agent: str = "Claude (evolve)",
    promote_p: float = 0.05,
    promote: bool = True,
    work: Path | None = None,
) -> dict[str, Any]:
    template = Template.load(TEMPLATES / family)
    hero_ref = botlib.resolve(hero or template.parent)
    field_refs = [r for r in botlib.resolve_many(field or DEFAULT_FIELD) if r.path != hero_ref.path]
    seed = seed or datetime.now().strftime("evo%m%d%H%M%S")
    rng = random.Random(seed)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    work = work or (RUNS / f"{stamp}-{family}")
    work.mkdir(parents=True, exist_ok=False)
    candidates_dir = work / "candidates"
    start = load_start(template, hero_ref)
    start_id = genome_id(start)

    def folder(genome: Genome) -> Path:
        return template.materialize(genome, candidates_dir / genome_id(genome))

    def label(genome: Genome) -> str:
        return f"evo-{genome_id(genome)}"

    save_json(work / "experiment.json", {
        "family": family, "template": template.dir.relative_to(REPO).as_posix(), "hero": {"label": hero_ref.label, "path": str(hero_ref.path), "fingerprint": hero_ref.fingerprint()},
        "field": [{"label": f.label, "path": str(f.path), "fingerprint": f.fingerprint()} for f in field_refs],
        "seed": seed, "population": population, "generations": generations, "tables_per_generation": tables,
        "validation_tables": validation_tables, "test_tables": test_tables, "mutation_rate": mutation_rate,
        "start_genome": start, "genes": {n: {"default": g.default, "min": g.low, "max": g.high, "int": g.int_valued} for n, g in template.genes.items()},
        "constraints": template.constraints, "started": datetime.now().isoformat(timespec="seconds"),
    })
    log(f"\n=== evolve {family}: hero {hero_ref.label}, field {', '.join(f.label for f in field_refs)}, seed {seed} -> {work.relative_to(REPO).as_posix()}")

    # 1. identity ------------------------------------------------------------------------------
    t0 = time.time()
    check = evaluate_arms(hero_ref, field_refs, {label(start): folder(start)}, seed=f"{seed}:verify", tables=40, workers=workers)
    arm = check.arms[label(start)]
    save_json(work / "identity.json", check.to_dict())
    if not arm.healthy or not identical(check, label(start)):
        raise SystemExit(
            f"Template {family} with the starting genome does not reproduce {hero_ref.label}: "
            f"{sum(1 for d in check.diffs[label(start)] if d != 0)} of {len(check.diffs[label(start)])} tables differ, "
            f"errors {arm.errors}, illegal {arm.illegal}. Fix evolve/hoist.py before tuning. Details: {work / 'identity.json'}"
        )
    log(f"  identity: template == {hero_ref.label} on {arm.tables} tables ({time.time() - t0:.0f} s)")

    # 2. train ----------------------------------------------------------------------------------
    pop = make_population(template, [start], population, rng, 0, rate=mutation_rate)
    finalists: dict[str, Genome] = {start_id: start}
    history = []
    for gen in range(generations):
        gen_seed = f"{seed}:train:{gen}"
        arms = {label(g): folder(g) for g in pop if genome_id(g) != start_id}
        t0 = time.time()
        result = evaluate_arms(hero_ref, field_refs, arms, seed=gen_seed, tables=tables, workers=workers)
        ranked = []
        for g in pop:
            gid = genome_id(g)
            if gid == start_id:
                ranked.append({"id": gid, "label": hero_ref.label, "genome": g, "healthy": True, "fitness": 0.0, "ci95": 0.0, "points": result.arms[hero_ref.label].mean})
                continue
            a = result.arms[label(g)]
            ranked.append({
                "id": gid, "label": label(g), "genome": g, "healthy": a.healthy,
                "fitness": result.diff_mean(label(g)) if a.healthy else BAD,
                "ci95": result.diff_ci95(label(g)), "points": a.mean,
            })
        ranked.sort(key=lambda r: r["fitness"], reverse=True)
        log(f"  generation {gen + 1}/{generations}: seed {gen_seed}, {tables} tables x {len(arms) + 1} arms, parent {result.arms[hero_ref.label].mean:.2f} pts ({time.time() - t0:.0f} s)")
        print_generation(result, ranked, template)
        healthy = [r for r in ranked if r["healthy"]]
        if not healthy:
            raise SystemExit("Every candidate failed; see the candidates' tracebacks in the generation file.")
        winner = healthy[0]
        finalists[winner["id"]] = winner["genome"]
        history.append({"generation": gen + 1, "seed": gen_seed, "ranked": [{k: v for k, v in r.items()} for r in ranked], "arms": result.to_dict()})
        save_json(work / f"generation_{gen + 1}.json", history[-1])
        elites = [r["genome"] for r in healthy[:2]]
        pop = make_population(template, elites, population, rng, gen + 1, rate=mutation_rate)

    # 3. validate -------------------------------------------------------------------------------
    val_seed = f"{seed}:validation"
    arms = {label(g): folder(g) for gid, g in finalists.items() if gid != start_id}
    log(f"  validation: {len(arms)} finalists vs {hero_ref.label}, seed {val_seed}, {validation_tables} tables")
    t0 = time.time()
    validation = evaluate_arms(hero_ref, field_refs, arms, seed=val_seed, tables=validation_tables, workers=workers) if arms else None
    rows = [{"id": start_id, "label": hero_ref.label, "genome": start, "healthy": True, "fitness": 0.0, "ci95": 0.0, "points": validation.arms[hero_ref.label].mean if validation else float("nan")}]
    if validation:
        for gid, g in finalists.items():
            if gid == start_id:
                continue
            a = validation.arms[label(g)]
            rows.append({"id": gid, "label": label(g), "genome": g, "healthy": a.healthy, "fitness": validation.diff_mean(label(g)) if a.healthy else BAD, "ci95": validation.diff_ci95(label(g)), "points": a.mean})
        rows.sort(key=lambda r: r["fitness"], reverse=True)
        print_generation(validation, rows, template)
        log(f"  ({time.time() - t0:.0f} s)")
    save_json(work / "validation.json", {"seed": val_seed, "ranked": rows, "arms": validation.to_dict() if validation else None})
    selected = rows[0]
    report: dict[str, Any] = {
        "family": family, "hero": hero_ref.label, "field": [f.label for f in field_refs], "seed": seed,
        "work": work.relative_to(REPO).as_posix(), "selected": selected["id"], "selected_genome": selected["genome"],
        "changed_genes": template.changed_genes(selected["genome"]), "validation_diff": selected["fitness"], "validation_ci95": selected["ci95"],
        "test": None, "promoted": None, "generations": len(history),
    }

    # 4. held-out test --------------------------------------------------------------------------
    if selected["id"] == start_id:
        log("  validation picked the starting genome: no candidate beat the parent on unseen tables. Nothing to test or promote.")
        report["verdict"] = "no improvement"
        save_json(work / "report.json", report)
        return report

    best_dir = template.materialize(selected["genome"], work / "best", note=f"Evolved by evolve/ga.py from {hero_ref.label} (genome {selected['id']}); see parameters.json and BOT.md.")
    challenger = BotRef(f"{hero_ref.label}-evo-{selected['id'][:6]}", best_dir)
    test_seed = f"{seed}:test"
    log(f"  held-out test: arena ab {hero_ref.label} vs {challenger.label}, seed {test_seed}, {test_tables} pairs, clock enforced")
    t0 = time.time()
    question = f"evolve {family}: genome {selected['id']} ({len(report['changed_genes'])} genes changed) vs {hero_ref.label}, held-out seed"
    ab = recorded_ab(hero_ref, challenger, field_refs, seed=test_seed, tables=test_tables, name=f"evolve-{family}", agent=agent, question=question, workers=workers)
    report["test"] = ab
    log(f"  result: {challenger.label} - {hero_ref.label} = {fmt(ab.get('mean_diff'))} ±{ab.get('ci95', float('nan')):.2f} pts/table over {ab.get('n')} pairs, p={ab.get('p_value', float('nan')):.3f} ({time.time() - t0:.0f} s) -> {ab['run_dir']}")
    fails = {r["label"]: r["failures"] for r in ab["ranking"]}
    challenger_fails = fails.get(challenger.label, 0)

    # 5. promote --------------------------------------------------------------------------------
    diff, p = ab.get("mean_diff", 0.0), ab.get("p_value", 1.0)
    if diff > 0 and p < promote_p and challenger_fails <= max(2, fails.get(hero_ref.label, 0) + 2):
        report["verdict"] = "improved"
        if promote:
            name = next_evo_name(template.parent.split("/")[-1])
            dest = botlib.POOL_DIR / name
            template.materialize(selected["genome"], dest, note=f"{name} - evolved from {hero_ref.label} by evolve/ga.py (genome {selected['id']}); genes and evidence in BOT.md.")
            (dest / "BOT.md").write_text(bot_md(name, template, hero_ref, field_refs, selected, report, history), encoding="utf-8")
            report["promoted"] = f"bots/{name}"
            log(f"  PROMOTED -> bots/{name}")
    else:
        why = "negative" if diff <= 0 else f"p={p:.3f} >= {promote_p}" if p >= promote_p else f"{challenger_fails} failed decisions"
        report["verdict"] = f"not promoted ({why})"
        log(f"  not promoted: held-out difference {fmt(diff)} ({why}). Candidate kept at {best_dir.relative_to(REPO).as_posix()}")
    save_json(work / "report.json", report)
    return report


def bot_md(name: str, template: Template, hero: BotRef, field: list[BotRef], selected: dict[str, Any], report: dict[str, Any], history: list[dict[str, Any]]) -> str:
    ab = report["test"] or {}
    lines = [
        f"# {name} - evolved parameters of `{hero.label}`",
        "",
        f"**Strategy implemented:** {template.strategy}. Same code as `{template.parent}`; only the constants in the",
        "TUNABLES block differ. Produced by `python -m evolve run " + template.family + "` (evolve/README.md).",
        "",
        f"**Parent:** `{hero.path.relative_to(REPO).as_posix()}` (fingerprint `{hero.fingerprint()}`).",
        f"**Training field:** {', '.join(f.label for f in field)} (every candidate took the parent's seats in the same dealt tables).",
        "",
        "## Genes changed",
        "",
        "| gene | parent | evolved |",
        "|---|---|---|",
    ]
    for gene, (old, new) in sorted(report["changed_genes"].items()):
        lines.append(f"| `{gene}` | {old:g} | **{new:g}** |")
    unchanged = len(template.genes) - len(report["changed_genes"])
    lines += [
        "", f"{unchanged} of {len(template.genes)} genes unchanged. Full genome: `parameters.json`.", "",
        "## Evidence (all paired vs the parent; details in `" + report["work"] + "/`)", "",
        "| stage | seed | tables | diff (pts/table) | 95% CI | p |", "|---|---|---|---|---|---|",
    ]
    for h in history:
        top = h["ranked"][0]
        lines.append(f"| train gen {h['generation']} winner | `{h['seed']}` | {h['arms']['arms'][hero.label]['tables']} | {top['fitness']:+.2f} | ±{top['ci95']:.2f} | |")
    lines.append(f"| validation (selected) | `{report['seed']}:validation` | {ab.get('n', '-') if False else ''} | {report['validation_diff']:+.2f} | ±{report['validation_ci95']:.2f} | |")
    lines.append(f"| **held-out test (arena ab, clock on)** | `{report['seed']}:test` | {ab.get('n')} pairs | **{ab.get('mean_diff', 0):+.2f}** | ±{ab.get('ci95', 0):.2f} | {ab.get('p_value', 1):.3f} |")
    lines += [
        "", f"Held-out run: `{ab.get('run_dir')}/leaderboard.md` (also logged in strategy/08-experiments.md).", "",
        "**Status:** PROMISING (arena paired A/B, one field). **Promote** to the scoreboard after it also beats the parent in a",
        "field it was not trained against and a strict-mode run shows no timeouts. **Demote** if a second field reverses the sign.",
        "", "Never edit this bot; evolve again from it (`python -m evolve run " + template.family + " --hero bots/" + name + "`).", "",
    ]
    return "\n".join(lines)


def verify(family: str, *, hero: str | None = None, field: list[str] | None = None, tables: int = 40, workers: int | None = None) -> bool:
    template = Template.load(TEMPLATES / family)
    hero_ref = botlib.resolve(hero or template.parent)
    field_refs = [r for r in botlib.resolve_many(field or DEFAULT_FIELD) if r.path != hero_ref.path]
    start = load_start(template, hero_ref)
    scratch = RUNS / "_verify" / family / genome_id(start)
    if scratch.exists():
        import shutil
        shutil.rmtree(scratch)
    template.materialize(start, scratch)
    lbl = f"evo-{genome_id(start)}"
    result = evaluate_arms(hero_ref, field_refs, {lbl: scratch}, seed=f"verify:{family}", tables=tables, workers=workers)
    arm = result.arms[lbl]
    same = identical(result, lbl) and arm.healthy
    differing = sum(1 for d in result.diffs[lbl] if d != 0)
    log(f"{family}: template vs {hero_ref.label} on {arm.tables} tables: {'IDENTICAL' if same else 'DIFFERENT'} "
        f"({differing} tables differ, errors {arm.errors}, illegal {arm.illegal}, p99 {arm.to_dict()['lat_p99_ms']} ms, {len(template.genes)} genes)")
    return same


_name_re = re.compile(r"[^a-z0-9-]+")
