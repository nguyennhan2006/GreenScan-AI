from __future__ import annotations

import hashlib
import json
import uuid
from collections import Counter
from collections.abc import Callable
from pathlib import Path

from quantum_gw.data.export import write_run_layers
from quantum_gw.domain.enums import DocumentRole, Severity
from quantum_gw import model_mode
from quantum_gw.domain.models import (
    AnalysisResult,
    AnalysisSummary,
    DocumentInput,
    RunManifest,
    VerificationResult,
)
from quantum_gw.feedback.memory import FeedbackMemory
from quantum_gw.legal.org_pack import ClaimFacts, OrgPackSet
from quantum_gw.settings import AppSettings, load_settings
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.utils.text import file_sha256

from .claim_extractor import ClaimExtractionAgent
from .corpus import profile_corpus
from .figures import DisclosedFigureAgent, corroborate, cross_foot, keep_material, table_checks
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

        memory = FeedbackMemory(self.settings.feedback, audit)
        verifier = VerificationAgent(self.settings.verification, audit, llm_judge=memory.local_judge())
        judge = verifier.llm_judge
        memory.attach_examples(judge)
        # The organisation's own rules, off unless QUANTUM_ORG_PACKS names a pack.
        # A pack that fails validation is reported in the manifest and not applied.
        org_packs = OrgPackSet(self.settings.legal.org_packs) if self.settings.legal.org_packs else None
        manifest = RunManifest(
            run_id=run_id,
            pipeline_version=self.settings.version,
            config_hash=self.settings.stable_hash(),
            input_hashes=self._input_hashes(documents),
            plan=self.PLAN,
            corpus_version=self.settings.corpus_version,
            rule_pack_version=self.settings.legal.rule_pack_file,
            # The prompt version and the models that may answer it, e.g.
            # "stance-v2@fpt:GLM-5.2"; empty when no model is consulted.
            prompt_version=getattr(judge, "version", "") if judge is not None else "",
            org_packs=org_packs.entries if org_packs is not None else None,
            feedback=memory.manifest(),
            model_stages=model_mode.describe(self.settings.verification),
        )
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        if org_packs is not None:
            audit.write("org_packs_loaded", {"packs": [
                {k: e[k] for k in ("path", "org_id", "pack_version", "status", "sha256", "errors")}
                for e in org_packs.entries
            ]})

        step("parse_and_ocr_documents", "PDF lớn có thể mất 1–2 phút")
        intake = DocumentIntakeAgent(self.settings.intake, audit)
        chunks = intake.run(documents)
        corpus = profile_corpus(documents, chunks)
        audit.write("corpus_profiled", corpus.to_json())
        step("extract_green_claims", f"{len(chunks)} đoạn văn")
        extractor = ClaimExtractionAgent(self.settings.claim_extraction, audit)
        claims = extractor.run(chunks)
        self._assist_claims(claims, audit)
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
        org_findings = [] if org_packs is not None else None
        for index, (claim, evidence) in enumerate(work, start=1):
            step("check_applicable_law", f"{index}/{len(work)} tuyên bố: kiểm chứng, pháp lý, rủi ro")
            verification = verifier.run(claim, evidence)
            verifications.append(verification)
            legal_check = legal_agent.run(verification)
            if legal_check is not None:
                legal_checks.append(legal_check)
            risks.append(scorer.run(verification))
            if org_packs is not None:
                org_findings.append(self._org_record(org_packs, verification, legal_agent.sector))
        if org_findings is not None:
            audit.write("org_rules_checked", dict(Counter(
                f["outcome"] for record in org_findings for f in record["findings"]
            )))

        step("score_greenwashing_risk", "số liệu công bố và hàng đợi soát")
        figures = DisclosedFigureAgent(audit).run(chunks)
        figure_checks = cross_foot(figures)
        figure_checks += table_checks(figures, figure_checks) + corroborate(figures)
        figures = keep_material(figures, figure_checks)
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
        # Past decisions: precedents beside the verdict, shadow model, and queue places
        # that may only be added (feedback-loop-v1). Verdicts, risks and release are not touched.
        precedents = memory.apply(verifications, priorities, org_findings, output_dir)
        from quantum_gw.feedback.queue import audit_sample

        sampled = audit_sample(priorities, run_id, self.settings.review.audit_sample_size)
        if sampled:
            audit.write("audit_sample", {"size": len(sampled), "claim_ids": sampled})
        if verifier.ir_reader is not None:
            queued = {p.item_id for p in priorities if p.in_queue and p.item_type == "claim"}
            read = sum(verifier.dual_note(v) for v in verifications if v.claim.claim_id in queued)
            audit.write("assist_dual_reader", {"queued_claims": len(queued), "noted": read,
                                               "reader": getattr(verifier.ir_reader, "model", "?")})
        self._assist_explain(verifications, priorities, audit)

        step("apply_quality_gates")
        gates = ReviewerAgent(audit).run(
            chunks, verifications, risks, manifest, legal_checks, legal_agent.unavailable_reason,
            integrity=intake.integrity, reading=intake.reading,
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
            org_findings=org_findings,
            precedents=precedents,
            integrity=intake.integrity,
            reading=intake.reading,
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
    def _org_record(org_packs: OrgPackSet, verification: VerificationResult, sector: str | None) -> dict:
        """The organisation's rules on one claim. Reads the verification; changes nothing in it."""
        claim = verification.claim
        record: dict = {"claim_id": claim.claim_id, "findings": []}
        evidence = [
            {"chunk_id": e.chunk_id, "text": e.text, "source_type": e.source_type.value,
             "suspicious_instruction": e.suspicious_instruction, "below_threshold": e.below_threshold}
            for e in verification.evidence
        ]
        try:
            record["findings"] = org_packs.evaluate(ClaimFacts.from_claim(claim, sector), evidence)
        except Exception as exc:  # noqa: BLE001 - an org rule that cannot run must not stop the run
            record["error"] = f"Không đánh giá được quy tắc nội bộ: {exc}"
        return record

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

    def _assist_claims(self, claims, audit) -> None:
        """S1 and S2 of llm_stages_v1, each behind its own flag; neither sets a verdict."""
        if self.settings.claim_extraction.claim_model_dir:
            from .claim_model import ClaimModel

            model = ClaimModel(self.settings.claim_extraction.claim_model_dir,
                               self.settings.claim_extraction.claim_model_threshold)
            audit.write("assist_claim_model", model.mark(claims))
        if self.settings.verification.assist_attributes:
            from quantum_gw.assist.client import StageModel
            from quantum_gw.assist.stages import fill_attributes

            stage = StageModel("attributes", "claim_normalization", cache_dir=self.settings.verification.llm_cache_dir)
            audit.write("assist_attributes", fill_attributes(claims, stage) if stage.available
                        else {"skipped": "chưa có mô hình cho bước điền thuộc tính"})

    def _assist_explain(self, verifications, priorities, audit) -> None:
        """S6 of llm_stages_v1: explanations for the queue (or every claim), beside the rules rationale."""
        mode = self.settings.verification.assist_explain
        if mode == "off":
            return
        from quantum_gw.assist.client import StageModel
        from quantum_gw.assist.stages import explain_result

        from .verifier import missing_attributes

        stage = StageModel("explain", "claim_explanation", cache_dir=self.settings.verification.llm_cache_dir)
        if not stage.available:
            audit.write("assist_explain", {"skipped": "chưa có mô hình cho bước giải thích"})
            return
        queued = {p.item_id for p in priorities if p.in_queue and p.item_type == "claim"}
        shown = 0
        for v in verifications:
            if mode == "all" or v.claim.claim_id in queued:
                shown += explain_result(v, stage, missing_attributes(v.claim))
        audit.write("assist_explain", {"mode": mode, "shown": shown, "route": stage.route(),
                                       "version": stage.version, **stage.stats})

    @staticmethod
    def _release_status(gates, risks) -> str:
        if any(g.status == "FAIL" for g in gates):
            return "BLOCKED"
        if any(g.status == "PENDING_HUMAN_REVIEW" for g in gates):
            return "PENDING_HUMAN_REVIEW"
        if any(r.severity in {Severity.HIGH, Severity.CRITICAL} for r in risks):
            return "PENDING_HUMAN_REVIEW"
        return "RELEASABLE"
