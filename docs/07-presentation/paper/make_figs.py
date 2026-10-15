# -*- coding: utf-8 -*-
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
OUT = sys.argv[1]
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, MUTED, GRID, BASE, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": BASE, "axes.labelcolor": INK2,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "axes.titlecolor": INK, "axes.titleweight": "bold",
    "axes.titlesize": 11, "axes.grid": False, "savefig.dpi": 170})

def style(ax):
    ax.spines["left"].set_color(BASE); ax.spines["bottom"].set_color(BASE)
    ax.yaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)

def save(fig, name):
    fig.tight_layout(); fig.savefig(f"{OUT}/{name}", bbox_inches="tight"); plt.close(fig); print("ok", name)

# Fig 1
sysn = ["Đoán toàn lớp đông nhất", "Zero-shot (mDeBERTa-xnli)", "Luật từ khoá hiện tại", "Học trò e5-base (v3)"]
v = [0.194, 0.271, 0.355, 0.726]; lo = [0.194, 0.242, 0.327, 0.690]; hi = [0.194, 0.296, 0.385, 0.764]
fig, ax = plt.subplots(figsize=(7.2, 3.2)); y = np.arange(len(sysn))
ax.barh(y, v, height=0.55, color=[MUTED, S2, S4, S1], edgecolor=SURF, linewidth=2)
ax.errorbar(v[1:], y[1:], xerr=[np.subtract(v[1:], lo[1:]), np.subtract(hi[1:], v[1:])], fmt="none", ecolor=INK, elinewidth=1.2, capsize=3)
for yi, vi in zip(y, v): ax.text(vi + 0.012, yi, f"{vi:.2f}", va="center", color=INK, fontsize=10)
ax.set_yticks(y, sysn); ax.set_xlim(0, 0.9); ax.invert_yaxis(); ax.xaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
ax.set_xlabel("Macro-F1 (4 lớp) · CV theo công ty · 1.217 câu, 15 công ty · KTC 95% bootstrap theo công ty")
ax.set_title("Hình 1. Nhận diện tuyên bố (T1): học trò so với các mốc so sánh")
save(fig, "fig1_t1_macro_f1.png")

# Fig 2
cls = ["NOT_CLAIM\n(n=769)", "QUALITATIVE\n(n=249)", "QUANTIFIED\n(n=97)", "VAGUE\n(n=102)"]
r = [0.712, 0.358, 0.350, 0.0]; e = [0.880, 0.710, 0.743, 0.570]
fig, ax = plt.subplots(figsize=(7.2, 3.4)); x = np.arange(4); w = 0.36
ax.bar(x - w/2, r, w, color=S4, label="Luật từ khoá", edgecolor=SURF, linewidth=2)
ax.bar(x + w/2, e, w, color=S1, label="Học trò e5-base", edgecolor=SURF, linewidth=2)
for xi, ri, ei in zip(x, r, e):
    ax.text(xi - w/2, ri + 0.02, f"{ri:.2f}", ha="center", color=INK, fontsize=9)
    ax.text(xi + w/2, ei + 0.02, f"{ei:.2f}", ha="center", color=INK, fontsize=9)
ax.set_xticks(x, cls); ax.set_ylim(0, 1); ax.set_ylabel("F1 từng lớp"); style(ax); ax.legend(frameon=False, loc="upper right")
ax.set_title("Hình 2. F1 theo lớp: luật không có lớp VAGUE, học trò yếu nhất ở VAGUE")
save(fig, "fig2_t1_per_class.png")

# Fig 3
frac = [25, 50, 75, 100]; v2 = [0.45, 0.60, 0.64, 0.66]; v3 = [0.624, 0.667, 0.700, 0.719]
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ax.plot(frac, v2, color=S2, lw=2, marker="o", ms=6, label="v2 · 498 câu nhãn (12/10)")
ax.plot(frac, v3, color=S1, lw=2, marker="o", ms=6, label="v3 · 1.217 câu nhãn (13/10)")
ax.text(100, 0.63, "0,66", color=INK, ha="center"); ax.text(100, 0.735, "0,72", color=INK, ha="center")
ax.set_xticks(frac, [f"{f}%" for f in frac]); ax.set_ylim(0.4, 0.8)
ax.set_xlabel("Phần tập huấn luyện được dùng (cùng số bước học)"); ax.set_ylabel("Macro-F1 (CV theo công ty)")
style(ax); ax.legend(frameon=False, loc="lower right"); ax.set_title("Hình 3. Đường học còn dốc: thêm nhãn vẫn còn lợi")
save(fig, "fig3_learning_curve.png")

