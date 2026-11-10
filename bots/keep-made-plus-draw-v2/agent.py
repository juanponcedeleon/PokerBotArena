"""PokerBot v0 - quick heuristic bot for the Bay Area variant (Crazy Pineapple, one exposed card).

Preflop: tight-aggressive by 3-card hand class, push/fold when short.
Select: keep the two cards making the best 5-card hand with the flop, plus draw/overcard bonuses
        whose weights were tuned offline and scale with the number of live opponents; expose the weaker one.
        Strategy entries: strategy/03-selection.md S3.1 (keep rule, tuned weights) + S3.3 (opponent count).
        v2 of the keep-rule family; everything else identical to bot/agent.py v0.
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


# Draw bonuses in eval7 value space (one pair = 1 << 24), tuned in calc/i_keep_weights.py
# (50,000 deals, hero vs N made-hand opponents, pot share) and scaled by the number of live
# opponents (strategy/03 S3.1 refinement 2 / S3.3): multiway, draws and overcards are worth more.
# Columns: 4-flush with both kept cards suited, 4-flush with one kept card (monotone board),
# open-ended straight draw, gutshot, per-overcard bonus (only when the subset has no pair).
M = 1_000_000
WEIGHTS = {
    1: (15 * M, 15 * M, 8 * M, 2 * M, 0),       # heads-up: 50.76% vs 50.47% (v1) vs 49.69% (made only)
    3: (20 * M, 15 * M, 8 * M, 4 * M, 0),       # 3 opponents: 26.24% vs 25.59% vs 24.62%
    6: (20 * M, 15 * M, 16 * M, 4 * M, 2 * M),  # 6 opponents: 15.67% vs 14.91% vs 14.03%
}


def weights_for(n_opp):
    if n_opp <= 2:
        return WEIGHTS[1]
    if n_opp <= 4:
        return WEIGHTS[3]
    return WEIGHTS[6]


def draw_bonus(five, w):
    """Bonus for the 5 cards (flop + 2 kept) under weight vector w."""
    w_fd, w_fd1, w_oesd, w_gut, w_over = w
    bonus = 0
    suits = [c[1] for c in five]
    for s in "cdhs":
        if suits.count(s) == 4:
            bonus += w_fd if (five[3][1] == s and five[4][1] == s) else w_fd1
            break
    ranks = set(RVAL[c[0]] for c in five)
    if 12 in ranks:
        ranks.add(-1)
    oesd = False
    for lo in range(0, 9):  # 2345 .. TJQK; A234 and JQKA are gutshots, not open-enders
        if lo in ranks and lo + 1 in ranks and lo + 2 in ranks and lo + 3 in ranks:
            oesd = True
            break
    if oesd:
        bonus += w_oesd
    elif w_gut:
        for lo in range(-1, 9):  # 5-rank windows A2345 .. TJQKA holding 4 of our ranks
            if sum(1 for r in range(lo, lo + 5) if r in ranks) >= 4:
                bonus += w_gut
                break
    if w_over:
        top = max(RVAL[c[0]] for c in five[:3])
        if RVAL[five[3][0]] != RVAL[five[4][0]] and all(RVAL[c[0]] not in (RVAL[b[0]] for b in five[:3]) for c in five[3:]):
            bonus += w_over * sum(1 for c in five[3:] if RVAL[c[0]] > top)
    return bonus


def select(state: GameState) -> Action:
    cards = state.cards
    board = list(state.board)
    n_opp = sum(1 for s in state.seats if s.seat != state.seat and s.status in ("active", "all_in"))
    w = weights_for(n_opp)
    best = None
    for discard in range(3):
        keep = [i for i in range(3) if i != discard]
        five = board + [cards[keep[0]], cards[keep[1]]]
        v = _ev(five) + draw_bonus(five, w)
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

    if cls == 3:
        if raised:
            return _raise(state, max(3 * to_call, 3 * bb) + me.bet)
        return _raise(state, 3 * bb)
    if cls == 2:
        if not raised:
            return _raise(state, 2.5 * bb)
        if to_call <= 6 * bb:
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
