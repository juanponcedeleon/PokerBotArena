"""icm-pushfold - v0 heuristic bot + ICM-aware push/fold with precomputed 3-card shove tables.

Implements strategy/06-tournament-icm.md S6.1 (phase by effective stack), S6.2 (push/fold
tables for 3-card hands, built by calc/i_pushfold_tables.py) and S6.3 (bubble: shove first,
call tight) and strategy/02-preflop.md S2.5 (hand-vs-range equity lookup).

Everything except `preflop()` and the import-time table loading is identical to bot/agent.py
(v0), so an A/B against bot/ isolates the preflop strategy.

Preflop decision model (all in points, via Malmuth-Harville ICM on the live stacks and
`state.config.payouts`):
  * unopened pot, effective stack <= PUSH_MAX BB: shove iff
        P(no call) * ICM(me + pot) + P(call) * [eq * ICM(win) + (1 - eq) * ICM(lose)] >= ICM(fold)
    with callers assumed to call the top X*% (chip-EV Nash fixed point for this stack / players
    behind) and eq = our class's equity vs that range.
  * facing an all-in: call iff the ICM EV of calling beats folding, the shover assumed to shove
    the top Y*% for their stack / players behind them (tighter when others already called).
  * facing a normal raise with <= RESHOVE_MAX BB: re-shove or fold by the same arithmetic, the
    raiser assumed to call with X*% of an opening range.
  * deeper stacks: the v0 heuristic preflop (unchanged).
Select and postflop: v0, unchanged.
"""

import csv
import os

import eval7
import numpy as np
import poker_agent_sdk
from poker_agent_sdk import Action, GameState, icm as icm_generic

RANKS = "23456789TJQKA"
RVAL = {r: i for i, r in enumerate(RANKS)}  # 0..12

# Hand-type thresholds in eval7's value space (approximate category floors).
PAIR = 1 << 24
TWO_PAIR = 2 << 24
TRIPS = 3 << 24
STRAIGHT = 4 << 24

# ---------------------------------------------------------------- tunables (push/fold)
PUSH_MAX = 13.0        # BB: unopened pot at or below this -> shove or fold by the tables
RESHOVE_MAX = 16.0     # BB: facing a raise at or below this -> re-shove or fold by the tables
ALLIN_FRACTION = 0.6   # a raise this share of the raiser's stack (or more) is treated as a shove
OPEN_RANGE = 25.0      # % of hands a non-all-in raiser is assumed to have opened with
SHOVE_MARGIN = 0.0     # points: shove needs EV(shove) - EV(fold) >= this
CALL_MARGIN = 0.0      # points: call needs EV(call) - EV(fold) >= this

# ---------------------------------------------------------------- precomputed tables
_HERE = os.path.dirname(os.path.abspath(__file__))
X_GRID = (2, 5, 8, 12, 16, 20, 25, 30, 40, 50, 65, 80, 100)


def _load_hvr():
    out = {}
    with open(os.path.join(_HERE, "data", "hand_vs_range.csv"), newline="") as f:
        for row in csv.DictReader(f):
            out[row["label"]] = (float(row["pct"]), tuple(float(row[f"eq@{x}"]) for x in X_GRID))
    return out


def _load_nash():
    table = {}
    s_vals = set()
    with open(os.path.join(_HERE, "data", "pushfold_nash.csv"), newline="") as f:
        for row in csv.DictReader(f):
            s = float(row["S"])
            s_vals.add(s)
            table[(s, int(row["N"]))] = (float(row["shove_pct"]), float(row["call_pct"]))
    return table, sorted(s_vals)


HVR = _load_hvr()                 # label -> (pct of dealt hands, eq vs top-X% for X in X_GRID)
NASH, NASH_S = _load_nash()       # (S, N) -> (shove %, call %)


