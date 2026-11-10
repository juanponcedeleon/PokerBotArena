"""arena/results/dashboard.html — a self-contained page showing who is winning.

Rebuilt after every run (and by `python -m arena dashboard`). Open it in a browser and leave
the tab: it reloads itself every 60 s, so the watcher's ladder runs show up by themselves.
Everything is inline (data, SVG, styles); no network, no libraries.
"""

from __future__ import annotations

import html
import json
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any

from arena.bots import REPO

RESULTS = REPO / "arena" / "results"

# Categorical palette (validated default, see dataviz palette.md); slot = bot's fixed index.
LIGHT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
DARK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"]
OTHER = "#898781"


def load_runs() -> list[dict[str, Any]]:
    runs = []
    if not RESULTS.is_dir():
        return runs
    for directory in sorted(RESULTS.iterdir()):
        summary = directory / "summary.json"
        if directory.is_dir() and summary.is_file():
            try:
                data = json.loads(summary.read_text(encoding="utf-8"))
            except ValueError:
                continue
            data["_dir"] = directory.name
            runs.append(data)
    runs.sort(key=lambda r: r["run"]["started"])
    return runs


def slot_map(labels: list[str]) -> dict[str, int]:
    """Stable colour per bot: alphabetical order of every bot ever seen, first 8 get a hue."""
    return {label: i for i, label in enumerate(sorted(labels))}


def esc(text: Any) -> str:
    return html.escape(str(text))


def f(value: Any, digits: int = 2) -> str:
    if value is None or (isinstance(value, float) and value != value):
        return "–"
    return f"{value:.{digits}f}" if isinstance(value, float) else str(value)


def color_css(slots: dict[str, int]) -> str:
    light = "\n".join(
        f"  --bot-{i}: {LIGHT[i] if i < 8 else OTHER};" for i in range(max(len(slots), 1))
    )
    dark = "\n".join(
        f"  --bot-{i}: {DARK[i] if i < 8 else OTHER};" for i in range(max(len(slots), 1))
    )
    return light, dark


def bar_chart(ranking: list[dict[str, Any]], slots: dict[str, int]) -> str:
    """Horizontal bars of average points with 95% CI whiskers."""
    if not ranking:
        return "<p class='muted'>No ladder run yet.</p>"
    width, row_h, left, right = 760, 34, 190, 70
    height = row_h * len(ranking) + 40
    maximum = max((r["avg_points"] + (r["ci95"] or 0)) for r in ranking if r["avg_points"] == r["avg_points"])
    maximum = max(10.0, maximum * 1.05)
    scale = (width - left - right) / maximum
    parts = [f"<svg class='chart' viewBox='0 0 {width} {height}' role='img' aria-label='Average points per table with 95% confidence intervals'>"]
    for tick in range(0, int(maximum) + 1, 5 if maximum <= 40 else 10):
        x = left + tick * scale
        parts.append(f"<line class='grid' x1='{x:.1f}' y1='8' x2='{x:.1f}' y2='{height - 28}'/>")
        parts.append(f"<text class='tick' x='{x:.1f}' y='{height - 10}' text-anchor='middle'>{tick}</text>")
    for i, row in enumerate(ranking):
        y = 12 + i * row_h
        pts = row["avg_points"] if row["avg_points"] == row["avg_points"] else 0.0
        ci = row["ci95"] if row["ci95"] == row["ci95"] else 0.0
        slot = slots.get(row["label"], 99)
        w = max(0.0, pts * scale)
        label = esc(row["label"])
        tip = f"{label}: {pts:.2f} ± {ci:.2f} pts over {row['seats']} seats; avg place {row['avg_place']:.2f}; failures {row['failures']}"
        parts.append(f"<g class='bar' tabindex='0'><title>{tip}</title>")
        parts.append(f"<text class='label' x='{left - 10}' y='{y + 17}' text-anchor='end'>{label}</text>")
        parts.append(f"<rect x='{left}' y='{y + 4}' width='{w:.1f}' height='{row_h - 12}' rx='4' style='fill:var(--bot-{slot})'/>")
        if ci:
            x0, x1 = left + (pts - ci) * scale, left + (pts + ci) * scale
            ym = y + row_h / 2 - 2
            parts.append(f"<line class='whisker' x1='{x0:.1f}' y1='{ym}' x2='{x1:.1f}' y2='{ym}'/>")
            parts.append(f"<line class='whisker' x1='{x0:.1f}' y1='{ym - 5}' x2='{x0:.1f}' y2='{ym + 5}'/>")
            parts.append(f"<line class='whisker' x1='{x1:.1f}' y1='{ym - 5}' x2='{x1:.1f}' y2='{ym + 5}'/>")
        parts.append(f"<text class='value' x='{left + (pts + ci) * scale + 8:.1f}' y='{y + 17}'>{pts:.1f}</text>")
        parts.append("</g>")
    parts.append(f"<line class='axis' x1='{left}' y1='8' x2='{left}' y2='{height - 28}'/>")
    parts.append("</svg>")
    return "".join(parts)


