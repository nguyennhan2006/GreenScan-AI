"""Edit suggestions for a claim sentence: four kinds, from rule templates, never a new number.

The analysis already says what a claim lacks (period, baseline, scope, a
figure, evidence) and which words overreach. A suggestion turns one finding
into one concrete edit the reviewer can accept, reject or rework:

1. add_scope        — append the missing period / baseline / boundary as a slot to fill
2. placeholder      — mark a vague phrase, or a claim without a figure, with "[bổ sung: …]"
3. evidence_ref     — cite the evidence the run actually found, or a slot asking for one
4. soften           — replace an absolute or offset-based claim with a qualified one

What a suggestion may never do is supply a figure the company did not publish:
every replacement goes through `assert_no_new_numbers`, which allows only the
numbers already in the sentence and the page numbers of cited evidence. A
suggestion that fails the check is dropped, not shown.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import asdict, dataclass, field

from quantum_gw.utils.text import stable_id

from .document import fold

_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


class InventedNumberError(ValueError):
    pass


def numbers_in(text: str) -> set[str]:
    return {n.rstrip(".,") for n in _NUMBER.findall(text)}


def assert_no_new_numbers(before: str, after: str, allowed: set[str] | frozenset[str] = frozenset()) -> None:
    new = numbers_in(after) - numbers_in(before) - {str(a) for a in allowed}
    if new:
        raise InventedNumberError(f"Đề xuất chứa số không có trong câu gốc: {sorted(new)}")


@dataclass
class Suggestion:
    suggestion_id: str
    claim_id: str
    kind: str
    rule_code: str
    title: str
    # replace: the first occurrence of `target` in the claim becomes `replacement`.
    # append: `replacement` is inserted at the end of the claim, before its final punctuation.
    position: str
    target: str
    replacement: str
    reason: str
    basis: list[dict] = field(default_factory=list)
    source: str = "rule"
    before: str = ""
    after: str = ""
    segments: list[dict] = field(default_factory=list)

    def to_json(self) -> dict:
        return asdict(self)


KIND_LABELS = {
    "add_scope": "Thêm phạm vi, kỳ, năm gốc",
    "placeholder": "Chỗ trống cần bổ sung số liệu",
    "evidence_ref": "Thêm dẫn chiếu bằng chứng",
    "soften": "Làm nhẹ lời nói quá",
}

_RUBRIC = {"label": "Thang thuộc tính của GreenScan: chỉ số, số liệu, kỳ, năm gốc, phạm vi",
           "verification": "Quy tắc nội bộ"}
_GHG = {"label": "GHG Protocol Corporate Standard: ranh giới tổ chức, năm gốc (ch. 3–5)",
        "verification": "Tri thức miền, chưa đối chiếu điều khoản"}
_EU_GENERIC = {"label": "Chỉ thị (EU) 2024/825: cấm tuyên bố môi trường chung chung và tuyên bố trung hòa dựa trên bù trừ",
               "verification": "Tham chiếu quốc tế, không ràng buộc tại Việt Nam"}
_VN_CONSUMER = {"label": "Luật Bảo vệ quyền lợi người tiêu dùng 19/2023/QH15, Điều 10 (thông tin sai lệch, không đầy đủ)",
                "verification": "Căn cứ ứng viên, chưa có người xác minh"}

# Folded pattern → (replacement, rule code, why). Replacements carry no digits.
_OVERCLAIMS: list[tuple[str, str, str, str]] = [
    (r"trung hoa (?:cac[- ]?bon|carbon)|carbon neutral|net[- ]?zero|phat thai rong bang (?:0|khong)",
     "hướng tới trung hòa các-bon [bổ sung: phần giảm thực tế, phần bù trừ bằng tín chỉ, chuẩn áp dụng]",
     "OC-01", "Tuyên bố trung hòa ở thì hiện tại cần tách phần giảm thực tế khỏi phần bù trừ bằng tín chỉ."),
    (r"(?:100% |hoan toan )xanh|xanh hoan toan",
     "giảm tác động môi trường [bổ sung: so với mức nào, đo bằng chỉ số nào]",
     "OC-02", "Tuyên bố tuyệt đối không chứng minh được bằng một chỉ số."),
    (r"khong (?:gay )?(?:phat thai|o nhiem)|zero emission",
     "phát thải thấp hơn [bổ sung: mức so sánh và chỉ số]",
     "OC-03", "\"Không phát thải\" là tuyên bố tuyệt đối; cần mức so sánh."),
    (r"than thien (?:voi )?moi truong|environmentally friendly|eco[- ]friendly",
     "ít tác động môi trường hơn [bổ sung: chỉ số và mức so sánh]",
     "OC-04", "Tuyên bố môi trường chung chung, không có chỉ số."),
    (r"\b(?:hang dau|tien phong|xanh nhat|tot nhat|so 1)\b(?: (?:viet nam|the gioi|nganh))?",
     "[bổ sung: căn cứ xếp hạng và đơn vị xếp hạng]",
     "OC-05", "Tuyên bố so sánh bậc nhất cần căn cứ xếp hạng độc lập."),
]


def _span_by_fold(text: str, pattern: str) -> tuple[int, int] | None:
    match = re.search(pattern, fold(text))
    return (match.start(), match.end()) if match else None


def _sentence_end(text: str) -> int:
    stripped = text.rstrip()
    return len(stripped) - 1 if stripped and stripped[-1] in ".;!?" else len(stripped)


def apply(text: str, s: Suggestion) -> str | None:
    """The claim text with the suggestion applied, or None if its target is gone."""
    if s.position == "append":
        cut = _sentence_end(text)
        return text[:cut] + s.replacement + text[cut:]
    index = text.find(s.target)
    if index < 0:
        return None
    return text[:index] + s.replacement + text[index + len(s.target):]


def _segments(before: str, after: str) -> list[dict]:
    tokenize = re.compile(r"\s+|\w+|[^\w\s]", re.U).findall
    a, b = tokenize(before), tokenize(after)
    out: list[dict] = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            out.append({"op": "equal", "text": "".join(a[i1:i2])})
        else:
            if i2 > i1:
                out.append({"op": "del", "text": "".join(a[i1:i2])})
            if j2 > j1:
                out.append({"op": "ins", "text": "".join(b[j1:j2])})
    return out


def _make(claim_id: str, text: str, kind: str, rule: str, position: str, target: str, replacement: str,
          reason: str, basis: list[dict], allowed: set[str] | None = None) -> Suggestion | None:
    s = Suggestion(
        suggestion_id=stable_id(claim_id, rule, target, replacement),
        claim_id=claim_id, kind=kind, rule_code=rule, title=KIND_LABELS[kind],
        position=position, target=target, replacement=replacement, reason=reason, basis=basis,
    )
    after = apply(text, s)
    if after is None:
        return None
    try:
        assert_no_new_numbers(text, after, allowed or set())
    except InventedNumberError:
        return None
    s.before, s.after, s.segments = text, after, _segments(text, after)
    return s


def suggest(diag: dict, text: str) -> list[Suggestion]:
    """Suggestions for one diagnostic; `text` is the claim as it now reads in the editor."""
    claim_id = diag["claim_id"]
    out: list[Suggestion | None] = []
    missing = set(diag.get("missing", []))

    # 4. soften — first, because it changes words the other kinds leave alone.
    future = re.search(r"\b(?:den nam|muc tieu|cam ket|huong toi|phan dau|by 20|target)\b", fold(text))
    for pattern, replacement, rule, why in _OVERCLAIMS:
        if rule == "OC-01" and future:
            continue
        span = _span_by_fold(text, pattern)
        if span:
            basis = [_EU_GENERIC, _VN_CONSUMER]
            out.append(_make(claim_id, text, "soften", rule, "replace", text[span[0]:span[1]], replacement, why, basis))
            break

    # 2. placeholder — a vague phrase gets a slot right after it; no figure at all gets one at the end.
    vague_done = False
    for term in diag.get("vague_terms", [])[:1]:
        span = _span_by_fold(text, re.escape(fold(term)))
        if span and not any(s and s.kind == "soften" and s.target in text[span[0]:span[1]] for s in out):
            target = text[span[0]:span[1]]
            out.append(_make(claim_id, text, "placeholder", "VG-01", "replace", target,
                             f"{target} [bổ sung: số liệu chứng minh — chỉ số, giá trị, đơn vị, kỳ]",
                             f"Cụm \"{target}\" không đo được; cần số liệu đi kèm.", [_RUBRIC]))
            vague_done = True
    if not vague_done and "số liệu" in missing:
        out.append(_make(claim_id, text, "placeholder", "VG-02", "append", "",
                         " [bổ sung: số liệu định lượng — chỉ số, giá trị, đơn vị]",
                         "Tuyên bố không có số liệu định lượng nên không kiểm chứng được.", [_RUBRIC]))

    # 1. add_scope — only the attributes the claim lacks.
    slots = []
    if "kỳ" in missing:
        slots.append("kỳ báo cáo: [bổ sung]")
    if "năm gốc" in missing:
        slots.append("năm gốc: [bổ sung]")
    if "phạm vi" in missing and diag.get("claim_type") in {"emissions", "ghg", "energy", "carbon"}:
        slots.append("phạm vi: [bổ sung: ranh giới tổ chức, phạm vi phát thải 1/2/3]")
    elif "phạm vi" in missing:
        slots.append("phạm vi: [bổ sung: đơn vị, nhà máy hoặc toàn tập đoàn]")
    if slots:
        out.append(_make(claim_id, text, "add_scope", "SC-01", "append", "", f" ({'; '.join(slots)})",
                         "Tuyên bố thiếu " + ", ".join(sorted(missing & {"kỳ", "năm gốc", "phạm vi"})) + ".",
                         [_RUBRIC, _GHG]))

    # 3. evidence_ref — cite only what the run found and supports the claim.
    supporting = [e for e in diag.get("evidence", []) if e.get("relation") == "SUPPORTS" and e.get("page")]
    if supporting:
        e = supporting[0]
        page = str(e["page"])
        out.append(_make(claim_id, text, "evidence_ref", "EV-01", "append", "",
                         f" (xem: {e['source_name']}, tr. {page})",
                         "Bằng chứng xác nhận đã tìm thấy; dẫn chiếu giúp người đọc kiểm lại.",
                         [{"label": e.get("citation") or e["source_name"], "verification": "Bằng chứng do GreenScan tìm thấy"}],
                         allowed={page}))
    elif diag.get("status") != "SUPPORTED":
        out.append(_make(claim_id, text, "evidence_ref", "EV-02", "append", "",
                         " [bổ sung: dẫn chiếu bằng chứng — tài liệu, trang, bảng hoặc chứng nhận]",
                         "Chưa tìm thấy bằng chứng xác nhận trong tài liệu đã cung cấp.", [_RUBRIC]))

    return [s for s in out if s is not None]
