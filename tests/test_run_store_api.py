"""Saved-run, export and legal-corpus endpoints backing the v2 UI.

The pipeline is the only writer; these endpoints read what it wrote. The test
runs one analysis into a temporary runs dir and then reopens it the way the
History page, the Export page and a reloaded claim link do.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from quantum_gw import api
from quantum_gw.storage.runs import RunStore

CLAIM = {"name": "claim.txt", "text": "Năm 2024 công ty giảm 12% phát thải CO2 so với 2023.", "role": "claim_source", "source_type": "internal"}
EVIDENCE = {"name": "ev.txt", "text": "Phát thải CO2 năm 2024 giảm 12% so với 2023 theo kiểm toán.", "role": "evidence", "source_type": "external"}


@pytest.fixture
def client(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("QUANTUM_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.setenv("QUANTUM_DOCUMENTS_DIR", str(tmp_path / "documents"))
    return TestClient(api.app)


def test_run_can_be_listed_reopened_labelled_and_exported(client):
    created = client.post("/v1/analyze/text", json={"documents": [CLAIM, EVIDENCE]}).json()
    run_id = created["result"]["run_id"]

    listed = client.get("/v1/runs").json()["runs"]
    assert [r["run_id"] for r in listed] == [run_id]
    assert listed[0]["documents"] == ["claim.txt", "ev.txt"]
    assert listed[0]["total_claims"] == 1
    assert listed[0]["label"] == ""

    reopened = client.get(f"/v1/runs/{run_id}").json()
    assert reopened["result"]["run_id"] == run_id
    assert reopened["result"]["claims"] == created["result"]["claims"]
    # Suggestions are derived, not stored, and must come back identically.
    assert reopened["suggestions"] == created["suggestions"]

    assert client.put(f"/v1/runs/{run_id}/label", json={"label": "  HPG   thử "}).json()["label"] == "HPG thử"
    assert client.get("/v1/runs").json()["runs"][0]["label"] == "HPG thử"

    for fmt, name in [("json", "result.json"), ("md", "evidence_pack.md"), ("manifest", "manifest.json"), ("audit", "audit.jsonl")]:
        response = client.get(f"/v1/runs/{run_id}/export", params={"format": fmt})
        assert response.status_code == 200, fmt
        assert name in response.headers["content-disposition"]
        assert response.content
    assert client.get(f"/v1/runs/{run_id}/export", params={"format": "pdf"}).status_code == 400


def test_unknown_or_malformed_run_ids_are_404(client):
    assert client.get("/v1/runs/0123456789abcdef").status_code == 404
    assert client.get("/v1/runs/..").status_code == 404
    assert client.put("/v1/runs/0123456789abcdef/label", json={"label": "x"}).status_code == 404
    assert client.get("/v1/runs/0123456789abcdef/export").status_code == 404


def test_run_store_rejects_path_traversal(tmp_path: Path):
    store = RunStore(tmp_path)
    with pytest.raises(KeyError):
        store.load("../etc")
    with pytest.raises(KeyError):
        store.artifact("0123456789abcdef", "../../secret")
    assert store.list() == []


def test_legal_corpus_lists_registered_instruments(client):
    body = client.get("/v1/legal/corpus").json()
    assert body["documents"], "registry should not be empty"
    doc = body["documents"][0]
    for key in ("document_number", "title", "effective_from", "status", "legal_issues", "usable", "text_is_ocr"):
        assert key in doc
    # Newest effective_from first, so the amendment chain reads top-down.
    dates = [d["effective_from"] or "" for d in body["documents"]]
    assert dates == sorted(dates, reverse=True)