def trend_chart(ladders: list[dict[str, Any]], slots: dict[str, int]) -> str:
    """Average points per bot across ladder runs (one line per bot)."""
    if len(ladders) < 2:
        return "<p class='muted'>Trend appears after the second ladder run.</p>"
    series: dict[str, list[tuple[int, float, float]]] = {}
    for index, run in enumerate(ladders):
        for row in run["ranking"]:
            if row["avg_points"] == row["avg_points"]:
                series.setdefault(row["label"], []).append((index, row["avg_points"], row["ci95"] or 0.0))
    width, height, left, right, top, bottom = 760, 300, 48, 150, 16, 36
    n = len(ladders)
    ymax = max(10.0, max(p for s in series.values() for _, p, _ in s) * 1.1)
    sx = (width - left - right) / max(1, n - 1)
    sy = (height - top - bottom) / ymax
    parts = [f"<svg class='chart' viewBox='0 0 {width} {height}' role='img' aria-label='Average points per bot across ladder runs'>"]
    for tick in range(0, int(ymax) + 1, 10):
        y = height - bottom - tick * sy
        parts.append(f"<line class='grid' x1='{left}' y1='{y:.1f}' x2='{width - right}' y2='{y:.1f}'/>")
        parts.append(f"<text class='tick' x='{left - 8}' y='{y + 4:.1f}' text-anchor='end'>{tick}</text>")
    step = max(1, round(n / 6))
    for index, run in enumerate(ladders):
        x = left + index * sx
        when = run["run"]["started"][5:16].replace("T", " ")
        if index % step == 0 or index == n - 1:
            parts.append(f"<text class='tick' x='{x:.1f}' y='{height - 12}' text-anchor='middle'>{esc(when)}</text>")
    ordered = sorted(series.items(), key=lambda kv: -kv[1][-1][1])
    for label, points in ordered:
        slot = slots.get(label, 99)
        path = " ".join(f"{'M' if i == 0 else 'L'}{left + idx * sx:.1f},{height - bottom - p * sy:.1f}" for i, (idx, p, _) in enumerate(points))
        parts.append(f"<path class='line' d='{path}' style='stroke:var(--bot-{slot})'/>")
        for idx, p, ci in points:
            x, y = left + idx * sx, height - bottom - p * sy
            tip = f"{esc(label)} — run {idx + 1}: {p:.2f} ± {ci:.2f}"
            parts.append(f"<circle class='dot' cx='{x:.1f}' cy='{y:.1f}' r='4' style='fill:var(--bot-{slot})'><title>{tip}</title></circle>")
    # Direct labels at the line ends, pushed apart so they never overlap (top to bottom).
    wanted = [(label, height - bottom - points[-1][1] * sy, points[-1][0]) for label, points in ordered]
    placed: list[float] = []
    for label, y, idx in wanted:
        y = max(top + 6, y)
        if placed:
            y = max(y, placed[-1] + 13)
        placed.append(y)
        x_end = left + idx * sx
        y_dot = height - bottom - series[label][-1][1] * sy
        if abs(y - y_dot) > 6:  # a leader line from the dot to the moved label
            parts.append(f"<line class='leader' x1='{x_end + 5:.1f}' y1='{y_dot:.1f}' x2='{x_end + 9:.1f}' y2='{y:.1f}'/>")
        parts.append(f"<text class='label small' x='{x_end + 10:.1f}' y='{y + 4:.1f}'>{esc(label)}</text>")
    parts.append(f"<line class='axis' x1='{left}' y1='{height - bottom}' x2='{width - right}' y2='{height - bottom}'/>")
    parts.append("</svg>")
    return "".join(parts)


