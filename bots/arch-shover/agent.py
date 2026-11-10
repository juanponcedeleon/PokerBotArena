"""arch-shover: sparring archetype — the pure shover seen in the practice round (4 teams, VPIP >= 90%,
shove/100 hands > 50, 0.9–2.0 pts/table). Preflop: goes all-in with every hand that is not pure trash,
calls any all-in. Postflop (rare): bets all-in with any pair, calls everything otherwise. Not a candidate.
"""

import poker_agent_sdk
from poker_agent_sdk import Action, GameState

RANKS = "23456789TJQKA"


class Agent(poker_agent_sdk.Agent):
    def act(self, state: GameState, memory: bytes) -> tuple[Action, bytes]:
        try:
            return decide(state), b""
        except Exception:
            if state.phase != "betting":
                first = state.legal_actions[0]
                return Action(first.kind, first.min_amount), b""
            return (Action.call() if state.can("call") else Action.check() if state.can("check") else Action.fold()), b""


def decide(state: GameState) -> Action:
    if state.phase != "betting":
        first = state.legal_actions[0]
        return Action(first.kind, first.min_amount)
    ranks = sorted((RANKS.index(c[0]) for c in state.cards), reverse=True)
    trash = not state.board and ranks[0] <= 6 and ranks[0] != ranks[1] and ranks[1] != ranks[2]
    r = state.can("raise")
    if r and not trash:
        return Action.raise_to(r.max_amount)
    if state.can("call"):
        return Action.call()
    return Action.check() if state.can("check") else Action.fold()
