"""fp-v4 — fp-v3 + heads-up / 3-handed ranges, bubble margin, and cap awareness from exposed cards.

Changes vs fp-v3 (everything else identical):
  * Heads-up: button opens the top 70% (shoves the top 70% when <= 10 BB), big blind defends the top 55% and
    3-bets the top 15%; all-in calls heads-up use no ICM margin (first vs second is pure chip equity).
  * 3-handed: open 12 points wider, shove 10 points wider, all-in call margin 0.03.
  * Bubble (4 live players): all-in call margin +0.06.
  * Cap awareness: an opponent whose exposed card does not pair an unpaired board and cannot make a flush or a
    straight is publicly capped at one pair (strategy/01 S1.1). Against only capped opponents, top pair bets and
    calls bigger, and heads-up air/weak hands take a stab on flop and turn.
  * Heads-up position bug fixed (big blind counted one player behind).

fp-v3 — fp-v2 + ICM-tight deep all-in calls (>= 25 BB, call >= 45% of stack: eq_vs1 >= pot odds + 0.16, top-8% class).
fp-v2 — fp-v1 + GC tuning.  fp-v1 — first-principles design, see bots/fp-v1/BOT.md.
"""

import csv
import gc
from pathlib import Path

import eval7
import poker_agent_sdk
from poker_agent_sdk import Action, GameState

RANKS = "23456789TJQKA"
RVAL = {r: i for i, r in enumerate(RANKS)}
PAIR = 1 << 24

_DATA = Path(__file__).resolve().parent / "data" / "preflop_classes.csv"
EQ = {}
with _DATA.open(encoding="utf-8") as _f:
    for _row in csv.DictReader(_f):
        EQ[_row["label"]] = (float(_row["eq_vs1"]), float(_row["eq_vs3"]), float(_row["eq_vs7"]))


def _combos(label):
    if label.endswith("sss"):
        return 4
    if "-" in label:
        return 12
    if label.endswith("r"):
        return 12 if label[0] == label[1] else 24
    if label.endswith("s"):
        return 12
    return 4


def _percentiles(index):
    items = sorted(EQ.items(), key=lambda kv: kv[1][index])
    total = sum(_combos(l) for l, _ in items)
    out, below = {}, 0
    i = 0
    while i < len(items):
        j = i
        while j < len(items) and items[j][1][index] == items[i][1][index]:
            j += 1
        tie = sum(_combos(items[k][0]) for k in range(i, j))
        p = (below + tie / 2) / total
        for k in range(i, j):
            out[items[k][0]] = p
        below += tie
        i = j
    return out


PCT1, PCT3, PCT7 = _percentiles(0), _percentiles(1), _percentiles(2)
gc.collect()
gc.freeze()
gc.set_threshold(50000, 50, 50)


def class_label(cards):
    cs = sorted(cards, key=lambda c: -RVAL[c[0]])
    r = [c[0] for c in cs]
    s = [c[1] for c in cs]
    if r[0] == r[1] == r[2]:
        return r[0] * 3
    if r[0] == r[1] or r[1] == r[2]:
        if r[0] == r[1]:
            p, k, ks = r[0], r[2], s[2]
            psuits = (s[0], s[1])
        else:
            p, k, ks = r[1], r[0], s[0]
            psuits = (s[1], s[2])
        return f"{p}{p}{k}" + ("s" if ks in psuits else "r")
    a, b, d = r
    if s[0] == s[1] == s[2]:
        return f"{a}{b}{d}sss"
    if s[0] == s[1]:
        return f"{a}{b}{d}-{a}{b}s"
    if s[0] == s[2]:
        return f"{a}{b}{d}-{a}{d}s"
    if s[1] == s[2]:
        return f"{a}{b}{d}-{b}{d}s"
    return f"{a}{b}{d}r"


OPEN_PCT = {0: 0.74, 1: 0.70, 2: 0.66, 3: 0.72, 4: 0.78, 5: 0.83, 6: 0.86, 7: 0.88}
SHOVE_PCT = {0: 0.40, 1: 0.45, 2: 0.52, 3: 0.60, 4: 0.66, 5: 0.72, 6: 0.76, 7: 0.80}
THREE_BET_PCT = 0.97
CALL_OPEN_PCT = 0.85
FOUR_BET_PCT = 0.988
CALL_3BET_PCT = 0.94
# Heads-up
HU_OPEN_PCT = 0.30
HU_SHOVE_PCT = 0.30
HU_DEFEND_PCT = 0.45
HU_3BET_PCT = 0.85


