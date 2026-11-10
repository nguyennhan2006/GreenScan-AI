"""Is this extracted sentence probably not a claim at all? (claim-quality-v1, 2026-11-09)

GS-Eval v2 (05/11) found that about 30 % of the sentences the extractor keeps are
not claims (44/146, Wilson [0,23; 0,38]): table cells and a report's index read
left to right, section labels glued to a caption, the title of a standard, a
paragraph quoting a decree. Each of them still received a full risk score -- every
"missing" component penalised -- and could reach the head of the review queue.

This module does **not** remove anything. Whether a sentence is a claim is the
reviewer's call (ISSUES P5, ARCHITECTURE_INVARIANTS): a flagged claim keeps its
verdict and stays in the claim list with the reason shown, but it is left out of
the review queue and out of the risk score, because a score on a non-claim is
noise the auditor has to argue with.

Only structural signals are used -- things a reader can check on the sentence
itself -- never a model. Rules that also fired on true claims during development
were dropped: a list lead-in ending in ":" ("Effective water management in 2024
resulted in … as follows:") and a URL ("Công ty áp dụng công cụ kiểm kê … trên
website https://…") are both often real claims.

Measured before use (configs/measurement_decisions.yaml, block claim_quality_v1).
"""

from __future__ import annotations

import re

from quantum_gw.utils.text import normalize_for_match

# Reasons as a Vietnamese auditor reads them on the screen and the working paper.
REASON_VI = {
    "layout_glue": "chữ dàn trang dính nhau (ô bảng, mục lục hoặc tiêu đề đọc liền thành câu)",
    "standard_title": "tên một tiêu chuẩn, không phải lời doanh nghiệp tự khẳng định",
    "legal_text": "trích văn bản pháp luật, không phải lời doanh nghiệp tự khẳng định",
    "contact_line": "thông tin liên hệ",
}

# A bare integer standing alone between words: the page numbers of an index
# ("… 140 Mô hình … 141 …"), the column numbers of a table, the item numbers of
# a materiality matrix ("DHG Pharma 2 6 1 3 4 Phát triển bền vững").
_STANDALONE_INT = re.compile(r"(?<![\w.,/%:+-])(\d{1,3})(?![\w.,/%-])")
# …unless a label in front makes it part of the statement ("Phạm vi 1 và 2",
# "Bước 4", "Điều 91") or a unit after it makes it a measurement ("5 nhà máy").
_LABEL_BEFORE = re.compile(
    r"(?:phạm vi|scope|gri|bước|phần|mục|điều|khoản|iso|part|chương|giai đoạn|kỳ|top|số|nhóm|lô|tier|cấp|"
    r"loại|sdg|mục tiêu|tầng|lớp|hạng|vị trí|nguyên tắc|principle|goal|target|step|level|grade)\s*$",
    re.IGNORECASE,
)
_UNIT_AFTER = re.compile(
    r"\s*(?:%|tấn|kwh|mwh|gwh|gj|tj|m3|m³|kg|ha\b|tco2|triệu|tỷ|nghìn|ngàn|lần|năm|tháng|ngày|giờ|người|"
    r"nhà máy|dự án|cây|mw|kw|cơ sở|đơn vị|công ty|doanh nghiệp|sites?|plants?|tonnes?|tons?|years?|people|"
    r"employees?|projects?|trees?|times?)",
    re.IGNORECASE,
)
_GRI_CODE = re.compile(r"\bGRI\s*\d{3}\b")
# A table header read across: four or more years in a row ("2015 2016 2017 2019").
_YEAR_RUN = re.compile(r"(?:\b(?:19|20)\d{2}\b[\s,;/|–-]+){3,}\b(?:19|20)\d{2}\b")
# The gas columns of an inventory table ("CO2 CH4 SF6 N2O HFCs PFCs").
_GAS = re.compile(r"(?<!\w)(?:CO2|CH4|N2O|SF6|NF3|HFCs?|PFCs?)(?!\w)")
_CAP_WORD = re.compile(r"^[A-ZÀ-ỸĐ][\wÀ-ỹ'’-]*$")
_QUOTED = re.compile(r"“[^”]*”|\"[^\"]*\"")
_CONTACT = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\+84[\s\d.]{6,}|(?:điện thoại|tel|fax|hotline)\s*[:.]", re.IGNORECASE)
_STANDARD_TITLE = re.compile(r"^\s*(?:ISO|TCVN|IFRS|ISSB|SASB|TCFD|GHG Protocol)\s*[\w.-]*\s*:", re.IGNORECASE)
_LEGAL_WORD = re.compile(r"(?<!\w)(?:luật|nghị định|thông tư|quyết định|nđ-cp|tt-btc|qđ-ttg)(?!\w)", re.IGNORECASE)
# The reporting entity speaking, or acting on the law it cites: then the sentence
# is a claim about compliance, not a quotation ("Công ty tuân thủ Luật BVMT …").
_SELF_OR_ACT = re.compile(
    r"(?<!\w)(?:công ty|tập đoàn|chúng tôi|doanh nghiệp|nhà máy|đơn vị|tuân thủ|thực hiện|đã|áp dụng|đáp ứng|"
    r"we|our|the company|the group|comply|complied|complies)(?!\w)",
    re.IGNORECASE,
)
# Capitalised words in a row: a heading strip or a matrix read across
# ("Topic Identification Stakeholder Engagement Environmental Social Governance").
# Vietnamese allows longer runs: entity names are long ("Công ty TNHH MTV Thép
# Hòa Phát Hưng Yên") and all-caps headings are already rejected upstream.
_CAP_RUN_MIN = {"vi": 8, "en": 6}


def standalone_integers(text: str) -> int:
    count = 0
    for match in _STANDALONE_INT.finditer(text):
        if _LABEL_BEFORE.search(text[max(0, match.start() - 16): match.start()]):
            continue
        if _UNIT_AFTER.match(text[match.end():]):
            continue
        count += 1
    return count


def longest_capitalised_run(text: str) -> int:
    """Longest run of capitalised words; a comma, a semicolon or a quotation ends a run."""
    best = current = 0
    for raw in re.split(r"\s+", _QUOTED.sub(" , ", text)):
        word = raw.strip("()[]\"“”,;.:–—")
        if word and ((_CAP_WORD.match(word) and not word.isupper()) or (word.isupper() and len(word) >= 2)):
            current += 1
            best = max(best, current)
        elif word:
            current = 0
        if raw.rstrip()[-1:] in (",", ";", ".", ":"):
            current = 0
    return best


def suspect_reason(text: str) -> str | None:
    """A reason code from REASON_VI when the sentence is probably not a claim, else None."""
    stripped = (text or "").strip()
    if not stripped:
        return None
    integers, gri = standalone_integers(stripped), len(_GRI_CODE.findall(stripped))
    if integers >= 3 or gri >= 2 or (gri >= 1 and integers >= 2):
        return "layout_glue"
    if _YEAR_RUN.search(stripped) or len(_GAS.findall(stripped)) >= 4:
        return "layout_glue"
    language = "vi" if normalize_for_match(stripped) != stripped.lower() else "en"
    if longest_capitalised_run(stripped) >= _CAP_RUN_MIN[language]:
        return "layout_glue"
    if _CONTACT.search(stripped) and len(stripped.split()) < 20:
        return "contact_line"
    if _STANDARD_TITLE.match(stripped):
        return "standard_title"
    if len(_LEGAL_WORD.findall(stripped)) >= 2 and not _SELF_OR_ACT.search(stripped):
        return "legal_text"
    return None


def reason_vi(code: str | None) -> str:
    return REASON_VI.get(code or "", "")
