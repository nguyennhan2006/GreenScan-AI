from __future__ import annotations

import copy
import re
from pathlib import Path

import yaml

from quantum_gw.domain.enums import VerificationStatus
from quantum_gw.domain.models import Claim, RetrievedEvidence, VerificationResult
from quantum_gw.parsers.ocr import matches_value
from quantum_gw.settings import VerificationSettings
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.utils import vn_format as vn
from quantum_gw.utils.security import contains_prompt_injection, scan_injection
from quantum_gw.utils.security import describe as describe_injection
from quantum_gw.utils.text import (
    YEAR_RE,
    content_bigrams,
    content_tokens,
    emission_scopes,
    normalize_for_match,
    parse_quantities,
    split_sentences,
)
from quantum_gw.verification.numeric_facts import (
    AMBIGUOUS,
    NOT_COMPARABLE,
    NumericFact,
    describe,
    eligibility,
    facts_in,
)
from quantum_gw.verification.numeric_facts import (
    POLICY_ID as ELIGIBILITY_POLICY,
)
from quantum_gw.verification.absolute import absolute_conflict, allocated_share
from quantum_gw.verification.assessment import assess
from quantum_gw.verification.stance import (
    CONTEXT,
    CONTRADICTS,
    PARTIAL,
    SUPPORTS,
    StanceLexicon,
    StanceSignal,
    qualitative_stance,
)

# The company speaking about itself: its own report, its own financial
# statements. A refutation cue here is prose, not a finding (contradiction guard).
SELF_SOURCES = frozenset({"internal", "financial"})
# Types given by claim-typing-v2 when no claim_type matched (configs/taxonomy.yaml v4).
FALLBACK_CLAIM_TYPES = frozenset({"resource_use", "metric_disclosure", "environmental_compliance", "greening"})

# internal-inconsistency-v1: where a report keeps its data (folded text), and words that say a figure was restated.
_DATA_PAGE_RE = re.compile(r"\b(gri\s*3\d\d|bang so lieu|chi so moi truong|phu luc|bang \d+|du lieu moi truong)")
_RESTATED_RE = re.compile(r"\b(dieu chinh|trinh bay lai|restat\w*)")

class _RecordingJudge:
    """Stands in for the model during the dry pass: notes the question, answers nothing."""

    def __init__(self):
        self.asked: list[tuple[str, str]] = []

    def judge(self, claim_text: str, evidence_text: str) -> None:
        self.asked.append((claim_text, evidence_text))
        return None


# Sources the company did not write. A company's annual or financial report, its GHG
# inventory and its monitoring data are its own account, however carefully kept.
# Studio reads the same set (studio/document.py).
INDEPENDENT_SOURCE_TYPES = frozenset({"legal", "external", "standard"})


class _NullAudit:
    def write(self, event: str, payload=None) -> None:
        return None


