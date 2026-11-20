"""GS-Issue taxonomy: issue codes, families, edit kinds, and the fix oracle (shared by generator, scorer and worker).

The codes are those of benchmark/gs_eval_v2/LABELING_GUIDE.md section 2 (D-EDIT), unchanged.
A family groups codes the guide itself lets overlap (MISSING_SCOPE says "công ty mẹ hay tập đoàn",
ENTITY_SCOPE_AMBIGUOUS says the same): scoring reports strict codes and families.
"""
import re
import unicodedata

CODES = {
    "MISSING_PERIOD": "Thiếu kỳ báo cáo / năm của số liệu",
    "MISSING_BASELINE": "Tuyên bố thay đổi (giảm, tăng, tiết kiệm) không có năm gốc",
    "MISSING_SCOPE": "Thiếu ranh giới (nhà máy nào, công ty mẹ hay tập đoàn, phạm vi phát thải 1/2/3)",
    "NO_FIGURE": "Tuyên bố hiệu quả môi trường mà không có số liệu",
    "VAGUE_TERM": "Từ mơ hồ hoặc quảng cáo: xanh, thân thiện môi trường, bền vững, không ngừng",
    "ABSOLUTE_CLAIM": "Tuyệt đối hoá: 100 %, hoàn toàn, không phát thải, tốt nhất",
    "OFFSET_NEUTRALITY": "Trung hòa / net zero dựa vào bù trừ, không nêu tỷ lệ bù trừ",
    "FUTURE_AS_ACHIEVED": "Cam kết / mục tiêu diễn đạt như đã đạt",
    "UNVERIFIED_LABEL_OR_CERT": "Nhắc nhãn, chứng nhận, giải thưởng mà không nêu tổ chức cấp, phạm vi, hiệu lực",
    "NO_EVIDENCE_REF": "Tuyên bố định lượng không dẫn nguồn / phương pháp",
    "HIDDEN_TRADEOFF": "Nêu một mặt tốt, che mặt xấu lớn hơn liên quan trực tiếp",
    "IRRELEVANT_CLAIM": "Khoe điều hiển nhiên hoặc bắt buộc theo luật như một thành tích",
    "INTENSITY_VS_ABSOLUTE": "Dùng cường độ giảm để ngụ ý tổng phát thải giảm",
    "ENTITY_SCOPE_AMBIGUOUS": "Không rõ số của công ty mẹ hay tập đoàn",
}
FAMILY = {"MISSING_SCOPE": "SCOPE", "ENTITY_SCOPE_AMBIGUOUS": "SCOPE",
          "VAGUE_TERM": "VAGUE", "NO_FIGURE": "VAGUE"}


def family(code: str) -> str:
    return FAMILY.get(code, code)


KINDS = {
    "add_scope": "thêm kỳ, năm gốc, ranh giới, phạm vi còn thiếu, dạng chỗ trống [bổ sung: ...]",
    "placeholder": "thay cụm mơ hồ / câu không có số bằng chỗ trống [bổ sung: chỉ số và giá trị]",
    "evidence_ref": "thêm dẫn chiếu nguồn: [bổ sung: nguồn xác minh]",
    "soften": "bỏ hoặc làm nhẹ lời nói quá, nói lại đúng mức",
}
# The kind the guide prescribes for each code (several are acceptable for some).
KIND_OK = {
    "MISSING_PERIOD": {"add_scope"}, "MISSING_BASELINE": {"add_scope"}, "MISSING_SCOPE": {"add_scope"},
    "ENTITY_SCOPE_AMBIGUOUS": {"add_scope"}, "NO_FIGURE": {"placeholder"}, "VAGUE_TERM": {"placeholder", "soften"},
    "ABSOLUTE_CLAIM": {"soften"}, "OFFSET_NEUTRALITY": {"soften"}, "FUTURE_AS_ACHIEVED": {"soften"},
    "UNVERIFIED_LABEL_OR_CERT": {"add_scope", "evidence_ref"}, "NO_EVIDENCE_REF": {"evidence_ref"},
    "HIDDEN_TRADEOFF": {"add_scope", "evidence_ref", "soften"}, "IRRELEVANT_CLAIM": {"soften"},
    "INTENSITY_VS_ABSOLUTE": {"soften", "add_scope"},
}