def class_key(cards):
    """Label of a concrete 3-card hand (same convention as calc/results/b_preflop_classes.csv)."""
    rs = sorted(((RVAL[c[0]], c[1]) for c in cards), key=lambda x: -x[0])
    r = [x[0] for x in rs]
    s = [x[1] for x in rs]
    if r[0] == r[1] == r[2]:
        return RANKS[r[0]] * 3
    if r[0] == r[1]:
        return RANKS[r[0]] * 2 + RANKS[r[2]] + ("s" if s[2] in (s[0], s[1]) else "r")
    if r[1] == r[2]:
        return RANKS[r[1]] * 2 + RANKS[r[0]] + ("s" if s[0] in (s[1], s[2]) else "r")
    a, b, d = RANKS[r[0]], RANKS[r[1]], RANKS[r[2]]
    if s[0] == s[1] == s[2]:
        return a + b + d + "sss"
    if s[0] == s[1]:
        return f"{a}{b}{d}-{a}{b}s"
    if s[0] == s[2]:
        return f"{a}{b}{d}-{a}{d}s"
    if s[1] == s[2]:
        return f"{a}{b}{d}-{b}{d}s"
    return a + b + d + "r"


def eq_vs_top(eqs, Y):
    """Equity vs an opponent holding the top Y% of hands (linear interpolation on X_GRID)."""
    if Y <= X_GRID[0]:
        return eqs[0]
    if Y >= X_GRID[-1]:
        return eqs[-1]
    for i in range(1, len(X_GRID)):
        if Y <= X_GRID[i]:
            x0, x1 = X_GRID[i - 1], X_GRID[i]
            return eqs[i - 1] + (Y - x0) / (x1 - x0) * (eqs[i] - eqs[i - 1])
    return eqs[-1]


def nash_ranges(S, N):
    """(shove %, call %) at the nearest tabulated effective stack S (BB) and N players behind."""
    N = max(1, min(7, int(N)))
    best = NASH_S[0]
    for s in NASH_S:
        if abs(s - S) < abs(best - S):
            best = s
    return NASH[(best, N)]


def icm_points(stacks, payouts):
    """Malmuth-Harville ICM for up to 3 paid places (numpy, ~20 us for 8 seats); generic fallback."""
    if len(payouts) > 3:
        return icm_generic(stacks, payouts)
    s = np.asarray(stacks, dtype=float)
    T = s.sum()
    if T <= 0:
        return [0.0] * len(stacks)
    p1 = s / T
    eq = p1 * payouts[0]
    if len(payouts) > 1:
        rem1 = T - s
        with np.errstate(divide="ignore", invalid="ignore"):
            P2 = np.where(rem1[:, None] > 0, p1[:, None] * s[None, :] / rem1[:, None], 0.0)
        np.fill_diagonal(P2, 0.0)
        eq = eq + P2.sum(axis=0) * payouts[1]
        if len(payouts) > 2:
            rem2 = T - s[:, None] - s[None, :]
            with np.errstate(divide="ignore", invalid="ignore"):
                W = np.where(rem2 > 0, P2 / rem2, 0.0)
            np.fill_diagonal(W, 0.0)
            P3 = s * (W.sum() - W.sum(axis=1) - W.sum(axis=0))
            eq = eq + P3 * payouts[2]
    return eq.tolist()


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


def _ev(cards):
    return eval7.evaluate([eval7.Card(c) for c in cards])


def preflop_class(cards):
    """0 = trash, 1 = marginal, 2 = good, 3 = premium (v0 heuristic, used when deep)."""
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


# ---------------------------------------------------------------- preflop: ICM push/fold

