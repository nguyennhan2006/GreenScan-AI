from __future__ import annotations

import hashlib
import json
import uuid
from collections import Counter
from pathlib import Path

from quantum_gw.domain.enums import Severity
from quantum_gw.domain.models import (
    AnalysisResult,
    AnalysisSummary,
    DocumentInput,
    RunManifest,
)
from quantum_gw.settings import AppSettings, load_settings
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.utils.text import file_sha256

from .claim_extractor import ClaimExtractionAgent
from .intake import DocumentIntakeAgent
from .reporter import ReportingAgent
from .retriever import EvidenceRetrievalAgent
from .reviewer import ReviewerAgent
from .scorer import RiskScoringAgent
from .verifier import VerificationAgent


class OrchestratorAgent:
    PLAN = [
        "validate_inputs",
        "parse_and_ocr_documents",
        "extract_green_claims",
        "build_hybrid_retrieval_index",
        "retrieve_evidence_per_claim",
        "verify_claim_evidence_pairs",
        "score_greenwashing_risk",
        "apply_quality_gates",
        "write_evidence_pack",
    ]

    def __init__(self, settings: AppSettings | None = None):
        self.settings = settings or load_settings()

    def run(self, documents: list[DocumentInput]) -> AnalysisResult:
        if not documents:
            raise ValueError("At least one document is required")
        run_id = uuid.uuid4().hex[:16]
        output_dir = Path(self.settings.runs_dir) / run_id
        output_dir.mkdir(parents=True, exist_ok=True)
        audit = AuditLogger(output_dir / "audit.jsonl")
        audit.write("run_started", {"run_id": run_id, "plan": self.PLAN})

        manifest = RunManifest(
            run_id=run_id,
            pipeline_version=self.settings.version,
            config_hash=self.settings.stable_hash(),
            input_hashes=self._input_hashes(documents),
            plan=self.PLAN,
        )
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

        chunks = DocumentIntakeAgent(self.settings.intake, audit).run(documents)
        claims = ClaimExtractionAgent(self.settings.claim_extraction, audit).run(chunks)
        retrieval_agent = EvidenceRetrievalAgent(chunks, self.settings, audit)
        verifier = VerificationAgent(self.settings.verification, audit)
        scorer = RiskScoringAgent(self.settings.scoring["rubric_file"], audit)

        verifications = []
        risks = []
        for claim in claims:
            evidence = retrieval_agent.run(claim)
            verification = verifier.run(claim, evidence)
            verifications.append(verification)
            risks.append(scorer.run(verification))

        gates = ReviewerAgent(audit).run(chunks, verifications, risks, manifest)
        release_status = self._release_status(gates, risks)
        summary = AnalysisSummary(
            total_documents=len(documents),
            total_chunks=len(chunks),
            total_claims=len(claims),
            status_counts=dict(Counter(v.status.value for v in verifications)),
            severity_counts=dict(Counter(r.severity.value for r in risks)),
            release_status=release_status,
        )
        result = AnalysisResult(
            run_id=run_id,
            manifest=manifest,
            claims=claims,
            verifications=verifications,
            risks=risks,
            quality_gates=gates,
            summary=summary,
            output_directory=str(output_dir),
        )
        ReportingAgent().write(result)
        audit.write("run_completed", {"release_status": release_status})
        return result

    @staticmethod
    def _input_hashes(documents: list[DocumentInput]) -> dict[str, str]:
        hashes: dict[str, str] = {}
        for index, document in enumerate(documents):
            name = document.display_name()
            if document.path:
                hashes[f"{index}:{name}"] = file_sha256(document.path)
            else:
                hashes[f"{index}:{name}"] = hashlib.sha256((document.text or "").encode()).hexdigest()
        return hashes

    @staticmethod
    def _release_status(gates, risks) -> str:
        if any(g.status == "FAIL" for g in gates):
            return "BLOCKED"
        if any(g.status == "PENDING_HUMAN_REVIEW" for g in gates):
            return "PENDING_HUMAN_REVIEW"
        if any(r.severity in {Severity.HIGH, Severity.CRITICAL} for r in risks):
            return "PENDING_HUMAN_REVIEW"
        return "RELEASABLE"
