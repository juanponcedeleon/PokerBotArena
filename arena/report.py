"""Where results go and how they are rendered.

arena/results/
├── LEADERBOARD.md              ← the published standing: latest `ladder` run over the whole pool
├── bots/<label>.md             ← per-bot page: its latest ladder row, A/B results, failures
├── <stamp>-<name>/             ← one directory per run
│   ├── run.json                ← command, seed, rules, bots + fingerprints (reproducible)
│   ├── tables.jsonl            ← one line per table (seats, points, places, failures, latency)
│   ├── summary.json            ← aggregated statistics (what leaderboard.md is rendered from)
│   ├── leaderboard.md          ← the human-readable report for this run
│   ├── log.jsonl.gz            ← (--log) every hand with every card, for arena.history_stats
│   └── history-<hero>.jsonl.gz ← (--history HERO) participant-format replay for `replay`
└── ...
and one entry appended to strategy/08-experiments.md per run (unless --no-experiment-log).
"""

from __future__ import annotations

import csv
import gzip
import json
import platform
import secrets
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from poker_engine.history import private_view, public_view
from poker_engine.table import TableRules, rules_to_dict

from arena.bots import REPO, BotRef
from arena.outcome import TableOutcome
from arena.plan import Plan, base_label
from arena.stats import ab_comparison, aggregate, head_to_head

RESULTS = REPO / "arena" / "results"
EXPERIMENTS = REPO / "strategy" / "08-experiments.md"


def fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        if value != value:  # NaN
            return "-"
        return f"{value:.{digits}f}"
    return str(value)


