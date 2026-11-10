"""fp-cfc - fp-v3 (percentile preflop, keep rule v2, non-pairing exposure, ICM-tight all-in calls) with the
postflop module of cap-floor-count-v6 (action-conditioned cap/floor/count, 01 S1.1-S1.3 + 04 S4.1-S4.4) transplanted
in place of fp-v3's tiered postflop. Everything before the flop is fp-v3 byte for byte; everything after the flop
is cap-floor-count-v6 byte for byte. Original fp-v3 docstring follows.

fp-v3 — fp-v2 + ICM-tight deep all-in calls: at >= 25 BB a call that costs >= 45% of our stack needs
heads-up equity >= pot odds + 0.16 and a top-8% class (57 of 110 early busts in the logged league were
calls of all-ins with median class percentile 0.90, mostly against shovers; folding keeps ~12.5 pts of equity).

fp-v2 — fp-v1 + GC tuning (gc.freeze + high threshold, as cap-floor-count-v6) to remove the 19 ms GC tail.
Play is byte-identical to fp-v1.

fp-v1 — a first-principles bot for the Bay Area variant, shaped by the practice-round winners.

Design (see BOT.md and strategy/05 S5.3, calc/results/j_practice_deepdive.md):
  Preflop  every 3-card class has an all-in equity vs 1/3/7 opponents (calc/results/b_preflop_classes.csv);
           decisions use the class's PERCENTILE among dealt hands. Open-raise 2.5 BB from a position-dependent
           top-X% (tighter early), never limp, 3-bet only the top ~3%, call opens with the top ~15% when cheap,
           never escalate 4-bet wars without a monster, push/fold at <= 10 BB with position-aware ranges, call
           all-ins only with pot-odds equity plus an ICM margin that shrinks as we get short.
  Select   keep rule v2 (strategy/03 S3.1 + S3.3: made hand + tuned draw/overcard bonuses by live opponents);
           expose a card that does NOT pair the board (top-10 teams: 0.5% pairing exposures), lower rank
           first, 20% deterministic mix to stay non-invertible.
  Postflop hand tiers (nuts / top pair or two pair / weak pair or strong draw / air) x street x pot odds x stack
           pressure. 75% c-bet heads-up as the aggressor, half-pot sizing, value bets with two pair+, one-pair
           discipline (never stack off one pair deep), fold to raises without two pair+, draws only at price,
           shove-or-fold postflop when the stack-to-pot ratio is small.
Stateless: no memory is used.  All tables are built at import; a decision is a few dict lookups and <= 3 evaluate calls.
"""

import csv
import gc
from pathlib import Path

import gc

import eval7
import poker_agent_sdk
from poker_agent_sdk import Action, GameState

RANKS = "23456789TJQKA"
RVAL = {r: i for i, r in enumerate(RANKS)}
PAIR = 1 << 24

# ----------------------------------------------------------------------------------------------
# Preflop table: label -> (eq_vs1, eq_vs3, eq_vs7); percentiles weighted by how often the class is dealt.
# ----------------------------------------------------------------------------------------------
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
    return 4  # trips


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
    """Map three card strings to the label scheme of calc/b_preflop_classes.py."""
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


# Position: players still to act after us preflop -> required percentile (vs 3) to open-raise.
OPEN_PCT = {0: 0.74, 1: 0.70, 2: 0.66, 3: 0.72, 4: 0.78, 5: 0.83, 6: 0.86, 7: 0.88}
# Push/fold (<= 10 BB): required percentile (vs 1) to open-shove, by players behind.
SHOVE_PCT = {0: 0.40, 1: 0.45, 2: 0.52, 3: 0.60, 4: 0.66, 5: 0.72, 6: 0.76, 7: 0.80}
THREE_BET_PCT = 0.97
CALL_OPEN_PCT = 0.85
FOUR_BET_PCT = 0.988
CALL_3BET_PCT = 0.94


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


# ----------------------------------------------------------------------------------------------
# Action helpers
# ----------------------------------------------------------------------------------------------
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


