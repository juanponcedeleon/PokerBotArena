"""icm-pushfold-v8 - v0-nowar heuristic bot + ICM-aware push/fold with precomputed 3-card shove tables
and per-seat call/raise frequencies kept in memory.

Implements strategy/06-tournament-icm.md S6.1 (phase by effective stack; "track call-vs-shove
rates per seat"), S6.2 (push/fold tables for 3-card hands, built by calc/i_pushfold_tables.py),
S6.3 (bubble: shove first, call tight) and strategy/02-preflop.md S2.5 (hand-vs-range equity).

Everything except `preflop()`, the memory bookkeeping and the import-time table loading is
identical to bot/agent.py as of 2026-11-06 19:22 ("v0-nowar": v0 with the deep 3-bet war capped), so
an A/B against bot/ isolates the short-stack strategy. v2-v4 were measured against this baseline
while still carrying the *old* v0 deep-stack preflop, which is why they lost: the deep war, not
the push/fold, cost the points (see strategy/08-experiments.md).

Changes from icm-pushfold (v1), which lost 2.4 pts/table to v0:
  * calling an all-in is a call, never a re-shove of our whole stack ("isolation" bug);
  * players already committed to the pot (all-in, or >= 30% of their stack in) count as callers,
    and equity is scaled to the number of opponents (eq vs 1 / 3 / 7 columns);
  * each seat's call-vs-raise and raise frequencies are learned from `state.events` and blended
    with the Nash prior: fold equity comes from the actual table, not from theory.

Preflop decision model (points via Malmuth-Harville ICM on live stacks and config.payouts):
  * unopened pot, effective stack <= PUSH_MAX BB: shove iff
        P(no call) * ICM(me + pot) + P(call) * [eq * ICM(win) + (1 - eq) * ICM(lose)] >= ICM(fold)
  * facing an all-in: call iff ICM EV of calling beats folding; the shover's range is the Nash
    shove % for their stack blended with their observed raise frequency.
  * facing a normal raise with <= RESHOVE_MAX BB: re-shove or fold by the same arithmetic.
  * deeper: the v0 heuristic preflop (unchanged), INCLUDING all-in calls (v4): at >16 BB
    effective the ICM arithmetic (even with a survival premium) called raise-war all-ins with
    top-16% hands and busted in level 1 twice as often as v0; v0's "3-bet the top 12%, never
    call off" is the better response to a field of maniacs. The ICM machinery now runs only when
    the stack at risk is short: ours, or the shover's, at most RESHOVE_MAX BB.
Select and postflop: v0, unchanged.

v6 = v5 with identical decisions and a faster hot path: ICM through a numba-compiled O(n^3) loop
(compiled at import, ~2 us per call instead of 45-60 us; pure-Python fallback if numba is missing)
and a single struct.pack for the memory blob. v5 spent ~70% of its decision time in ICM.
v7 = v6 with the parameters the 300-pair sweep (seed icm3) preferred: PUSH_MAX 15 / RESHOVE_MAX 18
(+1.57 +-0.67 vs 13/16) and PREMIUM 0.30 (+1.40 +-0.63 vs 0.15).
"""

import csv
import os
import struct

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
PUSH_MAX = 18.0        # BB: unopened pot at or below this -> shove or fold by the tables
RESHOVE_MAX = 22.0     # BB: facing a raise at or below this -> re-shove or fold by the tables
ALLIN_FRACTION = 0.6   # a raise this share of the raiser's stack (or more) is treated as a shove
COMMITTED = 0.3        # a player with this share of their stack in the pot is assumed to call
OPEN_RANGE = 25.0      # % of hands a non-all-in raiser is assumed to have opened with
PRIOR_HANDS = 10.0     # weight (in observed decisions) of the Nash prior for a seat's frequencies
SHOVE_MARGIN = 0.0     # points: shove needs EV(shove) - EV(fold) >= this
CALL_MARGIN = 0.0      # points: call needs EV(call) - EV(fold) >= this
# Survival premium (v3): ICM assumes equal skill, but a field of simple bots busts itself, so
# folding is worth more than ICM(fold) early. Required edge = PREMIUM * ICM(fold) * (n - 2) / 6,
# n = players remaining (0 heads-up, full with 8). Multiway all-ins pay it once per extra player.
PREMIUM = 0.50
MULTIWAY_PREMIUM = 0.5

# ---------------------------------------------------------------- precomputed tables
_HERE = os.path.dirname(os.path.abspath(__file__))
X_GRID = (2, 5, 8, 12, 16, 20, 25, 30, 40, 50, 65, 80, 100)


