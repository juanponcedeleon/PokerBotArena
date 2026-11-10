"""Behavioural statistics per bot from hand logs: the numbers strategy/05-opponent-modeling.md
wants, computed the same way from an arena `log.jsonl.gz` (every card) and from a real
tournament download (public cards only). Standard library only.

Per bot: hands, VPIP, PFR, 3-bet, postflop aggression, went-to-showdown, won-at-showdown,
shoves (The Shover), empty bluffs, calling-station share, exposure habits (rank of the exposed
card, pairs the board, exposes the higher of the two kept when both became known), discard habits
(arena logs only: which of the three dealt cards goes), busts by blind level, automatic actions.
"""

from __future__ import annotations

import gzip
import json
from collections import Counter, defaultdict
from collections.abc import Iterator
from pathlib import Path
from typing import Any

RANKS = "23456789TJQKA"
BETTING = {"fold", "check", "call", "raise"}


def rank(card: str) -> int:
    return RANKS.index(card[0])


def read_tables(path: Path) -> Iterator[dict[str, Any]]:
    """Yield normalized tables: {labels, fillers, hands, own: {seat, automatic} | None, raw: bool}."""
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as source:
        first = source.readline()
        if not first.strip():
            return
        record = json.loads(first)
        if "tournament_id" in record:  # participant download: header, then public/private pairs
            teams = {e["entry_id"]: e["team_name"] for e in record["entries"]}
            while True:
                public = source.readline()
                if not public.strip():
                    return
                table = json.loads(public)
                own = json.loads(source.readline())["you"]
                yield {
                    "labels": [teams.get(s, s) for s in table["seats"]],
                    "fillers": table["fillers"],
                    "payouts": table.get("payouts", []),
                    "hands": table["hands"],
                    "own": own,
                    "raw": False,
                }
        else:  # arena raw log: one table per line
            for line in [first] + source.readlines():
                if not line.strip():
                    continue
                table = json.loads(line)
                yield {
                    "labels": table.get("labels") or table["seats"],
                    "fillers": table["fillers"],
                    "payouts": table.get("payouts", []),
                    "hands": table["hands"],
                    "own": None,
                    "raw": True,
                }


class BotStats:
    def __init__(self) -> None:
        self.c: Counter[str] = Counter()
        self.exposed_ranks: Counter[int] = Counter()
        self.discard_position: Counter[str] = Counter()  # lowest / middle / highest of the 3
        self.bust_levels: Counter[int] = Counter()
        self.points: list[float] = []
        self.points_filler_excluded = 0

    def rate(self, num: str, den: str) -> float | None:
        return self.c[num] / self.c[den] if self.c[den] else None