# ----------------------------------------------------------------------------------------------
# Preflop
# ----------------------------------------------------------------------------------------------
def _live(state):
    return [s for s in state.seats if s.status in ("active", "all_in")]


def _players_behind(state):
    """Live players who still act after us in the preflop order (blinds act last)."""
    n = len(state.seats)
    order = [(state.button + 1 + i) % n for i in range(n)]  # SB, BB, UTG, ..., BTN
    live = {s.seat for s in state.seats if s.status in ("active", "all_in")}
    order = [s for s in order if s in live or s == state.seat]
    if len(order) <= 2:  # heads-up: button is SB and acts first
        acting = order[::-1] if state.seat == state.button else order
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

    raises = [e for e in state.history if e.kind == "raise"]
    n_raises = len(raises)
    callers = sum(1 for e in state.history if e.kind == "call")
    # Is the bet we face an all-in (someone committed their whole stack)?
    facing_allin = False
    if raises:
        last = raises[-1]
        if last.seat is not None:
            opp = state.seats[last.seat]
            facing_allin = opp.status == "all_in" or opp.stack == 0
    n_live = len(_live(state))

    # ---- short stack: push / fold ------------------------------------------------------------
    if stack_bb <= 10:
        if n_raises == 0:
            need = SHOVE_PCT.get(behind, 0.8)
            if stack_bb <= 5:
                need -= 0.12
            if callers:  # limpers ahead: a shove needs a bit more
                need += 0.05
            if p1 >= need:
                return _shove(state)
            return Action.check() if to_call == 0 else Action.fold()
        return _call_allin_decision(state, eq1, p1, to_call, pot, stack_total, margin=0.03)

    # ---- unopened pot -------------------------------------------------------------------------
    if n_raises == 0:
        need = OPEN_PCT.get(behind, 0.86)
        if n_live <= 3:
            need -= 0.08  # short-handed: open wider
        if to_call == 0 and p3 < need:  # big blind, limped or walked: free flop
            return Action.check()
        if p3 >= need:
            size = 2.5 * bb + callers * bb
            if stack_bb <= 16:
                return _shove(state) if p1 >= SHOVE_PCT.get(behind, 0.8) + 0.08 else (_raise_to(state, size) if p3 >= need + 0.06 else _check_fold(state))
            return _raise_to(state, size)
        return _check_fold(state)

    # ---- facing a single raise ----------------------------------------------------------------
    if n_raises == 1:
        if facing_allin:
            return _call_allin_decision(state, eq1, p1, to_call, pot, stack_total, margin=_icm_margin(stack_bb))
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

    # ---- facing a 3-bet or more ---------------------------------------------------------------
    if facing_allin:
        return _call_allin_decision(state, eq1, p1, to_call, pot, stack_total, margin=_icm_margin(stack_bb))
    if p3 >= FOUR_BET_PCT:
        return _shove(state)
    if n_raises == 2 and p3 >= CALL_3BET_PCT and to_call <= 0.15 * stack_total:
        return _call(state)
    return _check_fold(state)


def _icm_margin(stack_bb):
    if stack_bb >= 30:
        return 0.10
    if stack_bb >= 15:
        return 0.06
    return 0.03


def _call_allin_decision(state, eq1, p1, to_call, pot, stack_total, margin):
    """Call an all-in iff our heads-up equity beats the pot odds by the margin (and the class is not junk)."""
    if to_call <= 0:
        return Action.check() if state.can("check") else _call(state)
    need = to_call / (pot + to_call)
    # Cheap relative to our stack: the margin matters less.
    if to_call <= 0.10 * stack_total:
        margin = min(margin, 0.03)
    min_pct = 0.55
    bb = state.blinds.big_blind or 1
    if stack_total / bb >= 25 and to_call >= 0.45 * stack_total:
        margin = max(margin, 0.16)  # deep and for our tournament life: only a big favourite calls
        min_pct = 0.92
    if eq1 >= need + margin and p1 >= min_pct:
        return _call(state)
    return Action.fold() if state.can("fold") else _call(state)