class RunWriter:
    def __init__(self, name: str, *, refs: list[BotRef], plan: Plan, rules: TableRules, mode: str, argv: list[str]):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.dir = RESULTS / f"{stamp}-{name}-{secrets.token_hex(2)}"
        self.dir.mkdir(parents=True, exist_ok=False)
        self.refs = refs
        self.plan = plan
        self.rules = rules
        self.mode = mode
        self.started = datetime.now()
        self.outcomes: list[TableOutcome] = []
        self.run_info = {
            "name": name,
            "started": self.started.isoformat(timespec="seconds"),
            "argv": argv,
            "mode": mode,
            "seed": plan.seed,
            "scheme": plan.scheme,
            "hero": plan.hero,
            "challenger": plan.challenger,
            "tables_planned": len(plan.tables),
            "rules": rules_to_dict(rules),
            "bots": {ref.label: {"path": str(ref.path), "fingerprint": ref.fingerprint()} for ref in refs},
            "platform": platform.platform(),
            "python": sys.version.split()[0],
        }
        (self.dir / "run.json").write_text(json.dumps(self.run_info, indent=2), encoding="utf-8")
        (self.dir / "plan.json").write_text(json.dumps(plan.to_dict()), encoding="utf-8")
        self._tables = (self.dir / "tables.jsonl").open("w", encoding="utf-8")
        self._log: gzip.GzipFile | None = None
        self._history: Any = None
        self._history_hero: str | None = None

    def enable_log(self) -> None:
        self._log = gzip.open(self.dir / "log.jsonl.gz", "wt", encoding="utf-8")

    def enable_history(self, hero: str) -> None:
        """Participant-format history from the hero's seat (tables without the hero are skipped),
        for `replay` and for the same pipeline that will read real tournament downloads."""
        self._history_hero = hero
        self._history = (self.dir / f"history-{hero}.jsonl.gz").open("wb")
        copies = sorted({copy for spec in self.plan.tables for copy in spec.seats})
        # Entry ids are seat copies ("tight#2"); the hero's own seat at each table is exported
        # under the plain label so the kit's reader and `replay` find "you" in every table.
        header = {
            "tournament_id": f"arena-{self.plan.seed}",
            "you": hero,
            "entries": [{"entry_id": hero, "team_name": hero}]
            + [{"entry_id": copy, "team_name": base_label(copy)} for copy in copies],
        }
        self._history.write(gzip.compress((json.dumps(header, separators=(",", ":")) + "\n").encode(), mtime=0))

    def add(self, outcome: TableOutcome) -> None:
        self.outcomes.append(outcome)
        self._tables.write(json.dumps(outcome.to_dict(with_log=False), separators=(",", ":")) + "\n")
        raw = outcome.raw_table()
        if raw is None:
            return
        if self._log is not None:
            self._log.write(json.dumps(raw, separators=(",", ":")) + "\n")
        if self._history is not None:
            hero_seats = [i for i, label in enumerate(raw["labels"]) if label == self._history_hero]
            if hero_seats:
                seat = hero_seats[0]
                table = dict(raw)
                table["seats"] = list(raw["seats"])
                table["seats"][seat] = self._history_hero
                public = dict(public_view(table))
                private = private_view(table, seat)
                lines = json.dumps(public, separators=(",", ":")) + "\n" + json.dumps(private, separators=(",", ":")) + "\n"
                self._history.write(gzip.compress(lines.encode(), compresslevel=6, mtime=0))

    def finish(self) -> dict[str, Any]:
        self._tables.close()
        if self._log is not None:
            self._log.close()
        if self._history is not None:
            self._history.close()
        summary = summarize(self.outcomes, self.plan, self.run_info)
        summary["elapsed_s"] = round((datetime.now() - self.started).total_seconds(), 1)
        (self.dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
        write_seats_csv(self.dir / "seats.csv", self.outcomes)
        text = render(summary)
        (self.dir / "leaderboard.md").write_text(text, encoding="utf-8")
        return summary


def summarize(outcomes: list[TableOutcome], plan: Plan, run_info: dict[str, Any]) -> dict[str, Any]:
    rows = aggregate(outcomes)
    ranking = sorted(rows.values(), key=lambda r: (-(r["avg_points"] if r["avg_points"] == r["avg_points"] else -1), r["label"]))
    summary: dict[str, Any] = {
        "run": run_info,
        "run_dir": None,
        "tables": len(outcomes),
        "hands": sum(o.hands for o in outcomes),
        "ranking": ranking,
        "head_to_head": head_to_head(outcomes),
        "bot_errors": sorted({e[:400] for o in outcomes for e in o.bot_errors})[:20],
    }
    if plan.scheme == "ab" and plan.hero and plan.challenger:
        summary["ab"] = ab_comparison(outcomes, plan.hero, plan.challenger)
    return summary


def write_seats_csv(path: Path, outcomes: list[TableOutcome]) -> None:
    fields = [
        "table_id", "iteration", "number", "arm", "seed", "hands", "seat", "copy", "label", "filler",
        "points", "place", "decisions", "failures", "timeouts", "errors", "illegal", "truncated",
        "lat_p50_ms", "lat_p99_ms", "lat_max_ms", "mem_max_bytes", "bust_hand", "final_stack",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for outcome in outcomes:
            for seat in outcome.seats:
                row = {k: v for k, v in seat.to_dict().items() if k in fields}
                row.update(table_id=outcome.table_id, iteration=outcome.iteration, number=outcome.number,
                           arm=outcome.arm, seed=outcome.seed, hands=outcome.hands)
                writer.writerow(row)


def render(summary: dict[str, Any]) -> str:
    run = summary["run"]
    lines = [
        f"# Arena run `{run['name']}` — {run['mode']} mode",
        "",
        f"Started {run['started']} · seed `{run['seed']}` · scheme {run['scheme']} · "
        f"{summary['tables']} tables · {summary['hands']} hands · {summary.get('elapsed_s', '?')} s",
        "",
        "Command: `" + " ".join(run["argv"]) + "`",
        "",
    ]
    if run["mode"] == "fast":
        lines += ["Timing in fast mode excludes pipe/JSON overhead (optimistic by ~0.1–0.4 ms). "
                  "Confirm anything near 1 ms with `--mode strict`.", ""]
    if "ab" in summary:
        ab = summary["ab"]
        sign = "+" if ab["mean_diff"] >= 0 else ""
        verdict = "no significant difference"
        if ab["p_value"] == ab["p_value"] and ab["p_value"] < 0.05:
            verdict = f"**{ab['challenger']} is better**" if ab["mean_diff"] > 0 else f"**{ab['hero']} is better**"
        lines += [
            f"## A/B: `{ab['challenger']}` replaces `{ab['hero']}` in the same seats",
            "",
            f"| pairs | hero pts | challenger pts | diff (challenger − hero) | 95% CI | p | challenger better / tied / worse | verdict |",
            "|---|---|---|---|---|---|---|---|",
            f"| {ab['n']} | {fmt(ab['hero_avg_points'])} | {fmt(ab['challenger_avg_points'])} | "
            f"{sign}{fmt(ab['mean_diff'])} | ±{fmt(ab['ci95'])} | {fmt(ab['p_value'], 3)} | "
            f"{ab['b_better_tables']} / {ab['tied_tables']} / {ab['a_better_tables']} | {verdict} |",
            "",
        ]
        if ab.get("tables_for_1pt"):
            lines += [f"Pairs needed to resolve a 1-point difference at this variance: ~{ab['tables_for_1pt']}.", ""]
    lines += [
        "## Leaderboard (points per table, 50/30/20 + ICM at the hand cap)",
        "",
        "| # | bot | tables | seats | avg pts | ±95% | avg place | top-3 | survived | fail/decision | timeouts | errors | illegal | p50 ms | p99 ms | max ms | mem B |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for rank, row in enumerate(summary["ranking"], 1):
        lines.append(
            f"| {rank} | **{row['label']}** | {row['tables']} | {row['seats']} | {fmt(row['avg_points'])} | "
            f"{fmt(row['ci95'])} | {fmt(row['avg_place'])} | {fmt(100 * row['top3_share'], 0)}% | "
            f"{fmt(100 * row['survived_share'], 0)}% | {fmt(row['failure_rate'], 4)} | {row['timeouts']} | "
            f"{row['errors']} | {row['illegal']} | {fmt(row['lat_p50_ms'], 3)} | {fmt(row['lat_p99_ms'], 3)} | "
            f"{fmt(row['lat_max_ms'], 2)} | {row['mem_max_bytes']} |"
        )
    lines += ["", "Place distribution (share of scoring seats):", "", "| bot | " + " | ".join(f"{p}" for p in range(1, 9)) + " |",
              "|---|" + "---|" * 8]
    for row in summary["ranking"]:
        shares = row["place_share"]
        lines.append(f"| {row['label']} | " + " | ".join(f"{100 * shares.get(p, shares.get(str(p), 0.0)):.0f}%" for p in range(1, 9)) + " |")
    h2h = summary["head_to_head"]
    labels = [row["label"] for row in summary["ranking"]]
    if len(labels) > 1 and h2h:
        lines += ["", "## Head-to-head (row finished above column: wins-ties-losses)", "", "| | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
        for a in labels:
            cells = []
            for b in labels:
                if a == b:
                    cells.append("·")
                else:
                    w, t, l = h2h.get(a, {}).get(b, [0, 0, 0])
                    cells.append(f"{w}-{t}-{l}")
            lines.append(f"| **{a}** | " + " | ".join(cells) + " |")
    if summary["bot_errors"]:
        lines += ["", "## Bot errors (first occurrence per table; untrusted text)", ""]
        for text in summary["bot_errors"]:
            lines += ["```", text.strip(), "```"]
    lines += ["", f"Files: `{summary.get('run_dir') or ''}` (tables.jsonl, seats.csv, summary.json, run.json)."]
    return "\n".join(lines) + "\n"


def experiment_entry(summary: dict[str, Any], run_dir: Path, agent: str, question: str | None) -> str:
    run = summary["run"]
    date = run["started"][:10]
    top = summary["ranking"][:6]
    result = "; ".join(f"{r['label']} {fmt(r['avg_points'])}±{fmt(r['ci95'])} (fail {r['failures']})" for r in top)
    if "ab" in summary:
        ab = summary["ab"]
        result = (f"{ab['challenger']} − {ab['hero']} = {'+' if ab['mean_diff'] >= 0 else ''}{fmt(ab['mean_diff'])} "
                  f"±{fmt(ab['ci95'])} pts/table over {ab['n']} paired tables (p={fmt(ab['p_value'], 3)}). " + result)
    question = question or (f"A/B {run['challenger']} vs {run['hero']}" if run.get("challenger") else f"League: {run['name']}")
    rel = run_dir.relative_to(REPO).as_posix()
    return (
        f"\n**{date} | {agent} | {question}**\n"
        f"Setup: `python -m arena {' '.join(run['argv'])}` — {run['mode']} mode, seed `{run['seed']}`, "
        f"{summary['tables']} tables, bots: {', '.join(run['bots'])}.\n"
        f"Result: {result}\n"
        f"Decision: (fill in) → see `{rel}/leaderboard.md`.\n"
    )


def append_experiment(entry: str) -> None:
    EXPERIMENTS.parent.mkdir(parents=True, exist_ok=True)
    if not EXPERIMENTS.exists():
        EXPERIMENTS.write_text("# 08 — Experiment log (append-only)\n\nOne entry per run. Format: date | agent | question | setup | result | decision.\n\n---\n", encoding="utf-8")
    with EXPERIMENTS.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def publish_ladder(summary: dict[str, Any], run_dir: Path) -> Path:
    """Overwrite the published standing with this run and refresh each bot's page."""
    RESULTS.mkdir(parents=True, exist_ok=True)
    rel = run_dir.relative_to(REPO).as_posix()
    text = render(summary).replace("# Arena run", "# LEADERBOARD — latest full-pool ladder run\n\nSource run", 1)
    text += f"\nRe-run: `python -m arena ladder` · per-bot pages in `arena/results/bots/`. Full run: `{rel}/`.\n"
    (RESULTS / "LEADERBOARD.md").write_text(text, encoding="utf-8")
    pages = RESULTS / "bots"
    pages.mkdir(exist_ok=True)
    for rank, row in enumerate(summary["ranking"], 1):
        update_bot_page(pages / f"{row['label']}.md", row, rank, len(summary["ranking"]), summary, rel)
    return RESULTS / "LEADERBOARD.md"


def update_bot_page(path: Path, row: dict[str, Any], rank: int, field: int, summary: dict[str, Any], rel: str) -> None:
    h2h = summary["head_to_head"].get(row["label"], {})
    lines = [
        f"# {row['label']}",
        "",
        f"Latest ladder: **#{rank} of {field}**, {fmt(row['avg_points'])} ± {fmt(row['ci95'])} points/table over "
        f"{row['seats']} seats ({summary['run']['started']}, {summary['run']['mode']} mode, run `{rel}`).",
        "",
        f"- avg place {fmt(row['avg_place'])}, top-3 {fmt(100 * row['top3_share'], 0)}%, survived to hand cap {fmt(100 * row['survived_share'], 0)}%"
        + (f", avg bust hand {fmt(row['avg_bust_hand'], 0)}" if row["avg_bust_hand"] else ""),
        f"- failures {row['failures']} of {row['decisions']} decisions (timeouts {row['timeouts']}, errors {row['errors']}, illegal {row['illegal']}, memory cut {row['truncated']})",
        f"- latency p50 {fmt(row['lat_p50_ms'], 3)} ms, p99 {fmt(row['lat_p99_ms'], 3)} ms, max {fmt(row['lat_max_ms'], 2)} ms; memory max {row['mem_max_bytes']} B",
        "",
        "Head-to-head (finished above opponent: wins-ties-losses):",
        "",
    ]
    for other, (w, t, l) in sorted(h2h.items()):
        lines.append(f"- vs {other}: {w}-{t}-{l}")
    errors = [e for e in summary["bot_errors"] if e.startswith(row["label"])]
    if errors:
        lines += ["", "Errors:", ""] + [f"```\n{e}\n```" for e in errors[:5]]
    lines += ["", "History of ladder runs:", ""]
    previous = []
    if path.exists():
        text = path.read_text(encoding="utf-8")
        marker = "History of ladder runs:\n\n"
        if marker in text:
            previous = [l for l in text.split(marker, 1)[1].splitlines() if l.startswith("- ")]
    lines.append(f"- {summary['run']['started']}: #{rank}/{field}, {fmt(row['avg_points'])} ± {fmt(row['ci95'])} pts ({row['seats']} seats, {summary['run']['mode']})")
    lines += previous[:30]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
