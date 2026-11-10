#!/usr/bin/env python3
"""Pull live tournament data (hand histories, results, bot health) from the No Limit 2026 site
into data/, where every agent in this project can read it. Standard library only.

    python fetch_history.py                 # download hands + results for every completed round our bot played
    python fetch_history.py --all           # every completed round, even ones we forfeited (hands may be empty)
    python fetch_history.py --tables 500    # smaller subset: only the first 500 tables of each round
    python fetch_history.py --list          # show rounds, our result, and which files exist
    python fetch_history.py --tournament bd8406dc   # one round, by id or id prefix

Files (never overwritten once complete; delete one to re-download):
    data/hands/<kind>-<createdUTC>-<id8>.jsonl.gz            participant hand-history download
    data/hands/<kind>-<createdUTC>-<id8>-first-<N>.jsonl.gz  the --tables subset
    data/results/<kind>-<createdUTC>-<id8>.json              tournament record + full results table + our health row
    data/hands/INDEX.md                                      regenerated every run: one row per round

Hand-history format: starter-kit/hand-history/README.md. Readers: starter-kit/hand-history/read.py,
arena/history_stats.py (participant downloads are detected automatically).

API: GET /api/teams/{team}/tournaments/{tournament}/hands[?tables=N] -> application/gzip.
The API key is read from NO_LIMIT_API_KEY, else %APPDATA%\\no-limit-2026\\api-key or
~/.config/no-limit-2026/api-key (saved by the setup skill).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SITE = "https://pokerbot.sequoiacap.com/tournament"
API = SITE + "/api"
ROOT = Path(__file__).resolve().parent
HANDS_DIR = ROOT / "data" / "hands"
RESULTS_DIR = ROOT / "data" / "results"


def read_key() -> str:
    key = os.environ.get("NO_LIMIT_API_KEY", "").strip()
    if key:
        return key
    candidates = []
    if os.environ.get("APPDATA"):
        candidates.append(Path(os.environ["APPDATA"]) / "no-limit-2026" / "api-key")
    candidates.append(Path.home() / ".config" / "no-limit-2026" / "api-key")
    for path in candidates:
        try:
            key = path.read_text(encoding="ascii").strip()
        except OSError:
            continue
        if key:
            return key
    sys.exit("No API key. Set NO_LIMIT_API_KEY or save one to " + " or ".join(map(str, candidates)))


class Api:
    def __init__(self, key: str) -> None:
        self.key = key

    def _request(self, path: str) -> urllib.request.Request:
        return urllib.request.Request(API + path, headers={"Authorization": f"Bearer {self.key}"})

    def get_json(self, path: str):
        try:
            with urllib.request.urlopen(self._request(path), timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if e.code == 401:
                sys.exit("API key wrong or expired (401): make a new one at Settings -> API keys")
            raise SystemExit(f"GET {path}: HTTP {e.code} {body[:300]}")

    def download(self, path: str, dest: Path) -> int:
        """Stream to dest.part, then rename. Returns bytes written."""
        part = dest.with_suffix(dest.suffix + ".part")
        total = 0
        try:
            with urllib.request.urlopen(self._request(path), timeout=300) as resp, part.open("wb") as out:
                while True:
                    chunk = resp.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
                    total += len(chunk)
                    print(f"\r   {total / 1e6:8.1f} MB", end="", flush=True)
        except urllib.error.HTTPError as e:
            part.unlink(missing_ok=True)
            raise SystemExit(f"\nGET {path}: HTTP {e.code} {e.read().decode('utf-8', 'replace')[:300]}")
        except BaseException:
            part.unlink(missing_ok=True)
            raise
        print()
        part.replace(dest)
        return total


def team_info(api: Api) -> tuple[str, str, str]:
    auth = api.get_json("/auth/api-key")
    teams = auth.get("teams") or []
    if not teams:
        sys.exit("This account is not on a team yet.")
    chosen = os.environ.get("NO_LIMIT_TEAM_ID")
    team = next((t for t in teams if t["team_id"] == chosen), teams[0]) if chosen else teams[0]
    if len(teams) > 1 and not chosen:
        print(f"note: several teams, using {team['team_name']}; set NO_LIMIT_TEAM_ID to pick another", file=sys.stderr)
    return team["team_id"], team["competition_id"], team["team_name"]


def stamp(iso: str) -> str:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%Y%m%dT%H%M")


def base_name(t: dict) -> str:
    return f"{t['kind']}-{stamp(t['created_at'])}-{t['id'][:8]}"


def our_row(results: dict, team_id: str) -> tuple[int | None, dict | None]:
    items = results.get("items", [])
    for rank, row in enumerate(items, 1):
        if row.get("team_id") == team_id:
            return rank, row
    return None, None


def write_index(rounds: list[dict], team_name: str) -> None:
    HANDS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Live tournament data for team {team_name}",
        "",
        f"Regenerated by `python fetch_history.py` on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}.",
        "Hand files follow the participant download format (starter-kit/hand-history/README.md).",
        "`arena/history_stats.py <file>` and `starter-kit/hand-history/read.py <file>` read them directly.",
        "Decisions/missed are our bot's own counts in that round (team health). Rank is among non-forfeiting teams.",
        "",
        "| round (kind, UTC) | id | tables | teams | our avg pts | rank | decisions | missed | hands file | subset | results |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rounds:
        t = r["tournament"]
        rank, row = r["rank"], r["row"]
        health = r["health"] or {}
        files = sorted(p.name for p in HANDS_DIR.glob(base_name(t) + "*.jsonl.gz"))
        full = next((f for f in files if "-first-" not in f), "")
        subsets = ", ".join(f for f in files if "-first-" in f)
        res = (RESULTS_DIR / (base_name(t) + ".json")).name if (RESULTS_DIR / (base_name(t) + ".json")).exists() else ""
        lines.append(
            f"| {t['kind']} {t['created_at'][:16].replace('T', ' ')} | `{t['id'][:8]}` | {t['iterations']} | "
            f"{t['entries'] - t['forfeits']}/{t['entries']} | "
            f"{row['average_points']:.3f} ± {row['margin_of_error']:.2f}" if row else
            f"| {t['kind']} {t['created_at'][:16].replace('T', ' ')} | `{t['id'][:8]}` | {t['iterations']} | "
            f"{t['entries'] - t['forfeits']}/{t['entries']} | forfeit"
        )
        lines[-1] += (
            f" | {rank or '-'} | {health.get('decisions', '-')} | {health.get('missed', '-')} | "
            f"{'`data/hands/' + full + '`' if full else '-'} | {subsets or '-'} | {'`data/results/' + res + '`' if res else '-'} |"
        )
    lines += ["", "Columns: tables = sit-and-go tables played per entry (iterations). Rank 1 = best average points."]
    (HANDS_DIR / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--list", action="store_true", help="list rounds and existing files; download nothing")
    p.add_argument("--all", action="store_true", help="include rounds our bot forfeited")
    p.add_argument("--tables", type=int, metavar="N", help="download only the first N tables of each round")
    p.add_argument("--tournament", metavar="ID", help="only this round (id or prefix)")
    p.add_argument("--no-results", action="store_true", help="skip the results/health JSON")
    args = p.parse_args()

    api = Api(read_key())
    team_id, competition_id, team_name = team_info(api)
    tournaments = api.get_json(f"/competitions/{competition_id}/tournaments").get("items", [])
    health = {h["tournament_id"]: h for h in api.get_json(f"/teams/{team_id}/health").get("items", [])}
    tournaments.sort(key=lambda t: t["created_at"])
    if args.tournament:
        tournaments = [t for t in tournaments if t["id"].startswith(args.tournament)]
        if not tournaments:
            sys.exit(f"no round matches {args.tournament}")

    rounds = []
    for t in tournaments:
        if not t.get("completed_at"):
            print(f"-- {base_name(t)}: not completed yet, skipping")
            continue
        played = bool((health.get(t["id"]) or {}).get("submission_id"))
        results = api.get_json(f"/tournaments/{t['id']}/results")
        rank, row = our_row(results, team_id)
        rounds.append({"tournament": t, "health": health.get(t["id"]), "rank": rank, "row": row, "played": played})
        if args.list:
            continue
        if not played and not args.all:
            print(f"-- {base_name(t)}: our bot did not play (forfeit); use --all to download anyway")
            continue
        name = base_name(t)
        HANDS_DIR.mkdir(parents=True, exist_ok=True)
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        if not args.no_results:
            (RESULTS_DIR / f"{name}.json").write_text(json.dumps(
                {"tournament": t, "our_rank": rank, "our_result": row, "our_health": health.get(t["id"]),
                 "results": results}, indent=1), encoding="utf-8")
        suffix = f"-first-{args.tables}" if args.tables else ""
        dest = HANDS_DIR / f"{name}{suffix}.jsonl.gz"
        if dest.exists() and dest.stat().st_size > 0:
            print(f"-- {dest.name}: already here ({dest.stat().st_size / 1e6:.1f} MB)")
            continue
        query = f"?{urllib.parse.urlencode({'tables': args.tables})}" if args.tables else ""
        print(f"-> {dest.name}")
        api.download(f"/teams/{team_id}/tournaments/{t['id']}/hands{query}", dest)

    write_index(rounds, team_name)
    print()
    print((HANDS_DIR / "INDEX.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