# ----------------------------------------------------------------------------------------------
# Selection: keep rule v2 + non-pairing exposure
# ----------------------------------------------------------------------------------------------
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
        reveal, alt = (b, a) if pa else (a, b)  # show the card that does not pair the board
        mixable = False
    else:
        reveal, alt = lo, hi
        mixable = True
    # Deterministic 20% mix (hand number + cards), so a reader cannot invert the rule, but only
    # between two non-pairing (or two pairing) cards.
    if mixable and (hash((state.hand_number, cards[0], cards[1], cards[2])) % 5 == 0):
        reveal = alt
    return Action("select", cards=(discard, reveal))


# ----------------------------------------------------------------------------------------------
# Postflop
# ----------------------------------------------------------------------------------------------
def _board_shape(board):
    counts = {}
    for c in board:
        counts[c[0]] = counts.get(c[0], 0) + 1
    pairs = sum(1 for n in counts.values() if n == 2)
    trips = any(n >= 3 for n in counts.values())
    return pairs, trips


def hand_tier(board, hole, street):
    """4 nuts-ish, 3 top pair / strong two pair, 2 weak pair or strong draw, 1 air. Also returns flags."""
    v = _ev(board + hole)
    cat = v >> 24
    br = [RVAL[c[0]] for c in board]
    hr = [RVAL[c[0]] for c in hole]
    top = max(br)
    pocket = hr[0] == hr[1]
    hits = [r for r in hr if r in br]  # hole ranks that pair the board
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
    # draws (flop / turn only)
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
        tier = 2 if (fd or oesd) else 1
        return tier, cat, fd, oesd, False
    if cat >= 3:
        return 4, cat, fd, oesd, True
    if cat == 2:
        if len(hits) == 2 or (pocket and pairs_on_board == 0 and hits):
            return 4, cat, fd, oesd, True  # two pair with both hole cards: strong
        return 3, cat, fd, oesd, True
    if cat == 1:
        overpair = pocket and hr[0] > top
        top_pair = bool(hits) and max(hits) == top
        if overpair or top_pair:
            return 3, cat, fd, oesd, True
        return 2, cat, fd, oesd, True
    tier = 2 if (fd or oesd) else 1
    return tier, cat, fd, oesd, False


def _opp_scare(state, board, our_pair_rank):
    """Opponents whose exposed card pairs the board (public pair) and whether one outranks our pair."""
    board_ranks = {c[0] for c in board}
    shown_pair, above = 0, False
    for s in state.seats:
        if s.seat == state.seat or s.status not in ("active", "all_in"):
            continue
        for c in s.shown_cards[:1]:
            if c[0] in board_ranks:
                shown_pair += 1
                if our_pair_rank is not None and RVAL[c[0]] > our_pair_rank:
                    above = True
    return shown_pair, above


SUITS = "cdhs"
DECK = [r + s for r in RANKS for s in SUITS]
CARD = {c: eval7.Card(c) for c in DECK}
TWO_PAIR = 2 << 24
TRIPS = 3 << 24
STRAIGHT = 4 << 24

# Latency: import-time objects to the permanent GC generation, rare collections (cap-floor-count v5).
gc.freeze()
gc.set_threshold(50000, 50, 50)


def _cat(v):
    return v >> 24