# Fig 4
cm = np.array([[646, 63, 26, 34], [27, 187, 13, 22], [8, 8, 81, 0], [18, 20, 1, 63]])
lab = ["NOT_CLAIM", "QUALITATIVE", "QUANTIFIED", "VAGUE"]
fig, ax = plt.subplots(figsize=(5.6, 4.6))
norm = cm / cm.sum(axis=1, keepdims=True)
cmap = LinearSegmentedColormap.from_list("seq", [SURF] + SEQ)
ax.imshow(norm, cmap=cmap, vmin=0, vmax=1)
for i in range(4):
    for j in range(4):
        ax.text(j, i, f"{cm[i,j]}\n{norm[i,j]*100:.0f}%", ha="center", va="center", fontsize=9, color=("#f0efec" if norm[i,j] > 0.55 else INK))
ax.set_xticks(range(4), lab, rotation=20); ax.set_yticks(range(4), lab)
ax.set_xlabel("Học trò dự đoán"); ax.set_ylabel("Nhãn tham chiếu (Claude, 2 lượt mù + trọng tài)")
for s in ax.spines.values(): s.set_visible(False)
ax.set_title("Hình 4. Ma trận nhầm lẫn e5-base (CV, 1.217 câu)")
save(fig, "fig4_confusion.png")

# Fig 5
names = ["GreenScan (luật, offline)", "gemma-4-26B-A4B", "gemma-4-31B", "Llama-3.3-70B", "GLM-5.2", "qwen3:8b (CPU)"]
clean = [(20, 45, 77), (29, 76, 97), (32, 89, 100), (30, 80, 98), (32, 89, 100), (28, 72, 95)]
noisy = [(7, 19, 59), (18, 75, 99), (17, 69, 97), (15, 57, 91), (17, 69, 97), (12, 41, 81)]
fc_clean = [1, 1, 0, 2, 0, 3]; fc_noisy = [0, 1, 2, 3, 2, 4]
fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6), sharey=True)
for ax, data, n, fc, title in [(axes[0], clean, 32, fc_clean, "Bộ sạch (n = 32 ca)"), (axes[1], noisy, 19, fc_noisy, "Bộ trang thật Hòa Phát (n = 19 ca)")]:
    y = np.arange(len(names))
    for yi, (a, l, h), f in zip(y, data, fc):
        c = S4 if yi == 0 else S1
        ax.plot([l, h], [yi, yi], color=c, lw=2, alpha=0.5); ax.plot(a/n*100, yi, "o", color=c, ms=8)
        ax.text(h + 2, yi, f"{a}/{n}" + (f"  · {f} xác nhận sai" if f else ""), va="center", fontsize=8.5, color=INK2)
    ax.set_yticks(y, names); ax.invert_yaxis(); ax.set_xlim(0, 150); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("% ca đúng (chấm) và KTC 95% Wilson (thanh)")
    ax.xaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True); ax.set_title(title, fontsize=10)
fig.suptitle("Hình 5. Thang kích thước mô hình (10/10/2026): mô hình lớn đọc đúng hơn, nhưng xác nhận sai nhiều hơn ở trang thật", fontsize=11, fontweight="bold", color=INK)
save(fig, "fig5_size_ladder.png")

# Fig 6
rel = ["PARTIAL", "CONTEXT", "SUPPORTS", "CONTRADICTS"]
off = [648, 84, 48, 0]; on = [290, 327, 151, 12]
fig, ax = plt.subplots(figsize=(7.2, 2.9))
for yi, (vals, name) in enumerate([(off, "Tắt mô hình: 713 cặp\nđoán theo độ giống chữ"), (on, "Bật GLM-5.2 đọc 713 cặp\n(có chốt chặn)")]):
    left = 0
    for v_, c, lb in zip(vals, [S4, MUTED, S3, S2], rel):
        ax.barh(yi, v_, left=left, color=c, edgecolor=SURF, linewidth=2, label=lb if yi == 0 else None)
        if v_ > 40: ax.text(left + v_/2, yi, str(v_), ha="center", va="center", fontsize=9, color=INK if c in (S4, S3) else "#f0efec")
        left += v_
    ax.text(left + 8, yi, name, va="center", fontsize=8.5, color=INK2)
