from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path

TOKEN_RE = re.compile(r"[\w%+./-]+", re.UNICODE)
YEAR_RE = re.compile(r"\b(20\d{2}|19\d{2})\b")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_for_match(text: str) -> str:
    text = normalize_text(text).lower()
    text = "".join(
        char for char in unicodedata.normalize("NFD", text) if unicodedata.category(char) != "Mn"
    )
    # đ/Đ are base letters, not letter+mark, so NFD leaves them; fold them too so
    # "Điều", OCR output "Dieu" and the lexicon entry "dieu" all agree.
    return text.replace("đ", "d")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(normalize_for_match(text)) if len(token) > 1]


# Function words in both languages, kept accented. Overlap between a claim and a
# passage is measured on what is left: "năm", "công ty" and "của" are shared by
# nearly every pair of sentences in a report and said nothing about relatedness.
STOPWORDS = frozenset("""
năm công ty tập đoàn của và trong so với các được đã là có cho từ đến theo về này đó một những
tại trên dưới ra vào khi nếu thì mà hay hoặc như để bị bởi cùng còn rất hơn nhất toàn bộ mọi
chúng tôi ta mình nó họ sẽ đang cần phải làm thực hiện việc định gồm bao
the of and in to a an by for with from on at as is are was were be been being its our we it this
that these those or not no than which who whom whose where when while will would shall should
may might can could has have had do does did into over under per about also both each such
""".split())

_CONTENT_TOKEN_RE = re.compile(r"[\w%]+", re.UNICODE)


def content_tokens(text: str) -> set[str]:
    """Tokens that carry meaning: no function words, no bare years.

    Accents are kept. Folding made "sử dụng" and "không đúng" share the token
    "dung", and "tới" collide with "tôi" -- the same class of error as
    "thiếu"/"thiêu" in the cue lexicon, showing up here as phantom overlap.
    """
    lowered = normalize_text(text).lower()
    return {
        token for token in _CONTENT_TOKEN_RE.findall(lowered)
        if len(token) > 1 and token not in STOPWORDS and not YEAR_RE.fullmatch(token)
    }


def content_bigrams(text: str) -> set[str]:
    """Adjacent token pairs with at least one content token, accents kept.

    Vietnamese words are mostly two syllables, so two shared *tokens* can be
    one shared word ("năng lượng"); a shared bigram is closer to a shared word
    and is what the support-cue check counts.
    """
    tokens = _CONTENT_TOKEN_RE.findall(normalize_text(text).lower())
    return {
        f"{a} {b}" for a, b in zip(tokens, tokens[1:], strict=False)
        if (a not in STOPWORDS or b not in STOPWORDS)
        and not (YEAR_RE.fullmatch(a) or YEAR_RE.fullmatch(b))
    }


def stable_id(*parts: str, length: int = 16) -> str:
    digest = hashlib.sha256("||".join(parts).encode("utf-8", errors="ignore")).hexdigest()
    return digest[:length]


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


# Words after which a number is a label, not a quantity: "phạm vi 1 và 2",
# "Scope 3", "ISO 14064-1", "Điều 5", "Bảng 7", "QĐ 21/2025". Comparing the 1
# in "Scope 1" against the 1 in another "Scope 1" produced a 0% relative error
# and a false SUPPORTS that hid a real 30% vs 8% conflict.
LABEL_WORDS = (
    "pham vi", "scope", "tier", "category", "cat", "iso", "tcvn", "qcvn", "gri", "sdg", "sasb",
    "dieu", "khoan", "muc", "phu luc", "chuong", "phan", "bang", "hinh", "trang", "thuyet minh",
    "chu thich", "ghi chu", "section", "article", "clause", "table", "figure", "fig", "page", "note",
    "appendix", "annex", "chapter", "part", "item", "step", "buoc", "giai doan", "phase", "quy", "q",
    "nghi dinh", "quyet dinh", "thong tu", "luat", "nd", "qd", "tt", "so", "no", "ref", "id", "ma",
)
_LABEL_RE = re.compile(
    r"(?:^|(?<=\W))(?:" + "|".join(re.escape(w) for w in LABEL_WORDS) + r")\.?\s*$"
)
# Enumerator at the start of a line/sentence: "4.1 |", "2) ", "III.".
_LABEL_CHAIN_RE = re.compile(r"[\s,]*(?:va|and|&|\+|to|den|-|toi|hoac|or)?[\s,]*")
_ENUMERATOR_RE = re.compile(r"^\s*(?:\d+(?:\.\d+)*|[ivx]+)\s*[.)|:\-–]\s")

