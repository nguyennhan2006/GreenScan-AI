"""Charts (PNG) of every result folder: quality against the rules and the registered limits, training curves, latency.

    python plots.py --results out --out out/hinh [--ref ref_llm_stages.json]

Looks for (any missing one is skipped): t1/metrics.json, t1/history.json, stance/metrics.json, stance/history.json,
reranker/metrics.json, reranker/history.json, explain-*/history.json, stance-*/history.json, explain_eval/*.json,
stance_eval/*.json. Labels are Vietnamese (the charts go into the team's report).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

C_RULE, C_MODEL, C_REF, C_BAD = "#8a8f98", "#1f6f5c", "#c9a227", "#b8423a"
plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

# llm_stages_v1 numbers measured 11/11 (configs/measurement_decisions.yaml), shown as reference bars
REF = {"s1_gate_v11": {"e5-small (nhãn v1.1)": (28, 26), "e5-base (nhãn v1.1)": (31, 27), "luật": (11, 1)},
       "s5": {"luật": 0.397, "Qwen3-4B (prompt)": 0.605, "Qwen3-8B (prompt)": 0.617, "Qwen3-32B (prompt)": 0.575},
       "s6": {"luật": 0.015, "Qwen3-4B (prompt)": 0.140, "Qwen3-32B (prompt)": 0.210, "gpt-oss-120b (40 mục)": 0.356}}


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def bars(ax, names, vals, colors, cis=None, fmt="{:.3f}", limit=None, limit_label=""):
    x = range(len(names))
    err = None
    if cis:
        err = [[v - (c[0] if c else v) for v, c in zip(vals, cis)], [(c[1] if c else v) - v for v, c in zip(vals, cis)]]
    ax.bar(x, vals, color=colors, yerr=err, capsize=3)
    for i, v in enumerate(vals):
        ax.text(i, v, fmt.format(v), ha="center", va="bottom", fontsize=8)
    ax.set_xticks(list(x), names, rotation=20, ha="right")
    if limit is not None:
        ax.axhline(limit, color=C_BAD, ls="--", lw=1)
        ax.text(len(names) - 0.5, limit, limit_label, color=C_BAD, ha="right", va="bottom", fontsize=8)


def save(fig, out: Path, name: str, made: list):
    fig.tight_layout()
    fig.savefig(out / name)
    plt.close(fig)
    made.append(name)


def curves(hist, title, out, name, made, key="run"):
    if not hist:
        return
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    if isinstance(hist, dict):   # SFT history
        tr = hist.get("train", [])
        ax.plot([h["epoch"] for h in tr], [h["loss"] for h in tr], color=C_MODEL, label="train")
        va = [h for h in hist.get("val", []) if h.get("loss") is not None]
        if va:
            ax.plot([h["epoch"] for h in va], [h["loss"] for h in va], "o--", color=C_REF, label="validation (DN giữ lại)")
        ax.set_xlabel("epoch")
    else:
        runs = {}
        for h in hist:
            runs.setdefault(h[key], []).append(h)
        for r, hs in runs.items():
            final = "final" in r
            ax.plot([h["epoch"] for h in hs], [h["loss"] for h in hs], lw=1.6 if final else 0.7,
                    alpha=1 if final else 0.45, label=r if final else None)
        ax.set_xlabel("epoch (đường mờ: các fold kiểm chéo)")
    ax.set_ylabel("loss")
    ax.set_title(title)
    ax.legend(fontsize=7)
    save(fig, out, name, made)


def t1_charts(m, out, made):
    runs = m["runs"]
    names = list(runs)
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    bars(ax, names, [runs[n]["cv"]["macro_f1"] for n in names], [C_MODEL] * len(names))
    ax.axhline(0.355, color=C_RULE, ls=":", lw=1)
    ax.text(len(names) - 0.5, 0.355, "luật 0,355 (11/11)", color=C_RULE, ha="right", va="bottom", fontsize=8)
    ax.set_ylabel("macro-F1 4 lớp")
    ax.set_title("T1 nhận diện tuyên bố: kiểm chéo theo doanh nghiệp (nhãn Q13 v1.2)")
    save(fig, out, "t1_cv_macro_f1.png", made)

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    lab, caught, flagged, col = [], [], [], []
    for n in names:
        g = runs[n]["s1_gate"]["0.5"]
        lab.append(n); caught.append(g["not_claim_caught"]); flagged.append(g["true_claims_flagged"]); col.append(C_MODEL)
    for n, (c, f) in REF["s1_gate_v11"].items():
        lab.append(n); caught.append(c); flagged.append(f); col.append(C_RULE if n == "luật" else C_REF)
    bars(axes[0], lab, caught, col, fmt="{:.0f}", limit=22, limit_label="cần ≥ 22/44")
    axes[0].set_title("Bắt đúng câu không phải tuyên bố (/44)")
    bars(axes[1], lab, flagged, col, fmt="{:.0f}", limit=6, limit_label="trần 6/102")
    axes[1].set_title("Gắn nhầm tuyên bố thật (/102) — càng thấp càng an toàn")
    fig.suptitle("Cổng S1 tại ngưỡng 0,5 (xanh: lượt mới · vàng: 11/11 · xám: luật)")
    save(fig, out, "t1_gate_s1.png", made)

    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    for n in names:
        g = runs[n]["s1_gate"]
        ts = sorted(g, key=float)
        ax.plot([g[t]["true_claims_flagged"] for t in ts], [g[t]["not_claim_caught"] for t in ts], "o-", label=n)
        for t in ts:
            ax.annotate(t, (g[t]["true_claims_flagged"], g[t]["not_claim_caught"]), fontsize=6)
    ax.axvline(6, color=C_BAD, ls="--", lw=1)
    ax.axhline(22, color=C_BAD, ls="--", lw=1)
    ax.set_xlabel("tuyên bố thật bị gắn nhầm (/102)")
    ax.set_ylabel("câu không phải tuyên bố bắt được (/44)")
    ax.set_title("Đánh đổi theo ngưỡng (vùng đạt: trên-trái hai đường đỏ)")
    ax.legend(fontsize=7)
    save(fig, out, "t1_threshold_tradeoff.png", made)


def confusion_chart(cm, labels, title, out, name, made):
    fig, ax = plt.subplots(figsize=(4.6, 4))
    ax.imshow(cm, cmap="Greens")
    for i, row in enumerate(cm):
        for j, v in enumerate(row):
            ax.text(j, i, v, ha="center", va="center", fontsize=9, color="black")
    ax.set_xticks(range(len(labels)), labels, rotation=30, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel("dự đoán")
    ax.set_ylabel("nhãn")
    ax.set_title(title)
    save(fig, out, name, made)


def stance_charts(m, out, made):
    cv = m["cv"]
    confusion_chart(cv["confusion"], cv["labels"], "Chấm quan hệ mDeBERTa: kiểm chéo", out, "stance_confusion.png", made)
    names = ["mDeBERTa tinh chỉnh"] + list(m.get("cv_baselines", {}))
    vals = [cv["macro_f1"]] + [v["macro_f1"] for v in m.get("cv_baselines", {}).values()]
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.5))
    bars(axes[0], names, vals, [C_MODEL] + [C_RULE] * (len(names) - 1),
         cis=[cv.get("ci95_macro_f1")] + [None] * (len(names) - 1))
    axes[0].set_title("821 cặp: macro-F1 4 quan hệ (theo DN)")
    s5 = m["s5"]
    n2 = ["mDeBERTa tinh chỉnh"] + list(REF["s5"])
    v2 = [s5["model"]["macro_f1_SO"]] + list(REF["s5"].values())
    bars(axes[1], n2, v2, [C_MODEL] + [C_RULE] + [C_REF] * 3, cis=[s5["model"]["ci95"]] + [None] * 4)
    axes[1].set_title(f"S5 (391 cặp ngoài): macro-F1(S,O) · sai C: {s5['model']['false_C']} (luật {s5['rules']['false_C']})")
    save(fig, out, "stance_quality.png", made)
    rc = cv.get("risk_coverage")
    if rc:
        fig, ax = plt.subplots(figsize=(5.4, 3.4))
        ax.plot([r["coverage"] for r in rc], [r["accuracy"] for r in rc], "o-", color=C_MODEL)
        ax.set_xlabel("độ phủ (tỉ lệ cặp mô hình tự quyết, chắc nhất trước)")
        ax.set_ylabel("độ chính xác trên phần tự quyết")
        ax.set_title("Đường độ phủ – độ chính xác (phần còn lại chuyển người soát)")
        save(fig, out, "stance_risk_coverage.png", made)


def reranker_charts(m, out, made):
    systems = [k for k in ("lite", "bm25", "zero_shot", "fine_tuned_cv") if k in m]
    vn = {"lite": "lite (offline hiện tại)", "bm25": "BM25", "zero_shot": "gte chưa tinh chỉnh", "fine_tuned_cv": "gte tinh chỉnh"}
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
    for ax, k, t in zip(axes, ("ndcg5", "mrr5", "hit5"), ("nDCG@5", "MRR@5", "hit@5 (đoạn đáng trích)")):
        bars(ax, [vn[s] for s in systems], [m[s][k]["mean"] for s in systems],
             [C_MODEL if s == "fine_tuned_cv" else C_RULE for s in systems], cis=[m[s][k]["ci95"] for s in systems])
        ax.set_title(t)
    fig.suptitle(f"Xếp hạng bằng chứng trong pool đã gán nhãn ({m['fine_tuned_cv']['claims'] if 'fine_tuned_cv' in m else '?'} tuyên bố, kiểm chéo theo DN)")
    save(fig, out, "reranker_quality.png", made)


def explain_charts(res_dir: Path, out, made):
    rows = []
    for f in sorted((res_dir / "explain_eval").glob("*.json")):
        r = load(f)
        for sname, s in r["systems"].items():
            rows.append((f"{f.stem} · {sname}", s))
    if not rows:
        return
    names = [n for n, _ in rows] + list(REF["s6"])
    vals = [s["must_mention_proxy"] for _, s in rows] + list(REF["s6"].values())
    cis = [s.get("ci95") for _, s in rows] + [None] * len(REF["s6"])
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"width_ratios": [3, 2]})
    bars(axes[0], names, vals, [C_MODEL] * len(rows) + [C_RULE] + [C_REF] * (len(REF["s6"]) - 1), cis=cis)
    axes[0].set_title("S6 lời giải thích: tỉ lệ nêu đủ ý (142 mục)")
    bars(axes[1], [n for n, _ in rows], [s["with_new_number"] for _, s in rows], [C_BAD] * len(rows), fmt="{:.0f}")
    axes[1].set_title("Số lời giải thích có số mới (code chặn, phải = 0 sau chặn)")
    save(fig, out, "explain_quality.png", made)


def stance_llm_charts(res_dir: Path, out, made):
    rows = []
    for f in sorted((res_dir / "stance_eval").glob("*.json")):
        r = load(f)
        for sname, s in r["systems"].items():
            rows.append((f"{f.stem} · {sname}", s))
        rule = r["rules"]
    if not rows:
        return
    fig, ax = plt.subplots(figsize=(7, 3.6))
    names = [n for n, _ in rows] + ["luật"]
    bars(ax, names, [s["macro_f1_SO"] for _, s in rows] + [rule["macro_f1_SO"]],
         [C_MODEL] * len(rows) + [C_RULE], cis=[s["ci95"] for _, s in rows] + [rule["ci95"]])
    ax.set_title("S5 chấm quan hệ bằng LLM (A100): macro-F1(S,O); nhãn: sai C / 100")
    for i, (_, s) in enumerate(rows):
        ax.text(i, 0.02, f"sai C {s['false_C_per_100']}", ha="center", fontsize=7, color="white")
    save(fig, out, "stance_llm_quality.png", made)


def latency_chart(res_dir: Path, out, made):
    items = []
    t1 = load(res_dir / "t1" / "metrics.json")
    if t1:
        items += [(f"T1 {n}", r.get("cpu_ms_per_sentence_4threads")) for n, r in t1["runs"].items()]
    st = load(res_dir / "stance" / "metrics.json")
    if st:
        items.append(("chấm quan hệ mDeBERTa / cặp", st.get("cpu_ms_per_pair_4threads")))
    rr = load(res_dir / "reranker" / "metrics.json")
    if rr:
        items.append(("reranker gte / đoạn", rr.get("cpu_ms_per_passage_4threads")))
    items = [(n, v) for n, v in items if v]
    if not items:
        return
    fig, ax = plt.subplots(figsize=(7, 3.4))
    bars(ax, [n for n, _ in items], [v for _, v in items], [C_MODEL] * len(items), fmt="{:.0f} ms",
         limit=300, limit_label="trần 300 ms / cặp")
    ax.axhline(50, color=C_REF, ls=":", lw=1)
    ax.set_ylabel("ms (CPU 4 luồng, đo trên Kaggle)")
    ax.set_title("Tốc độ suy luận trên CPU (laptop i7-1355U cần đo lại)")
    save(fig, out, "latency_cpu.png", made)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="out")
    ap.add_argument("--out", default="out/hinh")
    a = ap.parse_args()
    res, out = Path(a.results), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    made: list[str] = []
    m = load(res / "t1" / "metrics.json")
    if m:
        t1_charts(m, out, made)
    curves(load(res / "t1" / "history.json"), "T1: loss huấn luyện", out, "t1_loss.png", made)
    for sd in ("stance", "stance_nli", "stance_nli_zs", "stance_nli_probe"):   # 4-way new head; NLI head kept (entailment / neutral / contradiction)
        m = load(res / sd / "metrics.json")
        if m:
            sub = out / sd if sd != "stance" else out
            sub.mkdir(exist_ok=True)
            stance_charts(m, sub, made)
        curves(load(res / sd / "history.json"), f"Chấm quan hệ mDeBERTa ({sd}): loss", out, f"{sd}_loss.png", made)
    m = load(res / "reranker" / "metrics.json")
    if m:
        reranker_charts(m, out, made)
    curves(load(res / "reranker" / "history.json"), "Reranker: loss danh sách", out, "reranker_loss.png", made)
    for d in sorted(res.glob("*-*b")) + sorted(res.glob("*-*b-*")):
        h = load(d / "history.json")
        if h:
            curves(h, f"{d.name}: loss SFT (chỉ token câu trả lời)", out, f"{d.name}_loss.png", made)
    explain_charts(res, out, made)
    stance_llm_charts(res, out, made)
    latency_chart(res, out, made)
    print(f"[plots] {len(made)} charts -> {out}: {made}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
