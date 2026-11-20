"""Label hygiene: which human labels may teach, score or be shown, and to whom.

Three filters, each with a reason that is about trust rather than statistics:

* **The checked party does not teach the checker.** A label whose reviewer role
  is `reviewed_company` stays in the audit trail and is never train-eligible
  (storage/reviews.py sets `train_eligible`).
* **A disagreement is not a label.** A sample of finalized decisions is
  re-decided blind by a second reviewer. Where the two differ the label is held
  out of training and scoring until an adjudicator decides; the adjudicated
  verdict then replaces it. Agreement is reported as Cohen's kappa.
* **An organisation's labels stay with it.** A label written by reviewers of
  organisation X is visible to X (precedents, its own dataset). It reaches the
  core memory, which every deployment learns from, only when the GreenScan team
  promotes it by name. Labels with no organisation belong to the deployment
  itself and count as core.

The QA file (second reviews, adjudications, promotions) is append-only, like
the decision store, and lives next to it.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from quantum_gw.storage.reviews import ReviewError, ReviewStore
from quantum_gw.utils.jsonl import dumps, read_jsonl

STATUSES = ("SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE")
SECOND_REVIEW = "second_review"
ADJUDICATION = "adjudication"
CORE_PROMOTION = "core_promotion"
KINDS = (SECOND_REVIEW, ADJUDICATION, CORE_PROMOTION)

SCOPE_CORE = "core"


def key_of(record: dict) -> str:
    return f"{record['run_id']}:{record['claim_id']}"


class QAStore:
    """Append-only second reviews, adjudications and core promotions."""

    def __init__(self, path: str | Path | None = None, reviews: ReviewStore | None = None):
        if path is None:
            path = os.environ.get("QUANTUM_QA_FILE") or (Path((reviews or ReviewStore()).path).parent / "qa.jsonl")
        self.path = Path(path)

    def all(self) -> list[dict]:
        return read_jsonl(self.path)

    def _append(self, record: dict) -> dict:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(dumps(record) + "\n")
        return record

    def _base(self, kind: str, run_id: str, claim_id: str, by: str, comment: str) -> dict:
        by = (by or "").strip()
        if not by:
            raise ReviewError("a QA record needs the name of the person who made it")
        return {"qa_id": uuid.uuid4().hex[:16], "kind": kind, "run_id": run_id, "claim_id": claim_id,
                "by": by, "at": datetime.now(UTC).isoformat(), "comment": (comment or "").strip()}

    def record_second(self, *, run_id: str, claim_id: str, reviewer: str, status: str,
                      first_reviewer: str, comment: str = "") -> dict:
        """A blind second decision on a finalized claim. Must come from someone else."""
        status = (status or "").strip().upper()
        if status not in STATUSES:
            raise ReviewError(f"status must be one of {STATUSES}")
        if (reviewer or "").strip().casefold() == (first_reviewer or "").strip().casefold():
            raise ReviewError("the second review must come from a different person than the first")
        return self._append({**self._base(SECOND_REVIEW, run_id, claim_id, reviewer, comment), "status": status})

    def record_adjudication(self, *, run_id: str, claim_id: str, adjudicator: str, status: str,
                            comment: str = "") -> dict:
        status = (status or "").strip().upper()
        if status not in STATUSES:
            raise ReviewError(f"status must be one of {STATUSES}")
        return self._append({**self._base(ADJUDICATION, run_id, claim_id, adjudicator, comment), "status": status})

    def promote_to_core(self, *, run_id: str, claim_id: str, approved_by: str, comment: str = "") -> dict:
        """Move one organisation's label into the core memory every deployment learns from."""
        return self._append(self._base(CORE_PROMOTION, run_id, claim_id, approved_by, comment))


def sample_for_second_review(gold: list[dict], rate: float = 0.10, seed: str = "") -> list[dict]:
    """A deterministic sample of finalized labels: the same seed gives the same sample.

    The seed is meant to be the month ("2026-11"), so each month draws a fresh sample
    and anyone can recompute which claims were drawn.
    """
    seed = seed or datetime.now(UTC).strftime("%Y-%m")
    out = []
    for g in gold:
        digest = hashlib.sha256(f"{seed}|{key_of(g)}".encode()).digest()
        if int.from_bytes(digest[:8], "big") / 2**64 < rate:
            out.append({"run_id": g["run_id"], "claim_id": g["claim_id"], "claim_text": g.get("claim_text"),
                        "first_reviewer": g.get("reviewer"), "seed": seed})
    return out


