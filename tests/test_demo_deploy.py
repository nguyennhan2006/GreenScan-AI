"""What a deployed prototype needs (2026-11-09): a password in front of it, and a
document store that still finds its files after being copied to another machine."""

from __future__ import annotations

import asyncio
import base64
import json

from quantum_gw.api import _DemoAuth
from quantum_gw.storage.documents import DocumentStore


async def _ok(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"ok"})


def _call(app, path, auth=None):
    sent = []

    async def send(message):
        sent.append(message)

    async def receive():
        return {"type": "http.request"}

    headers = [(b"authorization", auth.encode("latin-1"))] if auth else []
    asyncio.run(app({"type": "http", "path": path, "headers": headers}, receive, send))
    return sent[0]["status"]


def test_demo_auth_is_off_unless_configured(monkeypatch):
    monkeypatch.delenv("QUANTUM_DEMO_USERS", raising=False)
    assert _call(_DemoAuth(_ok), "/v1/runs") == 200


def test_demo_auth_requires_a_listed_account_except_for_health(monkeypatch):
    monkeypatch.setenv("QUANTUM_DEMO_USERS", "giamkhao:mk1;doi:mk2")
    app = _DemoAuth(_ok)
    good = "Basic " + base64.b64encode(b"giamkhao:mk1").decode()
    bad = "Basic " + base64.b64encode(b"giamkhao:sai").decode()
    assert _call(app, "/v1/runs") == 401
    assert _call(app, "/v1/runs", bad) == 401
    assert _call(app, "/v1/runs", good) == 200
    assert _call(app, "/health") == 200


def test_a_copied_document_store_finds_its_blobs(tmp_path):
    original = DocumentStore(tmp_path / "laptop")
    record = original.put(b"%PDF-1.4 demo", "HPG.pdf")
    # Copy the store elsewhere: the index keeps the laptop's absolute path.
    moved_root = tmp_path / "server"
    (moved_root / "blobs" / record.sha256[:2]).mkdir(parents=True)
    (moved_root / "blobs" / record.sha256[:2] / record.path.name).write_bytes(record.path.read_bytes())
    row = json.loads((tmp_path / "laptop" / "index.jsonl").read_text(encoding="utf-8").splitlines()[0])
    row["path"] = "D:\\Sinh viên\\GreenScan\\.quantum\\documents\\blobs\\" + record.sha256[:2] + "\\" + record.path.name
    (moved_root / "index.jsonl").write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    moved = DocumentStore(moved_root)
    found = moved.get(record.doc_id)
    assert found is not None and found.path.read_bytes() == b"%PDF-1.4 demo"
    assert moved.find(record.sha256) is not None


def test_seeded_runs_install_once_and_never_overwrite(tmp_path, monkeypatch):
    from quantum_gw.storage.seed import install

    seed = tmp_path / "seed"
    (seed / "runs" / "r1").mkdir(parents=True)
    (seed / "runs" / "r1" / "result.json").write_text("{}", encoding="utf-8")
    (seed / "documents" / "blobs" / "ab").mkdir(parents=True)
    (seed / "documents" / "blobs" / "ab" / "abc.pdf").write_bytes(b"%PDF")
    row = {"doc_id": "d1", "sha256": "abc", "name": "x.pdf", "path": "blobs/ab/abc.pdf",
           "content_type": "application/pdf", "bytes": 4}
    (seed / "documents" / "index.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    monkeypatch.setenv("QUANTUM_SEED_DIR", str(seed))
    runs, docs = tmp_path / "store" / "runs", tmp_path / "store" / "documents"
    assert install(runs, docs) == {"runs": 1, "documents": 1}
    (runs / "r1" / "result.json").write_text('{"kept": true}', encoding="utf-8")
    assert install(runs, docs) == {"runs": 0, "documents": 0}
    assert "kept" in (runs / "r1" / "result.json").read_text(encoding="utf-8")
    assert DocumentStore(docs).get("d1") is not None
    monkeypatch.setenv("QUANTUM_SEED_DIR", "")
    assert install(runs, docs) == {"runs": 0, "documents": 0}
