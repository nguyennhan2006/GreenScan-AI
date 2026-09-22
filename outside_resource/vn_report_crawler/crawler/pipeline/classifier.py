"""Phân loại tài liệu và chuẩn hoá metadata mô tả."""

from __future__ import annotations

from ..utils import fold_text

# Từ khoá mặc định, dùng khi source config không khai báo report_types riêng.
DEFAULT_REPORT_TYPES: dict[str, list[str]] = {
    "sustainability": [
        "báo cáo phát triển bền vững",
        "phát triển bền vững",
        "sustainability report",
        "esg report",
        "esg",
    ],
    "annual": ["báo cáo thường niên", "annual report"],
    "financial": [
        "báo cáo tài chính",
        "bctc",
        "financial statements",
        "financial statement",
    ],
    "governance": [
        "báo cáo quản trị",
        "quản trị công ty",
        # Biến thể quan sát được trong dry-run thật trên vinamilk.com.vn:
        # "Bao_cao_QTCT_ca_nam_2025", "Bao_cao_tinh_hinh_quan_tri_cong_ty_nam_2015".
        # "báo cáo quản trị" không khớp vì so khớp là substring liền mạch.
        "tình hình quản trị",
        "qtct",
        "corporate governance report",
    ],
    "prospectus": ["bản cáo bạch", "prospectus"],
    "bond_disclosure": ["trái phiếu", "bond", "công bố thông tin trái phiếu"],
    "explanatory": [
        "giải trình",
        "công văn",
        "explanation",
        "kqkd",  # giai-trinh-kqkd-hop-nhat-6-thang-dau-nam-2025.pdf
    ],
}

_SCOPE_KEYWORDS = {
    "consolidated": ["hợp nhất", "consolidated"],
    "separate": ["riêng", "công ty mẹ", "separate", "parent company"],
}

_PERIOD_KEYWORDS = {
    "quarterly": ["quý", "quarter", "q1", "q2", "q3", "q4"],
    "semiannual": ["bán niên", "giữa niên độ", "6 tháng", "interim", "half year"],
    "annual": ["năm", "thường niên", "annual", "full year"],
}

_ASSURANCE_KEYWORDS = {
    "audited": ["đã kiểm toán", "kiểm toán", "audited"],
    "reviewed": ["soát xét", "reviewed"],
}


def classify_report(text: str, report_types: dict[str, list[str]] | None = None) -> str | None:
    """Trả về report_type khớp nhiều từ khoá nhất, hoặc None."""
    haystack = fold_text(text)
    types = report_types or DEFAULT_REPORT_TYPES
    scored: list[tuple[int, int, str]] = []
    for report_type, phrases in types.items():
        matched = [p for p in phrases if fold_text(p) in haystack]
        if matched:
            # Ưu tiên số từ khoá khớp, rồi tới độ dài từ khoá dài nhất (cụ thể hơn).
            scored.append((len(matched), max(len(fold_text(p)) for p in matched), report_type))
    if not scored:
        return None
    scored.sort(reverse=True)
    return scored[0][2]


def excluded(text: str, patterns: list[str]) -> bool:
    haystack = fold_text(text)
    return any(fold_text(p) in haystack for p in patterns)


def _first_match(haystack: str, mapping: dict[str, list[str]]) -> str | None:
    for label, keywords in mapping.items():
        if any(fold_text(k) in haystack for k in keywords):
            return label
    return None


def describe_document(text: str) -> dict[str, str | None]:
    """Trích các chiều mô tả phụ để phục vụ sampling theo quota."""
    haystack = fold_text(text)
    return {
        "statement_scope": _first_match(haystack, _SCOPE_KEYWORDS),
        "period_type": _first_match(haystack, _PERIOD_KEYWORDS),
        "assurance_status": _first_match(haystack, _ASSURANCE_KEYWORDS),
    }
