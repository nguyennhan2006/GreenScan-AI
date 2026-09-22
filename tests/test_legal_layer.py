"""Legal layer: clause structure, temporal correctness, and refusal to overreach.

The three failures these guard against are all silent:
  - a chunk that cuts through a condition, so a citation points at half a rule;
  - a 2022 claim judged by 2026 law;
  - "no evidence found" reported as "does not comply".
"""

from datetime import date

import pytest

from quantum_gw.legal.checker import LegalChecker
from quantum_gw.legal.corpus import CURRENT, HISTORICAL, LegalCorpus, LegalDocument
from quantum_gw.legal.parser import (
    duplicate_id_report,
    parse_document,
    structure_summary,
)
from quantum_gw.legal.rules import (
    INSUFFICIENT_EVIDENCE,
    MATCH,
    NOT_MATCH,
    NOT_SATISFIED,
    PARTIAL_MATCH,
    SATISFIED,
    UNKNOWN,
    Condition,
    Rule,
    RulePack,
    combine,
    evaluate_condition,
)

STATUTE = """
Chương I
QUY ĐỊNH CHUNG

Điều 1. Phạm vi điều chỉnh
Quyết định này quy định tiêu chí môi trường.

Điều 3. Tiêu chí môi trường
1. Dự án đầu tư thuộc danh mục phân loại xanh phải đáp ứng các tiêu chí sau:
a) Có báo cáo đánh giá tác động môi trường được phê duyệt;
b) Tỷ lệ tái chế đạt tối thiểu 50%;
c) Không thuộc danh mục ngành nghề bị hạn chế.
2. Việc xác nhận được thực hiện theo trình tự tại Điều 5.

PHỤ LỤC I
DANH MỤC TIÊU CHÍ
1. Năng lượng tái tạo.
2. Xử lý chất thải.
"""


# ---------------- L1 parser ----------------

def test_parser_reaches_item_level():
    clauses = parse_document("QD21-2025", STATUTE)
    ids = {c.clause_id for c in clauses}
    assert "QD21-2025:article_3:paragraph_1:item_b" in ids


def test_item_text_is_not_cut_mid_condition():
    clauses = {c.clause_id: c for c in parse_document("QD21-2025", STATUTE)}
    item_b = clauses["QD21-2025:article_3:paragraph_1:item_b"]
    assert "50%" in item_b.text
    assert item_b.text.strip().endswith(";")


def test_paragraph_stem_is_kept():
    """The stem introduces the items; dropping it orphans every one of them."""
    clauses = {c.clause_id: c for c in parse_document("QD21-2025", STATUTE)}
    stem = clauses["QD21-2025:article_3:paragraph_1"]
    assert "đáp ứng các tiêu chí sau" in stem.text


def test_citation_reads_like_a_lawyer_wrote_it():
    clauses = {c.clause_id: c for c in parse_document("QD21-2025", STATUTE)}
    assert clauses["QD21-2025:article_3:paragraph_1:item_b"].citation == (
        "Điều 3, khoản 1, điểm b"
    )


def test_parent_path_allows_walking_back_up():
    clauses = {c.clause_id: c for c in parse_document("QD21-2025", STATUTE)}
    item = clauses["QD21-2025:article_3:paragraph_1:item_c"]
    assert item.parent_path == ["QD21-2025", "QD21-2025:article_3",
                               "QD21-2025:article_3:paragraph_1"]


def test_chapter_context_is_attached():
    clauses = {c.clause_id: c for c in parse_document("QD21-2025", STATUTE)}
    assert clauses["QD21-2025:article_1"].chapter == "I"


def test_annex_is_parsed_separately_from_articles():
    clauses = parse_document("QD21-2025", STATUTE)
    annex = [c for c in clauses if c.annex]
    assert annex and all(c.article is None for c in annex)
    assert structure_summary(clauses)["annexes"] == 1


def test_empty_document_yields_no_clauses():
    assert parse_document("X", "") == []


# ---------------- L2 temporal ----------------

@pytest.fixture
def corpus():
    return LegalCorpus.from_registry("configs/legal/LEGAL_SOURCE_REGISTRY.yaml")


