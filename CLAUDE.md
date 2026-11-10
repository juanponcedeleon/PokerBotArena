# PokerBot — project guide for humans and AI agents

We are building a bot for the **No Limit 2026** poker bot competition. Variant: **"Bay Area"**
(Crazy Pineapple with one exposed card). Read `starter-kit/RULES.md` and `starter-kit/AGENTS.md`
before touching bot code; this file explains how the *project* is organized and how several
agents work on it at once without stepping on each other.

## The game in one paragraph

8-max no-limit sit-and-go. 2,000 chips each, blinds rise every 20 hands
(10/20 → 2000/4000), table ends at one survivor or 250 hands, places pay 50/30/20 points
(ICM split at the hand cap). Each player gets **3 hole cards**. After the flop, before flop
betting, everyone *simultaneously* discards one card and **exposes one of the two kept cards
face-up**. Showdown is best 5 of (board + 2 kept cards), hold'em style (use 0, 1 or 2 hole
cards). All showdown hands are revealed automatically. The bot has **1 ms per decision**
(100 ms time bank per table) and only `memory` bytes (≤16 KB practical) between turns.

## Repository layout

```
PokerBot/
├── CLAUDE.md                 ← this file (project conventions; keep it current)
├── starter-kit/              ← competition kit. Treat sdk/ and RULES.md as READ-ONLY.
│   ├── RULES.md              ← variant rules + bot interface (authoritative)
│   ├── README.md / AGENTS.md ← platform limits, CLI commands, submission
│   ├── agent.py              ← template bot (we do NOT edit this one)
│   ├── examples/             ← check_or_fold, min_raiser (sparring partners)
│   ├── sdk/                  ← engine + protocol + SDK (local simulator)
│   ├── hand-history/         ← sample histories, reader, CASES.md edge cases
│   └── .venv/                ← Python 3.12 venv; eval7 is installed here
├── strategy/                 ← STRATEGY LIBRARY (markdown). What works, what doesn't, why.
│   ├── README.md             ← index + ranked scoreboard of strategies
│   ├── 00-game-model.md      ← rules distilled into structural facts and constraints
│   ├── 01-exposed-card-information.md ← capping logic, hidden-card counting, exposure as range
│   ├── 02-preflop.md         ← 3-card hand classes, equities, opening/3-bet/shove ranges
│   ├── 03-selection.md       ← keep/discard + which card to expose
│   ├── 04-postflop.md        ← betting with public information, bluff-catch math, sizing
│   ├── 05-opponent-modeling.md ← exploits, memory budget, what to track per seat
│   ├── 06-tournament-icm.md  ← blind pressure timeline, ICM, push/fold, hand-cap play
│   ├── 07-anti-patterns.md   ← things that lose (with evidence)
│   ├── 08-experiments.md     ← append-only experiment log (every sim run, every A/B)
│   ├── 09-engineering-constraints.md ← 1 ms budget, precompute, memory format
│   └── _template.md          ← copy this for a new strategy entry
├── calc/                     ← offline calculators (NOT shipped). Python, run with the venv.
│   ├── common.py             ← card helpers shared by calculators
│   ├── <topic>.py            ← one script per question; prints results, writes results/*.csv|.md
│   └── results/              ← outputs referenced from strategy/*.md
├── arena/                    ← local tournament infrastructure (NOT shipped). See arena/__init__.py.
│   ├── fast.py               ← in-process runner, all cores, thousands of tables/min (slightly optimistic timing)
│   ├── strict.py             ← SDK BotPool runner, exact platform timing (Linux/WSL only)
│   ├── plan.py               ← league / ab seating plans, seeded and reproducible
│   ├── bots.py, outcome.py   ← bot discovery, per-table results
│   └── usage: starter-kit/.venv/Scripts/python.exe -m arena league --all --tables 400
├── bots/                     ← STRATEGY POOL: one directory per candidate bot (see bots/README.md)
│   └── <strategy-name>/      ← agent.py (uploadable as-is) + BOT.md (hypothesis, strategy entries it implements) + data/
├── evolve/                   ← evolutionary tuning of bots/ families, scored in the arena (NOT shipped). See evolve/README.md.
└── bot/                      ← the current submission candidate (agent.py, data/, tests/)
```

If a folder above does not exist yet, the first agent that needs it creates it with exactly
that name. `bots/README.md` is authoritative for the pool conventions; `arena/__init__.py` for the runners.

## Workflow (phases run in parallel across agents)

1. **Research:** compute and simulate offline (`calc/`), write findings into `strategy/`. Every
   claim gets an evidence tag (see below).
2. **Build:** each strategy idea becomes a bot directory in `bots/<name>/` with a `BOT.md` naming the
   `strategy/` entries it implements. `bot/` holds the current best submission candidate.
3. **Iterate:** run `arena` leagues / A-B plans, log each run in `strategy/08-experiments.md`,
   promote/demote strategies on the scoreboard in `strategy/README.md`, copy the winner to `bot/`.

## How to run things

