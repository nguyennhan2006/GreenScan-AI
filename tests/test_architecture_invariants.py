"""The ten invariants, enforced rather than written down.

`docs/00-project/ARCHITECTURE_INVARIANTS.md` states what GreenScan may and may
not do. A statement in a document is a wish; a failing test is a boundary. Each
test below is named after the invariant it guards, and a change that violates
one turns this file red before it reaches a reviewer.

Two kinds of guard live here:

    behavioural   run the pipeline and assert the property holds on the output
    structural    read the source and assert the forbidden shape is absent

Structural guards are blunt on purpose. A grep for `company_is_greenwashing` is
crude, and it is also the thing that catches the day somebody adds it.
"""

from __future__ import annotations

import re
from pathlib import Path

from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.domain.enums import DocumentRole, SourceType, VerificationStatus
from quantum_gw.domain.models import AnalysisResult, DocumentInput

SRC = Path(__file__).resolve().parents[1] / "src" / "quantum_gw"


def _sources() -> dict[Path, str]:
    return {p: p.read_text(encoding="utf-8") for p in SRC.rglob("*.py")}


def _run(settings, claim: str, evidence: str, source_type: SourceType = SourceType.EXTERNAL):
    return OrchestratorAgent(settings).run([
        DocumentInput(name="claim.txt", text=claim, role=DocumentRole.CLAIM_SOURCE,
                      source_type=SourceType.INTERNAL),
        DocumentInput(name="evidence.txt", text=evidence, role=DocumentRole.EVIDENCE,
                      source_type=source_type),
    ])


# --- 1. verify claims, never judge a company ---------------------------------

def test_invariant_1_no_company_level_verdict_exists_anywhere():
    """A company-level greenwashing flag is the one output this product refuses."""
    forbidden = re.compile(
        r"company_(?:is_)?greenwash|is_greenwashing|greenwashing_score|company_verdict",
        re.IGNORECASE,
    )
    offenders = [str(path) for path, text in _sources().items() if forbidden.search(text)]
    assert not offenders, f"a company-level verdict appeared in {offenders}"
    assert not any(
        "company" in name and "verdict" in name for name in AnalysisResult.model_fields
    )


# --- 2. atomic claims that can be traced back --------------------------------

def test_invariant_2_every_extracted_object_can_be_traced_to_its_source(settings):
    result = _run(
        settings,
        "Năm 2024 phát thải khí nhà kính giảm 20% so với năm 2020; tỷ lệ tái chế đạt 99%.",
        "Kiểm kê: phát thải khí nhà kính năm 2020 là 100.000 tấn CO2e, năm 2024 là 80.000 tấn CO2e.",
    )
    assert len(result.claims) >= 2, "a sentence with two measured assertions must split"
    for claim in result.claims:
        assert claim.source_chunk_id and claim.source_doc_id and claim.source_name
        assert claim.text.strip(), "a claim must keep the words it was made of"
    for figure in result.disclosed_figures:
        assert figure.source_chunk_id and figure.source_doc_id


# --- 3. retrieval finds candidates; it does not decide truth ------------------

def test_invariant_3_similarity_alone_never_produces_a_decisive_verdict(settings):
    """A passage on the same topic with no figure and no cue cannot settle anything."""
    result = _run(
        settings,
        "Tập đoàn đã giảm phát thải khí nhà kính tại các nhà máy thép trong năm 2024.",
        "Các nhà máy thép của Tập đoàn vận hành trong năm 2024 với nhiều hoạt động sản xuất "
        "và bảo trì thiết bị theo kế hoạch.",
        SourceType.FINANCIAL,
    )
    assert _status(result) not in {VerificationStatus.SUPPORTED, VerificationStatus.CONTRADICTED}
    for verification in result.verifications:
        for item in verification.evidence:
            if item.relation in {"SUPPORTS", "CONTRADICTS"}:
                assert item.relation_method in {"numeric", "qualitative_cue", "llm"}, (
                    "only arithmetic, a cue or an escalated model may take a side"
                )


# --- 4. compare only what is comparable --------------------------------------

