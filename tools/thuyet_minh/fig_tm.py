"""Figure 2.1 of the system description: the 10 pipeline steps with the real counts of both cases.

Run with the Python that has matplotlib:  C:/Python314/python.exe -X utf8 tools/thuyet_minh/fig_tm.py <facts.json> <out.png>
`facts.json` is written by build_tm.py (counts per step and case).
"""
import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

facts = json.load(open(sys.argv[1], encoding="utf-8"))
steps = facts["steps"]          # list of {"n", "name", "title", "a", "b"}
fig, ax = plt.subplots(figsize=(16, 9.2), dpi=170)
ax.set_xlim(0, 100)
ax.set_ylim(0, 58)
ax.axis("off")
plt.rcParams["font.family"] = "DejaVu Sans"

BLUE, GREEN, AMBER, INK, GREY = "#1d4e89", "#2d6a4f", "#b7791f", "#1f2937", "#6b7280"
w, h = 18, 21.5
xs = [1.5 + i * 19.6 for i in range(5)]
rows = [33.5, 5.5]
for i, s in enumerate(steps):
    r, c = divmod(i, 5)
    x, y = xs[c], rows[r]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=1.2",
                                fc="#f4f8fb", ec=BLUE, lw=1.6))
    ax.text(x + 1, y + h - 2.2, f"{s['n']}", fontsize=17, fontweight="bold", color=BLUE, va="center")
    ax.text(x + (4.6 if s["n"] >= 10 else 3.6), y + h - 2.2, s["title"], fontsize=9.6, fontweight="bold", color=INK, va="center", wrap=True)
    ax.text(x + 1, y + h - 5.0, s["name"], fontsize=7.4, color=GREY, family="monospace", va="center")
    ax.plot([x + 0.8, x + w - 0.8], [y + h - 6.6, y + h - 6.6], color="#cbd5e1", lw=0.8)
    ax.text(x + 1, y + h - 8.4, "Ca A", fontsize=8.6, fontweight="bold", color=GREEN, va="top")
    ax.text(x + 1, y + h - 10.3, s["a"], fontsize=8.3, color=INK, va="top", linespacing=1.35)
    ax.text(x + 1, y + h - 15.0, "Ca B", fontsize=8.6, fontweight="bold", color=AMBER, va="top")
    ax.text(x + 1, y + h - 16.9, s["b"], fontsize=8.3, color=INK, va="top", linespacing=1.35)
    if c < 4:
        ax.annotate("", xy=(xs[c + 1] - 0.4, y + h / 2), xytext=(x + w + 0.4, y + h / 2),
                    arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.6))
ax.annotate("", xy=(xs[0] + w / 2, rows[1] + h + 0.5), xytext=(xs[4] + w / 2, rows[0] - 0.5),
            arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.4, connectionstyle="arc3,rad=0.08", linestyle="--"))
ax.text(50, 56.6, "Luồng phân tích 10 bước (OrchestratorAgent) — số liệu thật của hai ca minh hoạ",
        ha="center", fontsize=13.5, fontweight="bold", color=INK)
ax.text(50, 1.2, facts["footer"], ha="center", fontsize=8.6, color=GREY, style="italic")
plt.savefig(sys.argv[2], bbox_inches="tight", facecolor="white")
print("figure", sys.argv[2])
