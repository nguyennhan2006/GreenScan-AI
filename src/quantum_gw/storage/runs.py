"""Read-only access to completed runs.

Every run already writes `manifest.json`, `result.json`, `audit.jsonl` and
`evidence_pack.md` under `runs_dir/<run_id>/`. Nothing else is stored, so a
"run store" is just a listing over that directory: the pipeline stays the only
writer and a run that is on disk is, by construction, a run that completed
`write_evidence_pack`.

This is what lets the UI reopen a saved analysis — the demo insurance in
EXECUTION_PLAN S3.2 — without a database the pipeline would have to keep in
sync with the files it writes anyway.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from quantum_gw.domain.models import AnalysisResult

# Human-readable labels for runs are the UI's concern; the pipeline only knows
# run ids. They live next to the run so they survive a page reload and travel
# with the evidence pack.
LABEL_FILE = "label.json"


@dataclass(frozen=True)
class RunSummary:
    run_id: str
    created_at: str
    pipeline_version: str
    total_documents: int
    total_chunks: int
    total_claims: int
    status_counts: dict[str, int]
    severity_counts: dict[str, int]
    release_status: str
    label: str
    documents: list[str]


class RunStore:
    def __init__(self, runs_dir: str | Path):
        self.root = Path(runs_dir)

    def _dir(self, run_id: str) -> Path:
        # A run id is 16 hex characters; anything else is a path traversal attempt.
        if not run_id or not all(c in "0123456789abcdef" for c in run_id):
            raise KeyError(run_id)
        return self.root / run_id

    def exists(self, run_id: str) -> bool:
        try:
            return (self._dir(run_id) / "result.json").exists()
        except KeyError:
            return False

    def load(self, run_id: str) -> AnalysisResult:
        path = self._dir(run_id) / "result.json"
        if not path.exists():
            raise KeyError(run_id)
        return AnalysisResult.model_validate_json(path.read_text(encoding="utf-8"))

    def artifact(self, run_id: str, name: str) -> Path:
        if name not in {"result.json", "evidence_pack.md", "manifest.json", "audit.jsonl"}:
            raise KeyError(name)
        path = self._dir(run_id) / name
        if not path.exists():
            raise KeyError(name)
        return path

    def label_of(self, run_id: str) -> str:
        path = self._dir(run_id) / LABEL_FILE
        if not path.exists():
            return ""
        try:
            return str(json.loads(path.read_text(encoding="utf-8")).get("label", ""))
        except (OSError, ValueError):
            return ""

    def set_label(self, run_id: str, label: str) -> str:
        directory = self._dir(run_id)
        if not (directory / "result.json").exists():
            raise KeyError(run_id)
        label = " ".join(label.split())[:120]
        (directory / LABEL_FILE).write_text(
            json.dumps({"label": label}, ensure_ascii=False), encoding="utf-8"
        )
        return label

    def summary(self, run_id: str) -> RunSummary:
        result = self.load(run_id)
        manifest = result.manifest
        documents = [key.split(":", 1)[1] if ":" in key else key for key in manifest.input_hashes]
        return RunSummary(
            run_id=result.run_id,
            created_at=manifest.created_at.isoformat(),
            pipeline_version=manifest.pipeline_version,
            total_documents=result.summary.total_documents,
            total_chunks=result.summary.total_chunks,
            total_claims=result.summary.total_claims,
            status_counts=result.summary.status_counts,
            severity_counts=result.summary.severity_counts,
            release_status=result.summary.release_status,
            label=self.label_of(run_id),
            documents=documents,
        )

    def list(self, limit: int = 50) -> list[dict]:
        """Newest first. A run whose result.json cannot be read is skipped, not fatal."""
        if not self.root.exists():
            return []
        candidates = [p for p in self.root.iterdir() if (p / "result.json").exists()]
        candidates.sort(key=lambda p: (p / "result.json").stat().st_mtime, reverse=True)
        out: list[dict] = []
        for path in candidates[:limit]:
            try:
                out.append(asdict(self.summary(path.name)))
            except (KeyError, ValueError, OSError):
                continue
        return out