class VerificationAgent:
    """Claim + retrieved evidence -> a status, with the per-passage stance behind it.

    Order of authority, strongest first:

        1. numeric      two comparable figures agree or disagree
        2. qualitative  a cue phrase refutes or confirms the claim
        3. direction    the trend stated in the claim is reversed in evidence
        4. similarity   nothing decided; fall back to how related the text is

    The per-passage stance is now computed *before* the claim status and the
    status is derived from it. Previously the status was decided from retrieval
    scores alone and the stances were attached afterwards, which let the two
    disagree: DWS-2023 was reported PARTIALLY_SUPPORTED on the strength of a
    passage saying the firm "lacked formalized controls to verify use of the ESG
    Engine". A refutation counted towards support because nothing ever asked the
    passage which side it was on.
    """

    def __init__(
        self,
        settings: VerificationSettings,
        audit: AuditLogger,
        lexicon: StanceLexicon | None = None,
        llm_judge=None,
        taxonomy_path: str = "configs/taxonomy.yaml",
        ir_reader=None,
    ):
        self.settings = settings
        self.audit = audit
        self.lexicon = lexicon or StanceLexicon()
        self._llm_judge = llm_judge
        self._ir_reader = ir_reader
        self.taxonomy = _load_taxonomy(taxonomy_path)
        # Set by the orchestrator once per run (agents/corpus.py). None means
        # unknown, which is treated as insufficient: absence may only become
        # UNSUPPORTED when we know what was searched.
        self.corpus = None

    @property
    def llm_judge(self):
        """Built on first use so `llm_stance: off` never constructs a gateway."""
        if self._llm_judge is None and self.settings.llm_stance == "on_ambiguous":
            from quantum_gw.verification.llm_judge import LLMStanceJudge

            self._llm_judge = LLMStanceJudge(
                cache_dir=self.settings.llm_cache_dir, workers=self.settings.llm_workers
            )
        return self._llm_judge

    @property
    def ir_reader(self):
        """The IR reader of QUANTUM_VERIFY=dual (S4 of llm_stages_v1); None when off or no provider serves `ir_reading`."""
        if self._ir_reader is None and self.settings.verify_mode == "dual":
            from quantum_gw.providers.router import ModelGateway
            from quantum_gw.verification.ir_reader import IRReader

            provider = ModelGateway().resolve("ir_reading")
            self._ir_reader = IRReader(provider, self.settings.llm_cache_dir) if provider is not None else False
        return self._ir_reader or None

    def prefetch_llm(self, work: list[tuple[Claim, list[RetrievedEvidence]]]) -> dict | None:
        """Ask the model about every pair this run will escalate, concurrently, up front.

        Which pairs reach the judge is decided by the deterministic layers, so a
        dry pass with a judge that only records the question finds exactly
        them; the real pass then reads every answer from the judge's cache. The
        dry pass writes no audit events and its verdicts are discarded.
        """
        judge = self.llm_judge
        if judge is None or not hasattr(judge, "prefetch"):
            return None
        recorder = _RecordingJudge()
        dry = copy.copy(self)
        dry.audit = _NullAudit()
        dry._llm_judge = recorder
        for claim, evidence in work:
            dry.run(claim, [item.model_copy() for item in evidence])
        return judge.prefetch(recorder.asked)

    def run(self, claim: Claim, evidence: list[RetrievedEvidence]) -> VerificationResult:
        warnings: list[str] = []
        clean_evidence = []
        # A sentence addressed to the grader is a finding, not a claim to weigh:
        # it is never shown to a model (see _stance) and goes to a person.
        planted = scan_injection(claim.text)
        if planted:
            warnings.append(
                "Câu tuyên bố chứa lời nhắn tới hệ thống chấm tự động ("
                f"{describe_injection(planted)}); không đưa cho mô hình ngôn ngữ, cần người soát xét."
            )
        for item in evidence:
            if item.suspicious_instruction:
                warnings.append(
                    f"Đã loại một đoạn bằng chứng chứa lời nhắn tới hệ thống chấm tự động: {item.citation}"
                    if self.settings.injection_policy == "exclude" else
                    f"Đoạn bằng chứng chứa lời nhắn tới hệ thống chấm tự động, giữ lại nhưng không đưa cho mô hình: {item.citation}"
                )
                if self.settings.injection_policy == "exclude":
                    continue
            clean_evidence.append(item)

        if not clean_evidence:
            result = VerificationResult(
                claim=claim,
                status=VerificationStatus.INSUFFICIENT_EVIDENCE,
                rationale="No admissible evidence passed the retrieval threshold.",
                evidence=[],
                warnings=warnings + _reading_warnings(claim, []),
                suspected_injection=bool(planted) or any(i.suspicious_instruction for i in evidence),
                doubtful_reading=bool(claim.doubtful_numbers),
            )
            self._audit(result)
            return result

        numeric = self._numeric_comparison(claim, clean_evidence)

        by_rules: dict[int, StanceSignal] = {}
        model_saw_injection = []
        misread = []
        for item in clean_evidence:
            signal = self._stance(claim, item)
            if signal.doubtful:
                misread.append(item.citation)
            if signal.method == "llm" and signal.fallback is not None:
                by_rules[id(item)] = signal.fallback
            if signal.injection:
                model_saw_injection.append(item.citation)
            item.relation = signal.relation
            item.relation_reason = signal.reason
            item.relation_method = signal.method
        if model_saw_injection:
            warnings.append(
                "Mô hình ngôn ngữ báo đoạn văn chứa lời nhắn tới máy chấm; lập trường của đoạn đó không được dùng: "
                + "; ".join(model_saw_injection[:3])
            )

        warnings += _reading_warnings(claim, misread)

        status, rationale = self._status(claim, clean_evidence, numeric)
        # A model's reading needs a human only where it matters: where it changed
        # the verdict the rules would have given, or where it suspects a
        # contradiction. Flagging every claim it touched (156 of 156 on HPG,
        # 28/09) makes the flag meaningless.
        escalated = bool(by_rules) and (
            self._status_by_rules(claim, clean_evidence, numeric, by_rules)[0] != status
            or any(i.relation == CONTRADICTS and i.relation_method == "llm" for i in clean_evidence)
        )
        if escalated:
            warnings.append(
                "Kết luận này phụ thuộc vào lập trường do mô hình ngôn ngữ đề xuất; cần người xác nhận."
            )

        flags = []
        if any(i.relation_method == "internal" for i in clean_evidence):
            flags.append("internal_inconsistency")
        if (status == VerificationStatus.PARTIALLY_SUPPORTED and rationale.startswith("Bằng chứng không thống nhất")):
            flags.append("conflicting_evidence")
        if any(
            (i.relation_method == "absolute" and i.score >= self.settings.partial_support_score)
            or (i.relation_method == "numeric" and i.relation in (CONTRADICTS, PARTIAL)
                and "nghĩa là 100% vốn" in (i.relation_reason or ""))
            for i in clean_evidence
        ):
            flags.append("absolute_claim_conflict")
        if flags:
            warnings.append(
                "Cần người soát: "
                + "; ".join({"internal_inconsistency": "không nhất quán nội bộ (lời văn ≠ bảng số liệu cùng tài liệu)",
                             "conflicting_evidence": "các đoạn bằng chứng nêu số khác nhau cho cùng chỉ số",
                             "absolute_claim_conflict": "tuyên bố tuyệt đối nhưng bằng chứng cho thấy chỉ một phần"}[f]
                            for f in flags)
                + "."
            )

        result = VerificationResult(
            claim=claim,
            status=status,
            rationale=rationale,
            evidence=clean_evidence,
            computed_values=numeric,
            warnings=warnings,
            review_flags=flags,
            assessment=assess(claim, clean_evidence, status.value),
            requires_llm_review=escalated,
            suspected_injection=bool(planted or model_saw_injection)
            or any(i.suspicious_instruction for i in evidence),
            doubtful_reading=bool(claim.doubtful_numbers or misread),
        )
        self._audit(result)
        return result

    def dual_note(self, result: VerificationResult) -> bool:
        """S4: attach the IR reader's reading to a verified claim (called for queued claims, amendment 17h05)."""
        notes = self._dual_reading(result.claim, result.evidence)
        if not notes:
            return False
        result.assist["ir"] = notes
        if any(n["dual"] != n["rules"] and n["dual"] in ("S", "C") for n in notes):
            result.warnings.append(
                "Bộ đọc số liệu (mô hình ngôn ngữ) đề xuất một kết luận khác luật cho số liệu của tuyên bố; "
                "chỉ để người soát xem, không đổi kết luận."
            )
        return True

    def _dual_reading(self, claim: Claim, evidence: list[RetrievedEvidence]) -> list[dict]:
        """S4: the IR reader's S / C / N per passage beside the rules', combined by AG-2 union_noloneS.

        Only claims that write a figure, only passage sentences that write one (at most three, those about the
        claim's metric first). A reviewer note: it never touches a relation, the status or the review flag.
        """
        reader = self.ir_reader
        if reader is None or not re.search(r"\d", claim.text):
            return []
        from quantum_gw.verification.ir_reader import dual

        notes = []
        for item in evidence:
            if item.suspicious_instruction:
                continue
            sentences = [x for x in self._metric_sentences(claim, item.text) if re.search(r"\d", x)]
            sentences += [x for x in (split_sentences(item.text) or []) if re.search(r"\d", x) and x not in sentences]
            if not sentences:
                continue
            try:
                ir, why = reader.label(claim.text, " ".join(sentences[:3]))
            except Exception:  # noqa: BLE001 - a reader outage leaves the rules alone
                continue
            rules = ("S" if item.relation == SUPPORTS and item.relation_method != "llm" else
                     "C" if item.relation == CONTRADICTS and item.relation_method != "llm" else "N")
            notes.append({"citation": item.citation, "rules": rules, "ir": ir, "dual": dual(rules, ir),
                          "why": why[:3], "reader": getattr(reader, "model", "?")})
        return notes

    # ---------- status ----------

    def _status_by_rules(self, claim, evidence, numeric, by_rules):
        """The verdict with every model stance replaced by the rules' own reading."""
        saved = [(i, i.relation, i.relation_reason, i.relation_method)
                 for i in evidence if id(i) in by_rules]
        for item, *_ in saved:
            rule = by_rules[id(item)]
            item.relation, item.relation_reason, item.relation_method = (
                rule.relation, rule.reason, rule.method)
        try:
            return self._status(claim, evidence, numeric)
        finally:
            for item, relation, reason, method in saved:
                item.relation, item.relation_reason, item.relation_method = relation, reason, method

    def _status(
        self,
        claim: Claim,
        evidence: list[RetrievedEvidence],
        numeric: dict,
    ) -> tuple[VerificationStatus, str]:
        best = evidence[0]
        overlap = self._metric_overlap(claim, evidence)
        # A model's stance points a reviewer at a passage; it does not close a
        # finding (verification/llm_judge.py). On HPG, 28/09, letting it decide
        # produced 10 CONTRADICTED and 2 CRITICAL on a control company -- a
        # garbled table row read as "100% male", a process description read as
        # a refutation. Only the gold set may lift this (llm_stance_decisive).
        decisive_model = self.settings.llm_stance_decisive
        contradicting = [
            item for item in evidence
            if item.relation == CONTRADICTS and (decisive_model or item.relation_method != "llm")
        ]

        # figure-consistency-v1: a passage from another document matches the claim's figure exactly while
        # another passage disagrees with a different figure (GS-Bench ba-N14: "3,18 tỷ kWh" for two plants
        # in one sentence, "788 triệu kWh" for one plant in the next). The evidence disagrees with itself;
        # a reviewer decides which figure is about the claim.
        if contradicting and self.settings.figure_consistency_check and all(
            i.relation_method == "numeric" for i in contradicting
        ):
            agreeing = self._agreeing_figure(claim, evidence)
            if agreeing is not None:
                return (
                    VerificationStatus.PARTIALLY_SUPPORTED,
                    f"Bằng chứng không thống nhất: {agreeing.relation_reason.rstrip('.')} ({agreeing.citation}); "
                    f"nhưng {contradicting[0].relation_reason[0].lower()}{contradicting[0].relation_reason[1:].rstrip('.')} "
                    f"({contradicting[0].citation}). Cần người xem đoạn nào nói về đúng đối tượng của tuyên bố.",
                )
        if contradicting:
            reason = contradicting[0].relation_reason
            return (
                VerificationStatus.CONTRADICTED,
                f"Bằng chứng đã truy xuất bác bỏ tuyên bố. {reason}",
            )
        suspected = [
            item for item in evidence
            if item.relation == CONTRADICTS and item.relation_method == "llm"
        ]
        if suspected and best.score >= self.settings.partial_support_score:
            return (
                VerificationStatus.PARTIALLY_SUPPORTED,
                "Mô hình ngôn ngữ nghi một đoạn mâu thuẫn với tuyên bố nhưng không có phép "
                f"tính hay nguồn có thẩm quyền xác nhận; cần người xem. {suspected[0].relation_reason}",
            )
        # A reversed trend with no figure to anchor it ("giảm" in the claim,
        # "tăng" in a passage about the same metric) is a reviewer's flag, not a
        # verdict: Vietnamese prose uses both words in nearly every paragraph
        # about a metric. It caps the status at PARTIALLY_SUPPORTED.
        reversed_trend = any(item.relation_method == "direction" for item in evidence)
        if reversed_trend and best.score >= self.settings.partial_support_score:
            return (
                VerificationStatus.PARTIALLY_SUPPORTED,
                "Bằng chứng cùng chỉ số nêu xu hướng ngược với tuyên bố nhưng không có "
                "số liệu để đối chiếu; cần người xem xét.",
            )
        # The two review flags (internal-inconsistency-v1 in flag mode, stance-cues-v3):
        # they cap the status at PARTIALLY_SUPPORTED, whatever another passage confirms.
        flagged = [
            item for item in evidence
            if item.relation == PARTIAL and (
                item.relation_method == "internal"
                or (item.relation_method == "absolute" and item.score >= self.settings.partial_support_score)
                # absolute-share-v1 computed a share below 100% but above the contradiction line: say so
                or (item.relation_method == "numeric" and "nghĩa là 100% vốn" in (item.relation_reason or ""))
            )
        ]
        if flagged:
            return (
                VerificationStatus.PARTIALLY_SUPPORTED,
                f"{flagged[0].relation_reason} ({flagged[0].citation})",
            )

        # SUPPORTED needs a passage from a document other than the one the
        # claim was taken from. A report's highlights page restating its own
        # data table is consistency, not evidence -- 3 of 3 "supported" Hòa Phát
        # claims were the claim agreeing with itself on the same page. Such a
        # match still counts, as PARTIAL, and the rubric's independent_assurance
        # component says what is missing.
        supporting = [item for item in evidence if item.relation == SUPPORTS]
        # An empty id is unknown provenance (inline text, older records), not the same file.
        external = [
            item for item in supporting
            if not (claim.source_doc_id and item.doc_id == claim.source_doc_id)
        ]
        # The passage that supports the claim must itself clear the retrieval
        # floor; the best-ranked passage may be a different, merely similar one.
        external = [e for e in external if e.score >= self.settings.partial_support_score]
        # Support guard (flag, off by default): the company's other documents restating a
        # claim show its reports agree, not that the claim is true. All 5 SUPPORTED verdicts
        # on GS-Eval v2 (05/11) were wrong; see independent_support_v1.
        echo = None
        if self.settings.support_requires_independent_source:
            own = [e for e in external if e.source_type.value not in INDEPENDENT_SOURCE_TYPES]
            external = [e for e in external if e.source_type.value in INDEPENDENT_SOURCE_TYPES]
            echo = self._confirming(claim, own, decisive_model)
        # A figure that agrees is support on its own. A cue phrase ("chứng
        # nhận", "xác nhận") is not: 3 of 3 Hòa Phát SUPPORTED verdicts on
        # 2026-09-22 rested on one such word in the annual report (ISSUES N4).
        # A phrase confirms a claim only when the sentence it sits in also
        # names what the claim is about -- its metric, and every period and
        # scope the claim states -- and at least two of those line up. The
        # count is a hypothesis to sweep on the gold set (RESEARCH_PROGRAM RQ7).
        for item in external:
            if item.relation_method == "numeric":
                return (
                    VerificationStatus.SUPPORTED,
                    f"Một nguồn ngoài tài liệu tuyên bố xác nhận: {item.relation_reason}",
                )
        weak: list[str] = []
        model_backed: list[RetrievedEvidence] = []
        for item in external:
            if item.relation_method == "llm" and not decisive_model:
                model_backed.append(item)
                continue
            matched, stated = self._attributes_matched(claim, item.text)
            required = {"metric"} | (stated & {"period", "scopes"})
            if required <= matched and len(matched) >= self.settings.support_min_attributes:
                return (
                    VerificationStatus.SUPPORTED,
                    f"Một nguồn ngoài tài liệu tuyên bố xác nhận: {item.relation_reason} "
                    f"Thuộc tính khớp: {', '.join(sorted(matched))}.",
                )
            weak.append(", ".join(sorted(matched)) or "không")
        if echo is not None:
            return (
                VerificationStatus.PARTIALLY_SUPPORTED,
                "Chỉ tài liệu khác của chính doanh nghiệp xác nhận tuyên bố: "
                f"{echo.relation_reason.rstrip('.')}. Chưa có nguồn độc lập (văn bản pháp luật, "
                "nguồn bên ngoài doanh nghiệp, chuẩn mực) nói như vậy; các báo cáo của cùng một "
                "doanh nghiệp khớp nhau chưa phải là kiểm chứng, cần người xem.",
            )
        if weak:
            return (
                VerificationStatus.PARTIALLY_SUPPORTED,
                "Có xác nhận định tính từ nguồn khác nhưng chưa có số liệu và câu xác nhận "
                f"không nêu đủ chỉ số/kỳ/phạm vi của tuyên bố (thuộc tính khớp: {weak[0]}); cần người xem.",
            )
        if model_backed:
            return (
                VerificationStatus.PARTIALLY_SUPPORTED,
                "Mô hình ngôn ngữ đánh giá một đoạn từ nguồn khác là xác nhận, nhưng không có "
                "số liệu hay cụm từ xác nhận để luật chốt; cần người xem. "
                f"{model_backed[0].relation_reason}",
            )
        if any(e.score >= self.settings.partial_support_score for e in supporting):
            return (
                VerificationStatus.PARTIALLY_SUPPORTED,
                "Chỉ tài liệu của chính nguồn tuyên bố khớp với tuyên bố; chưa có nguồn "
                "đối chiếu độc lập (báo cáo khác, kiểm toán, cơ quan quản lý).",
            )
        # A claim with no figure and promotional wording ("a leading green
        # company"), or a pledge about the future with no figure, has nothing a
        # passage could partially agree with; similarity alone must not lift it
        # above UNSUPPORTED. A PARTIAL stance (same subject, some figures) still can.
        unverifiable_by_similarity = claim.is_vague or (claim.is_future_commitment and not claim.values)
        if unverifiable_by_similarity and not any(item.relation == PARTIAL for item in evidence):
            if best.score >= self.settings.partial_support_score and overlap >= 0.10:
                return self._absence(
                    claim,
                    "Tuyên bố mơ hồ, không có chỉ số hay số liệu để đối chiếu; tài liệu "
                    "liên quan không xác nhận được nội dung quảng bá.",
                )
            return (
                VerificationStatus.INSUFFICIENT_EVIDENCE,
                "Tuyên bố mơ hồ và không có tài liệu nào đủ liên quan để đối chiếu.",
            )
        # Say which of the five attributes is missing. 168 of 181 Hòa Phát claims
        # came back with the same two English sentences on 2026-09-22, which tells
        # a reviewer nothing about what to do next (ISSUES N3).
        if best.score >= self.settings.strong_support_score and overlap >= 0.30:
            return (
                VerificationStatus.PARTIALLY_SUPPORTED,
                "Có bằng chứng cùng chủ đề nhưng chưa xác minh được đầy đủ. "
                + _gap_sentence(claim),
            )
        if best.score >= self.settings.partial_support_score and overlap >= 0.25:
            return (
                VerificationStatus.PARTIALLY_SUPPORTED,
                "Bằng chứng liên quan nhưng chưa đủ để xác minh. " + _gap_sentence(claim),
            )
        # UNSUPPORTED asserts that related material was found and does not
        # substantiate the claim. A passage that merely shares surface form with
        # the claim (no content token in common) is not related material, and the
        # honest answer is that nothing was found -- an abstain, not a negative.
        if best.score >= self.settings.partial_support_score and overlap >= 0.10:
            return self._absence(
                claim, "Tài liệu liên quan đã được truy xuất nhưng không xác nhận tuyên bố."
            )
        return (
            VerificationStatus.INSUFFICIENT_EVIDENCE,
            "Bằng chứng hiện có quá yếu để ủng hộ hay bác bỏ tuyên bố." + self._corpus_note(),
        )

    @staticmethod
    def _agreeing_figure(claim: Claim, evidence: list[RetrievedEvidence]):
        """A numeric match from a document other than the claim's own, or None."""
        return next((
            i for i in evidence
            if i.relation == SUPPORTS and i.relation_method == "numeric"
            and not (claim.source_doc_id and i.doc_id == claim.source_doc_id)
        ), None)

    def _corpus_note(self) -> str:
        corpus = self.corpus
        if corpus is None:
            return ""
        if corpus.missing:
            return " Kho tài liệu thiếu: " + "; ".join(corpus.missing) + "."
        return " Kho tài liệu đã có tài liệu đối chiếu và nguồn độc lập."

    def _absence(self, claim: Claim, found_nothing: str) -> tuple[VerificationStatus, str]:
        """No support found: UNSUPPORTED only when the corpus could have carried it.

        Open world: a claim checked against one sustainability report has no
        evidence because nothing that could hold it was uploaded. UNSUPPORTED
        requires a comparison document and an independent source to have been
        searched, and a document dated to the claim's period when it names one.
        """
        corpus = self.corpus
        if corpus is None or not corpus.sufficient_for_absence:
            missing = list(corpus.missing) if corpus is not None else ["hồ sơ kho tài liệu"]
            return (
                VerificationStatus.INSUFFICIENT_EVIDENCE,
                f"{found_nothing} Kho tài liệu chưa đủ để suy ra không có bằng chứng — thiếu: "
                + ("; ".join(missing) if missing else "nguồn đối chiếu") + ".",
            )
        if not corpus.period_covered(claim.period):
            return (
                VerificationStatus.INSUFFICIENT_EVIDENCE,
                f"{found_nothing} Không có tài liệu nào trong kho thuộc kỳ {claim.period} của "
                f"tuyên bố (kho có: {', '.join(corpus.years) or 'không rõ năm'}).",
            )
        return (
            VerificationStatus.UNSUPPORTED,
            f"{found_nothing} Kho đã có tài liệu đối chiếu và nguồn độc lập cùng kỳ "
            "(not supported in provided corpus).",
        )

    def _confirming(self, claim: Claim, items: list[RetrievedEvidence], decisive_model: bool):
        """The passage that would make the claim SUPPORTED, by the rule `_status` applies.

        A figure that agrees, else a cue sentence naming the claim's metric and every
        period and scope it states. Used by the support guard to say what the company's
        own documents confirm when no independent source does.
        """
        for item in items:
            if item.relation_method == "numeric":
                return item
        for item in items:
            if item.relation_method == "llm" and not decisive_model:
                continue
            matched, stated = self._attributes_matched(claim, item.text)
            required = {"metric"} | (stated & {"period", "scopes"})
            if required <= matched and len(matched) >= self.settings.support_min_attributes:
                return item
        return None

    # ---------- per-passage stance ----------

    def _stance(self, claim: Claim, item: RetrievedEvidence) -> StanceSignal:
        """Stance of one passage towards the claim.

        Retrieval rank measures similarity, which is a different question: the
        top-ranked passage can be the one that contradicts the claim. A reviewer
        needs the stance per passage, not one status for the whole set.
        """
        same_document = bool(claim.source_doc_id) and item.doc_id == claim.source_doc_id
        guarded = not self.settings.self_evidence_can_contradict
        numeric = self._numeric_relation(claim, item)
        if numeric is not None:
            # Two figures in the claim's own report that disagree are, on real
            # reports, nearly always about two different things: 926 t CO2 from
            # unfired bricks against 1,936 t from mineralised concrete, 23 t of
            # paper trays against 14 t of PET liners (19 of 20 false numeric
            # CONTRADICTED, GS-Eval v2). The figures stay visible to the reviewer.
            if guarded and same_document and numeric.relation == CONTRADICTS:
                if self.settings.internal_inconsistency in ("flag", "contradict"):
                    internal = self._internal_inconsistency(claim, item, numeric)
                    if internal is not None:
                        return internal
                return StanceSignal(
                    relation=CONTEXT,
                    reason=(
                        f"{numeric.reason.rstrip('.')}, nhưng hai số nằm trong cùng tài liệu của tuyên bố "
                        "và có thể nói về hai đối tượng khác nhau; không coi là mâu thuẫn."
                    ),
                    method="numeric",
                )
            # Still arithmetic's answer, withheld when a compared number is one OCR misread.
            numeric = self._unless_misread(claim, item, numeric)
            return numeric

        overlap = self._metric_overlap(claim, [item])
        cue = qualitative_stance(
            item.text,
            source_type=item.source_type.value,
            overlap=overlap,
            minimum_overlap=self.settings.qualitative_min_overlap,
            lexicon=self.lexicon,
            claim_tokens=self._topic_tokens(claim),
            claim_bigrams=content_bigrams(claim.text),
            topic_terms=self._taxonomy_terms(claim),
        )
        # A refutation cue in the company's own prose is not a finding against
        # it: "không ghi nhận trường hợp nào vi phạm" and a GRI index that lists
        # "Nghị định ... về xử phạt vi phạm hành chính" were every one of the
        # cue-based false CONTRADICTED on real reports (GS-Eval v2). Such a cue
        # counts only inside a ruling on statements (cue.authoritative); else
        # the passage is read as if it carried no cue.
        if (
            cue is not None
            and guarded
            and cue.relation == CONTRADICTS
            and not cue.authoritative
            and (same_document or item.source_type.value in SELF_SOURCES)
        ):
            cue = None
        # A compliance claim ("0 trường hợp vi phạm", "0 sự cố môi trường") restated by a passage that
        # names the same violations: the word "vi phạm" is the topic, not a finding (GS-Bench S0, 15/11).
        if (cue is not None and cue.relation == CONTRADICTS and not cue.authoritative
                and claim.claim_type == "environmental_compliance"):
            cue = None
        # An absolute claim ("toàn bộ", "100%") and a sentence about it that says
        # only part is done ("chưa phân bổ", "giai đoạn 1"): a reviewer's flag, never a
        # contradiction, since a phrase is weaker than the arithmetic above (stance-cues-v3).
        if self.settings.absolute_conflict_cues and (cue is None or cue.relation != CONTRADICTS):
            conflict = absolute_conflict(claim.text, item.text, content_bigrams(claim.text), content_bigrams)
            if conflict is not None:
                return StanceSignal(
                    relation=PARTIAL,
                    reason=(
                        f"Tuyên bố dùng từ tuyệt đối “{conflict['absolute']}” nhưng đoạn này nói "
                        f"“{conflict['partial']}”: “{conflict['sentence']}”. Cần người soát xem phần còn lại."
                    ),
                    method="absolute",
                    cues=[conflict["absolute"], conflict["partial"]],
                )
        if cue is not None:
            # A quantified claim is confirmed by its figure, not by a phrase. An
            # assurance statement that "reviewed the GHG management system"
            # says nothing about whether emissions fell 30%.
            if cue.relation == SUPPORTS and _measurements(claim.text):
                return StanceSignal(
                    relation=PARTIAL,
                    reason=f"{cue.reason} Tuy nhiên đoạn không nêu lại số liệu của tuyên bố.",
                    method=cue.method,
                    cues=cue.cues,
                    authoritative=cue.authoritative,
                )
            return cue

        if self._direction_contradiction(claim, [item]):
            return StanceSignal(
                relation=PARTIAL,
                reason="Xu hướng trong đoạn này ngược với tuyên bố; không có số liệu để đối chiếu.",
                method="direction",
            )

        if overlap >= 0.30:
            by_rules = StanceSignal(
                relation=PARTIAL,
                reason="Cùng chủ đề nhưng chưa đủ số liệu để xác nhận.",
                method="similarity",
            )
        else:
            by_rules = StanceSignal(
                relation=CONTEXT,
                reason="Liên quan về ngữ cảnh, không xác nhận hay bác bỏ.",
                method="similarity",
            )

        judge = self.llm_judge
        # Text that addresses the grader never reaches a model, whichever side it is on.
        shielded = item.suspicious_instruction or contains_prompt_injection(claim.text)
        if judge is not None and not shielded and overlap >= self.settings.llm_stance_min_overlap:
            verdict = judge.judge(claim.text, item.text)
            if verdict is not None:
                verdict.fallback = by_rules
                if verdict.injection:
                    # The model noticed an instruction the patterns missed: keep
                    # the rules' reading and say so; nothing it said is used.
                    by_rules.injection = True
                    return by_rules
                return verdict
        return by_rules

    def _unless_misread(self, claim: Claim, item: RetrievedEvidence, signal: StanceSignal) -> StanceSignal:
        """A figure comparison resting on a number OCR was unsure of decides nothing.

        Tesseract reads "30" as "80" and says how sure it is (parsers/ocr.py;
        the thresholds come from docs/decisions/0005-ocr-confidence.md). An
        agreement or a disagreement computed from such a number would be a
        verdict about the scanner, so it goes to a person as PARTIAL with the
        number named. A doubtful number counts, on either side, when it is one
        of the values compared (a "1,2" before "triệu" is 1.2 million); a claim
        with a doubtful figure the comparison did not use is still flagged for
        review, by `run`, but this comparison stands.
        """
        if signal.relation not in (SUPPORTS, CONTRADICTS) or not signal.figures:
            return signal
        shaky = list(dict.fromkeys(
            token for token in [*claim.doubtful_numbers, *item.doubtful_numbers]
            if matches_value(token, signal.figures)
        ))
        if not shaky:
            return signal
        return StanceSignal(
            relation=PARTIAL,
            reason=(
                f"{signal.reason.rstrip('.')}; nhưng số {', '.join(shaky[:4])} do máy đọc ảnh chữ (OCR) đọc "
                "với độ tin cậy thấp, cần đối chiếu trang gốc trước khi kết luận."
            ),
            method="numeric",
            figures=signal.figures,
            doubtful=True,
        )

    def _numeric_relation(self, claim: Claim, item: RetrievedEvidence) -> StanceSignal | None:
        """Stance from comparable figures, or None when there is no pair to compare.

        Comparable is decided by `numeric_facts.eligibility` before any
        arithmetic: same canonical unit, and no explicit mismatch of basis
        (share vs change vs absolute vs intensity), organisational boundary,
        technology, metric variant or GHG scope. A pair the rule marks
        AMBIGUOUS (target vs actual, or a gap of 20-100x with a dimension
        unread) is handed to the reviewer as PARTIAL, never as CONTRADICTED.
        Only sentences about the claim's metric are read, and -- when the claim
        names a period -- a sentence dated to some other year is not support.
        """
        # A continuity claim ("giảm liên tục hằng năm") usually carries no figure
        # of its own, so this runs before the "no figures, nothing to compare"
        # exit: what it checks is the completeness of the evidence series.
        continuity = self._continuity_gap(claim, item)
        if continuity is not None:
            return continuity

        # "Hoàn toàn / toàn bộ / 100%" about green-bond proceeds is a claim that the
        # share used is 100%; with a total and a used amount in the passage that share
        # can be computed (absolute-share-v1, case A2).
        if self.settings.absolute_share_check:
            share = self._absolute_share(claim, item)
            if share is not None:
                return share

        claim_facts = _claim_facts(claim.text)
        if not claim_facts:
            return None

        # A claim of the form "giảm 20%" is not a figure to match against another
        # figure; it is an assertion about two figures. Recompute it from the
        # base and current values when the evidence carries both -- until this
        # existed, "giảm 20%" against "100.000 → 80.000 tCO2e" could not be
        # decided at all, because "%" and "tCO2e" are different units (B9(c)).
        recomputed = self._recomputed_change(claim, item)
        if recomputed is not None:
            return recomputed

        best = None        # (error, claim_fact, evidence_fact, sentence)
        ambiguous = None   # (error, claim_fact, evidence_fact, reason)
        blocked = None     # (reason, claim_fact, evidence_fact)
        per_fact: dict[int, tuple] = {}   # claim fact index -> its own closest comparable (error, evidence_fact)
        for sentence in self._metric_sentences(claim, item.text):
            for evidence_fact in facts_in(sentence):
                for index, claim_fact in enumerate(claim_facts):
                    verdict, reason = eligibility(claim_fact, evidence_fact)
                    if verdict == NOT_COMPARABLE:
                        if reason != "different_unit" and blocked is None:
                            blocked = (reason, claim_fact, evidence_fact)
                        continue
                    error = abs(evidence_fact.value - claim_fact.value) / max(abs(claim_fact.value), 1.0)
                    if verdict == AMBIGUOUS:
                        if ambiguous is None or error < ambiguous[0]:
                            ambiguous = (error, claim_fact, evidence_fact, reason)
                        continue
                    if index not in per_fact or error < per_fact[index][0]:
                        per_fact[index] = (error, evidence_fact)
                    if best is None or error < best[0]:
                        best = (error, claim_fact, evidence_fact, sentence)
        if best is None:
            if ambiguous is not None:
                _, c_fact, e_fact, reason = ambiguous
                return StanceSignal(
                    relation=PARTIAL,
                    reason=(
                        f"Số liệu {vn.figure(c_fact.value)} (tuyên bố) và {vn.figure(e_fact.value)} (tài liệu) không so sánh "
                        f"được tự động: {describe(reason)}."
                    ),
                    method="numeric",
                )
            if blocked is not None:
                reason, c_fact, e_fact = blocked
                return StanceSignal(
                    relation=CONTEXT,
                    reason=(
                        f"Có số liệu cùng đơn vị ({vn.figure(c_fact.value)} so với {vn.figure(e_fact.value)}) nhưng {describe(reason)}, "
                        "nên không phải mâu thuẫn."
                    ),
                    method="numeric",
                )
            return None
        error, c_fact, e_fact, sentence = best
        claim_q, evidence_q = c_fact.as_tuple(), e_fact.as_tuple()
        c_value, e_value = c_fact.value, e_fact.value
        other_period = _dated_to_other_year(sentence, claim)
        tolerance = self._tolerance(claim_q, evidence_q)
        if error <= tolerance:
            # GS-Mutation v1 (14/11): "giảm 12,8%" rewritten as "tăng 12,8%" stayed SUPPORTED in
            # 5 of 5 cases, because the figure still matched. The same figure going the other way
            # is a contradiction, not a match.
            reversed_word = _reversed_in(claim, sentence, e_value) if self.settings.figure_consistency_check else None
            other_base = _other_baseline(claim, sentence) if self.settings.figure_consistency_check else None
            if other_base and not reversed_word:
                # Same change, different base year: "giảm 39% so với 2017" against "giảm 39% so với 2020".
                return StanceSignal(
                    relation=PARTIAL,
                    reason=(
                        f"Số liệu khớp ({vn.figure(c_value)} ≈ {vn.figure(e_value)}) nhưng năm gốc khác: tuyên bố so với "
                        f"{claim.baseline}, tài liệu so với {other_base}; cần người xem."
                    ),
                    method="numeric",
                )
            if reversed_word:
                return StanceSignal(
                    relation=CONTRADICTS,
                    reason=(
                        f"Số liệu khớp ({vn.figure(c_value)} ≈ {vn.figure(e_value)}) nhưng ngược hướng: tuyên bố nói "
                        f"“{'giảm' if claim.direction == 'decrease' else 'tăng'}”, tài liệu nói “{reversed_word}”."
                    ),
                    method="numeric",
                    figures=(c_value, e_value),
                )
            # A claim with two figures where one matches and the other is far off is not
            # supported by the one that matches (GS-Mutation v1 M1: 58.4 Mt "chiếm 99,55%"
            # against 23.4 Mt "chiếm 99,55%" was SUPPORTED). A reviewer's case, not a verdict.
            off = [] if not self.settings.figure_consistency_check else [(err, e) for i, (err, e) in per_fact.items()
                   if claim_facts[i] is not c_fact and err >= self.settings.numeric_contradiction_error
                   and claim_facts[i].value != c_value]
            if off:
                err, e_other = min(off, key=lambda x: x[0])
                return StanceSignal(
                    relation=PARTIAL,
                    reason=(
                        f"Một số khớp ({vn.figure(c_value)} ≈ {vn.figure(e_value)}) nhưng số khác của tuyên bố lệch xa "
                        f"số cùng loại trong tài liệu ({vn.figure(e_other.value)}); cần người xem."
                    ),
                    method="numeric",
                )
            if other_period:
                return StanceSignal(
                    relation=PARTIAL,
                    reason=(
                        f"Số liệu khớp ({vn.figure(c_value)} ≈ {vn.figure(e_value)}) nhưng câu bằng chứng thuộc kỳ "
                        f"{other_period}, không phải kỳ {claim.period} của tuyên bố."
                    ),
                    method="numeric",
                )
            return StanceSignal(
                relation=SUPPORTS,
                reason=f"Số liệu khớp: {vn.figure(c_value)} ≈ {vn.figure(e_value)} (dung sai ±{vn.figure(round(tolerance * 100, 2))}% theo độ chính xác công bố).",
                method="numeric",
                figures=(c_value, e_value),
            )
        if error >= self.settings.numeric_contradiction_error:
            # Holdout v1 (PAN 2020, 15/11/2026): both CONTRADICTED were wrong. "Power consumption of compressor
            # reduces by 40%" met "consumption via online sales grew 25%" -- the claim names no metric the
            # taxonomy knows, so every sentence was compared; and an investment of VND 483 million met a
            # sponsorship of VND 700 million. Without the claim's metric, or for money in a claim that is not
            # about green finance, a gap goes to a reviewer.
            unanchored = not claim.metric and not (content_bigrams(claim.text) & content_bigrams(sentence))
            if self.settings.figure_consistency_check and (
                unanchored or (c_fact.unit == "currency" and claim.claim_type != "green_finance")
            ):
                return StanceSignal(
                    relation=PARTIAL,
                    reason=(
                        f"Số liệu lệch ({vn.figure(c_value)} so với {vn.figure(e_value)}) nhưng "
                        + ("chưa xác định được chỉ số của tuyên bố" if unanchored
                           else "đây là khoản tiền, không phải chỉ số môi trường của tuyên bố")
                        + ", nên không kết luận mâu thuẫn; cần người xem."
                    ),
                    method="numeric",
                )
            ratio = max(abs(c_value), abs(e_value)) / max(min(abs(c_value), abs(e_value)), 1e-9)
            if (claim.claim_type in FALLBACK_CLAIM_TYPES and ratio >= 3.0
                    and "unknown" in (c_fact.boundary, e_fact.boundary)):
                # claim-typing-v2: the type was inferred, the figures are 3x+ apart and the boundary is
                # unread on one side -- more often two different objects than a misstatement.
                return StanceSignal(
                    relation=PARTIAL,
                    reason=(
                        f"Số liệu lệch lớn ({vn.figure(c_value)} so với {vn.figure(e_value)}) nhưng chưa xác định được "
                        "hai số có cùng ranh giới; có thể là hai đối tượng khác nhau, cần người xem."
                    ),
                    method="numeric",
                )
            if other_period:
                return StanceSignal(
                    relation=CONTEXT,
                    reason=f"Số liệu thuộc kỳ {other_period}, không phải {claim.period}, nên không so sánh được.",
                    method="numeric",
                )
            return StanceSignal(
                relation=CONTRADICTS,
                reason=(
                    f"Số liệu lệch: tuyên bố {vn.figure(c_value)}, tài liệu {vn.figure(e_value)} "
                    f"(cùng {_same_dimensions(c_fact, e_fact)})."
                ),
                method="numeric",
                figures=(c_value, e_value),
            )
        # Between the published precision and a material difference: the
        # figures are about the same thing and do not agree. Arithmetic has
        # spoken, so no cue phrase in the same passage may confirm the claim.
        return StanceSignal(
            relation=PARTIAL,
            reason=(
                f"Số liệu gần nhưng lệch ngoài dung sai công bố: tuyên bố {vn.figure(c_value)}, "
                f"tài liệu {vn.figure(e_value)} (dung sai ±{vn.figure(round(tolerance * 100, 2))}%)."
            ),
            method="numeric",
        )

    def _absolute_share(self, claim: Claim, item: RetrievedEvidence) -> StanceSignal | None:
        """Share of a green instrument's proceeds used, against the 100% an absolute claim asserts."""
        found = allocated_share(claim.text, item.text)
        if found is None:
            return None
        share = found["share_pct"]
        gap = (100.0 - share) / 100.0
        head = (
            f"Tuyên bố “{found['absolute']}” nghĩa là 100% vốn {found['instrument']}; "
            f"tính từ đoạn này: {found['formula']}"
        )
        if gap <= 0.005:
            relation, tail = SUPPORTS, ", khớp với tuyên bố."
        elif gap >= self.settings.numeric_contradiction_error:
            relation, tail = CONTRADICTS, f", thấp hơn 100% là {vn.figure(round(gap * 100, 1))} điểm phần trăm."
        else:
            relation, tail = PARTIAL, ", chưa phải toàn bộ nhưng độ lệch dưới ngưỡng mâu thuẫn; cần người xem."
        return StanceSignal(relation=relation, reason=head + tail, method="numeric", figures=(100.0, share))

    def _internal_inconsistency(self, claim: Claim, item: RetrievedEvidence, numeric: StanceSignal) -> StanceSignal | None:
        """A figure in the claim's prose against the same report's data table (internal-inconsistency-v1).

        The contradiction guard stays the default: two numbers in one report are
        usually about two things. A same-document disagreement is let through only
        when the passage is a data table or data page, the figures are comparable
        under comparison-policy-v3 (now also by segment), the passage is dated to
        the claim's period (and its base year for a change), no figure is an OCR
        doubt, and nothing near it says the figure was restated. Anything less and
        the old behaviour holds.
        """
        if claim.source_chunk_id and item.chunk_id == claim.source_chunk_id:
            return None
        folded = normalize_for_match(item.text)
        if not (item.is_table or _DATA_PAGE_RE.search(folded)):
            return None
        if _RESTATED_RE.search(folded):
            return None
        if not claim.period or str(claim.period) not in item.text:
            return None
        if claim.direction and claim.baseline and str(claim.baseline) not in item.text:
            return None
        if self._unless_misread(claim, item, numeric).relation != CONTRADICTS:
            return None
        relation = CONTRADICTS if self.settings.internal_inconsistency == "contradict" else PARTIAL
        return StanceSignal(
            relation=relation,
            reason=(
                f"Không nhất quán nội bộ: {numeric.reason.rstrip('.')}; lời văn và bảng số liệu trong cùng "
                "tài liệu không khớp, cần người soát đặt hai dòng cạnh nhau."
            ),
            method="internal",
            figures=numeric.figures,
        )

    def _continuity_gap(self, claim: Claim, item: RetrievedEvidence) -> StanceSignal | None:
        """"Giảm liên tục từ 2020 đến 2025" needs every year, not two endpoints.

        A claim about a *continuous* trend asserts something at each step of the
        period. Two endpoints support "lower in 2025 than in 2020" and say
        nothing about the years between, so a missing year is reported as a gap
        rather than read as a smooth decline (P9).
        """
        if not _CONTINUOUS_RE.search(normalize_for_match(claim.text)):
            return None
        if not claim.baseline or not claim.period:
            return None
        try:
            first, last = sorted((int(claim.baseline), int(claim.period)))
        except ValueError:
            return None
        if last - first < 2:
            return None  # two adjacent years have nothing in between to miss

        seen: dict[str, float] = {}
        for sentence in self._metric_sentences(claim, item.text):
            for year, fact in _dated_quantities(sentence):
                seen.setdefault(year, fact.value)
        wanted = [str(year) for year in range(first, last + 1)]
        missing = [year for year in wanted if year not in seen]
        if not missing:
            return None  # the full series is present; the usual checks apply
        if len(missing) == len(wanted):
            return None  # nothing to say: no series at all, fall through
        return StanceSignal(
            relation=PARTIAL,
            reason=(
                f"Tuyên bố nói xu hướng **liên tục** {first}–{last} nhưng kho tài liệu thiếu "
                f"số liệu năm {', '.join(missing)}; hai đầu kỳ không chứng minh được từng năm đều giảm."
            ),
            method="numeric",
        )

    def _recomputed_change(self, claim: Claim, item: RetrievedEvidence) -> StanceSignal | None:
        """Re-derive the percentage the claim asserts from the figures behind it.

        Needs a claim that states a direction and a percentage, and evidence that
        carries a figure for the baseline period and one for the claim's period,
        in the same unit and with no dimension mismatch between them. Anything
        less is not enough to do the arithmetic, and the caller falls back to
        comparing figures directly.

        When the two figures are themselves percentages the answer is ambiguous
        by construction -- 20% to 30% is +10 percentage points and also +50%
        relative -- so both readings are computed and the claim is never called
        contradicted on the strength of one of them (P8).
        """
        claimed = next(
            (f for f in _claim_facts(claim.text) if f.unit == "%" and not f.is_target), None
        )
        if claimed is None or not claim.direction or not claim.baseline or not claim.period:
            return None

        base = current = None
        for sentence in self._metric_sentences(claim, item.text):
            for year, fact in _dated_quantities(sentence):
                if fact.unit == "%" and fact.value == claimed.value:
                    continue  # the claim's own figure quoted back
                if year == claim.baseline and base is None:
                    base = fact
                elif year == claim.period and current is None:
                    current = fact
        if base is None or current is None or base.value == 0:
            return None
        verdict, reason = eligibility(base, current)
        if verdict == NOT_COMPARABLE:
            return StanceSignal(
                relation=CONTEXT,
                reason=(
                    f"Có số liệu kỳ gốc và kỳ báo cáo nhưng {describe(reason)}, "
                    "nên không tính lại được mức thay đổi."
                ),
                method="numeric",
            )

        relative = (current.value - base.value) / abs(base.value) * 100.0
        claimed_signed = -claimed.value if claim.direction == "decrease" else claimed.value
        unit = base.unit
        calculation = (
            f"({vn.figure(current.value)} − {vn.figure(base.value)}) / {vn.figure(base.value)} = {vn.signed(round(relative, 2))}%"
        )
        tolerance = max(0.5, _half_digit(claimed.value))

        if base.unit == "%":
            # Two percentages: report both readings and let a reviewer choose.
            points = current.value - base.value
            matches = (
                abs(points - claimed_signed) <= tolerance
                or abs(relative - claimed_signed) <= tolerance
            )
            return StanceSignal(
                relation=PARTIAL,
                reason=(
                    f"Hai giá trị đều là tỷ lệ: chênh {vn.signed(round(points, 2))} điểm phần trăm, "
                    f"tương đương {vn.signed(round(relative, 2))}% tương đối. Tuyên bố nêu {vn.signed(claimed_signed)}% — "
                    + ("khớp một trong hai cách đọc; cần người xác nhận cách đo."
                       if matches else "không khớp cách đọc nào; cần người xem.")
                ),
                method="numeric",
            )

        difference = relative - claimed_signed
        if abs(difference) <= tolerance:
            return StanceSignal(
                relation=SUPPORTS,
                reason=(
                    f"Tính lại từ số liệu: {calculation} {unit}, khớp mức {vn.signed(claimed_signed)}% "
                    f"của tuyên bố (dung sai ±{vn.figure(round(tolerance, 2))} điểm phần trăm)."
                ),
                method="numeric",
                figures=(claimed.value, base.value, current.value),
            )
        material = max(tolerance, self.settings.numeric_contradiction_error * abs(claimed_signed))
        if abs(difference) >= material:
            return StanceSignal(
                relation=CONTRADICTS,
                reason=(
                    f"Tính lại từ số liệu: {calculation} {unit}, trong khi tuyên bố nêu "
                    f"{vn.signed(claimed_signed)}% — lệch {vn.signed(round(difference, 2))} điểm phần trăm."
                ),
                method="numeric",
                figures=(claimed.value, base.value, current.value),
            )
        return StanceSignal(
            relation=PARTIAL,
            reason=(
                f"Tính lại từ số liệu: {calculation} {unit}, gần nhưng chưa khớp mức "
                f"{vn.signed(claimed_signed)}% của tuyên bố."
            ),
            method="numeric",
        )

    def _tolerance(self, claim: tuple, evidence: tuple) -> float:
        """Relative tolerance for one pair (fraction of the claim value) -- policy `precision-v1`.

        Two figures agree when they differ by no more than the coarser of the
        two published precisions (half of the last significant digit), capped
        at `numeric_relative_tolerance` of the claim value so that a claim of
        "100%" is not matched by anything from 50 upwards. There is no global
        percentage any more: "12%" tolerates 11.5–12.5, "12,0%" only 11.95–12.05.
        """
        c_value, c_unit, c_half = claim
        _, e_unit, e_half = evidence
        # "100%" means all of it, not a figure rounded to the hundred (GS-Mutation v1.1 M5: "tự chủ 100%"
        # matched 98% under the 10% cap). The same for 0%. Only the published unit digit is tolerated.
        if self.settings.figure_consistency_check and c_unit == "%" and abs(c_value) in (0.0, 100.0):
            c_half = e_half = 0.5
        absolute = min(max(c_half, e_half), self.settings.numeric_relative_tolerance * abs(c_value))
        return absolute / max(abs(c_value), 1e-9)

    def _numeric_comparison(self, claim: Claim, evidence: list[RetrievedEvidence]) -> dict:
        """Audit record of every figure pair considered, with the eligibility verdict on each."""
        claim_facts = _claim_facts(claim.text)
        claim_scopes = emission_scopes(claim.text)
        pairs: list[dict] = []
        skipped: list[dict] = []
        matched = False
        closest = None
        for item in evidence:
            for sentence in self._metric_sentences(claim, item.text):
                for e_fact in facts_in(sentence):
                    for c_fact in claim_facts:
                        verdict, reason = eligibility(c_fact, e_fact)
                        if verdict == NOT_COMPARABLE:
                            if reason != "different_unit" and len(skipped) < 20:
                                skipped.append({
                                    "claim": c_fact.value, "evidence": e_fact.value, "unit": c_fact.unit,
                                    "reason": reason, "citation": item.citation,
                                    "claim_dimensions": c_fact.dimensions(),
                                    "evidence_dimensions": e_fact.dimensions(),
                                })
                            continue
                        relative_error = abs(e_fact.value - c_fact.value) / max(abs(c_fact.value), 1.0)
                        tolerance = self._tolerance(c_fact.as_tuple(), e_fact.as_tuple())
                        candidate = {
                            "claim": c_fact.value,
                            "claim_unit": c_fact.unit,
                            "evidence": e_fact.value,
                            "evidence_unit": e_fact.unit,
                            "relative_error": relative_error,
                            "tolerance": tolerance,
                            "eligibility": verdict,
                            "eligibility_reason": reason,
                            "citation": item.citation,
                        }
                        if len(pairs) < 30:
                            pairs.append(candidate)
                        if verdict == AMBIGUOUS:
                            continue
                        if closest is None or relative_error < closest["relative_error"]:
                            closest = candidate
                        if relative_error <= tolerance:
                            matched = True
        contradiction = bool(
            claim_facts
            and not matched
            and closest
            and closest["relative_error"] >= self.settings.numeric_contradiction_error
        )
        return {
            "claim_numbers": [(f.value, f.unit) for f in claim_facts],
            "claim_facts": [{"value": f.value, "unit": f.unit, **f.dimensions()} for f in claim_facts],
            "claim_scopes": _scopes(claim_scopes) if claim_scopes else None,
            "evidence_numbers": [(p["evidence"], p["evidence_unit"], p["citation"]) for p in pairs],
            "pairs_considered": pairs,
            "skipped_not_comparable": skipped,
            "matched": matched,
            "contradiction": contradiction,
            "closest_pair": closest,
            "tolerance_used": closest["tolerance"] if closest else None,
            "policy_id": "precision-v1",
            "eligibility_policy": ELIGIBILITY_POLICY,
            "contradiction_error_threshold": self.settings.numeric_contradiction_error,
            "calculation_method": "deterministic-relative-error",
        }

    def _direction_contradiction(self, claim: Claim, evidence: list[RetrievedEvidence]) -> bool:
        """The trend in the claim is reversed in the evidence.

        Read on accented text, whole words, and without the compounds that are
        not trends: "giảm thiểu" (mitigate), "tăng cường" (strengthen), "tăng
        trưởng" (growth). Only sentences about the claim's metric are read, so
        a rise in revenue does not reverse a fall in emissions.
        """
        if not claim.direction or not claim.metric:
            return False
        terms = self._metric_terms(claim)
        decrease = increase = False
        for item in evidence[:3]:
            for sentence in split_sentences(item.text) or [item.text]:
                if not any(term in normalize_for_match(sentence) for term in terms):
                    continue
                decrease = decrease or bool(_DECREASE_RE.search(sentence.lower()))
                increase = increase or bool(_INCREASE_RE.search(sentence.lower()))
        if claim.direction == "decrease" and increase and not decrease:
            return True
        if claim.direction == "increase" and decrease and not increase:
            return True
        return False

    def _attributes_matched(self, claim: Claim, text: str) -> tuple[set[str], set[str]]:
        """(attributes of the claim found in the passage, attributes the claim states).

        Read on the sentences about the claim's metric so a period found in a
        sentence about revenue does not count for an emissions claim.
        """
        stated: set[str] = set()
        matched: set[str] = set()
        sentences = self._metric_sentences(claim, text)
        joined = " ".join(sentences)
        folded = normalize_for_match(joined)
        if claim.metric:
            stated.add("metric")
            if sentences and any(term in folded for term in self._metric_terms(claim)):
                matched.add("metric")
        if claim.period and claim.period_source != "report_year":
            stated.add("period")
            if claim.period in YEAR_RE.findall(joined):
                matched.add("period")
        if claim.baseline:
            stated.add("baseline")
            if claim.baseline in YEAR_RE.findall(joined):
                matched.add("baseline")
        claim_scopes = emission_scopes(claim.text)
        if claim_scopes:
            stated.add("scopes")
            if emission_scopes(joined) == claim_scopes:
                matched.add("scopes")
        elif claim.scope:
            stated.add("scopes")
            entry = (self.taxonomy.get("scope_buckets") or {}).get(claim.scope) or {}
            terms = [normalize_for_match(t) for lang in ("vi", "en") for t in entry.get(lang) or []]
            if any(term in folded for term in terms):
                matched.add("scopes")
        if claim.direction:
            stated.add("direction")
            regex = _DECREASE_RE if claim.direction == "decrease" else _INCREASE_RE
            if regex.search(joined.lower()):
                matched.add("direction")
        return matched, stated

    @staticmethod
    def _metric_overlap(claim: Claim, evidence: list[RetrievedEvidence]) -> float:
        """Share of the claim's content tokens present in the top passages.

        Function words and bare years are excluded: "năm", "công ty" and "2024"
        gave an unrelated passage 18% overlap and a PARTIALLY_SUPPORTED status.
        """
        claim_tokens = content_tokens(claim.text)
        evidence_tokens = content_tokens(" ".join(item.text for item in evidence[:3]))
        return len(claim_tokens & evidence_tokens) / max(1, len(claim_tokens))

    def _topic_tokens(self, claim: Claim) -> set[str]:
        """Content words of the claim plus the taxonomy vocabulary of its type and metric.

        A cue counts only in a sentence that shares one of these. The taxonomy
        terms are what let a court's "environmental statements" connect to a
        claim that says "sustainable future" without sharing a word with it.
        """
        tokens = content_tokens(claim.text)
        for section, key in (("claim_types", claim.claim_type), ("metrics", claim.metric)):
            entry = (self.taxonomy.get(section) or {}).get(key) if key else None
            for language in ("vi", "en"):
                for term in (entry or {}).get(language) or []:
                    tokens.update(content_tokens(term))
        return tokens

    def _taxonomy_terms(self, claim: Claim) -> set[str]:
        """Accented vocabulary of the claim's type and metric from the taxonomy."""
        terms: set[str] = set()
        for section, key in (("claim_types", claim.claim_type), ("metrics", claim.metric)):
            entry = (self.taxonomy.get(section) or {}).get(key) if key else None
            for language in ("vi", "en"):
                terms.update((entry or {}).get(language) or [])
        return terms

    def _metric_terms(self, claim: Claim) -> list[str]:
        entry = (self.taxonomy.get("metrics") or {}).get(claim.metric) if claim.metric else None
        return [
            normalize_for_match(term)
            for language in ("vi", "en")
            for term in (entry or {}).get(language) or []
        ]

    def _metric_sentences(self, claim: Claim, text: str) -> list[str]:
        """Sentences of the passage that mention the claim's metric (all, when it has none)."""
        terms = self._metric_terms(claim)
        sentences = split_sentences(text) or [text]
        if not terms:
            return sentences
        return [s for s in sentences if any(term in normalize_for_match(s) for term in terms)]

    def _audit(self, result: VerificationResult) -> None:
        self.audit.write(
            "claim_verified",
            {
                "claim_id": result.claim.claim_id,
                "status": result.status,
                "citations": [e.citation for e in result.evidence],
                "stances": [
                    {"citation": e.citation, "relation": e.relation, "method": e.relation_method}
                    for e in result.evidence
                ],
                "requires_llm_review": result.requires_llm_review,
                "warnings": result.warnings,
            },
        )