def test_document_not_in_force_before_its_effective_date(corpus):
    qd21 = corpus.documents["QD21-2025-QD-TTg"]
    assert not qd21.in_force_on(date(2025, 8, 21))
    assert qd21.in_force_on(date(2025, 8, 22))


def test_historical_mode_uses_the_claim_date_not_today(corpus):
    as_of = corpus.resolve_as_of(HISTORICAL, date(2022, 6, 30), date(2026, 8, 9))
    assert as_of == date(2022, 6, 30)


def test_current_mode_uses_today(corpus):
    assert corpus.resolve_as_of(CURRENT, date(2022, 6, 30), date(2026, 8, 9)) == date(2026, 8, 9)


def test_historical_mode_refuses_without_a_publication_date(corpus):
    """Guessing the date would silently pick an arbitrary body of law."""
    with pytest.raises(ValueError, match="publication date"):
        corpus.resolve_as_of(HISTORICAL, None, date(2026, 8, 9))


def test_amendment_in_force_joins_the_chain(corpus):
    """Asserted as membership, not set equality.

    An earlier version pinned the exact set and broke the moment the registry
    gained NĐ 48/2026 — a genuine amendment discovered later. A chain test must
    fail when the *semantics* break, not when the corpus grows.
    """
    chain = {d.id for d in corpus.effective_chain("ND08-2022-ND-CP", date(2026, 1, 1))}
    assert "ND08-2022-ND-CP" in chain, "the base instrument must always be present"
    assert "ND05-2025-ND-CP" in chain, "an amendment in force must join the chain"


def test_amendment_absent_before_it_took_effect(corpus):
    chain = {d.id for d in corpus.effective_chain("ND08-2022-ND-CP", date(2024, 1, 1))}
    assert chain == {"ND08-2022-ND-CP"}, "no amendment had taken effect by 2024"


def test_chain_grows_monotonically_over_time(corpus):
    """Later dates can only add amendments, never remove the base."""
    early = {d.id for d in corpus.effective_chain("ND06-2022-ND-CP", date(2023, 1, 1))}
    late = {d.id for d in corpus.effective_chain("ND06-2022-ND-CP", date(2026, 8, 14))}
    assert early <= late
    assert "ND06-2022-ND-CP" in early


def test_documents_without_text_are_not_offered_as_applicable():
    """Registered is not the same as readable.

    Written against a synthetic corpus: asserting on the live registry pinned
    the pre-OCR state and broke the moment QĐ 21/2025 became readable.
    """
    readable = LegalDocument(
        id="R", document_number="1/2025", title="t", doc_type="quyet_dinh", authority="a",
        issued_date=None, effective_from=date(2025, 1, 1), effective_to=None,
        status="effective", legal_issues=["green_taxonomy"], text_acquisition="ok")
    unread = LegalDocument(
        id="U", document_number="2/2025", title="t", doc_type="quyet_dinh", authority="a",
        issued_date=None, effective_from=date(2025, 1, 1), effective_to=None,
        status="effective", legal_issues=["green_taxonomy"],
        text_acquisition="source_unavailable")
    corpus = LegalCorpus([readable, unread])
    assert [d.id for d in corpus.applicable("green_taxonomy", date(2026, 8, 9))] == ["R"]
    assert [d.id for d in corpus.blocked("green_taxonomy", date(2026, 8, 9))] == ["U"]


# ---------------- L3 rules ----------------

def test_missing_evidence_is_unknown_not_failure():
    """The most damaging possible error: silence read as non-compliance."""
    c = Condition(id="x", description="d", source_clause="s",
                  check="terms_present", any_of_terms=["tái chế"])
    assert evaluate_condition(c, [])["status"] == UNKNOWN
    assert evaluate_condition(c, [{"chunk_id": "c1", "text": "nội dung không liên quan"}])[
        "status"] == UNKNOWN


def test_terms_present_marks_which_evidence_supported_it():
    c = Condition(id="x", description="d", source_clause="s",
                  check="terms_present", any_of_terms=["tái chế"])
    out = evaluate_condition(c, [{"chunk_id": "c1", "text": "tỷ lệ tái chế đạt 55%"}])
    assert out["status"] == SATISFIED
    assert out["evidence_ids"] == ["c1"]


