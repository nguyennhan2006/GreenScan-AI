from __future__ import annotations

import hashlib
import json
import uuid
from collections import Counter
from collections.abc import Callable
from pathlib import Path

from quantum_gw.data.export import write_run_layers
from quantum_gw.domain.enums import DocumentRole, Severity
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
from .corpus import profile_corpus
from .figures import DisclosedFigureAgent, corroborate, cross_foot
from .intake import DocumentIntakeAgent
from .legal_check import LegalCheckAgent
from .prioritizer import PrioritizationAgent, entity_names
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
        "check_applicable_law",
        "score_greenwashing_risk",
        "apply_quality_gates",
        "write_evidence_pack",
    ]

    def __init__(self, settings: AppSettings | None = None):
        self.settings = settings or load_settings()

    def run(
        self,
        documents: list[DocumentInput],
        progress: Callable[[str, int, int, str], None] | None = None,
    ) -> AnalysisResult:
        """Run the plan. `progress(step, index, total, detail)` hears each step."""

        def step(name: str, detail: str = "") -> None:
            if progress is not None:
                progress(name, self.PLAN.index(name) + 1, len(self.PLAN), detail)

        step("validate_inputs", f"{len(documents)} tài liệu")
        if not documents:
            raise ValueError("At least one document is required")
        run_id = uuid.uuid4().hex[:16]
        output_dir = Path(self.settings.runs_dir) / run_id
        output_dir.mkdir(parents=True, exist_ok=True)
        audit = AuditLogger(output_dir / "audit.jsonl")
        audit.write("run_started", {"run_id": run_id, "plan": self.PLAN})

        verifier = VerificationAgent(self.settings.verification, audit)
        judge = verifier.llm_judge
        manifest = RunManifest(
            run_id=run_id,
            pipeline_version=self.settings.version,
            config_hash=self.settings.stable_hash(),
            input_hashes=self._input_hashes(documents),
            plan=self.PLAN,
            corpus_version=self.settings.corpus_version,
            rule_pack_version=self.settings.legal.rule_pack_file,
            # The prompt version and the models that may answer it, e.g.
            # "stance-v1@fpt:GLM-5.2"; empty when no model is consulted.
            prompt_version=getattr(judge, "version", "") if judge is not None else "",
        )
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

        step("parse_and_ocr_documents", "PDF lớn có thể mất 1–2 phút")
        chunks = DocumentIntakeAgent(self.settings.intake, audit).run(documents)
        corpus = profile_corpus(documents, chunks)
        audit.write("corpus_profiled", corpus.to_json())
        step("extract_green_claims", f"{len(chunks)} đoạn văn")
        extractor = ClaimExtractionAgent(self.settings.claim_extraction, audit)
        claims = extractor.run(chunks)
        step("build_hybrid_retrieval_index", f"{len(claims)} tuyên bố")
        retrieval_agent = EvidenceRetrievalAgent(chunks, self.settings, audit)
        verifier.corpus = corpus
        sectors = {
            str(d.metadata.get("sector")).strip()
            for d in documents if d.metadata.get("sector")
        }
        legal_agent = LegalCheckAgent(
            self.settings.legal, audit,
            sector=sectors.pop() if len(sectors) == 1 else None,
            subject_type=next(
                (str(d.metadata["subject_type"]) for d in documents if d.metadata.get("subject_type")),
                None,
            ),
        )
        scorer = RiskScoringAgent(
            self.settings.scoring["rubric_file"], audit, review=self.settings.review
        )

        work = []
        for index, claim in enumerate(claims, start=1):
            step("retrieve_evidence_per_claim", f"{index}/{len(claims)} tuyên bố")
            work.append((claim, retrieval_agent.run(claim)))
        # With the stance model on, every escalated pair is asked in one
        # concurrent batch here; the loop below then reads answers from cache.
        step(
            "verify_claim_evidence_pairs",
            "hỏi mô hình cho các cặp luật chưa quyết được" if judge is not None else "luật và phép tính",
        )
        prefetch = verifier.prefetch_llm(work)
        if prefetch is not None:
            audit.write("llm_stance_prefetch", prefetch)

        verifications = []
        risks = []
        legal_checks = []
        for index, (claim, evidence) in enumerate(work, start=1):
            step("check_applicable_law", f"{index}/{len(work)} tuyên bố: kiểm chứng, pháp lý, rủi ro")
            verification = verifier.run(claim, evidence)
            verifications.append(verification)
            legal_check = legal_agent.run(verification)
            if legal_check is not None:
                legal_checks.append(legal_check)
            risks.append(scorer.run(verification))

        step("score_greenwashing_risk", "số liệu công bố và hàng đợi soát")
        figures = DisclosedFigureAgent(audit).run(chunks)
        figure_checks = cross_foot(figures) + corroborate(figures)
        audit.write("figure_checks_completed", {
            "checks": len(figure_checks),
            "inconsistent": sum(1 for c in figure_checks if c.status == "INCONSISTENT"),
        })

        prioritizer = PrioritizationAgent(self.settings.priority_policy, audit)
        entity = entity_names(
            (c.text for c in chunks if c.role == DocumentRole.CLAIM_SOURCE),
            declared=[
                d.metadata.get(key) for d in documents
                for key in ("company", "company_name", "issuer") if d.metadata.get(key)
            ],
        )
        audit.write("entity_resolved", {"names": entity})
        priorities = prioritizer.run(
            verifications, legal_checks, figures, figure_checks, entity=entity
        )

        step("apply_quality_gates")
        gates = ReviewerAgent(audit).run(
            chunks, verifications, risks, manifest, legal_checks, legal_agent.unavailable_reason
        )
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
            legal_checks=legal_checks,
            priorities=[p.to_json() for p in priorities],
            disclosed_figures=figures,
            figure_checks=figure_checks,
            scope_note=prioritizer.scope_note(priorities),
            entity=entity,
            corpus=corpus.to_json(),
            quality_gates=gates,
            summary=summary,
            output_directory=str(output_dir),
        )
        step("write_evidence_pack")
        ReportingAgent().write(result)
        layer_counts = write_run_layers(
            output_dir / "contract",
            run_id=run_id,
            producer_version=self.settings.version,
            documents=documents,
            chunks=chunks,
            claims=claims,
            rejected=getattr(extractor, "rejected_sentences", []),
            figures=figures,
        )
        audit.write("data_layers_written", layer_counts)
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
