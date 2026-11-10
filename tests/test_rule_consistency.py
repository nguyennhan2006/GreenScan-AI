"""Consistency of the checking logic across rule packs.

A user's rules are not always the standard ones, so the same claim may rightly
get different findings under two organisations' packs. What must never vary is
the logic: the same claim under the same pack version gives the same findings,
every time and in any order; and a company-specific exception lives in that
company's pack and moves only the rule it names. These are the properties a
reviewer's "the rule does not fit here" feedback (storage/reviews.py,
RULE_NOT_APPLICABLE) relies on when it becomes a new pack version.
"""

from __future__ import annotations

import copy
from datetime import date
from pathlib import Path

import yaml

from quantum_gw.legal.org_pack import NOT_APPLICABLE, VIOLATION, ClaimFacts, evaluate_claim, load_org_pack

FIXTURE = Path(__file__).parent / "fixtures" / "org_packs" / "fixture_bank"
DAY = date(2026, 11, 10)

CLAIMS = [
    ClaimFacts(claim_id="c1", text="Năm 2024 tập đoàn giảm 5% phát thải.", claim_type="emissions_reduction",
               sector="steel", attributes={"period": "2024"}),
    ClaimFacts(claim_id="c2", text="Năm 2024 giảm 5% phát thải so với năm 2020.", claim_type="emissions_reduction",
               sector="steel", attributes={"period": "2024", "baseline": "2020"}),
    ClaimFacts(claim_id="c3", text="Sản phẩm thân thiện với môi trường, hướng tới net zero.",
               claim_type="other", sector=None, attributes={}),
    ClaimFacts(claim_id="c4", text="Hòa Phát sản xuất thép xanh tại Dung Quất.", claim_type="other",
               sector="steel", attributes={}),
]
EVIDENCE = [{"chunk_id": "i1", "text": "Báo cáo của công ty.", "source_type": "internal"}]


def _pack_data() -> dict:
    return yaml.safe_load((FIXTURE / "pack.yaml").read_text(encoding="utf-8"))


def _write(root: Path, data: dict) -> Path:
    folder = root / data["org_id"]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "pack.yaml").write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    for doc in data.get("documents", []):
        (folder / doc["path"]).write_text("§1 Chính sách giả lập.\n", encoding="utf-8")
    return folder


def _outcomes(packs, claim) -> dict:
    return {(f.org_id, f.rule_id): f.outcome for f in evaluate_claim(packs, claim, EVIDENCE, DAY)}


def test_same_claim_same_pack_same_findings_every_time():
    pack = load_org_pack(FIXTURE)
    reloaded = load_org_pack(FIXTURE)
    for claim in CLAIMS:
        first = [f.to_json() for f in evaluate_claim([pack], claim, EVIDENCE, DAY)]
        assert first == [f.to_json() for f in evaluate_claim([pack], claim, EVIDENCE, DAY)]
        assert first == [f.to_json() for f in evaluate_claim([reloaded], claim, EVIDENCE, DAY)]


def test_pack_order_does_not_change_any_finding(tmp_path):
    data_b = _pack_data()
    data_b["org_id"] = "org_b"
    pack_a, pack_b = load_org_pack(FIXTURE), load_org_pack(_write(tmp_path, data_b))
    for claim in CLAIMS:
        assert _outcomes([pack_a, pack_b], claim) == _outcomes([pack_b, pack_a], claim)


def test_a_company_exception_moves_only_the_rule_it_names(tmp_path):
    """Org B does not require a baseline year (its version of FB_001 is dropped).
    The claim without a baseline violates FB_001 under A, and FB_001 does not
    exist under B; every other rule gives the same outcome under both."""
    data_b = copy.deepcopy(_pack_data())
    data_b["org_id"] = "org_b"
    data_b["pack_version"] = "0.2.0"
    data_b["rules"] = [r for r in data_b["rules"] if r["rule_id"] != "FB_001"]
    pack_a, pack_b = load_org_pack(FIXTURE), load_org_pack(_write(tmp_path, data_b))

    for claim in CLAIMS:
        under_a = {rule: out for (_, rule), out in _outcomes([pack_a], claim).items()}
        under_b = {rule: out for (_, rule), out in _outcomes([pack_b], claim).items()}
        assert "FB_001" not in under_b
        under_a.pop("FB_001")
        assert under_a == under_b, claim.claim_id

    without_baseline = {rule: out for (_, rule), out in _outcomes([pack_a], CLAIMS[0]).items()}
    assert without_baseline["FB_001"] == VIOLATION


def test_every_finding_names_the_pack_version_and_rule_it_came_from(tmp_path):
    data_b = _pack_data()
    data_b["org_id"] = "org_b"
    data_b["pack_version"] = "9.9.9"
    pack_b = load_org_pack(_write(tmp_path, data_b))
    findings = evaluate_claim([pack_b], CLAIMS[0], EVIDENCE, DAY)
    assert findings and all(f.pack_version == "9.9.9" and f.rule_id and f.org_id == "org_b" for f in findings)
    applied = [f for f in findings if f.outcome != NOT_APPLICABLE]
    assert applied and all(f.source_clauses for f in applied)
