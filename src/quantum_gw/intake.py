"""What a document will give the pipeline, said before the pipeline runs.

The audit of 14/10 fed the parser a scanned page on the demo laptop: no
tesseract, so `ocr_page` returned "" and the page became zero passages -- no
error, no warning, and a run that would have ended "no claims found". The
preview reads each file the way the parser will (native text per page, OCR
availability) and says which pages will come out empty, how long the run
should take, and what the file looks like it is (company, year, report type),
so the reviewer confirms instead of filling in.

URL fetching lives here too: the browser cannot download a report from another
site, so the server does it and hands the bytes back as an ordinary upload.
"""

from __future__ import annotations

import ipaddress
import re
import socket
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

import fitz

from quantum_gw.parsers.ocr import TesseractOCR
from quantum_gw.parsers.office import docx_text, html_text
from quantum_gw.settings import IntakeSettings

# Calibrated on HPG BCPTBV 2025 + BCTN 2024: 264 pages in 107-121 s on a laptop
# CPU (benchmark/queue_quality_2026-10-06.md). Text-only files are timed by
# their length in "page equivalents" of 2,500 characters.
SECONDS_PER_PAGE = 0.45
CHARS_PER_PAGE = 2500
MAX_FETCH_BYTES = 60 * 1024 * 1024

_VI_CHARS = re.compile(r"[ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]", re.I)
_SENTENCE_END = re.compile(r"[.!?;](\s|$)")
_YEAR = re.compile(r"\b(20[12]\d)\b")
_COMPANY = re.compile(
    r"(?:CÔNG TY CỔ PHẦN|Công ty Cổ phần|CTCP|TẬP ĐOÀN|Tập đoàn|TỔNG CÔNG TY|Tổng Công ty)\s+"
    r"([A-ZÀ-Ỹ][\wÀ-ỹ&.\- ]{2,50}?)(?=\s*(?:\n|,|\.|;|\(|-|–|$))"
)
_TICKER = re.compile(r"^([A-Z]{3})(?:[_\-\s]|$)")
_REPORT_TYPES = [
    ("sustainability", "Báo cáo phát triển bền vững", r"phát triển bền vững|sustainab|\besg\b|bcptbv"),
    ("annual", "Báo cáo thường niên", r"thường niên|annual report|bctn"),
    ("financial", "Báo cáo tài chính", r"báo cáo tài chính|financial statement|bctc|thuyết minh"),
    ("ghg_inventory", "Báo cáo kiểm kê khí nhà kính", r"kiểm kê khí nhà kính|ghg inventory|iso 14064"),
    ("legal", "Văn bản pháp lý", r"nghị định|thông tư|quyết định số|luật số|bản án"),
]
# Role and source type the intake screen should preselect for each report type.
_DEFAULTS = {
    "sustainability": ("claim_source", "internal"),
    "annual": ("claim_source", "internal"),
    "financial": ("evidence", "financial"),
    "ghg_inventory": ("evidence", "environmental"),
    "legal": ("evidence", "legal"),
}


def _guess(name: str, sample: str) -> dict:
    # The file name decides when it names the type; otherwise the type the first
    # pages mention most (an annual report mentions "phát triển bền vững" too).
    plain_name = re.sub(r"[_\-.]+", " ", name.lower())
    lowered = sample[:20000].lower()
    scores = {key: (100 if re.search(pattern, plain_name) else 0) + len(re.findall(pattern, lowered))
              for key, _, pattern in _REPORT_TYPES}
    best = max(scores, key=scores.get)
    report = (best, next(label for key, label, _ in _REPORT_TYPES if key == best)) if scores[best] else (None, None)
    years = Counter(int(y) for y in _YEAR.findall(sample[:20000] or name))
    company = None
    for match in _COMPANY.finditer(sample[:20000]):
        candidate = re.sub(r"\s+", " ", match.group(1)).strip(" -–")
        if len(candidate) >= 3:
            company = candidate
            break
    ticker = _TICKER.match(Path(name).name)
    vi_ratio = len(_VI_CHARS.findall(sample)) / max(1, len(sample))
    role, source_type = _DEFAULTS.get(report[0] or "", ("claim_source", "internal"))
    return {
        "report_type": report[0],
        "report_type_label": report[1],
        "year": years.most_common(1)[0][0] if years else None,
        "company": company,
        "ticker": ticker.group(1) if ticker else None,
        "language": "vi" if vi_ratio > 0.01 else "en",
        "suggested_role": role,
        "suggested_source_type": source_type,
    }


def _sentences(text: str) -> int:
    return len(_SENTENCE_END.findall(text)) + (1 if text.strip() and not _SENTENCE_END.search(text[-3:]) else 0)


