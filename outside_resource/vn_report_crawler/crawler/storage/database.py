"""SQLite metadata store.

Bảng `documents` là bản ghi logic (mỗi URL nguồn một dòng, giữ nguyên
provenance). Bảng `objects` là nội dung thực (mỗi SHA-256 một dòng). Nhiều
document có thể trỏ về cùng một object.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..models import CrawlStatus

SCHEMA = """
CREATE TABLE IF NOT EXISTS objects (
    sha256 TEXT PRIMARY KEY,
    extension TEXT NOT NULL,
    object_path TEXT NOT NULL,
    content_length INTEGER,
    first_seen_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    adapter TEXT,
    source_authority TEXT,
    company TEXT,
    ticker TEXT,
    report_type TEXT,
    document_family TEXT,
    statement_scope TEXT,
    period_type TEXT,
    assurance_status TEXT,
    title TEXT,
    year INTEGER,
    source_page_url TEXT,
    file_url TEXT NOT NULL,
    canonical_source_url TEXT,
    original_filename TEXT,
    object_sha256 TEXT REFERENCES objects(sha256),
    -- Thuộc tính của NHÓM cùng object, được tính lại mỗi khi nhóm thay đổi.
    canonical_document_id TEXT,
    file_format TEXT,
    discovered_at TEXT NOT NULL,
    downloaded_at TEXT,
    crawl_status TEXT NOT NULL DEFAULT 'discovered',
    attempt_count INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TEXT,
    last_error_code TEXT,
    last_error_message TEXT,
    next_retry_at TEXT,
    metadata_json TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_file_url ON documents(file_url);
CREATE INDEX IF NOT EXISTS idx_documents_company_year ON documents(company, year);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(report_type);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(crawl_status);
CREATE INDEX IF NOT EXISTS idx_documents_object ON documents(object_sha256);
"""

TERMINAL_STATUSES = {
    CrawlStatus.DOWNLOADED.value,
    CrawlStatus.DUPLICATE.value,
}


class Database:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "metadata.sqlite3"
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    @staticmethod
    def now() -> str:
        return datetime.now(UTC).isoformat()

    # ---------------- objects ----------------

    def register_object(self, sha256: str, extension: str, path: Path, length: int) -> None:
        self.conn.execute(
            """
            INSERT INTO objects (sha256, extension, object_path, content_length, first_seen_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(sha256) DO NOTHING
            """,
            (sha256, extension, str(path), length, self.now()),
        )
        self.conn.commit()

    def object_exists(self, sha256: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM objects WHERE sha256 = ? LIMIT 1", (sha256,)
        ).fetchone()
        return row is not None

    def set_canonical(self, sha256: str, canonical_document_id: str) -> None:
        """Ghi canonical cho toàn bộ document dùng chung object này."""
        self.conn.execute(
            "UPDATE documents SET canonical_document_id = ? WHERE object_sha256 = ?",
            (canonical_document_id, sha256),
        )
        self.conn.commit()

    def documents_for_object(self, sha256: str) -> list[sqlite3.Row]:
        return list(
            self.conn.execute(
                "SELECT * FROM documents WHERE object_sha256 = ? ORDER BY discovered_at",
                (sha256,),
            )
        )

    # ---------------- documents ----------------

    def get_document(self, file_url: str) -> sqlite3.Row | None:
        return self.conn.execute(
            "SELECT * FROM documents WHERE file_url = ? LIMIT 1", (file_url,)
        ).fetchone()

    def upsert_discovery(self, document_id: str, record: dict[str, Any]) -> None:
        fields = {
            "document_id": document_id,
            "source_id": record["source_id"],
            "adapter": record.get("adapter"),
            "source_authority": record.get("source_authority"),
            "company": record.get("company"),
            "ticker": record.get("ticker"),
            "report_type": record.get("report_type"),
            "document_family": record.get("document_family"),
            "statement_scope": record.get("statement_scope"),
            "period_type": record.get("period_type"),
            "assurance_status": record.get("assurance_status"),
            "title": record.get("title"),
            "year": record.get("year"),
            "source_page_url": record.get("source_page_url"),
            "file_url": record["file_url"],
            "canonical_source_url": record.get("canonical_source_url"),
            "discovered_at": record.get("discovered_at", self.now()),
            "metadata_json": json.dumps(record.get("metadata", {}), ensure_ascii=False),
        }
        self.conn.execute(
            """
            INSERT INTO documents (
                document_id, source_id, adapter, source_authority, company, ticker,
                report_type, document_family, statement_scope, period_type,
                assurance_status, title, year, source_page_url, file_url,
                canonical_source_url, discovered_at, metadata_json
            ) VALUES (
                :document_id, :source_id, :adapter, :source_authority, :company, :ticker,
                :report_type, :document_family, :statement_scope, :period_type,
                :assurance_status, :title, :year, :source_page_url, :file_url,
                :canonical_source_url, :discovered_at, :metadata_json
            )
            ON CONFLICT(file_url) DO UPDATE SET
                report_type=COALESCE(excluded.report_type, documents.report_type),
                document_family=COALESCE(excluded.document_family, documents.document_family),
                statement_scope=COALESCE(excluded.statement_scope, documents.statement_scope),
                period_type=COALESCE(excluded.period_type, documents.period_type),
                assurance_status=COALESCE(excluded.assurance_status, documents.assurance_status),
                title=COALESCE(excluded.title, documents.title),
                year=COALESCE(excluded.year, documents.year),
                source_page_url=excluded.source_page_url,
                canonical_source_url=COALESCE(
                    excluded.canonical_source_url, documents.canonical_source_url),
                metadata_json=excluded.metadata_json
            """,
            fields,
        )
        self.conn.commit()

    def mark_status(
        self,
        file_url: str,
        status: CrawlStatus | str,
        *,
        error_code: str | None = None,
        error_message: str | None = None,
        next_retry_at: str | None = None,
    ) -> None:
        value = status.value if isinstance(status, CrawlStatus) else status
        self.conn.execute(
            """
            UPDATE documents
            SET crawl_status = ?,
                attempt_count = attempt_count + 1,
                last_attempt_at = ?,
                last_error_code = ?,
                last_error_message = ?,
                next_retry_at = ?
            WHERE file_url = ?
            """,
            (value, self.now(), error_code, error_message, next_retry_at, file_url),
        )
        self.conn.commit()

    def mark_downloaded(
        self,
        file_url: str,
        sha256: str,
        file_format: str,
        original_filename: str,
        *,
        duplicate: bool = False,
    ) -> None:
        status = CrawlStatus.DUPLICATE.value if duplicate else CrawlStatus.DOWNLOADED.value
        self.conn.execute(
            """
            UPDATE documents
            SET object_sha256 = ?,
                file_format = ?,
                original_filename = ?,
                downloaded_at = ?,
                crawl_status = ?,
                attempt_count = attempt_count + 1,
                last_attempt_at = ?,
                last_error_code = NULL,
                last_error_message = NULL,
                next_retry_at = NULL
            WHERE file_url = ?
            """,
            (sha256, file_format, original_filename, self.now(), status, self.now(), file_url),
        )
        self.conn.commit()

    def should_skip(self, file_url: str) -> bool:
        """Bỏ qua nếu đã tải xong và object vẫn còn trên đĩa."""
        row = self.get_document(file_url)
        if row is None:
            return False
        if row["crawl_status"] not in TERMINAL_STATUSES:
            return False
        if not row["object_sha256"]:
            return False
        obj = self.conn.execute(
            "SELECT object_path FROM objects WHERE sha256 = ?", (row["object_sha256"],)
        ).fetchone()
        return bool(obj and Path(obj["object_path"]).exists())

    def status_counts(self) -> dict[str, int]:
        rows = self.conn.execute(
            "SELECT crawl_status, COUNT(*) AS n FROM documents GROUP BY crawl_status"
        )
        return {row["crawl_status"]: row["n"] for row in rows}
