"""Partial-offline pilot: the cloud model never sees figures or entity names.

Locally: every quantity in the claim and the evidence is replaced by a slot
(<S1>, <E1>, ...) whose value stays on this machine; units, years and scope
labels stay in the text because they carry meaning and are not sensitive;
company / facility names become [DOANH_NGHIỆP], [CƠ_SỞ_A] ...
Remotely: the model only says which evidence slot (or sum / change between two
slots) measures the same thing as each claim slot.
Locally again: the values are put back and compared with the precision the
figure was published to.

usage: run_masked.py <out.json> [model ...]     (run from the repository root)
       LADDER_CASES=cases_noisy ... for the real-page set
"""
from __future__ import annotations

import json, os, re, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(__file__))
CASES = __import__(os.environ.get("LADDER_CASES", "cases")).CASES
os.environ.setdefault("QUANTUM_RUNS_DIR", tempfile.mkdtemp(prefix="gs-masked-runs-"))

import quantum_gw.utils.text as T  # noqa: E402
from quantum_gw.providers.router import ModelGateway  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
out_path = sys.argv[1]
MODELS = sys.argv[2:] or ["gemma-4-31B-it", "GLM-5.2"]

# Names that identify the reporting entity or its sites. In the product these
# come from the run's entity resolution and the documents' metadata.
ENTITIES = [
    (r"T[ậa]p\s+đo[àa]n\s+H[òo]a\s+Ph[áa]t|H[òo]a\s+Ph[áa]t", "[DOANH_NGHIỆP]"),
    (r"Dung\s+Qu[ấa]t", "[CƠ_SỞ_A]"),
    (r"H[ảa]i\s+D[ươ]ơng", "[CƠ_SỞ_B]"),
]
_NUM = re.compile(r"(?<![\w./:\-])(\d[\d.,]*\d|\d)(?![\d/])")
_MULT_WORD = re.compile(r"\s*(triệu|tỷ|tỉ|nghìn|ngàn)(?!\w)", re.IGNORECASE)
_MULT = {"triệu": 1e6, "tỷ": 1e9, "tỉ": 1e9, "nghìn": 1e3, "ngàn": 1e3}
_RANGE = re.compile(r"(?<![\w./:])(\d[\d.,]*)\s*[-–]\s*(\d[\d.,]*)(?![\d/])")
_STANDARD_BEFORE = re.compile(r"(iso|tcvn|qcvn|iec|en|astm|gri)\s*$")
_SCOPE_BEFORE = re.compile(r"(pham vi|scope)\s*(?:[123]\s*(?:,|va|and|&|\+)?\s*)*$")


def _tolerance(raw: str, value: float, mult: float, unit: str | None) -> float:
    """Half of the last published digit. A percentage is read at its written
    decimals ("20%" = ±0.5, "12,0%" = ±0.05); for other figures trailing zeros
    may be rounding (project rule), capped at 1% of the value so "1.000.000"
    does not swallow a 50% difference."""
    if unit == "%":
        decimals = len(re.split(r"[.,]", raw.strip(".,"))[1]) if re.search(r"[.,]\d+$", raw) else 0
        return 0.5 * 10 ** (-decimals)
    return min(T._half_unit(raw, mult), 0.01 * abs(value)) or 0.5


def mask(text: str, prefix: str) -> tuple[str, dict]:
    for pattern, token in ENTITIES:
        text = re.sub(pattern, token, text, flags=re.IGNORECASE)
    # A range "5.6-6.2%" / "750-900 độ C" is two figures, not an identifier like
    # "ISO 14064-1": space the dash so both numbers are masked.
    text = _RANGE.sub(lambda m: m.group(0) if _STANDARD_BEFORE.search(T.normalize_for_match(text[max(0, m.start() - 12):m.start()]))
                      else f"{m.group(1)} – {m.group(2)}", text)
    slots: dict[str, dict] = {}
    out, last = [], 0
    for m in _NUM.finditer(text):
        raw = m.group(1)
        before = text[: m.start()]
        before_norm = T.normalize_for_match(before[-30:])
        after = text[m.end():]
        if re.fullmatch(r"(19|20|21)\d\d", raw):
            continue                                   # a year: keep, it is the period
        if after[:1] in {"/", "-", ":"} and after[1:2].isdigit():
            continue
        line_start = text.rfind("\n", 0, m.start()) + 1
        if not text[line_start:m.start()].strip() and re.match(r"[.)]\s+\S", after):
            continue                                   # enumerator: "1. Tổng phát thải …"
        if line_start == 0 and not text[:m.start()].strip() and re.fullmatch(r"\d{1,3}", raw) and after[:1] == "\n":
            continue                                   # page number on the first line
        if _SCOPE_BEFORE.search(before_norm) or T._LABEL_RE.search(before_norm[-24:]):
            continue                                   # Phạm vi 1 và 2, Bảng 5.2, ISO …
        value = T._parse_locale_number(raw)
        if value is None:
            continue
        mult_m = _MULT_WORD.match(after)
        mult = _MULT[mult_m.group(1).lower()] if mult_m else 1.0
        end = m.end() + (mult_m.end() if mult_m else 0)
        unit_m = T._UNIT_RE.match(T.normalize_for_match(text[end:end + 20]))
        unit = T._canonical_unit(unit_m.group("unit")) if unit_m and unit_m.group("unit") else None
        name = f"{prefix}{len(slots) + 1}"
        slots[name] = {"value": value * mult, "unit": unit, "half": _tolerance(raw, value * mult, mult, unit),
                       "raw": text[m.start():end], "start": m.start(),
                       "before": text[max(0, m.start() - 30):m.start()]}
        out.append(text[last:m.start()])
        out.append(f"<{name}>")
        last = end
    out.append(text[last:])
    return "".join(out), slots


