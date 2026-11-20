"""GS-Feedback (feedback-loop-v1, tier 1): every finalized decision becomes a frozen regression case.

A case is the claim the reviewer saw, the evidence the reviewer saw (the text
kept in the decision's evidence snapshot) and the reviewer's verdict. Running
the bench re-verifies each claim against that frozen evidence with the current
rules, so retrieval drift cannot move a case: only a change in how the system
*reads* can.

The ratchet is what makes the system stop forgetting. `ratchet.json` lists the
cases that pass. A later run in which a listed case fails is a regression and
the bench exits non-zero; a case that starts passing is added only when someone
asks (`--update-ratchet`), so the list grows by decision and never shrinks by
accident. A case the machine got wrong and still gets wrong is not a regression:
it is the to-do list.

Old decisions kept only a 280-character preview of each passage. Such cases are
run on the preview and marked `evidence_truncated`, so a reader can discount them.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import Claim, EvidenceChunk, RetrievedEvidence

from .hygiene import SCOPE_CORE, QAStore, clean_labels, key_of

BENCH_DIR = Path("benchmark/gs_feedback")
CASES_FILE = BENCH_DIR / "cases.jsonl"
RATCHET_FILE = BENCH_DIR / "ratchet.json"
SCHEMA = "gs-feedback-v1"


class _NoAudit:
    def write(self, event: str, payload: dict | None = None) -> None:
        return None


def _run_corpus(run_id: str, cache: dict) -> dict | None:
    """The corpus profile of the run a decision was made on, read from its saved result, if it is still there.

    The verifier may call a claim UNSUPPORTED only when it knows what was searched
    (agents/corpus.py); without the profile a re-run can only say INSUFFICIENT_EVIDENCE.
    """
    if run_id not in cache:
        cache[run_id] = None
        try:
            from quantum_gw.settings import load_settings

            result = Path(load_settings().runs_dir) / run_id / "result.json"
            if result.is_file():
                cache[run_id] = json.loads(result.read_text(encoding="utf-8")).get("corpus") or None
        except Exception:  # noqa: BLE001 - a missing run only makes the case weaker, not broken
            cache[run_id] = None
    return cache[run_id]


def build_cases(gold: list[dict], qa: list[dict] | None = None, scope: str = SCOPE_CORE) -> list[dict]:
    """Clean labels (hygiene.clean_labels) that carry enough to be re-run: a claim and its evidence."""
    cases, corpora = [], {}
    for g in clean_labels(gold, qa, scope):
        claim = dict(g.get("claim") or {})
        text = claim.get("text") or g.get("claim_text")
        if not text or not g.get("label"):
            continue
        claim["text"] = text
        evidence = g.get("evidence_snapshot") or []
        cases.append({
            "schema": SCHEMA,
            "case_id": key_of(g),
            "label": g["label"],
            "label_source": g.get("label_source"),
            "ai_status_then": g.get("ai_status"),
            "error_stage": g.get("error_stage"),
            "override_reason": g.get("override_reason"),
            "reviewer": g.get("reviewer"),
            "decided_at": g.get("decided_at"),
            "rule_context": g.get("rule_context") or {},
            "claim": claim,
            "evidence": evidence,
            "evidence_truncated": any(not e.get("text") for e in evidence),
            "corpus": _run_corpus(g["run_id"], corpora),
        })
    return cases


def write_cases(cases: list[dict], path: str | Path = CASES_FILE) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases), encoding="utf-8")
    return path


def read_cases(path: str | Path = CASES_FILE) -> list[dict]:
    path = Path(path)
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _claim(snapshot: dict, extractor) -> Claim:
    try:
        return Claim.model_validate(snapshot)
    except ValidationError:
        # Old decisions kept only the sentence: rebuild the attributes production would give it.
        chunk = EvidenceChunk(chunk_id="gs-feedback", doc_id="gs-feedback",
                              source_name=snapshot.get("source_name") or "gs-feedback",
                              role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL,
                              text=snapshot["text"])
        return extractor.describe(snapshot["text"], chunk)


def _evidence(snapshot: list[dict]) -> list[RetrievedEvidence]:
    out = []
    for index, e in enumerate(snapshot, start=1):
        text = e.get("text") or e.get("text_preview") or ""
        if not text:
            continue
        try:
            source_type = SourceType(e.get("source_type") or "internal")
        except ValueError:
            source_type = SourceType.INTERNAL
        name = e.get("source_name") or "?"
        out.append(RetrievedEvidence(
            chunk_id=e.get("chunk_id") or f"snapshot-{index}", doc_id=e.get("doc_id") or "",
            source_name=name, source_type=source_type, text=text, page=e.get("page"),
            score=float(e.get("score") or 0.0),
            citation=name + (f" tr. {e['page']}" if e.get("page") else ""),
        ))
    return out


def run_cases(cases: list[dict], settings: Any = None, lexicon: Any = None) -> list[dict]:
    """Re-verify every case on its frozen evidence with the current rules (no model is consulted)."""
    from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
    from quantum_gw.agents.verifier import VerificationAgent
    from quantum_gw.settings import load_settings

    settings = settings or load_settings()
    verification_settings = settings.verification.model_copy(update={"llm_stance": "off"})
    verifier = VerificationAgent(verification_settings, _NoAudit(), lexicon=lexicon)
    extractor = ClaimExtractionAgent(settings.claim_extraction, _NoAudit())
    from quantum_gw.agents.corpus import CorpusProfile

    results = []
    for case in cases:
        try:
            verifier.corpus = CorpusProfile(**case["corpus"]) if case.get("corpus") else None
            result = verifier.run(_claim(case["claim"], extractor), _evidence(case["evidence"]))
            predicted, error = result.status.value, None
        except Exception as exc:  # noqa: BLE001 - one broken case must not hide the others
            predicted, error = None, f"{type(exc).__name__}: {exc}"[:200]
        results.append({
            "case_id": case["case_id"], "label": case["label"], "predicted": predicted,
            "ai_status_then": case.get("ai_status_then"), "passed": predicted == case["label"],
            "error_stage": case.get("error_stage"), "evidence_truncated": case.get("evidence_truncated", False),
            "error": error,
        })
    return results


def read_ratchet(path: str | Path = RATCHET_FILE) -> dict:
    path = Path(path)
    if not path.is_file():
        return {"schema": SCHEMA, "passing": [], "history": []}
    return json.loads(path.read_text(encoding="utf-8"))


def check_ratchet(results: list[dict], path: str | Path = RATCHET_FILE, update: bool = False,
                  note: str = "") -> dict:
    """Regressions against the ratchet, newly passing cases, and (with `update`) the ratchet grown by them."""
    ratchet = read_ratchet(path)
    passing_before = set(ratchet.get("passing", []))
    present = {r["case_id"] for r in results}
    passing_now = {r["case_id"] for r in results if r["passed"]}
    regressions = sorted(c for c in passing_before & present if c not in passing_now)
    newly = sorted(passing_now - passing_before)
    report = {
        "cases": len(results),
        "passed": len(passing_now),
        "failed": len(results) - len(passing_now),
        "pass_rate": round(len(passing_now) / len(results), 4) if results else None,
        "machine_then_right": sum(1 for r in results if r["ai_status_then"] == r["label"]),
        "fixed_since_decision": sorted(r["case_id"] for r in results if r["passed"] and r["ai_status_then"] != r["label"]),
        "by_stage": {stage: {"cases": n, "passed": sum(1 for r in results if r["error_stage"] == stage and r["passed"])}
                     for stage, n in Counter(r["error_stage"] for r in results).items()},
        "ratchet_size": len(passing_before),
        "regressions": regressions,
        "newly_passing": newly,
        "missing_from_bench": sorted(passing_before - present),
        "truncated_cases": sum(1 for r in results if r["evidence_truncated"]),
    }
    if update and not regressions:
        ratchet["passing"] = sorted(passing_before | passing_now)
        ratchet.setdefault("history", []).append({
            "at": datetime.now(UTC).isoformat(), "added": newly, "size": len(ratchet["passing"]), "note": note,
        })
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(ratchet, ensure_ascii=False, indent=2), encoding="utf-8")
        report["ratchet_updated"] = True
    else:
        report["ratchet_updated"] = False
    return report


def export_from_store(store=None, qa: QAStore | None = None, path: str | Path = CASES_FILE,
                      scope: str = SCOPE_CORE) -> tuple[Path, int]:
    from quantum_gw.storage.reviews import ReviewStore

    store = store or ReviewStore()
    cases = build_cases(store.gold_records(), (qa or QAStore(reviews=store)).all(), scope)
    return write_cases(cases, path), len(cases)
