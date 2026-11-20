"""Precedent memory (feedback-loop-v1, tier 2): claims a person already decided, found again.

When a new claim reads like one a reviewer finalized before (same metric, same
phrasing, the same company's previous report), the earlier decision is shown
beside the verdict: who decided, what the machine had said, what the person
concluded and why. Nothing is trained and nothing is changed: the verdict still
comes from the rules. What changes is that reviewers stop deciding the same
question two different ways, and a claim like one where the machine was wrong
before can be raised into the review queue (feedback/queue.py).

Similarity is lexical (accent-folded word unigrams and bigrams, cosine), so the
memory runs on the 8 GB profile and its matches can be explained: the shared
words are the reason. Which labels a deployment may see is decided by
hygiene.visible_records (an organisation sees core labels and its own).
"""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from quantum_gw.storage.reviews import OVERRIDE, ReviewStore
from quantum_gw.utils.text import fold, normalize_text

from .hygiene import QAStore, visible_records

_WORD = re.compile(r"[0-9a-z]+(?:[.,][0-9]+)*%?")
# Words too common in Vietnamese report prose to say anything about which claim this is.
_STOP = frozenset(
    "va cua cac nhung la duoc trong voi cho tai tu den theo mot nay do da se dang co khong cung nhu "
    "the of and to in for on with by is are was were be has have had this that from at as an a".split()
)
# A reviewer's verdict read as the relation of the passage that decided it, for stance examples.
LABEL_TO_RELATION = {"SUPPORTED": "SUPPORTS", "PARTIALLY_SUPPORTED": "PARTIAL", "CONTRADICTED": "CONTRADICTS"}


def tokens(text: str) -> Counter:
    words = [w for w in _WORD.findall(fold(normalize_text(text or ""))) if w not in _STOP]
    grams = Counter(words)
    grams.update(f"{a}_{b}" for a, b in zip(words, words[1:]))
    return grams


def cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0) for k, v in a.items())
    if not dot:
        return 0.0
    return dot / (math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values())))


def _claim_text(claim: Any) -> str:
    return claim.get("text", "") if isinstance(claim, dict) else getattr(claim, "text", "") or ""


def _claim_field(claim: Any, name: str) -> Any:
    return claim.get(name) if isinstance(claim, dict) else getattr(claim, name, None)


def store_fingerprint(store: ReviewStore) -> dict:
    """What the manifest records about the memory a run consulted, so a run can be re-read later."""
    path = Path(store.path)
    if not path.is_file():
        return {"path": str(path), "records": 0, "sha256": None}
    content = path.read_bytes()
    return {"path": str(path), "records": content.count(b"\n"), "sha256": hashlib.sha256(content).hexdigest()}


