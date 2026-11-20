"""feedback-loop-v1: pointer labels, hygiene, precedents, GS-Feedback, miner, models, queue (docs/03-architecture/FEEDBACK_LOOP.md).

The invariant every test here leans on: past decisions may add information beside
a verdict and add places to the review queue; they never change a verdict, a risk
score or a release status.
"""

from __future__ import annotations

import json
from collections import Counter

import numpy as np
import pytest

from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.agents.prioritizer import ReviewPriority
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import DocumentInput
from quantum_gw.feedback import hygiene, registry
from quantum_gw.feedback.bench import build_cases, check_ratchet, run_cases
from quantum_gw.feedback.dataset import assign_split, human_pairs
from quantum_gw.feedback.local_judge import LocalStanceJudge
from quantum_gw.feedback.miner import cue_candidates, org_rule_drafts
from quantum_gw.feedback.precedents import PrecedentIndex
from quantum_gw.feedback.queue import raise_queue
from quantum_gw.feedback.stance_model import HashedLinearStance, challenger_metrics, champion_metrics, train
from quantum_gw.settings import FeedbackSettings, load_settings
from quantum_gw.storage.reviews import ReviewError, ReviewStore, classify_stage

EVIDENCE = [
    {"chunk_id": "c1", "doc_id": "d1", "source_name": "BCTC 2024", "source_type": "financial", "page": 12,
     "relation": "PARTIAL", "score": 0.81,
     "text": "Trong số 500 tỷ đồng trái phiếu xanh, 180 tỷ đồng vẫn đang gửi ngân hàng và chưa được phân bổ cho dự án."},
    {"chunk_id": "c2", "doc_id": "d2", "source_name": "Báo cáo PTBV", "source_type": "internal", "page": 3,
     "relation": "SUPPORTS", "score": 0.55, "text": "Công ty phát hành trái phiếu xanh năm 2024 để tài trợ dự án điện mặt trời."},
]
CLAIM = {"text": "Nguồn vốn từ trái phiếu xanh được sử dụng hoàn toàn cho các dự án năng lượng tái tạo."}


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("QUANTUM_REVIEWS_FILE", str(tmp_path / "reviews" / "decisions.jsonl"))
    monkeypatch.delenv("QUANTUM_QA_FILE", raising=False)
    return ReviewStore()


def override(store, run="r1", claim="k1", decisive=("c1",), quote="", role="auditor", org="", label="CONTRADICTED",
             text=None, reviewer="Hà"):
    return store.record(run_id=run, claim_id=claim, reviewer=reviewer, decision="OVERRIDE", reviewer_status=label,
                        override_reason="MODEL_MISREAD", ai_status="PARTIALLY_SUPPORTED", evidence=EVIDENCE,
                        claim={"text": text or CLAIM["text"]}, decisive_chunk_ids=list(decisive),
                        decisive_quote=quote, reviewer_role=role, reviewer_org=org, comment="180 tỷ chưa phân bổ")


# ---------------------------------------------------------------- tier 0: pointer labels


def test_stage_comes_from_the_pointer():
    shown = [{"chunk_id": "c1"}, {"chunk_id": "c2"}]
    assert classify_stage("OVERRIDE", "MODEL_MISREAD", ["c1"], "", shown) == "reading"
    assert classify_stage("OVERRIDE", "MODEL_MISREAD", ["zz"], "", shown) == "retrieval"
    assert classify_stage("OVERRIDE", "MODEL_MISREAD", [], "đoạn người soát dán", shown) == "retrieval"
    assert classify_stage("OVERRIDE", "RULE_WRONG", ["c1"], "", shown) == "rule"
    assert classify_stage("OVERRIDE", "EVIDENCE_MISSED", [], "", shown) == "retrieval"
    assert classify_stage("CONFIRM", None, [], "", shown) == "none"
    assert classify_stage("ABSTAIN", None, [], "", shown) == ""


