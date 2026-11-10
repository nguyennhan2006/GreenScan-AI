"""GS-Bench v1, step 2: keep figures two readers agree on, generate labelled claims, merge the 51 constructed cases.

Reader A: Claude, one pass over candidates.jsonl (ir_claude.jsonl).
Reader B: deterministic checks against the sentence itself (verbatim value / unit / year / multiplier, and
cue words for target, change, intensity, scope). A figure is kept only when B finds nothing against A.

Claims are generated from the kept evidence figure. The label of each claim follows from the perturbation
family (definition below), NOT from irlib: irlib is one of the systems under test. `selfcheck` reports
where irlib disagrees with the family label (a bug in one of the two).

    S0 restate               S   same figure, template sentence
    S1 rounded               S   "khoảng 1,2 triệu" for 1.234.567 (within the published precision)
    C1 value changed         C   value moved well beyond both tolerances
    C2 magnitude             C   multiplier one step up (15.000 m3 -> 15.000 nghìn m3)
    C3 direction             C   "giảm" <-> "tăng" for a change
    N1 period                N   the year before
    N2 status                N   actual <-> target
    N3 scope                 N   another GHG scope
    N4 boundary              N   a named facility's figure claimed for the whole group
    N5 basis                 N   absolute value claimed as an intensity
    N6 metric                N   a neighbouring metric with the same unit

usage (repository root): .venv/Scripts/python.exe -I benchmark/gs_bench_v1/build.py
"""
from __future__ import annotations

import hashlib, json, math, re, sys, unicodedata
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "size_ladder_2026-10-10"))
from irlib import IR, compare, parse_number, unit_dimension  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
SECTOR = {"tra": "dược", "dhg": "dược", "bvh": "bảo hiểm", "pnj": "bán lẻ trang sức", "vnm": "sữa", "ctd": "xây dựng",
          "pow": "điện", "pan": "nông nghiệp – thực phẩm", "cdn": "cảng biển", "sab": "đồ uống", "dpr": "cao su"}
TARGET_CUE = re.compile(r"mục tiêu|kế hoạch|phấn đấu|cam kết|định hướng|dự kiến|hướng tới|lộ trình|đến năm 20\d\d|vào năm 20\d\d", re.I)
CHANGE_CUE = re.compile(r"giảm|tăng|tiết kiệm|cắt giảm|so với", re.I)
MULT_AFTER = re.compile(r"^\s*(nghìn|ngàn|triệu|tỷ|tỉ)\b", re.I)
NEIGHBOUR = {
    "water_use": ("wastewater", "lượng nước thải"), "wastewater": ("water_use", "lượng nước sử dụng"),
    "waste_generated": ("waste_recycled", "lượng chất thải được tái chế"),
    "waste_recycled": ("waste_generated", "lượng chất thải phát sinh"),
    "hazardous_waste": ("waste_generated", "tổng lượng chất thải phát sinh"),
    "electricity_consumption": ("renewable_energy", "lượng điện từ năng lượng tái tạo"),
    "renewable_energy": ("electricity_consumption", "tổng lượng điện tiêu thụ"),
    "energy_consumption": ("electricity_consumption", "lượng điện tiêu thụ"),
}
NEXT_MULT = {"": "nghìn", "nghìn": "triệu", "ngàn": "triệu", "triệu": "tỷ"}


def h(*parts) -> int:
    return int(hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest(), 16)


def reader_b(fig: dict, text: str) -> str | None:
    """Reason to reject reader A's figure, or None when nothing in the sentence contradicts it."""
    low = text.lower()
    v = fig.get("value_text") or ""
    if fig.get("confidence") == "low":
        return "A không chắc"
    if not v or v not in text:
        return "số không có nguyên văn"
    try:
        parse_number(v)
    except ValueError:
        return "không đọc được số"
    unit = (fig.get("unit_text") or "").strip()
    if not unit or unit.lower() not in low:
        return "đơn vị không có nguyên văn"
    after = text[text.index(v) + len(v):]
    mult = (fig.get("multiplier_text") or "").strip().lower()
    if bool(mult) != bool(MULT_AFTER.match(after)) or (mult and not after.strip().lower().startswith(mult)):
        return "bội số không khớp câu"
    for key in ("period", "baseline_year"):
        if fig.get(key) not in (None, "") and str(fig[key]) not in text:
            return f"{key} không có trong câu"
    if (fig.get("status") == "target") != bool(TARGET_CUE.search(text)):
        return "thực hiện / mục tiêu không khớp từ báo hiệu"
    if fig.get("value_kind") == "change" and not CHANGE_CUE.search(text):
        return "change nhưng câu không có từ tăng/giảm"
    if ("/" in unit) != (fig.get("value_kind") == "intensity"):
        return "cường độ không khớp đơn vị có '/'"
    if unit_dimension(unit)[0] == "percent" and fig.get("value_kind") in ("absolute", "count"):
        return "% nhưng loại giá trị là tuyệt đối"
    if fig.get("scope") and not re.search(r"phạm vi|scope", low):
        return "có scope nhưng câu không nêu phạm vi"
    if fig.get("metric") not in NEIGHBOUR and fig.get("metric") not in (
            "ghg_emissions", "fuel_consumption", "recycled_input", "air_pollutants", "land_trees", "other_env"):
        return "mã chỉ số lạ"
    return None