def _load_hvr():
    out = {}
    with open(os.path.join(_HERE, "data", "hand_vs_range.csv"), newline="") as f:
        for row in csv.DictReader(f):
            out[row["label"]] = (float(row["pct"]),
                                 tuple(float(row[f"eq@{x}"]) for x in X_GRID),
                                 (float(row["eq@100"]), float(row["eq_vs3"]), float(row["eq_vs7"])))
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


HVR = _load_hvr()                 # label -> (pct, eq vs top-X% for X in X_GRID, (eq vs 1, 3, 7 random))
NASH, NASH_S = _load_nash()       # (S, N) -> (shove %, call %)
_DEFAULT_HVR = (50.0, (0.45,) * len(X_GRID), (0.45, 0.22, 0.10))


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
    """Equity vs one opponent holding the top Y% of hands (linear interpolation on X_GRID)."""
    if Y <= X_GRID[0]:
        return eqs[0]
    if Y >= X_GRID[-1]:
        return eqs[-1]
    for i in range(1, len(X_GRID)):
        if Y <= X_GRID[i]:
            x0, x1 = X_GRID[i - 1], X_GRID[i]
            return eqs[i - 1] + (Y - x0) / (x1 - x0) * (eqs[i] - eqs[i - 1])
    return eqs[-1]


def eq_multiway(hvr, Y, k):
    """Equity vs k opponents who each hold the top Y%: heads-up range equity scaled by the
    random-opponent multiway curve (vs 1 / 3 / 7 columns, interpolated in k)."""
    pct, eqs, (e1, e3, e7) = hvr
    if k <= 1:
        return eq_vs_top(eqs, Y)
    if k <= 3:
        base = e1 + (e3 - e1) * (k - 1) / 2.0
    else:
        base = e3 + (e7 - e3) * (min(k, 7) - 3) / 4.0
    ratio = eq_vs_top(eqs, Y) / max(e1, 1e-6)
    return max(0.0, min(1.0, base * ratio))


def nash_ranges(S, N):
    """(shove %, call %) at the nearest tabulated effective stack S (BB) and N players behind."""
    N = max(1, min(7, int(N)))
    best = NASH_S[0]
    for s in NASH_S:
        if abs(s - S) < abs(best - S):
            best = s
    return NASH[(best, N)]


try:
    import numba

    @numba.njit(cache=False)
    def _icm3_nb(st, p0, p1, p2):
        n = st.shape[0]
        eq = np.zeros(n)
        T = 0.0
        for i in range(n):
            T += st[i]
        if T <= 0:
            return eq
        for i in range(n):
            si = st[i]
            if si <= 0:
                continue
            pi = si / T
            eq[i] += pi * p0
            if p1 == 0.0:
                continue
            Ti = T - si
            if Ti <= 0:
                continue
            for j in range(n):
                if j == i or st[j] <= 0:
                    continue
                pij = pi * st[j] / Ti
                eq[j] += pij * p1
                if p2 == 0.0:
                    continue
                Tij = Ti - st[j]
                if Tij <= 0:
                    continue
                f = pij * p2 / Tij
                for k in range(n):
                    if k != i and k != j and st[k] > 0:
                        eq[k] += f * st[k]
        return eq

    _icm3_nb(np.array([2000.0, 1000.0, 0.0, 500.0]), 50.0, 30.0, 20.0)  # compile at import
    _HAVE_NUMBA = True
except Exception:  # pragma: no cover - platform without numba
    _HAVE_NUMBA = False


def icm_points(stacks, payouts):
    """Malmuth-Harville ICM for up to 3 paid places: numba O(n^3) loop (~2 us), else pure Python
    for <= 6 live players / numpy above; generic SDK routine for more than 3 paid places."""
    if len(payouts) > 3:
        return icm_generic(stacks, payouts)
    if _HAVE_NUMBA:
        p = [float(payouts[i]) if i < len(payouts) else 0.0 for i in range(3)]
        return _icm3_nb(np.asarray(stacks, dtype=np.float64), p[0], p[1], p[2]).tolist()
    live = [i for i in range(len(stacks)) if stacks[i] > 0]
    n = len(stacks)
    if len(live) <= 6:
        T = float(sum(stacks))
        eq = [0.0] * n
        if T <= 0:
            return eq
        p = [payouts[i] if i < len(payouts) else 0.0 for i in range(3)]
        for i in live:
            si = stacks[i]
            pi = si / T
            eq[i] += pi * p[0]
            if p[1] == 0:
                continue
            Ti = T - si
            if Ti <= 0:
                continue
            for j in live:
                if j == i:
                    continue
                sj = stacks[j]
                pij = pi * sj / Ti
                eq[j] += pij * p[1]
                if p[2] == 0:
                    continue
                Tij = Ti - sj
                if Tij <= 0:
                    continue
                f = pij * p[2] / Tij
                for k in live:
                    if k != i and k != j:
                        eq[k] += f * stacks[k]
        return eq
    s = np.asarray(stacks, dtype=float)
    T = s.sum()
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


