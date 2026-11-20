"""Score GS-Mutation v1 outputs: pass rate per planted error, split and configuration, with Wilson 95% CIs.

usage (repo root): .venv/Scripts/python.exe -I benchmark/gs_mutation_v1/score.py
writes benchmark/gs_mutation_v1/results.json and RESULTS.md
"""
from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIGS = ("before", "after", "v2", "internal", "contradict")
WHAT = {
    "M0": "bản gốc không thành CONTRADICTED (1 − tỉ lệ vu oan)",
    "M1": "phóng đại số → CONTRADICTED",
    "M2": "đảo hướng tăng/giảm → CONTRADICTED",
    "M3": "lùi năm gốc → không còn SUPPORTED",
    "M4": "xoá phạm vi → báo thiếu phạm vi",
    "M5": "tuyệt đối hoá (X% → 100%, phần lớn → toàn bộ) → không còn SUPPORTED",
    "M6": "chèn từ quảng bá mơ hồ → cờ mơ hồ hoặc cờ ngôn ngữ quảng bá",
    "M7": "thay bằng chứng của công ty khác → không còn SUPPORTED",
    "M8": "đổi đơn vị (tấn → kg, kWh → MWh, triệu ↔ nghìn) → không còn SUPPORTED",
    "M9": "phóng to ranh giới (nhà máy → toàn Tập đoàn) → không còn SUPPORTED",
    "M10": "mục tiêu viết thành đã đạt → không còn SUPPORTED",
    "M11": "cường độ viết thành tổng phát thải → không còn SUPPORTED",
    "M0i": "một tài liệu, bản gốc → không thành CONTRADICTED",
    "M1i": "một tài liệu, phóng đại số → CONTRADICTED hoặc cờ không nhất quán nội bộ",
}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centre - half), min(1.0, centre + half))


def passes(case: dict, out: dict) -> bool:
    exp, rows = case["expected"], out["verifications"]
    statuses = {r["status"] for r in rows}
    if "not" in exp:
        return not (statuses & set(exp["not"]))
    if "any" in exp:
        return bool(statuses & set(exp["any"])) or bool(
            exp.get("or_flag") and any(exp["or_flag"] in r["flags"] for r in rows))
    if "missing" in exp:
        return any(any(m == exp["missing"] or "phạm vi" in m for m in r["missing"]) for r in rows)
    if "vague" in exp:
        return any(r["vague"] or r.get("promo") for r in rows)
    raise ValueError(exp)


def main() -> None:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    cases = {c["case_id"]: c for c in map(json.loads, (HERE / "cases.jsonl").open(encoding="utf-8")) if c}
    results: dict = {"date": date.today().isoformat(), "n_cases": len(cases), "configs": {}}
    for config in CONFIGS:
        path = HERE / "out" / f"{config}.jsonl"
        if not path.exists():
            continue
        outs = {o["case_id"]: o for o in map(json.loads, path.open(encoding="utf-8"))}
        table = {}
        for kind in WHAT:
            for split in ("dev", "test", "all"):
                sel = [c for c in cases.values() if c["mutation"] == kind and (split == "all" or c["split"] == split)
                       and c["case_id"] in outs]
                if not sel:
                    continue
                k = sum(passes(c, outs[c["case_id"]]) for c in sel)
                lo, hi = wilson(k, len(sel))
                table[f"{kind}/{split}"] = {"n": len(sel), "pass": k, "rate": round(k / len(sel), 3),
                                            "ci95": [round(lo, 3), round(hi, 3)]}
        m0 = [c for c in cases.values() if c["mutation"] == "M0" and c["base_label"] == "S" and c["case_id"] in outs]
        table["M0_S_still_supported/all"] = {
            "n": len(m0), "pass": sum("SUPPORTED" in {r["status"] for r in outs[c["case_id"]]["verifications"]} for c in m0)}
        errors = sum(1 for o in outs.values() if o.get("error"))
        seconds = sum(o["seconds"] for o in outs.values())
        results["configs"][config] = {"table": table, "errors": errors, "n_run": len(outs),
                                      "mean_seconds": round(seconds / max(len(outs), 1), 2)}
    (HERE / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")

    lines = [f"# GS-Mutation v1: kết quả ({results['date']})", "",
             "Ngưỡng đăng ký trước: `PREREG_2026-11-14.md`. Tỉ lệ kèm khoảng tin cậy Wilson 95%.", ""]
    shown = [c for c in CONFIGS if c in results["configs"]]
    lines.append("| Kiểu | Đúng khi | Tập | " + " | ".join(shown) + " |")
    lines.append("|---|---|---|" + "---|" * len(shown))
    for kind, what in WHAT.items():
        for split in ("dev", "test"):
            key = f"{kind}/{split}"
            cells = []
            for config in shown:
                t = results["configs"][config]["table"].get(key)
                cells.append(f"{t['pass']}/{t['n']} = {t['rate'] * 100:.0f}% [{t['ci95'][0] * 100:.0f}–{t['ci95'][1] * 100:.0f}]"
                             if t else "—")
            if any(c != "—" for c in cells):
                lines.append(f"| {kind} | {what} | {split} | " + " | ".join(cells) + " |")
    lines += ["", "Lỗi chạy: " + ", ".join(f"{c} {results['configs'][c]['errors']}/{results['configs'][c]['n_run']}" for c in shown),
              "Thời gian trung bình mỗi ca (giây): " + ", ".join(f"{c} {results['configs'][c]['mean_seconds']}" for c in shown)]
    (HERE / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