PROMPT = """Bạn là kiểm toán viên. Trong TUYÊN BỐ và ĐOẠN BẰNG CHỨNG dưới đây, mọi con số đã được thay bằng mã: <S1>, <S2>… là số trong tuyên bố; <E1>, <E2>… là số trong bằng chứng. Giá trị thật được giữ bí mật; đơn vị (%, tCO2e, kWh, m3, tấn…), năm và nhãn phạm vi vẫn hiển thị. Tên doanh nghiệp, cơ sở đã được thay bằng [DOANH_NGHIỆP], [CƠ_SỞ_A]…

Với MỖI mã <S…> trong tuyên bố, hãy cho biết số nào trong bằng chứng đo ĐÚNG CÙNG đại lượng: cùng chỉ số, cùng kỳ (năm), cùng phạm vi phát thải, cùng ranh giới (toàn tập đoàn / cơ sở / công ty mẹ / mảng), cùng loại giá trị (thực hiện hay mục tiêu; tuyệt đối, cường độ, tỷ trọng hay mức thay đổi). Các dạng được phép:
- {{"slot": "S1", "type": "direct", "evidence": "E3"}} — số E3 đo đúng cùng đại lượng với S1;
- {{"slot": "S1", "type": "sum", "evidence": ["E1", "E2"]}} — S1 là tổng của các thành phần trong bằng chứng;
- {{"slot": "S1", "type": "change", "from": "E1", "to": "E2"}} — S1 là phần trăm thay đổi, bằng chứng cho giá trị kỳ gốc E1 và kỳ sau E2 của cùng đại lượng;
- {{"slot": "S1", "type": "none"}} — không số nào trong bằng chứng đo cùng đại lượng (khác chỉ số, khác kỳ, khác phạm vi, khác ranh giới, mục tiêu so với thực hiện, cường độ so với tuyệt đối…).
Bạn KHÔNG cần và KHÔNG được đoán giá trị; việc so sánh số sẽ do máy tính làm.

Nếu tuyên bố KHÔNG có mã <S…> nào, hãy xếp nhãn định tính: "SUPPORTED" (bằng chứng xác nhận), "CONTRADICTED" (bằng chứng phủ nhận), hoặc "NOT_ENOUGH_INFO".

TUYÊN BỐ: {claim}

ĐOẠN BẰNG CHỨNG: {evidence}

Trả lời đúng một đối tượng JSON: {{"mappings": [...], "qualitative": "SUPPORTED" | "CONTRADICTED" | "NOT_ENOUGH_INFO" | null, "ly_do": "<một câu>"}}"""


def _direction(before: str) -> int:
    """Sign of the change a claim states, read just before its slot: giảm/hạ → -1, tăng/nâng → +1.
    Compared on accented text: folded, "năng lượng" would read as "nâng"."""
    window = before.lower()
    if re.search(r"(?<!\w)(giảm|hạ)(?!\w)", window):
        return -1
    if re.search(r"(?<!\w)(tăng|nâng)(?!\w)", window):
        return 1
    return 0


