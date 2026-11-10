# fp-v2

`bots/fp-v1` with GC tuning only (`gc.freeze()` after the import-time tables, threshold 50000/50/50, as cap-floor-count-v6). Decisions are byte-identical to fp-v1; purpose: remove the ~19 ms garbage-collection tail seen in `arena check fp-v1`. See `bots/fp-v1/BOT.md` for the design and results.