_MULTIPLIERS = {
    "nghin": 1e3, "ngan": 1e3, "thousand": 1e3, "k": 1e3,
    "trieu": 1e6, "million": 1e6, "mn": 1e6, "mil": 1e6,
    "ty": 1e9, "billion": 1e9, "bn": 1e9,
}
# Canonical unit per surface form (surface forms are accent-folded).
_UNITS = [
    (r"t\s*co2\s*(?:e|eq|td|tuong duong)?|tan\s*co2\s*(?:e|eq|td|tuong duong)?|tco2|tan co2", "tco2e"),
    (r"kg\s*co2\s*(?:e|eq)?", "kgco2e"),
    (r"co2\s*(?:e|eq)?", "tco2e"),
    (r"gwh", "gwh"), (r"mwh", "mwh"), (r"kwh", "kwh"), (r"gj", "gj"), (r"mj", "mj"), (r"tj", "tj"),
    (r"m3|m³|met khoi", "m3"), (r"tan|tonnes?|tons?", "tan"), (r"kg", "kg"), (r"ha", "ha"),
    (r"vnd|dong|usd|eur", "currency"), (r"%|phan tram|percent", "%"),
]
_UNIT_RE = re.compile(
    r"\s*(?P<mult>" + "|".join(_MULTIPLIERS) + r")?\s*(?P<unit>" + "|".join(u for u, _ in _UNITS) + r")?(?!\w)",
    re.IGNORECASE,
)
_NUMBER_TOKEN_RE = re.compile(r"(?<![\w./-])(\d[\d.,]*)")
_SCOPE_RE = re.compile(r"(?:scope|pham vi)\s*((?:[123]\s*(?:,|va|and|&|\+|-|to|den)?\s*)+)(?!\d)")


def _canonical_unit(surface: str | None) -> str | None:
    if not surface:
        return None
    for pattern, canon in _UNITS:
        if re.fullmatch(pattern, surface, re.IGNORECASE):
            return canon
    return surface


def _parse_locale_number(raw: str) -> float | None:
    """Vietnamese and English digit groups: 1.200.000 · 1,2 · 1,200,000 · 1.2 · 12,5%."""
    raw = raw.strip().rstrip(".,")
    if not raw:
        return None
    dots, commas = raw.count("."), raw.count(",")
    if dots and commas:
        last_dot, last_comma = raw.rfind("."), raw.rfind(",")
        if last_comma > last_dot:  # 1.234,56
            cleaned = raw.replace(".", "").replace(",", ".")
        else:  # 1,234.56
            cleaned = raw.replace(",", "")
    elif dots > 1 or (dots == 1 and re.fullmatch(r"\d{1,3}\.\d{3}", raw)):
        cleaned = raw.replace(".", "")  # 1.200.000 · 1.200
    elif commas > 1 or (commas == 1 and re.fullmatch(r"\d{1,3},\d{3}", raw) and not re.fullmatch(r"\d,\d{3}", raw)):
        cleaned = raw.replace(",", "")  # 1,200,000 · 12,000
    else:
        cleaned = raw.replace(",", ".")  # 1,2 · 12,5 · 0,8
    try:
        return float(cleaned)
    except ValueError:
        return None


# A number followed by an ALL-CAPS word is a section number in a PDF text flow
# ("5.1 KIỂM KÊ KHÍ NHÀ KÍNH", "1 GIỚI THIỆU"); decided on the original text
# because case is lost after normalisation.
_HEADING_NUMBER_RE = re.compile(r"(?<![\w.,])\d+(?:\.\d+)*\s+(?=[A-ZÀ-Ỹ]{2,})")
# "05 bộ khung": a leading zero marks an enumerator, not a quantity (decimals
# such as 0,7 / 0.7 keep their zero because it is followed by a separator).
_LEADING_ZERO_RE = re.compile(r"^0\d")


