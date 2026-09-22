"""Khử trùng lặp theo nội dung và chọn canonical source.

Nguyên tắc: KHÔNG hợp nhất bản ghi logic. Hai URL trỏ cùng nội dung vẫn là hai
document riêng với provenance riêng; chúng chỉ dùng chung một object. Canonical
source được chọn theo authority score để bước indexing về sau biết nên lấy bản
nào làm gốc.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..models import AUTHORITY_SCORE, SourceAuthority
from ..storage.database import Database
from ..storage.object_store import ObjectStore


@dataclass
class StoreResult:
    sha256: str
    path: Path
    is_duplicate: bool
    existing_document_ids: list[str]


class Deduplicator:
    def __init__(self, store: ObjectStore, db: Database):
        self.store = store
        self.db = db

    def store_content(self, content: bytes, extension: str) -> StoreResult:
        sha256 = ObjectStore.digest(content)
        existing = self.db.documents_for_object(sha256)
        _, path, is_new = self.store.put_object(content, extension)
        self.db.register_object(sha256, extension, path, len(content))
        return StoreResult(
            sha256=sha256,
            path=path,
            is_duplicate=not is_new or bool(existing),
            existing_document_ids=[row["document_id"] for row in existing],
        )

    def canonical_document(self, sha256: str) -> str | None:
        """Chọn document có authority cao nhất trong nhóm cùng nội dung.

        Thứ tự: authority cao nhất -> phát hiện sớm nhất -> document_id nhỏ nhất.
        Hai tiêu chí sau bảo đảm kết quả ỔN ĐỊNH: thêm một bản mirror mới không
        được làm đổi canonical của cả nhóm.
        """
        rows = self.db.documents_for_object(sha256)
        if not rows:
            return None

        def sort_key(row) -> tuple[int, str, str]:
            try:
                authority = SourceAuthority(row["source_authority"])
            except (ValueError, TypeError):
                authority = SourceAuthority.MIRROR
            return (
                -AUTHORITY_SCORE[authority],
                row["discovered_at"] or "",
                row["document_id"] or "",
            )

        return min(rows, key=sort_key)["document_id"]

    def refresh_canonical(self, sha256: str) -> str | None:
        """Tính lại canonical và ghi cho TOÀN BỘ nhóm cùng object.

        Canonical là thuộc tính của nhóm, không phải của từng document. Nếu chỉ
        ghi lúc tải xong thì bản ghi cũ sẽ giữ giá trị lỗi thời khi có tài liệu
        mới cùng nội dung xuất hiện.
        """
        canonical = self.canonical_document(sha256)
        if canonical is not None:
            self.db.set_canonical(sha256, canonical)
        return canonical