def test_record_keeps_pointer_role_and_full_text(store):
    record = override(store)
    assert record.error_stage == "reading" and record.decisive_chunk_ids == ["c1"]
    assert record.evidence_snapshot[0]["rank"] == 1 and record.evidence_snapshot[0]["source_type"] == "financial"
    assert record.evidence_snapshot[0]["text"].startswith("Trong số 500 tỷ")
    [gold] = store.gold_records()
    assert gold["train_eligible"] and gold["error_stage"] == "reading" and gold["claim"]["text"] == CLAIM["text"]
    assert store.stats()["pointer_labels"] == 1


def test_pointer_only_on_a_label_and_roles_are_checked(store):
    with pytest.raises(ReviewError):
        store.record(run_id="r", claim_id="k", reviewer="Hà", decision="ABSTAIN", decisive_chunk_ids=["c1"])
    with pytest.raises(ReviewError):
        store.record(run_id="r", claim_id="k", reviewer="Hà", decision="CONFIRM", reviewer_role="ceo")


def test_the_checked_company_never_trains(store):
    override(store, role="reviewed_company")
    [gold] = store.gold_records()
    assert gold["train_eligible"] is False
    assert hygiene.clean_labels(store.gold_records()) == []


# ---------------------------------------------------------------- hygiene


def test_kappa():
    assert hygiene.cohen_kappa([("S", "S"), ("C", "C")]) == 1.0
    assert hygiene.cohen_kappa([]) is None
    assert hygiene.cohen_kappa([("S", "C"), ("C", "S")]) < 0


def test_disagreement_is_held_out_until_adjudicated(store, tmp_path):
    override(store)
    qa = hygiene.QAStore(tmp_path / "qa.jsonl")
    with pytest.raises(ReviewError):
        qa.record_second(run_id="r1", claim_id="k1", reviewer="hà", status="CONTRADICTED", first_reviewer="Hà")
    qa.record_second(run_id="r1", claim_id="k1", reviewer="Lan", status="PARTIALLY_SUPPORTED", first_reviewer="Hà")
    report = hygiene.agreement(store.gold_records(), qa.all())
    assert report["double_reviewed"] == 1 and len(report["unresolved"]) == 1
    assert hygiene.clean_labels(store.gold_records(), qa.all()) == []
    qa.record_adjudication(run_id="r1", claim_id="k1", adjudicator="Minh", status="CONTRADICTED")
    [label] = hygiene.clean_labels(store.gold_records(), qa.all())
    assert label["label"] == "CONTRADICTED" and label["label_source"] == "adjudicated"


def test_an_organisation_sees_only_core_and_its_own(store, tmp_path):
    override(store, run="r1", org="ngan_hang_a")
    override(store, run="r2", org="")
    gold = store.gold_records()
    assert {g["run_id"] for g in hygiene.visible_records(gold, "ngan_hang_b")} == {"r2"}
    assert {g["run_id"] for g in hygiene.visible_records(gold, "ngan_hang_a")} == {"r1", "r2"}
    qa = hygiene.QAStore(tmp_path / "qa.jsonl")
    qa.promote_to_core(run_id="r1", claim_id="k1", approved_by="Đội GreenScan")
    assert {g["run_id"] for g in hygiene.visible_records(gold, "ngan_hang_b", qa.all())} == {"r1", "r2"}


def test_second_review_sample_is_deterministic():
    gold = [{"run_id": f"r{i}", "claim_id": "k", "claim_text": "x", "reviewer": "Hà"} for i in range(200)]
    a = hygiene.sample_for_second_review(gold, 0.1, "2026-11")
    assert a == hygiene.sample_for_second_review(gold, 0.1, "2026-11") and 5 <= len(a) <= 40


# ---------------------------------------------------------------- tier 2: precedents


def test_precedents_find_the_same_claim_and_examples_need_a_pointer(store):
    override(store)
    store.record(run_id="r9", claim_id="k9", reviewer="Hà", decision="CONFIRM", ai_status="SUPPORTED",
                 evidence=EVIDENCE, claim={"text": "Doanh thu năm 2024 tăng 12% so với năm trước."})
    index = PrecedentIndex.from_store(store)
    [card] = index.find({"text": "Vốn trái phiếu xanh được sử dụng hoàn toàn cho dự án năng lượng tái tạo."})
    assert card["overridden"] and card["label"] == "CONTRADICTED" and card["decisive"][0]["chunk_id"] == "c1"
    assert "trai" in card["shared_words"] or "phieu" in card["shared_words"]
    [example] = index.stance_examples(CLAIM["text"], k=3)
    assert example["relation"] == "CONTRADICTS" and "180 tỷ" in example["passage"]


