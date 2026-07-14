from __future__ import annotations

from quantum_gw.domain.models import Claim, EvidenceChunk, RetrievedEvidence
from quantum_gw.retrieval.hybrid import HybridRetriever
from quantum_gw.settings import RetrievalSettings
from quantum_gw.storage.audit import AuditLogger


class EvidenceRetrievalAgent:
    def __init__(self, chunks: list[EvidenceChunk], settings: RetrievalSettings, audit: AuditLogger):
        self.retriever = HybridRetriever(chunks, settings)
        self.audit = audit

    def run(self, claim: Claim) -> list[RetrievedEvidence]:
        evidence = self.retriever.search(claim)
        self.audit.write(
            "evidence_retrieved",
            {"claim_id": claim.claim_id, "count": len(evidence), "scores": [e.score for e in evidence]},
        )
        return evidence