# ---------------------------------------------------------------- memory: per-seat frequencies
# Header: magic "IP2", flags (bit0 preflop, bit1 raised, bit2 all-in seen), then per seat:
#   dealt, pfr, faced_raise, cont_vs_raise, faced_allin, call_allin (uint16) + stack (uint32).
_MAGIC = b"IP2"
_HDR = struct.Struct("<3sB")
_SEAT = struct.Struct("<6HI")
_NSEATS = 10
_MEM_LEN = _HDR.size + _SEAT.size * _NSEATS
_FIELDS = 7


def _parse_memory(memory, state):
    """Return (flags, [[dealt, pfr, faced_raise, cont, faced_allin, call_allin, stack] * seats])."""
    n = max(len(state.seats), 1)
    fresh = [[0, 0, 0, 0, 0, 0, state.config.starting_stack] for _ in range(_NSEATS)]
    if not memory or len(memory) != _MEM_LEN:
        return 0, fresh, True
    try:
        magic, flags = _HDR.unpack_from(memory, 0)
        if magic != _MAGIC:
            return 0, fresh, True
        seats = []
        for i in range(_NSEATS):
            seats.append(list(_SEAT.unpack_from(memory, _HDR.size + i * _SEAT.size)))
        return flags, seats, False
    except Exception:
        return 0, fresh, True


_ALL = struct.Struct("<3sB" + "6HI" * _NSEATS)


def _pack_memory(flags, seats):
    flat = [_MAGIC, flags & 0xFF]
    for s in seats:
        if s[0] > 60000:  # keep counters in range after very long tables
            s[:6] = [v >> 1 for v in s[:6]]
        flat.extend(s[:6])
        flat.append(min(max(s[6], 0), 0xFFFFFFFF))
    return _ALL.pack(*flat)


def _update_stats(flags, seats, events, first):
    """Consume the events since our last turn (preflop actions only) into per-seat counters."""
    preflop = bool(flags & 1)
    raised = bool(flags & 2)
    allin = bool(flags & 4)
    for e in events:
        k = e.kind
        if k == "hand":
            preflop, raised, allin = True, False, False
            continue
        s = e.seat
        if k == "board":
            preflop = False
            continue
        if k == "stack":
            if s is not None and 0 <= s < _NSEATS:
                seats[s][6] = e.amount
            continue
        if not preflop or s is None or not (0 <= s < _NSEATS):
            continue
        st = seats[s]
        if k == "blind":
            continue
        if k in ("fold", "check", "call", "raise"):
            st[0] += 1  # one preflop decision this hand (a seat acts at least once if dealt in)
            if raised:
                st[2] += 1
                if k != "fold":
                    st[3] += 1
            if allin:
                st[4] += 1
                if k != "fold":
                    st[5] += 1
            if k == "raise":
                st[1] += 1
                raised = True
                if e.amount >= st[6] - 0:
                    allin = True
    flags = (1 if preflop else 0) | (2 if raised else 0) | (4 if allin else 0)
    return flags, seats


def _seat_call_prob(st, prior):
    """Blend of the Nash calling probability and the seat's observed continue-vs-raise rate."""
    n_al, c_al = st[4], st[5]
    n_r, c_r = st[2], st[3]
    if n_al >= 4:
        obs_n, obs = n_al, c_al / n_al
    elif n_r > 0:
        obs_n, obs = n_r, c_r / n_r
    else:
        return prior
    return (PRIOR_HANDS * prior + obs_n * obs) / (PRIOR_HANDS + obs_n)


def _seat_raise_pct(st, prior):
    """Blend of the Nash shove % and the seat's observed preflop raise frequency (in %)."""
    if st[0] <= 0:
        return prior
    return (PRIOR_HANDS * prior + st[0] * (100.0 * st[1] / st[0])) / (PRIOR_HANDS + st[0])


