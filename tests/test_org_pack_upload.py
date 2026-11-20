"""org-pack-v1: uploaded packs are drafts, approved by someone else, chosen per run; drafts from policy text.

Docs: docs/03-architecture/ORG_PACK.md (section "Gửi bộ quy tắc qua giao diện").
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from quantum_gw import api
from quantum_gw.legal import org_registry
from quantum_gw.legal.org_draft import clauses, draft, heuristic_rules, write
from quantum_gw.legal.org_pack import load_org_pack

FIXTURE = Path("tests/fixtures/org_packs/fixture_bank")
POLICY = Path("configs/org_packs/demo_ngan_hang_xanh/internal_policy.md")


@pytest.fixture(autouse=True)
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("QUANTUM_ORG_PACK_STORE", str(tmp_path / "org_packs"))
    return tmp_path / "org_packs"


def _files(folder: Path = FIXTURE) -> list[tuple[str, bytes]]:
    return [(f.name, f.read_bytes()) for f in folder.iterdir() if f.is_file()]


def _zip(entries: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def test_upload_is_always_a_draft():
    result = org_registry.ingest(_files(), "Lan")
    assert result["status"] == "draft" and result["self_approval_removed"] is True
    pack = load_org_pack(result["path"])
    assert pack.draft and pack.org_id == "fixture_bank"
    assert org_registry.list_packs()[0]["status"] == "draft"
    assert org_registry.ingest(_files(), "Lan")["status"] == "duplicate"


def test_zip_of_the_folder_is_accepted_and_bad_paths_are_not():
    entries = {f"fixture_bank/{name}": content for name, content in _files()}
    assert org_registry.ingest([("pack.zip", _zip(entries))], "Lan")["status"] == "draft"
    bad = org_registry.ingest([("pack.zip", _zip({"../pack.yaml": b"x"}))], "Lan")
    assert bad["status"] == "rejected" and "không an toàn" in bad["errors"][0]
    exe = org_registry.ingest([("pack.zip", _zip({"pack.yaml": b"a: 1", "run.exe": b"MZ"}))], "Lan")
    assert exe["status"] == "rejected" and "run.exe" in exe["errors"][0]
    assert org_registry.ingest(_files(), "")["status"] == "rejected"


def test_a_broken_pack_is_refused_with_reasons():
    files = dict(_files())
    data = yaml.safe_load(files["pack.yaml"])
    data["rules"][0]["on_fail"] = "change_verdict"
    files["pack.yaml"] = yaml.safe_dump(data, allow_unicode=True).encode("utf-8")
    result = org_registry.ingest(list(files.items()), "Lan")
    assert result["status"] == "rejected" and any("on_fail" in e for e in result["errors"])
    assert org_registry.list_packs() == []


def test_four_eyes_approval_then_choice_per_run():
    up = org_registry.ingest(_files(), "Lan")
    with pytest.raises(ValueError):
        org_registry.resolve(["fixture_bank"])            # nothing approved yet
    assert org_registry.resolve([f"fixture_bank@{up['version']}"]) == [up["path"]]   # a draft can be named
    with pytest.raises(ValueError):
        org_registry.approve("fixture_bank", up["version"], "lan")                   # same person
    approved = org_registry.approve("fixture_bank", up["version"], "Minh", "đã đọc")
    assert approved["status"] == "approved" and not load_org_pack(up["path"]).draft
    assert org_registry.resolve(["fixture_bank"]) == [up["path"]]
    org_registry.retire("fixture_bank", up["version"], "Minh")
    with pytest.raises(ValueError):
        org_registry.resolve(["fixture_bank"])


def test_draft_from_the_demo_policy_cites_clauses_and_validates(tmp_path):
    text = POLICY.read_text(encoding="utf-8")
    assert ("§2.1", ) == tuple(c for c, _ in clauses(text) if c == "§2.1")
    result = draft(text, "ngan_hang_demo", "Ngân hàng demo")
    assert result["method"] == "heuristic" and result["errors"] == []
    rules = result["pack"]["rules"]
    assert result["pack"]["approved_by"] == ""
    checks = {r["conditions"][0]["check"] for r in rules}
    assert {"claim_attribute_present", "claim_terms_absent", "evidence_independent"} <= checks
    baseline = next(r for r in rules if r["conditions"][0].get("attribute") == "baseline")
    assert baseline["source_clauses"] == ["POL-01:§2.1"] and baseline["when"][0]["check"] == "claim_terms_present"
    absent = next(r for r in rules if r["conditions"][0]["check"] == "claim_terms_absent")
    assert "net zero" in absent["conditions"][0]["any_of_terms"]
    folder = write(tmp_path / "ngan_hang_demo", result["pack"], text)
    assert load_org_pack(folder).draft


def test_unnumbered_text_becomes_paragraph_clauses():
    rules = heuristic_rules("Mọi tuyên bố phải nêu phạm vi áp dụng.\n\nĐoạn này chỉ giới thiệu.")
    assert [r["source_clauses"] for r in rules] == [["POL-01:P1"]]
    assert rules[0]["conditions"][0]["attribute"] == "scope"


def test_llm_draft_falls_back_offline():
    class Broken:
        def generate(self, *args, **kwargs):
            raise RuntimeError("no provider")

    result = draft("§1 Tuyên bố phải nêu năm gốc.", "x_org", "X", use_llm=True, gateway=Broken())
    assert result["method"] == "heuristic" and any("mô hình" in n for n in result["notes"])


# ---------------------------------------------------------------- API


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("QUANTUM_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.setenv("QUANTUM_DOCUMENTS_DIR", str(tmp_path / "documents"))
    monkeypatch.setenv("QUANTUM_REVIEWS_FILE", str(tmp_path / "reviews" / "decisions.jsonl"))
    return TestClient(api.app)


def test_api_upload_approve_preview_and_analyze(client):
    files = [("files", (name, content)) for name, content in _files()]
    up = client.post("/v1/org-packs/upload", files=files, data={"uploaded_by": "Lan"})
    assert up.status_code == 200 and up.json()["status"] == "draft"
    version = up.json()["version"]
    assert client.post(f"/v1/org-packs/fixture_bank/{version}/approve", json={"by": "Lan"}).status_code == 400
    assert client.post(f"/v1/org-packs/fixture_bank/{version}/approve", json={"by": "Minh"}).json()["status"] == "approved"
    listed = client.get("/v1/org-packs").json()
    assert listed["uploaded"][0]["status"] == "approved"
    preview = client.post("/v1/org-packs/preview", json={"pack": f"fixture_bank@{version}",
                                                         "text": "Công ty cam kết đạt trung hòa carbon vào năm 2050."})
    assert preview.status_code == 200 and preview.json()["findings"]
    docs = [{"name": "claim.txt", "text": "Công ty cam kết đạt trung hòa carbon vào năm 2050.",
             "role": "claim_source", "source_type": "internal"}]
    run = client.post("/v1/analyze/text", json={"documents": docs, "org_packs": ["fixture_bank"]}).json()
    assert run["result"]["manifest"]["org_packs"][0]["org_id"] == "fixture_bank"
    assert run["result"]["org_findings"] is not None
    bad = client.post("/v1/analyze/text", json={"documents": docs, "org_packs": ["khong_co"]})
    assert bad.status_code == 400


def test_api_draft_from_policy_is_stored_as_draft(client):
    response = client.post("/v1/org-packs/draft", data={
        "org_id": "ngan_hang_demo", "org_name": "Ngân hàng demo", "uploaded_by": "Lan",
        "policy_text": POLICY.read_text(encoding="utf-8")})
    body = response.json()
    assert response.status_code == 200 and body["stored"]["status"] == "draft" and body["pack"]["rules"]


def test_api_review_accepts_a_pointer_and_feedback_summary(client):
    review = client.post("/v1/reviews", json={
        "run_id": "r1", "claim_id": "k1", "reviewer": "Hà", "decision": "OVERRIDE",
        "reviewer_status": "CONTRADICTED", "override_reason": "MODEL_MISREAD", "ai_status": "PARTIALLY_SUPPORTED",
        "evidence": [{"chunk_id": "c1", "text": "180 tỷ đồng chưa được phân bổ.", "source_name": "BCTC"}],
        "claim": {"text": "Vốn trái phiếu xanh được sử dụng hoàn toàn."},
        "decisive_chunk_ids": ["c1"], "reviewer_role": "auditor"})
    assert review.status_code == 200 and review.json()["error_stage"] == "reading"
    summary = client.get("/v1/feedback/summary").json()
    assert summary["stats"]["pointer_labels"] == 1 and summary["clean_labels"] == 1
    found = client.get("/v1/feedback/precedents", params={"text": "Vốn trái phiếu xanh được dùng hoàn toàn."}).json()
    assert found["precedents"][0]["label"] == "CONTRADICTED"
    assert "chưa được phân bổ" in client.get("/v1/feedback/proposals").json()["markdown"]
    qa = client.post("/v1/feedback/qa", json={"run_id": "r1", "claim_id": "k1", "reviewer": "Lan",
                                              "status": "CONTRADICTED", "kind": "second_review"})
    assert qa.status_code == 200
