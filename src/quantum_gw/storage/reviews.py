"""Append-only store for human review decisions.

Two jobs at once, which is why the record is heavier than a status field:

1. **Audit trail.** Who decided what, when, on which evidence, and what the state
   was before. Append-only: a decision is never edited, it is superseded by a
   later one. Mutation would destroy the only thing that makes the trail worth
   keeping.
2. **Gold dataset.** Each finalized decision is a human-adjudicated label. The
   evidence snapshot is what makes it survive: retrieval changes between runs,
   so a label that only referenced chunk ids would silently come to mean
   something else. The snapshot records what the reviewer actually saw.

The state machine is deliberately small:

    AI_SUGGESTED -> HUMAN_REVIEWED -> FINALIZED

`FINALIZED` can be reopened to `HUMAN_REVIEWED`; nothing may skip straight from
`AI_SUGGESTED` to `FINALIZED`, because that would record a human sign-off that
no human made.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from quantum_gw.utils.jsonl import dumps, read_jsonl

# Workflow states.
AI_SUGGESTED = "AI_SUGGESTED"
HUMAN_REVIEWED = "HUMAN_REVIEWED"
FINALIZED = "FINALIZED"
STATES = (AI_SUGGESTED, HUMAN_REVIEWED, FINALIZED)

# What a reviewer can do.
CONFIRM = "CONFIRM"                    # AI verdict is right
OVERRIDE = "OVERRIDE"                  # AI verdict is wrong; reviewer supplies the verdict
ABSTAIN = "ABSTAIN"                    # evidence genuinely insufficient to decide
REQUEST_EVIDENCE = "REQUEST_EVIDENCE"  # decidable, but needs a document we do not have
REOPEN = "REOPEN"                      # undo a finalization
DECISIONS = (CONFIRM, OVERRIDE, ABSTAIN, REQUEST_EVIDENCE, REOPEN)

# decision -> state it moves the claim into.
_TRANSITIONS = {
    CONFIRM: FINALIZED,
    OVERRIDE: FINALIZED,
    ABSTAIN: HUMAN_REVIEWED,
    REQUEST_EVIDENCE: HUMAN_REVIEWED,
    REOPEN: HUMAN_REVIEWED,
}

# Only these are gold-quality: a human looked and committed to a verdict.
GOLD_DECISIONS = (CONFIRM, OVERRIDE)

class ReviewError(ValueError):
    """Invalid decision, reviewer, or state transition."""


@dataclass(frozen=True)
class ReviewRecord:
    decision_id: str
    run_id: str
    claim_id: str
    reviewer: str
    decided_at: str
    decision: str
    previous_state: str
    new_state: str
    comment: str = ""
    ai_status: str | None = None
    ai_risk_score: float | None = None
    reviewer_status: str | None = None
    evidence_snapshot: list[dict[str, Any]] = field(default_factory=list)
    claim_snapshot: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict:
        return asdict(self)


def snapshot_evidence(evidence: list[dict] | None) -> list[dict]:
    """Freeze what the reviewer saw.

    Retrieval is not stable across runs — reranking, chunking and corpus changes
    all move results. Hashing the text means a later run can detect that the
    passage behind a label has changed, instead of silently relabelling it.
    """
    out = []
    for item in evidence or []:
        text = item.get("text") or ""
        out.append({
            "chunk_id": item.get("chunk_id"),
            "doc_id": item.get("doc_id"),
            "source_name": item.get("source_name"),
            "page": item.get("page"),
            "relation": item.get("relation"),
            "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "text_preview": text[:280],
        })
    return out


class ReviewStore:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(
            path or os.environ.get("QUANTUM_REVIEWS_FILE", ".quantum/reviews/decisions.jsonl")
        )

    # ---------- write ----------

    def record(
        self,
        *,
        run_id: str,
        claim_id: str,
        reviewer: str,
        decision: str,
        comment: str = "",
        reviewer_status: str | None = None,
        ai_status: str | None = None,
        ai_risk_score: float | None = None,
        evidence: list[dict] | None = None,
        claim: dict | None = None,
    ) -> ReviewRecord:
        decision = (decision or "").strip().upper()
        reviewer = (reviewer or "").strip()
        if decision not in DECISIONS:
            raise ReviewError(f"Unknown decision {decision!r}; expected one of {DECISIONS}")
        if not reviewer:
            raise ReviewError("reviewer is required — an audit trail without an author is not one")
        if decision == OVERRIDE and not reviewer_status:
            raise ReviewError("OVERRIDE requires reviewer_status: the verdict replacing the AI one")

        previous = self.state_of(run_id, claim_id)
        if decision == REOPEN and previous != FINALIZED:
            raise ReviewError(f"REOPEN only applies to a FINALIZED claim (currently {previous})")
        if decision in {CONFIRM, OVERRIDE} and previous == FINALIZED:
            raise ReviewError("Claim is already FINALIZED; REOPEN before deciding again")

        record = ReviewRecord(
            decision_id=uuid.uuid4().hex[:16],
            run_id=run_id,
            claim_id=claim_id,
            reviewer=reviewer,
            decided_at=datetime.now(UTC).isoformat(),
            decision=decision,
            previous_state=previous,
            new_state=_TRANSITIONS[decision],
            comment=comment.strip(),
            ai_status=ai_status,
            ai_risk_score=ai_risk_score,
            reviewer_status=reviewer_status,
            evidence_snapshot=snapshot_evidence(evidence),
            claim_snapshot=claim or {},
        )
        self._append(record)
        return record

    def _append(self, record: ReviewRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(dumps(record.to_json()) + "\n")

    # ---------- read ----------

    def all(self) -> list[dict]:
        return read_jsonl(self.path)

    def history(self, run_id: str, claim_id: str) -> list[dict]:
        """Every decision for this claim, oldest first."""
        return [r for r in self.all() if r["run_id"] == run_id and r["claim_id"] == claim_id]

    def latest(self, run_id: str, claim_id: str) -> dict | None:
        h = self.history(run_id, claim_id)
        return h[-1] if h else None

    def state_of(self, run_id: str, claim_id: str) -> str:
        last = self.latest(run_id, claim_id)
        return last["new_state"] if last else AI_SUGGESTED

    def states_for_run(self, run_id: str) -> dict[str, str]:
        states: dict[str, str] = {}
        for r in self.all():
            if r["run_id"] == run_id:
                states[r["claim_id"]] = r["new_state"]
        return states

    # ---------- dataset ----------

    def gold_records(self) -> list[dict]:
        """Human-adjudicated labels, one per claim, latest decision wins.

        Only CONFIRM/OVERRIDE qualify. ABSTAIN and REQUEST_EVIDENCE are real
        workflow outcomes but they are not labels — treating them as such would
        teach a model that "we could not tell" is a verdict.
        """
        latest: dict[tuple[str, str], dict] = {}
        for r in self.all():
            latest[(r["run_id"], r["claim_id"])] = r
        out = []
        for r in latest.values():
            if r["decision"] not in GOLD_DECISIONS or r["new_state"] != FINALIZED:
                continue
            out.append({
                "run_id": r["run_id"],
                "claim_id": r["claim_id"],
                "claim_text": (r.get("claim_snapshot") or {}).get("text"),
                "label": r.get("reviewer_status") or r.get("ai_status"),
                "label_source": "human_override" if r["decision"] == OVERRIDE else "human_confirmed",
                "ai_status": r.get("ai_status"),
                "reviewer": r["reviewer"],
                "decided_at": r["decided_at"],
                "comment": r.get("comment", ""),
                "evidence_snapshot": r.get("evidence_snapshot", []),
            })
        return out

    def stats(self) -> dict:
        rows = self.all()
        by_decision: dict[str, int] = {}
        by_state: dict[str, int] = {}
        for r in rows:
            by_decision[r["decision"]] = by_decision.get(r["decision"], 0) + 1
        for state in {(r["run_id"], r["claim_id"]): r["new_state"] for r in rows}.values():
            by_state[state] = by_state.get(state, 0) + 1
        overrides = by_decision.get(OVERRIDE, 0)
        finalized = overrides + by_decision.get(CONFIRM, 0)
        return {
            "total_decisions": len(rows),
            "claims_touched": len({(r["run_id"], r["claim_id"]) for r in rows}),
            "by_decision": by_decision,
            "by_state": by_state,
            "reviewers": sorted({r["reviewer"] for r in rows}),
            "gold_records": len(self.gold_records()),
            # How often the AI verdict was wrong where a human committed — the
            # single most honest quality number this store can produce.
            "ai_override_rate": round(overrides / finalized, 4) if finalized else None,
        }