class Agent(poker_agent_sdk.Agent):
    def act(self, state: GameState, memory: bytes) -> tuple[Action, bytes]:
        try:
            flags, seats, _ = _parse_memory(memory, state)
            flags, seats = _update_stats(flags, seats, state.events, False)
            new_memory = _pack_memory(flags, seats)
        except Exception:
            seats = [[0, 0, 0, 0, 0, 0, state.config.starting_stack] for _ in range(_NSEATS)]
            new_memory = memory if memory and len(memory) == _MEM_LEN else b""
        try:
            return decide(state, seats), new_memory
        except Exception:
            if state.phase != "betting":
                first = state.legal_actions[0]
                return Action(first.kind, first.min_amount), new_memory
            return (Action.check() if state.can("check") else Action.fold()), new_memory


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


def decide(state: GameState, stats) -> Action:
    if state.phase == "select":
        return select(state)
    if state.phase != "betting":
        first = state.legal_actions[0]
        return Action(first.kind, first.min_amount)
    if not state.board:
        return preflop(state, stats)
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
        self.live = [s for s in self.seats if s.seat != state.seat and s.status == "active"]
        self.allin = [s for s in self.seats if s.seat != state.seat and s.status == "all_in"]
        self._cache = {}

    def _pts(self, st):
        key = tuple(st)
        v = self._cache.get(key)
        if v is None:
            v = icm_points(st, self.payouts)[self.state.seat]
            self._cache[key] = v
        return v

    def fold_pts(self, winner_seat):
        st = [s.stack for s in self.seats]
        st[winner_seat] += self.pot  # the pot (incl. our dead blind) to whoever is winning it
        return self._pts(st)

    def uncontested_pts(self):
        st = [s.stack for s in self.seats]
        st[self.state.seat] = self.me.stack + self.pot
        return self._pts(st)

    def showdown_pts(self, villain, extra_dead=0):
        """(points if we win, points if we lose) for stacks heads-up vs `villain`."""
        v_total = villain.stack + villain.bet
        risk = min(self.my_total, v_total)
        dead = self.pot - self.me.bet - villain.bet + extra_dead
        st = [s.stack for s in self.seats]
        st[self.state.seat] = self.my_total + risk + dead
        st[villain.seat] = v_total - risk
        win = self._pts(st)
        st[self.state.seat] = self.my_total - risk
        st[villain.seat] = v_total + risk + dead
        lose = self._pts(st)
        return win, lose


def _biggest(seats):
    return max(seats, key=lambda s: s.stack + s.bet)


def _premium(spot, fold_pts, extra_players=0):
    """Edge over folding required before we put our stack in, in points."""
    n = max(2, spot.state.players_remaining)
    base = PREMIUM * max(fold_pts, 0.0) * (n - 2) / 6.0
    return base * (1.0 + MULTIWAY_PREMIUM * extra_players)


def _shove_ev(spot, hvr, callers, fold_winner):
    """EV(shove) - EV(fold) in points. `callers`: list of (seat, call probability, range %)."""
    if not callers:
        return spot.uncontested_pts() - spot.fold_pts(fold_winner)
    pf = 1.0
    wsum = 0.0
    eqsum = 0.0
    for s, c, Y in callers:
        pf *= 1.0 - c
        wsum += c
        eqsum += c * eq_vs_top(hvr[1], Y)
    sure = [s for s, c, Y in callers if c >= 0.95]
    if len(sure) >= 2:
        # Several near-certain callers: multiway equity vs their average range.
        Ybar = sum(Y for s, c, Y in callers if c >= 0.95) / len(sure)
        eq = eq_multiway(hvr, Ybar, len(sure))
    else:
        eq = eqsum / wsum if wsum > 0 else eq_vs_top(hvr[1], 100)
    villain = _biggest([s for s, c, Y in callers if c >= 0.2] or [s for s, c, Y in callers])
    win, lose = spot.showdown_pts(villain)
    ev_shove = pf * spot.uncontested_pts() + (1.0 - pf) * (eq * win + (1.0 - eq) * lose)
    return ev_shove - spot.fold_pts(fold_winner)


