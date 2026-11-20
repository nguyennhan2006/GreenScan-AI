"""Absolute claims: compute the share they assert, or flag a passage that says "only part".

"Vốn trái phiếu xanh được sử dụng hoàn toàn" is a claim that the share used is
100%. It carries no figure, so the figure comparison never ran and case A2
(500 tỷ raised, 320 disbursed, 180 unallocated) stayed PARTIALLY_SUPPORTED.

Two rules, both deterministic:

* absolute-share-v1 (`allocated_share`). Green-finance claims only: a claim that
  says "hoàn toàn / toàn bộ / tất cả / 100%" about using or allocating the
  proceeds of a green instrument, and a passage that names the same instrument
  with a total and a used (or unused) amount in the same currency. The share is
  used / total, or (total - unused) / total, and the result carries the
  arithmetic so a reviewer can redo it.
* stance-cues-v3 rule layer (`absolute_conflict`). Any absolute claim, and a
  sentence of the passage that shares a content bigram with the claim and says
  "chưa phân bổ / một phần / phần lớn / đang triển khai ...". A phrase is weaker
  than arithmetic, so the caller makes this PARTIAL plus a review flag, never
  CONTRADICTED.
"""

from __future__ import annotations

import re
import unicodedata

POLICY_SHARE = "absolute-share-v1"
POLICY_CONFLICT = "stance-cues-v3"

ABSOLUTE_RE = re.compile(
    r"(?<!\w)(hoàn toàn|toàn bộ|tất cả|100\s?%|100 phần trăm|mọi|duy nhất|không phát thải|"
    r"phát thải ròng bằng (?:0|không)|đã hoàn thành|fully|entirely|all of|100 percent|zero[- ]emissions?)(?!\w)"
)
# The share rule needs the absolute word to qualify the use of the money, not, say, "toàn bộ dự án".
USE_RE = re.compile(r"(?<!\w)(sử dụng|dùng|phân bổ|giải ngân|đầu tư|tài trợ|used|allocated|disbursed|invested)(?!\w)")
GREEN_FINANCE_TERMS = (
    "trái phiếu xanh", "trái phiếu bền vững", "tín dụng xanh", "khoản vay xanh",
    "green bond", "sustainability bond", "green loan",
)

# Only cues that say the thing itself is unfinished. The plan's wider list (còn lại, một phần, phần lớn,
# đang triển khai, đang thực hiện, giai đoạn 1/đầu, remaining, in progress) was replayed on 1,766 stored
# verifications of real reports on 14/11/2026: 17 new flags, 0 right on reading (a "giai đoạn đầu" of the
# steel life cycle, "một phần cốt lõi trong chiến lược", "the remaining breweries"...). Kept here, unused.
WEAK_PARTIAL_CUES = ("còn lại", "một phần", "phần lớn", "đang triển khai", "đang thực hiện", "giai đoạn 1",
                     "giai đoạn đầu", "partially", "partly", "remaining", "in progress")
PARTIAL_RE = re.compile(
    r"(?<!\w)(chưa (?:được )?(?:phân bổ|giải ngân|sử dụng|hoàn thành)|not yet (?:allocated|disbursed|used|completed)|"
    r"unallocated|undisbursed)(?!\w)"
)

