from __future__ import annotations
import io, zipfile
from pathlib import Path
from urllib.parse import urlparse
MIME={
 "application/pdf":".pdf", "application/msword":".doc",
 "application/vnd.ms-excel":".xls",
 "application/vnd.openxmlformats-officedocument.wordprocessingml.document":".docx",
 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":".xlsx",
 "text/csv":".csv", "text/html":".html", "application/xhtml+xml":".html"
}
def infer_extension(url: str, content_type: str, content: bytes) -> str|None:
    if content.startswith(b"%PDF-"): return ".pdf"
    if content.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                names=z.namelist()
                if any(x.startswith("word/") for x in names): return ".docx"
                if any(x.startswith("xl/") for x in names): return ".xlsx"
        except zipfile.BadZipFile: pass
    mime=(content_type or "").split(";",1)[0].strip().lower()
    if mime in MIME: return MIME[mime]
    suffix=Path(urlparse(url).path).suffix.lower()
    return ".html" if suffix==".htm" else suffix if suffix in {".pdf",".doc",".docx",".xls",".xlsx",".csv",".html"} else None