def _ev(cards):
    return eval7.evaluate([eval7.Card(c) for c in cards])


class Agent(poker_agent_sdk.Agent):
    def act(self, state: GameState, memory: bytes) -> tuple[Action, bytes]:
        try:
            return decide(state), b""
        except Exception:
            if state.phase != "betting":
                first = state.legal_actions[0]
                return Action(first.kind, first.min_amount), b""
            return (Action.check() if state.can("check") else Action.fold()), b""


def _raise_to(state, total):
    r = state.can("raise")
    if not r:
        return Action.call() if state.can("call") else (Action.check() if state.can("check") else Action.fold())
    return Action.raise_to(max(r.min_amount, min(r.max_amount, int(total))))


def _shove(state):
    return _raise_to(state, 10**9)


def _call(state):
    if state.can("call"):
        return Action.call()
    return Action.check() if state.can("check") else Action.fold()


def _check_fold(state):
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


# ------------------------------------------------------------------------------------------ preflop
def _live(state):
    return [s for s in state.seats if s.status in ("active", "all_in")]


def _players_behind(state):
    n = len(state.seats)
    order = [(state.button + 1 + i) % n for i in range(n)]
    live = {s.seat for s in state.seats if s.status in ("active", "all_in")}
    order = [s for s in order if s in live or s == state.seat]
    if len(order) <= 2:
        acting = [state.button] + [s for s in order if s != state.button]
    else:
        acting = order[2:] + order[:2]
    if state.seat not in acting:
        return 0
    return len(acting) - 1 - acting.index(state.seat)


def preflop(state: GameState) -> Action:
    me = state.seats[state.seat]
    bb = state.blinds.big_blind or 1
    stack_total = me.stack + me.bet
    stack_bb = stack_total / bb
    to_call = state.to_call
    pot = max(state.pot, 1)
    label = class_label(state.cards)
    eq1, eq3, eq7 = EQ.get(label, (0.4, 0.2, 0.1))
    p1, p3 = PCT1.get(label, 0.3), PCT3.get(label, 0.3)
    behind = _players_behind(state)
    n_live = len(_live(state))
    hu = n_live <= 2

    raises = [e for e in state.history if e.kind == "raise"]
    n_raises = len(raises)
    callers = sum(1 for e in state.history if e.kind == "call")
    facing_allin = False
    if raises:
        last = raises[-1]
        if last.seat is not None:
            opp = state.seats[last.seat]
            facing_allin = opp.status == "all_in" or opp.stack == 0
    margin = _icm_margin(stack_bb, n_live)

    # ---- heads-up ---------------------------------------------------------------------------
    if hu:
        if n_raises == 0:
            if state.seat == state.button or to_call > 0:
                # button (small blind) first to act
                if stack_bb <= 10:
                    return _shove(state) if p1 >= HU_SHOVE_PCT else Action.fold()
                if p3 >= HU_OPEN_PCT:
                    return _shove(state) if stack_bb <= 14 and p1 >= 0.55 else _raise_to(state, 2.5 * bb)
                return Action.fold() if to_call > 0 else Action.check()
            return Action.check()  # big blind, button limped/checked
        if facing_allin:
            return _call_allin_decision(state, eq1, p1, to_call, pot, stack_total, margin=0.0, min_pct=0.30)
        if n_raises == 1:
            if p3 >= HU_3BET_PCT:
                return _shove(state) if stack_bb <= 25 else _raise_to(state, me.bet + to_call + 2.5 * to_call)
            if p3 >= HU_DEFEND_PCT and to_call <= 0.25 * stack_total:
                return _call(state)
            if stack_bb <= 12 and p1 >= 0.45:
                return _shove(state)
            return _check_fold(state)
        if p3 >= 0.95:
            return _shove(state)
        if p3 >= 0.80 and to_call <= 0.25 * stack_total:
            return _call(state)
        return _check_fold(state)

    # ---- short stack: push / fold -------------------------------------------------------------
    if stack_bb <= 10:
        if n_raises == 0:
            need = SHOVE_PCT.get(behind, 0.8)
            if stack_bb <= 5:
                need -= 0.12
            if n_live == 3:
                need -= 0.10
            if callers:
                need += 0.05
            if p1 >= need:
                return _shove(state)
            return Action.check() if to_call == 0 else Action.fold()
        return _call_allin_decision(state, eq1, p1, to_call, pot, stack_total, margin=min(margin, 0.03))

    # ---- unopened pot --------------------------------------------------------------------------
    if n_raises == 0:
        need = OPEN_PCT.get(behind, 0.86)
        if n_live == 3:
            need -= 0.12
        elif n_live <= 4:
            need -= 0.05
        if to_call == 0 and p3 < need:
            return Action.check()
        if p3 >= need:
            size = 2.5 * bb + callers * bb
            if stack_bb <= 16:
                if p1 >= SHOVE_PCT.get(behind, 0.8) + 0.08:
                    return _shove(state)
                return _raise_to(state, size) if p3 >= need + 0.06 else _check_fold(state)
            return _raise_to(state, size)
        return _check_fold(state)

    # ---- facing a single raise -----------------------------------------------------------------
    if n_raises == 1:
        if facing_allin:
            return _call_allin_decision(state, eq1, p1, to_call, pot, stack_total, margin=margin)
        if p3 >= THREE_BET_PCT:
            target = me.bet + to_call + 2.2 * to_call + callers * bb
            if target >= 0.4 * stack_total or stack_bb <= 20:
                return _shove(state)
            return _raise_to(state, target)
        if p3 >= CALL_OPEN_PCT and to_call <= 0.10 * stack_total and to_call <= 6 * bb:
            return _call(state)
        if p3 >= 0.93 and to_call <= 0.18 * stack_total:
            return _call(state)
        return _check_fold(state)

    # ---- facing a 3-bet or more ----------------------------------------------------------------
    if facing_allin:
        return _call_allin_decision(state, eq1, p1, to_call, pot, stack_total, margin=margin)
    if p3 >= FOUR_BET_PCT:
        return _shove(state)
    if n_raises == 2 and p3 >= CALL_3BET_PCT and to_call <= 0.15 * stack_total:
        return _call(state)
    return _check_fold(state)


