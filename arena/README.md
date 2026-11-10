# Arena — adversarial testing for PokerBot strategies

The arena plays real No Limit 2026 ("Bay Area") sit-and-go tables between any bots you give it,
under the competition's rules (8-max, 2,000 chips, blinds up every 20 hands, 250-hand cap,
50/30/20 + ICM, 1 ms decisions, 100 ms bank, memory cut), and publishes who wins with error bars.

**Plug and play in three commands:**

```sh
# from PokerBot/  (Windows: starter-kit/.venv/Scripts/python.exe ; WSL/Linux: starter-kit/.venv-wsl/bin/python)
PY=starter-kit/.venv/Scripts/python.exe

$PY -m arena check  bots/my-bot                      # 1. legal submission? fast enough? (seconds)
$PY -m arena ab     bot bots/my-bot --tables 300     # 2. is it better than the current submission? (paired, ~1 min)
$PY -m arena ladder                                  # 3. whole pool, publishes arena/results/LEADERBOARD.md
```

Results are files you can read without running anything:

| where | what |
|---|---|
| `arena/results/dashboard.html` | **the dashboard**: open in a browser (`python -m arena dashboard`). Leader, points bar chart with CIs, trend across ladder runs, leaderboard, head-to-head matrix, A/B results, recent runs. Rebuilt after every run; the page reloads itself every 60 s |
| `arena/results/LEADERBOARD.md` | **the published standing** from the latest `ladder` run over every bot in `bots/` + examples |
| `arena/results/bots/<name>.md` | per-bot page: rank, points, failures, latency, head-to-head, history of ladder runs |
| `arena/results/<stamp>-<name>-<id>/leaderboard.md` | the report of one run (league or A/B) |
| `.../tables.jsonl`, `seats.csv`, `summary.json`, `run.json`, `plan.json` | raw per-table data, aggregates, exact command, seed, rules, bot fingerprints |
| `.../log.jsonl.gz` (with `--log`) | every hand with every card and every discard: input for `arena stats` |
| `.../history-<bot>.jsonl.gz` (with `--history BOT`) | participant-format replay for `replay FILE` (the kit's viewer) |
| `strategy/08-experiments.md` | one appended entry per run (date, agent, command, seed, result); fill in the **Decision** line |

## For agents writing bots

1. Create `bots/<your-name>/agent.py` (a complete submission: `class Agent(poker_agent_sdk.Agent)`,
   only `requirements.txt` libraries, data files next to it). Add `bots/<your-name>/BOT.md`
   (hypothesis, which `strategy/` entries it implements, what result would promote/demote them).
   Read `bots/README.md`.
2. `python -m arena check bots/<your-name>` — must say `verdict: OK`. Failures/timeouts/illegal
   actions cost you decisions on the platform (it checks or folds for you).
3. Compare against something, paired: `python -m arena ab <baseline> bots/<your-name> --tables 300
   --agent <your-name> --question "<one line>"`. The challenger takes the baseline's seats in the
   same dealt tables, so the paired difference needs ~10× fewer tables than two separate runs.
   Read the **A/B** block: `diff ± 95% CI` and `p`. Under 0.05 with the sign you want = promote.
4. Run `python -m arena ladder` (or let `python -m arena watch` do it whenever `bots/` changes) and
   read `arena/results/LEADERBOARD.md` and your page in `arena/results/bots/`.
5. Diagnose with `--log` + `python -m arena stats <run>/log.jsonl.gz`: VPIP, PFR, aggression,
   showdown rates, shoves, exposure and discard habits, busts by blind level, for every bot at the
   table (including opponents: this is the opponent-modeling input).
6. Write the Decision line into your entry in `strategy/08-experiments.md`, update the strategy's
   status on the scoreboard in `strategy/README.md`. Never edit a bot that has results; copy it.

Pass `--agent <your-name>` (or set `ARENA_AGENT`) so the experiment log says who ran what.

## The watcher (continuous testing)

A detached `python -m arena watch` process checks `bots/` every 30 s and, whenever any bot's files
change or a new bot appears, plays a 200-table ladder and republishes `LEADERBOARD.md` and the bot
pages. Its output is in `arena/results/watch.log`. It does not survive a reboot or logoff.

```powershell
# start (PowerShell, from anywhere)
$r="C:\Users\jmast\OneDrive\Desktop\Coding\PokerBot"; Start-Process "$r\starter-kit\.venv\Scripts\python.exe" -ArgumentList "-m","arena","watch","--interval","30","--tables","200","--agent","arena-watch" -WorkingDirectory $r -RedirectStandardError "$r\arena\results\watch.log" -WindowStyle Hidden
# is it running?  stop it?
Get-CimInstance Win32_Process | ? { $_.CommandLine -like "*arena watch*" } | select ProcessId
Get-CimInstance Win32_Process | ? { $_.CommandLine -like "*arena watch*" } | % { Stop-Process -Id $_.ProcessId }
```

## Commands

```
python -m arena list                              bots the arena can find (bots/, examples, bot/)
python -m arena ladder [--no-examples]            whole pool league; publishes LEADERBOARD.md + bot pages
python -m arena league BOT BOT... [--all] [--examples] [--publish]
python -m arena ab HERO CHALLENGER [--field BOT...] [--all]
python -m arena check BOT [--tables 4]            poker-agent pack/check + in-process latency probe
python -m arena stats FILE [--json] [--out X.md]  behaviour stats from log.jsonl.gz or a tournament download
python -m arena report RUN_DIR [--publish]        re-render a run from its tables.jsonl
python -m arena watch [--interval 30]             re-run the ladder whenever a bot in bots/ changes
```

Bot names: a directory (`bots/tight`, `../elsewhere/x`), a name in `bots/`, `check_or_fold` /
`min_raiser` (starter-kit examples), `bot` (the submission folder), or `label=path`.

Run options (ladder / league / ab / watch):

| option | default | meaning |
|---|---|---|
| `--tables N` | 200 | tables to play (A/B: pairs). Rounded up to whole iterations |
| `--seed S` | random | same seed + same bots = same cards, button, payouts. Always quote it in a log entry |
| `--mode fast\|strict` | fast | see below |
| `--workers W` | cores−1 / 8 | fast: worker processes. strict: tables in flight |
| `--decision-ms N` | 1 | decision limit. fast mode: `0` records latency without enforcing it |
| `--hand-cap N` | 250 | shorter tables for quick strategy screens (changes the game; say so) |
| `--players N` | 8 | seats per table (short-handed studies) |
| `--random-payouts` | off | each table draws its own split of 100 points (tests `state.config.payouts` handling) |
| `--log` | off | keep every hand (all cards, discards) in `log.jsonl.gz` |
| `--history BOT` | off | participant-format replay file from BOT's seat |
| `--name`, `--agent`, `--question` | | labels for the results directory and the experiment log |
| `--no-experiment-log` | | do not append to `strategy/08-experiments.md` (smoke tests) |

## Seating

With n bots and 8 seats, each iteration has lcm(n, 8)/8 tables and every bot has lcm(n, 8)/n
seats in it, shuffled by the engine's own `seat_iteration` (the competition's seating function).
No fillers, every seat scores. With fewer than 8 bots a table holds several seats of the same
bot (self-play), exactly as `poker-agent play` does when a folder is repeated. 8 distinct bots
= one table per iteration with one seat each, the competition's shape.