def fmt(value: float, decimals: int) -> str:
    """Vietnamese number: 1.234.567 and 23,5."""
    s = f"{value:,.{decimals}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


SCOPE_TEXT = {"s1": "phạm vi 1", "s2": "phạm vi 2", "s3": "phạm vi 3", "s1+s2": "phạm vi 1 và 2", "s1+s2+s3": "phạm vi 1, 2 và 3"}


def sentence(ir: IR) -> str:
    subject = ir.subject_text or "Công ty"
    metric = ir.metric_text or ir.metric
    if ir.scope:  # v1.1 wrote no scope: S0 and N3 of one PV Power figure were the same sentence with labels S and N
        metric = re.sub(r"\s*phạm vi [\d, và+]+", "", metric).strip() + " " + SCOPE_TEXT.get(ir.scope, ir.scope)
    qty = " ".join(x for x in (ir.value_text, ir.multiplier_text, ir.unit_text) if x)
    if ir.unit_text.strip() == "%":
        qty = f"{ir.value_text}%"
    year = f"năm {ir.period}" if ir.period else ""
    if ir.status == "target":
        verb = {"decrease": "giảm", "increase": "tăng"}.get(ir.change_direction or "", "đạt")
        tail = f" vào {year}" if year else ""
        out = f"{subject} đặt mục tiêu {metric} {verb} {qty}{tail}."
        return out[0].upper() + out[1:]
    lead = f"{year[0].upper() + year[1:]}, " if year else ""
    if ir.value_kind == "change":
        verb = "giảm" if ir.change_direction == "decrease" else "tăng"
        base = f" so với năm {ir.baseline_year}" if ir.baseline_year else ""
        out = f"{lead}{metric} của {subject} {verb} {qty}{base}."
        return out[0].upper() + out[1:]
    verb = "đạt" if ir.value_kind == "share" else "là"
    out = f"{lead}{metric} của {subject} {verb} {qty}."
    return out[0].upper() + out[1:]


def variants(ev: IR, key: str) -> list[tuple[str, str, IR]]:
    if ev.value_kind == "change":  # "mức giảm tiêu thụ gas … tăng 1,4%" reads as nonsense
        ev = IR.from_dict(ev.as_dict())
        ev.metric_text = re.sub(r"(?:mức )?(?:cắt giảm|giảm|tăng|tiết kiệm)\s+", "", unicodedata.normalize("NFC", ev.metric_text), flags=re.I)
    base = IR.from_dict(ev.as_dict())
    if base.boundary == "facility":
        base.subject_text = base.subject_text or "Nhà máy"
    out = [("S0 restate", "S", base)]
    value, half = parse_number(ev.value_text)
    decimals = max(0, -round(math.log10(half * 2))) if half < 0.5 else 0
    if ev.value_kind in ("absolute", "count", "intensity") and not ev.multiplier_text and value >= 10_000:
        scale, word = (1e6, "triệu") if value >= 1e6 else (1e3, "nghìn")
        r = IR.from_dict(ev.as_dict()); r.value_text, r.multiplier_text = fmt(round(value / scale, 1), 1), word
        r.metric_text = r.metric_text or r.metric
        out.append(("S1 rounded", "S", r))
    c = IR.from_dict(ev.as_dict())
    if unit_dimension(ev.unit_text)[0] == "percent":
        new = value + 15 if value <= 80 else value - 15
    else:
        new = value * (0.7, 0.8, 1.25, 1.4)[key % 4]
        if abs(new - value) <= 4 * half:  # small integers: 5 -> 4 is inside 0,5 + 0,5
            new = value + 10 * half * max(1, value / (20 * half))
    c.value_text = fmt(new, decimals)
    out.append(("C1 value", "C", c))
    if ev.value_kind in ("absolute", "count") and value != 0 and (ev.multiplier_text or "").lower() in NEXT_MULT \
            and unit_dimension(ev.unit_text)[0] not in ("percent", "count_tree"):
        m = IR.from_dict(ev.as_dict()); m.multiplier_text = NEXT_MULT[(ev.multiplier_text or "").lower()]
        out.append(("C2 magnitude", "C", m))
    if ev.value_kind == "change" and ev.change_direction in ("decrease", "increase"):
        d = IR.from_dict(ev.as_dict()); d.change_direction = "increase" if ev.change_direction == "decrease" else "decrease"
        out.append(("C3 direction", "C", d))
    if ev.period and not (ev.value_kind == "change" and ev.baseline_year and ev.period - 1 <= ev.baseline_year):
        p = IR.from_dict(ev.as_dict()); p.period = ev.period - 1
        out.append(("N1 period", "N", p))
    s = IR.from_dict(ev.as_dict())
    s.status = "actual" if ev.status == "target" else "target"
    if s.status == "target" and (not s.period or s.period < 2026):  # a target for a past year reads oddly
        s.period = 2030
    if s.status == "actual":  # "Năm 2030, … là X" reads oddly; an undated result claim says the same
        s.period = None
    out.append(("N2 status", "N", s))
    if ev.metric == "ghg_emissions" and ev.scope:
        g = IR.from_dict(ev.as_dict()); g.scope = {"s1": "s1+s2", "s1+s2": "s1", "s2": "s1", "s3": "s1+s2+s3"}.get(ev.scope, "s1")
        out.append(("N3 scope", "N", g))
    if ev.boundary == "facility":
        b = IR.from_dict(ev.as_dict()); b.boundary, b.subject_text = "group", "Tập đoàn"
        out.append(("N4 boundary", "N", b))
    if ev.value_kind == "absolute" and ev.unit_text and "/" not in ev.unit_text and unit_dimension(ev.unit_text)[0] != "percent":
        i = IR.from_dict(ev.as_dict()); i.value_kind, i.unit_text = "intensity", ev.unit_text + "/tấn sản phẩm"
        out.append(("N5 basis", "N", i))
    if ev.metric in NEIGHBOUR:
        n = IR.from_dict(ev.as_dict()); n.metric, n.metric_text = NEIGHBOUR[ev.metric]
        out.append(("N6 metric", "N", n))
    return out


