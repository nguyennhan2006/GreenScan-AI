"""Release gates: a missing document must never become "no applicable law".

    LEGAL SOURCE READY = official_source AND full_text_available
                         AND clause_parse_valid AND effective_date_known
                         AND amendment_chain_resolved AND provenance_complete

    LEGAL RULE ACTIVE  = source_clause_bound AND human_reviewed
                         AND unit_tests_pass AND temporal_scope_defined

The gate reports *which* condition failed, because "no instrument governs this"
and "we could not read the instrument" need opposite follow-up.
"""

from datetime import date

import pytest

from quantum_gw.legal.corpus import LegalCorpus, LegalDocument
from quantum_gw.legal.gates import check_rule, check_source
from quantum_gw.legal.rules import Condition, Rule, RulePack


def make_doc(**kw) -> LegalDocument:
    base = dict(
        id="D1", document_number="21/2025/QĐ-TTg", title="t", doc_type="quyet_dinh",
        authority="Thủ tướng Chính phủ", issued_date=date(2025, 7, 4),
        effective_from=date(2025, 8, 22), effective_to=None, status="effective",
        legal_issues=["green_taxonomy"], text_acquisition="ok",
        landing_url="https://vanban.chinhphu.vn/?pageid=27160&docid=214447",
        relations={},
    )
    base.update(kw)
    raw = {
        "document_number": base["document_number"], "authority": base["authority"],
        "issued_date": "2025-07-04",
        "original_url": kw.pop("original_url", "https://congbaocdn.chinhphu.vn/x.pdf"),
        "clauses_file": kw.get("clauses_file"),
    }
    raw.update(kw.get("raw", {}))
    base["raw"] = raw
    base.pop("raw_extra", None)
    return LegalDocument(**{k: v for k, v in base.items()
                            if k in LegalDocument.__dataclass_fields__})


@pytest.fixture
def clauses_file(tmp_path):
    p = tmp_path / "clauses.jsonl"
    p.write_text('{"clause_id": "D1:article_1", "text": "x"}\n', encoding="utf-8")
    return p


def source_gate(doc, corpus=None, root=None):
    return check_source(doc, corpus or LegalCorpus([doc]), repo_root=root)


# ---------------------------------------------------------- source gate

def test_ready_document_passes_every_condition(tmp_path, clauses_file):
    doc = make_doc(clauses_file=str(clauses_file.relative_to(tmp_path)))
    doc.raw["clauses_file"] = str(clauses_file.relative_to(tmp_path))
    r = source_gate(doc, root=tmp_path)
    assert r.ready, r.failed
    assert all(r.conditions.values())


def test_scanned_pdf_blocks_on_text_not_on_source(tmp_path, clauses_file):
    """The QĐ 21/2025 situation: authoritative source, unreadable text."""
    doc = make_doc(text_acquisition="scanned_no_text")
    r = source_gate(doc, root=tmp_path)
    assert not r.ready
    assert "full_text_available" in r.failed
    assert "official_source" not in r.failed, "the source is fine; only the text is not"


def test_unofficial_url_is_rejected(tmp_path):
    doc = make_doc(landing_url="https://thuvienphapluat.vn/abc")
    doc.raw["original_url"] = "https://random-mirror.example/x.pdf"
    r = source_gate(doc, root=tmp_path)
    assert "official_source" in r.failed


def test_missing_effective_date_blocks(tmp_path, clauses_file):
    doc = make_doc(effective_from=None)
    doc.raw["clauses_file"] = str(clauses_file.relative_to(tmp_path))
    assert "effective_date_known" in source_gate(doc, root=tmp_path).failed


def test_unregistered_amender_blocks_the_chain(tmp_path, clauses_file):
    """A chain that stops silently leaves a superseded rule in force."""
    doc = make_doc(relations={"amended_by": ["ND-NOT-REGISTERED"]})
    doc.raw["clauses_file"] = str(clauses_file.relative_to(tmp_path))
    r = source_gate(doc, LegalCorpus([doc]), root=tmp_path)
    assert "amendment_chain_resolved" in r.failed
    assert "ND-NOT-REGISTERED" in r.reasons["amendment_chain_resolved"]


def test_registered_amender_resolves(tmp_path, clauses_file):
    amender = make_doc(id="D2", document_number="05/2025/NĐ-CP")
    doc = make_doc(relations={"amended_by": ["D2"]})
    doc.raw["clauses_file"] = str(clauses_file.relative_to(tmp_path))
    r = check_source(doc, LegalCorpus([doc, amender]), repo_root=tmp_path)
    assert "amendment_chain_resolved" not in r.failed


def test_text_ok_but_zero_clauses_still_blocks(tmp_path):
    """Extracting prose is not the same as producing citable clauses."""
    doc = make_doc()
    r = source_gate(doc, root=tmp_path)
    assert "clause_parse_valid" in r.failed


