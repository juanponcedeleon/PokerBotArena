"""`python -m arena <command>` — see arena/README.md.

  list                       bots the arena can find
  ladder                     whole pool (bots/ + examples) in a league; publishes results/LEADERBOARD.md
  league BOT [BOT...]        league between named bots (--all adds the pool, --examples the sparring bots)
  ab HERO CHALLENGER         paired A/B: challenger takes the hero's seats in the same tables
  check BOT                  submission check + latency/memory probe
  stats FILE                 behavioural statistics from a log.jsonl.gz or a tournament download
  report RUN_DIR             re-render a run's leaderboard from tables.jsonl
  watch                      re-run the ladder whenever a bot in bots/ changes
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path

from arena import bots as botlib
from arena import plan as planlib
from arena import report
from arena.bots import REPO, BotRef
from arena.outcome import TableOutcome, make_rules


def add_run_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tables", type=int, default=200, help="Tables to play (pairs for ab). Default 200.")
    parser.add_argument("--seed", default=None, help="Same seed + same bots = same cards.")
    parser.add_argument("--mode", choices=["fast", "strict"], default="fast")
    parser.add_argument("--workers", type=int, default=None, help="fast: worker processes (default cores-1). strict: shard processes (default cores/4, max 4).")
    parser.add_argument("--concurrency", type=int, default=1, help="strict: tables sharing one event loop (default 1 = clean timing; poker-agent play uses 8).")
    parser.add_argument("--decision-ms", type=int, default=1, help="Decision limit. fast mode: 0 records latency without enforcing it.")
    parser.add_argument("--hand-cap", type=int, default=250)
    parser.add_argument("--players", type=int, default=8)
    parser.add_argument("--random-payouts", action="store_true", help="Each table draws its own split of 100 points.")
    parser.add_argument("--log", action="store_true", help="Keep every hand (all cards) in log.jsonl.gz for `arena stats`.")
    parser.add_argument("--history", metavar="HERO", help="Also write a participant-format replay file from HERO's seat.")
    parser.add_argument("--name", default=None, help="Run name (results directory).")
    parser.add_argument("--agent", default=os.environ.get("ARENA_AGENT", "arena"), help="Who ran it, for the experiment log.")
    parser.add_argument("--question", default=None, help="One line for the experiment log.")
    parser.add_argument("--no-experiment-log", action="store_true")
    parser.add_argument("--quiet", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m arena", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="Bots the arena can find.")

    ladder = commands.add_parser("ladder", help="Whole pool league; publishes results/LEADERBOARD.md.")
    ladder.add_argument("--no-examples", action="store_true", help="Leave out check_or_fold / min_raiser.")
    add_run_arguments(ladder)

    league = commands.add_parser("league", help="League between named bots.")
    league.add_argument("bots", nargs="*", help="Bot names or directories (label=path allowed).")
    league.add_argument("--all", action="store_true", help="Add every bot in bots/.")
    league.add_argument("--examples", action="store_true", help="Add the starter kit's example bots.")
    league.add_argument("--publish", action="store_true", help="Also overwrite results/LEADERBOARD.md.")
    add_run_arguments(league)

    ab = commands.add_parser("ab", help="Paired A/B test.")
    ab.add_argument("hero")
    ab.add_argument("challenger")
    ab.add_argument("--field", nargs="*", default=[], help="Opponents (default: min_raiser check_or_fold + --all).")
    ab.add_argument("--all", action="store_true", help="Field = every bot in bots/ (minus hero/challenger).")
    add_run_arguments(ab)

    check = commands.add_parser("check", help="Submission check + latency probe.")
    check.add_argument("bot")
    check.add_argument("--tables", type=int, default=4)

    stats = commands.add_parser("stats", help="Behavioural statistics from a hand log.")
    stats.add_argument("file", type=Path)
    stats.add_argument("--json", action="store_true")
    stats.add_argument("--out", type=Path, default=None, help="Write the markdown report here.")

    rep = commands.add_parser("report", help="Re-render a run directory.")
    rep.add_argument("run_dir", type=Path)
    rep.add_argument("--publish", action="store_true")

    dash = commands.add_parser("dashboard", help="Rebuild results/dashboard.html (and open it).")
    dash.add_argument("--no-open", action="store_true")

    watch = commands.add_parser("watch", help="Re-run the ladder whenever bots/ changes.")
    watch.add_argument("--interval", type=int, default=30, help="Seconds between checks.")
    add_run_arguments(watch)
    return parser


def progress_printer(quiet: bool):
    last = {"t": 0.0}

    def show(done: int, total: int) -> None:
        now = time.time()
        if not quiet and (done == total or now - last["t"] > 2):
            last["t"] = now
            print(f"\r  {done}/{total} tables", end="" if done < total else "\n", file=sys.stderr, flush=True)

    return show


def run_plan(args: argparse.Namespace, refs: list[BotRef], plan: planlib.Plan, name: str, *, publish: bool = False) -> Path:
    rules = make_rules(
        players=args.players,
        decision_ms=args.decision_ms,
        hand_cap=args.hand_cap,
        random_payouts=args.random_payouts,
    )
    paths = {ref.label: ref.path for ref in refs}
    writer = report.RunWriter(name, refs=refs, plan=plan, rules=rules, mode=args.mode, argv=sys.argv[1:])
    if args.log:
        writer.enable_log()
    if args.history:
        if args.history not in paths:
            raise SystemExit(f"--history {args.history}: not one of the bots in this run.")
        writer.enable_history(args.history)
    keep_log = bool(args.log or args.history)
    if not args.quiet:
        print(f"{plan.scheme}: {len(plan.tables)} tables, {len(refs)} bots, seed {plan.seed}, {args.mode} mode -> {writer.dir}", file=sys.stderr)
    progress = progress_printer(args.quiet)
    if args.mode == "fast":
        from arena import fast

        outcomes = fast.run(plan.tables, paths, rules=rules, workers=args.workers,
                            enforce_time=args.decision_ms > 0, keep_log=keep_log, progress=progress)
    else:
        from arena import strict

        outcomes = strict.run(plan.tables, paths, rules=rules, concurrency=args.concurrency,
                              shards=args.workers, keep_log=keep_log, progress=progress)
    for outcome in outcomes:
        writer.add(outcome)
    summary = writer.finish()
    summary["run_dir"] = writer.dir.relative_to(REPO).as_posix()
    (writer.dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    text = report.render(summary)
    (writer.dir / "leaderboard.md").write_text(text, encoding="utf-8")
    print(text)
    if publish:
        where = report.publish_ladder(summary, writer.dir)
        print(f"Published: {where.relative_to(REPO).as_posix()}", file=sys.stderr)
    if not args.no_experiment_log:
        report.append_experiment(report.experiment_entry(summary, writer.dir, args.agent, args.question))
    from arena import dashboard

    dashboard.write()
    return writer.dir


def relaunch_in_wsl() -> int:
    """Strict mode on Windows: run the same command inside WSL with the Linux venv."""
    linux_repo = "/mnt/" + REPO.drive[0].lower() + REPO.as_posix()[2:]
    python = f"{linux_repo}/starter-kit/.venv-wsl/bin/python"
    argv = " ".join(_shell_quote(a) for a in sys.argv[1:])
    script = f"cd {_shell_quote(linux_repo)} && {python} -m arena {argv}"
    print(f"[arena] strict mode: re-launching in WSL: {script}", file=sys.stderr)
    return subprocess.call(["wsl.exe", "-e", "bash", "-lc", script])


def _shell_quote(text: str) -> str:
    return "'" + text.replace("'", "'\\''") + "'"


def main() -> None:
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to cp1252.
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args()
    if getattr(args, "mode", None) == "strict" and sys.platform == "win32":
        raise SystemExit(relaunch_in_wsl())

    if args.command == "list":
        for ref in botlib.pool(examples=True):
            kind = "example" if ref.path.is_relative_to(botlib.EXAMPLES_DIR) else "pool"
            print(f"{ref.label:24s} {kind:8s} {ref.path}")
        if botlib.is_bot_dir(botlib.SUBMISSION_DIR):
            print(f"{'bot':24s} {'submit':8s} {botlib.SUBMISSION_DIR}")
        return

    seed = getattr(args, "seed", None) or secrets.token_hex(4)

    if args.command in ("ladder", "watch"):
        refs = botlib.pool(examples=not getattr(args, "no_examples", False))
        if botlib.is_bot_dir(botlib.SUBMISSION_DIR):
            refs.append(BotRef("bot", botlib.SUBMISSION_DIR.resolve()))
        refs = botlib.unique_labels(refs)
        if len(refs) < 2:
            raise SystemExit("The pool needs at least two bots (bots/<name>/agent.py).")
        if args.command == "watch":
            watch(args, refs)
            return
        plan = planlib.league_plan([r.label for r in refs], seed=seed, tables=args.tables, players=args.players)
        run_plan(args, refs, plan, args.name or "ladder", publish=True)
        return

    if args.command == "league":
        refs = botlib.resolve_many(args.bots, all_pool=args.all, examples=args.examples)
        if len(refs) < 2:
            raise SystemExit("Give at least two bots (or --all / --examples).")
        plan = planlib.league_plan([r.label for r in refs], seed=seed, tables=args.tables, players=args.players)
        run_plan(args, refs, plan, args.name or "league", publish=args.publish)
        return

    if args.command == "ab":
        hero, challenger = botlib.resolve(args.hero), botlib.resolve(args.challenger)
        field_names = args.field or (["min_raiser", "check_or_fold"] if not args.all else [])
        field = botlib.resolve_many(field_names, all_pool=args.all, examples=False)
        field = [f for f in field if f.path not in (hero.path, challenger.path)]
        if hero.label == challenger.label:
            challenger = BotRef(challenger.label + "@B", challenger.path)
        refs = botlib.unique_labels([hero, challenger] + field)
        hero, challenger, field = refs[0], refs[1], refs[2:]
        plan = planlib.ab_plan(hero.label, challenger.label, [f.label for f in field], seed=seed, tables=args.tables, players=args.players)
        run_plan(args, refs, plan, args.name or f"ab-{challenger.label}-vs-{hero.label}")
        return

    if args.command == "check":
        check(botlib.resolve(args.bot), args.tables)
        return

    if args.command == "stats":
        from arena import history_stats

        text, data = history_stats.analyze(args.file)
        if args.out:
            args.out.write_text(text, encoding="utf-8")
        print(json.dumps(data, indent=2) if args.json else text)
        return

    if args.command == "report":
        rerender(args.run_dir, publish=args.publish)
        return

    if args.command == "dashboard":
        from arena import dashboard

        path = dashboard.write(open_browser=not args.no_open)
        print(path)
        return


def check(ref: BotRef, tables: int) -> None:
    import tempfile

    from poker_agent_sdk.bundle import SubmissionError, pack

    from arena import fast

    print(f"Checking {ref.label} at {ref.path}")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            result = pack(ref.path, Path(tmp) / "bot.zip")
            print(f"  submission check: OK ({result.size_bytes} bytes, {len(result.files)} files, sha256 {result.sha256[:12]})")
        except (SubmissionError, OSError, ValueError) as error:
            print(f"  submission check: FAILED — {error}")
    probe = fast.latency_probe(ref.path, tables=tables)
    print(f"  self-play {tables} tables: {probe['decisions']} decisions, {probe['failures']} failures")
    print(f"  latency p50 {probe['p50_ms']:.3f} ms, p90 {probe['p90_ms']:.3f}, p99 {probe['p99_ms']:.3f}, max {probe['max_ms']:.3f}; "
          f"over 1 ms: {100 * probe['over_1ms_share']:.2f}% of decisions")
    print(f"  memory max {probe['mem_max_bytes']} bytes (keep under 16384)")
    verdict = []
    if probe["failures"]:
        verdict.append("FAILURES — fix before anything else")
    if probe["p99_ms"] > 0.6:
        verdict.append("p99 above 0.6 ms in-process: the platform adds overhead, expect timeouts; run --mode strict")
    if probe["mem_max_bytes"] > 16 * 1024:
        verdict.append("memory over 16 KB")
    print("  verdict: " + ("; ".join(verdict) if verdict else "OK"))


def rerender(run_dir: Path, *, publish: bool) -> None:
    run_dir = run_dir if run_dir.is_absolute() else (REPO / run_dir)
    run_info = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    plan = planlib.Plan.from_dict(json.loads((run_dir / "plan.json").read_text(encoding="utf-8")))
    outcomes = [TableOutcome.from_dict(json.loads(line)) for line in (run_dir / "tables.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    summary = report.summarize(outcomes, plan, run_info)
    summary["run_dir"] = run_dir.relative_to(REPO).as_posix()
    text = report.render(summary)
    (run_dir / "leaderboard.md").write_text(text, encoding="utf-8")
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(text)
    if publish:
        report.publish_ladder(summary, run_dir)


def watch(args: argparse.Namespace, refs: list[BotRef]) -> None:
    """Loop: whenever any bot's files change (or a bot appears), run the ladder and publish."""
    print(f"Watching {botlib.POOL_DIR} every {args.interval}s. Ctrl+C to stop.", file=sys.stderr)
    last: dict[str, str] = {}
    while True:
        refs = botlib.unique_labels(botlib.pool(examples=not getattr(args, "no_examples", False))
                                    + ([BotRef("bot", botlib.SUBMISSION_DIR.resolve())] if botlib.is_bot_dir(botlib.SUBMISSION_DIR) else []))
        current = {ref.label: ref.fingerprint() for ref in refs}
        if current != last and len(refs) >= 2:
            changed = sorted(k for k in current if last.get(k) != current[k])
            print(f"[watch] changed: {', '.join(changed)} — running ladder", file=sys.stderr)
            try:
                plan = planlib.league_plan([r.label for r in refs], seed=args.seed or secrets.token_hex(4), tables=args.tables, players=args.players)
                run_plan(args, refs, plan, args.name or "ladder", publish=True)
            except Exception as error:  # noqa: BLE001 - keep watching.
                print(f"[watch] run failed: {error!r}", file=sys.stderr)
            last = current
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
