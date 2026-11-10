"""arch-folder: sparring archetype — the tight folder seen in the practice round (19 teams with VPIP <= 15%,
14–19 pts/table, e.g. "Lemonade" 14% VPIP, 19.2 pts). Opens only premium 3-card classes for 2.5 BB, never
limps, never calls a raise except with a premium pair, shoves premium-or-better when <= 10 BB, otherwise
folds. Postflop: bets two pair+ for 60% pot, calls small bets with top pair, folds the rest.
Keeps the made-hand-best pair, exposes the lower kept card. Not a candidate.
"""

import eval7
import poker_agent_sdk
from poker_agent_sdk import Action, GameState

RANKS = "23456789TJQKA"
RVAL = {r: i for i, r in enumerate(RANKS)}
PAIR = 1 << 24
TWO_PAIR = 2 << 24


def _ev(cards):
    return eval7.evaluate([eval7.Card(c) for c in cards])


def premium(cards):
    """Pairs TT+ with any kicker, AA/KK/QQ with anything, AK+ suited combos count as premium."""
    rs = sorted((RVAL[c[0]] for c in cards), reverse=True)
    pair = max(rs[0] if rs[0] == rs[1] else -1, rs[1] if rs[1] == rs[2] else -1)
    if pair >= RVAL["T"]:
        return 2
    if pair >= RVAL["7"] or (rs[0] == 12 and rs[1] >= RVAL["K"]):
        return 1
    return 0


class Agent(poker_agent_sdk.Agent):
    def act(self, state: GameState, memory: bytes) -> tuple[Action, bytes]:
        try:
            return decide(state), b""
        except Exception:
            if state.phase != "betting":
                first = state.legal_actions[0]
                return Action(first.kind, first.min_amount), b""
            return (Action.check() if state.can("check") else Action.fold()), b""


def _raise(state, amount):
    r = state.can("raise")
    if not r:
        return Action.call() if state.can("call") else Action.check()
    return Action.raise_to(max(r.min_amount, min(r.max_amount, int(amount))))


def _check_or_fold(state):
    return Action.check() if state.can("check") else Action.fold()


def decide(state: GameState) -> Action:
    if state.phase == "select":
        cards = state.cards
        board = list(state.board)
        best = None
        for discard in range(3):
            keep = [i for i in range(3) if i != discard]
            v = _ev(board + [cards[keep[0]], cards[keep[1]]])
            if best is None or v > best[0]:
                best = (v, discard, keep)
        _, discard, keep = best
        a, b = keep
        reveal = a if RVAL[cards[a][0]] <= RVAL[cards[b][0]] else b
        return Action("select", cards=(discard, reveal))
    if state.phase != "betting":
        first = state.legal_actions[0]
        return Action(first.kind, first.min_amount)
    me = state.seats[state.seat]
    bb = state.blinds.big_blind
    if not state.board:
        p = premium(state.cards)
        raised = any(e.kind == "raise" for e in state.history)
        stack_bb = (me.stack + me.bet) / bb
        if stack_bb <= 10:
            if p >= 1:
                return _raise(state, 10**9)
            return _check_or_fold(state)
        if p == 2:
            if raised:
                return Action.call() if state.can("call") and state.to_call <= 0.25 * (me.stack + me.bet) else _check_or_fold(state)
            return _raise(state, 2.5 * bb + me.bet)
        if p == 1 and not raised:
            return _raise(state, 2.5 * bb + me.bet)
        return _check_or_fold(state)
    v = _ev(list(state.board) + list(state.cards))
    pot = max(state.pot, 1)
    if v >= TWO_PAIR:
        if state.to_call == 0:
            return _raise(state, 0.6 * pot + me.bet)
        return Action.call() if state.can("call") else Action.check()
    if v >= PAIR and state.to_call <= 0.4 * pot:
        return Action.call() if state.to_call else Action.check()
    return _check_or_fold(state)