_AMOUNT_RE = re.compile(
    r"(?<![\w.,])(\d{1,3}(?:[.,]\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?)\s*"
    r"(nghìn tỷ đồng|ngàn tỷ đồng|tỷ đồng|tỷ vnd|triệu đồng|triệu vnd|đồng|vnd|vnđ|tỷ usd|triệu usd|usd)(?!\w)"
)
_SCALE = {
    "nghìn tỷ đồng": (1e12, "VND"), "ngàn tỷ đồng": (1e12, "VND"), "tỷ đồng": (1e9, "VND"), "tỷ vnd": (1e9, "VND"),
    "triệu đồng": (1e6, "VND"), "triệu vnd": (1e6, "VND"), "đồng": (1.0, "VND"), "vnd": (1.0, "VND"),
    "vnđ": (1.0, "VND"), "tỷ usd": (1e9, "USD"), "triệu usd": (1e6, "USD"), "usd": (1.0, "USD"),
}
_UNUSED_RE = re.compile(
    r"chưa (?:được )?(?:phân bổ|giải ngân|sử dụng)|tiền gửi|đầu tư tạm thời|unallocated|not yet allocated|undisbursed|unused"
)
_USED_RE = re.compile(r"đã (?:được )?(?:giải ngân|phân bổ|sử dụng)|được phân bổ (?:vào|cho)|giải ngân cho|allocated|disbursed")
# A table that states its unit once, in a column header: "Giá trị (tỷ VND)" (Techcombank 2024 allocation
# report, 15/11/2026). Bare figures in such a passage are read in that unit.
_HEADER_UNIT_RE = re.compile(r"\((nghìn tỷ đồng|tỷ đồng|tỷ vnd|triệu đồng|triệu vnd|tỷ usd|triệu usd)\)")
_BARE_RE = re.compile(r"(?<![\w.,/%-])(\d{1,3}(?:[.,]\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?![\w%/-]|[.,]\d|\s?%)")
_ENUMERATION_RE = re.compile(r"\(\s*[1-9]\s*\)")
_TOTAL_RE = re.compile(
    r"khoản thu|tổng giá trị|tổng vốn|tổng số tiền|tổng số|tổng mệnh giá|hạn mức|giá trị phát hành|phát hành|"
    r"huy động được|proceeds|total"
)
_BOUNDARY_RE = re.compile(r";|(?<=[.!?])\s|\n")


def _fold(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text or "").lower())


def is_absolute(claim_text: str) -> str | None:
    match = ABSOLUTE_RE.search(_fold(claim_text))
    return match.group(1) if match else None


def green_instrument(text: str) -> str | None:
    folded = _fold(text)
    return next((t for t in GREEN_FINANCE_TERMS if t in folded), None)


def _number(raw: str) -> float | None:
    """Vietnamese first: '1.250' is twelve hundred and fifty, '2,5' is two and a half."""
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?", raw):
        raw = raw.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?", raw):
        raw = raw.replace(",", "")
    else:
        raw = raw.replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def amounts(passage: str) -> list[dict]:
    """Money amounts in a passage, each with its role read from the words next to it.

    The role is read from the clause the amount sits in, cut at the neighbouring
    amounts: words after the amount first ("320 tỷ đồng đã giải ngân"), then words
    before it ("khoản thu ... là 500 tỷ đồng"). An amount with no role cue is
    ignored rather than guessed.
    """
    folded = _fold(passage)
    found = [m for m in _AMOUNT_RE.finditer(folded)]
    header = _HEADER_UNIT_RE.search(folded)
    table_mode = not found and header is not None
    if table_mode:
        # Row label first, figure after: "… được phân bổ vào Dự Án đủ điều kiện | 89% | 399".
        found = [m for m in _BARE_RE.finditer(folded, header.end())
                 if not (1900 <= (_number(m.group(1)) or 0) <= 2100 and "," not in m.group(1) and "." not in m.group(1))]
    bounds = [m.start() for m in _BOUNDARY_RE.finditer(folded)]
    out = []
    for i, m in enumerate(found):
        value = _number(m.group(1))
        if value is None:
            continue
        scale, currency = _SCALE[header.group(1)] if table_mode else _SCALE[m.group(2)]
        left = max([b for b in bounds if b < m.start()] + [found[i - 1].end() if i else 0])
        right = min([b for b in bounds if b > m.end()] + [found[i + 1].start() if i + 1 < len(found) else len(folded)])
        head, tail = folded[left:m.start()], folded[m.end():right]
        role = None
        for text in ((head, tail) if table_mode else (tail, head)):
            if _UNUSED_RE.search(text):
                role = "unused"
            elif _USED_RE.search(text):
                role = "used"
            if role:
                break
        if role is None and _TOTAL_RE.search(head + " " + tail):
            role = "total"
        if role:
            shown = f"{m.group(1)} {header.group(1)}" if table_mode else m.group(0)
            out.append({"value": value * scale, "shown": shown, "currency": currency, "role": role})
    return out