def _icm_margin(stack_bb, n_live):
    if stack_bb >= 30:
        m = 0.10
    elif stack_bb >= 15:
        m = 0.06
    else:
        m = 0.03
    if n_live == 4:
        m += 0.06  # bubble: three places pay
    elif n_live == 3:
        m = min(m, 0.03)
    return m


def _call_allin_decision(state, eq1, p1, to_call, pot, stack_total, margin, min_pct=0.55):
    if to_call <= 0:
        return Action.check() if state.can("check") else _call(state)
    need = to_call / (pot + to_call)
    if to_call <= 0.10 * stack_total:
        margin = min(margin, 0.03)
    bb = state.blinds.big_blind or 1
    n_live = len(_live(state))
    if n_live > 2 and stack_total / bb >= 25 and to_call >= 0.45 * stack_total:
        margin = max(margin, 0.16)
        min_pct = 0.92
    if eq1 >= need + margin and p1 >= min_pct:
        return _call(state)
    return Action.fold() if state.can("fold") else _call(state)


# ------------------------------------------------------------------------------------------ select
M = 1_000_000
WEIGHTS = {1: (15 * M, 15 * M, 8 * M, 2 * M, 0), 3: (20 * M, 15 * M, 8 * M, 4 * M, 0), 6: (20 * M, 15 * M, 16 * M, 4 * M, 2 * M)}


def weights_for(n_opp):
    if n_opp <= 2:
        return WEIGHTS[1]
    if n_opp <= 4:
        return WEIGHTS[3]
    return WEIGHTS[6]


def draw_bonus(five, w):
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
    for lo in range(0, 9):
        if lo in ranks and lo + 1 in ranks and lo + 2 in ranks and lo + 3 in ranks:
            oesd = True
            break
    if oesd:
        bonus += w_oesd
    elif w_gut:
        for lo in range(-1, 9):
            if sum(1 for r in range(lo, lo + 5) if r in ranks) >= 4:
                bonus += w_gut
                break
    if w_over:
        top = max(RVAL[c[0]] for c in five[:3])
        board_ranks = {RVAL[c[0]] for c in five[:3]}
        if RVAL[five[3][0]] != RVAL[five[4][0]] and all(RVAL[c[0]] not in board_ranks for c in five[3:]):
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
    a, b = keep
    board_ranks = {c[0] for c in board}
    pa, pb = cards[a][0] in board_ranks, cards[b][0] in board_ranks
    lo, hi = (a, b) if RVAL[cards[a][0]] <= RVAL[cards[b][0]] else (b, a)
    if pa != pb:
        reveal, alt = (b, a) if pa else (a, b)
        mixable = False
    else:
        reveal, alt = lo, hi
        mixable = True
    if mixable and (hash((state.hand_number, cards[0], cards[1], cards[2])) % 5 == 0):
        reveal = alt
    return Action("select", cards=(discard, reveal))