PH = re.compile(r"[\[(][^\])]*(?:bổ sung|cần nêu|cần bổ sung|cần ghi)[^\])]*[\])]", re.I)
# What a placeholder must mention to fill each missing slot.
SLOT_WORDS = {
    "period": r"kỳ|năm(?! gốc)|thời gian|giai đoạn",
    "baseline": r"gốc|so sánh|mốc",
    "scope": r"phạm vi|ranh giới|nhà máy|cơ sở|công ty mẹ|hợp nhất|tập đoàn|đơn vị",
    "figure": r"số|giá trị|chỉ số|mức|định lượng",
    "source": r"nguồn|trang|tài liệu|báo cáo|phương pháp|xác minh|kiểm toán|bảo đảm",
    "issuer": r"tổ chức|cấp|hiệu lực|phạm vi|đơn vị",
    "context": r"tổng|toàn bộ|diễn biến|bối cảnh|cùng kỳ|tuyệt đối|phát thải",
    "offset": r"tỷ lệ|bù trừ|tín chỉ|sổ đăng ký",
}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "").lower()
    return re.sub(r"\s+", " ", s).strip()


NUM = re.compile(r"\d+(?:[.,]\d+)*")


def numbers(s: str) -> set[str]:
    return {re.sub(r"[.,]", "", x) for x in NUM.findall(s or "")}


def placeholders(text: str) -> list[str]:
    return [fold(m.group(0)) for m in PH.finditer(text or "")]


def slot_filled(before: str, after: str, slot: str) -> bool:
    """A new placeholder (not in the text before) names the slot."""
    old = placeholders(before)
    new = [p for p in placeholders(after) if p not in old]
    return any(re.search(SLOT_WORDS[slot], p) for p in new)


def oracle(case: dict, before: str, after: str) -> dict:
    """Did the edited text fix this case's planted issue, and keep everything else?

    resolves: the slot is asked for (drop mutations) or the planted phrase is gone or softened (inject mutations).
    keeps_numbers: every number of the text before is still there. new_numbers: numbers the edit invented.
    """
    o = case["oracle"]
    a = fold(after)
    if o["type"] == "all":  # several planted issues: every one must be fixed
        parts = [oracle(dict(case, oracle=p), before, after) for p in o["parts"]]
        return {"resolves": all(p["resolves"] for p in parts), "keeps_numbers": all(p["keeps_numbers"] for p in parts),
                "new_numbers": sorted(set().union(*(p["new_numbers"] for p in parts)))}
    if o["type"] == "slot":
        res = slot_filled(before, after, o["slot"])
    elif o["type"] == "phrase":
        gone = fold(o["phrase"]) not in a
        asked = any(re.search(SLOT_WORDS[o.get("slot", "context")], p) for p in placeholders(after) if p not in placeholders(before))
        res = gone or asked
        if o.get("forbid"):  # e.g. FUTURE_AS_ACHIEVED: "đã giảm" must not remain
            res = res and not re.search(o["forbid"], a)
        if o.get("require"):
            res = res and bool(re.search(o["require"], a))
        if o.get("alt"):  # another acceptable fix, e.g. "theo quy định" for IRRELEVANT_CLAIM
            res = res or bool(re.search(o["alt"], a))
    else:
        res = False
    before_n, after_n = numbers(before), numbers(after)
    droppable = numbers(o.get("phrase", ""))  # softening "100 %" may drop the 100
    return {"resolves": bool(res), "keeps_numbers": (before_n - droppable) <= after_n,
            "new_numbers": sorted(after_n - before_n)}
