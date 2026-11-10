"""Deep dive into the practice-round download: what do the winning teams actually DO?

Reads data/hands/practice-*.jsonl.gz (participant export: public events, our private cards) with the
standard library only, groups teams by points per table, and reports per group the decisions a bot
has to make: preflop action mix and open size, shoving / calling shoves by stack depth, c-bet and bet
sizing, fold-to-bet, bust timing, chip trajectory, and what hands reach showdown after an open.

Usage: python calc/j_practice_deepdive.py [path] [--max-tables N]
Writes calc/results/j_practice_deepdive.md.  Owner: Claude (keep-rule agent), 2026-11-06.
"""
from __future__ import annotations

import gzip
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

RANKS = "23456789TJQKA"
BETTING = {"fold", "check", "call", "raise"}
STACK_BANDS = [(0, 7, "<=7bb"), (7, 12, "7-12bb"), (12, 20, "12-20bb"), (20, 40, "20-40bb"), (40, 999, ">40bb")]
SIZE_BANDS = [(0, 2.2, "<=2.2x"), (2.2, 3.5, "2.2-3.5x"), (3.5, 6, "3.5-6x"), (6, 1e9, ">6x")]
POT_BANDS = [(0, 0.4, "<0.4 pot"), (0.4, 0.7, "0.4-0.7"), (0.7, 1.1, "0.7-1.1"), (1.1, 1e9, ">1.1 pot")]


def band(x, bands):
    for lo, hi, name in bands:
        if lo <= x < hi:
            return name
    return bands[-1][2]


def hand2_class(cards):
    r = sorted((RANKS.index(c[0]) for c in cards), reverse=True)
    suited = cards[0][1] == cards[1][1]
    if r[0] == r[1]:
        return "pair"
    if r[0] >= 8 and r[1] >= 8:
        return "two broadway"
    if r[0] == 12:
        return "ace-x"
    if suited:
        return "suited other"
    return "other"


class Stats:
    def __init__(self):
        self.c = Counter()
        self.lists = defaultdict(list)

    def add(self, key, n=1):
        self.c[key] += n

    def push(self, key, value):
        self.lists[key].append(value)