def cohen_kappa(pairs: list[tuple[str, str]]) -> float | None:
    """Agreement beyond chance between two raters over the five statuses; None without pairs."""
    if not pairs:
        return None
    n = len(pairs)
    observed = sum(1 for a, b in pairs if a == b) / n
    first = Counter(a for a, _ in pairs)
    second = Counter(b for _, b in pairs)
    expected = sum(first[c] * second[c] for c in set(first) | set(second)) / (n * n)
    if expected >= 1.0:
        return 1.0 if observed >= 1.0 else 0.0
    return round((observed - expected) / (1 - expected), 4)


def agreement(gold: list[dict], qa: list[dict]) -> dict:
    """First vs second reviewer on the doubly-reviewed labels, and what is still unresolved."""
    labels = {key_of(g): g for g in gold}
    seconds: dict[str, dict] = {}
    adjudicated: dict[str, dict] = {}
    for r in qa:
        if r["kind"] == SECOND_REVIEW:
            seconds[key_of(r)] = r
        elif r["kind"] == ADJUDICATION:
            adjudicated[key_of(r)] = r
    pairs, disagreements = [], []
    for key, second in seconds.items():
        first = labels.get(key)
        if first is None or not first.get("label"):
            continue
        pairs.append((first["label"], second["status"]))
        if first["label"] != second["status"]:
            disagreements.append({
                "run_id": first["run_id"], "claim_id": first["claim_id"], "claim_text": first.get("claim_text"),
                "first": first["label"], "first_reviewer": first.get("reviewer"),
                "second": second["status"], "second_reviewer": second["by"],
                "adjudicated": adjudicated.get(key, {}).get("status"),
            })
    return {
        "double_reviewed": len(pairs),
        "agree": sum(1 for a, b in pairs if a == b),
        "kappa": cohen_kappa(pairs),
        "disagreements": disagreements,
        "unresolved": [d for d in disagreements if not d["adjudicated"]],
    }


def promoted_keys(qa: list[dict]) -> set[str]:
    return {key_of(r) for r in qa if r["kind"] == CORE_PROMOTION}


def in_scope(record: dict, scope: str, promoted: set[str]) -> bool:
    """`core`: labels with no organisation, or promoted. `org:<id>`: core plus that organisation's own."""
    org = record.get("reviewer_org") or ""
    if not org or key_of(record) in promoted or record.get("reviewer_role") == "greenscan":
        return True
    return scope.startswith("org:") and org == scope[4:]


def clean_labels(gold: list[dict], qa: list[dict] | None = None, scope: str = SCOPE_CORE) -> list[dict]:
    """The labels that may train or score a model in `scope`, with adjudications applied.

    Dropped: labels that are not train-eligible (rule feedback, the checked company's
    own labels), labels whose second review disagrees and has not been adjudicated,
    and labels outside the scope. An adjudicated label carries the adjudicator's verdict.
    """
    qa = qa or []
    promoted = promoted_keys(qa)
    report = agreement(gold, qa)
    unresolved = {f"{d['run_id']}:{d['claim_id']}" for d in report["unresolved"]}
    adjudicated = {key_of(r): r for r in qa if r["kind"] == ADJUDICATION}
    out = []
    for g in gold:
        key = key_of(g)
        if not g.get("train_eligible") or key in unresolved or not in_scope(g, scope, promoted):
            continue
        if key in adjudicated:
            g = {**g, "label": adjudicated[key]["status"], "label_source": "adjudicated",
                 "adjudicator": adjudicated[key]["by"]}
        out.append(g)
    return out


def visible_records(gold: list[dict], org_id: str, qa: list[dict] | None = None) -> list[dict]:
    """What a deployment configured for `org_id` may be shown as precedents."""
    promoted = promoted_keys(qa or [])
    scope = f"org:{org_id}" if org_id else SCOPE_CORE
    return [g for g in gold if in_scope(g, scope, promoted)]
