"""T1 label = attributes a model reads + conventions a policy sets.

The default policy must reproduce codebook v1.1 on its own examples, so labels
composed from attributes stay comparable with every label made so far. A
different policy must move only the sentences its convention covers.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from quantum_gw.domain.claim_attributes import (
    NOT_CLAIM,
    QUALITATIVE,
    QUANTIFIED,
    VAGUE,
    ClaimAttributes,
    ClaimPolicy,
    InvalidAttributes,
    compose_label,
)

A = ClaimAttributes

# (codebook example, attributes a careful reader gives it, expected label, expected why_not)
CODEBOOK_CASES = [
    ("Phát thải năm 2024 là 23.474.480 tCO2e, giảm 4% so với 2023.",
     A(quantity="measure"), QUANTIFIED, None),
    ("Lắp hệ thống xử lý nước thải tại nhà máy Dung Quất.", A(), QUALITATIVE, None),
    ("Luôn chú trọng bảo vệ môi trường, hướng tới phát triển bền vững.", A(concrete=False), VAGUE, None),
    ("Q6: Trung hòa carbon vào năm 2050.", A(target=True, target_year=True), QUALITATIVE, None),
    ("Q6: Thép phế đạt 30% vào năm 2030.", A(target=True, target_year=True, quantity="measure"), QUANTIFIED, None),
    ("Q7: Đạt chứng nhận ISO 14001:2015.", A(), QUALITATIVE, None),
    ("Q10: 26 nhà máy đạt ISO 14001.", A(quantity="count"), QUANTIFIED, None),
    ("Q11: Lọt Top 100 doanh nghiệp bền vững.", A(kind="award"), QUALITATIVE, None),
    ("Q12: Báo cáo được lập theo GRI và có đảm bảo độc lập.", A(kind="esg_process"), QUALITATIVE, None),
    ("Q12: Báo cáo này bao gồm giai đoạn 01/01–31/12/2024.", A(kind="report_meta"), NOT_CLAIM, "other"),
    ("Q13: Bảng 3 — Tiêu thụ năng lượng theo năm", A(form="table_or_heading", quantity="measure"), NOT_CLAIM, "table_heading"),
    ("Q4: …và SẢN XUẤT 37 HÒA", A(form="broken"), NOT_CLAIM, "broken"),
    ("Q1: VSA kêu gọi các doanh nghiệp thép giảm phát thải.", A(speaker="other_org"), NOT_CLAIM, "other_org"),
    ("Q2: Lò điện hồ quang phát thải thấp hơn lò cao.", A(general_knowledge=True), NOT_CLAIM, "general_knowledge"),
    ("Q14: Phát triển bền vững là nền tảng kinh doanh trường tồn.", A(environmental=False), NOT_CLAIM, "non_env"),
    ("Q15: Công trình khách hàng đạt chứng chỉ LEED Gold.", A(speaker="client_project"), NOT_CLAIM, "other_org"),
    ("Q17: Công ty tuân thủ đầy đủ quy định về môi trường.", A(kind="compliance"), QUALITATIVE, None),
    ("Q17: Nhà máy dùng nước ngầm và than cám cho lò hơi.", A(), QUALITATIVE, None),
]


@pytest.mark.parametrize(("sentence", "attrs", "label", "why_not"), CODEBOOK_CASES,
                         ids=[c[0][:40] for c in CODEBOOK_CASES])
def test_default_policy_reproduces_codebook_v1_1(sentence, attrs, label, why_not):
    composed = compose_label(attrs)
    assert (composed.label, composed.why_not) == (label, why_not), sentence
    assert composed.policy_id == "codebook_v1_1"


def test_the_policy_file_is_the_default_policy():
    assert ClaimPolicy.load(Path("configs/claim_policy/codebook_v1_1.yaml")) == ClaimPolicy()


def test_not_claim_reasons_follow_codebook_order():
    """Q8: a table cell spoken by another organisation is a table cell first."""
    attrs = A(form="table_or_heading", speaker="other_org", general_knowledge=True, environmental=False)
    assert compose_label(attrs).why_not == "table_heading"
    assert compose_label(A(speaker="other_org", environmental=False)).why_not == "other_org"


@pytest.mark.parametrize(("change", "moved"), [
    ({"year_only_target": VAGUE}, {"Q6: Trung hòa carbon vào năm 2050."}),
    ({"count_is_quantity": False}, {"Q10: 26 nhà máy đạt ISO 14001."}),
    ({"esg_process_is_claim": False}, {"Q12: Báo cáo được lập theo GRI và có đảm bảo độc lập."}),
    ({"award_is_claim": False}, {"Q11: Lọt Top 100 doanh nghiệp bền vững."}),
    ({"compliance_is_claim": False}, {"Q17: Công ty tuân thủ đầy đủ quy định về môi trường."}),
    ({"client_project_is_claim": True}, {"Q15: Công trình khách hàng đạt chứng chỉ LEED Gold."}),
])
def test_a_convention_moves_only_the_sentences_it_covers(change, moved):
    other = ClaimPolicy(policy_id="org_x", **change)
    changed = {
        sentence for sentence, attrs, _, _ in CODEBOOK_CASES
        if compose_label(attrs, other).label != compose_label(attrs).label
    }
    assert changed == moved


def test_the_label_says_which_conventions_decided_it():
    """A reviewer who disagrees can tell 'the model misread' (an attribute) from
    'the convention does not fit' (a policy key) — the split reviews.py records."""
    assert compose_label(A(target=True, target_year=True)).decided_by == ("year_only_target",)
    assert compose_label(A(quantity="count")).decided_by == ("count_is_quantity",)
    assert compose_label(A(quantity="measure")).decided_by == ()


def test_composition_is_deterministic():
    for _, attrs, _, _ in CODEBOOK_CASES:
        assert compose_label(attrs) == compose_label(ClaimAttributes.from_json(attrs.to_json()))


def test_bad_attributes_and_policies_are_refused(tmp_path):
    with pytest.raises(InvalidAttributes, match="speaker"):
        A(speaker="government")
    with pytest.raises(InvalidAttributes, match="unknown"):
        ClaimAttributes.from_json({"form": "sentence", "is_green": True})
    with pytest.raises(ValueError, match="year_only_target"):
        ClaimPolicy(year_only_target=QUANTIFIED)
    bad = tmp_path / "p.yaml"
    bad.write_text("policy_id: x\nignore_rules: true\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unknown policy key"):
        ClaimPolicy.load(bad)