# --- tunables of the postflop policy (priors until the arena says otherwise) ------------------
# How much a "currently best" probability overstates equity with cards to come, by our category.
SHRINK_FLOP = {0: 0.60, 1: 0.72, 2: 0.80, 3: 0.88, 4: 0.92}  # key = min(category, 4)
SHRINK_TURN = {0: 0.75, 1: 0.85, 2: 0.90, 3: 0.95, 4: 0.97}
OUTS_MULT_FLOP = 1.9       # two cards to come
OUTS_MULT_TURN = 1.0
VALUE_BET_EQ = 0.60        # bet when nobody has bet and our equity estimate is above this
RAISE_EQ = 0.78            # raise a bet when above this
NUTS_BET_POT = 0.80        # bet size (fraction of pot) when we beat every cap
VALUE_BET_POT = 0.60       # bet size otherwise
CALL_MARGIN = 0.05         # call needs eq >= pot odds + margin
AGGR_ALPHA = 0.90        # weight of the made-hand-only count for a street aggressor
AGGR_ALPHA_EARLIER = 0.50  # ... for someone who bet an earlier street and checks now
BETA_MAX = 0.80          # weight of the two-pair-plus-only count for a big bet / repeated aggression
AGGR_ALPHA_RAISE = 1.00  # ... for someone who raised a bet this street
UNKNOWN_LOSE = {0: 0.70, 1: 0.45, 2: 0.25, 3: 0.12, 4: 0.06}  # opponent with no exposed card



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
    # Aggression on the current street: raises after the last board event (bets are raises here).
    aggr = {}       # raises on the current street
    aggr_hand = {}  # raises on any postflop street this hand
    seen_board = False
    for e in state.history:
        if e.kind == "board":
            aggr = {}
            seen_board = True
        elif e.kind == "raise" and e.seat is not None and seen_board:
            aggr[e.seat] = aggr.get(e.seat, 0) + 1
            aggr_hand[e.seat] = aggr_hand.get(e.seat, 0) + 1
    opps = []
    for s in state.seats:
        shown = tuple(s.shown_cards or ())
        for c in shown:
            dead.add(c)
        if s.seat == state.seat or s.status not in ("active", "all_in"):
            continue
        opps.append((shown, aggr.get(s.seat, 0), aggr_hand.get(s.seat, 0)))
    unseen = [c for c in DECK if c not in dead]
    return board, hole, opps, unseen


def count_opponent(shown, bcards, ucards, ours, alpha, board_v, beta):
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
    made = 0        # hidden cards giving them pair+ that uses a hole card (what a value bettor holds)
    made_beat = 0.0
    big = 0         # hidden cards giving them two pair or better (what a big bet means)
    big_beat = 0.0
    for h in ucards:
        hand[1] = h
        v = evaluate(hand)
        if v > cap:
            cap = v
        if v < floor:
            floor = v
        w = 1.0 if v > ours else 0.5 if v == ours else 0.0
        if w == 1.0:
            beat += 1
        elif w == 0.5:
            ties += 1
        if v >= PAIR and v > board_v:
            made += 1
            made_beat += w
            if v >= TWO_PAIR:
                big += 1
                big_beat += w
    lose = (beat + 0.5 * ties) / len(ucards)
    if alpha > 0.0 and made > 0:
        made_lose = made_beat / made
        if beta > 0.0 and big > 0:
            made_lose = beta * (big_beat / big) + (1.0 - beta) * made_lose
        lose = alpha * made_lose + (1.0 - alpha) * lose
    return cap, floor, lose


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
    board_v = eval7.evaluate(bcards) if len(bcards) >= 5 else 0
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
    bet_frac = to_call / max(pot - to_call, 1) if to_call > 0 else 0.0  # their bet relative to the pot before it
    for shown, n_aggr, n_hand in opps:
        if not shown or not unseen:
            lose = UNKNOWN_LOSE[cat]
            beat_all_caps = False
        else:
            if n_aggr >= 2:
                alpha = AGGR_ALPHA_RAISE
            elif n_aggr == 1:
                alpha = AGGR_ALPHA
            elif n_hand >= 1:
                alpha = AGGR_ALPHA_EARLIER   # bet an earlier street, checking now
            else:
                alpha = 0.0
            beta = 0.0
            if n_aggr >= 1:
                beta = min(BETA_MAX, max(0.0, (bet_frac - 0.35) / 0.4 * BETA_MAX))  # 0 at <=0.35 pot, max at >=0.75 pot
                if n_aggr >= 2 or n_hand >= 2:
                    beta = BETA_MAX
            cap, floor, lose = count_opponent(shown, bcards, ucards, ours, alpha, board_v, beta)
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
