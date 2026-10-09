"""What makes the product usable without a terminal (review 2026-10-05).

A background job with progress instead of one long request, a runtime report
that says which engine serves which task, a Vietnamese working paper rendered
from the saved run and the review trail, and every route reachable under
`/api` so the built UI and the API share one port.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from quantum_gw import api
from quantum_gw.jobs import JobRunner

CLAIM = {"name": "claim.txt", "text": "Năm 2024 Tập đoàn giảm 12% phát thải CO2 so với 2023.",
         "role": "claim_source", "source_type": "internal"}
EVIDENCE = {"name": "ev.txt", "text": "Phát thải CO2 năm 2024 giảm 12% so với 2023 theo kiểm toán.",
            "role": "evidence", "source_type": "external"}


@pytest.fixture
def client(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("QUANTUM_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.setenv("QUANTUM_DOCUMENTS_DIR", str(tmp_path / "documents"))
    monkeypatch.setenv("QUANTUM_REVIEWS_FILE", str(tmp_path / "reviews" / "decisions.jsonl"))
    return TestClient(api.app)


def _wait(client, job_id: str, timeout: float = 60.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        status = client.get(f"/v1/jobs/{job_id}").json()
        if status["state"] in {"done", "failed"}:
            return status
        time.sleep(0.1)
    raise AssertionError("job did not finish")


def test_a_background_job_reports_its_steps_and_ends_in_a_saved_run(client):
    started = client.post("/v1/jobs/analyze/text", json={
        "documents": [CLAIM, EVIDENCE], "label": "Thử nền", "company": "Hòa Phát",
    })
    assert started.status_code == 202
    status = _wait(client, started.json()["job_id"])
    assert status["state"] == "done", status
    assert status["step"] == "write_evidence_pack"
    assert status["step_index"] == status["total_steps"] == 10

    run = client.get(f"/v1/runs/{status['run_id']}").json()["result"]
    assert run["entity"] == ["Hòa Phát"]          # declared company reaches the result
    assert client.get("/v1/runs").json()["runs"][0]["label"] == "Thử nền"


def test_a_failed_job_says_why_instead_of_hanging():
    runner = JobRunner()

    def broken(progress):
        progress("validate_inputs", 1, 10, "")
        raise ValueError("At least one document is required")

    job = runner.submit(broken)
    for _ in range(100):
        status = runner.status(job.job_id)
        if status["state"] != "queued" and status["state"] != "running":
            break
        time.sleep(0.02)
    assert status["state"] == "failed"
    assert "document" in status["error"]


def test_every_route_is_also_served_under_api(client):
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/v1/runs").status_code == 200


def test_runtime_reports_what_a_run_would_do(client, monkeypatch):
    monkeypatch.setenv("QUANTUM_LLM_STANCE", "off")
    report = client.get("/v1/runtime").json()
    assert report["mode"] == "offline"
    assert report["sends_documents_out"] is False
    stance = next(t for t in report["tasks"] if t["task"] == "qualitative_stance")
    assert stance["engine"] == "rules" and stance["route"] == []
    numbers = next(t for t in report["tasks"] if t["task"] == "quantitative_verification")
    assert numbers["engine"] == "deterministic"


def test_the_working_paper_is_vietnamese_and_carries_the_review_trail(client):
    created = client.post("/v1/analyze/text", json={"documents": [CLAIM, EVIDENCE]}).json()
    run_id = created["run_id"]
    claim_id = created["result"]["claims"][0]["claim_id"]
    client.post("/v1/reviews", json={
        "run_id": run_id, "claim_id": claim_id, "reviewer": "Quỳnh", "decision": "ABSTAIN",
        "comment": "cần bảng kiểm kê gốc",
    })
    page = client.get(f"/v1/runs/{run_id}/workpaper")
    assert page.status_code == 200 and page.headers["content-type"].startswith("text/html")
    html = page.text
    for section in ("GIẤY LÀM VIỆC", "Phạm vi tài liệu", "Hàng đợi soát", "KHÔNG được kiểm", "Người soát xét"):
        assert section in html
    assert "Quỳnh" in html and "cần bảng kiểm kê gốc" in html
    assert client.get("/v1/runs/0123456789abcdef/workpaper").status_code == 404


def test_a_local_model_is_not_configured_unless_someone_names_one(monkeypatch):
    """The old default pointed at port 8000 -- GreenScan's own API."""
    from quantum_gw.settings import load_gateway_settings

    monkeypatch.delenv("LOCAL_LLM_BASE_URL", raising=False)
    assert load_gateway_settings().local_base_url == ""


def test_a_profile_fills_only_what_is_unset(monkeypatch):
    from quantum_gw.settings import apply_profile

    monkeypatch.delenv("EMBEDDING_PROVIDER", raising=False)
    monkeypatch.setenv("QUANTUM_LLM_STANCE", "off")
    assert apply_profile("cloud") == "cloud"
    import os

    assert os.environ["EMBEDDING_PROVIDER"] == "lite"     # filled in
    assert os.environ["QUANTUM_LLM_STANCE"] == "off"      # explicit value kept
    with pytest.raises(ValueError):
        apply_profile("turbo")
