"""v0-nowar - v0 preflop with the 3-bet war capped

Preflop change (the only change vs the parent): facing a 3-bet or more, class-3 hands no longer
re-raise 3x without limit (two v0 copies escalate to all-in at 100 BB on hand 1; 59% of seats bust in
blind level 1 in the pool, see strategy/08-experiments.md 2026-11-06 cfc-v1-ab-pool). Now: QQ+ pairs shove,
TT-JJ call up to 30% of stack, 77-99 call up to 12%, everything else folds. Class-2 hands only call a
single open. Push/fold (<=12 BB) untouched.

Parent docstring follows.
PokerBot v0 - quick heuristic bot for the Bay Area variant (Crazy Pineapple, one exposed card).

Preflop: tight-aggressive by 3-card hand class, push/fold when short.
Select: keep the two cards making the best 5-card hand with the flop, expose the weaker one.
Postflop: bet/raise strong made hands, call with medium hands if price is right, else check/fold.
"""

import eval7
import poker_agent_sdk
from poker_agent_sdk import Action, GameState

RANKS = "23456789TJQKA"
RVAL = {r: i for i, r in enumerate(RANKS)}  # 0..12

# Hand-type thresholds in eval7's value space (approximate category floors).
PAIR = 1 << 24
TWO_PAIR = 2 << 24
TRIPS = 3 << 24
STRAIGHT = 4 << 24


def _ev(cards):
    return eval7.evaluate([eval7.Card(c) for c in cards])


def preflop_class(cards):
    """0 = trash, 1 = marginal, 2 = good, 3 = premium."""
    rs = sorted((RVAL[c[0]] for c in cards), reverse=True)
    suits = [c[1] for c in cards]
    pair = max(rs[0] if rs[0] == rs[1] else -1, rs[1] if rs[1] == rs[2] else -1)
    suited = len(set(suits)) < 3
    high = sum(1 for r in rs if r >= RVAL["T"])
    ace = rs[0] == 12
    connected = (rs[0] - rs[1] <= 2) or (rs[1] - rs[2] <= 2)
    if pair >= RVAL["T"] or (pair >= RVAL["7"] and high >= 1 and ace):
        return 3
    if high >= 2 and ace:
        return 3
    if pair >= RVAL["6"] or high >= 2 or (ace and suited):
        return 2
    if pair >= 0 or high >= 1 or (suited and connected):
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
    amount = max(r.min_amount, min(r.max_amount, int(amount)))
    return Action.raise_to(amount)


def _call_or_check(state):
    if state.can("call"):
        return Action.call()
    if state.can("check"):
        return Action.check()
    return Action.fold()


def _check_or_fold(state):
    return Action.check() if state.can("check") else Action.fold()


def decide(state: GameState) -> Action:
    if state.phase == "select":
        return select(state)
    if state.phase != "betting":
        first = state.legal_actions[0]
        return Action(first.kind, first.min_amount)
    if not state.board:
        return preflop(state)
    return postflop(state)


def select(state: GameState) -> Action:
    cards = state.cards
    board = list(state.board)
    best = None
    for discard in range(3):
        keep = [i for i in range(3) if i != discard]
        v = _ev(board + [cards[keep[0]], cards[keep[1]]])
        if best is None or v > best[0]:
            best = (v, discard, keep)
    _, discard, keep = best
    # Expose the weaker card (lower rank), keep the stronger hidden.
    a, b = keep
    reveal = a if RVAL[cards[a][0]] <= RVAL[cards[b][0]] else b
    return Action("select", cards=(discard, reveal))


def preflop(state: GameState) -> Action:
    me = state.seats[state.seat]
    bb = state.blinds.big_blind
    stack_bb = (me.stack + me.bet) / bb if bb else 50
    cls = preflop_class(state.cards)
    to_call = state.to_call
    raised = any(e.kind == "raise" for e in state.history)

    if stack_bb <= 12:
        # Push/fold.
        if cls >= 2 or (cls == 1 and stack_bb <= 6 and not raised):
            return _raise(state, 10**9)
        if to_call == 0:
            return Action.check()
        return Action.fold()

    n_raises = sum(1 for e in state.history if e.kind == "raise")
    if cls == 3:
        if not raised:
            return _raise(state, 3 * bb)
        if n_raises == 1:  # facing a single open: 3-bet
            return _raise(state, max(3 * to_call, 3 * bb) + me.bet)
        # Facing a 3-bet or more: no unlimited escalation (the v0 war). Only big pairs keep raising.
        rs = sorted((RVAL[c[0]] for c in state.cards), reverse=True)
        pair = max(rs[0] if rs[0] == rs[1] else -1, rs[1] if rs[1] == rs[2] else -1)
        if pair >= RVAL["Q"]:
            return _raise(state, 10**9)
        if pair >= RVAL["T"] and to_call <= 0.3 * (me.stack + me.bet):
            return _call_or_check(state)
        if pair >= RVAL["7"] and to_call <= 0.12 * (me.stack + me.bet):
            return _call_or_check(state)
        return _check_or_fold(state)
    if cls == 2:
        if not raised:
            return _raise(state, 2.5 * bb)
        if to_call <= 6 * bb and n_raises == 1:
            return _call_or_check(state)
        return _check_or_fold(state)
    if cls == 1:
        if to_call <= bb and not raised:
            return _call_or_check(state)
        return _check_or_fold(state)
    return _check_or_fold(state)


def postflop(state: GameState) -> Action:
    board = list(state.board)
    hole = list(state.cards)
    v = _ev(board + hole)
    board_v = _ev(board) if len(board) >= 5 else 0
    pot = max(state.pot, 1)
    to_call = state.to_call
    me = state.seats[state.seat]
    raised = any(e.kind == "raise" for e in state.history)

    # Pair strength: is our pair using a hole card and top-pair-ish?
    board_ranks = [RVAL[c[0]] for c in board]
    hole_ranks = [RVAL[c[0]] for c in hole]
    top_board = max(board_ranks)
    has_top_pair = any(r in board_ranks and r >= top_board for r in hole_ranks) or hole_ranks[0] == hole_ranks[1] and hole_ranks[0] > top_board

    strong = v >= TWO_PAIR and v > board_v
    medium = (v >= PAIR and has_top_pair) or (v >= TWO_PAIR)
    weak_pair = v >= PAIR

    if strong:
        if to_call == 0:
            return _raise(state, 0.7 * pot + me.bet)
        if v >= TRIPS or to_call <= pot:
            return _raise(state, 2.5 * to_call + me.bet + 0.5 * pot)
        return _call_or_check(state)
    if medium:
        if to_call == 0:
            return _raise(state, 0.5 * pot + me.bet)
        if to_call <= 0.6 * pot:
            return _call_or_check(state)
        return _check_or_fold(state)
    if weak_pair:
        if to_call == 0:
            return Action.check()
        if to_call <= 0.3 * pot:
            return _call_or_check(state)
        return _check_or_fold(state)
    # Draws: flush draw or open-ender on flop/turn -> call small bets.
    if len(board) < 5:
        suits = [c[1] for c in board + hole]
        fd = any(suits.count(s) >= 4 for s in set(suits)) and hole[0][1] == hole[1][1]
        if fd and to_call <= 0.35 * pot:
            return _call_or_check(state)
    if to_call == 0:
        # Occasional continuation bet when we were the preflop aggressor.
        if raised and len(board) == 3 and max(hole_ranks) >= RVAL["J"]:
            return _raise(state, 0.5 * pot + me.bet)
        return Action.check()
    return _check_or_fold(state)