_DECREASE_RE = re.compile(
    r"(?<!\w)(?:giảm(?!\s+(?:thiểu|nhẹ|giá|tải|trừ))|cắt giảm|decrease[ds]?|reduc(?:ed|tion)|lower(?:ed)?|fell|declined?)(?!\w)"
)
_INCREASE_RE = re.compile(
    r"(?<!\w)(?:tăng(?!\s+(?:cường|trưởng|tốc|ca|giá))|gia tăng|increase[ds]?|rose|grew|higher|climbed)(?!\w)"
)


def _load_taxonomy(path: str) -> dict:
    resolved = Path(path)
    if not resolved.exists():
        resolved = Path(__file__).resolve().parents[3] / path
    try:
        return yaml.safe_load(resolved.read_text(encoding="utf-8")) or {}
    except OSError:
        return {}


def _dated_to_other_year(sentence: str, claim: Claim) -> str | None:
    """The year the sentence is about, when it is not the claim's period or baseline."""
    if not claim.period or claim.period_source == "report_year":
        return None
    years = set(YEAR_RE.findall(sentence))
    if not years or claim.period in years or (claim.baseline and claim.baseline in years):
        return None
    return "/".join(sorted(years))


_BASE_YEAR_RE = re.compile(r"so (?:voi|với) (?:nam |năm |cung ky nam |cùng kỳ năm )?((?:19|20)\d\d)")


