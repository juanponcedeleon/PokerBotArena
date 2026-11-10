"""icm-pushfold-v10 - fp-v3 + the icm-pushfold-v7 short-stack module.

Preflop at <= 15 BB effective (unopened) or when the stack at risk is <= 18 BB (facing a raise / all-in):
table-driven ICM push/fold with per-seat call/raise frequencies kept in memory and a survival premium of
0.30 (strategy/06 S6.1, S6.2, S6.5; strategy/02 S2.5; tables from calc/i_pushfold_tables.py). Everything else
(fp-v2's percentile preflop, keep rule v2 + non-pairing exposure, tiered postflop) is fp-v3 byte for byte,
so an A/B against bots/fp-v3 isolates the short-stack module. Module history: bots/icm-pushfold-v7/BOT.md.
Parent docstring follows.

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
import os
import struct
from pathlib import Path

import eval7
import numpy as np
import poker_agent_sdk
from poker_agent_sdk import Action, GameState, icm as icm_generic

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


def decide(state: GameState, stats) -> Action:
    if state.phase == "select":
        return select(state)
    if state.phase != "betting":
        first = state.legal_actions[0]
        return Action(first.kind, first.min_amount)
    if not state.board:
        return preflop(state, stats)
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


def preflop_deep(state: GameState) -> Action:
    """fp-v3 preflop, used above 15 BB effective / when the stack at risk is above 18 BB."""
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
        return preflop_deep(state)  # fp-v3 preflop

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

    # ---- deep, facing a raise: fp-v3 preflop
    return preflop_deep(state)
    if cls == 2:
        if to_call <= 6 * bb and n_raises == 1:
            return _call_or_check(state)
        return _check_or_fold(state)
    return _check_or_fold(state)



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


def postflop(state: GameState) -> Action:
    board = list(state.board)
    hole = list(state.cards)
    me = state.seats[state.seat]
    bb = state.blinds.big_blind or 1
    pot = max(state.pot, 1)
    to_call = state.to_call
    stack = me.stack
    stack_bb = (stack + me.bet) / bb
    street = len(board)  # 3 flop, 4 turn, 5 river
    n_opp = sum(1 for s in state.seats if s.seat != state.seat and s.status in ("active", "all_in"))
    tier, cat, fd, oesd, uses_hole = hand_tier(board, hole, street)
    hr = [RVAL[c[0]] for c in hole]
    br = [RVAL[c[0]] for c in board]
    our_pair_rank = None
    if cat == 1 and uses_hole:
        hits = [r for r in hr if r in br]
        our_pair_rank = hits[0] if hits else hr[0]
    shown_pair, above = _opp_scare(state, board, our_pair_rank)
    if tier == 3 and above:
        tier = 2  # someone publicly holds a higher pair
    # who was the preflop aggressor? (last raise before the first board event)
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

    # ---------------- tier 4: value --------------------------------------------------------
    if tier == 4:
        if not facing:
            return _raise_to(state, me.bet + 0.65 * pot) if not short else _shove(state)
        if allin_call or short or to_call >= 0.4 * stack:
            return _call(state)
        return _raise_to(state, me.bet + to_call + to_call + 0.7 * pot)

    # ---------------- tier 3: top pair / two pair ---------------------------------------
    if tier == 3:
        if short:
            return _shove(state) if not facing else _call(state)
        if not facing:
            if street == 5 and (n_opp >= 2 or shown_pair):
                return Action.check()
            return _raise_to(state, me.bet + 0.55 * pot)
        if allin_call:
            return _call(state) if (to_call <= 0.6 * pot and stack_bb <= 20) else Action.fold()
        limit = 0.65 if n_opp == 1 else 0.45
        if street == 5:
            limit = 0.5 if n_opp == 1 else 0.35
        # A raise against our bet: one pair folds unless cheap.
        if bet_this_street and we_bet_this_street(state):
            limit = min(limit, 0.4)
        if bet_frac <= limit and to_call <= 0.30 * (stack + me.bet):
            return _call(state)
        return _check_fold(state)

    # ---------------- tier 2: weak pair or strong draw ----------------------------------
    if tier == 2:
        has_pair = cat >= 1 and uses_hole
        if not facing:
            if street < 5 and n_opp == 1 and we_pfr and not shown_pair:
                return _raise_to(state, me.bet + 0.55 * pot)  # c-bet / semi-bluff
            if street < 5 and (fd or oesd) and n_opp == 1 and not shown_pair and street == 3:
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
            if bet_frac <= price and to_call <= 0.15 * (stack + me.bet):
                return _call(state)
        return _check_fold(state)

    # ---------------- tier 1: air ------------------------------------------------------------
    if not facing:
        if street == 3 and we_pfr and n_opp == 1 and not shown_pair:
            return _raise_to(state, me.bet + 0.55 * pot)
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