Head-to-head counts a table once per pair of bots and compares each bot's best seat.

## fast vs strict

| | fast (default) | strict |
|---|---|---|
| bots run | imported in-process, one Agent per bot per worker | separate processes via the SDK's BotPool, exactly like `poker-agent play` and the platform |
| throughput | ~10 tables/s on 8 workers (hundreds of hands each); thousands of tables in minutes | ~1–2 tables/s; the SDK keeps one event loop per process |
| timing | per-decision `perf_counter`, 1 ms + 2 ms allowance, 100 ms bank, timeouts play passive and keep old memory | measured by the host across the pipe, including JSON encoding of the state |
| what it misses | pipe + JSON cost (~0.1–0.4 ms per decision), so it is optimistic; all cores busy → jitter | nothing; it is the real thing |
| platform | Windows, WSL, Linux | Linux/WSL only; on Windows `--mode strict` re-launches itself in WSL (`starter-kit/.venv-wsl`) |

Rule of thumb: iterate on strategy in fast mode; before promoting a bot or uploading it, run
`--mode strict` once and require zero timeouts. A bot whose in-process p99 is above ~0.6 ms will
time out on the platform.

Strict-mode timing details (measured here, WSL on a 16-core laptop, 2026-11-06):

- Each strict shard runs **one table per event loop** (`--concurrency 1`). The kit's own
  `poker-agent play` runs 8 tables per loop, and its deadline clock then includes the engine's
  work for the other seven tables: trivial bots measure p50 ≈ 1.4 ms and real bots collect
  spurious timeouts. With one table per loop the same bots measure p50 ≈ 0.55 ms, which is the
  pipe + JSON round trip; a bot's own work adds to that.