def _other_baseline(claim: Claim, sentence: str) -> str | None:
    """The base year the sentence compares with, when the claim names a different one."""
    if not claim.baseline:
        return None
    years = {m.group(1) for m in _BASE_YEAR_RE.finditer(sentence.lower())}
    return sorted(years)[0] if years and claim.baseline not in years else None


def _reversed_in(claim: Claim, sentence: str, value: float | None = None) -> str | None:
    """The trend word governing the matched figure when it is the opposite of the claim's.

    First the nearest trend word in the 50 characters before the figure ("…, mức tiêu thụ gas giảm
    tương ứng là 39%" while production "tăng 20%" earlier in the sentence, GS-Bench C3); else the
    sentence's only trend word, as before.
    """
    if claim.direction not in ("decrease", "increase"):
        return None
    low = sentence.lower()
    if value is not None:
        at = _position_of(sentence, value)
        if at is not None:
            left = low[max(0, at - 50):at]
            words = [(m.start(), "decrease", m.group(0)) for m in _DECREASE_RE.finditer(left)]
            words += [(m.start(), "increase", m.group(0)) for m in _INCREASE_RE.finditer(left)]
            if words:
                _, kind, word = max(words)
                return word if kind != claim.direction else None
    decrease, increase = _DECREASE_RE.search(low), _INCREASE_RE.search(low)
    if claim.direction == "increase" and decrease and not increase:
        return decrease.group(0)
    if claim.direction == "decrease" and increase and not decrease:
        return increase.group(0)
    return None


