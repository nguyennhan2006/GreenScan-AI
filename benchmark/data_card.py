"""Thống kê và biểu đồ cân bằng cho MỌI bộ dữ liệu của GreenScan (nguồn số cho docs/04-data-ai/THE_DU_LIEU_2026-11-11.md).

    python -X utf8 benchmark/data_card.py        # -> benchmark/data_card/stats.json + fig_*.png

Độ đo cân bằng cho mỗi trường nhãn: số lớp, lớp nhỏ nhất, tỷ lệ lớn nhất / nhỏ nhất (IR), độ đều Pielou
J = H / ln(k) (1 = đều tuyệt đối), và cờ "lệch" khi IR > 3 hoặc lớp nhỏ nhất < 20 ca (không đủ cho Wilson
khoảng ±20 điểm). Nhóm theo doanh nghiệp: tỷ trọng doanh nghiệp lớn nhất.
"""
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "benchmark"
OUT = B / "data_card"
INK, INK2, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e4e3df"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]


def jl(p):
    return [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]


def jl_glob(folder, pat):
    return [r for f in sorted(Path(folder).glob(pat)) for r in jl(f)]


def balance(counter, min_n=20, max_ir=3.0):
    vals = [v for v in counter.values() if v > 0]
    k, n = len(vals), sum(vals)
    if k < 2:
        return {"classes": k, "n": n}
    H = -sum(v / n * math.log(v / n) for v in vals)
    ir = max(vals) / min(vals)
    return {"classes": k, "n": n, "min_class": min(counter, key=lambda c: counter[c] if counter[c] else 1e9), "min_n": min(vals),
            "imbalance_ratio": round(ir, 2), "pielou_J": round(H / math.log(k), 3), "unbalanced": ir > max_ir or min(vals) < min_n,
            "counts": dict(counter.most_common())}


def top_share(counter):
    n = sum(counter.values())
    c, v = counter.most_common(1)[0]
    return {"largest": c, "share": round(v / n, 3), "groups": len(counter)}