# ---------------------------------------------------------------- queue: raise only


def _priority(cid, score, queued):
    return ReviewPriority(item_type="claim", item_id=cid, text="t", priority_score=score, rank=1, in_queue=queued)


def test_raise_queue_only_adds():
    items = [_priority("a", 70, True), _priority("b", 20, False), _priority("c", 10, False), _priority("d", 5, False)]
    findings = [{"claim_id": "b", "findings": [{"on_fail": "raise_priority", "outcome": "VIOLATION", "org_id": "o", "rule_id": "R1"}]},
                {"claim_id": "c", "findings": [{"on_fail": "flag_for_review", "outcome": "VIOLATION", "org_id": "o", "rule_id": "R2"}]}]
    precedents = {"d": [{"overridden": True, "similarity": 0.9, "run_id": "r", "claim_id": "k"}]}
    learning = {"c": {"value": 0.6, "reasons": []}, "a": {"value": 0.9, "reasons": []}}
    summary = raise_queue(items, org_findings=findings, precedents=precedents, learning=learning, slots=1)
    by = {p.item_id: p for p in items}
    assert by["a"].in_queue and by["a"].raised_by == []          # already queued, not picked by learning
    assert by["b"].in_queue and by["b"].raised_by == ["org_rule:o/R1"]
    assert by["c"].in_queue and by["c"].raised_by == ["active_learning"]   # flag_for_review alone does not raise
    assert by["d"].in_queue and by["d"].raised_by[0].startswith("precedent:")
    assert [p.priority_score for p in items] == [70, 20, 10, 5] and summary["raised"] == 3


# ---------------------------------------------------------------- the pipeline


def _docs():
    return [
        DocumentInput(name="claim.txt", role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL,
                      text="Năm 2024, công ty giảm 15% phát thải khí nhà kính phạm vi 1 so với năm 2020."),
        DocumentInput(name="evidence.txt", role=DocumentRole.EVIDENCE, source_type=SourceType.EXTERNAL,
                      text="Báo cáo kiểm toán độc lập: phát thải phạm vi 1 năm 2024 giảm 9% so với năm 2020."),
    ]


def test_precedents_never_change_a_verdict(store, settings):
    first = OrchestratorAgent(settings).run(_docs())
    assert first.precedents is None and first.manifest.feedback is None
    v = first.verifications[0]
    label = "PARTIALLY_SUPPORTED" if v.status.value != "PARTIALLY_SUPPORTED" else "CONTRADICTED"
    store.record(run_id=first.run_id, claim_id=v.claim.claim_id, reviewer="Hà", decision="OVERRIDE",
                 reviewer_status=label, override_reason="MODEL_MISREAD", ai_status=v.status.value,
                 evidence=[e.model_dump(mode="json") for e in v.evidence], claim=v.claim.model_dump(mode="json"),
                 decisive_chunk_ids=[v.evidence[0].chunk_id] if v.evidence else [])
    on = OrchestratorAgent(settings).run(_docs())
    off_settings = settings.model_copy(deep=True)
    off_settings.feedback.precedents = False
    off = OrchestratorAgent(off_settings).run(_docs())

    def dump(items):
        return [i.model_dump(mode="json") for i in items]

    assert dump(on.verifications) == dump(off.verifications) == dump(first.verifications)
    assert dump(on.risks) == dump(off.risks)
    assert on.summary.release_status == off.summary.release_status
    cards = on.precedents[v.claim.claim_id]
    assert cards[0]["similarity"] == 1.0 and cards[0]["overridden"]
    assert on.manifest.feedback["store"]["records"] == 1
    claim_priority = next(p for p in on.priorities if p["item_id"] == v.claim.claim_id)
    assert claim_priority["in_queue"] and claim_priority["raised_by"][0].startswith("precedent:")
    assert off.precedents is None and "precedents" not in json.loads(
        (__import__("pathlib").Path(off.output_directory) / "result.json").read_text(encoding="utf-8"))