```sh
# from PokerBot/starter-kit (Windows Git Bash / PowerShell)
.venv/Scripts/python.exe  calc_script.py         # offline calculators (eval7, numpy available)
.venv/Scripts/poker-agent check bot/agent.py      # legality + timing check (once bot exists)
.venv/Scripts/poker-agent play ../bot examples/check_or_fold examples/min_raiser --tables 200

# ARENA (from PokerBot/): leagues, paired A/B, published leaderboard — read arena/README.md
starter-kit/.venv/Scripts/python.exe -m arena check bots/<name>        # legal + fast enough?
starter-kit/.venv/Scripts/python.exe -m arena ab bot bots/<name> --tables 300 --agent <you>
starter-kit/.venv/Scripts/python.exe -m arena ladder                    # -> arena/results/LEADERBOARD.md
```

`eval7.evaluate(cards)` ranks best-5 of any card list; higher is better. `eval7.handtype(v)`
names the category. Its range/equity helpers assume 2 hole cards — do not use them for 3.

Offline scripts write large intermediate files to your scratchpad, not the repo; commit
only compact results (`calc/results/*.csv`, small `.md` tables).

## Strategy library conventions

Every strategy entry (a section in one of the `strategy/0X-*.md` files) has this header:

```
### <Strategy name>
Status: PROVEN | PROMISING | UNTESTED | REJECTED
Evidence: MATH (exact) | SIM (offline Monte Carlo) | LOCAL (poker-agent play) | LIVE (tournament)
Owner: <agent/person>   Last updated: YYYY-MM-DD
```

- **PROVEN** needs SIM or stronger evidence with numbers quoted in the entry.
- **REJECTED** entries are moved to `07-anti-patterns.md`, never deleted — we want to remember
  why something lost.
- Numbers belong in tables, with the script that produced them named
  (`calc/<script>.py`) so anyone can rerun them.
- `strategy/README.md` holds the **scoreboard**: one row per strategy, ranked by expected
  impact on points-per-table. Update the row when you change a status.
- `strategy/08-experiments.md` is **append-only**. One entry per run: date, agent, question,
  setup (seed, tables, opponents), result, decision. Never rewrite another agent's entry.

## Multi-agent collaboration rules

- **Claim before you write.** Add a line under *Active work* below with your name, the file
  or section, and the date. Remove it when done. Two agents never edit the same section at once.
- **One topic, one file.** Put findings in the file whose name matches the topic. If a finding
  spans topics, write it once and link to it from the others (relative markdown links).
- **Do not edit `starter-kit/`** except to install packages into `.venv`. Rules, engine and
  SDK are the competition's; local changes would make our tests lie.
- **Do not edit another agent's calculator**; add a new script or a clearly named function.
- **Bot code:** never edit a bot that has arena results; copy `bots/<name>/` to a new name and
  change the copy (bots/README.md). `bot/agent.py` is owned by one agent at a time (claim it).
- **Arena results are the arbiter.** A strategy moves to PROVEN on the scoreboard only with an arena
  result (tables, seed, opponents) logged in `strategy/08-experiments.md`.
- **Hard limits to respect in any design:** 1 ms per decision, memory ≤16 KB and parsed
  defensively, no network/subprocess/background work, only libraries in
  `starter-kit/requirements.txt`, stateless `Agent` (nothing on `self`/globals between calls).
- Prefer Windows-safe paths and commands; the venv is `starter-kit/.venv` (Python 3.12.10).

## Current state (2026-11-06)

`strategy/` has all ten files populated; `calc/` has eight calculators with outputs in `calc/results/`.
`arena/` (fast runner, plans) and the `bots/` pool convention exist. `bot/` = `bots/fp-cfc2` (agent.py + data/preflop_classes.csv) since 2026-11-07 04:59Z (fp-v3 first-principles bot +
certain-math cap/floor overrides; upload 6a60c397 `fp-cfc2.zip`; +1.10 ±0.44 vs fp-v3, which was +1.26 vs fp-v2, which was
+2.2…+4.1 vs cap-floor-count-v6). `bots/v0-baseline` is the frozen v0. The practice round
(v0) scored 8.67 pts/table, rank 99/123 — see strategy/05 S5.3 for the real field and strategy/README.md for direction.
Start with `strategy/README.md` (scoreboard + open questions). Highest-value unclaimed work: push/fold
tables (02 S2.5 → 06 S6.2), the exposure-rule A/B (03 S3.2) in the arena, the hand-history analysis
pipeline (05 S5.3), and porting the proven keep rule (03 S3.1: made hand + draw bonus) into `bots/`.

## Active work

- Claude (evolve agent) — `evolve/` (new package), `bots/<head>-evoN/` (promoted genomes only), `strategy/08-experiments.md` (append via arena ab) — 2026-11-06

<!-- name | file or section | since -->
- (none; initial library complete. Claim a section here before editing it.)

- Claude (headmaster) — judge only (bot/ = bots/fp-cfc2, upload 6a60c397 active since 2026-11-07 04:59Z; claim bot/ before changing it): `strategy/08-experiments.md` Decision lines (append/fill), `strategy/README.md` scoreboard + Open questions, `strategy/07-anti-patterns.md`, `strategy/05-opponent-modeling.md` S5.3 population priors — 2026-11-06


## Open questions (pick one up, log the answer in strategy/)

- How good a selection heuristic can run inside 1 ms, and how far is it from the oracle?
- Push/fold thresholds for 3-card hands at 10 BB and below, 8-max down to heads-up.
- Does exposing a 2–5 and betting (the "Empty Bluffer" prize) ever pay in points, or only in the side prize?
- What per-seat stats fit in 16 KB and actually change decisions?
