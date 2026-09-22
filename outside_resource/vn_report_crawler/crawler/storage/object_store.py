"""Content-addressed store: bytes lưu theo SHA-256, tách khỏi tên logic của tài liệu.

Bản cũ ghi thẳng file theo slug của tiêu đề, nên khi hai URL trỏ tới cùng nội
dung, bản ghi "báo cáo thường niên 2023" lại có local_path là
`.../2024/bao-cao-phat-trien-ben-vung-2024.pdf`. Tách object khỏi document giải
quyết việc đó: nhiều document có thể tham chiếu cùng một object mà vẫn giữ
nguyên provenance riêng.

    data/
    ├── objects/sha256/ab/abcdef....pdf
    └── documents/<source_id>/<ticker>/<year>/<report_type>-<short_hash>.json
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ..utils import slugify


class ObjectStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.objects_dir = self.root / "objects" / "sha256"
        self.documents_dir = self.root / "documents"
        self.objects_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def digest(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def object_path(self, sha256: str, extension: str) -> Path:
        ext = extension if extension.startswith(".") else f".{extension}"
        return self.objects_dir / sha256[:2] / f"{sha256}{ext}"

    def has_object(self, sha256: str, extension: str) -> bool:
        return self.object_path(sha256, extension).exists()

    def put_object(self, content: bytes, extension: str) -> tuple[str, Path, bool]:
        """Ghi bytes vào CAS. Trả về (sha256, path, is_new)."""
        sha256 = self.digest(content)
        path = self.object_path(sha256, extension)
        if path.exists():
            return sha256, path, False
        path.parent.mkdir(parents=True, exist_ok=True)
        # Ghi tạm rồi rename để tránh file hỏng khi bị ngắt giữa chừng.
        tmp = path.with_suffix(path.suffix + ".part")
        tmp.write_bytes(content)
        tmp.replace(path)
        return sha256, path, True

    def document_path(self, document_id: str, meta: dict[str, Any]) -> Path:
        source_id = meta.get("source_id") or "unknown"
        ticker = meta.get("ticker") or "unknown"
        year = meta.get("year") or "unknown"
        report_type = meta.get("report_type") or "other"
        short = hashlib.sha1(document_id.encode("utf-8")).hexdigest()[:8]
        name = f"{slugify(report_type)}-{short}.json"
        return self.documents_dir / slugify(source_id) / slugify(str(ticker)) / str(year) / name

    def put_document(self, document_id: str, meta: dict[str, Any]) -> Path:
        path = self.document_path(document_id, meta)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(meta)
        payload["document_id"] = document_id
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path


def make_document_id(source_id: str, ticker: str | None, year: int | None,
                     report_type: str | None, url: str) -> str:
    """ID logic ổn định: source:ticker:year:type:hash(url)."""
    url_hash = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    parts = [
        source_id,
        ticker or "unknown",
        str(year or "unknown"),
        report_type or "other",
        url_hash,
    ]
    return ":".join(parts)