def analyze(path: Path, max_tables: int | None = None):
    team_pts = defaultdict(list)  # entry -> list of points per scored table
    per_team = defaultdict(Stats)
    names = {}
    opener = gzip.open if path.suffix == ".gz" else open
    n_tables = 0
    with opener(path, "rt", encoding="utf-8") as f:
        header = json.loads(f.readline())
        names = {e["entry_id"]: e["team_name"] for e in header["entries"]}
        you = header["you"]
        while True:
            line = f.readline()
            if not line.strip():
                break
            table = json.loads(line)
            f.readline()  # private record, unused here
            n_tables += 1
            if max_tables and n_tables > max_tables:
                break
            seats = table["seats"]
            fillers = table["fillers"]
            hands = table["hands"]
            if not hands:
                continue
            last = hands[-1]
            for s, entry in enumerate(seats):
                if not fillers[s]:
                    team_pts[entry].append(last["equity_after"][s])
            n_seats = len(seats)
            busted = set(s for s in range(n_seats) if hands[0]["stacks_before"][s] == 0)
            for h in hands:
                sb, bb, ante = h["blinds"]
                level = min(12, (h["hand"] - 1) // 20 + 1)
                stacks = list(h["stacks_before"])
                alive = [s for s in range(n_seats) if stacks[s] > 0]
                street_contrib = [0] * n_seats
                total_contrib = [0] * n_seats
                street = 0  # 0 preflop, 1 flop, 2 turn, 3 river
                raises_this_street = 0
                last_raiser = None
                pre_aggressor = None
                checked_to = True  # nobody bet yet this street
                acted_pre = set()
                allin_open = False  # a raise all-in is pending on this street
                shown = {}
                exposed = {}
                for e in h["events"]:
                    k = e["kind"]
                    s = e.get("seat")
                    if k == "board":
                        street += 1
                        street_contrib = [0] * n_seats
                        raises_this_street = 0
                        checked_to = True
                        allin_open = False
                        continue
                    if k in ("blind", "ante"):
                        street_contrib[s] += e["amount"]
                        total_contrib[s] += e["amount"]
                        continue
                    if k == "reveal":
                        exposed[s] = e["cards"][0]
                        continue
                    if k == "show":
                        shown[s] = e["cards"]
                        continue
                    if k not in BETTING:
                        continue
                    st = per_team[seats[s]]
                    pot = sum(total_contrib)
                    my_stack = stacks[s] - total_contrib[s]
                    stack_bb = (stacks[s]) / bb
                    sband = band(stack_bb, STACK_BANDS)
                    to_call = max(street_contrib) - street_contrib[s]
                    if street == 0:
                        if s not in acted_pre:
                            acted_pre.add(s)
                            st.add(("pre_hands", level))
                            st.add("pre_hands_total")
                            st.add(("pre_hands_band", sband))
                        if k == "fold":
                            st.add("pre_fold")
                            if raises_this_street == 0:
                                st.add("pre_fold_unopened")
                            if allin_open:
                                st.add(("face_shove", sband, "fold"))
                        elif k == "call":
                            if raises_this_street == 0:
                                st.add("pre_limp")
                            else:
                                st.add("pre_call_raise")
                            if allin_open:
                                st.add(("face_shove", sband, "call"))
                            st.add("pre_vpip")
                        elif k == "raise":
                            amt = e["amount"]
                            st.add("pre_vpip")
                            is_allin = amt >= stacks[s] - 0  # total this street == whole stack preflop
                            if raises_this_street == 0:
                                st.add("pre_open")
                                if not is_allin:
                                    st.push("open_size_bb", amt / bb)
                                    st.add(("open_size", band(amt / bb, SIZE_BANDS)))
                                else:
                                    st.add("open_shove")
                            elif raises_this_street == 1:
                                st.add("pre_3bet")
                            else:
                                st.add("pre_4bet_plus")
                            if is_allin:
                                st.add(("shove", sband))
                                st.add("shove_pre")
                                allin_open = True
                            if allin_open and not is_allin:
                                pass
                            raises_this_street += 1
                            last_raiser = s
                            pre_aggressor = s
                        elif k == "check":
                            st.add("pre_check")
                    else:
                        st.add("post_decisions")
                        facing_bet = to_call > 0
                        if k == "raise":
                            amt = e["amount"]
                            added = amt - street_contrib[s]
                            is_allin = added >= my_stack - 1
                            if not facing_bet:
                                st.add("post_bet")
                                frac = (amt - street_contrib[s]) / max(pot, 1)
                                st.add(("bet_size", band(frac, POT_BANDS)))
                                if is_allin:
                                    st.add("post_bet_allin")
                                if street == 1 and pre_aggressor == s:
                                    st.add("cbet_yes")
                            else:
                                st.add("post_raise")
                            if is_allin:
                                st.add(("shove", sband))
                                st.add("shove_post")
                            raises_this_street += 1
                            checked_to = False
                            last_raiser = s
                        elif k == "check":
                            st.add("post_check")
                            if street == 1 and pre_aggressor == s and not facing_bet:
                                st.add("cbet_no")
                        elif k == "call":
                            st.add("post_call")
                            st.add("face_bet")
                            st.add("face_bet_call")
                        elif k == "fold":
                            st.add("post_fold")
                            st.add("face_bet")
                            st.add("face_bet_fold")
                        if k == "raise" and facing_bet:
                            st.add("face_bet")
                            st.add("face_bet_raise")
                    # chips
                    if k == "call":
                        street_contrib[s] += e["amount"]
                        total_contrib[s] += e["amount"]
                    elif k == "raise":
                        added = e["amount"] - street_contrib[s]
                        street_contrib[s] = e["amount"]
                        total_contrib[s] += added
                # showdown hands
                for s, cards in shown.items():
                    if len(cards) == 2:
                        st = per_team[seats[s]]
                        st.add(("shown", hand2_class(cards)))
                        st.add("shown_total")
                        if pre_aggressor == s:
                            st.add(("shown_after_open", hand2_class(cards)))
                            st.add("shown_after_open_total")
                        if s in exposed:
                            other = [c for c in cards if c != exposed[s]]
                            if other:
                                hi = RANKS.index(exposed[s][0]) > RANKS.index(other[0][0])
                                st.add("expose_higher" if hi else "expose_lower")
                # busts and trajectory
                for s in alive:
                    if h["stacks_after"][s] == 0:
                        per_team[seats[s]].add(("bust_level", level))
                        per_team[seats[s]].push("bust_hand", h["hand"])
                        per_team[seats[s]].add("busts")
                if h["hand"] in (21, 41, 61, 81, 101):
                    for s in alive:
                        per_team[seats[s]].push(("stack_at", h["hand"]), stacks[s] / 2000)
            # survival
            for s, entry in enumerate(seats):
                if not fillers[s]:
                    per_team[entry].add("tables")
                    if last["stacks_after"][s] > 0:
                        per_team[entry].add("alive_at_end")
    return names, you, team_pts, per_team, n_tables


def pct(c, num, den):
    d = c[den] if isinstance(den, str) else den
    return f"{100 * c[num] / d:.0f}%" if d else "-"


def group_report(label, teams, per_team, team_pts):
    c = Counter()
    lists = defaultdict(list)
    for t in teams:
        c.update(per_team[t].c)
        for k, v in per_team[t].lists.items():
            lists[k].extend(v)
    pts = statistics.mean(statistics.mean(team_pts[t]) for t in teams) if teams else 0
    rows = {}
    rows["pts/table"] = f"{pts:.1f}"
    rows["teams"] = str(len(teams))
    ph = c["pre_hands_total"]
    rows["VPIP"] = pct(c, "pre_vpip", ph)
    rows["open-raise / hand"] = pct(c, "pre_open", ph)
    rows["limp / hand"] = pct(c, "pre_limp", ph)
    rows["call-raise / hand"] = pct(c, "pre_call_raise", ph)
    rows["3-bet / hand"] = pct(c, "pre_3bet", ph)
    rows["4-bet+ / hand"] = pct(c, "pre_4bet_plus", ph)
    rows["fold unopened / hand"] = pct(c, "pre_fold_unopened", ph)
    rows["open size median (x BB)"] = f"{statistics.median(lists['open_size_bb']):.1f}" if lists["open_size_bb"] else "-"
    n_open = sum(c[("open_size", b)] for _, _, b in SIZE_BANDS)
    for _, _, b in SIZE_BANDS:
        rows[f"open size {b}"] = pct(c, ("open_size", b), n_open)
    rows["open = shove (of opens)"] = pct(c, "open_shove", c["pre_open"])
    for _, _, b in STACK_BANDS:
        rows[f"shove / hand at {b}"] = pct(c, ("shove", b), c[("pre_hands_band", b)])
    for _, _, b in STACK_BANDS:
        n = c[("face_shove", b, "fold")] + c[("face_shove", b, "call")]
        rows[f"call shove at {b}"] = pct(c, ("face_shove", b, "call"), n) + f" (n={n})"
    rows["c-bet flop (as aggressor)"] = pct(c, "cbet_yes", c["cbet_yes"] + c["cbet_no"])
    pd = c["post_decisions"]
    rows["postflop bet / decision"] = pct(c, "post_bet", pd)
    rows["postflop raise / decision"] = pct(c, "post_raise", pd)
    rows["fold facing bet"] = pct(c, "face_bet_fold", "face_bet")
    rows["raise facing bet"] = pct(c, "face_bet_raise", "face_bet")
    nb = sum(c[("bet_size", b)] for _, _, b in POT_BANDS)
    for _, _, b in POT_BANDS:
        rows[f"bet size {b}"] = pct(c, ("bet_size", b), nb)
    rows["bets that are all-in"] = pct(c, "post_bet_allin", "post_bet")
    rows["shoves preflop : postflop"] = f"{c['shove_pre']} : {c['shove_post']}"
    rows["survive to table end"] = pct(c, "alive_at_end", "tables")
    rows["bust hand median"] = f"{statistics.median(lists['bust_hand']):.0f}" if lists["bust_hand"] else "-"
    for lv in (1, 2, 3, 4, 5):
        rows[f"busts in level {lv}"] = pct(c, ("bust_level", lv), "busts")
    rows["busts level 6+"] = pct(c, None, 1) if False else f"{100 * sum(c[('bust_level', l)] for l in range(6, 13)) / max(c['busts'], 1):.0f}%"
    for hn in (21, 41, 61, 81, 101):
        v = lists[("stack_at", hn)]
        rows[f"mean stack at hand {hn} (x start, survivors)"] = f"{statistics.mean(v):.2f}" if v else "-"
    for cls in ("pair", "two broadway", "ace-x", "suited other", "other"):
        rows[f"shown after own open: {cls}"] = pct(c, ("shown_after_open", cls), "shown_after_open_total")
    for cls in ("pair", "two broadway", "ace-x", "suited other", "other"):
        rows[f"shown (all): {cls}"] = pct(c, ("shown", cls), "shown_total")
    rows["exposed the higher kept card"] = pct(c, "expose_higher", c["expose_higher"] + c["expose_lower"])
    return rows


def main():
    argv = sys.argv[1:]
    max_tables = None
    if "--max-tables" in argv:
        i = argv.index("--max-tables")
        max_tables = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    args = [a for a in argv if not a.startswith("--")]
    path = Path(args[0]) if args else next(Path("data/hands").glob("practice-*.jsonl.gz"))
    names, you, team_pts, per_team, n_tables = analyze(path, max_tables)
    ranking = sorted(((statistics.mean(v), t) for t, v in team_pts.items() if len(v) >= 20), reverse=True)
    top10 = [t for _, t in ranking[:10]]
    top30 = [t for _, t in ranking[:30]]
    allt = [t for _, t in ranking]
    bottom30 = [t for _, t in ranking[-30:]]
    groups = [("top 10", top10), ("top 30", top30), ("all", allt), ("bottom 30", bottom30), ("us (v0)", [you])]
    reports = [(g, group_report(g, teams, per_team, team_pts)) for g, teams in groups]
    keys = list(reports[0][1].keys())
    lines = [f"# Practice round deep dive — `{path.name}`, {n_tables} tables, {len(ranking)} teams with >= 20 tables", ""]
    lines.append("Pooled over the group's seat-hands (not medians of teams). Preflop rates are per hand in which the seat acted.")
    lines.append("")
    lines.append("| metric | " + " | ".join(g for g, _ in reports) + " |")
    lines.append("|---|" + "---|" * len(reports))
    for k in keys:
        lines.append(f"| {k} | " + " | ".join(r[k] for _, r in reports) + " |")
    lines.append("")
    lines.append("## Top 10 teams")
    lines.append("")
    lines.append("| team | pts/table | tables | VPIP | open/hand | open size | 3-bet | shove/hand | c-bet | fold v bet | survive | bust median |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for p, t in ranking[:10]:
        r = group_report(t, [t], per_team, team_pts)
        lines.append(f"| {names.get(t, t)} | {p:.2f} | {len(team_pts[t])} | {r['VPIP']} | {r['open-raise / hand']} | {r['open size median (x BB)']} | {r['3-bet / hand']} | "
                     f"{pct(per_team[t].c, 'shove_pre', 'pre_hands_total')} | {r['c-bet flop (as aggressor)']} | {r['fold facing bet']} | {r['survive to table end']} | {r['bust hand median']} |")
    text = "\n".join(lines) + "\n"
    out = Path(__file__).parent / "results" / "j_practice_deepdive.md"
    out.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
