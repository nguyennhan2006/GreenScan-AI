"""Ghi manifest JSONL cho mỗi lần chạy crawl.

README cũ mô tả `data/manifests/crawl-YYYYMMDD-HHMMSS.jsonl` nhưng code chưa
bao giờ tạo file này. Đây là bản hiện thực.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import Any, TextIO


class ManifestWriter:
    def __init__(self, root: Path, run_id: str | None = None):
        self.run_id = run_id or datetime.now(UTC).strftime("crawl-%Y%m%d-%H%M%S")
        self.dir = root / "manifests"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / f"{self.run_id}.jsonl"
        self._handle: TextIO | None = None
        self.counts: dict[str, int] = {}

    def __enter__(self) -> ManifestWriter:
        self._handle = self.path.open("a", encoding="utf-8")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def write(self, record: dict[str, Any]) -> None:
        if self._handle is None:
            raise RuntimeError("ManifestWriter chưa được mở (dùng làm context manager)")
        payload = dict(record)
        payload.setdefault("run_id", self.run_id)
        payload.setdefault("logged_at", datetime.now(UTC).isoformat())
        self._handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self._handle.flush()
        status = str(payload.get("crawl_status", "unknown"))
        self.counts[status] = self.counts.get(status, 0) + 1

    def close(self) -> None:
        if self._handle is not None:
            self._handle.close()
            self._handle = None

    def summary(self) -> dict[str, int]:
        return dict(sorted(self.counts.items()))
