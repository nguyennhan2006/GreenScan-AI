"""Raise items into the review queue; never take one out (feedback-loop-v1).

Three things may put a claim in front of a reviewer that the risk score alone
left out:

* an org rule whose `on_fail` is `raise_priority` came out VIOLATION or
  NEEDS_REVIEW (an approved pack only: a draft pack's rules are NOT_APPLICABLE);
* a precedent: a person overrode the machine on a very similar claim;
* active learning: one of the `slots` items whose label would teach most.

The priority score and the rank are left exactly as the policy computed them;
only `in_queue` may turn true, and `raised_by` says why. An item already queued
keeps its place and gains the reason. Nothing is removed and no verdict, risk
score or release status is read or written.
"""

from __future__ import annotations

RAISE = "raise_priority"


def audit_sample(priorities, run_id: str, size: int) -> list[str]:
    """Mark `size` claims outside the queue for a person to read (audit-sample-v1, expert review 15/11/2026).

    The draw is deterministic -- ordered by sha1 of the claim id, which is stable across runs of the same documents
    (run ids are random) -- so a re-run marks the same claims. Nothing about the queue changes: the sample is read beside it, and a reviewer who finds a claim
    that should have been queued has measured a miss (0 misses in n reads bounds the miss rate near 3/n).
    """
    import hashlib

    if size <= 0:
        return []
    outside = [p for p in priorities if p.item_type == "claim" and not p.in_queue]
    outside.sort(key=lambda p: hashlib.sha1(f"audit-sample-v1:{p.item_id}".encode()).hexdigest())
    for p in outside[:size]:
        p.audit_sample = True
    return [p.item_id for p in outside[:size]]


QUEUE_OUTCOMES = ("VIOLATION", "NEEDS_REVIEW")


def raise_queue(priorities, *, org_findings: list[dict] | None = None, precedents: dict[str, list] | None = None,
                precedent_similarity: float = 0.75, learning: dict[str, dict] | None = None,
                slots: int = 0, flags: dict[str, list[str]] | None = None) -> dict:
    by_id = {p.item_id: p for p in priorities if p.item_type == "claim"}
    reasons: dict[str, list[str]] = {}

    # A verifier review flag (internal_inconsistency, absolute_claim_conflict) asks for a person by itself.
    for claim_id, names in (flags or {}).items():
        for name in names:
            reasons.setdefault(claim_id, []).append(f"flag:{name}")

    for record in org_findings or []:
        for finding in record.get("findings", []):
            if finding.get("on_fail") == RAISE and finding.get("outcome") in QUEUE_OUTCOMES:
                reasons.setdefault(record["claim_id"], []).append(
                    f"org_rule:{finding.get('org_id')}/{finding.get('rule_id')}")

    for claim_id, cards in (precedents or {}).items():
        for card in cards:
            if card.get("overridden") and card.get("similarity", 0) >= precedent_similarity:
                reasons.setdefault(claim_id, []).append(f"precedent:{card['run_id']}/{card['claim_id']}")
                break

    if slots and learning:
        ranked = sorted(
            (cid for cid, item in learning.items()
             if cid in by_id and not by_id[cid].in_queue and cid not in reasons and item["value"] >= 0.3),
            key=lambda cid: -learning[cid]["value"],
        )
        for claim_id in ranked[:slots]:
            reasons.setdefault(claim_id, []).append("active_learning")

    raised, already = [], []
    for claim_id, why in reasons.items():
        priority = by_id.get(claim_id)
        if priority is None:
            continue
        (already if priority.in_queue else raised).append(claim_id)
        priority.in_queue = True
        priority.raised_by = list(dict.fromkeys([*priority.raised_by, *why]))
    return {"raised": len(raised), "already_queued": len(already),
            "by_reason": {kind: sum(1 for why in reasons.values() if any(w.startswith(kind) for w in why))
                          for kind in ("org_rule", "precedent", "active_learning", "flag")}}
