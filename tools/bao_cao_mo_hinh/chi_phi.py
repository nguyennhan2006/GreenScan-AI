"""Bảng so sánh chi phí và thời gian của các phương án chạy GreenScan, xuất ảnh PNG.

    .venv/Scripts/python.exe -X utf8 tools/bao_cao_mo_hinh/chi_phi.py [--out docs/04-data-ai/hinh_mo_hinh]

Đọc configs/chi_phi_gia_dinh.yaml (mỗi số có ghi nguồn). Ghi: chi_phi_bang.png (bảng), chi_phi_thang.png (chi phí
tháng và thời gian mỗi bộ hồ sơ), chi_phi_huan_luyen.png (chi phí huấn luyện), chi_phi.json (số liệu đã tính).
Giá GPU dùng mức giữa; thanh lỗi là khoảng thấp–cao của giá thuê.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import yaml  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def options(c: dict) -> list[dict]:
    r, s, u, g = c["report"], c["seconds_per_text"], c["usage"], c["gpu_usd_per_hour"]
    month_reports = u["reports_per_month"]
    laptop_vnd_h = c["laptop"]["watts"] / 1000 * c["laptop"]["vnd_per_kwh"]
    usd = c["usd_vnd"]
    out = []

    def add(name, plan, secs, usd_month, usd_rng, note, data_out):
        out.append({"phuong_an": plan, "ten": name, "giay_moi_bo": round(secs), "usd_thang": round(usd_month, 1),
                    "usd_thang_khoang": [round(x, 1) for x in usd_rng], "vnd_moi_bo": round(usd_month * usd / month_reports),
                    "ghi_chu": note, "du_lieu_ra_ngoai": data_out})

    # Phương án 1: ngoại tuyến hoàn toàn trên laptop
    secs = r["rules_seconds"]
    e = secs / 3600 * laptop_vnd_h * month_reports / usd
    add("Laptop, chỉ luật", "PA1", secs, e, (e, e), "bản nộp hiện tại", "không")
    secs = r["rules_seconds"] + r["stance_texts"] * s["laptop_cpu_mdeberta_stance"]
    e = secs / 3600 * laptop_vnd_h * month_reports / usd
    add("Laptop + mô hình CPU đã huấn luyện", "PA1", secs, e, (e, e), "mDeBERTa chấm quan hệ, e5 lọc tuyên bố", "không")
    secs = r["rules_seconds"] + r["explain_items"] * s["laptop_ollama_4b_explain"]
    e = secs / 3600 * laptop_vnd_h * month_reports / usd
    add("Laptop + Qwen3-4B viết lời giải thích", "PA1", secs, e, (e, e), "Ollama Q4; chậm nhưng không cần mạng", "không")

    # Phương án 2: máy GPU tự thuê (vast.ai)
    texts = r["stance_texts"] + r["explain_items"]
    for key, label, sp in (("a100_80gb", "vast.ai A100 80 GB (gpt-oss-120b)", s["a100_vllm_gptoss"]),
                           ("rtx_4090_24gb", "vast.ai RTX 4090 (Qwen3-14B)", s["rtx4090_vllm_14b"])):
        secs = r["rules_seconds"] + texts * sp
        on = u["server_hours_per_day"] * u["work_days_per_month"]
        add(label + ", bật giờ hành chính", "PA2", secs, g[key]["mid"] * on,
            (g[key]["low"] * on, g[key]["high"] * on), f"{on} giờ/tháng, đọc mọi tuyên bố có số", "chỉ cặp tuyên bố–đoạn, về máy nhóm thuê")
        per_run_h = secs / 3600 + u["spinup_minutes"] / 60
        add(label + ", thuê theo lượt", "PA2", secs + u["spinup_minutes"] * 60, g[key]["mid"] * per_run_h * month_reports,
            (g[key]["low"] * per_run_h * month_reports, g[key]["high"] * per_run_h * month_reports),
            f"bật máy {u['spinup_minutes']} phút mỗi bộ", "chỉ cặp tuyên bố–đoạn, về máy nhóm thuê")

    # Tham chiếu: API đám mây (chỉ tài liệu công khai)
    p = c["api_usd_per_mtok"]["groq_gpt_oss_120b"]
    tok_in = r["stance_texts"] * r["tokens_stance"]["in"] + r["explain_items"] * r["tokens_explain"]["in"]
    tok_out = r["stance_texts"] * r["tokens_stance"]["out"] + r["explain_items"] * r["tokens_explain"]["out"]
    per = (tok_in * p["in"] + tok_out * p["out"]) / 1e6
    secs = r["rules_seconds"] + texts * s["groq_api"]
    add("API Groq gpt-oss-120b (tham chiếu)", "Đám mây", secs, per * month_reports, (per * month_reports,) * 2,
        "chỉ được dùng cho báo cáo công khai", "có, ra nước ngoài")
    return out


def table_png(rows, out: Path, c: dict):
    cols = ["Phương án", "Cấu hình", "Thời gian / bộ", "USD / tháng", "VND / bộ", "Dữ liệu ra ngoài", "Ghi chú"]
    cells = [[r["phuong_an"], r["ten"], f"{r['giay_moi_bo'] // 60} ph {r['giay_moi_bo'] % 60:02d} s",
              f"{r['usd_thang']:,.1f}" + (f" ({r['usd_thang_khoang'][0]:,.0f}–{r['usd_thang_khoang'][1]:,.0f})"
                                          if r["usd_thang_khoang"][0] != r["usd_thang_khoang"][1] else ""),
              f"{r['vnd_moi_bo']:,}".replace(",", "."), r["du_lieu_ra_ngoai"], r["ghi_chu"]] for r in rows]
    fig, ax = plt.subplots(figsize=(14, 0.32 * len(rows) + 0.9))
    ax.axis("off")
    t = ax.table(cellText=cells, colLabels=cols, loc="center", cellLoc="left", colLoc="left")
    t.auto_set_font_size(False)
    t.set_fontsize(8)
    t.scale(1, 1.35)
    t.auto_set_column_width(list(range(len(cols))))
    for (i, _), cell in t.get_celld().items():
        if i == 0:
            cell.set_facecolor("#1f6f5c")
            cell.set_text_props(color="white", weight="bold")
        elif rows[i - 1]["phuong_an"] == "PA1":
            cell.set_facecolor("#eef6f3")
        elif rows[i - 1]["phuong_an"] == "PA2":
            cell.set_facecolor("#fbf6e6")
    u = c["usage"]
    ax.set_title(f"So sánh chi phí: {u['reports_per_month']} bộ hồ sơ/tháng · giá {c['date']} · "
                 f"khoảng trong ngoặc = giá thuê thấp–cao", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "chi_phi_bang.png")
    plt.close(fig)


def bars_png(rows, out: Path):
    col = {"PA1": "#1f6f5c", "PA2": "#c9a227", "Đám mây": "#8a8f98"}
    names = [r["ten"] for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
    v = [r["usd_thang"] for r in rows]
    err = [[x - r["usd_thang_khoang"][0] for x, r in zip(v, rows)], [r["usd_thang_khoang"][1] - x for x, r in zip(v, rows)]]
    axes[0].barh(names, v, xerr=err, color=[col[r["phuong_an"]] for r in rows], capsize=3)
    for i, x in enumerate(v):
        axes[0].text(x, i, f" {x:,.0f} USD", va="center", fontsize=8)
    axes[0].set_xlabel("USD / tháng")
    axes[0].set_title("Chi phí tháng")
    axes[0].invert_yaxis()
    m = [r["giay_moi_bo"] / 60 for r in rows]
    axes[1].barh(names, m, color=[col[r["phuong_an"]] for r in rows])
    for i, x in enumerate(m):
        axes[1].text(x, i, f" {x:.1f} ph", va="center", fontsize=8)
    axes[1].set_xlabel("phút / bộ hồ sơ")
    axes[1].set_title("Thời gian xử lý một bộ hồ sơ")
    axes[1].invert_yaxis()
    axes[1].set_yticks([])
    fig.suptitle("Xanh: PA1 ngoại tuyến · vàng: PA2 GPU tự thuê · xám: API đám mây (tham chiếu)")
    fig.tight_layout()
    fig.savefig(out / "chi_phi_thang.png")
    plt.close(fig)


def training_png(c: dict, out: Path) -> dict:
    g, h = c["gpu_usd_per_hour"], c["training_gpu_hours"]
    rows = [("Kaggle T4 (PA1)", h["kaggle_t4"], 0.0, 0.0, 0.0),
            ("vast.ai A100 (PA2)", h["a100"], h["a100"] * g["a100_80gb"]["low"], h["a100"] * g["a100_80gb"]["mid"],
             h["a100"] * g["a100_80gb"]["high"])]
    fig, ax = plt.subplots(figsize=(7, 1.6))
    ax.axis("off")
    t = ax.table(cellText=[[n, f"{hh:.1f}", f"{mid:.2f} ({lo:.2f}–{hi:.2f})"] for n, hh, lo, mid, hi in rows],
                 colLabels=["Nơi huấn luyện", "Giờ GPU", "USD"], loc="center", cellLoc="left")
    t.auto_set_font_size(False)
    t.set_fontsize(9)
    ax.set_title("Chi phí huấn luyện toàn bộ mô hình (một lần)", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "chi_phi_huan_luyen.png")
    plt.close(fig)
    return {n: {"gio_gpu": hh, "usd": [lo, mid, hi]} for n, hh, lo, mid, hi in rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "configs" / "chi_phi_gia_dinh.yaml"))
    ap.add_argument("--out", default=str(ROOT / "docs" / "04-data-ai" / "hinh_mo_hinh"))
    a = ap.parse_args()
    c = yaml.safe_load(open(a.config, encoding="utf-8"))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = options(c)
    table_png(rows, out, c)
    bars_png(rows, out)
    train = training_png(c, out)
    (out / "chi_phi.json").write_text(json.dumps({"config": c["version"], "date": c["date"], "rows": rows,
                                                  "training": train}, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows:
        print(f"{r['phuong_an']:8} {r['ten'][:46]:46} {r['giay_moi_bo']:>5} s  {r['usd_thang']:>8} USD/tháng")
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
