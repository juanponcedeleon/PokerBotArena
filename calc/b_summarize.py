"""Summarize results/b_preflop_classes.csv into markdown tables for strategy/02-preflop.md."""
import csv
from collections import defaultdict

rows = list(csv.DictReader(open("results/b_preflop_classes.csv")))
for r in rows:
    for k in ("eq_vs1", "eq_vs3", "eq_vs7"):
        r[k] = float(r[k])
n = len(rows)
rows.sort(key=lambda r: -r["eq_vs7"])
for i, r in enumerate(rows):
    r["pct7"] = (i + 0.5) / n * 100
rows1 = sorted(rows, key=lambda r: -r["eq_vs1"])
for i, r in enumerate(rows1):
    r["pct1"] = (i + 0.5) / n * 100

out = []
out.append(f"Classes: {n}; trials per class: {rows[0]['trials']}; equity = pot share, all-in preflop, "
           f"oracle best-2 for everyone (ranking is what matters).\n")
out.append("### Top 40 by 8-way equity\n")
out.append("| rank | hand | structure | vs 1 | vs 3 | vs 7 |\n|---|---|---|---|---|---|")
for i, r in enumerate(rows[:40]):
    out.append(f"| {i+1} | {r['label']} | {r['structure']} | {r['eq_vs1']:.1%} | {r['eq_vs3']:.1%} | {r['eq_vs7']:.1%} |")
out.append("\n### Bottom 15 by 8-way equity\n")
out.append("| rank | hand | structure | vs 1 | vs 3 | vs 7 |\n|---|---|---|---|---|---|")
for i, r in enumerate(rows[-15:]):
    out.append(f"| {n-15+i+1} | {r['label']} | {r['structure']} | {r['eq_vs1']:.1%} | {r['eq_vs3']:.1%} | {r['eq_vs7']:.1%} |")

out.append("\n### Average equity by structure\n")
out.append("| structure | classes | avg vs 1 | avg vs 3 | avg vs 7 |\n|---|---|---|---|---|")
by = defaultdict(list)
for r in rows:
    by[r["structure"]].append(r)
for s, rs in sorted(by.items(), key=lambda kv: -sum(r["eq_vs7"] for r in kv[1]) / len(kv[1])):
    out.append(f"| {s} | {len(rs)} | {sum(r['eq_vs1'] for r in rs)/len(rs):.1%} | "
               f"{sum(r['eq_vs3'] for r in rs)/len(rs):.1%} | {sum(r['eq_vs7'] for r in rs)/len(rs):.1%} |")

out.append("\n### Selected comparisons (what the third card is worth)\n")
want = ["AAA", "AAKr", "AAKs", "AA2r", "KKK", "KKAr", "KKAs", "KK2r", "QQQ", "QQAr", "QQ7r", "888", "88Ar", "88As", "882r",
        "222", "22Ar", "AKQr", "AKQsss", "AKQ-AKs", "AK2r", "AK2-AKs", "AK2-A2s", "JT9r", "JT9sss", "JT9-JTs",
        "KQJsss", "KQJr", "T98sss", "765sss", "765r", "A72r", "A72-A7s", "A72-72s", "A72sss", "K72r", "952r", "732r", "742sss"]
idx = {r["label"]: r for r in rows}
out.append("| hand | structure | vs 1 | vs 3 | vs 7 | percentile (8-way) |\n|---|---|---|---|---|---|")
for w in want:
    r = idx.get(w)
    if r:
        out.append(f"| {w} | {r['structure']} | {r['eq_vs1']:.1%} | {r['eq_vs3']:.1%} | {r['eq_vs7']:.1%} | top {r['pct7']:.0f}% |")

out.append("\n### Heads-up equity thresholds (for push/fold work)\n")
out.append("| top X% of classes (by HU equity) | HU equity at cutoff | example hand at cutoff |\n|---|---|---|")
for pct in (5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 100):
    i = min(n - 1, int(n * pct / 100) - 1)
    r = rows1[i]
    out.append(f"| {pct}% | {r['eq_vs1']:.1%} | {r['label']} |")

# weighted by frequency: suit patterns are not equally likely. Weights per class (combos out of 22100):
def combos(label, structure):
    if structure == "trips":
        return 4
    if structure == "pair+kicker":
        return 6 * 2  # pair (6 suit combos) x kicker suit not matching either pair suit: 4 - 2 = 2
    if structure == "pair+kicker suited":
        return 6 * 2
    if structure == "rainbow":
        return 4 * 3 * 2
    if structure.startswith("two suited"):
        return 4 * 3
    if structure == "three suited":
        return 4
    raise ValueError(structure)
tot = sum(combos(r["label"], r["structure"]) for r in rows)
out.append(f"\n(Class weights check: {tot} combos, expect 22100.)\n")
# frequency-weighted percentile by HU equity
acc = 0
out.append("### Frequency-weighted hand ranking (what % of DEALT hands are at least this strong, HU equity)\n")
out.append("| hand | HU equity | % of dealt hands at least this strong |\n|---|---|---|")
marks = [0.02, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.75]
mi = 0
for r in rows1:
    acc += combos(r["label"], r["structure"]) / tot
    while mi < len(marks) and acc >= marks[mi]:
        out.append(f"| {r['label']} | {r['eq_vs1']:.1%} | {marks[mi]:.0%} |")
        mi += 1
open("results/b_preflop_summary.md", "w").write("\n".join(out))
print("\n".join(out))