def decide(claim_text, cslots, eslots, answer) -> tuple[str, list[str]]:
    """S / C / N from the model's slot mapping, with all arithmetic done here."""
    notes = []
    if not cslots:
        q = str(answer.get("qualitative") or "").upper()
        return {"SUPPORTED": "S", "CONTRADICTED": "C"}.get(q, "N"), ["định tính"]
    maps = {m.get("slot"): m for m in answer.get("mappings") or [] if isinstance(m, dict)}
    verdicts = []
    for name, s in cslots.items():
        m = maps.get(name, {"type": "none"})
        kind = m.get("type")
        try:
            if kind == "direct":
                e = eslots[m["evidence"]]
                if s["unit"] and e["unit"] and s["unit"] != e["unit"]:
                    verdicts.append("N"); notes.append(f"{name}: khác đơn vị"); continue
                diff, tol = abs(s["value"] - e["value"]), s["half"] + e["half"]
                verdicts.append("S" if diff <= tol else "C")
                notes.append(f"{name}={s['value']:g} vs {m['evidence']}={e['value']:g} (±{tol:g})")
            elif kind == "sum":
                parts = [eslots[x] for x in m["evidence"]]
                total = sum(p["value"] for p in parts)
                tol = s["half"] + sum(p["half"] for p in parts)
                verdicts.append("S" if abs(s["value"] - total) <= tol else "C")
                notes.append(f"{name}={s['value']:g} vs Σ={total:g} (±{tol:g})")
            elif kind == "change":
                a, b = eslots[m["from"]], eslots[m["to"]]
                pct = (b["value"] - a["value"]) / a["value"] * 100
                sign = _direction(s.get("before", "")) or 1
                expected = sign * s["value"]
                tol = s["half"] + 0.05      # claim's written precision + rounding of the recomputed %
                verdicts.append("S" if abs(pct - expected) <= tol else "C")
                notes.append(f"{name}: thay đổi {pct:+.2f}% vs {expected:+g}% (±{tol:g})")
            else:
                verdicts.append("N"); notes.append(f"{name}: không ứng số nào")
        except (KeyError, TypeError, ZeroDivisionError) as exc:
            verdicts.append("N"); notes.append(f"{name}: ánh xạ không hợp lệ ({exc!r})")
    if "C" in verdicts:
        return "C", notes
    if verdicts and all(v == "S" for v in verdicts):
        return "S", notes
    return "N", notes


def run_case(provider, case):
    cid, family, claim, evidence, ok = case
    mclaim, cslots = mask(claim, "S")
    mevid, eslots = mask(evidence, "E")
    sent = PROMPT.format(claim=mclaim, evidence=mevid)
    leaked_digits = [d for d in re.findall(r"\d[\d.,]*", mclaim + " " + mevid)
                     if not re.fullmatch(r"(19|20|21)\d\d", d)]
    t = time.time()
    for attempt in range(3):
        try:
            resp = provider.generate([{"role": "user", "content": sent}], response_schema={"type": "object"})
            answer = resp.parsed or {}
            label, notes = decide(claim, cslots, eslots, answer)
            return {"label": label, "notes": notes, "mappings": answer.get("mappings"),
                    "reason": str(answer.get("ly_do", ""))[:300], "seconds": round(time.time() - t, 1),
                    "sent_claim": mclaim, "digits_left_in_prompt": leaked_digits[:20], "usage": resp.usage}
        except Exception as exc:  # noqa: BLE001
            err = repr(exc)[:200]
            time.sleep(3 * (attempt + 1))
    return {"label": "?", "reason": err, "seconds": round(time.time() - t, 1)}


results = {"cases": [{"id": c[0], "family": c[1], "claim": c[2], "ok": sorted(c[4])} for c in CASES], "systems": {}}
fpt = ModelGateway()._provider("fpt")
for model in MODELS:
    provider = fpt.bind_model(model)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=6) as pool:
        answers = list(pool.map(lambda c: run_case(provider, c), CASES))
    results["systems"][f"{model} (che số + tên)"] = {c[0]: a for c, a in zip(CASES, answers)}
    print(f"{model} masked done in {time.time()-t0:.1f}s", flush=True)
    json.dump(results, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

ok = {c[0]: c[4] for c in CASES}
for name, ans in results["systems"].items():
    correct = sum(a["label"] in ok[k] for k, a in ans.items())
    fs = sum(a["label"] == "S" and "S" not in ok[k] for k, a in ans.items())
    fc = sum(a["label"] == "C" and "C" not in ok[k] for k, a in ans.items())
    leaks = sum(bool(a.get("digits_left_in_prompt")) for a in ans.values())
    print(f"{name:34s} {correct}/{len(ok)}  falseS={fs} falseC={fc}  prompts with non-year digits={leaks}")
