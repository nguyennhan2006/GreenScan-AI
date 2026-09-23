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
        for item in external:
            matched, stated = self._attributes_matched(claim, item.text)
            required = {"metric"} | (stated & {"period", "scopes"})
            if required <= matched and len(matched) >= self.settings.support_min_attributes:
                return (
                    VerificationStatus.SUPPORTED,
                    f"Một nguồn ngoài tài liệu tuyên bố xác nhận: {item.relation_reason} "
                    f"Thuộc tính khớp: {', '.join(sorted(matched))}.",
                )
            weak.append(", ".join(sorted(matched)) or "không")
        if external:
            return (
                VerificationStatus.PARTIALLY_SUPPORTED,
                "Có xác nhận định tính từ nguồn khác nhưng chưa có số liệu và câu xác nhận "
                f"không nêu đủ chỉ số/kỳ/phạm vi của tuyên bố (thuộc tính khớp: {weak[0]}); cần người xem.",
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
            topic_terms=self._taxonomy_terms(claim),
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

        Comparable is decided by `numeric_facts.eligibility` before any
        arithmetic: same canonical unit, and no explicit mismatch of basis
        (share vs change vs absolute vs intensity), organisational boundary,
        technology, metric variant or GHG scope. A pair the rule marks
        AMBIGUOUS (target vs actual, or a gap of 20-100x with a dimension
        unread) is handed to the reviewer as PARTIAL, never as CONTRADICTED.
        Only sentences about the claim's metric are read, and -- when the claim
        names a period -- a sentence dated to some other year is not support.
        """
        claim_facts = _claim_facts(claim.text)
        if not claim_facts:
            return None
        best = None        # (error, claim_fact, evidence_fact, sentence)
        ambiguous = None   # (error, claim_fact, evidence_fact, reason)
        blocked = None     # (reason, claim_fact, evidence_fact)
        for sentence in self._metric_sentences(claim, item.text):
            for evidence_fact in facts_in(sentence):
                for claim_fact in claim_facts:
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
                    if best is None or error < best[0]:
                        best = (error, claim_fact, evidence_fact, sentence)
        if best is None:
            if ambiguous is not None:
                _, c_fact, e_fact, reason = ambiguous
                return StanceSignal(
                    relation=PARTIAL,
                    reason=(
                        f"Số liệu {c_fact.value} (tuyên bố) và {e_fact.value} (tài liệu) không so sánh "
                        f"được tự động: {describe(reason)}."
                    ),
                    method="numeric",
                )
            if blocked is not None:
                reason, c_fact, e_fact = blocked
                return StanceSignal(
                    relation=CONTEXT,
                    reason=(
                        f"Có số liệu cùng đơn vị ({c_fact.value} vs {e_fact.value}) nhưng {describe(reason)}, "
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
        if error >= self.settings.numeric_contradiction_error:
            if other_period:
                return StanceSignal(
                    relation=CONTEXT,
                    reason=f"Số liệu thuộc kỳ {other_period}, không phải {claim.period}, nên không so sánh được.",
                    method="numeric",
                )
            return StanceSignal(
                relation=CONTRADICTS,
                reason=(
                    f"Số liệu lệch: tuyên bố {c_value}, tài liệu {e_value} "
                    f"(cùng {_same_dimensions(c_fact, e_fact)})."
                ),
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
        if claim.period:
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


# The five attributes the rubric scores, in the order a reviewer fills them in.
_ATTRIBUTE_LABELS = {
    "metric": "chỉ số cụ thể",
    "values": "số liệu",
    "period": "kỳ báo cáo",
    "baseline": "năm gốc để so sánh",
    "scope": "phạm vi / ranh giới",
}


def missing_attributes(claim: Claim) -> list[str]:
    """Which of the five mandatory attributes the claim itself does not state."""
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
