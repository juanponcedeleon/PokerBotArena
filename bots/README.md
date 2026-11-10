# bots/ — the strategy pool

One directory per candidate strategy, each containing an `agent.py` that defines
`class Agent(poker_agent_sdk.Agent)` exactly as a submission would (plus any data files it
reads from its own folder). The arena treats every such directory as one entry in the pool.

```
bots/
├── README.md
├── <strategy-name>/
│   ├── agent.py        ← the bot (a real, uploadable submission)
│   ├── BOT.md          ← optional: hypothesis, parent strategy, what to watch for
│   └── data/           ← optional precomputed tables the bot reads
└── ...
```

Conventions

- Directory names are the bot's label everywhere (leaderboards, histories, experiment log).
  Use short kebab-case names: `tight-icm`, `expose-high`, `shove-15bb`.
- Never edit a bot that is on the leaderboard; copy it to a new name and change the copy, so
  every result stays reproducible.
- `BOT.md` should say which strategy entries in `strategy/*.md` the bot implements and what
  result would promote or demote them.
- The sparring partners `starter-kit/examples/check_or_fold` and `starter-kit/examples/min_raiser`
  are always available under the names `check_or_fold` and `min_raiser`.

Full arena guide: `arena/README.md`. Run the pool against itself:

```sh
# from PokerBot/
starter-kit/.venv/Scripts/python.exe -m arena league --all --tables 400
```
