"""The edited text of one run document, its change log and its saved versions.

Stored next to the run (`<runs_dir>/<run_id>/studio/<doc_id>.json`), so a run
and the edits made on it travel together. The log is append-only: entries are
added, never rewritten, and restoring a version is itself a log entry.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

ACTORS = {"user", "ai-rule", "ai-llm", "system"}
ACTIONS = {"accept", "reject", "edit", "ignore", "save", "restore", "rework"}


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class StudioSession:
    def __init__(self, run_dir: Path, doc_id: str):
        self.path = Path(run_dir) / "studio" / f"{doc_id}.json"
        self.doc_id = doc_id

    def load(self, base_text: str, name: str = "") -> dict:
        if self.path.is_file():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {
            "doc_id": self.doc_id, "name": name, "base_sha256": sha(base_text),
            "text": base_text, "doc_class": "B", "versions": [], "log": [], "created_at": _now(),
        }

    def _write(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(self.path)

    def save(self, base_text: str, text: str, entries: list[dict], note: str = "", snapshot: bool = False,
             doc_class: str | None = None, name: str = "") -> dict:
        data = self.load(base_text, name)
        if data.get("base_sha256") != sha(base_text):
            raise ValueError("Văn bản gốc đã thay đổi kể từ phiên sửa này.")
        for entry in entries:
            actor = entry.get("actor", "user")
            action = entry.get("action", "edit")
            if actor not in ACTORS or action not in ACTIONS:
                raise ValueError(f"Mục nhật ký không hợp lệ: {actor}/{action}")
            clean = {k: entry.get(k) for k in (
                "actor", "action", "claim_id", "suggestion_id", "rule_code", "kind", "before", "after",
                "reason", "user", "client_ts", "source",
            ) if entry.get(k) is not None}
            clean["ts"] = _now()
            clean["seq"] = len(data["log"]) + 1
            data["log"].append(clean)
        data["text"] = text
        data["updated_at"] = _now()
        if doc_class in {"A", "B", "C"}:
            data["doc_class"] = doc_class
        if snapshot:
            version = len(data["versions"]) + 1
            data["versions"].append({"version": version, "saved_at": _now(), "note": note, "text": text,
                                     "sha256": sha(text), "log_seq": len(data["log"])})
            data["log"].append({"actor": "user", "action": "save", "reason": note or f"Phiên bản {version}",
                                "ts": _now(), "seq": len(data["log"]) + 1})
        self._write(data)
        return data

    def restore(self, base_text: str, version: int) -> dict:
        data = self.load(base_text)
        if version == 0:
            text = base_text
        else:
            match = next((v for v in data["versions"] if v["version"] == version), None)
            if match is None:
                raise KeyError(version)
            text = match["text"]
        data["text"] = text
        data["log"].append({"actor": "user", "action": "restore", "reason": f"Khôi phục phiên bản {version}"
                            if version else "Khôi phục văn bản gốc", "ts": _now(), "seq": len(data["log"]) + 1})
        self._write(data)
        return data