def test_incomplete_provenance_blocks(tmp_path, clauses_file):
    doc = make_doc()
    doc.raw["clauses_file"] = str(clauses_file.relative_to(tmp_path))
    doc.raw["authority"] = ""
    assert "provenance_complete" in source_gate(doc, root=tmp_path).failed


def test_failed_list_names_the_condition_not_just_false(tmp_path):
    doc = make_doc(text_acquisition="source_unavailable", effective_from=None)
    r = source_gate(doc, root=tmp_path)
    assert set(r.failed) >= {"full_text_available", "effective_date_known"}
    assert r.to_json()["reasons"], "a blocked gate must explain itself"


# ------------------------------------------------------------ rule gate

def rule(**kw) -> Rule:
    base = dict(
        rule_id="R1", title="t", source_document="D1",
        source_clauses=["D1:article_3:paragraph_1"], claim_types=["green_project"],
        legal_issue="green_taxonomy",
        conditions=[Condition(id="c", description="d", source_clause="D1:article_3")],
        effective_from=date(2025, 8, 22), reviewed_by="quynh",
    )
    base.update(kw)
    return Rule(**base)


def test_fully_bound_reviewed_rule_is_active():
    corpus = LegalCorpus([make_doc()])
    r = check_rule(rule(), corpus, known_clause_ids={"D1:article_3:paragraph_1"},
                   unit_tests_pass=True)
    assert r.ready, r.failed


def test_unbound_clauses_block():
    corpus = LegalCorpus([make_doc()])
    r = check_rule(rule(source_clauses=[]), corpus, unit_tests_pass=True)
    assert "source_clause_bound" in r.failed


def test_unbound_placeholder_blocks():
    corpus = LegalCorpus([make_doc()])
    r = check_rule(rule(source_clauses=["QD21-2025:UNBOUND"]), corpus, unit_tests_pass=True)
    assert "source_clause_bound" in r.failed


def test_clause_id_absent_from_parsed_corpus_blocks():
    corpus = LegalCorpus([make_doc()])
    r = check_rule(rule(), corpus, known_clause_ids={"D1:article_9"}, unit_tests_pass=True)
    assert "source_clause_bound" in r.failed


def test_unreviewed_rule_blocks():
    corpus = LegalCorpus([make_doc()])
    r = check_rule(rule(reviewed_by=""), corpus,
                   known_clause_ids={"D1:article_3:paragraph_1"}, unit_tests_pass=True)
    assert "human_reviewed" in r.failed


def test_unit_test_status_must_be_supplied_not_assumed():
    """A rule pack asserting its own tests pass is not evidence."""
    corpus = LegalCorpus([make_doc()])
    r = check_rule(rule(), corpus, known_clause_ids={"D1:article_3:paragraph_1"})
    assert "unit_tests_pass" in r.failed


def test_missing_temporal_scope_blocks():
    corpus = LegalCorpus([make_doc()])
    r = check_rule(rule(effective_from=None), corpus,
                   known_clause_ids={"D1:article_3:paragraph_1"}, unit_tests_pass=True)
    assert "temporal_scope_defined" in r.failed


def test_rule_citing_an_unregistered_document_blocks():
    r = check_rule(rule(source_document="GHOST"), LegalCorpus([make_doc()]),
                   known_clause_ids={"D1:article_3:paragraph_1"}, unit_tests_pass=True)
    assert "source_clause_bound" in r.failed


# --------------------------------------------------------- shipped state

def test_shipped_rule_pack_is_not_active():
    """The draft pack must not pass the gate while it is still unbound."""
    corpus = LegalCorpus.from_registry("configs/legal/LEGAL_SOURCE_REGISTRY.yaml")
    pack = RulePack.from_yaml("configs/legal/rule_pack_vn_green_v0.1.yaml")
    for r in pack.rules:
        assert not check_rule(r, corpus, unit_tests_pass=False).ready


def test_ocr_text_counts_as_available_but_is_flagged(tmp_path, clauses_file):
    """OCR text is citable; its lower trust is enforced by the rule gate instead."""
    doc = make_doc(text_acquisition="ok_ocr")
    doc.raw["clauses_file"] = str(clauses_file.relative_to(tmp_path))
    r = source_gate(doc, root=tmp_path)
    assert "full_text_available" not in r.failed
    assert r.ready


def test_still_blocks_when_text_was_never_extracted(tmp_path, clauses_file):
    doc = make_doc(text_acquisition="source_unavailable")
    doc.raw["clauses_file"] = str(clauses_file.relative_to(tmp_path))
    assert "full_text_available" in source_gate(doc, root=tmp_path).failed