def test_invariant_4_a_dimension_mismatch_can_never_be_a_contradiction(settings):
    """Same unit is not the same measurement: scope, boundary and basis all gate it."""
    cases = [
        ("Phát thải khí nhà kính Scope 1 và 2 năm 2025 là 80.000 tấn CO2e.",
         "Kiểm kê: phát thải khí nhà kính Scope 1 năm 2025 là 100.000 tấn CO2e."),
        ("Phát thải khí nhà kính của toàn Tập đoàn năm 2025 là 100.000 tấn CO2e.",
         "Kiểm kê: phát thải tại nhà máy Dung Quất năm 2025 là 80.000 tấn CO2e."),
        ("Phát thải khí nhà kính của Tập đoàn năm 2025 là 100.000 tấn CO2e.",
         "Cường độ phát thải năm 2025 là 0,8 tấn CO2e trên mỗi tấn thép thô."),
    ]
    for claim, evidence in cases:
        result = _run(settings, claim, evidence)
        assert _status(result) != VerificationStatus.CONTRADICTED, claim


# --- 5. the arithmetic belongs to code ---------------------------------------

def test_invariant_5_numeric_conclusions_carry_the_policy_and_the_calculation(settings):
    result = _run(
        settings,
        "Phát thải khí nhà kính Scope 1 và 2 của Tập đoàn năm 2025 giảm 20% so với năm 2020.",
        "Kiểm kê độc lập: phát thải khí nhà kính Scope 1 và 2 của Tập đoàn năm 2020 là "
        "100.000 tấn CO2e, năm 2025 là 80.000 tấn CO2e.",
    )
    computed = result.verifications[0].computed_values
    assert computed["policy_id"] and computed["eligibility_policy"]
    assert computed["calculation_method"] == "deterministic-relative-error"
    assert "Tính lại từ số liệu" in result.verifications[0].evidence[0].relation_reason


def test_invariant_5_a_model_may_not_overrule_the_comparator():
    """The numeric branch returns before any cue or model is consulted."""
    stance = (SRC / "agents" / "verifier.py").read_text(encoding="utf-8")
    body = stance[stance.index("def _stance("):stance.index("def _numeric_relation(")]
    numeric_at = body.index("numeric = self._numeric_relation")
    cue_at = body.index("qualitative_stance(")
    judge_at = body.index("self.llm_judge")
    assert numeric_at < cue_at < judge_at, (
        "arithmetic must be consulted first and must return before the model does"
    )
    assert "return numeric" in body[numeric_at:cue_at]


# --- 6. a target is not an achievement; silence is not a denial ---------------

def test_invariant_6_absence_and_contradiction_stay_different(settings):
    """They are different findings, and they must not collapse into one another."""
    absent = _run(
        settings,
        "Tập đoàn đã đạt chứng nhận trung hòa carbon cho toàn bộ nhà máy trong năm 2024.",
        "Báo cáo tài chính năm 2024 trình bày doanh thu và chi phí hoạt động.",
        SourceType.FINANCIAL,
    )
    assert _status(absent) != VerificationStatus.CONTRADICTED

    target = _run(
        settings,
        "Tập đoàn đã giảm 30% phát thải khí nhà kính Scope 1 và 2 so với năm 2020.",
        "Tập đoàn đặt mục tiêu giảm 30% phát thải khí nhà kính Scope 1 và 2 vào năm 2030 "
        "so với năm 2020.",
    )
    assert _status(target) != VerificationStatus.SUPPORTED


# --- 7. relevant is not applicable -------------------------------------------

def test_invariant_7_the_legal_layer_separates_relevance_from_applicability(settings):
    result = _run(
        settings,
        "Nhà máy thép của Tập đoàn đã giảm phát thải khí nhà kính trong năm 2025.",
        "Kiểm kê ghi nhận phát thải khí nhà kính tại nhà máy thép năm 2025.",
    )
    for check in result.legal_checks:
        assert "rules_relevant" in check and "rules_applied" in check
        assert set(check["rules_applied"]) <= set(check["rules_relevant"])
        for rejected in check.get("not_applicable_rules", []):
            assert rejected["reason"], "a rejected rule must say why it does not apply"


