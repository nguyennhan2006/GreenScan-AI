"""Giải thích bằng toán vì sao một mô hình không qua cổng đã đăng ký (offline_training_v1), từ số đo thật.

    C:/Python314/python.exe -X utf8 tools/bao_cao_mo_hinh/giai_thich_truot.py [--results deploy/vastai_a100/out_kaggle/merged]

Ghi: docs/04-data-ai/hinh_mo_hinh/t1_roc_dprime.png, stance_kappa_lift.png, stance_latency_flops.png, và
docs/04-data-ai/GIAI_THICH_TRUOT_2026-11-13.md (số điền từ metrics.json; chạy lại khi có kết quả mới).

T1 (cổng S1): mô hình nhị phân "không phải tuyên bố" trên câu GS-Eval. Cổng = một ngưỡng t với TPR = bắt/44 >= 0,5 và
FPR = gắn nhầm/102 <= 6/102. Mô hình nhị chuẩn (binormal): điểm của hai lớp ~ N(0,1) và N(d',1), nên
TPR = Phi(d' + Phi^-1(FPR)). Cổng cần d' >= Phi^-1(0,5) - Phi^-1(6/102) = 1,565, tức AUC = Phi(d'/sqrt 2) >= 0,866.
Chấm quan hệ: kappa của Cohen từ ma trận nhầm lẫn kiểm chéo, lift = precision / tỉ lệ nền của lớp, và chi phí tính
FLOPs(L) của mDeBERTa-v3-base (12 lớp, d = 768, FFN 3072, chú ý tách rời ~ 3 lần chú ý thường) so với 300 ms.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import NormalDist

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "docs" / "04-data-ai" / "hinh_mo_hinh"
DOC = ROOT / "docs" / "04-data-ai" / "GIAI_THICH_TRUOT_2026-11-13.md"
N = NormalDist()
plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def z(p: float, n: int) -> float:
    p = min(max(p, 0.5 / n), 1 - 0.5 / n)        # hiệu chỉnh liên tục để 0/n không thành vô cực
    return N.inv_cdf(p)


def wilson(k: int, n: int, zz: float = 1.96) -> tuple[float, float]:
    p = k / n
    c = (p + zz * zz / (2 * n)) / (1 + zz * zz / n)
    h = zz * ((p * (1 - p) / n + zz * zz / (4 * n * n)) ** 0.5) / (1 + zz * zz / n)
    return round(c - h, 3), round(c + h, 3)


def t1_part(m: dict, out: list) -> dict:
    need = N.inv_cdf(0.5) - N.inv_cdf(6 / 102)
    pts = []
    for name, r in m["runs"].items():
        for t, g in r["s1_gate"].items():
            fpr, tpr = g["true_claims_flagged"] / g["true_claims_total"], g["not_claim_caught"] / g["not_claim_total"]
            d = z(tpr, g["not_claim_total"]) - z(fpr, g["true_claims_total"])
            pts.append({"run": name, "t": float(t), "fpr": fpr, "tpr": tpr, "d": d, "flag": g["true_claims_flagged"],
                        "caught": g["not_claim_caught"]})
    usable = [p for p in pts if 0 < p["fpr"] < 1 and 0 < p["tpr"] < 1]
    best = max(usable, key=lambda p: p["d"])
    d_med = sorted(p["d"] for p in usable)[len(usable) // 2]
    tpr_at_gate = N.cdf(d_med + N.inv_cdf(6 / 102))
    fig, ax = plt.subplots(figsize=(6.2, 4.6))
    xs = [i / 200 for i in range(1, 200)]
    for d, ls in ((0.5, ":"), (d_med, "-"), (need, "--")):
        ax.plot(xs, [N.cdf(d + N.inv_cdf(x)) for x in xs], ls, color="#8a8f98" if d != need else "#b8423a", lw=1,
                label=f"d' = {d:.2f}" + (" (cần cho cổng)" if d == need else " (trung vị đo được)" if d == d_med else ""))
    for run in m["runs"]:
        p = [q for q in pts if q["run"] == run]
        ax.plot([q["fpr"] for q in p], [q["tpr"] for q in p], "o-", ms=4, label=run)
    ax.add_patch(plt.Rectangle((0, 0.5), 6 / 102, 0.5, color="#1f6f5c", alpha=0.15))
    ax.text(0.003, 0.93, "vùng đạt cổng", color="#1f6f5c", fontsize=8)
    ax.set_xlim(0, 0.4)
    ax.set_ylim(0, 1)
    ax.set_xlabel("FPR = tuyên bố thật bị gắn nhầm / 102")
    ax.set_ylabel("TPR = câu không phải tuyên bố bắt được / 44")
    ax.set_title("T1 trên GS-Eval: điểm ROC theo ngưỡng và đường d' nhị chuẩn")
    ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "t1_roc_dprime.png")
    plt.close(fig)
    out.append("t1_roc_dprime.png")
    return {"need_d": round(need, 3), "need_auc": round(N.cdf(need / 2 ** 0.5), 3), "median_d": round(d_med, 3),
            "median_auc": round(N.cdf(d_med / 2 ** 0.5), 3), "best": best, "tpr_at_gate_median_d": round(tpr_at_gate, 3),
            "points": len(usable), "wilson_best_fpr": wilson(best["flag"], 102)}


def kappa(cm: list[list[int]]) -> float:
    n = sum(map(sum, cm))
    po = sum(cm[i][i] for i in range(len(cm))) / n
    pe = sum(sum(cm[i]) * sum(r[i] for r in cm) for i in range(len(cm))) / n / n
    return (po - pe) / (1 - pe)


def flops_mdeberta(L: int, layers=12, d=768, ff=3072) -> float:
    lin = 2 * (4 * d * d + 2 * d * ff) * L          # Q,K,V,O + FFN, 2 FLOPs mỗi phép nhân-cộng
    att = 3 * 4 * L * L * d                         # QK^T và AV, x3 cho chú ý tách rời (c2c, c2p, p2c)
    return layers * (lin + att)


def stance_part(m: dict, out: list) -> dict:
    cv = m["cv"]
    labels, cm = cv["labels"], cv["confusion"]
    keep = [i for i, l in enumerate(labels) if sum(cm[i]) or sum(r[i] for r in cm)]
    cm2 = [[cm[i][j] for j in keep] for i in keep]
    names = [labels[i] for i in keep]
    n = sum(map(sum, cm2))
    k = kappa(cm2)
    rows = []
    for i, l in enumerate(names):
        prior = sum(cm2[i]) / n
        pred = sum(r[i] for r in cm2)
        prec = cm2[i][i] / pred if pred else 0.0
        rows.append({"label": l, "prior": round(prior, 4), "precision": round(prec, 4),
                     "lift": round(prec / prior, 2) if prior else None, "support": sum(cm2[i]), "predicted": pred})
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    x = range(len(rows))
    axes[0].bar([i - 0.2 for i in x], [r["prior"] for r in rows], 0.4, color="#8a8f98", label="tỉ lệ nền (đoán bừa)")
    axes[0].bar([i + 0.2 for i in x], [r["precision"] for r in rows], 0.4, color="#1f6f5c", label="precision mô hình")
    for i, r in enumerate(rows):
        axes[0].text(i + 0.2, r["precision"], f"lift {r['lift']}", ha="center", va="bottom", fontsize=8)
    axes[0].set_xticks(list(x), names)
    axes[0].set_title(f"Kiểm chéo theo DN: κ Cohen = {k:.3f} (≈ 0: không hơn ngẫu nhiên)")
    axes[0].legend(fontsize=7)
    Ls = list(range(64, 513, 16))
    meas = m.get("cpu_ms_per_pair_4threads")
    L_ref = 384
    thr = flops_mdeberta(L_ref) / (meas / 1000) if meas else None
    if thr:
        axes[1].plot(Ls, [flops_mdeberta(L) / thr * 1000 for L in Ls], color="#1f6f5c", label="dự báo t(L) = FLOPs(L) / thông lượng đo")
        axes[1].plot([L_ref], [meas], "o", color="#b8423a", label=f"đo trên Kaggle: {meas:.0f} ms (L ≤ 384)")
        axes[1].plot(Ls, [flops_mdeberta(L) / thr * 1000 / 2 for L in Ls], "--", color="#c9a227", label="nếu lượng tử int8 (~2 lần nhanh hơn)")
        axes[1].axhline(300, color="#b8423a", ls="--", lw=1)
        axes[1].text(70, 310, "trần 300 ms / cặp", color="#b8423a", fontsize=8)
        axes[1].set_xlabel("số token của cặp (L)")
        axes[1].set_ylabel("ms / cặp, CPU 4 luồng")
        axes[1].set_title("Vì sao chậm: chi phí tăng theo L và L²")
        axes[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "stance_kappa_lift.png")
    plt.close(fig)
    out.append("stance_kappa_lift.png")
    L_ok = max((L for L in Ls if thr and flops_mdeberta(L) / thr * 1000 <= 300), default=None)
    L_ok_int8 = max((L for L in Ls if thr and flops_mdeberta(L) / thr * 1000 / 2 <= 300), default=None)
    s5 = m["s5"]
    return {"kappa": round(k, 3), "rows": rows, "n": n, "gflops_384": round(flops_mdeberta(384) / 1e9, 1),
            "throughput_gflops": round(thr / 1e9, 1) if thr else None, "L_ok": L_ok, "L_ok_int8": L_ok_int8,
            "cpu_ms": meas, "s5_model": s5["model"]["macro_f1_SO"], "s5_model_ci": s5["model"]["ci95"],
            "s5_rules": s5["rules"]["macro_f1_SO"], "s5_rules_ci": s5["rules"]["ci95"],
            "cv_macro": cv["macro_f1"], "nli": m.get("cv_baselines", {}).get("nli-mdeberta", {}).get("macro_f1"),
            "rules_pairs": m.get("cv_baselines", {}).get("rules", {}).get("macro_f1")}


def label_stats() -> dict:
    lab = [json.loads(x) for x in open(ROOT / "training/data/claude/pairs/labels.jsonl", encoding="utf-8")]
    sup = [x for x in lab if x["relation"] == "SUPPORTS"]
    part = [x for x in lab if x["relation"] == "PARTIAL"]
    ctx_rule = [x for x in lab if x["relation"] == "CONTEXT" and x.get("flag") in ("khac_ky", "muc_tieu", "khac_pham_vi", "can_tinh")]
    pos = len(sup) + len(part)
    return {"supports": len(sup), "supports_lap_lai": sum(x.get("flag") == "lap_lai" for x in sup), "partial": len(part),
            "context": sum(x["relation"] == "CONTEXT" for x in lab), "context_by_rule": len(ctx_rule),
            "eta_semantic": round(len(ctx_rule) / (pos + len(ctx_rule)), 3)}


def nli_part(m: dict) -> dict:
    cv = m["cv"]
    cm = [r[:2] for r in cv["confusion"][:2]]
    L = m.get("max_len", 256)
    f_lin = 12 * 2 * (4 * 768 ** 2 + 2 * 768 * 3072) * L / flops_mdeberta(L)
    S = m["cpu_ms_per_pair_4threads"] / m["cpu_ms_per_pair_int8"] if m.get("cpu_ms_per_pair_int8") else None
    s_int8 = f_lin / (1 / S - (1 - f_lin)) if S else None
    return {"kappa": round(kappa(cm), 3), "cv_macro": cv["macro_f1"], "cv_ci": cv["ci95_macro_f1"],
            "nli_zero_shot": m["cv_baselines"].get("nli-mdeberta", {}).get("macro_f1"),
            "rules": m["cv_baselines"].get("rules", {}).get("macro_f1"), "temperature": cv["temperature"],
            "s5": m["s5"]["model"]["macro_f1_SO"], "s5_ci": m["s5"]["model"]["ci95"], "s5_rules": m["s5"]["rules"]["macro_f1_SO"],
            "s5_rules_ci": m["s5"]["rules"]["ci95"], "false_c": m["s5"]["model"]["false_C"], "L": L,
            "cpu_ms": m["cpu_ms_per_pair_4threads"], "int8_ms": m.get("cpu_ms_per_pair_int8"), "int8_same": m.get("int8_same_argmax"),
            "f_lin": round(f_lin, 3), "amdahl_S": round(S, 3) if S else None, "int8_gemm_speedup": round(s_int8, 2) if s_int8 else None,
            "ideal_ms": round(m["cpu_ms_per_pair_4threads"] * ((1 - f_lin) + f_lin / 2), 0)}


def write_doc(t1: dict | None, st: dict | None, nl: dict | None = None, ls: dict | None = None) -> None:
    L = ["# Vì sao các mô hình không qua cổng: giải thích bằng toán (13/11/2026)", "",
         "Tệp sinh tự động bởi `tools/bao_cao_mo_hinh/giai_thich_truot.py` từ `metrics.json` của các lượt Kaggle "
         "(khối `offline_training_v1` trong `configs/measurement_decisions.yaml`). Nhãn đều là nhãn bạc.", ""]
    if t1:
        b = t1["best"]
        L += ["## 1. T1 lọc tuyên bố: trượt cổng S1", "",
              "**Cổng.** Có một ngưỡng t mà TPR = bắt / 44 ≥ 0,5 và FPR = gắn nhầm / 102 ≤ 6/102 = 0,059.",
              "",
              "**Mô hình nhị chuẩn.** Giả sử điểm P(NOT_CLAIM) của tuyên bố thật ~ N(0, 1) và của câu không phải tuyên bố "
              "~ N(d′, 1). Khi đó TPR = Φ(d′ + Φ⁻¹(FPR)). Đặt TPR = 0,5 và FPR = 6/102:",
              "",
              f"  d′ ≥ Φ⁻¹(0,5) − Φ⁻¹(0,059) = 0 + 1,565 = **{t1['need_d']}**, tương đương AUC = Φ(d′/√2) ≥ **{t1['need_auc']}**.",
              "",
              f"**Đo được.** Trên {t1['points']} điểm (4 cấu hình × 6 ngưỡng), d′ trung vị là **{t1['median_d']}** "
              f"(AUC ≈ {t1['median_auc']}), d′ lớn nhất {b['d']:.2f} ({b['run']}, t = {b['t']}). "
              f"Với d′ = {t1['median_d']}, khi đã giữ FPR = 6/102 thì TPR chỉ còn Φ({t1['median_d']} − 1,565) = "
              f"**{t1['tpr_at_gate_median_d']}**, khoảng {round(44 * t1['tpr_at_gate_median_d'])}/44, xa mức 22/44 cổng cần. "
              f"Điểm có d′ lớn nhất bắt {b['caught']}/44 nhưng gắn nhầm {b['flag']}/102 "
              f"(Wilson 95% cho FPR: {t1['wilson_best_fpr']}).",
              "",
              "**Vì sao d′ thấp dù kiểm chéo nội bộ T1 đạt macro-F1 0,72–0,74.** Mô hình tách tốt các lớp *theo định nghĩa T1*, "
              "nhưng 102 câu GS-Eval được tính là tuyên bố có nhiều câu mà sổ tay T1 gọi là không phải tuyên bố (dòng bảng, câu "
              "cơ chế chung, câu của tổ chức khác). Đây là nhiễu nhãn giữa hai định nghĩa: phần chồng lấn của hai phân phối điểm "
              "nằm ở chính định nghĩa, nên không mô hình nào học được chỉ từ T1. Q13 v1.2 mới chuyển 31 câu nên d′ chỉ tăng ít "
              "(gắn nhầm ở ngưỡng 0,5 giảm từ 26 xuống 21–25).",
              "",
              "**Muốn qua:** cần d′ ≥ 1,57. Muốn vậy phải thống nhất định nghĩa nhãn T1 với GS-Eval. Cách làm: đọc các câu "
              "bị gắn nhầm (notebook `gs-off-t1-q13-v2` xuất xác suất từng câu), sửa sổ tay, gán lại, rồi huấn luyện lại. "
              "Chọn ngưỡng khác không đủ, vì đường ROC đã nằm dưới vùng đạt.", "", "![](hinh_mo_hinh/t1_roc_dprime.png)", ""]
    if st:
        r = {x["label"]: x for x in st["rows"]}
        L += ["## 2. mDeBERTa chấm quan hệ: không hơn luật và quá chậm", "",
              f"**Học được gì trên 821 cặp (kiểm chéo theo DN, n = {st['n']}).** Với κ Cohen = (p_o − p_e)/(1 − p_e) tính từ "
              f"ma trận nhầm lẫn, đo được **κ = {st['kappa']}**, gần như bằng 0: mô hình không khớp nhãn hơn đoán theo tỉ lệ. "
              "Với lift = precision / tỉ lệ nền: "
              + "; ".join(f"{x['label']} {x['precision']} / {x['prior']} = **{x['lift']}**" for x in st["rows"])
              + ". PARTIAL có lift ≈ 1, tức không hơn đoán bừa.",
              "",
              f"**Vì sao.** (1) Đầu phân loại NLI (entailment / neutral / contradiction) bị khởi tạo lại thành 4 lớp "
              "(`ignore_mismatched_sizes`). Như vậy đã bỏ đúng phần tri thức \"hỗ trợ\" mà bản chưa tinh chỉnh có sẵn: NLI "
              f"chưa tinh chỉnh đạt {st['nli']}, cao hơn bản tinh chỉnh {st['cv_macro']}. "
              f"(2) Lớp thiểu số rất ít: SUPPORTS {r.get('SUPPORTS', {}).get('support')} cặp, mỗi fold huấn luyện còn "
              "khoảng 4/5 số đó, lại trải trên 11 doanh nghiệp. Phần lớn SUPPORTS là đoạn lặp lại tuyên bố (cờ `lap_lai`), nên "
              "mô hình học \"giống chữ\" thay vì \"xác nhận\". (3) Ranh giới PARTIAL / CONTEXT phụ thuộc kỳ, phạm vi, mục tiêu "
              "(R3, R7), tức là so năm và số. Đó là việc của code, không phải của một bộ mã hoá 280 triệu tham số học từ "
              "vài trăm ví dụ.",
              "",
              f"**S5 (391 cặp ngoài).** Mô hình đạt macro-F1(S,O) = {st['s5_model']} {st['s5_model_ci']}; luật tính cùng cách gộp "
              f"(PARTIAL tính là S) đạt {st['s5_rules']} {st['s5_rules_ci']}. Cổng đăng ký so với 0,397, là số của luật tính theo "
              "cách gộp cũ ở llm_stages_v1. Theo chữ thì CI dưới vượt 0,397, nhưng so cùng cách gộp thì mô hình **không hơn "
              "luật**. Ghi nhận: không dùng.",
              "",
              f"**Tốc độ.** FLOPs(L) ≈ 12 · [2(4d² + 2d·d_ff)·L + 3·4·L²·d], với d = 768, d_ff = 3072. Ở L = 384 ra "
              f"{st['gflops_384']} GFLOP mỗi cặp. Đo được {st['cpu_ms']} ms, tức thông lượng hiệu dụng khoảng "
              f"{st['throughput_gflops']} GFLOP/s. Muốn ≤ 300 ms ở cùng thông lượng thì L ≤ **{st['L_ok']}** token; nếu lượng "
              f"tử int8 (nhanh khoảng 2 lần) thì L ≤ {st['L_ok_int8']}. Laptop i7-1355U (AVX2, 2 nhân P) có thể chậm hơn CPU "
              "Kaggle.",
              "",
              "**Muốn qua:** giữ đầu NLI và ánh xạ entailment → SUPPORTS/PARTIAL, neutral → CONTEXT, contradiction → "
              "CONTRADICTS. Cắt cặp còn khoảng 256 token, lượng tử int8, rồi chấm lại; khi đó nhãn vàng mới đủ để xét cổng.",
              "", "![](hinh_mo_hinh/stance_kappa_lift.png)", ""]
    DOC.write_text("\n".join(L), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(ROOT / "deploy/vastai_a100/out_kaggle/merged"))
    a = ap.parse_args()
    res = Path(a.results)
    FIG.mkdir(parents=True, exist_ok=True)
    made: list[str] = []
    t1 = st = None
    if (res / "t1/metrics.json").exists():
        t1 = t1_part(json.loads((res / "t1/metrics.json").read_text(encoding="utf-8")), made)
    if (res / "stance/metrics.json").exists():
        st = stance_part(json.loads((res / "stance/metrics.json").read_text(encoding="utf-8")), made)
    nl = None
    if (res / "stance_nli/metrics.json").exists():
        nl = nli_part(json.loads((res / "stance_nli/metrics.json").read_text(encoding="utf-8")))
    ls = label_stats()
    write_doc(t1, st, nl, ls)
    print(json.dumps({"nli": nl, "labels": ls}, ensure_ascii=False, default=str)[:1200])
    print(f"-> {made}, {DOC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