def collect():
    S = {}
    gb = jl(B / "gs_bench_v1/gs_bench_v1.jsonl")
    lab = lambda r: "+".join(r["labels"])
    S["GS-Bench v1 (kết luận)"] = {"n": len(gb), "label": balance(Counter(lab(r) for r in gb if "+" not in lab(r))),
                                   "company": top_share(Counter(r["company"] for r in gb)), "sector": top_share(Counter(r["sector"] for r in gb)),
                                   "source": "ca dựng + câu thật, nhãn Claude/đội", "path": "benchmark/gs_bench_v1/gs_bench_v1.jsonl"}
    for name, f in [("GS-Bench ngoài mẫu v1.2", "gs_heldout_v12.jsonl"), ("GS-Bench ngoài mẫu v1.3", "gs_bench_v13_heldout.jsonl")]:
        r = jl(B / "gs_bench_v1" / f)
        S[name] = {"n": len(r), "label": balance(Counter(lab(x) for x in r)), "company": top_share(Counter(x["company"] for x in r)),
                   "source": "câu thật doanh nghiệp mới", "path": f"benchmark/gs_bench_v1/{f}"}
    ex = jl_glob(B / "gs_eval_v2/explain/labels", "*.jsonl")
    S["D-EXPLAIN"] = {"n": len(ex), "label": balance(Counter(r["ref_verdict"] for r in ex)),
                      "review": dict(Counter(r["review_status"] for r in ex)), "source": "câu thật, nhãn Claude", "path": "benchmark/gs_eval_v2/explain/labels"}
    ed = jl_glob(B / "gs_eval_v2/edit/labels", "*.jsonl")
    S["D-EDIT (mã vấn đề)"] = {"n": len(ed), "label": balance(Counter(i["code"] for r in ed for i in r.get("issues") or [])),
                               "needs_edit": dict(Counter(r["needs_edit"] for r in ed)), "source": "câu thật, nhãn Claude",
                               "path": "benchmark/gs_eval_v2/edit/labels"}
    se = B / "gs_issue/data/supp_explain.jsonl"
    if se.exists():
        sx = jl(se)
        S["D-EXPLAIN + bù 11/11"] = {"n": len(ex) + len(sx), "label": balance(Counter(r["ref_verdict"] for r in ex + sx)),
                                     "source": "D-EXPLAIN + 85 ca C/S từ GS-Bench v1", "path": "benchmark/gs_issue/data/supp_explain.jsonl"}
    sc = jl_glob(B / "gs_eval_v2/score", "merged_*.jsonl")
    S["D-SCORE"] = {"n": len(sc), "adjudicated": len(jl_glob(B / "gs_eval_v2/score", "adjudicated_*.jsonl")),
                    "label": balance(Counter(r.get("holistic_band_a") for r in sc)), "source": "câu thật, hai lượt Claude + phân xử",
                    "path": "benchmark/gs_eval_v2/score"}
    ru = jl_glob(B / "gs_eval_v2/rules", "cases_r*.jsonl")
    S["D-RULES (org pack)"] = {"n": len(ru), "label": balance(Counter(r["expected_outcome"] for r in ru)),
                               "case_type": balance(Counter(r["case_type"] for r in ru), min_n=5),
                               "org": top_share(Counter(r["org_id"] for r in ru)), "source": "ca dựng", "path": "benchmark/gs_eval_v2/rules"}
    pa = jl(B / "gs_eval_v2/inputs/pool_a.jsonl")
    S["Kho câu thật pool A"] = {"n": len(pa), "company": top_share(Counter(r["company"] for r in pa)),
                                "company_counts": dict(Counter(r["company"] for r in pa).most_common()), "source": "GreenScan trích từ báo cáo thật",
                                "path": "benchmark/gs_eval_v2/inputs/pool_a.jsonl"}
    ga = B / "gs_issue/data/layer_a.jsonl"
    if ga.exists():
        a = jl(ga)
        S["GS-Issue lớp A (mới)"] = {"n": len(a), "label": balance(Counter(c for r in a if r["split"] != "A-multi" for c in (r["codes"] or ["CLEAN"]))),
                                     "split": dict(Counter(r["split"] for r in a)), "sector": top_share(Counter(r["sector"] for r in a)),
                                     "source": "đột biến có đáp án, doanh nghiệp hư cấu", "path": "benchmark/gs_issue/data/layer_a.jsonl"}
    gs = B / "gs_issue/data/layer_b_silver.jsonl"
    if gs.exists():
        s = jl(gs)
        S["GS-Issue lớp B (nhãn bạc)"] = {"n": len(s), "label": balance(Counter(c for r in s for c in (r["codes"] or ["CLEAN"]))),
                                          "company": top_share(Counter(r["company"] for r in s)), "source": "câu thật, 14B và 32B cùng gán",
                                          "path": "benchmark/gs_issue/data/layer_b_silver.jsonl"}
    gsel = B / "gs_issue/data/layer_b_balanced.jsonl"
    if gsel.exists():
        s = jl(gsel)
        S["GS-Issue lớp B cân bằng"] = {"n": len(s), "label": balance(Counter(c for r in s for c in (r["codes"] or ["CLEAN"]))),
                                        "company": top_share(Counter(r["company"] for r in s)), "source": "chọn từ nhãn bạc, trần mỗi mã",
                                        "path": "benchmark/gs_issue/data/layer_b_balanced.jsonl"}
    return S