def preflop(state: GameState, stats) -> Action:
    spot = _Spot(state)
    me, bb = spot.me, spot.bb
    hvr = HVR.get(class_key(state.cards), _DEFAULT_HVR)
    cls = preflop_class(state.cards)
    to_call = state.to_call
    raises = [e for e in state.history if e.kind == "raise"]
    raiser_seats = []
    for e in raises:
        if e.seat not in raiser_seats:
            raiser_seats.append(e.seat)
    others = spot.live + spot.allin
    opp_max_total = max((s.stack + s.bet for s in others), default=0)
    eff = min(spot.my_total, opp_max_total) / bb if opp_max_total else spot.my_total / bb
    n_behind = len(spot.live)

    def committed(s):
        tot = s.stack + s.bet
        return s.status == "all_in" or (tot > 0 and s.bet >= COMMITTED * tot)

    if not raises:
        # ---- unopened (or limped) pot
        if eff <= PUSH_MAX:
            _, call_pct = nash_ranges(eff, max(1, n_behind))
            callers = []
            for s in spot.live:
                prior = min(1.0, call_pct / 100.0 * (1.3 if s.bet > 0 else 1.0))
                c = _seat_call_prob(stats[s.seat], prior)
                if committed(s):
                    c = max(c, 0.9)
                # The hands they call with: their calling range, as wide as their call probability.
                callers.append((s, c, max(2.0, 100.0 * c)))
            winner = max(spot.live, key=lambda s: s.bet).seat if spot.live else state.seat
            ev = _shove_ev(spot, hvr, callers, winner)
            if ev >= SHOVE_MARGIN + _premium(spot, spot.fold_pts(winner)) * 0.5:
                return _raise(state, 10**9)
            return _check_or_fold(state) if to_call > 0 else Action.check()
        # deep: v0-nowar heuristic, unopened
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
    others_in = [s for s in others if s.seat != last and (s.bet >= raise_total or committed(s))]
    behind_me = [s for s in spot.live if s.seat != last and s.bet < raise_total and not committed(s)]

    eff_raiser = min(raiser_total, spot.my_total) / bb
    short_spot = eff <= RESHOVE_MAX or (is_allin and eff_raiser <= RESHOVE_MAX and not others_in)
    if short_spot:
        # Shover's assumed range: Nash shove % for their stack and the players behind them,
        # blended with how often this seat actually raises.
        n_behind_raiser = max(1, len([s for s in others if s.seat != last]) + 1)
        s_eff_raiser = min(raiser_total, spot.my_total) / bb
        shove_pct, _ = nash_ranges(s_eff_raiser, n_behind_raiser)
        shove_pct = _seat_raise_pct(stats[last], shove_pct)
        if not is_allin:
            shove_pct = min(shove_pct, OPEN_RANGE) if len(raises) == 1 else min(shove_pct, 12.0)
        elif len(raises) > 1 and stats[last][0] < 5:
            shove_pct = min(shove_pct, 15.0)  # a re-raise all-in from an unknown seat is strong
        shove_pct = max(2.0, shove_pct)

        if is_allin or to_call >= me.stack:
            k = 1 + len(others_in)
            eq = eq_multiway(hvr, shove_pct, k) if k > 1 else eq_vs_top(hvr[1], shove_pct)
            # Players still to act behind us may also come along: a small tax per live seat.
            for s in behind_me:
                eq -= 0.01 * _seat_call_prob(stats[s.seat], 0.5)
            villain = _biggest([raiser] + others_in)
            win, lose = spot.showdown_pts(villain)
            fold_pts = spot.fold_pts(last)
            ev_call = eq * win + (1.0 - eq) * lose - fold_pts
            if ev_call >= CALL_MARGIN + _premium(spot, fold_pts, len(others_in)):
                return _call_or_check(state)   # call; never turn a call into a stack-sized shove
            return _check_or_fold(state)

        # Normal raise, we are short: re-shove or fold. The raiser calls with the part of their
        # opening range that is in the Nash calling range (or at their observed rate); players
        # behind call at their observed / Nash rate; committed players call.
        _, call_pct = nash_ranges(eff, 1)
        prior_r = min(1.0, call_pct / OPEN_RANGE)
        callers = [(raiser, max(_seat_call_prob(stats[last], prior_r), 0.5 if committed(raiser) else 0.0),
                    min(OPEN_RANGE, max(2.0, call_pct)))]
        for s in others_in:
            callers.append((s, 0.9, max(5.0, min(OPEN_RANGE, _seat_raise_pct(stats[s.seat], OPEN_RANGE)))))
        for s in behind_me:
            c = _seat_call_prob(stats[s.seat], call_pct / 100.0)
            callers.append((s, c, max(2.0, 100.0 * c)))
        ev = _shove_ev(spot, hvr, callers, last)
        if ev >= SHOVE_MARGIN + _premium(spot, spot.fold_pts(last), len(others_in)):
            return _raise(state, 10**9)
        return _check_or_fold(state)

    # ---- deep, facing a raise: v0-nowar heuristic (3-bet war capped)
    n_raises = len(raises)
    if cls == 3:
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
        if to_call <= 6 * bb and n_raises == 1:
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
