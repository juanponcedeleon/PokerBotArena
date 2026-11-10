# PokerBotArena

A research workbench and bot for the **No Limit 2026** poker-bot competition, variant **"Bay Area"**:
Crazy Pineapple with one exposed card, played as an 8-max no-limit sit-and-go.

Each player receives three hole cards. After the flop, everyone simultaneously discards one card and
turns one of the two kept cards face-up. Showdown is best five of board plus two kept cards, hold'em
style. The bot has **1 ms per decision**, a 100 ms time bank per table, and at most 16 KB of memory
between turns. Blinds rise every 20 hands; places pay 50/30/20 points with an ICM split at the
250-hand cap.

The repository holds everything used to build, test and tune the submission:

| Folder | Purpose |
|---|---|
| `bot/` | Current submission candidate (`agent.py` + data tables), uploadable as-is |
| `bots/` | Strategy pool: one directory per candidate bot with a `BOT.md` stating its hypothesis |
| `strategy/` | Strategy library in markdown: game model, exposed-card information, preflop, selection, postflop, opponent modeling, ICM, anti-patterns, experiment log, engineering constraints |
| `calc/` | Offline calculators (eval7 Monte Carlo, exact enumeration); results in `calc/results/` |
| `arena/` | Local tournament infrastructure: multi-core fast runner, strict SDK-timed runner, seeded league and A/B plans, leaderboard |
| `evolve/` | Evolutionary tuning of bot families, scored in the arena |
| `data/` | Downloaded tournament results and hand-history summaries |
| `starter-kit/` | Competition kit (rules, SDK, examples, sample histories). Treated as read-only |
| `submit.py`, `fetch_history.py` | Upload a bot zip and download hand histories via the competition API |

## Getting started

```sh
cd starter-kit
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt          # Windows; use .venv/bin/pip on Linux/WSL

# legality and timing check for the submission candidate
.venv/Scripts/poker-agent check ../bot/agent.py

# play 200 tables against the example bots
.venv/Scripts/poker-agent play ../bot examples/check_or_fold examples/min_raiser --tables 200
```

Arena commands run from the repository root:

```sh
starter-kit/.venv/Scripts/python.exe -m arena check bots/<name>
starter-kit/.venv/Scripts/python.exe -m arena ab bot bots/<name> --tables 300
starter-kit/.venv/Scripts/python.exe -m arena ladder        # -> arena/results/LEADERBOARD.md
```

Uploading needs a competition API key in the `NO_LIMIT_API_KEY` environment variable or in
`%APPDATA%\no-limit-2026\api-key`. Keys are never committed.

## How the work is organized

`CLAUDE.md` is the project guide for humans and AI agents working in parallel: claiming rules,
evidence tags (MATH / SIM / LOCAL / LIVE), the strategy scoreboard in `strategy/README.md`, and the
append-only experiment log in `strategy/08-experiments.md`. Arena results are the arbiter: a
strategy is promoted only with a logged, reproducible arena result.

## What is not in git

Virtual environments, raw hand histories (`data/hands/`, hundreds of MB), full arena run logs
(only `summary.json` and `leaderboard.md` per run are kept) and evolve candidate populations are
ignored. Re-create them with the commands above, `fetch_history.py`, or by rerunning the arena.