class PrecedentIndex:
    def __init__(self, gold: list[dict]):
        self.records = [g for g in gold if g.get("claim_text") and g.get("label")]
        self._grams = [tokens(g["claim_text"]) for g in self.records]

    @classmethod
    def from_store(cls, store: ReviewStore | None = None, org_id: str = "",
                   qa: QAStore | None = None) -> PrecedentIndex:
        store = store or ReviewStore()
        qa_rows = (qa or QAStore(reviews=store)).all()
        return cls(visible_records(store.gold_records(), org_id, qa_rows))

    def __len__(self) -> int:
        return len(self.records)

    def find(self, claim: Any, k: int = 3, min_similarity: float = 0.55,
             exclude: tuple[str, str] | None = None) -> list[dict]:
        """The `k` most similar decided claims, most similar first, at or above `min_similarity`."""
        grams = tokens(_claim_text(claim))
        metric, claim_type = _claim_field(claim, "metric"), _claim_field(claim, "claim_type")
        scored = []
        for record, other in zip(self.records, self._grams):
            if exclude and (record["run_id"], record["claim_id"]) == exclude:
                continue
            similarity = cosine(grams, other)
            snapshot = record.get("claim") or {}
            # A small nudge for the same metric and claim type; the words carry the match.
            if metric and snapshot.get("metric") == metric:
                similarity += 0.05
            if claim_type and snapshot.get("claim_type") == claim_type:
                similarity += 0.03
            similarity = min(similarity, 1.0)
            if similarity >= min_similarity:
                scored.append((similarity, record, other))
        scored.sort(key=lambda item: -item[0])
        return [self._card(record, similarity, grams, other) for similarity, record, other in scored[:k]]

    @staticmethod
    def _card(record: dict, similarity: float, grams: Counter, other: Counter) -> dict:
        evidence = {e.get("chunk_id"): e for e in record.get("evidence_snapshot") or []}
        decisive = [
            {"chunk_id": cid, "source_name": evidence[cid].get("source_name"), "page": evidence[cid].get("page"),
             "text_preview": evidence[cid].get("text_preview")}
            for cid in record.get("decisive_chunk_ids") or [] if cid in evidence
        ]
        if record.get("decisive_quote"):
            decisive.append({"chunk_id": None, "source_name": "trích dẫn của người soát", "page": None,
                             "text_preview": record["decisive_quote"][:280]})
        shared = sorted((g for g in grams if g in other and "_" not in g), key=lambda g: -other[g])[:8]
        return {
            "run_id": record["run_id"], "claim_id": record["claim_id"], "claim_text": record["claim_text"],
            "decision": "OVERRIDE" if record.get("label_source") in ("human_override", "adjudicated")
            and record.get("label") != record.get("ai_status") else "CONFIRM",
            "ai_status": record.get("ai_status"), "label": record.get("label"),
            "overridden": record.get("label") != record.get("ai_status"),
            "override_reason": record.get("override_reason"), "error_stage": record.get("error_stage"),
            "rule_ref": record.get("rule_ref") or "", "comment": record.get("comment") or "",
            "reviewer": record.get("reviewer"), "reviewer_role": record.get("reviewer_role") or "",
            "reviewer_org": record.get("reviewer_org") or "", "decided_at": record.get("decided_at"),
            "similarity": round(similarity, 3), "shared_words": shared, "decisive": decisive,
        }

    def stance_examples(self, claim_text: str, k: int = 2, min_similarity: float = 0.35) -> list[dict]:
        """Pointer-labelled precedents as (claim, passage, relation) examples for the stance model (S5).

        Only labels that say which passage decided the case qualify: a verdict alone does
        not say what any one passage means. Unsupported / insufficient verdicts are left
        out because "no passage supports it" names no passage.
        """
        out = []
        for score, record in self._ranked_with_records(claim_text, min_similarity):
            relation = LABEL_TO_RELATION.get(record.get("label") or "")
            if relation is None or not record.get("train_eligible"):
                continue
            passage = _decisive_text(record)
            if not passage:
                continue
            out.append({"ref": f"{record['run_id']}:{record['claim_id']}", "claim": record["claim_text"],
                        "passage": passage[:600], "relation": relation, "similarity": score})
            if len(out) >= k:
                break
        return out

    def _ranked_with_records(self, claim_text: str, min_similarity: float):
        grams = tokens(claim_text)
        scored = sorted(
            ((cosine(grams, other), record) for record, other in zip(self.records, self._grams)),
            key=lambda item: -item[0],
        )
        return [(round(s, 3), r) for s, r in scored if s >= min_similarity]


def _decisive_text(record: dict) -> str:
    evidence = {e.get("chunk_id"): e for e in record.get("evidence_snapshot") or []}
    for cid in record.get("decisive_chunk_ids") or []:
        item = evidence.get(cid)
        if item:
            return item.get("text") or item.get("text_preview") or ""
    return record.get("decisive_quote") or ""


def overridden_precedents(cards: list[dict], min_similarity: float) -> list[dict]:
    """Precedents close enough, where a person overrode the machine: the ones worth a queue place."""
    return [c for c in cards if c["overridden"] and c["similarity"] >= min_similarity]


__all__ = ["PrecedentIndex", "overridden_precedents", "store_fingerprint", "tokens", "cosine", "OVERRIDE"]