def _scopes(scopes) -> str:
    return "+".join(str(n) for n in sorted(scopes))


def _measurements(text: str) -> list[tuple[float, str | None, float]]:
    """Quantities (value, unit, half-unit of precision), with bare years dropped.

    A year is a label, not a measurement: comparing the 2024 in a claim against
    the 2023 in a table produces a 0.05% relative error and a false SUPPORTS.
    """
    return [q for q in parse_quantities(text) if q[0] < 1900 or q[0] > 2100]


# The five attributes the rubric scores, in the order a reviewer fills them in.
_ATTRIBUTE_LABELS = {
    "metric": "chỉ số cụ thể",
    "values": "số liệu",
    "period": "kỳ báo cáo",
    "baseline": "năm gốc để so sánh",
    "scope": "phạm vi / ranh giới",
}


def missing_attributes(claim: Claim) -> list[str]:
    """Which of the five mandatory attributes the claim itself does not state.

    The one definition: frontend/src/lib/claims.js `attributeStates` mirrors it for
    the queue tag and the attribute card, and Studio names its result.
    """
    missing = []
    if not claim.metric:
        missing.append("metric")
    if not claim.values:
        missing.append("values")
    if not claim.period:
        missing.append("period")
    if (claim.direction or claim.is_future_commitment) and not claim.baseline:
        missing.append("baseline")
    if not claim.scope and not emission_scopes(claim.text):
        missing.append("scope")
    return missing


