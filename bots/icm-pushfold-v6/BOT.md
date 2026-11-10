# icm-pushfold-v6 — v5 decisions, numba ICM

**Status: superseded by v7 (parameters).** Parent: `bots/icm-pushfold-v5`. Living summary: `bots/icm-pushfold-v7/BOT.md`.

Identical decisions to v5. ICM is a numba-compiled O(n³) Malmuth-Harville loop compiled at import (2.6 µs per
call vs 45–60 µs; pure-Python / numpy fallback if numba is unavailable), memory packed with one struct call.
`arena check`: p50 0.045 ms, p99 0.23 ms, max 0.41 ms, 0 failures. Not A/B'd separately (same decisions as v5).