def leaderboard_table(ranking: list[dict[str, Any]], slots: dict[str, int]) -> str:
    rows = []
    for rank, r in enumerate(ranking, 1):
        slot = slots.get(r["label"], 99)
        flag = ""
        if r["failures"]:
            flag = " <span class='status critical' title='failed decisions'>✖ failures</span>"
        elif (r["lat_p99_ms"] or 0) > 0.6:
            flag = " <span class='status warning' title='p99 latency above 0.6 ms in-process'>▲ slow</span>"
        rows.append(
            f"<tr><td class='num'>{rank}</td>"
            f"<td><span class='swatch' style='background:var(--bot-{slot})'></span>{esc(r['label'])}{flag}</td>"
            f"<td class='num'><b>{f(r['avg_points'])}</b> <span class='muted'>± {f(r['ci95'])}</span></td>"
            f"<td class='num'>{f(r['avg_place'])}</td><td class='num'>{f(100 * r['top3_share'], 0)}%</td>"
            f"<td class='num'>{f(100 * r['survived_share'], 0)}%</td><td class='num'>{r['seats']}</td>"
            f"<td class='num'>{r['failures']}</td><td class='num'>{f(r['lat_p99_ms'], 3)}</td>"
            f"<td class='num'>{r['mem_max_bytes']}</td></tr>"
        )
    return (
        "<table><thead><tr><th>#</th><th>bot</th><th>pts / table</th><th>avg place</th><th>top-3</th>"
        "<th>survived</th><th>seats</th><th>fails</th><th>p99 ms</th><th>mem B</th></tr></thead><tbody>"
        + "".join(rows) + "</tbody></table>"
    )


def h2h_matrix(summary: dict[str, Any]) -> str:
    labels = [r["label"] for r in summary["ranking"]]
    h2h = summary.get("head_to_head", {})
    if len(labels) < 2:
        return ""
    head = "<tr><th></th>" + "".join(f"<th class='rot'><div>{esc(b)}</div></th>" for b in labels) + "</tr>"
    rows = []
    for a in labels:
        cells = []
        for b in labels:
            if a == b:
                cells.append("<td class='self'></td>")
                continue
            w, t, l = h2h.get(a, {}).get(b, [0, 0, 0])
            total = w + t + l
            share = (w + 0.5 * t) / total if total else 0.5
            step = min(6, int(share * 7))  # 7 steps of the sequential blue ramp
            ink = "#fff" if step >= 4 else "var(--text-primary)"
            cells.append(f"<td class='cell' style='background:var(--seq-{step});color:{ink}' title='{esc(a)} above {esc(b)}: {w}-{t}-{l}'>{f(100 * share, 0)}%</td>")
        rows.append(f"<tr><th class='rowh'>{esc(a)}</th>{''.join(cells)}</tr>")
    return f"<table class='matrix'>{head}{''.join(rows)}</table>"