- Throughput comes from `--workers` shard processes (default cores/4, max 4), ~1 table/s each.
- Even so, the tail on a laptop is noisy (p99 10–15 ms, occasional 50–300 ms stalls hit even
  `check_or_fold`), so a timeout or two per thousand decisions is machine noise, not the bot.
  The number that matters is the **difference** between bots in the same run, and the final
  word is the team's build machine (see starter-kit/AGENTS.md), which mirrors the platform.

## Reading the numbers

- **avg pts ± 95%**: points per table with a 95% confidence interval. Two bots whose intervals
  overlap are not separated yet; run more tables or use `ab`.
- **A/B diff**: challenger minus hero on the same tables; `p` from a paired t-test; the
  `challenger better / tied / worse` counts show consistency. The report also says how many pairs
  would resolve a 1-point difference at the observed variance.
- **fail/decision, timeouts, errors, illegal**: anything above 0 is a bug to fix before reading
  strategy results (a failed decision checks or folds).
- **p50 / p99 / max ms**: decision latency as measured by the runner. **mem B**: largest memory
  blob returned (keep under 16,384).
- **survived**: share of seats still in at the 250-hand cap (ICM split).

## Reproducibility

`run.json` records the command, seed, rules, and a fingerprint of every bot directory. Same
seed + same bot code = same deals; deterministic bots then reproduce the result exactly. `report
RUN_DIR` re-renders any old run.

## Limits and honesty

- Fast mode loads every bot into the same worker process. Bots with same-named helper modules
  are kept apart at import time; a bot that imports modules lazily inside `act` could still
  collide. Strict mode has no such caveat.
- Global state between calls is against the rules; both modes reuse one Agent per bot across
  tables, so a bot that cheats this way sees mixed-up state here too (as it would on the platform).
- The `--random-payouts` ranges are a guess; the organizers have not published theirs.
- Opponents here are our own bots and the two kit examples. The real field is unknown until the
  first round's hand history download, which `arena stats` reads directly.

## Layout

```
arena/
├── __main__.py        CLI
├── bots.py            find bots (bots/, starter-kit/examples, bot/), fingerprints
├── plan.py            league / ab seating plans (TableSpec), seeded
├── outcome.py         table rules + per-table result records
├── fast.py            in-process runner (multiprocessing)
├── strict.py          SDK BotPool runner (asyncio, Linux)
├── stats.py           CI, paired t-test, head-to-head, aggregation
├── report.py          run directories, leaderboard rendering, publishing, experiment log
├── history_stats.py   behaviour statistics from hand logs / tournament downloads
└── results/           published output (see the table at the top)
```