def test_default_feedback_settings_leave_the_config_hash_alone():
    settings = load_settings("configs/default.yaml")
    assert "feedback" not in settings.model_dump()
    changed = settings.model_copy(deep=True)
    changed.feedback = FeedbackSettings(active_learning_slots=2)
    assert changed.stable_hash() != settings.stable_hash()


def test_env_switches(monkeypatch):
    monkeypatch.setenv("QUANTUM_FEEDBACK_PRECEDENTS", "off")
    monkeypatch.setenv("QUANTUM_ACTIVE_LEARNING_SLOTS", "3")
    monkeypatch.setenv("QUANTUM_FEEDBACK_ORG", "ngan_hang_a")
    feedback = load_settings("configs/default.yaml").feedback
    assert (feedback.precedents, feedback.active_learning_slots, feedback.org_id) == (False, 3, "ngan_hang_a")


# ---------------------------------------------------------------- tier 1: GS-Feedback


def test_gs_feedback_ratchet_catches_a_regression(store, tmp_path):
    override(store)
    cases = build_cases(store.gold_records())
    assert cases and cases[0]["evidence"][0]["text"]
    results = run_cases(cases)
    assert results[0]["predicted"] is not None and results[0]["error"] is None
    ratchet = tmp_path / "ratchet.json"
    ratchet.write_text(json.dumps({"passing": [cases[0]["case_id"]], "history": []}), encoding="utf-8")
    report = check_ratchet([{**results[0], "passed": False}], ratchet, update=True)
    assert report["regressions"] == [cases[0]["case_id"]] and report["ratchet_updated"] is False
    report = check_ratchet([{**results[0], "passed": True}], tmp_path / "new.json", update=True)
    assert report["newly_passing"] == [cases[0]["case_id"]] and report["ratchet_updated"]


# ---------------------------------------------------------------- tier 3: miner


def test_miner_proposes_a_well_cut_cue_and_warns_about_the_guard(store):
    override(store)
    cues = cue_candidates(hygiene.clean_labels(store.gold_records()))
    terms = [c["term"] for c in cues]
    assert "chưa được phân bổ" in terms
    assert not any(t.split()[0] == "và" or t.split()[-1] in ("chưa", "được") for t in terms)
    cue = next(c for c in cues if c["term"] == "chưa được phân bổ")
    assert cue["family"] == "refutes" and "chốt chống vu oan" in cue["note"]


def test_miner_drafts_an_org_rule_from_repeated_markdowns(store):
    for i in range(2):
        store.record(run_id=f"r{i}", claim_id="k", reviewer="Hà", decision="OVERRIDE",
                     reviewer_status="PARTIALLY_SUPPORTED", override_reason="MODEL_MISREAD", ai_status="SUPPORTED",
                     evidence=EVIDENCE, claim={"text": "Giảm 10% phát thải.", "baseline": None, "values": [10]},
                     reviewer_org="ngan_hang_a")
    drafts = org_rule_drafts(store.gold_records())
    baseline = next(d for d in drafts if d["attribute"] == "baseline")
    assert baseline["org_id"] == "ngan_hang_a" and baseline["support"] == 2
    assert "claim_attribute_present" in baseline["rule_yaml"]


# ---------------------------------------------------------------- tier 4: models and the gate


def _pairs(n=120):
    rows = []
    for i in range(n):
        if i % 3 == 0:
            rows.append(("Giảm 10% phát thải năm 2024", f"Phát thải năm 2024 giảm 10% so với năm 2020 (bảng {i})", "SUPPORTS"))
        elif i % 3 == 1:
            rows.append(("Giảm 10% phát thải năm 2024", f"Công ty tổ chức ngày hội gia đình lần thứ {i}", "CONTEXT"))
        else:
            rows.append(("Giảm 10% phát thải năm 2024", f"Phát thải có giảm nhưng chưa rõ mức, dự án {i}", "PARTIAL"))
    pairs = [{"id": str(i), "claim": c, "passage": p, "relation": r, "weight": 1.0, "provenance": "test",
              "group": f"g{i % 10}", "champion": "CONTEXT"} for i, (c, p, r) in enumerate(rows)]
    return assign_split(pairs, 0.3, seed="t")