def preview_file(path: str | Path, name: str, settings: IntakeSettings) -> dict:
    """Pages with text, pages that need OCR, sentences, time estimate and a first guess of what the file is."""
    path = Path(path)
    suffix = path.suffix.lower()
    ocr = TesseractOCR(settings.tesseract_command, settings.ocr_languages)
    out: dict = {"name": name, "kind": suffix.lstrip("."), "warnings": []}
    if suffix == ".pdf":
        pdf = fitz.open(path)
        scanned: list[int] = []
        sample_parts: list[str] = []
        sentences = 0
        for number, page in enumerate(pdf, start=1):
            text = page.get_text("text")
            if len(text.strip()) < settings.min_native_text_chars:
                scanned.append(number)
            else:
                sentences += _sentences(text)
                if number <= 4:
                    sample_parts.append(text)
        pages = pdf.page_count
        pdf.close()
        out.update(pages=pages, text_pages=pages - len(scanned), scanned_pages=scanned,
                   sentences=sentences, estimated_seconds=round(pages * SECONDS_PER_PAGE))
        sample = "\n".join(sample_parts)
        if scanned:
            if settings.ocr_enabled and ocr.available:
                out["warnings"].append(
                    f"{len(scanned)} trang là ảnh quét; sẽ OCR (chậm hơn, có thể sai dấu)."
                )
                out["estimated_seconds"] += len(scanned) * 4
            else:
                out["warnings"].append(
                    f"{len(scanned)}/{pages} trang là ảnh quét nhưng máy này không có OCR (tesseract): "
                    "những trang đó sẽ không có chữ nào."
                )
    else:
        if suffix == ".docx":
            text = docx_text(path)
        elif suffix in {".html", ".htm"}:
            text = html_text(path.read_text(encoding="utf-8", errors="ignore"))
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")
        page_equivalents = max(1, round(len(text) / CHARS_PER_PAGE))
        out.update(pages=None, text_pages=None, scanned_pages=[], sentences=_sentences(text),
                   estimated_seconds=max(2, round(page_equivalents * SECONDS_PER_PAGE)))
        sample = text[:20000]
        if not text.strip():
            out["warnings"].append("Không đọc được chữ nào từ tệp này.")
    out["ocr_available"] = bool(settings.ocr_enabled and ocr.available)
    out["guess"] = _guess(name, sample)
    return out


# ---------- URL ----------

class FetchError(ValueError):
    pass


def _check_host(host: str) -> None:
    """Refuse loopback, private and link-local targets: this endpoint must not reach the machine's own network."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise FetchError(f"Không phân giải được tên miền {host}.") from exc
    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved or address.is_multicast:
            raise FetchError("Địa chỉ nội bộ không được phép tải.")


class _CheckedRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlparse(newurl)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise FetchError("Chuyển hướng tới địa chỉ không hợp lệ.")
        _check_host(parsed.hostname)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_EXTENSIONS = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/html": ".html",
    "text/plain": ".txt",
}


def fetch_url(url: str, opener=None) -> tuple[bytes, str]:
    """Download a report; returns (bytes, file name with the right extension)."""
    parsed = urllib.parse.urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise FetchError("Chỉ nhận đường dẫn http:// hoặc https://.")
    _check_host(parsed.hostname)
    opener = opener or urllib.request.build_opener(_CheckedRedirects)
    request = urllib.request.Request(url.strip(), headers={"User-Agent": "GreenScan/1.0 (+report intake)"})
    with opener.open(request, timeout=30) as response:
        content_type = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        data = response.read(MAX_FETCH_BYTES + 1)
        disposition = response.headers.get("Content-Disposition") or ""
    if len(data) > MAX_FETCH_BYTES:
        raise FetchError("Tệp lớn hơn 60 MB.")
    name = ""
    match = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)', disposition)
    if match:
        name = urllib.parse.unquote(match.group(1))
    if not name:
        name = urllib.parse.unquote(Path(parsed.path).name) or parsed.hostname
    suffix = Path(name).suffix.lower()
    if data[:4] == b"%PDF":
        wanted = ".pdf"
    elif data[:2] == b"PK" and suffix == ".docx":
        wanted = ".docx"
    else:
        wanted = _EXTENSIONS.get(content_type, suffix if suffix in {".pdf", ".docx", ".html", ".htm", ".txt"} else "")
    if not wanted:
        raise FetchError(f"Không nhận dạng được loại tệp ({content_type or 'không rõ'}).")
    if suffix != wanted:
        name = f"{Path(name).stem or 'tai-lieu'}{wanted}"
    return data, name


# ---------- demo samples ----------

SAMPLE_SETS = [
    {
        "id": "hpg",
        "label": "Hòa Phát (HPG): BCPTBV 2025 + BCTN 2024",
        "company": "Hòa Phát",
        "files": [
            {"path": "data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf",
             "role": "claim_source", "source_type": "internal"},
            {"path": "data/real_cases/sources/originals/HPG_Annual_Report_2024.pdf",
             "role": "evidence", "source_type": "internal"},
        ],
    },
]


def sample_sets(root: str | Path = ".") -> list[dict]:
    """Sample sets whose files exist here (the PDFs are not in git)."""
    root = Path(root)
    out = []
    for sample in SAMPLE_SETS:
        files = [f for f in sample["files"] if (root / f["path"]).is_file()]
        if len(files) == len(sample["files"]):
            out.append({**sample, "files": [{**f, "name": Path(f["path"]).name,
                                             "bytes": (root / f["path"]).stat().st_size} for f in files]})
    return out


def sample_file(sample_id: str, index: int, root: str | Path = ".") -> Path | None:
    for sample in SAMPLE_SETS:
        if sample["id"] == sample_id and 0 <= index < len(sample["files"]):
            path = Path(root) / sample["files"][index]["path"]
            return path if path.is_file() else None
    return None
