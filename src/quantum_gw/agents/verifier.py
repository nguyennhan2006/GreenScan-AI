from __future__ import annotations

import re
from pathlib import Path

import yaml

from quantum_gw.domain.enums import VerificationStatus
from quantum_gw.domain.models import Claim, RetrievedEvidence, VerificationResult
from quantum_gw.settings import VerificationSettings
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.utils.text import (
    YEAR_RE,
    content_bigrams,
    content_tokens,
    emission_scopes,
    normalize_for_match,
    parse_quantities,
    split_sentences,
)
from quantum_gw.verification.stance import (
    CONTEXT,
    CONTRADICTS,
    PARTIAL,
    SUPPORTS,
    StanceLexicon,
    StanceSignal,
    qualitative_stance,
)


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
    ):
        self.settings = settings
        self.audit = audit
        self.lexicon = lexicon or StanceLexicon()
        self._llm_judge = llm_judge
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

            self._llm_judge = LLMStanceJudge()
        return self._llm_judge

    def run(self, claim: Claim, evidence: list[RetrievedEvidence]) -> VerificationResult:
        warnings: list[str] = []
        clean_evidence = []
        for item in evidence:
            if item.suspicious_instruction:
                warnings.append(f"Excluded suspicious document instruction: {item.citation}")
                if self.settings.injection_policy == "exclude":
                    continue
            clean_evidence.append(item)

        if not clean_evidence:
            result = VerificationResult(
                claim=claim,
                status=VerificationStatus.INSUFFICIENT_EVIDENCE,
                rationale="No admissible evidence passed the retrieval threshold.",
                evidence=[],
                warnings=warnings,
            )
            self._audit(result)
            return result

        numeric = self._numeric_comparison(claim, clean_evidence)

        escalated = False
        for item in clean_evidence:
            signal = self._stance(claim, item)
            if signal.method == "llm":
                escalated = True
            item.relation = signal.relation
            item.relation_reason = signal.reason
            item.relation_method = signal.method

        status, rationale = self._status(claim, clean_evidence, numeric)
        if escalated:
            warnings.append(
                "Một phần lập trường bằng chứng do mô hình ngôn ngữ đề xuất; cần người xác nhận."
            )

        result = VerificationResult(
            claim=claim,
            status=status,
            rationale=rationale,
            evidence=clean_evidence,
            computed_values=numeric,
            warnings=warnings,
            requires_llm_review=escalated,
        )
        self._audit(result)
        return result

    # ---------- status ----------

    def _status(
        self,
        claim: Claim,
        evidence: list[RetrievedEvidence],
        numeric: dict,
    ) -> tuple[VerificationStatus, str]:
        best = evidence[0]
        overlap = self._metric_overlap(claim, evidence)
        contradicting = [item for item in evidence if item.relation == CONTRADICTS]

        if contradicting:
            reason = contradicting[0].relation_reason
            return (
                VerificationStatus.CONTRADICTED,
                f"Bằng chứng đã truy xuất bác bỏ tuyên bố. {reason}",
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
        if external:
            reason = external[0].relation_reason
            return (
                VerificationStatus.SUPPORTED,
                f"Một nguồn ngoài tài liệu tuyên bố xác nhận: {reason}",
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
        if best.score >= self.settings.strong_support_score and overlap >= 0.30:
            return (
                VerificationStatus.PARTIALLY_SUPPORTED,
                "Relevant evidence was found, but the claim is not fully verified at the "
                "same scope, period or precision.",
            )
        if best.score >= self.settings.partial_support_score and overlap >= 0.25:
            return (
                VerificationStatus.PARTIALLY_SUPPORTED,
                "Evidence is related but incomplete; additional baseline, scope or "
                "assurance is required.",
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

    # ---------- per-passage stance ----------

    def _stance(self, claim: Claim, item: RetrievedEvidence) -> StanceSignal:
        """Stance of one passage towards the claim.

        Retrieval rank measures similarity, which is a different question: the
        top-ranked passage can be the one that contradicts the claim. A reviewer
        needs the stance per passage, not one status for the whole set.
        """
        numeric = self._numeric_relation(claim, item)
        if numeric is not None:
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

        judge = self.llm_judge
        if judge is not None and overlap >= self.settings.llm_stance_min_overlap:
            verdict = judge.judge(claim.text, item.text)
            if verdict is not None:
                return verdict

        if overlap >= 0.30:
            return StanceSignal(
                relation=PARTIAL,
                reason="Cùng chủ đề nhưng chưa đủ số liệu để xác nhận.",
                method="similarity",
            )
        return StanceSignal(
            relation=CONTEXT,
            reason="Liên quan về ngữ cảnh, không xác nhận hay bác bỏ.",
            method="similarity",
        )

    def _numeric_relation(self, claim: Claim, item: RetrievedEvidence) -> StanceSignal | None:
        """Stance from comparable figures, or None when there is no pair to compare.

        Comparable means the same canonical unit, a sentence about the claim's
        metric, the same GHG scopes when both name them, and -- when the claim
        names a period -- a sentence that is not dated to some other year. A
        2023 figure agreeing with a claim about 2024 is not support for it.
        """
        claim_numbers = _measurements(claim.text)
        if not claim_numbers:
            return None
        claim_scopes = emission_scopes(claim.text)
        best = None  # (error, claim_q, evidence_q, sentence)
        for sentence in self._metric_sentences(claim, item.text):
            closest = _closest_pair(claim_numbers, _measurements(sentence))
            if closest and (best is None or closest[0] < best[0]):
                best = (*closest, sentence)
        if best is None:
            return None
        error, claim_q, evidence_q, sentence = best
        c_value, e_value = claim_q[0], evidence_q[0]
        item_scopes = emission_scopes(sentence) or emission_scopes(item.text)
        boundary_differs = bool(claim_scopes and item_scopes and claim_scopes != item_scopes)
        other_period = _dated_to_other_year(sentence, claim)
        tolerance = self._tolerance(claim_q, evidence_q)
        if error <= tolerance:
            if boundary_differs:
                return StanceSignal(
                    relation=PARTIAL,
                    reason=(
                        f"Số liệu khớp ({c_value} ≈ {e_value}) nhưng khác ranh giới phát thải: "
                        f"tuyên bố Scope {_scopes(claim_scopes)}, tài liệu Scope {_scopes(item_scopes)}."
                    ),
                    method="numeric",
                )
            if other_period:
                return StanceSignal(
                    relation=PARTIAL,
                    reason=(
                        f"Số liệu khớp ({c_value} ≈ {e_value}) nhưng câu bằng chứng thuộc kỳ "
                        f"{other_period}, không phải kỳ {claim.period} của tuyên bố."
                    ),
                    method="numeric",
                )
            return StanceSignal(
                relation=SUPPORTS,
                reason=f"Số liệu khớp: {c_value} ≈ {e_value} (dung sai ±{tolerance * 100:.2g}% theo độ chính xác công bố).",
                method="numeric",
            )
        if error >= 0.35:
            if boundary_differs or other_period:
                why = (
                    f"khác ranh giới phát thải (Scope {_scopes(claim_scopes)} vs {_scopes(item_scopes)})"
                    if boundary_differs else f"thuộc kỳ {other_period}, không phải {claim.period}"
                )
                return StanceSignal(
                    relation=CONTEXT,
                    reason=f"Số liệu {why} nên không so sánh được.",
                    method="numeric",
                )
            return StanceSignal(
                relation=CONTRADICTS,
                reason=f"Số liệu lệch: tuyên bố {c_value}, tài liệu {e_value}.",
                method="numeric",
            )
        # Between the published precision and a material difference: the
        # figures are about the same thing and do not agree. Arithmetic has
        # spoken, so no cue phrase in the same passage may confirm the claim.
        return StanceSignal(
            relation=PARTIAL,
            reason=(
                f"Số liệu gần nhưng lệch ngoài dung sai công bố: tuyên bố {c_value}, "
                f"tài liệu {e_value} (dung sai ±{tolerance * 100:.2g}%)."
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
        c_value, _, c_half = claim
        _, _, e_half = evidence
        absolute = min(max(c_half, e_half), self.settings.numeric_relative_tolerance * abs(c_value))
        return absolute / max(abs(c_value), 1e-9)

    def _numeric_comparison(self, claim: Claim, evidence: list[RetrievedEvidence]) -> dict:
        claim_numbers = _measurements(claim.text)
        claim_scopes = emission_scopes(claim.text)
        evidence_numbers = []
        skipped_boundary = []
        for item in evidence:
            item_scopes = emission_scopes(item.text)
            if claim_scopes and item_scopes and claim_scopes != item_scopes:
                skipped_boundary.append({"citation": item.citation, "scopes": _scopes(item_scopes)})
                continue
            evidence_numbers.extend(
                (value, unit, half, item.citation)
                for value, unit, half in self._metric_measurements(claim, item.text)
            )
        matched = False
        closest = None
        for claim_q in claim_numbers:
            c_value, c_unit, _ = claim_q
            for e_value, e_unit, e_half, citation in evidence_numbers:
                if not _compatible_units(c_unit, e_unit):
                    continue
                relative_error = abs(e_value - c_value) / max(abs(c_value), 1.0)
                tolerance = self._tolerance(claim_q, (e_value, e_unit, e_half))
                candidate = {
                    "claim": c_value,
                    "claim_unit": c_unit,
                    "evidence": e_value,
                    "evidence_unit": e_unit,
                    "relative_error": relative_error,
                    "tolerance": tolerance,
                    "citation": citation,
                }
                if closest is None or relative_error < closest["relative_error"]:
                    closest = candidate
                if relative_error <= tolerance:
                    matched = True
        contradiction = bool(
            claim_numbers
            and evidence_numbers
            and not matched
            and closest
            and closest["relative_error"] >= 0.35
        )
        return {
            "claim_numbers": [(v, u) for v, u, _ in claim_numbers],
            "claim_scopes": _scopes(claim_scopes) if claim_scopes else None,
            "evidence_numbers": [(v, u, c) for v, u, _, c in evidence_numbers[:30]],
            "skipped_boundary_mismatch": skipped_boundary[:10],
            "matched": matched,
            "contradiction": contradiction,
            "closest_pair": closest,
            "tolerance_used": closest["tolerance"] if closest else None,
            "policy_id": "precision-v1",
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

    def _metric_measurements(self, claim: Claim, text: str) -> list[tuple[float, str | None, float]]:
        """Figures from the sentences that talk about the claim's metric.

        A passage can carry several figures about several things; comparing the
        claim's 50% renewables against a 12% emissions increase in the same
        passage produced a contradiction about nothing. Without a metric on the
        claim every sentence is eligible.
        """
        terms = self._metric_terms(claim)
        if not terms:
            return _measurements(text)
        eligible = [
            sentence for sentence in (split_sentences(text) or [text])
            if any(term in normalize_for_match(sentence) for term in terms)
        ]
        return [value for sentence in eligible for value in _measurements(sentence)]

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


def _compatible_units(claim_unit: str | None, evidence_unit: str | None) -> bool:
    """Same canonical unit, and a unit on both sides.

    Two bare numbers are counts of unknown things -- "2 nhà máy" against "3
    dự án", a page number against a section number -- and agreeing or
    disagreeing says nothing about the claim.
    """
    return claim_unit is not None and claim_unit == evidence_unit


def _closest_pair(claim_numbers: list[tuple], evidence_numbers: list[tuple]) -> tuple | None:
    """(relative error, claim quantity, evidence quantity) for the closest unit-compatible pair."""
    closest = None
    for claim_q in claim_numbers:
        for evidence_q in evidence_numbers:
            if not _compatible_units(claim_q[1], evidence_q[1]):
                continue
            error = abs(evidence_q[0] - claim_q[0]) / max(abs(claim_q[0]), 1.0)
            if closest is None or error < closest[0]:
                closest = (error, claim_q, evidence_q)
    return closest


def _dated_to_other_year(sentence: str, claim: Claim) -> str | None:
    """The year the sentence is about, when it is not the claim's period or baseline."""
    if not claim.period:
        return None
    years = set(YEAR_RE.findall(sentence))
    if not years or claim.period in years or (claim.baseline and claim.baseline in years):
        return None
    return "/".join(sorted(years))


def _scopes(scopes) -> str:
    return "+".join(str(n) for n in sorted(scopes))


def _measurements(text: str) -> list[tuple[float, str | None, float]]:
    """Quantities (value, unit, half-unit of precision), with bare years dropped.

    A year is a label, not a measurement: comparing the 2024 in a claim against
    the 2023 in a table produces a 0.05% relative error and a false SUPPORTS.
    """
    return [q for q in parse_quantities(text) if q[0] < 1900 or q[0] > 2100]