def _half_unit(raw: str, multiplier: float) -> float:
    """Half of the last significant digit's place: the precision a figure was published to.

    "12" → 0.5 · "12,5" → 0.05 · "1,2 triệu" → 50 000 · "112.000" → 500 (the
    trailing zeros of an integer are taken as rounding, not as precision).
    """
    cleaned = raw.strip().rstrip(".,")
    digits = re.sub(r"[.,]", "", cleaned)
    dots, commas = cleaned.count("."), cleaned.count(",")
    decimals = 0
    if dots and commas:
        sep = "," if cleaned.rfind(",") > cleaned.rfind(".") else "."
        decimals = len(cleaned.rsplit(sep, 1)[1])
    elif commas == 1 and not re.fullmatch(r"\d{1,3},\d{3}", cleaned):
        decimals = len(cleaned.split(",")[1])
    elif dots == 1 and not re.fullmatch(r"\d{1,3}\.\d{3}", cleaned):
        decimals = len(cleaned.split(".")[1])
    if decimals:
        place = -decimals
    else:
        stripped = digits.rstrip("0")
        place = len(digits) - len(stripped)  # trailing integer zeros are rounding
    return 0.5 * (10 ** place) * multiplier


def parse_quantities(text: str) -> list[tuple[float, str | None, float]]:
    """Quantities as (value, canonical unit, half-unit of published precision)."""
    return list(_iter_quantities(text))


def parse_numbers(text: str) -> list[tuple[float, str | None]]:
    """Quantities in the text as (value, canonical unit).

    Not returned: numbers that label something (scope, standard, clause, table,
    document number), section enumerators, and parts of identifiers such as
    14064-1 or 21/2025. Multipliers are applied (1,2 triệu → 1200000) and units
    are canonicalised so tấn CO2e and tCO2e compare.
    """
    return [(value, unit) for value, unit, _ in _iter_quantities(text)]


def _iter_quantities(text: str):
    normalized = normalize_for_match(_HEADING_NUMBER_RE.sub(" ", normalize_text(text)))
    normalized = _ENUMERATOR_RE.sub(" ", normalized)
    values: list[tuple[float, str | None, float]] = []
    label_end = -1  # end offset of the last label number, for "1 và 2", "1, 2 and 3"
    for match in _NUMBER_TOKEN_RE.finditer(normalized):
        raw = match.group(1)
        before = normalized[: match.start()]
        after = normalized[match.end():]
        gap = normalized[label_end: match.start()]
        chained = label_end >= 0 and len(gap) <= 8 and _LABEL_CHAIN_RE.fullmatch(gap)
        if _LABEL_RE.search(before[-24:]) or chained:
            label_end = match.end()
            continue
        if after[:1] in {"/", "-"} and after[1:2].isdigit():
            continue  # 21/2025, 14064-1
        if _LEADING_ZERO_RE.match(raw):
            continue  # 05, 08 -- enumerators
        value = _parse_locale_number(raw)
        if value is None:
            continue
        tail = _UNIT_RE.match(after)
        multiplier = 1.0
        unit = None
        if tail:
            if tail.group("mult"):
                multiplier = _MULTIPLIERS[tail.group("mult").lower()]
            unit = _canonical_unit(tail.group("unit"))
        values.append((value * multiplier, unit, _half_unit(raw, multiplier)))
    return values


def emission_scopes(text: str) -> frozenset[int]:
    """GHG scopes named in the text: "Scope 1 và 2" → {1, 2}; "Scope 1, 2 và 3" → {1, 2, 3}."""
    scopes: set[int] = set()
    for group in _SCOPE_RE.findall(normalize_for_match(text)):
        scopes.update(int(d) for d in re.findall(r"[123]", group))
    return frozenset(scopes)


def split_sentences(text: str) -> list[str]:
    text = normalize_text(text)
    parts = re.split(r"(?<=[.!?])\s+|\n+|(?<=;)\s+", text)
    return [part.strip(" •\t") for part in parts if len(part.strip()) >= 12]


def path_name(path: str) -> str:
    return Path(path).name