def _gap_sentence(claim: Claim) -> str:
    gaps = missing_attributes(claim)
    if not gaps:
        return "Tuyên bố có đủ năm thuộc tính; chưa tìm được nguồn đối chiếu độc lập."
    return "Tuyên bố thiếu: " + ", ".join(_ATTRIBUTE_LABELS[name] for name in gaps) + "."


# Words that turn a claim about a period into a claim about every year in it.
_CONTINUOUS_RE = re.compile(
    r"(?<!\w)(?:lien tuc|hang nam|tung nam|moi nam|nam nao cung|deu dan|"
    r"year[- ]on[- ]year|every year|each year|consistently|continuously)(?!\w)"
)


def _half_digit(value: float) -> float:
    """Half of the last digit the figure was written to: 20 -> 0.5, 20.5 -> 0.05."""
    text = f"{value:g}"
    decimals = len(text.split(".")[1]) if "." in text else 0
    return 0.5 * (10 ** -decimals)


def _dated_quantities(sentence: str) -> list[tuple[str, NumericFact]]:
    """Figures in the sentence paired with the year each one belongs to.

    A disclosure writes both endpoints in one line -- "năm 2020 là 100.000 tấn
    CO2e, năm 2025 là 80.000 tấn CO2e" -- so a figure is attributed to the
    nearest year stated before it. A figure with no year before it is dropped
    rather than guessed at.
    """
    pairs: list[tuple[str, NumericFact]] = []
    for fact in facts_in(sentence):
        position = _position_of(sentence, fact.value)
        if position is None:
            continue
        years = YEAR_RE.findall(sentence[:position])
        if not years:
            continue
        pairs.append((years[-1], fact))
    return pairs