def test_model_trains_saves_and_loads_without_pickle(tmp_path):
    pairs = _pairs()
    model = train(pairs)
    folder = tmp_path / "hl-test"
    model.save(folder)
    loaded = HashedLinearStance.load(folder)
    assert loaded.predict("Giảm 10% phát thải năm 2024", "Công ty tổ chức ngày hội gia đình")[0] == "CONTEXT"
    with np.load(folder / "weights.npz", allow_pickle=False) as data:
        assert data["coef"].shape[0] == len(loaded.labels)


def test_gate_registry_and_local_judge(tmp_path):
    pairs = _pairs()
    model = train(pairs)
    folder = tmp_path / "models" / "hl-1"
    model.save(folder)
    holdout = [p for p in pairs if p["split"] == "holdout"]
    reg = tmp_path / "models" / "registry.json"
    entry = registry.register(reg, folder, champion=champion_metrics(holdout), challenger=challenger_metrics(model, holdout),
                              data={"pairs": len(pairs)}, trained_by="An", kind="hashed-linear-v1")
    assert entry["status"] == "candidate"
    with pytest.raises(ValueError):
        LocalStanceJudge(folder, reg)                       # not promoted: refused
    with pytest.raises(ValueError):
        registry.promote(reg, "hl-1", "An")                 # the trainer cannot approve
    if entry["gate"]["passed"]:
        registry.promote(reg, "hl-1", "Bình")
        judge = LocalStanceJudge(folder, reg)
        assert judge.version.startswith("local:hl-1")
        (folder / "weights.npz").write_bytes(b"tampered")
        with pytest.raises(ValueError):
            LocalStanceJudge(folder, reg)                   # weights swapped after promotion
    worse = {**entry["challenger"], "false_contradicts": entry["champion"]["false_contradicts"] + 1}
    assert registry.gate(entry["champion"], worse)["passed"] is False


def test_human_pairs_need_a_pointer(store):
    override(store)
    store.record(run_id="r2", claim_id="k2", reviewer="Hà", decision="CONFIRM", ai_status="SUPPORTED",
                 evidence=EVIDENCE, claim={"text": "x"})
    pairs = human_pairs(hygiene.clean_labels(store.gold_records()))
    assert len(pairs) == 1 and pairs[0]["relation"] == "CONTRADICTS" and pairs[0]["champion"] == "PARTIAL"


# ---------------------------------------------------------------- S5 examples


class _Gateway:
    def __init__(self):
        self.messages = []

    def route(self, task):
        return ["fake"]

    def generate(self, messages, response_schema=None, task_type=None):
        self.messages.append(messages)

        class R:
            parsed = {"relation": "CONTEXT", "reason": "x", "injection": False}
            provider, model, usage = "fake", "fake-model", {}
        return R()


def test_stance_examples_are_fenced_and_change_the_cache_key(tmp_path):
    from quantum_gw.verification.llm_judge import LLMStanceJudge

    gateway = _Gateway()
    judge = LLMStanceJudge(gateway=gateway, cache_dir=tmp_path)
    plain = judge._key("c", "e")
    judge.examples_for = lambda text: [{"ref": "r1:k1", "claim": "ví dụ", "passage": "đoạn <<<x>>>", "relation": "CONTRADICTS"}]
    assert judge._key("c", "e") != plain
    judge.judge("c", "e")
    content = gateway.messages[-1][-1]["content"]
    assert "VÍ DỤ 1: TUYÊN BỐ" in content and "<<<x>>>" not in content and "CONTRADICTS" in content


def test_learning_values_have_reasons():
    from quantum_gw.feedback.active import learning_values

    class V:
        def __init__(self):
            self.claim = type("C", (), {"claim_id": "a", "claim_type": "emission"})()
            self.evidence = [type("E", (), {"relation": "SUPPORTS"})(), type("E", (), {"relation": "CONTRADICTS"})()]
            self.requires_llm_review = True

    out = learning_values([V()], {}, Counter({"emission": 1}), {"a": 2})
    assert out["a"]["value"] == 1.0 and len(out["a"]["reasons"]) == 5