def test_manual_condition_never_auto_satisfies():
    c = Condition(id="x", description="d", source_clause="s", check="manual")
    out = evaluate_condition(c, [{"chunk_id": "c1", "text": "văn bản xác nhận dự án xanh"}])
    assert out["status"] == UNKNOWN
    assert "người xem xét" in out["reason"]


def test_numeric_threshold_can_refute():
    c = Condition(id="x", description="d", source_clause="s", check="numeric_threshold",
                  operator=">=", threshold=50.0)
    assert evaluate_condition(c, [{"chunk_id": "c", "text": "tỷ lệ 12"}])["status"] == NOT_SATISFIED
    assert evaluate_condition(c, [{"chunk_id": "c", "text": "tỷ lệ 62"}])["status"] == SATISFIED


@pytest.mark.parametrize("statuses,expected", [
    ([SATISFIED, SATISFIED], MATCH),
    ([SATISFIED, UNKNOWN], PARTIAL_MATCH),
    ([UNKNOWN, UNKNOWN], INSUFFICIENT_EVIDENCE),
    ([SATISFIED, NOT_SATISFIED], NOT_MATCH),
    ([UNKNOWN, NOT_SATISFIED], NOT_MATCH),
    ([], INSUFFICIENT_EVIDENCE),
])
def test_combination_never_upgrades_unknown_to_match(statuses, expected):
    assert combine([{"status": s} for s in statuses]) == expected


# ---------------- checker ----------------

def test_checker_refuses_when_the_governing_text_was_never_read():
    """A corpus whose only relevant instrument is unread must not produce a verdict."""
    unread = LegalDocument(
        id="U", document_number="2/2025", title="t", doc_type="quyet_dinh", authority="a",
        issued_date=None, effective_from=date(2025, 1, 1), effective_to=None,
        status="effective", legal_issues=["green_taxonomy"],
        text_acquisition="source_unavailable",
        text_acquisition_note="Authority endpoint failed.")
    corpus = LegalCorpus([unread])
    pack = RulePack.from_yaml("configs/legal/rule_pack_vn_green_v0.1.yaml")
    result = LegalChecker(corpus, pack).check(
        claim={"claim_id": "k1", "claim_type": "green_project"},
        evidence=[{"chunk_id": "c1", "text": "dự án tái chế, tiêu chí môi trường"}],
        check_mode=CURRENT, today=date(2026, 8, 9),
    )
    assert result.legal_finding == INSUFFICIENT_EVIDENCE
    assert result.requires_human_review
    assert any(b["id"] == "U" for b in result.blocked_sources)
    assert "chưa đọc được văn bản" in result.notes


def test_checker_reports_the_mode_and_date_it_used(corpus):
    pack = RulePack.from_yaml("configs/legal/rule_pack_vn_green_v0.1.yaml")
    result = LegalChecker(corpus, pack).check(
        claim={"claim_id": "k1", "claim_type": "green_project"}, evidence=[],
        check_mode=HISTORICAL, claim_published=date(2023, 5, 1), today=date(2026, 8, 9),
    )
    assert (result.check_mode, result.as_of_date) == (HISTORICAL, "2023-05-01")


def test_checker_rejects_an_unknown_mode(corpus):
    pack = RulePack.from_yaml("configs/legal/rule_pack_vn_green_v0.1.yaml")
    with pytest.raises(ValueError, match="check_mode"):
        LegalChecker(corpus, pack).check(
            claim={"claim_id": "k"}, evidence=[], check_mode="vibes")


def test_rule_pack_requires_conditions(tmp_path):
    bad = tmp_path / "p.yaml"
    bad.write_text(
        "version: v\nrules:\n  - rule_id: R\n    title: t\n    source_document: D\n"
        "    legal_issue: green_taxonomy\n    conditions: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no conditions"):
        RulePack.from_yaml(bad)


def test_rule_not_in_force_is_not_applied():
    rule = Rule(rule_id="R", title="t", source_document="D", source_clauses=[],
                claim_types=["green_project"], legal_issue="green_taxonomy",
                conditions=[Condition(id="c", description="d", source_clause="s")],
                effective_from=date(2025, 8, 22))
    pack = RulePack("v", [rule])
    assert pack.for_claim("green_project", "green_taxonomy", date(2024, 1, 1)) == []
    assert pack.for_claim("green_project", "green_taxonomy", date(2026, 1, 1)) == [rule]


