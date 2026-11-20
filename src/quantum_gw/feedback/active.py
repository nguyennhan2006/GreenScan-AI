"""Active learning (feedback-loop-v1): which items a reviewer's label would teach most.

The review queue answers "where is the risk"; this answers "where is the
machine least sure, or least taught". Each claim gets a learning value in
[0, 1] with its reasons, and `feedback.active_learning_slots` extra queue places
go to the highest values not already queued (feedback/queue.py). The value is
shown with its reasons, so a reviewer knows why an item was put in front of them.

Components (each a reason a person can check):
  conflicting evidence      0.35  passages that support and passages that refute
  rules could not decide    0.25  the verifier wanted a model's reading
  shadow model disagrees    0.30  the trained challenger reads a passage differently
  few labels of this type   0.20  fewer than RARE labelled claims of this claim type
  no precedent              0.10  nobody has decided a similar claim yet
"""

from __future__ import annotations

from collections import Counter

RARE = 5
WEIGHTS = {"conflict": 0.35, "undecided": 0.25, "shadow": 0.30, "rare": 0.20, "no_precedent": 0.10}


def label_counts(clean_labels: list[dict]) -> Counter:
    return Counter((g.get("claim") or {}).get("claim_type") or "unknown" for g in clean_labels)


def learning_values(verifications, precedents: dict[str, list] | None = None, counts: Counter | None = None,
                    shadow_by_claim: dict[str, int] | None = None) -> dict[str, dict]:
    precedents = precedents or {}
    counts = counts or Counter()
    shadow_by_claim = shadow_by_claim or {}
    out = {}
    for verification in verifications:
        claim = verification.claim
        relations = {getattr(e, "relation", None) for e in verification.evidence[:5]}
        value, reasons = 0.0, []
        if relations & {"SUPPORTS", "PARTIAL"} and "CONTRADICTS" in relations:
            value += WEIGHTS["conflict"]
            reasons.append("bằng chứng trái chiều: có đoạn ủng hộ và có đoạn bác bỏ")
        if verification.requires_llm_review:
            value += WEIGHTS["undecided"]
            reasons.append("luật chưa quyết được, cần người hoặc mô hình đọc")
        if shadow_by_claim.get(claim.claim_id):
            value += WEIGHTS["shadow"]
            reasons.append(f"mô hình thử nghiệm đọc khác luật ở {shadow_by_claim[claim.claim_id]} đoạn")
        n = counts.get(claim.claim_type or "unknown", 0)
        if n < RARE:
            value += WEIGHTS["rare"]
            reasons.append(f"loại tuyên bố “{claim.claim_type}” mới có {n} nhãn")
        if not precedents.get(claim.claim_id):
            value += WEIGHTS["no_precedent"]
            reasons.append("chưa có tiền lệ tương tự")
        out[claim.claim_id] = {"value": round(min(value, 1.0), 2), "reasons": reasons}
    return out