def constructed() -> list[dict]:
    rows = []
    for module, layer in (("cases", "B-a sạch"), ("cases_noisy", "B-a trang thật")):
        for cid, family, claim, evidence, ok in __import__(module).CASES:
            rows.append({"id": f"ba-{cid}", "layer": layer, "company": "dựng" if module == "cases" else "hpg",
                         "sector": "thép", "family": family, "claim": claim, "evidence": evidence, "labels": sorted(ok)})
    return rows


def main() -> None:
    # batch 1 (211 sentences, Claude) and batch 2 (800 sentences, Claude Haiku, 31/10)
    pairs = [("candidates.jsonl", "ir_claude.jsonl"), ("candidates_v2.jsonl", "ir_claude_v2.jsonl")]
    sentences, readings = {}, []
    for cand, ir in pairs:
        if (HERE / ir).exists():
            sentences.update({r["id"]: r for r in map(json.loads, (HERE / cand).open(encoding="utf-8"))})
            readings += [json.loads(line) for line in (HERE / ir).open(encoding="utf-8")]
    rejected, kept, cases, mismatches = Counter(), [], [], []
    for rec in readings:
        src = sentences[rec["id"]]
        for j, fig in enumerate(rec.get("figures") or []):
            why = reader_b(fig, src["text"])
            if why:
                rejected[why] += 1
                continue
            kept.append((src, j, IR.from_dict(fig)))
    for src, j, ev in kept:
        key = h(src["id"], j)
        for family, label, claim_ir in variants(ev, key):
            claim = sentence(claim_ir)
            got, why = compare(claim_ir, ev)
            if got != label:
                mismatches.append({"family": family, "claim": claim, "evidence": src["text"], "irlib": got, "why": why})
            cases.append({"id": f"bb-{src['id']}-{j}-{family.split()[0]}", "layer": "B-b", "company": src["company_id"],
                          "sector": SECTOR.get(src["company_id"], "?"), "family": family, "claim": claim,
                          "evidence": src["text"], "labels": [label], "claim_ir": claim_ir.as_dict(), "evidence_ir": ev.as_dict(),
                          "fold": h(src["company_id"]) % 5})
    rows = constructed() + cases
    with (HERE / "gs_bench_v1.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    stats = {
        "sentences": len(readings), "figures_read": sum(len(r.get("figures") or []) for r in readings),
        "figures_kept": len(kept), "rejected_by_reader_b": dict(rejected.most_common()),
        "cases_total": len(rows), "B-a": len(rows) - len(cases), "B-b": len(cases),
        "B-b_by_label": dict(Counter(c["labels"][0] for c in cases)), "B-b_by_family": dict(Counter(c["family"] for c in cases)),
        "B-b_by_company": dict(Counter(c["company"] for c in cases)), "irlib_vs_family_mismatches": len(mismatches),
    }
    (HERE / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "selfcheck_mismatches.jsonl").write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in mismatches), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