# ---------------------------------------------------------------------------------------- postflop
def _board_shape(board):
    counts = {}
    for c in board:
        counts[c[0]] = counts.get(c[0], 0) + 1
    pairs = sum(1 for n in counts.values() if n == 2)
    trips = any(n >= 3 for n in counts.values())
    return pairs, trips


def hand_tier(board, hole, street):
    v = _ev(board + hole)
    cat = v >> 24
    br = [RVAL[c[0]] for c in board]
    hr = [RVAL[c[0]] for c in hole]
    top = max(br)
    pocket = hr[0] == hr[1]
    hits = [r for r in hr if r in br]
    pairs_on_board, trips_on_board = _board_shape(board)
    if len(board) == 5:
        uses_hole = v > _ev(board)
    else:
        if cat == 1:
            uses_hole = pairs_on_board == 0
        elif cat == 2:
            uses_hole = pairs_on_board < 2
        elif cat == 3:
            uses_hole = not trips_on_board
        else:
            uses_hole = True
    fd = oesd = False
    if len(board) < 5:
        suits = [c[1] for c in board + hole]
        for s in "cdhs":
            if suits.count(s) == 4 and any(c[1] == s for c in hole):
                fd = True
        ranks = set(br + hr)
        if 12 in ranks:
            ranks.add(-1)
        for lo in range(0, 9):
            if all(r in ranks for r in range(lo, lo + 4)):
                oesd = True
                break
    if not uses_hole:
        return (2 if (fd or oesd) else 1), cat, fd, oesd, False
    if cat >= 3:
        return 4, cat, fd, oesd, True
    if cat == 2:
        if len(hits) == 2 or (pocket and pairs_on_board == 0 and hits):
            return 4, cat, fd, oesd, True
        return 3, cat, fd, oesd, True
    if cat == 1:
        overpair = pocket and hr[0] > top
        top_pair = bool(hits) and max(hits) == top
        if overpair or top_pair:
            return 3, cat, fd, oesd, True
        return 2, cat, fd, oesd, True
    return (2 if (fd or oesd) else 1), cat, fd, oesd, False


def _opp_reads(state, board, our_pair_rank):
    """(number of opponents whose exposed card pairs the board, one of them above our pair,
    all opponents publicly capped at one pair)."""
    board_ranks = {c[0] for c in board}
    br = [RVAL[c[0]] for c in board]
    pairs_on_board, trips_on_board = _board_shape(board)
    shown_pair, above = 0, False
    all_capped = True
    any_opp = False
    for s in state.seats:
        if s.seat == state.seat or s.status not in ("active", "all_in"):
            continue
        any_opp = True
        if not s.shown_cards:
            all_capped = False
            continue
        c = s.shown_cards[0]
        if c[0] in board_ranks:
            shown_pair += 1
            all_capped = False
            if our_pair_rank is not None and RVAL[c[0]] > our_pair_rank:
                above = True
            continue
        if pairs_on_board or trips_on_board:
            all_capped = False
            continue
        # flush possible with the exposed card?
        if sum(1 for b in board if b[1] == c[1]) >= (2 if len(board) == 3 else 3):
            all_capped = False
            continue
        # straight possible with the exposed card (needs 3 board ranks in a 5-window with it)?
        er = RVAL[c[0]]
        ranks = set(br)
        if 12 in ranks:
            ranks.add(-1)
        e_set = {er, -1} if er == 12 else {er}
        straight = False
        for lo in range(-1, 9):
            window = set(range(lo, lo + 5))
            if window & e_set and len(window & ranks) >= 3:
                straight = True
                break
        if straight:
            all_capped = False
    return shown_pair, above, (all_capped and any_opp)


