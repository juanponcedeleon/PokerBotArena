#!/usr/bin/env python3
"""Upload a bot to the No Limit 2026 tournament from the command line.

Standard library only, so it runs from any Python (the kit venv, the build box, WSL).

    python submit.py                       # runs `poker-agent check`, uploads ./agent.py, waits for the verdict
    python submit.py starter-kit/agent.py  # or any other agent.py
    python submit.py my_bot.zip            # upload a zip made with `poker-agent pack my_bot my_bot.zip`
    python submit.py --no-check            # skip the local check
    python submit.py --no-wait             # return right after the upload is accepted
    python submit.py --list                # show the team's uploads and which one is active
    python submit.py --activate <id>       # make an earlier upload the active bot

The API key is read from NO_LIMIT_API_KEY, else %APPDATA%\\no-limit-2026\\api-key (Windows) or
~/.config/no-limit-2026/api-key. The setup skill saves it there.

An upload that passes its test match becomes the active bot automatically (unless the
competition is frozen). The team can upload once every 30 seconds.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SITE = "https://pokerbot.sequoiacap.com/tournament"
API = SITE + "/api"
TERMINAL = {"ready", "rejected", "cancelled", "canceled"}


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
    sys.exit(
        "No API key. Set NO_LIMIT_API_KEY or save one from Settings -> API keys to "
        + " or ".join(str(c) for c in candidates)
    )


class Api:
    def __init__(self, key: str) -> None:
        self.key = key

    def call(self, method: str, path: str, body: bytes | None = None, json_body=None, raw=False):
        url = API + path
        headers = {"Authorization": f"Bearer {self.key}", "Accept": "application/json"}
        data = None
        if json_body is not None:
            data = json.dumps(json_body).encode()
            headers["Content-Type"] = "application/json"
        elif body is not None:
            data = body
            headers["Content-Type"] = "application/octet-stream"
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                text = resp.read().decode("utf-8", "replace")
                return resp.status, (json.loads(text) if text and not raw else text)
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", "replace")
            try:
                return e.code, json.loads(text)
            except ValueError:
                return e.code, text


def team_id(api: Api) -> str:
    status, auth = api.call("GET", "/auth/api-key")
    if status == 401:
        sys.exit("The API key is wrong or expired (401). Make a new one at Settings -> API keys.")
    if status != 200:
        sys.exit(f"auth check failed: HTTP {status} {auth}")
    teams = auth.get("teams") or []
    if not teams:
        sys.exit("This account is not on a team yet.")
    if len(teams) > 1:
        names = ", ".join(f"{t['team_name']} ({t['competition_name']}): {t['team_id']}" for t in teams)
        chosen = os.environ.get("NO_LIMIT_TEAM_ID")
        if not chosen:
            sys.exit(f"Several teams; set NO_LIMIT_TEAM_ID to one of: {names}")
        return chosen
    return teams[0]["team_id"]


def local_check(target: Path) -> None:
    exe = shutil.which("poker-agent")
    if exe is None:
        here = Path(__file__).resolve().parent
        roots = (here / "starter-kit", here, Path.cwd())
        for cand in [r / v / b for r in roots for v, b in (
                (".venv", "Scripts/poker-agent.exe"), (".venv", "bin/poker-agent"), (".venv-wsl", "bin/poker-agent"))]:
            if cand.exists():
                exe = str(cand)
                break
    if exe is None:
        print("warning: poker-agent not found, skipping local check", file=sys.stderr)
        return
    print(f"-> {Path(exe).name} check {target.name}")
    result = subprocess.run([exe, "check", str(target)], capture_output=True, text=True)
    if result.returncode != 0:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        sys.exit("local check failed; nothing uploaded")
    print("   check passed")


def summarize(sub: dict) -> str:
    bits = [f"id={sub.get('id')}", f"status={sub.get('status')}"]
    for k in ("filename", "size_bytes", "created_at", "check_position", "rejection_reason"):
        if sub.get(k) is not None:
            bits.append(f"{k}={sub[k]}")
    if sub.get("check_log"):
        bits.append("check_log=" + str(sub["check_log"]).strip().splitlines()[-1][:120])
    return "  ".join(bits)


def cmd_list(api: Api, team: str) -> None:
    _, info = api.call("GET", f"/teams/{team}")
    active = info.get("active_submission_id")
    _, subs = api.call("GET", f"/teams/{team}/submissions")
    items = subs.get("items", []) if isinstance(subs, dict) else subs
    print(f"team: {info.get('name')}   active bot: {active or 'none'}")
    if not items:
        print("no uploads yet")
    for s in items:
        mark = "*" if s.get("id") == active else " "
        print(f"{mark} {summarize(s)}")


def cmd_activate(api: Api, team: str, sub_id: str) -> None:
    status, info = api.call("PATCH", f"/teams/{team}", json_body={"active_submission_id": sub_id})
    if status != 200:
        sys.exit(f"activate failed: HTTP {status} {info}")
    print(f"active bot is now {info.get('active_submission_id')}")


def cmd_upload(api: Api, team: str, target: Path, wait: bool, timeout_s: int) -> int:
    data = target.read_bytes()
    print(f"-> uploading {target.name} ({len(data):,} bytes)")
    q = urllib.parse.urlencode({"filename": target.name})
    status, sub = api.call("POST", f"/teams/{team}/submissions?{q}", body=data)
    if status == 429:
        sys.exit(f"rate limited (one upload per 30 s): {sub}")
    if status not in (200, 201, 202):
        sys.exit(f"upload refused: HTTP {status} {json.dumps(sub, indent=2) if isinstance(sub, dict) else sub}")
    print("   accepted:", summarize(sub))
    if not wait:
        return 0
    sub_id = sub.get("id")
    deadline = time.time() + timeout_s
    last = sub.get("status")
    print("-> waiting for the test match", end="", flush=True)
    while time.time() < deadline:
        time.sleep(5)
        _, subs = api.call("GET", f"/teams/{team}/submissions")
        items = subs.get("items", []) if isinstance(subs, dict) else subs
        cur = next((s for s in items if s.get("id") == sub_id), None)
        if cur is None:
            print(".", end="", flush=True)
            continue
        if cur.get("status") != last:
            last = cur.get("status")
            print(f" [{last}]", end="", flush=True)
        else:
            print(".", end="", flush=True)
        if last in TERMINAL:
            print()
            print(json.dumps(cur, indent=2))
            _, info = api.call("GET", f"/teams/{team}")
            active = info.get("active_submission_id")
            if last == "ready":
                print("READY." + (" It is now the active bot." if active == sub_id else
                                  f" Active bot is {active}; run --activate {sub_id} to switch."))
                return 0
            print(f"{last.upper()}. See the validation log on the team page: {SITE}/teams/{team}")
            return 1
    print()
    print(f"still {last} after {timeout_s}s; check {SITE}/teams/{team}")
    return 2


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", nargs="?", default="agent.py", help="agent.py or a zip from `poker-agent pack`")
    p.add_argument("--no-check", action="store_true", help="skip `poker-agent check` before uploading")
    p.add_argument("--no-wait", action="store_true", help="do not wait for the test match verdict")
    p.add_argument("--timeout", type=int, default=600, help="seconds to wait for the verdict (default 600)")
    p.add_argument("--list", action="store_true", help="list uploads and the active bot")
    p.add_argument("--activate", metavar="ID", help="make this upload the active bot")
    args = p.parse_args()

    api = Api(read_key())
    team = team_id(api)
    if args.list:
        cmd_list(api, team)
        return 0
    if args.activate:
        cmd_activate(api, team, args.activate)
        return 0
    target = Path(args.file)
    if not target.is_file():
        sys.exit(f"no such file: {target}")
    if not args.no_check:
        local_check(target)
    return cmd_upload(api, team, target, wait=not args.no_wait, timeout_s=args.timeout)


if __name__ == "__main__":
    sys.exit(main())