def analyze_table(table: dict[str, Any], stats: dict[str, BotStats]) -> None:
    labels, fillers, hands = table["labels"], table["fillers"], table["hands"]
    own = table["own"]
    automatic = defaultdict(set)
    if own:
        for hand_number, index in own.get("automatic", []):
            automatic[hand_number].add((own["seat"], index))
    for label in set(labels):
        stats.setdefault(label, BotStats()).c["tables"] += 1
    last = hands[-1] if hands else None
    if last:
        for seat, label in enumerate(labels):
            if not fillers[seat]:
                stats[label].points.append(last["equity_after"][seat])
    for hand in hands:
        level = max(1, hand["blinds"][1] // 20) if hand["blinds"][1] else 1
        events = hand["events"]
        seats_in = [s for s, stack in enumerate(hand["stacks_before"]) if stack > 0]
        for s in seats_in:
            stats[labels[s]].c["hands"] += 1
        street = 0
        board: list[str] = []
        folded: set[int] = set()
        preflop_raise_seen = False
        vpip: set[int] = set()
        pfr: set[int] = set()
        threebet: set[int] = set()
        saw_flop: set[int] = set()
        showed: dict[int, list[str]] = {}
        revealed: dict[int, str] = {}
        reveal_board: dict[int, list[str]] = {}
        for index, event in enumerate(events):
            kind = event["kind"]
            seat = event.get("seat")
            if kind == "board":
                if street == 0:
                    saw_flop = set(seats_in) - folded
                street += 1
                board += event["cards"]
                continue
            if seat is None:
                continue
            st = stats[labels[seat]]
            if kind in BETTING:
                st.c["decisions"] += 1
                st.c[f"act_{kind}"] += 1
                if event.get("automatic") or (seat, index) in automatic.get(hand["hand"], set()):
                    st.c["automatic"] += 1
                if street == 0:
                    if kind in ("call", "raise") and event.get("amount", 0) > 0:
                        vpip.add(seat)
                    if kind == "raise":
                        if preflop_raise_seen:
                            threebet.add(seat)
                        preflop_raise_seen = True
                        pfr.add(seat)
                else:
                    st.c["post_decisions"] += 1
                    st.c[f"post_{kind}"] += 1
                if kind == "fold":
                    folded.add(seat)
            elif kind == "reveal":
                card = event["cards"][0]
                revealed[seat] = card
                reveal_board[seat] = list(board)
                st.exposed_ranks[rank(card)] += 1
                st.c["reveals"] += 1
                if any(rank(b) == rank(card) for b in board):
                    st.c["reveal_pairs_board"] += 1
            elif kind == "show":
                showed[seat] = list(event["cards"])
            elif kind == "prize_the_shover":
                st.c["shoves"] += 1
            elif kind == "prize_the_empty_bluffer":
                st.c["empty_bluffs"] += 1
        for seat in seats_in:
            st = stats[labels[seat]]
            st.c["vpip"] += seat in vpip
            st.c["pfr"] += seat in pfr
            st.c["threebet"] += seat in threebet
            st.c["saw_flop"] += seat in saw_flop
            net = hand["stacks_after"][seat] - hand["stacks_before"][seat]
            if seat in showed:
                st.c["showdowns"] += 1
                st.c["won_showdown"] += net > 0
                if seat in revealed and len(showed[seat]) == 2:
                    exposed = revealed[seat]
                    hidden = [c for c in showed[seat] if c != exposed]
                    if hidden:
                        hidden_card = hidden[0]
                        st.c["both_known"] += 1
                        if rank(exposed) > rank(hidden_card):
                            st.c["exposed_higher"] += 1
                        elif rank(exposed) == rank(hidden_card):
                            st.c["exposed_equal"] += 1
                        flop = reveal_board[seat]
                        e_pairs = any(rank(b) == rank(exposed) for b in flop)
                        h_pairs = any(rank(b) == rank(hidden_card) for b in flop)
                        if e_pairs != h_pairs:
                            st.c["one_pairs_board"] += 1
                            st.c["exposed_the_pairing_card"] += e_pairs
            if net > 0 and seat not in showed:
                st.c["won_without_showdown"] += 1
            if hand["stacks_before"][seat] > 0 and hand["stacks_after"][seat] == 0:
                st.bust_levels[level] += 1
                st.c["busts"] += 1
        if table["raw"]:
            dealt = hand["cards"]
            for event in hand.get("sealed", []):
                if event["kind"] == "discarded" and event.get("seat") is not None:
                    seat = event["seat"]
                    three = dealt[seat]
                    if len(three) == 3:
                        order = sorted(three, key=rank)
                        pos = order.index(event["cards"][0])
                        stats[labels[seat]].discard_position[["lowest", "middle", "highest"][pos]] += 1


def pct(value: float | None) -> str:
    return "-" if value is None else f"{100 * value:.0f}%"


def analyze(path: Path) -> tuple[str, dict[str, Any]]:
    stats: dict[str, BotStats] = {}
    tables = 0
    for table in read_tables(path):
        tables += 1
        analyze_table(table, stats)
    data: dict[str, Any] = {}
    for label, st in stats.items():
        c = st.c
        exposed_total = sum(st.exposed_ranks.values()) or 1
        data[label] = {
            "tables": c["tables"],
            "hands": c["hands"],
            "avg_points": sum(st.points) / len(st.points) if st.points else None,
            "vpip": st.rate("vpip", "hands"),
            "pfr": st.rate("pfr", "hands"),
            "threebet": st.rate("threebet", "hands"),
            "saw_flop": st.rate("saw_flop", "hands"),
            "post_aggression": (c["post_raise"] / c["post_decisions"]) if c["post_decisions"] else None,
            "post_fold": (c["post_fold"] / c["post_decisions"]) if c["post_decisions"] else None,
            "wtsd": st.rate("showdowns", "saw_flop"),
            "won_sd": st.rate("won_showdown", "showdowns"),
            "won_no_sd_per_hand": st.rate("won_without_showdown", "hands"),
            "shoves_per_100": 100 * c["shoves"] / c["hands"] if c["hands"] else None,
            "empty_bluffs": c["empty_bluffs"],
            "calling_station": (c["act_call"] / c["decisions"]) if c["decisions"] else None,
            "automatic_share": st.rate("automatic", "decisions"),
            "reveal_pairs_board": st.rate("reveal_pairs_board", "reveals"),
            "exposed_higher": st.rate("exposed_higher", "both_known"),
            "exposed_the_pairing_card": st.rate("exposed_the_pairing_card", "one_pairs_board"),
            "exposed_rank_low_share": sum(v for r, v in st.exposed_ranks.items() if r <= 3) / exposed_total if c["reveals"] else None,
            "exposed_rank_dist": {RANKS[r]: v for r, v in sorted(st.exposed_ranks.items())},
            "discard_position": dict(st.discard_position),
            "busts_by_level": dict(sorted(st.bust_levels.items())),
            "decisions": c["decisions"],
        }
    order = sorted(data, key=lambda k: -(data[k]["avg_points"] or 0))
    lines = [
        f"# Behaviour from `{path.name}` — {tables} tables",
        "",
        "| bot | hands | pts | VPIP | PFR | 3bet | saw flop | post agg | post fold | WTSD | W$SD | shove/100 | call share | auto | expose pairs board | expose higher | expose pairing card | expose 2-5 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for label in order:
        d = data[label]
        lines.append(
            f"| **{label}** | {d['hands']} | {'-' if d['avg_points'] is None else f'{d["avg_points"]:.2f}'} | {pct(d['vpip'])} | {pct(d['pfr'])} | {pct(d['threebet'])} | "
            f"{pct(d['saw_flop'])} | {pct(d['post_aggression'])} | {pct(d['post_fold'])} | {pct(d['wtsd'])} | {pct(d['won_sd'])} | "
            f"{'-' if d['shoves_per_100'] is None else f'{d["shoves_per_100"]:.1f}'} | {pct(d['calling_station'])} | {pct(d['automatic_share'])} | "
            f"{pct(d['reveal_pairs_board'])} | {pct(d['exposed_higher'])} | {pct(d['exposed_the_pairing_card'])} | {pct(d['exposed_rank_low_share'])} |"
        )
    lines += ["", "Definitions: VPIP/PFR/3bet per hand dealt; post agg = raises / postflop decisions; WTSD = showdowns / flops seen; "
              "W$SD = showdowns with a chip gain; call share = Calling Station metric; auto = decisions the platform played for the bot "
              "(only the hero's in a tournament download); expose higher = exposed card outranks the hidden one when both became known; "
              "expose pairing card = when exactly one kept card paired the flop, the exposed one was it.", ""]
    raw_any = any(d["discard_position"] for d in data.values())
    if raw_any:
        lines += ["Discard position among the three dealt cards (arena logs only):", "", "| bot | lowest | middle | highest | busts by level |", "|---|---|---|---|---|"]
        for label in order:
            d = data[label]
            dp = d["discard_position"]
            tot = sum(dp.values()) or 1
            lines.append(f"| {label} | {pct(dp.get('lowest', 0) / tot)} | {pct(dp.get('middle', 0) / tot)} | {pct(dp.get('highest', 0) / tot)} | {d['busts_by_level']} |")
    return "\n".join(lines) + "\n", data