def postflop(state: GameState) -> Action:
    board = list(state.board)
    hole = list(state.cards)
    me = state.seats[state.seat]
    bb = state.blinds.big_blind or 1
    pot = max(state.pot, 1)
    to_call = state.to_call
    stack = me.stack
    stack_bb = (stack + me.bet) / bb
    street = len(board)
    n_opp = sum(1 for s in state.seats if s.seat != state.seat and s.status in ("active", "all_in"))
    tier, cat, fd, oesd, uses_hole = hand_tier(board, hole, street)
    hr = [RVAL[c[0]] for c in hole]
    br = [RVAL[c[0]] for c in board]
    our_pair_rank = None
    if cat == 1 and uses_hole:
        hits = [r for r in hr if r in br]
        our_pair_rank = hits[0] if hits else hr[0]
    shown_pair, above, capped = _opp_reads(state, board, our_pair_rank)
    if tier == 3 and above:
        tier = 2
    pf_aggr = None
    for e in state.history:
        if e.kind == "board":
            break
        if e.kind == "raise":
            pf_aggr = e.seat
    we_pfr = pf_aggr == state.seat
    bet_this_street = any(e.kind == "raise" for e in state.history[_street_start(state):])
    spr = stack / pot
    short = stack_bb <= 10 or spr <= 1.5
    facing = to_call > 0
    bet_frac = to_call / pot if facing else 0.0
    allin_call = facing and to_call >= stack
    # Our one pair is top pair and every opponent is publicly capped at one pair: play it like a strong hand.
    top_pair_vs_capped = tier == 3 and cat == 1 and capped and our_pair_rank is not None and our_pair_rank >= max(br)

    if tier == 4:
        if not facing:
            return _raise_to(state, me.bet + 0.65 * pot) if not short else _shove(state)
        if allin_call or short or to_call >= 0.4 * stack:
            return _call(state)
        return _raise_to(state, me.bet + to_call + to_call + 0.7 * pot)

    if tier == 3:
        if short:
            return _shove(state) if not facing else _call(state)
        if not facing:
            if street == 5 and (n_opp >= 2 or shown_pair) and not top_pair_vs_capped:
                return Action.check()
            return _raise_to(state, me.bet + (0.65 if top_pair_vs_capped else 0.55) * pot)
        if allin_call:
            if top_pair_vs_capped and to_call <= 1.2 * pot and stack_bb <= 30:
                return _call(state)
            return _call(state) if (to_call <= 0.6 * pot and stack_bb <= 20) else Action.fold()
        limit = 0.65 if n_opp == 1 else 0.45
        if street == 5:
            limit = 0.5 if n_opp == 1 else 0.35
        if top_pair_vs_capped:
            limit = 1.0 if n_opp == 1 else 0.7
        if bet_this_street and we_bet_this_street(state):
            limit = min(limit, 0.6 if top_pair_vs_capped else 0.4)
        max_frac = 0.45 if top_pair_vs_capped else 0.30
        if bet_frac <= limit and to_call <= max_frac * (stack + me.bet):
            return _call(state)
        return _check_fold(state)

    if tier == 2:
        has_pair = cat >= 1 and uses_hole
        if not facing:
            if street < 5 and n_opp == 1 and we_pfr and not shown_pair:
                return _raise_to(state, me.bet + 0.55 * pot)
            if street < 5 and n_opp == 1 and capped and not bet_this_street:
                return _raise_to(state, me.bet + 0.5 * pot)  # stab at a capped opponent
            if street == 3 and (fd or oesd) and n_opp == 1 and not shown_pair:
                return _raise_to(state, me.bet + 0.5 * pot)
            return Action.check()
        if allin_call:
            if short and has_pair and bet_frac <= 1.0:
                return _call(state)
            return Action.fold()
        if street < 5 and (fd or oesd):
            price = 0.40 if street == 3 else 0.28
            if fd and oesd:
                price += 0.15
            if bet_frac <= price:
                return _call(state)
        if has_pair:
            price = 0.33 if n_opp == 1 else 0.22
            if street == 5:
                price = 0.25 if n_opp == 1 else 0.0
            if capped and n_opp == 1:
                price += 0.15
            if bet_frac <= price and to_call <= 0.15 * (stack + me.bet):
                return _call(state)
        return _check_fold(state)

    if not facing:
        if street == 3 and we_pfr and n_opp == 1 and not shown_pair:
            return _raise_to(state, me.bet + 0.55 * pot)
        if street <= 4 and n_opp == 1 and capped and not bet_this_street and stack_bb > 10:
            return _raise_to(state, me.bet + 0.5 * pot)
        return Action.check()
    return _check_fold(state)


def _street_start(state):
    idx = 0
    for i, e in enumerate(state.history):
        if e.kind == "board":
            idx = i + 1
    return idx


def we_bet_this_street(state):
    for e in state.history[_street_start(state):]:
        if e.kind == "raise" and e.seat == state.seat:
            return True
    return False
