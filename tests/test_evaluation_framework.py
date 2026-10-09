"""The evaluation framework, checked against gold whose answer is known.

A harness that has only ever run on an empty gold set is a harness nobody has
tested. These build sessions with hand-made labels and assert the metrics come
out where arithmetic says they should — including the two properties that matter
most: retrieval and verification are measured separately, and an empty gold set
produces no numbers at all rather than zeros.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def ev():
    spec = importlib.util.spec_from_file_location(
        "evaluate_gold", ROOT / "tools" / "evaluate_gold.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _row(claim_id, *, company, split, gold_rank, n_candidates=5, verdict="SUPPORTED",
         is_claim="yes", labeler="quynh"):
    """One session row whose correct answer is fixed by construction."""
    candidates = [
        {"rank": i, "evidence_id": f"{claim_id}-e{i}", "retrieval_score": 1.0 / i,
         "text": f"Kiểm kê: phát thải khí nhà kính năm 2024 là {100 - i} nghìn tấn CO2e."}
        for i in range(1, n_candidates + 1)
    ]
    return {
        "claim_id": claim_id,
        "company_id": company,
        "split": split,
        "text": "Phát thải khí nhà kính năm 2024 giảm 20% so với năm 2020.",
        "evidence_candidates": candidates,
        "labels": {
            "is_claim": is_claim,
            "attrs": {},
            "evidence": {f"{claim_id}-e{gold_rank}": "supports"},
            "verdict": verdict,
            "labeler": labeler,
            "labeled_at": "2026-09-25",
        },
    }


def _session(tmp_path: Path, rows: list[dict]) -> Path:
    path = tmp_path / "session.jsonl"
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    return path


# --- empty gold produces no numbers ------------------------------------------

def test_an_empty_gold_set_reports_nothing_rather_than_zeros(ev, tmp_path):
    blank = _row("c1", company="hpg", split="test", gold_rank=1)
    blank["labels"]["labeler"] = None
    rows = ev.load_rows([_session(tmp_path, [blank])], None)
    assert len(rows) == 1
    assert ev.adjudicated(rows) == []
    assert ev.retrieval_metrics([])["rows"] == 0
    assert ev.claim_metrics([])["rows"] == 0


# --- retrieval ----------------------------------------------------------------

def test_recall_and_mrr_follow_the_rank_of_the_gold_evidence(ev, tmp_path):
    """Gold at rank 3 of three claims: nothing at k=1, everything at k=3."""
    rows = ev.load_rows([_session(tmp_path, [
        _row("c1", company="a", split="test", gold_rank=3),
        _row("c2", company="b", split="test", gold_rank=1),
        _row("c3", company="c", split="test", gold_rank=5),
    ])], None)
    metrics = ev.retrieval_metrics(ev.adjudicated(rows))

    assert metrics["rows"] == 3
    assert metrics["recall_at"]["@1"]["mean"] == pytest.approx(1 / 3, abs=1e-4)
    assert metrics["recall_at"]["@3"]["mean"] == pytest.approx(2 / 3, abs=1e-4)
    assert metrics["recall_at"]["@5"]["mean"] == pytest.approx(1.0)
    # 1/3 + 1/1 + 1/5, averaged
    assert metrics["mrr"]["mean"] == pytest.approx((1 / 3 + 1 + 1 / 5) / 3, abs=1e-4)


def test_a_claim_whose_gold_evidence_was_never_retrieved_scores_zero(ev, tmp_path):
    row = _row("c1", company="a", split="test", gold_rank=1)
    row["labels"]["evidence"] = {"not-in-the-candidate-list": "supports"}
    metrics = ev.retrieval_metrics(ev.adjudicated(
        ev.load_rows([_session(tmp_path, [row])], None)
    ))
    assert metrics["recall_at"]["@30"]["mean"] == 0.0
    assert metrics["mrr"]["mean"] == 0.0


def test_a_label_keyed_by_the_rank_the_labeller_saw_is_scored(ev, tmp_path):
    """`label_session.py set evidence.3=supports` stores "3", not an evidence id.

    Before this was resolved, every row labelled with the CLI scored as "gold
    evidence never retrieved" and verification ran on no evidence at all.
    """
    row = _row("c1", company="a", split="test", gold_rank=1)
    row["labels"]["evidence"] = {"3": "supports", "1": "not_relevant"}
    rows = ev.adjudicated(ev.load_rows([_session(tmp_path, [row])], None))

    assert rows[0]["labels"]["evidence"] == {"c1-e3": "supports", "c1-e1": "not_relevant"}
    metrics = ev.retrieval_metrics(rows)
    assert metrics["recall_at"]["@3"]["mean"] == 1.0
    assert metrics["mrr"]["mean"] == pytest.approx(1 / 3, abs=1e-4)


# --- verification -------------------------------------------------------------

def test_verification_is_measured_on_the_evidence_a_human_chose(ev, tmp_path, settings):
    """Retrieval is taken out of the picture: only the verifier is under test."""
    rows = ev.load_rows([_session(tmp_path, [
        _row("c1", company="a", split="test", gold_rank=1, verdict="SUPPORTED"),
        _row("c2", company="b", split="test", gold_rank=2, verdict="CONTRADICTED"),
    ])], None)
    settings.runs_dir = str(tmp_path / "runs")
    metrics = ev.verification_metrics(ev.adjudicated(rows), settings)

    assert metrics["rows"] == 2
    assert set(metrics["confusion"]) <= set(ev.VERDICTS)
    assert 0.0 <= metrics["accuracy"]["mean"] <= 1.0
    # the error this product cares about most is always reported on its own
    assert "false_contradiction" in metrics
    assert metrics["abstention"]["coverage"] is not None


def test_false_contradiction_is_counted_separately_from_accuracy(ev):
    """Averaging this away is exactly what must not happen."""
    source = (ROOT / "tools" / "evaluate_gold.py").read_text(encoding="utf-8")
    assert 'predicted == "CONTRADICTED" and gold != "CONTRADICTED"' in source
    assert "macro_f1" in source and "false_contradiction" in source


# --- split hygiene ------------------------------------------------------------

def test_a_company_on_both_sides_of_a_split_is_reported(ev, tmp_path):
    """Without this check every number above is measuring memorisation."""
    rows = ev.load_rows([_session(tmp_path, [
        _row("c1", company="hpg", split="train", gold_rank=1),
        _row("c2", company="hpg", split="test", gold_rank=1),
        _row("c3", company="bvh", split="test", gold_rank=1),
    ])], None)
    report = ev.split_report(rows)
    assert report["companies"] == 2
    assert report["companies_in_more_than_one_split"] == {"hpg": ["test", "train"]}


def test_the_report_refuses_to_look_clean_when_a_company_straddles_splits(ev, tmp_path):
    rows = ev.load_rows([_session(tmp_path, [
        _row("c1", company="hpg", split="train", gold_rank=1),
        _row("c2", company="hpg", split="test", gold_rank=1),
    ])], None)
    text = "\n".join(ev.render({
        "date": "2026-09-25", "sessions": ["s"], "rows_total": len(rows),
        "rows_adjudicated": len(ev.adjudicated(rows)), "splits": ev.split_report(rows),
        "retrieval": {"rows": 0}, "verification": {"rows": 0}, "claims": {"rows": 0},
    }))
    assert "nằm ở nhiều split" in text and "không dùng được" in text


def test_a_train_company_split_by_year_is_the_design_not_a_leak(ev, tmp_path):
    """company_split.json holds companies out for test, then splits the rest by year.

    Flagging dhg for having train, dev and future_holdout rows would mark the
    very first real labelling batch unusable and hide an actual test leak.
    """
    rows = ev.load_rows([_session(tmp_path, [
        _row("c1", company="dhg", split="train", gold_rank=1),
        _row("c2", company="dhg", split="dev", gold_rank=1),
        _row("c3", company="dhg", split="future_holdout", gold_rank=1),
        _row("c4", company="pan", split="test", gold_rank=1),
    ])], None)
    assert ev.split_report(rows)["companies_in_more_than_one_split"] == {}


# --- small samples state their uncertainty ------------------------------------

def test_a_tiny_sample_says_so_instead_of_pretending_to_a_confidence_interval(ev):
    assert ev._mean_ci([1.0, 0.0])["ci95"] is None
    assert "quá ít mẫu" in ev._mean_ci([1.0, 0.0])["note"]
    wide = ev._mean_ci([1.0, 0.0, 1.0, 0.0, 1.0])
    assert wide["ci95"] and wide["ci95"][0] < wide["mean"] < wide["ci95"][1]


def test_claims_of_one_company_widen_the_interval(ev):
    """Resampling companies, not claims: one company's claims are not independent.

    Two companies the system gets right and one it gets entirely wrong give an
    interval that reaches far below the item-level one (review 2026-10-06).
    """
    values = [1.0] * 20 + [1.0] * 20 + [0.0] * 20
    groups = ["A"] * 20 + ["B"] * 20 + ["C"] * 20
    clustered = ev._cluster_mean_ci(values, groups)
    naive = ev._mean_ci(values)
    assert clustered["groups"] == 3
    assert clustered["ci95"][0] < naive["ci95"][0]
    assert ev._cluster_mean_ci(values[:40], groups[:40])["ci95"] is None  # two companies: withheld