class _Spot:
    """Stacks and pot of the current hand, in chips, as seen from our seat."""

    def __init__(self, state: GameState):
        self.state = state
        self.seats = state.seats
        self.me = state.seats[state.seat]
        self.bb = max(1, state.blinds.big_blind)
        self.payouts = tuple(state.config.payouts) or (50, 30, 20)
        self.pot = state.pot
        self.my_total = self.me.stack + self.me.bet
        # Opponents still able to act (not folded, not all-in, not busted).
        self.live = [s for s in self.seats if s.seat != state.seat and s.status == "active"]
        self.allin = [s for s in self.seats if s.seat != state.seat and s.status == "all_in"]

    def _base(self):
        # Everyone's chips behind, bets included (bets are resolved by the scenario).
        return [s.stack + s.bet for s in self.seats]

    def fold_pts(self, winner_seat):
        st = [s.stack for s in self.seats]
        dead = self.pot - self.me.bet
        st[self.state.seat] = self.me.stack
        st[winner_seat] += dead + self.me.bet - 0  # the pot (incl. my dead blind) to the winner
        return icm_points(st, self.payouts)[self.state.seat]

    def uncontested_pts(self):
        st = [s.stack for s in self.seats]
        st[self.state.seat] = self.me.stack + self.pot
        return icm_points(st, self.payouts)[self.state.seat]

    def showdown_pts(self, villain):
        """(points if we win, points if we lose) heads-up for stacks vs `villain`."""
        v_total = villain.stack + villain.bet
        risk = min(self.my_total, v_total)
        dead = self.pot - self.me.bet - villain.bet
        st = [s.stack for s in self.seats]
        st[self.state.seat] = self.my_total + risk + dead
        st[villain.seat] = v_total - risk
        win = icm_points(st, self.payouts)[self.state.seat]
        st[self.state.seat] = self.my_total - risk
        st[villain.seat] = v_total + risk + dead
        lose = icm_points(st, self.payouts)[self.state.seat]
        return win, lose


def _biggest(seats):
    return max(seats, key=lambda s: s.stack + s.bet)


def _shove_ev(spot, eqs, callers, call_prob, fold_winner):
    """EV(shove) - EV(fold) in points. `callers`: seats that may call; `call_prob(seat)` their
    call probability; eq taken vs the range implied by the average call probability."""
    if not callers:
        return spot.uncontested_pts() - spot.fold_pts(fold_winner)
    pf = 1.0
    cs = []
    for s in callers:
        c = max(0.0, min(1.0, call_prob(s)))
        cs.append(c)
        pf *= 1.0 - c
    X = 100.0 * sum(cs) / len(cs)
    eq = eq_vs_top(eqs, X)
    villain = _biggest(callers)
    win, lose = spot.showdown_pts(villain)
    ev_shove = pf * spot.uncontested_pts() + (1.0 - pf) * (eq * win + (1.0 - eq) * lose)
    return ev_shove - spot.fold_pts(fold_winner)


def _folds_before(history, seat):
    """Players who folded before `seat`'s last raise this hand."""
    idx = -1
    for i, e in enumerate(history):
        if e.kind == "raise" and e.seat == seat:
            idx = i
    return sum(1 for e in history[:idx] if e.kind == "fold") if idx >= 0 else 0


