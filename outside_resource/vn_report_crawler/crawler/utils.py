from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from urllib.parse import parse_qs, urlparse, urlunparse

YEAR_RE = re.compile(r"\b(20(?:0\d|1\d|2\d|3\d))\b")


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return re.sub(r"\s+", " ", value).strip().lower()


def fold_text(value: str) -> str:
    """Bỏ dấu và coi -_. như khoảng trắng, để so khớp không phụ thuộc cách đặt tên.

    Tài liệu trên CDN thường có tên đã ASCII hoá và nối bằng gạch dưới:
        Bao_cao_quan_tri_Cong_ty_nam_2018.pdf
    Nếu chỉ normalize thường thì chuỗi này không bao giờ khớp "báo cáo quản trị"
    và tài liệu bị phân loại thành None.
    """
    value = unicodedata.normalize("NFD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    # đ/Đ không phải tổ hợp dấu nên phải xử lý riêng
    value = value.replace("đ", "d").replace("Đ", "D")
    value = re.sub(r"[_\-.]+", " ", value)
    return re.sub(r"\s+", " ", value).strip().lower()


def slugify(value: str, max_len: int = 140) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-_.").lower()
    return (value[:max_len] or "unknown").strip("-")


def extract_year(*values: str) -> int | None:
    for value in values:
        match = YEAR_RE.search(value or "")
        if match:
            return int(match.group(1))
    return None


def canonical_url(url: str) -> str:
    p = urlparse(url)
    return urlunparse((p.scheme.lower(), p.netloc.lower(), p.path, "", p.query, ""))


def domain_allowed(url: str, allowed_domains: list[str]) -> bool:
    host = (urlparse(url).hostname or "").lower()
    if not host:
        return False
    return any(host == d or host.endswith("." + d) for d in (x.lower() for x in allowed_domains))


def filename_from_url(url: str) -> str:
    """Lấy tên file gốc từ path hoặc từ query (?FileName=..., ?file=...)."""
    parsed = urlparse(url)
    for values in parse_qs(parsed.query).values():
        for value in values:
            name = Path(value).name
            if "." in name:
                return name
    return Path(parsed.path).name or "document"


def extract_ticker(*values: str) -> str | None:
    """Đoán mã chứng khoán 3 ký tự in hoa từ tiêu đề hoặc tên file."""
    for value in values:
        match = re.search(r"\b([A-Z]{3})\b", value or "")
        if match:
            return match.group(1)
    return None