# --- 8. abstention is a valid answer -----------------------------------------

def test_invariant_8_the_pipeline_is_allowed_to_decline(settings):
    result = _run(
        settings,
        "Công ty cam kết đạt Net Zero vào năm 2050.",
        "Doanh thu năm 2024 tăng 15%. Chi phí năng lượng tăng 20% do giá điện.",
        SourceType.FINANCIAL,
    )
    assert _status(result) in {
        VerificationStatus.INSUFFICIENT_EVIDENCE,
        VerificationStatus.UNSUPPORTED,
    }
    assert result.summary.release_status in {"PENDING_HUMAN_REVIEW", "RELEASABLE", "BLOCKED"}


# --- 9. verdict, risk and priority are three different statements -------------

def test_invariant_9_verdict_risk_and_priority_are_not_interchangeable(settings):
    result = _run(
        settings,
        "Tỷ lệ tái chế chất thải rắn đạt 100% trong năm 2024.",
        "Kiểm toán môi trường: tỷ lệ tái chế chất thải rắn năm 2024 đạt 60%.",
    )
    verdict = result.verifications[0]
    risk = result.risks[0]
    priority = next(p for p in result.priorities if p["item_id"] == verdict.claim.claim_id)

    assert verdict.status == VerificationStatus.CONTRADICTED
    # a contradiction always reaches a human, whatever the band arithmetic says
    assert risk.requires_human_review
    # risk is a rubric score, not a probability, and priority is neither
    assert 0 <= risk.risk_score <= 100
    assert priority["priority_score"] <= priority["max_available"]
    # queue membership says "look at this", never "this is false"
    queued = [p for p in result.priorities if p["in_queue"]]
    assert all("verdict" not in p for p in queued)


# --- 10. reproducible, and inspectable by a person ---------------------------

def test_invariant_10_a_run_records_what_it_would_take_to_repeat_it(settings):
    result = _run(settings, "Công ty đã giảm phát thải năm 2024.", "Phát thải năm 2024 giảm.")
    manifest = result.manifest
    for field in ("config_hash", "input_hashes", "pipeline_version", "corpus_version",
                  "rule_pack_version", "plan"):
        assert getattr(manifest, field), f"manifest is missing {field}"


def test_invariant_10_an_uncomputed_signal_is_never_reported_as_a_result(settings):
    """Zero means "measured and found nothing"; not_computed means nobody looked."""
    result = _run(settings, "Công ty đã giảm phát thải năm 2024.", "Phát thải năm 2024 giảm.")
    for priority in result.priorities:
        for component in priority["components"]:
            if component["status"] == "not_computed":
                assert component["score"] == 0
                assert component["name"] in priority["not_computed"]
                assert priority["max_available"] < 100
                assert "chưa tính" in component["reason"]


def test_invariant_10_every_decisive_evidence_item_carries_a_citation(settings):
    result = _run(
        settings,
        "Tỷ lệ tái chế chất thải rắn đạt 100% trong năm 2024.",
        "Kiểm toán môi trường: tỷ lệ tái chế chất thải rắn năm 2024 đạt 60%.",
    )
    for verification in result.verifications:
        for item in verification.evidence:
            if item.relation in {"SUPPORTS", "CONTRADICTS"}:
                assert item.citation and item.source_name


# --- the standing prohibitions, as source guards -----------------------------

def test_prohibited_shortcuts_are_absent_from_the_source():
    """The things this project decided not to do, checked rather than remembered."""
    sources = _sources()
    banned = {
        r"GraphRAG": "GraphRAG was ruled out (D-2026-09-18-02)",
        r"\bfine_?tune\b": "no model is fine-tuned before the semi-final (D-2026-09-18-02)",
    }
    for pattern, why in banned.items():
        regex = re.compile(pattern, re.IGNORECASE)
        offenders = [
            str(path) for path, text in sources.items()
            if any(regex.search(line) and not line.lstrip().startswith("#")
                   for line in text.splitlines())
        ]
        assert not offenders, f"{why}; found in {offenders}"


def _status(result) -> VerificationStatus:
    assert result.verifications, "no claim was extracted"
    return result.verifications[0].status