def style(ax):
    ax.set_facecolor(SURF)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=8, length=0)
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def figs(S):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = "DejaVu Sans"
    # 1. balance overview: Pielou J and smallest class per labelled dataset
    rows = [(k, v["label"]) for k, v in S.items() if "label" in v and v["label"].get("classes", 0) >= 2]
    fig, axes = plt.subplots(1, 2, figsize=(10, 0.42 * len(rows) + 1.4), facecolor=SURF, sharey=True)
    names = [r[0] for r in rows][::-1]
    J = [r[1]["pielou_J"] for r in rows][::-1]
    mn = [r[1]["min_n"] for r in rows][::-1]
    bad = [r[1]["unbalanced"] for r in rows][::-1]
    for ax, vals, title, line in ((axes[0], J, "Độ đều Pielou J (1 = đều)", None), (axes[1], mn, "Số ca của lớp nhỏ nhất", 20)):
        style(ax)
        ax.barh(names, vals, color=[SERIES[1] if b else SERIES[0] for b in bad], height=0.6)
        for y, v in enumerate(vals):
            ax.text(v, y, f" {v}", va="center", fontsize=8, color=INK)
        if line:
            ax.axvline(line, color=INK2, lw=1, ls="--")
            ax.text(line, len(names) - 0.4, " ngưỡng 20", fontsize=7, color=INK2)
        ax.set_title(title, fontsize=9, color=INK, loc="left")
    fig.suptitle("Cân bằng nhãn theo bộ dữ liệu (cam = lệch: tỷ lệ lớn/nhỏ > 3 hoặc lớp nhỏ nhất < 20)", fontsize=10, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(OUT / "fig_balance_overview.png", dpi=160)
    plt.close(fig)
    # 2. issue codes: D-EDIT vs GS-Issue layer A vs layer B (silver / balanced)
    sets = [k for k in ("D-EDIT (mã vấn đề)", "GS-Issue lớp A (mới)", "GS-Issue lớp B cân bằng") if k in S]
    codes = sorted({c for k in sets for c in S[k]["label"]["counts"]}, key=lambda c: -S[sets[0]]["label"]["counts"].get(c, 0))
    fig, ax = plt.subplots(figsize=(10, 0.36 * len(codes) + 1.2), facecolor=SURF)
    style(ax)
    h = 0.8 / len(sets)
    for j, k in enumerate(sets):
        vals = [S[k]["label"]["counts"].get(c, 0) for c in codes][::-1]
        ys = [y + (j - (len(sets) - 1) / 2) * h for y in range(len(codes))]
        ax.barh(ys, vals, height=h * 0.9, color=SERIES[j], label=k)
    ax.set_yticks(range(len(codes)))
    ax.set_yticklabels(codes[::-1], fontsize=8)
    ax.axvline(20, color=INK2, lw=1, ls="--")
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    ax.set_title("Số ca theo mã vấn đề: dữ liệu cũ (D-EDIT) và dữ liệu bổ sung (GS-Issue)", fontsize=10, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(OUT / "fig_issue_codes.png", dpi=160)
    plt.close(fig)
    # 3. verdict labels of verification sets
    vs = [k for k in S if k.startswith("GS-Bench") or k == "D-EXPLAIN"]
    fig, axes = plt.subplots(1, len(vs), figsize=(3.2 * len(vs), 2.8), facecolor=SURF)
    for ax, k in zip(axes, vs):
        style(ax)
        c = S[k]["label"]["counts"]
        ks = sorted(c, key=lambda x: -c[x])
        ax.barh(ks[::-1], [c[x] for x in ks][::-1], color=SERIES[0], height=0.6)
        for y, x in enumerate(ks[::-1]):
            ax.text(c[x], y, f" {c[x]}", va="center", fontsize=8, color=INK)
        ax.set_title(f"{k} (n {S[k]['n']})", fontsize=8.5, color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(OUT / "fig_verdict_labels.png", dpi=160)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    S = collect()
    json.dump(S, open(OUT / "stats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    figs(S)
    for k, v in S.items():
        lb = v.get("label", {})
        print(f"{k}: n={v['n']} classes={lb.get('classes')} min={lb.get('min_class')}:{lb.get('min_n')} IR={lb.get('imbalance_ratio')} "
              f"J={lb.get('pielou_J')} unbalanced={lb.get('unbalanced')} company={v.get('company')}")


if __name__ == "__main__":
    main()
