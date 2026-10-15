"""GreenScan Studio: suggestions never invent a figure; exports carry real tracked changes."""

from __future__ import annotations

import zipfile

import pytest

from quantum_gw.parsers.office import docx_paragraphs
from quantum_gw.studio.document import Locator, fold
from quantum_gw.studio.escalation import decide
from quantum_gw.studio.export import align, changes, docx_from_lines, docx_in_place
from quantum_gw.studio.session import StudioSession
from quantum_gw.studio.suggest import InventedNumberError, apply, assert_no_new_numbers, numbers_in, suggest


def _diag(**overrides):
    base = {
        "claim_id": "c1", "status": "PARTIALLY_SUPPORTED", "claim_type": "emissions",
        "missing": ["kỳ", "năm gốc", "phạm vi"], "vague_terms": [], "evidence": [],
    }
    base.update(overrides)
    return base


# ---------- the guard ----------

def test_guard_rejects_a_number_that_was_not_in_the_sentence():
    with pytest.raises(InventedNumberError):
        assert_no_new_numbers("Giảm phát thải đáng kể.", "Giảm 30% phát thải.")
    assert_no_new_numbers("Giảm 30% phát thải.", "Giảm 30% phát thải (năm gốc: [bổ sung]).")
    assert_no_new_numbers("Giảm phát thải.", "Giảm phát thải (xem: BCTC, tr. 12).", allowed={"12"})


CLAIMS = [
    ("Tập đoàn đã trung hòa carbon trong năm 2024 nhờ mua tín chỉ.", ["trung hoa carbon"]),
    ("Sản phẩm thân thiện với môi trường và hoàn toàn xanh.", ["than thien voi moi truong"]),
    ("Chúng tôi là doanh nghiệp thép xanh hàng đầu Việt Nam.", []),
    ("Năm 2024 phát thải giảm 12,5% so với năm 2020, đạt 1.480.000 tấn CO2e.", []),
    ("Công ty không ngừng nỗ lực giảm phát thải.", ["khong ngung"]),
]


@pytest.mark.parametrize("text,vague", CLAIMS)
def test_no_suggestion_adds_a_number(text, vague):
    evidence = [{"relation": "SUPPORTS", "page": 47, "source_name": "BCTC 2024.pdf", "citation": "BCTC 2024.pdf (page 47)"}]
    for diag in (_diag(vague_terms=vague, missing=["số liệu", "kỳ"]), _diag(vague_terms=vague, evidence=evidence)):
        suggestions = suggest(diag, text)
        assert suggestions, text
        for s in suggestions:
            new = numbers_in(s.after) - numbers_in(text) - {"47"}
            assert not new, (s.rule_code, s.after)
            assert apply(text, s) == s.after


def test_four_kinds_are_produced():
    text = "Tập đoàn đã trung hòa carbon và không ngừng giảm phát thải."
    kinds = {s.kind for s in suggest(_diag(vague_terms=["khong ngung"], missing=["số liệu", "kỳ", "năm gốc"]), text)}
    assert kinds == {"soften", "placeholder", "add_scope", "evidence_ref"}


def test_future_commitment_is_not_softened_as_a_present_claim():
    text = "Mục tiêu đến năm 2050 đạt trung hòa carbon."
    assert not [s for s in suggest(_diag(), text) if s.rule_code == "OC-01"]


def test_evidence_reference_cites_only_supporting_evidence():
    partial = [{"relation": "PARTIAL", "page": 9, "source_name": "BCTN.pdf"}]
    s = [x for x in suggest(_diag(evidence=partial), "Giảm phát thải.") if x.kind == "evidence_ref"][0]
    assert s.rule_code == "EV-02" and "tr. 9" not in s.after


# ---------- locating claims ----------

