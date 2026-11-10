"""cap-floor-count - PokerBot v0 with the postflop module replaced by "Cap, floor and count".

Strategy entries implemented (see BOT.md):
  strategy/01-exposed-card-information.md S1.1 (cap), S1.2 (floor), S1.3 (river counting), S1.5 (dead cards)
  strategy/04-postflop.md S4.1 (beat the cap -> value), S4.2 (never call below the floor),
                          S4.3 (bluff-catch by counting), S4.4 (one-pair discipline)

Preflop and selection are byte-for-byte the v0 rules from bot/agent.py (tight-aggressive by
3-card class, push/fold short; keep the made-hand-best pair, expose the weaker card), so an A/B
against bot/ isolates the postflop change.

Postflop pipeline (every decision, < 300 us):
  1. unseen = deck - board - my 3 cards - every exposed card at the table (folded seats included).
  2. ours = evaluate(board + my 2 kept cards).
  3. For every live opponent enumerate the hidden card h over `unseen`:
       cap = max rank, floor = min rank, lose = #(beats us) + 0.5 #(ties)  (45 evaluations, ~25 us)
  4. p_best = product over opponents of (1 - lose/|unseen|)   (uniform prior on the hidden card)
     river: exact.  flop/turn: shrink p_best by a category/street factor and add our own outs.
  5. beat every cap -> bet/raise for value; equity below pot odds -> fold; otherwise call/check;
     one pair is bet for value only when the count says so (opponents capped below it).
"""

import eval7
import poker_agent_sdk
from poker_agent_sdk import Action, GameState

RANKS = "23456789TJQKA"
RVAL = {r: i for i, r in enumerate(RANKS)}  # 0..12
SUITS = "cdhs"
DECK = [r + s for r in RANKS for s in SUITS]
CARD = {c: eval7.Card(c) for c in DECK}  # built once at import; act never constructs Cards

# Hand-type thresholds in eval7's value space (approximate category floors).
PAIR = 1 << 24
TWO_PAIR = 2 << 24
TRIPS = 3 << 24
STRAIGHT = 4 << 24

# --- tunables of the postflop policy (priors until the arena says otherwise) ------------------
# How much a "currently best" probability overstates equity with cards to come, by our category.
SHRINK_FLOP = {0: 0.60, 1: 0.72, 2: 0.80, 3: 0.88, 4: 0.92}  # key = min(category, 4)
SHRINK_TURN = {0: 0.75, 1: 0.85, 2: 0.90, 3: 0.95, 4: 0.97}
OUTS_MULT_FLOP = 1.9       # two cards to come
OUTS_MULT_TURN = 1.0
VALUE_BET_EQ = 0.62        # bet when nobody has bet and our equity estimate is above this
RAISE_EQ = 0.78            # raise a bet when above this
NUTS_BET_POT = 0.80        # bet size (fraction of pot) when we beat every cap
VALUE_BET_POT = 0.60       # bet size otherwise
CALL_MARGIN = 0.02         # call needs eq >= pot odds + margin
UNKNOWN_LOSE = {0: 0.70, 1: 0.45, 2: 0.25, 3: 0.12, 4: 0.06}  # opponent with no exposed card


def _ev(cards):
    return eval7.evaluate([CARD[c] for c in cards])


def _cat(v):
    return v >> 24


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


# ----------------------------------------------------------------------------------------------
# Postflop: cap, floor and count
# ----------------------------------------------------------------------------------------------

def read_table(state: GameState):
    """Dead-card accounting (S1.5) and the list of live opponents with their exposed cards."""
    board = list(state.board)
    hole = list(state.cards)
    dead = set(board) | set(hole)
    for c in state.variant.get("discarded", ()) or ():
        dead.add(c)
    opps = []
    for s in state.seats:
        shown = tuple(s.shown_cards or ())
        for c in shown:
            dead.add(c)
        if s.seat == state.seat or s.status not in ("active", "all_in"):
            continue
        opps.append(shown)
    unseen = [c for c in DECK if c not in dead]
    return board, hole, opps, unseen


