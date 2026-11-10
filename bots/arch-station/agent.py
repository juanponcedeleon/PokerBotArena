"""arch-station: sparring archetype — the calling station. Never folds when it can call, never raises
(except it min-raises nothing). Postflop and preflop alike: call if there is a bet, otherwise check.
Keeps the made-hand-best pair and exposes the first kept card (fallback-like). Not a candidate.
"""

import eval7
import poker_agent_sdk
from poker_agent_sdk import Action, GameState


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
    if state.phase == "select":
        cards = state.cards
        board = [eval7.Card(c) for c in state.board]
        best = None
        for discard in range(3):
            keep = [i for i in range(3) if i != discard]
            v = eval7.evaluate(board + [eval7.Card(cards[keep[0]]), eval7.Card(cards[keep[1]])])
            if best is None or v > best[0]:
                best = (v, discard, keep[0])
        return Action("select", cards=(best[1], best[2]))
    if state.phase != "betting":
        first = state.legal_actions[0]
        return Action(first.kind, first.min_amount)
    if state.can("call"):
        return Action.call()
    return Action.check() if state.can("check") else Action.fold()