def test_locator_tolerates_wraps_and_accents():
    text = "Mở đầu.\nNăm 2024 Tập đoàn  giảm 30%\nphát thải. Tiếp theo."
    span = Locator(text).find("Năm 2024 Tập đoàn giảm 30% phát thải.")
    assert span and text[span[0]:span[1]].startswith("Năm 2024") and text[span[0]:span[1]].endswith("thải.")
    assert len(fold("Đồng Hới")) == len("Đồng Hới")


# ---------- export ----------

def test_align_pairs_changes_inserts_and_deletes():
    kinds = [k for k, _, _ in align(["a", "b", "c"], ["a", "B", "c", "d"])]
    assert kinds == ["equal", "change", "equal", "insert"]


def test_docx_in_place_writes_tracked_changes_and_a_clean_copy(tmp_path):
    base = ["Tiêu đề", "Năm 2024 giảm 30% phát thải.", "Đoạn sẽ bị xóa.", "Kết thúc."]
    source = tmp_path / "goc.docx"
    source.write_bytes(docx_from_lines(base, base, [None] * 4, [], "", tracked=False))
    assert [p["text"] for p in docx_paragraphs(source)] == base
    edited = ["Tiêu đề", "Năm 2024 giảm 30% phát thải (năm gốc: [bổ sung]).", "Kết thúc.", "Đoạn mới thêm."]
    log = [{"actor": "ai-rule", "action": "accept", "after": "Năm 2024 giảm 30% phát thải (năm gốc: [bổ sung])."}]

    tracked, _ = docx_in_place(source, base, edited, log, "Nhân", tracked=True)
    out = tmp_path / "tracked.docx"
    out.write_bytes(tracked)
    xml = zipfile.ZipFile(out).read("word/document.xml").decode("utf-8")
    assert 'w:author="GreenScan AI (quy tắc)"' in xml and "<w:ins " in xml and "<w:del " in xml
    assert "Đoạn sẽ bị xóa." in xml  # deleted text stays, marked as w:delText
    visible = [p["text"] for p in docx_paragraphs(out) if p["text"]]
    assert "Đoạn mới thêm." in visible and "Đoạn sẽ bị xóa." not in visible

    clean, _ = docx_in_place(source, base, edited, log, "Nhân", tracked=False)
    out_clean = tmp_path / "clean.docx"
    out_clean.write_bytes(clean)
    assert [p["text"] for p in docx_paragraphs(out_clean)] == edited


def test_change_list_marks_word_level_edits():
    change = changes(["Giảm phát thải."], ["Giảm phát thải [bổ sung: số liệu]."])[0]
    assert change["kind"] == "change" and any(op == "ins" and "bổ sung" in t for op, t in change["ops"])


# ---------- escalation and log ----------

def test_escalation_follows_the_14_10_decision():
    assert decide(0.3, "A", None, True)["route"] == "local"          # τ not calibrated: nothing escalates
    assert decide(0.3, "A", 0.6, True)["route"] == "llm"
    assert decide(0.3, "B", 0.6, True)["route"] == "human"
    assert decide(0.3, "C", 0.6, True)["route"] == "human"
    assert decide(0.3, "A", 0.6, False)["route"] == "human"         # offline: never call the API
    assert decide(0.9, "A", 0.6, True)["route"] == "local"


def test_log_is_append_only_and_restore_is_logged(tmp_path):
    session = StudioSession(tmp_path, "d1")
    session.save("gốc", "sửa 1", [{"actor": "user", "action": "edit"}], snapshot=True, note="v1")
    data = session.save("gốc", "sửa 2", [{"actor": "ai-rule", "action": "accept", "rule_code": "SC-01"}])
    assert [e["seq"] for e in data["log"]] == [1, 2, 3]
    data = session.restore("gốc", 1)
    assert data["text"] == "sửa 1" and data["log"][-1]["action"] == "restore" and len(data["log"]) == 4
    with pytest.raises(ValueError):
        session.save("gốc", "x", [{"actor": "hacker", "action": "edit"}])
    with pytest.raises(ValueError):
        session.save("văn bản khác", "x", [])
