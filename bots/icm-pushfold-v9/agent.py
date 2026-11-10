"""icm-pushfold-v9 - cap-floor-count-v6 (bot/ as of 2026-11-06 19:53) + the icm-pushfold-v7 short-stack module.

Preflop at <= 15 BB effective (unopened) or when the stack at risk is <= 18 BB (facing a raise / all-in):
table-driven ICM push/fold with per-seat call/raise frequencies kept in memory and a survival premium of
0.30 (strategy/06 S6.1, S6.2, S6.5; strategy/02 S2.5; tables from calc/i_pushfold_tables.py). Everything else
(deep preflop with the 3-bet war capped and no class-1 limps, selection, cap/floor/count postflop) is
cap-floor-count-v6 byte for byte, so an A/B against bot/ isolates the short-stack module.
Module history: bots/icm-pushfold-v7/BOT.md. Parent docstring follows.

cap-floor-count-v6 - v5 + no limping with class-1 hands (preflop tightening; VPIP 61% -> ~40%); v4a with the stricter one-pair value gate (p_best >= 0.75, eq >= 0.60); v3 + bet-size and persistence aware count (alpha 0.9/1.0/0.5, beta up to 0.8 for >=0.75-pot bets or repeated aggression), call margin 0.05

Preflop change (the only change vs the parent): facing a 3-bet or more, class-3 hands no longer
re-raise 3x without limit (two v0 copies escalate to all-in at 100 BB on hand 1; 59% of seats bust in
blind level 1 in the pool, see strategy/08-experiments.md 2026-11-06 cfc-v1-ab-pool). Now: QQ+ pairs shove,
TT-JJ call up to 30% of stack, 77-99 call up to 12%, everything else folds. Class-2 hands only call a
single open. Push/fold (<=12 BB) untouched.

Parent docstring follows.
cap-floor-count-v2 - "Cap, floor and count" with the count conditioned on the opponent's aggression.

v2 changes vs cap-floor-count (v1): (a) an opponent who bet/raised on the current street is read
as holding a made hand (pair+ using a hole card) with weight AGGR_ALPHA, uniform otherwise;
(b) value bets with one pair resume at v0 aggression (eq >= 0.55 and p_best >= 0.60);
(c) the call margin grows from 0.02 to 0.03.  Everything else identical to v1.

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

import csv
import gc
import os
import struct

import eval7
import numpy as np
import poker_agent_sdk
from poker_agent_sdk import Action, GameState, icm as icm_generic

RANKS = "23456789TJQKA"
RVAL = {r: i for i, r in enumerate(RANKS)}  # 0..12
SUITS = "cdhs"
DECK = [r + s for r in RANKS for s in SUITS]
CARD = {c: eval7.Card(c) for c in DECK}  # built once at import; act never constructs Cards

# Latency: the decision itself is ~20 us per live opponent, but a cyclic-GC pass landing inside `act`
# costs milliseconds. Import-time objects go to the permanent generation and collections become rare
# (v4b -> v5 is decision-identical; this is the only change).
gc.freeze()
gc.set_threshold(50000, 50, 50)

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


# ---------------------------------------------------------------- tunables (push/fold)
PUSH_MAX = 15.0        # BB: unopened pot at or below this -> shove or fold by the tables
RESHOVE_MAX = 18.0     # BB: facing a raise at or below this -> re-shove or fold by the tables
ALLIN_FRACTION = 0.6   # a raise this share of the raiser's stack (or more) is treated as a shove
COMMITTED = 0.3        # a player with this share of their stack in the pot is assumed to call
OPEN_RANGE = 25.0      # % of hands a non-all-in raiser is assumed to have opened with
PRIOR_HANDS = 10.0     # weight (in observed decisions) of the Nash prior for a seat's frequencies
PF_SHOVE_MARGIN = 0.0     # points: shove needs EV(shove) - EV(fold) >= this
PF_CALL_MARGIN = 0.0      # points: call needs EV(call) - EV(fold) >= this
# Survival premium (v3): ICM assumes equal skill, but a field of simple bots busts itself, so
# folding is worth more than ICM(fold) early. Required edge = PREMIUM * ICM(fold) * (n - 2) / 6,
# n = players remaining (0 heads-up, full with 8). Multiway all-ins pay it once per extra player.
PREMIUM = 0.30
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
            if ev >= PF_SHOVE_MARGIN + _premium(spot, spot.fold_pts(winner)) * 0.5:
                return _raise(state, 10**9)
            return _check_or_fold(state) if to_call > 0 else Action.check()
        # deep: cap-floor-count-v6 heuristic, unopened (no limping with class-1 hands)
        if cls == 3:
            return _raise(state, 3 * bb)
        if cls == 2:
            return _raise(state, 2.5 * bb)
        if to_call == 0:
            return Action.check()
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
            if ev_call >= PF_CALL_MARGIN + _premium(spot, fold_pts, len(others_in)):
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
        if ev >= PF_SHOVE_MARGIN + _premium(spot, spot.fold_pts(last), len(others_in)):
            return _raise(state, 10**9)
        return _check_or_fold(state)

    # ---- deep, facing a raise: cap-floor-count-v6 heuristic (3-bet war capped)
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