def count_opponent(shown, bcards, ucards, ours):
    """Enumerate the hidden card. Returns (cap, floor, lose_fraction).
    `bcards`/`ucards` are eval7.Card lists built once per decision; the hand list is preallocated."""
    evaluate = eval7.evaluate
    if len(shown) >= 2:  # both kept cards public (should not happen mid-hand): exact
        v = evaluate([CARD[shown[0]], CARD[shown[1]]] + bcards)
        return v, v, (1.0 if v > ours else 0.5 if v == ours else 0.0)
    hand = [CARD[shown[0]], None] + bcards
    cap = 0
    floor = 1 << 40
    beat = 0
    ties = 0
    for h in ucards:
        hand[1] = h
        v = evaluate(hand)
        if v > cap:
            cap = v
        if v < floor:
            floor = v
        if v > ours:
            beat += 1
        elif v == ours:
            ties += 1
    return cap, floor, (beat + 0.5 * ties) / len(ucards)


def our_outs(bcards, hcards, ucards, ours):
    """Fraction of next cards that lift our category to two pair or better (one evaluation each)."""
    if len(bcards) >= 5:
        return 0.0
    evaluate = eval7.evaluate
    hand = bcards + hcards + [None]
    cat0 = ours >> 24
    n = 0
    for c in ucards:
        hand[-1] = c
        v = evaluate(hand)
        if (v >> 24) > cat0 and v >= TWO_PAIR:
            n += 1
    return n / len(ucards) if ucards else 0.0


def postflop(state: GameState) -> Action:
    board, hole, opps, unseen = read_table(state)
    bcards = [CARD[c] for c in board]
    hcards = [CARD[c] for c in hole]
    ucards = [CARD[c] for c in unseen]
    ours = eval7.evaluate(bcards + hcards)
    cat = min(_cat(ours), 4)
    street = len(board)
    pot = max(state.pot, 1)
    to_call = state.to_call
    me = state.seats[state.seat]
    raised = any(e.kind == "raise" for e in state.history)
    hole_ranks = [RVAL[c[0]] for c in hole]

    # --- cap / floor / count against every live opponent ---------------------------------------
    p_best = 1.0
    beat_all_caps = bool(opps) and bool(unseen)
    below_a_floor = False
    for shown in opps:
        if not shown or not unseen:
            lose = UNKNOWN_LOSE[cat]
            beat_all_caps = False
        else:
            cap, floor, lose = count_opponent(shown, bcards, ucards, ours)
            if ours <= cap:
                beat_all_caps = False
            if floor > ours:
                below_a_floor = True
        p_best *= 1.0 - lose

    # --- equity estimate -----------------------------------------------------------------------
    if street >= 5:
        eq = p_best
    else:
        shrink = (SHRINK_FLOP if street == 3 else SHRINK_TURN)[cat]
        mult = OUTS_MULT_FLOP if street == 3 else OUTS_MULT_TURN
        outs = min(1.0, our_outs(bcards, hcards, ucards, ours) * mult) if p_best < 0.97 else 0.0
        eq = p_best * shrink + (1.0 - p_best) * outs

    # --- policy --------------------------------------------------------------------------------
    if beat_all_caps:  # S4.1: nobody can currently beat us; bet for maximum value, never slow-play
        if to_call == 0:
            return _raise(state, NUTS_BET_POT * pot + me.bet)
        return _raise(state, 2.5 * to_call + me.bet + 0.6 * pot)

    if to_call > 0:
        if below_a_floor and street >= 5:  # S4.2: their minimum hand beats us, nothing to come
            return Action.fold()
        need = to_call / (pot + to_call) + CALL_MARGIN  # pot already contains their bet
        if eq >= RAISE_EQ and not below_a_floor:
            return _raise(state, 2.5 * to_call + me.bet + 0.5 * pot)
        if eq >= need:
            return _call_or_check(state)
        return _check_or_fold(state)

    # Nobody has bet to us.
    if below_a_floor:
        return Action.check()
    if eq >= VALUE_BET_EQ and (ours >= TWO_PAIR or p_best >= 0.75):  # S4.4: one pair needs the count
        return _raise(state, VALUE_BET_POT * pot + me.bet)
    # Occasional continuation bet when we were the preflop aggressor (unchanged from v0).
    if raised and street == 3 and max(hole_ranks) >= RVAL["J"] and ours < PAIR:
        return _raise(state, 0.5 * pot + me.bet)
    return Action.check()