def _position_of(sentence: str, value: float) -> int | None:
    """Where the figure is written, matched on digit boundaries.

    A plain substring search puts "20" inside "2020" and attributes a figure to
    the wrong year -- or to no year at all.
    """
    written = {
        f"{value:g}",
        f"{value:g}".replace(".", ","),
        f"{value:,.0f}".replace(",", "."),
        f"{value:,.0f}",
    }
    for text in sorted(written, key=len, reverse=True):
        match = re.search(r"(?<![\d.,])" + re.escape(text) + r"(?![\d])", sentence)
        if match:
            return match.start()
    return None


def _claim_facts(text: str) -> list[NumericFact]:
    """Figures in the claim with their dimensions; a claim may span a sentence boundary."""
    facts: list[NumericFact] = []
    for sentence in split_sentences(text) or [text]:
        facts.extend(facts_in(sentence))
    return facts


def _same_dimensions(a: NumericFact, b: NumericFact) -> str:
    """The dimensions both facts state, for the rationale of a contradiction."""
    parts = []
    if a.basis != "unknown":
        parts.append({"absolute": "số tuyệt đối", "intensity": "cường độ",
                      "percentage_share": "tỷ trọng", "percentage_change": "mức thay đổi"}.get(a.basis, a.basis))
    if a.boundary != "unknown":
        parts.append(f"ranh giới {a.boundary}")
    if a.scopes:
        parts.append(f"Scope {_scopes(a.scopes)}")
    if a.technology:
        parts.append(f"công nghệ {a.technology}")
    return ", ".join(parts) or "đơn vị"


def _reading_warnings(claim: Claim, misread: list[str]) -> list[str]:
    """What a reviewer is told about numbers OCR was unsure of, on the claim's side and the evidence's."""
    out = []
    if claim.doubtful_numbers:
        sure = f" (trang đọc với độ tin cậy trung bình {claim.ocr_confidence:.0f}/100)" if claim.ocr_confidence else ""
        out.append(
            f"Tuyên bố lấy từ trang quét{sure}; số {', '.join(claim.doubtful_numbers[:4])} được đọc với độ tin cậy "
            "thấp, cần đối chiếu trang gốc."
        )
    if misread:
        out.append(
            "Không dùng so khớp số liệu ở đoạn sau vì có số do máy đọc ảnh chữ (OCR) đọc chưa chắc: "
            + "; ".join(misread[:3])
        )
    return out
