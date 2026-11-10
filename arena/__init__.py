"""PokerBot arena: adversarial tournament infrastructure.

Runs local No Limit 2026 ("Bay Area") sit-and-go tournaments between any number of bot
directories, under the competition's conditions, and turns the outcomes into statistics a
strategy decision can rest on. Nothing here is shipped with the bot.

Two runners share one plan format and one report format:

* `arena.fast`   imports each bot in-process and drives the engine directly, one table per
                 task across all CPU cores. Thousands of tables per minute. Measures each
                 decision's latency and applies the 1 ms + time-bank rule, but without the
                 pipe/JSON overhead of the real platform, so it is slightly optimistic.
* `arena.strict` runs bots as separate processes through the SDK's own BotPool, exactly as
                 `poker-agent play` does (deadline measured from the host side, 2 shared
                 copies per bot, memory cut). Linux/WSL only. The authority on timing.

See arena/README.md.
"""

__all__ = ["bots", "plan", "fast", "strict", "stats", "report", "history_stats"]