def preflop(state: GameState) -> Action:
    spot = _Spot(state)
    me, bb = spot.me, spot.bb
    key = class_key(state.cards)
    pct, eqs = HVR.get(key, (50.0, (0.45,) * len(X_GRID)))
    cls = preflop_class(state.cards)
    to_call = state.to_call
    raises = [e for e in state.history if e.kind == "raise"]
    raiser_seats = []
    for e in raises:
        if e.seat not in raiser_seats:
            raiser_seats.append(e.seat)
    opp_max_total = max((s.stack + s.bet for s in spot.live + spot.allin), default=0)
    eff = min(spot.my_total, opp_max_total) / bb if opp_max_total else spot.my_total / bb
    n_behind = len(spot.live)

    if not raises:
        # ---- unopened (or limped) pot
        if eff <= PUSH_MAX:
            shove_pct, call_pct = nash_ranges(eff, max(1, n_behind))
            # Blinds/limpers call a little wider than a cold caller: they already have chips in.
            def cp(s, _c=call_pct / 100.0):
                return min(1.0, _c * (1.3 if s.bet > 0 else 1.0))
            winner = max(spot.live, key=lambda s: s.bet).seat if spot.live else state.seat
            ev = _shove_ev(spot, eqs, spot.live, cp, winner)
            if ev >= SHOVE_MARGIN:
                return _raise(state, 10**9)
            return _check_or_fold(state) if to_call > 0 else Action.check()
        # deep: v0 heuristic
        if cls == 3:
            return _raise(state, 3 * bb)
        if cls == 2:
            return _raise(state, 2.5 * bb)
        if cls == 1 and to_call <= bb:
            return _call_or_check(state)
        return _check_or_fold(state)

    # ---- someone raised
    last = raiser_seats[-1]
    raiser = state.seats[last]
    raise_total = raiser.bet
    raiser_total = raiser.stack + raiser.bet
    is_allin = raiser.status == "all_in" or raise_total >= ALLIN_FRACTION * raiser_total \
        or to_call >= ALLIN_FRACTION * me.stack
    others_in = [s for s in spot.live + spot.allin if s.seat != last and s.bet >= raise_total]
    if is_allin or eff <= RESHOVE_MAX or to_call >= me.stack:
        # Shover's assumed range: Nash shove % for their stack and the players behind them.
        n_behind_raiser = max(1, len([s for s in spot.live + spot.allin if s.seat != last]) + 1
                              - 0)  # me + live others (folded players already excluded)
        s_eff_raiser = min(raiser_total, spot.my_total) / bb
        shove_pct, _ = nash_ranges(s_eff_raiser, n_behind_raiser)
        if not is_allin:
            # A normal open: a stronger range than a shove-any range would be.
            shove_pct = min(shove_pct, OPEN_RANGE) if len(raises) == 1 else min(shove_pct, 12.0)
        if len(raises) > 1:
            shove_pct = min(shove_pct, 10.0)
        # Each extra player already in the pot roughly halves the range we must beat.
        shove_pct = max(2.0, shove_pct / (2.0 ** len(others_in)))
        eq = eq_vs_top(eqs, shove_pct)
        # Players still to act behind us can also call: tighten a little per live seat behind.
        behind_me = [s for s in spot.live if s.seat != last and s.bet < raise_total]
        eq -= 0.015 * len(behind_me)

        if is_allin or to_call >= me.stack:
            villain = _biggest([raiser] + others_in)
            win, lose = spot.showdown_pts(villain)
            ev_call = eq * win + (1.0 - eq) * lose - spot.fold_pts(last)
            if ev_call >= CALL_MARGIN:
                if to_call >= me.stack or not state.can("raise"):
                    return _call_or_check(state)
                return _raise(state, 10**9)  # isolate: our stack goes in anyway
            return _check_or_fold(state)

        # Normal raise, we are short: re-shove or fold. The raiser calls with the part of their
        # opening range that is in the Nash calling range; others behind call with call_pct.
        _, call_pct = nash_ranges(eff, 1)
        c_raiser = min(1.0, call_pct / OPEN_RANGE)

        def cp(s):
            return c_raiser if s.seat == last else min(1.0, call_pct / 100.0)
        callers = [raiser] + behind_me + others_in
        ev = _shove_ev(spot, eqs, callers, cp, last)
        if ev >= SHOVE_MARGIN:
            return _raise(state, 10**9)
        return _check_or_fold(state)

    # ---- deep, facing a normal raise: v0 heuristic
    if cls == 3:
        return _raise(state, max(3 * to_call, 3 * bb) + me.bet)
    if cls == 2:
        if to_call <= 6 * bb:
            return _call_or_check(state)
        return _check_or_fold(state)
    return _check_or_fold(state)


# ---------------------------------------------------------------- postflop: v0, unchanged

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