def allocated_share(claim_text: str, passage: str) -> dict | None:
    """The share of a green instrument's proceeds the passage says was used, or None.

    None unless every piece is present: an absolute claim about using the proceeds
    of a named green instrument, the same instrument in the passage, exactly one
    total, and used or unused amounts in the total's currency that do not add up
    to more than the total.
    """
    absolute = is_absolute(claim_text)
    instrument = green_instrument(claim_text)
    if not absolute or not instrument or not USE_RE.search(_fold(claim_text)):
        return None
    folded_passage = _fold(passage)
    # The passage must name the instrument, or at least its noun: an allocation table headed elsewhere on the
    # page reads "Số tiền thu được từ phát hành trái phiếu được phân bổ vào Dự Án đủ điều kiện".
    noun = {"trái phiếu xanh": "trái phiếu", "trái phiếu bền vững": "trái phiếu", "tín dụng xanh": "tín dụng",
            "khoản vay xanh": "khoản vay", "green bond": "bond", "sustainability bond": "bond", "green loan": "loan"}
    if instrument not in folded_passage and noun.get(instrument, instrument) not in folded_passage:
        return None
    found = amounts(passage)
    totals = {a["value"] for a in found if a["role"] == "total"}
    used = [a for a in found if a["role"] == "used"]
    unused = [a for a in found if a["role"] == "unused"]
    if not totals and used and unused and len({a["currency"] for a in used + unused}) == 1:
        # No total written, but both parts are: the whole is their sum (Techcombank 2024: 399 + 51).
        total_item = {"value": sum(a["value"] for a in used + unused), "currency": used[0]["currency"],
                      "shown": "(" + " + ".join(a["shown"] for a in used + unused) + ")"}
        totals = {total_item["value"]}
    elif len(totals) != 1:
        return None
    else:
        total_item = next(a for a in found if a["role"] == "total")
    total = total_item["value"]
    if total <= 0:
        return None
    used = [a for a in used if a["currency"] == total_item["currency"]]
    unused = [a for a in unused if a["currency"] == total_item["currency"]]
    used_sum, unused_sum = sum(a["value"] for a in used), sum(a["value"] for a in unused)
    if not used and not unused:
        return None
    if used_sum + unused_sum > total * 1.01:
        return None  # parts larger than the whole: a role was misread
    if used:
        share = used_sum / total
        formula = f"{' + '.join(a['shown'] for a in used)} đã sử dụng / {total_item['shown']} = {share * 100:.0f}%"
    else:
        share = (total - unused_sum) / total
        formula = (f"({total_item['shown']} − {' − '.join(a['shown'] for a in unused)} chưa sử dụng) / "
                   f"{total_item['shown']} = {share * 100:.0f}%")
    return {"policy": POLICY_SHARE, "absolute": absolute, "instrument": instrument,
            "share_pct": round(share * 100, 2), "formula": formula}


def absolute_conflict(claim_text: str, passage: str, claim_bigrams: set, bigrams_of) -> dict | None:
    """An absolute claim and a sentence about it that says only part is done, or None.

    `bigrams_of(text)` returns the content bigrams of a text (the verifier passes
    `utils.text.content_bigrams`); the sentence carrying the partial cue must
    share at least one with the claim, so a "giai đoạn 1" about some other project
    does not count.
    """
    absolute = is_absolute(claim_text)
    if not absolute or not claim_bigrams:
        return None
    for sentence in re.split(r"(?<=[.!?;])\s+|\n", passage or ""):
        match = PARTIAL_RE.search(_fold(sentence))
        # "(1) … (2) Số dư còn lại chưa được phân bổ, (3) …" lists what a report will contain (Techcombank
        # 2024 allocation report); it says nothing about how much is unallocated.
        if match and _ENUMERATION_RE.search(sentence):
            continue
        if match and claim_bigrams & bigrams_of(sentence):
            return {"policy": POLICY_CONFLICT, "absolute": absolute, "partial": match.group(1),
                    "sentence": sentence.strip()[:240]}
    return None