ax.set_yticks([]); ax.set_xlim(0, 1100)
ax.set_xlabel("Số cặp luật/số học không quyết được (Hòa Phát: 780 cặp, 67 do luật quyết)")
ax.spines["left"].set_visible(False); ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.35))
ax.set_title("Hình 6. Mô hình ngôn ngữ phân loại lại các cặp khó (A/B 28/09/2026)")
save(fig, "fig6_stance_ab.png")

# Fig 7
metrics = [("Mục trong hàng đợi soát", 22, 9), ("Mục đầu hàng là câu rác\n(giải thích công nghệ, dính cột)", 10, 0),
           ("Tuyên bố bị trích kèm\nNĐ 83/2026 sai", 55, 0), ("Số liệu không gắn được\nchỉ số môi trường", 34, 0)]
fig, axes = plt.subplots(1, 4, figsize=(9.6, 2.9))
for ax, (m, b, a) in zip(axes, metrics):
    ax.bar([0, 1], [b, a], color=[MUTED, S1], width=0.6, edgecolor=SURF, linewidth=2)
    for xi, val in enumerate([b, a]): ax.text(xi, val + max(b, 1)*0.03, str(val), ha="center", color=INK)
    ax.set_xticks([0, 1], ["05/10", "06/10"]); ax.set_ylim(0, max(b, 1)*1.2); ax.set_title(m, fontsize=9); style(ax)
fig.suptitle("Hình 7. Hàng đợi soát trên Hòa Phát (264 trang, offline) trước và sau rà soát 06/10; kết luận và mức rủi ro không đổi", fontsize=10.5, fontweight="bold", color=INK)
save(fig, "fig7_queue_quality.png")

# Fig 8
sl = [("Tiếng Việt (n=845)", 0.749), ("Tiếng Anh (n=372)", 0.679), ("Không cần ngữ cảnh (n=1.074)", 0.719),
      ("Cần ngữ cảnh (n=143)", 0.674), ("Câu môi trường, không số (n=217)", 0.762), ("Câu môi trường, có số (n=242)", 0.661)]
fig, ax = plt.subplots(figsize=(7.2, 3.2)); y = np.arange(len(sl))
ax.barh(y, [s[1] for s in sl], color=[S1, S1, S3, S3, S4, S4], height=0.55, edgecolor=SURF, linewidth=2)
for yi, s in zip(y, sl): ax.text(s[1] + 0.01, yi, f"{s[1]:.2f}", va="center", color=INK)
ax.axvline(0.726, color=INK2, lw=1, ls="--"); ax.text(0.728, -0.7, "toàn tập 0,73", fontsize=8.5, color=INK2)
ax.set_yticks(y, [s[0] for s in sl]); ax.invert_yaxis(); ax.set_xlim(0.5, 0.85); ax.xaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
ax.set_xlabel("Macro-F1 học trò e5-base theo lát cắt (v3)"); ax.set_title("Hình 8. Học trò yếu hơn ở câu tiếng Anh, câu cần ngữ cảnh và câu có số")
save(fig, "fig8_slices.png")

# Fig 9
fig, ax = plt.subplots(figsize=(7.2, 2.6))
rows = [("Kết luận kiểm chứng (156 tuyên bố)", [("Khớp một phần", 153, S4), ("Ủng hộ", 2, S3), ("Chưa đủ bằng chứng", 1, MUTED)]),
        ("Mức rủi ro (156)", [("MEDIUM", 154, S4), ("LOW", 2, S3)]),
        ("Nguồn bằng chứng (780 đoạn)", [("Tài liệu của chính doanh nghiệp", 780, MUTED)])]
for yi, (name, segs) in enumerate(rows):
    tot = sum(s[1] for s in segs); left = 0
    for lb, v_, c in segs:
        ax.barh(yi, v_/tot*100, left=left, color=c, edgecolor=SURF, linewidth=2)
        if v_/tot > 0.3: ax.text(left + v_/tot*50, yi, f"{lb} {v_}", ha="center", va="center", fontsize=9, color=INK)
        left += v_/tot*100
    ax.text(101, yi, name, va="center", fontsize=8.5, color=INK2)
ax.set_yticks([]); ax.set_xlim(0, 160); ax.set_xticks([0, 50, 100]); ax.set_xlabel("%"); ax.spines["left"].set_visible(False)
ax.set_title("Hình 9. Kết quả đầu–cuối trên Hòa Phát gần như phẳng: giá trị nằm ở hàng đợi, không ở nhãn kết luận")
save(fig, "fig9_hpg_flat.png")
