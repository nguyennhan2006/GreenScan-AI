"""Biểu đồ kết quả GS-Issue và bù dữ liệu (đọc results/score_issue.json, results/score_supp.json).

    python -X utf8 benchmark/gs_issue/make_figs.py     # -> results/figs/*.png

Thứ tự hệ thống (và màu) cố định: rules, q3-4b, q3-8b, q3-14b-awq, q3-32b-awq, hybrid; hệ thiếu thì bỏ qua,
màu của hệ còn lại không đổi. Biểu đồ tĩnh cho báo cáo và slide: nhãn trực tiếp, lưới nhạt, một trục.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
FIG = RES / "figs"
INK, INK2, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
ORDER = ["rules", "q3-4b", "q3-8b", "q3-14b-awq", "q3-32b-awq", "hybrid"]
COLOR = dict(zip(ORDER, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]))
NAME = {"rules": "Luật GreenScan", "q3-4b": "Qwen3-4B", "q3-8b": "Qwen3-8B", "q3-14b-awq": "Qwen3-14B",
        "q3-32b-awq": "Qwen3-32B", "hybrid": "Luật + 4B (có chốt số)"}
DSNAME = {"layer_a": "Lớp A: ca đột biến có đáp án", "d_edit": "D-EDIT: câu thật, nhãn Claude", "layer_b": "Lớp B: câu thật, nhãn bạc"}
BLUES = LinearSegmentedColormap.from_list("b", ["#f0f6fe", "#9ec5f4", "#3987e5", "#1c5cab", "#0d366b"])
plt.rcParams["font.family"] = "DejaVu Sans"


def style(ax, grid="x"):
    ax.set_facecolor(SURF)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8, length=0)
    if grid:
        ax.grid(True, axis=grid, color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def systems(d):
    return [t for t in ORDER if t in d["systems"]]


def fig_macro(R):
    dss = [k for k in ("layer_a", "d_edit", "layer_b") if k in R["datasets"]]
    fig, axes = plt.subplots(1, len(dss), figsize=(4.2 * len(dss), 3.2), facecolor=SURF, squeeze=False)
    for ax, ds in zip(axes[0], dss):
        d = R["datasets"][ds]
        ts = systems(d)
        style(ax)
        for y, t in enumerate(ts[::-1]):
            x = d["systems"][t]["detection"]
            ci = x.get("macro_f1_ci_sector_boot") or x.get("macro_f1_ci_company_boot") or [None, None]
            if ci[0] is not None:
                ax.plot(ci, [y, y], color=COLOR[t], lw=2, solid_capstyle="round")
            ax.plot([x["macro_f1"]], [y], "o", ms=8, color=COLOR[t], mec=SURF, mew=2)
            ax.text(x["macro_f1"], y + 0.28, f"{x['macro_f1']:.2f}", ha="center", fontsize=8, color=INK)
        ax.set_yticks(range(len(ts)))
        ax.set_yticklabels([NAME[t] for t in ts[::-1]], fontsize=8)
        ax.set_xlim(0, 1)
        ax.set_title(DSNAME[ds], fontsize=9, color=INK, loc="left")
    fig.suptitle("Tìm lỗ hổng: macro-F1 trên 14 mã vấn đề (chấm = điểm, vạch = CI95 bootstrap theo ngành / doanh nghiệp)",
                 fontsize=10, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(FIG / "fig_macro_f1.png", dpi=160)
    plt.close(fig)


def fig_heat(R):
    d = R["datasets"]["layer_a"]
    ts = systems(d)
    codes = list(next(iter(d["systems"].values()))["detection"]["per_code"])
    M = [[(d["systems"][t]["detection"]["per_code"].get(c) or {}).get("r") or 0 for t in ts] for c in codes]
    fig, ax = plt.subplots(figsize=(1.25 * len(ts) + 3.2, 0.36 * len(codes) + 1.4), facecolor=SURF)
    ax.imshow(M, cmap=BLUES, vmin=0, vmax=1, aspect="auto")
    for i, row in enumerate(M):
        for j, v in enumerate(row):
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7.5, color="#ffffff" if v > 0.6 else INK)
    ax.set_xticks(range(len(ts)))
    ax.set_xticklabels([NAME[t] for t in ts], fontsize=8, rotation=20, ha="right")
    ax.set_yticks(range(len(codes)))
    ax.set_yticklabels(codes, fontsize=7.5)
    ax.tick_params(length=0, colors=INK2)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Lớp A: tỷ lệ bắt được từng loại lỗ hổng (recall)", fontsize=10, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "fig_recall_by_code.png", dpi=160)
    plt.close(fig)


def fig_funnel(R):
    d = R["datasets"]["layer_a"]
    ts = systems(d)
    steps = [("detected", "Bắt đúng mã"), ("resolves", "Bản sửa gỡ được lỗi"), ("correct", "Sửa đúng (gỡ lỗi, giữ số, không bịa số)"),
             ("invents_number", "Bịa số mới")]
    fig, ax = plt.subplots(figsize=(9, 0.55 * len(ts) * len(steps) / 2 + 1.6), facecolor=SURF)
    style(ax)
    h = 0.8 / len(ts)
    for j, t in enumerate(ts):
        f = d["systems"][t]["fix"]["funnel_single"]
        vals = [f[k] or 0 for k, _ in steps]
        ys = [i + (j - (len(ts) - 1) / 2) * h for i in range(len(steps))]
        ax.barh(ys, vals, height=h * 0.86, color=COLOR[t], label=NAME[t])
        for y, v in zip(ys, vals):
            ax.text(v + 0.01, y, f"{v:.2f}", va="center", fontsize=7, color=INK)
    ax.set_yticks(range(len(steps)))
    ax.set_yticklabels([s for _, s in steps], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.08)
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    ax.set_title("Lớp A, 560 ca một lỗi: từ phát hiện đến bản sửa đúng", fontsize=10, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "fig_fix_funnel.png", dpi=160)
    plt.close(fig)


def fig_tradeoff(R):
    d = R["datasets"]["layer_a"]
    fig, ax = plt.subplots(figsize=(6.2, 4.2), facecolor=SURF)
    style(ax, grid="both")
    for t in systems(d):
        x = d["systems"][t]["detection"]
        fa, f1 = x["clean_false_alarm"], x["macro_f1"]
        ax.plot([fa], [f1], "o", ms=9, color=COLOR[t], mec=SURF, mew=2)
        ax.annotate(NAME[t], (fa, f1), xytext=(6, 4), textcoords="offset points", fontsize=8, color=INK)
    ax.set_xlim(-0.02, 1.05)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Tỷ lệ báo nhầm trên câu sạch (thấp hơn là tốt)", fontsize=8.5, color=INK2)
    ax.set_ylabel("macro-F1 tìm lỗ hổng (cao hơn là tốt)", fontsize=8.5, color=INK2)
    ax.set_title("Lớp A: bắt được nhiều mà không báo nhầm", fontsize=10, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "fig_false_alarm_vs_f1.png", dpi=160)
    plt.close(fig)


def fig_twins(S):
    t = S["twins"]["per_code"]
    codes = sorted(t, key=lambda c: -(t[c].get("up", 0) / t[c]["n"]))
    fig, ax = plt.subplots(figsize=(8.5, 0.4 * len(codes) + 1.4), facecolor=SURF)
    style(ax)
    parts = [("up", "Điểm tăng (đúng)", "#2a78d6"), ("tie", "Điểm không đổi (không thấy lỗi)", "#b8b7b0"), ("down", "Điểm giảm", "#eb6834")]
    left = [0] * len(codes)
    for key, lab, col in parts:
        vals = [t[c].get(key, 0) / t[c]["n"] for c in codes]
        ax.barh(codes, vals, left=left, color=col, label=lab, height=0.6, edgecolor=SURF, linewidth=2)
        left = [a + b for a, b in zip(left, vals)]
    for y, c in enumerate(codes):
        ax.text(1.01, y, f"n {t[c]['n']}", va="center", fontsize=7.5, color=INK2)
    ax.set_xlim(0, 1.1)
    ax.invert_yaxis()
    ax.legend(fontsize=8, frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.32), ncol=3)
    ax.set_title("Cặp song sinh: điểm ưu tiên của bản có lỗi so với bản sạch", fontsize=10, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "fig_twin_pairs.png", dpi=160)
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    R = json.load(open(RES / "score_issue.json", encoding="utf-8"))
    fig_macro(R)
    fig_heat(R)
    fig_funnel(R)
    fig_tradeoff(R)
    if (RES / "score_supp.json").exists():
        fig_twins(json.load(open(RES / "score_supp.json", encoding="utf-8")))
    print("figs ->", sorted(p.name for p in FIG.glob("*.png")))


if __name__ == "__main__":
    main()