def ab_table(runs: list[dict[str, Any]]) -> str:
    abs_ = [r for r in runs if "ab" in r][-15:]
    if not abs_:
        return "<p class='muted'>No A/B runs yet. <code>python -m arena ab HERO CHALLENGER --tables 300</code></p>"
    rows = []
    for r in reversed(abs_):
        ab = r["ab"]
        p = ab.get("p_value")
        significant = p == p and p is not None and p < 0.05
        if significant and ab["mean_diff"] > 0:
            verdict = f"<span class='status good'>✔ {esc(ab['challenger'])} better</span>"
        elif significant:
            verdict = f"<span class='status serious'>✖ {esc(ab['challenger'])} worse</span>"
        else:
            verdict = "<span class='muted'>not separated</span>"
        sign = "+" if ab["mean_diff"] >= 0 else ""
        rows.append(
            f"<tr><td>{esc(r['run']['started'][:16].replace('T', ' '))}</td><td>{esc(ab['challenger'])} <span class='muted'>vs</span> {esc(ab['hero'])}</td>"
            f"<td class='num'>{ab['n']}</td><td class='num'><b>{sign}{f(ab['mean_diff'])}</b> <span class='muted'>± {f(ab['ci95'])}</span></td>"
            f"<td class='num'>{f(p, 3)}</td><td class='num'>{ab['b_better_tables']} / {ab['tied_tables']} / {ab['a_better_tables']}</td>"
            f"<td>{verdict}</td><td class='muted'>{esc(r['run'].get('mode', ''))} · <a href='{esc(r['_dir'])}/leaderboard.md'>{esc(r['_dir'])}</a></td></tr>"
        )
    return (
        "<table><thead><tr><th>when</th><th>challenger vs hero</th><th>pairs</th><th>diff</th><th>p</th>"
        "<th>better / tied / worse</th><th>verdict</th><th>run</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


def recent_runs(runs: list[dict[str, Any]]) -> str:
    rows = []
    for r in reversed(runs[-12:]):
        top = r["ranking"][0]["label"] if r["ranking"] else "–"
        rows.append(
            f"<tr><td>{esc(r['run']['started'][:16].replace('T', ' '))}</td><td>{esc(r['run']['name'])}</td><td>{esc(r['run']['scheme'])}</td>"
            f"<td>{esc(r['run'].get('mode', ''))}</td><td class='num'>{r['tables']}</td><td>{esc(top)}</td>"
            f"<td class='muted'>{esc(r['run'].get('agent', '') or '')}</td><td><a href='{esc(r['_dir'])}/leaderboard.md'>{esc(r['_dir'])}</a></td></tr>"
        )
    return ("<table><thead><tr><th>when</th><th>name</th><th>scheme</th><th>mode</th><th>tables</th><th>winner</th><th>agent</th><th>run</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")


def build() -> str:
    runs = load_runs()
    ladders = [r for r in runs if r["run"]["scheme"] == "league" and r["run"]["name"] == "ladder"]
    latest = ladders[-1] if ladders else next((r for r in reversed(runs) if r["run"]["scheme"] == "league"), None)
    labels = sorted({row["label"] for r in runs for row in r["ranking"]})
    slots = slot_map(labels)
    light, dark = color_css(slots)
    ranking = latest["ranking"] if latest else []
    leader = ranking[0] if ranking else None
    stamp = latest["run"]["started"].replace("T", " ") if latest else "–"
    hero = (
        f"<div class='hero'><div class='hero-label'>Leading the arena</div>"
        f"<div class='hero-value'><span class='swatch big' style='background:var(--bot-{slots.get(leader['label'], 99)})'></span>{esc(leader['label'])}</div>"
        f"<div class='hero-sub'>{f(leader['avg_points'])} ± {f(leader['ci95'])} points per table · {latest['tables']} tables · {latest['run'].get('mode', '')} mode · ladder of {stamp}</div></div>"
        if leader else "<div class='hero'><div class='hero-label'>No ladder yet</div><div class='hero-sub'>Run <code>python -m arena ladder</code>.</div></div>"
    )
    runner_up = ""
    if len(ranking) > 1:
        gap = ranking[0]["avg_points"] - ranking[1]["avg_points"]
        sep = gap > (ranking[0]["ci95"] or 0) + (ranking[1]["ci95"] or 0)
        runner_up = (f"<p class='muted'>Gap to #2 <b>{esc(ranking[1]['label'])}</b>: {gap:.2f} points — "
                     + ("intervals do not overlap: the lead is real." if sep else "intervals overlap: not separated yet, run more tables.") + "</p>")
    bots_pages = " · ".join(f"<a href='bots/{esc(l)}.md'>{esc(l)}</a>" for l in labels)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="60">
<title>Arena Dashboard</title>
<style>
:root {{ color-scheme: light; --page:#f9f9f7; --surface:#fcfcfb; --text-primary:#0b0b0b; --text-secondary:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7; --border:rgba(11,11,11,.10);
  --seq-0:#cde2fb; --seq-1:#b7d3f6; --seq-2:#9ec5f4; --seq-3:#6da7ec; --seq-4:#3987e5; --seq-5:#2a78d6; --seq-6:#1c5cab;
  --good:#0ca30c; --warning:#fab219; --serious:#ec835a; --critical:#d03b3b;
{light}
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ color-scheme: dark; --page:#0d0d0d; --surface:#1a1a19; --text-primary:#f0efec; --text-secondary:#c3c2b7;
  --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10);
  --seq-0:#104281; --seq-1:#184f95; --seq-2:#1c5cab; --seq-3:#256abf; --seq-4:#2a78d6; --seq-5:#3987e5; --seq-6:#5598e7;
{dark}
}} }}
:root[data-theme="dark"] {{ color-scheme: dark; --page:#0d0d0d; --surface:#1a1a19; --text-primary:#f0efec; --text-secondary:#c3c2b7; --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10);
{dark}
}}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--page); color:var(--text-primary); font: 15px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif; }}
main {{ max-width: 1100px; margin: 0 auto; padding: 24px 16px 48px; }}
header {{ display:flex; justify-content:space-between; align-items:baseline; gap:16px; flex-wrap:wrap; }}
h1 {{ font-size: 20px; margin: 0; }} h2 {{ font-size: 15px; margin: 0 0 10px; color: var(--text-secondary); font-weight: 600; letter-spacing:.01em; }}
.card {{ background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:16px 18px; margin-top:16px; overflow-x:auto; }}
.grid2 {{ display:grid; grid-template-columns: 1fr; gap:16px; }} @media (min-width: 900px) {{ .grid2 {{ grid-template-columns: 1fr 1fr; }} }}
.grid2 .card {{ margin-top:0; }}
.hero-label {{ color:var(--text-secondary); font-size:13px; text-transform:uppercase; letter-spacing:.06em; }}
.hero-value {{ font-size: 40px; font-weight: 700; margin: 4px 0; display:flex; align-items:center; gap:12px; }}
.hero-sub {{ color:var(--text-secondary); }}
.muted {{ color: var(--muted); }} .num {{ text-align:right; font-variant-numeric: tabular-nums; }}
table {{ border-collapse: collapse; width:100%; font-size:14px; }} th, td {{ padding: 6px 10px; border-bottom: 1px solid var(--grid); text-align:left; vertical-align:top; }}
th {{ color: var(--text-secondary); font-weight:600; font-size:12.5px; }} tbody tr:hover {{ background: var(--grid); }}
.swatch {{ display:inline-block; width:10px; height:10px; border-radius:3px; margin-right:8px; vertical-align:middle; }} .swatch.big {{ width:18px; height:18px; border-radius:5px; }}
.status {{ font-size:12px; padding:1px 7px; border-radius:999px; color:#fff; margin-left:6px; white-space:nowrap; }}
.status.good {{ background:var(--good); }} .status.warning {{ background:var(--warning); color:#0b0b0b; }} .status.serious {{ background:var(--serious); }} .status.critical {{ background:var(--critical); }}
.chart {{ width:100%; height:auto; display:block; }} .grid {{ stroke: var(--grid); stroke-width:1; }} .axis {{ stroke: var(--axis); stroke-width:1; }}
.tick {{ fill: var(--muted); font-size: 11px; }} .label {{ fill: var(--text-primary); font-size: 13px; }} .value {{ fill: var(--text-secondary); font-size: 12px; font-variant-numeric: tabular-nums; }}
.whisker {{ stroke: var(--text-primary); stroke-width: 1.5; opacity:.7; }} .label.small {{ font-size: 11px; }} .leader {{ stroke: var(--muted); stroke-width: 1; }} .line {{ fill:none; stroke-width:2; }} .dot {{ stroke: var(--surface); stroke-width:2; }}
.bar:hover rect, .bar:focus rect {{ filter: brightness(1.08); }} .bar:focus {{ outline:none; }}
.matrix th.rot {{ height: 110px; white-space:nowrap; vertical-align:bottom; }} .matrix th.rot > div {{ transform: translate(8px, 0) rotate(-55deg); transform-origin: left bottom; width: 20px; }}
.matrix td.cell {{ text-align:center; font-variant-numeric: tabular-nums; font-size:13px; min-width:52px; }} .matrix td.self {{ background: var(--grid); }} .matrix th.rowh {{ text-align:right; white-space:nowrap; }}
code {{ background: var(--grid); padding: 1px 5px; border-radius: 4px; font-size: 13px; }} a {{ color: inherit; }}
footer {{ color: var(--muted); font-size: 12.5px; margin-top: 24px; }}
</style></head>
<body>
<main>
<header><h1>PokerBot Arena</h1><div class="muted">generated {generated} · refreshes every 60 s · <a href="LEADERBOARD.md">LEADERBOARD.md</a> · <a href="watch.log">watch.log</a></div></header>
<div class="card">{hero}{runner_up}</div>
<div class="grid2" style="margin-top:16px">
  <div class="card"><h2>Points per table, latest ladder (bar = mean, whisker = 95% CI)</h2>{bar_chart(ranking, slots)}</div>
  <div class="card"><h2>Points per table across ladder runs ({len(ladders)} runs)</h2>{trend_chart(ladders, slots)}</div>
</div>
<div class="card"><h2>Leaderboard — latest ladder</h2>{leaderboard_table(ranking, slots)}
<p class="muted">pts ± 95% CI; two bots whose intervals overlap are not separated. fails = timeouts + errors + illegal actions (any &gt; 0 is a bug). p99 above 0.6 ms in fast mode risks platform timeouts.</p></div>
<div class="card"><h2>Head-to-head: share of shared tables where the row bot finished above the column bot</h2>{h2h_matrix(latest) if latest else ''}</div>
<div class="card"><h2>A/B tests (paired; challenger takes the hero's seats in identical tables)</h2>{ab_table(runs)}</div>
<div class="card"><h2>Recent runs</h2>{recent_runs(runs)}</div>
<footer>Bot pages: {bots_pages or '–'}. Rebuild: <code>python -m arena dashboard</code>. Colours are fixed per bot across runs.</footer>
</main>
</body></html>
"""


def write(open_browser: bool = False) -> Path:
    RESULTS.mkdir(parents=True, exist_ok=True)
    path = RESULTS / "dashboard.html"
    path.write_text(build(), encoding="utf-8")
    if open_browser:
        webbrowser.open(path.as_uri())
    return path
