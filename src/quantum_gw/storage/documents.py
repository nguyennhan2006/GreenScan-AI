"""Persistent store for analysed source documents.

Uploads previously went into a `TemporaryDirectory` that was deleted the moment
analysis returned, so a citation could name "page 42" of a file that no longer
existed. Evidence you cannot reopen is not auditable, which is the whole point
of the product.

Two properties matter:

* **Stable ``doc_id``.** The parser derives it from the resolved file path, so a
  temp path produced a different id on every run. Writing bytes to a permanent,
  content-addressed path makes the id reproducible, and citations survive
  restarts.
* **Deduplication.** The same report analysed twice is one blob on disk; the
  index keeps every logical registration pointing at it.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from quantum_gw.utils.text import stable_id

# Extensions we are willing to hand back over HTTP.
SERVABLE = {".pdf", ".txt", ".md", ".json", ".csv", ".html", ".xml"}


@dataclass(frozen=True)
class StoredDocument:
    doc_id: str
    sha256: str
    name: str
    path: Path
    content_type: str
    bytes: int

    def to_json(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "sha256": self.sha256,
            "name": self.name,
            "path": str(self.path),
            "content_type": self.content_type,
            "bytes": self.bytes,
        }


class DocumentStore:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root or os.environ.get("QUANTUM_DOCUMENTS_DIR", ".quantum/documents"))
        self.blobs = self.root / "blobs"
        self.index_path = self.root / "index.jsonl"

    # ---------- writing ----------

    def put(self, data: bytes, name: str) -> StoredDocument:
        """Persist bytes and return the record, including the id the parser will derive."""
        self.blobs.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(data).hexdigest()
        suffix = Path(name).suffix.lower() or ".bin"
        path = self.blobs / digest[:2] / f"{digest}{suffix}"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

        record = StoredDocument(
            # Must match DocumentParser.parse: stable_id(resolved path, display name).
            doc_id=stable_id(str(path.resolve()), name),
            sha256=digest,
            name=name,
            path=path,
            content_type=mimetypes.guess_type(name)[0] or "application/octet-stream",
            bytes=len(data),
        )
        self._append_index(record)
        return record

    def _append_index(self, record: StoredDocument) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        if self.get(record.doc_id) is not None:
            return
        line = json.dumps(
            {**record.to_json(), "stored_at": datetime.now(UTC).isoformat()},
            ensure_ascii=False,
        )
        with self.index_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    # ---------- reading ----------

    def get(self, doc_id: str) -> StoredDocument | None:
        if not self.index_path.is_file():
            return None
        # split("\n"), not splitlines(): a filename may contain U+2028.
        for line in self.index_path.read_text(encoding="utf-8").split("\n"):
            if not line.strip():
                continue
            row = json.loads(line)
            if row["doc_id"] != doc_id:
                continue
            path = Path(row["path"])
            if not path.is_file():
                return None
            return StoredDocument(
                doc_id=row["doc_id"], sha256=row["sha256"], name=row["name"],
                path=path, content_type=row["content_type"], bytes=row["bytes"],
            )
        return None

    def is_servable(self, record: StoredDocument) -> bool:
        return record.path.suffix.lower() in SERVABLE


def highlight_rects(pdf_path: Path, page_number: int, needle: str, limit: int = 12) -> list[tuple]:
    """Rectangles on `page_number` matching `needle`.

    Chunks span several layout blocks and carry normalised whitespace, so an
    exact search for the whole chunk almost never hits. Probing progressively
    shorter leading fragments is what makes the highlight land in practice.
    Returns [] rather than raising when nothing matches — a page with no
    highlight is still useful to the reviewer.
    """
    import fitz

    with fitz.open(pdf_path) as doc:
        if page_number < 1 or page_number > doc.page_count:
            return []
        page = doc[page_number - 1]
        cleaned = " ".join((needle or "").split())
        for length in (220, 140, 90, 60, 40):
            probe = cleaned[:length].strip()
            if len(probe) < 20:
                continue
            rects = page.search_for(probe)
            if rects:
                return [tuple(r) for r in rects[:limit]]
        # Last resort: the longest single line, which survives re-flowed text.
        lines = sorted((ln.strip() for ln in (needle or "").split("\n")), key=len, reverse=True)
        for line in lines[:3]:
            if len(line) >= 25:
                rects = page.search_for(line[:120])
                if rects:
                    return [tuple(r) for r in rects[:limit]]
    return []


def render_page_png(pdf_path: Path, page_number: int, rects: list[tuple], zoom: float = 2.0) -> bytes:
    """Render one page to PNG with `rects` highlighted.

    Rendering server-side keeps the browser free of a PDF engine and works
    identically for scanned pages, where a text-layer highlight would fail.
    """
    import fitz

    with fitz.open(pdf_path) as doc:
        page = doc[page_number - 1]
        for rect in rects:
            annot = page.add_highlight_annot(fitz.Rect(*rect))
            annot.set_colors(stroke=(1, 0.85, 0.2))
            annot.update(opacity=0.45)
        return page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).tobytes("png")


def page_count(pdf_path: Path) -> int:
    import fitz

    with fitz.open(pdf_path) as doc:
        return doc.page_count