ANNEX_TABLE = """
Điều 1. Phạm vi
Nội dung điều một.

PHỤ LỤC I
TIÊU CHÍ MÔI TRƯỜNG
1. Sản xuất điện mặt trời.
2. Hiệu suất chuyển đổi quang điện.
1. Sản xuất điện gió.
2. Thiết bị phải được chứng nhận hợp chuẩn.
"""


def test_annex_repeated_numbering_does_not_collide():
    """Annex tables restart numbering per row; khoản-style ids would collide.

    Phụ lục I of 21/2025/QĐ-TTg repeats "2." 27 times, which produced 75
    duplicate clause_ids — and a duplicated citation key makes a rule binding
    ambiguous.
    """
    clauses = parse_document("D", ANNEX_TABLE)
    ids = [c.clause_id for c in clauses]
    assert len(ids) == len(set(ids)), "clause_id must be unique"

    annex = [c for c in clauses if c.annex]
    assert len(annex) == 4
    assert [c.clause_id for c in annex] == [
        "D:annex_I:item_001", "D:annex_I:item_002",
        "D:annex_I:item_003", "D:annex_I:item_004",
    ]


def test_annex_keeps_the_printed_number_for_display():
    """The address is a running ordinal; the number on the page is still shown."""
    annex = [c for c in parse_document("D", ANNEX_TABLE) if c.annex]
    assert [c.paragraph for c in annex] == [1, 2, 1, 2]


def test_articles_are_unaffected_by_the_annex_rule():
    clauses = parse_document("D", ANNEX_TABLE)
    article = [c for c in clauses if c.article == 1]
    assert article and article[0].clause_id == "D:article_1"


REPEATED = """
Điều 1. Phạm vi điều chỉnh
Điều 2. Đối tượng áp dụng

Điều 1. Phạm vi điều chỉnh
Quyết định này quy định tiêu chí môi trường.

Điều 2. Đối tượng áp dụng
Áp dụng với chủ dự án đầu tư.
"""


def test_repeated_article_numbers_never_collide():
    """A table of contents lists the same Điều numbers before the real articles."""
    clauses = parse_document("D", REPEATED)
    ids = [c.clause_id for c in clauses]
    assert len(ids) == len(set(ids)), f"duplicate clause_id: {ids}"


def test_collision_keeps_both_occurrences():
    """Nothing is dropped: a TOC line cannot be told from operative text reliably."""
    clauses = parse_document("D", REPEATED)
    first = [c for c in clauses if c.clause_id == "D:article_1"]
    second = [c for c in clauses if c.clause_id == "D:article_1#2"]
    assert first and second
    assert "tiêu chí môi trường" in second[0].text


def test_duplicate_report_surfaces_collisions_for_review():
    report = duplicate_id_report(parse_document("D", REPEATED))
    assert report.get("D:article_1") == 2


def test_gate_and_checker_agree_on_what_usable_means(corpus):
    """A document cannot be READY for the gate and blocked for the checker.

    The two carried separate literal status sets; QĐ 21/2025 passed
    LEGAL SOURCE READY on `ok_ocr` while `applicable()` still excluded it, so
    the finding reported it as blocked.
    """
    from quantum_gw.legal.gates import check_source
    for doc in corpus.documents.values():
        gate = check_source(doc, corpus)
        assert doc.usable == ("full_text_available" not in gate.failed), (
            f"{doc.id}: usable={doc.usable} but gate says "
            f"full_text_available failed={('full_text_available' in gate.failed)}"
        )


def test_ocr_text_is_usable_but_marked_as_recognised():
    doc = LegalDocument(
        id="X", document_number="n", title="t", doc_type="quyet_dinh", authority="a",
        issued_date=None, effective_from=date(2025, 1, 1), effective_to=None,
        status="effective", text_acquisition="ok_ocr",
    )
    assert doc.usable and doc.text_is_ocr


def test_unread_document_is_not_usable():
    doc = LegalDocument(
        id="X", document_number="n", title="t", doc_type="quyet_dinh", authority="a",
        issued_date=None, effective_from=date(2025, 1, 1), effective_to=None,
        status="effective", text_acquisition="scanned_no_text",
    )
    assert not doc.usable
