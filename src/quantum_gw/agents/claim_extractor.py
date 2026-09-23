from __future__ import annotations

import re
from pathlib import Path

import yaml

from quantum_gw.domain.enums import DocumentRole
from quantum_gw.domain.models import Claim, EvidenceChunk
from quantum_gw.settings import ClaimSettings
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.utils.text import (
    YEAR_RE,
    normalize_for_match,
    parse_numbers,
    split_sentences,
    stable_id,
)

# Lexicon languages, in the order used to break a tie when a sentence matches
# both equally. Vietnamese first: the deployment target is Vietnamese issuers.
LANGUAGES = ("vi", "en")

# Section enumerators and separators that mark a heading or a table-of-contents
# line: "4.1 | PHÁT THẢI", "2) Năng lượng", "III. Môi trường", "Chương 3 –".
_ENUMERATOR_RE = re.compile(r"^\s*(?:\d+(?:\.\d+)*|[IVXivx]+|[A-Za-z])\s*[.)|:\-–—]\s*\S")
_TOC_DOTS_RE = re.compile(r"\.{4,}\s*\d+\s*$")
# "1 GIỚI THIỆU BÁO CÁO", "5.1 KIỂM KÊ": a section number followed by a caps word.
_NUMBERED_CAPS_RE = re.compile(r"^\s*\d+(?:\.\d+)*\s+[A-ZÀ-Ỹ]{2,}")
# Three or more consecutive ALL-CAPS words anywhere: a heading glued to body
# text by the PDF text flow ("HÒA PHÁT trò nền tảng ...").
_CAPS_RUN_RE = re.compile(r"(?:\b[A-ZÀ-Ỹ]{2,}\b[\s&/,-]+){2,}\b[A-ZÀ-Ỹ]{2,}\b")
# Table-of-contents entry: short line ending in a page number.
_TRAILING_PAGE_RE = re.compile(r"\s\d{1,3}\s*$")
# A claim asserts something: it has a figure, a trend, a pledge, or a verb
# that commits the subject. Noun phrases ("quản lý năng lượng và khí nhà
# kính") match the lexicon and assert nothing.
_PREDICATE_VI_RE = re.compile(
    r"(?<!\w)(?:đã|đang|sẽ|được|đạt|giảm|tăng|thực hiện|triển khai|cam kết|hoàn thành|áp dụng|"
    r"sử dụng|đầu tư|xây dựng|lắp đặt|tuân thủ|kiểm kê|chứng nhận|phát triển|đảm bảo|bảo đảm|"
    r"tiết kiệm|tái chế|thu hồi|xử lý|cung cấp|chuyển đổi|vận hành|duy trì|hướng tới|hướng đến|"
    r"là|có|không|chiếm|đóng góp|góp phần|mua|bán|ký|tham gia|mở rộng|nâng cao|cải thiện|tối ưu)(?!\w)"
)
# English: a finite verb or modal is enough; the list is deliberately broad
# because English marketing copy is short ("Join us in creating a more
# sustainable future.") and still asserts something.
_PREDICATE_EN_RE = re.compile(
    r"(?<!\w)(?:is|are|was|were|be|been|has|have|had|will|would|can|could|shall|should|may|might|do|does|did|"
    r"join|\w+ed|\w+ing|\w+es|\w+s)(?!\w)",
    re.IGNORECASE,
)
_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
# A GRI disclosure index ("305-1", "306-4") or a line that opens with a unit
# ("Tấn 131.639 ...", "GJ 193.403.521 ...") is a row of an indicator table read
# left to right. It is evidence for a claim made elsewhere, not a claim: the
# Hòa Phát waste table produced five "claims" that contradicted each other.
_GRI_INDEX_RE = re.compile(r"(?<![\w-])(?:20[1-9]|30[1-9]|4[01]\d)-\d{1,2}(?![\w-])")
_UNIT_LEAD_RE = re.compile(
    r"^\s*(?:tan|tonnes?|tons?|gj|mj|tj|kwh|mwh|gwh|m3|kg|%|tco2e?|tan co2e?|ha)\s*[\d(]", re.IGNORECASE
)


def heading_reason(sentence: str) -> str | None:
    """Why this line is a heading, a caption or a table-of-contents entry -- or None.

    Headings passed the lexicon ("PHÁT THẢI KHÍ NHÀ KÍNH" contains an emissions
    term) and became claims: 419 claims from one Hòa Phát report, 67 with a
    figure, and the demo's first claim was a section title. A heading asserts
    nothing, so it cannot be verified or scored; the honest output is to reject
    it and say why.
    """
    stripped = sentence.strip()
    if _TOC_DOTS_RE.search(stripped):
        return "table_of_contents"
    if _GRI_INDEX_RE.search(stripped) or _UNIT_LEAD_RE.match(normalize_for_match(stripped)):
        return "table_row"
    if " | " in stripped or _ENUMERATOR_RE.match(stripped) or _NUMBERED_CAPS_RE.match(stripped):
        return "section_label"
    if _CAPS_RUN_RE.search(stripped):
        return "caps_run"
    words = _WORD_RE.findall(stripped)
    if _TRAILING_PAGE_RE.search(stripped) and len(words) < 10 and not re.search(r"\d\s*%|tco2|tấn|kwh|mwh", stripped.lower()):
        return "table_of_contents"
    letters = [c for c in stripped if c.isalpha()]
    if len(letters) >= 3 and sum(c.isupper() for c in letters) / len(letters) >= 0.7:
        return "all_caps"
    if len(words) < 6 and not any(c.isdigit() for c in stripped):
        return "too_short"
    # PDF text flow: a sentence that starts mid-word ("hợp với định hướng...")
    # is the tail of a line broken elsewhere, not a statement.
    first = next((c for c in stripped if c.isalpha()), "")
    if first and first.islower() and len(words) < 15:
        return "fragment"
    vietnamese = normalize_for_match(stripped) != stripped.lower()
    predicate = _PREDICATE_VI_RE if vietnamese else _PREDICATE_EN_RE
    if not predicate.search(stripped.lower()):
        return "no_predicate"
    return None


def _terms(entry: dict, language: str) -> list[str]:
    """Normalized terms for one language of one taxonomy entry."""
    return [normalize_for_match(term) for term in entry.get(language) or []]


def _by_language(section: dict) -> dict[str, dict[str, list[str]]]:
    """{bucket: {language: [normalized terms]}} for a taxonomy section."""
    return {
        name: {language: _terms(entry, language) for language in LANGUAGES}
        for name, entry in section.items()
    }


def _flat(buckets: dict[str, dict[str, list[str]]], name: str) -> list[str]:
    return [term for terms in buckets[name].values() for term in terms]


class ClaimExtractionAgent:
    def __init__(
        self,
        settings: ClaimSettings,
        audit: AuditLogger,
        taxonomy_path: str = "configs/taxonomy.yaml",
    ):
        self.settings = settings
        self.audit = audit
        path = Path(taxonomy_path)
        if not path.exists():
            path = Path(__file__).resolve().parents[3] / taxonomy_path
        self.taxonomy = yaml.safe_load(path.read_text(encoding="utf-8"))

        self.claim_types = _by_language(self.taxonomy["claim_types"])
        self.priority = {
            name: int(entry.get("priority", 1))
            for name, entry in self.taxonomy["claim_types"].items()
        }
        patterns = _by_language(self.taxonomy["risk_patterns"])
        self.vague_by_language = patterns["vague_terms"]
        self.vague_terms = _flat(patterns, "vague_terms")
        self.reduction_terms = _flat(patterns, "reduction_terms")
        self.increase_terms = _flat(patterns, "increase_terms")
        self.future_terms = _flat(patterns, "future_terms")
        self.scope_buckets = _by_language(self.taxonomy["scope_buckets"])
        self.metrics = _by_language(self.taxonomy["metrics"])

    def run(self, chunks: list[EvidenceChunk]) -> list[Claim]:
        claims: list[Claim] = []
        seen: set[str] = set()
        rejected: dict[str, int] = {}
        # Every refused sentence, kept for the extract layer and for the
        # reviewer's "what did it ignore" question (data/layers.py).
        self.rejected_sentences: list[tuple[EvidenceChunk, int, str, str]] = []
        for chunk in chunks:
            if chunk.role != DocumentRole.CLAIM_SOURCE:
                continue
            for index, sentence in enumerate(split_sentences(chunk.text)):
                # The first "sentence" of a chunk that opens in lower case is the
                # tail of a sentence cut by the chunker; it cannot be quoted as a
                # claim ("quốc gia về giảm phát thải... Duy trì cơ chế kê khai").
                first = next((c for c in sentence if c.isalpha()), "")
                if index == 0 and first and first.islower():
                    self._reject(rejected, chunk, index, sentence, "chunk_boundary_fragment")
                    continue
                normalized = normalize_for_match(sentence)
                claim_type = self._claim_type(normalized)
                if not claim_type:
                    continue
                reason = heading_reason(sentence)
                if reason:
                    self._reject(rejected, chunk, index, sentence, reason)
                    continue
                # A bare year is a label, not a figure: "năm 2025" must not turn the
                # chairman's letter into a quantified claim (ISSUES N3).
                numbers = [(v, u) for v, u in parse_numbers(sentence) if u is not None or not 1900 <= v <= 2100]
                vague_matched = [term for term in self.vague_terms if term in normalized]
                # A figure does not make promotional language honest, but it does
                # make the claim checkable, which is what is_vague is about.
                is_vague = bool(vague_matched) and not numbers
                if is_vague and not self.settings.include_vague_claims:
                    self._reject(rejected, chunk, index, sentence, "vague_without_figure")
                    continue
                future = any(term in normalized for term in self.future_terms)
                # The generic bucket matches on words like "ESG" or "bền vững"
                # alone. Such a sentence is a claim only when it commits to
                # something: a figure, a promotional adjective or a future pledge.
                if claim_type == "generic_sustainability" and not (numbers or vague_matched or future):
                    self._reject(rejected, chunk, index, sentence, "generic_without_commitment")
                    continue
                confidence = min(0.96, 0.48 + (0.18 if numbers else 0) + (0.12 if claim_type != "generic_sustainability" else 0))
                if confidence < self.settings.minimum_confidence:
                    self._reject(rejected, chunk, index, sentence, "below_minimum_confidence")
                    continue
                canonical = re.sub(r"\s+", " ", normalized).strip()
                if canonical in seen:
                    continue
                seen.add(canonical)
                years = YEAR_RE.findall(sentence)
                direction = None
                if any(term in normalized for term in self.reduction_terms):
                    direction = "decrease"
                elif any(term in normalized for term in self.increase_terms):
                    direction = "increase"
                claim = Claim(
                    claim_id=stable_id(chunk.chunk_id, sentence),
                    text=sentence,
                    claim_type=claim_type,
                    source_chunk_id=chunk.chunk_id,
                    source_doc_id=chunk.doc_id,
                    source_name=chunk.source_name,
                    source_page=chunk.page,
                    metric=self._first_bucket(self.metrics, normalized),
                    direction=direction,
                    values=[value for value, _ in numbers],
                    units=[unit for _, unit in numbers if unit],
                    period=years[0] if years else None,
                    baseline=years[-1] if len(years) > 1 else None,
                    scope=self._first_bucket(self.scope_buckets, normalized),
                    is_future_commitment=future,
                    is_vague=is_vague,
                    vague_terms_matched=vague_matched,
                    language=self._language(normalized),
                    confidence=confidence,
                )
                claims.append(claim)
        self.audit.write(
            "claims_extracted",
            {
                "count": len(claims),
                "by_language": _tally(claim.language for claim in claims),
                "by_type": _tally(claim.claim_type for claim in claims),
                "rejected": rejected,
            },
        )
        return claims

    def _reject(self, tally: dict[str, int], chunk, index: int, sentence: str, reason: str) -> None:
        tally[reason] = tally.get(reason, 0) + 1
        self.rejected_sentences.append((chunk, index, sentence, reason))

    def _claim_type(self, normalized: str) -> str | None:
        """Best-matching claim type, or None when the sentence makes no green claim.

        Ties are broken by the taxonomy's `priority`, not by dict order: a
        sentence like "ESG was integrated across investment teams" hits the bare
        token "esg" in generic_sustainability and several process terms in
        esg_process_integration, and the specific type has to win or the claim is
        routed to the wrong legal issue.
        """
        best: tuple[int, int, str] | None = None
        for name, by_language in self.claim_types.items():
            hits = sum(
                1
                for terms in by_language.values()
                for term in terms
                if term in normalized
            )
            if not hits:
                continue
            candidate = (hits, self.priority[name], name)
            if best is None or candidate > best:
                best = candidate
        return best[2] if best else None

    def _language(self, normalized: str) -> str:
        """Which lexicon the sentence is written in, by term hits.

        Not a general language detector — it answers the only question the
        pipeline needs: which of the taxonomy's lexicons applies to this claim,
        so a reviewer can see whether a Vietnamese rubric was applied to an
        English claim.
        """
        scores = {
            language: sum(
                1
                for section in (self.claim_types, self.scope_buckets, self.metrics)
                for by_language in section.values()
                for term in by_language[language]
                if term in normalized
            )
            + sum(1 for term in self.vague_by_language[language] if term in normalized)
            for language in LANGUAGES
        }
        best = max(scores.values())
        if best == 0:
            return "unknown"
        # LANGUAGES order decides a tie, deliberately: see the constant.
        return next(language for language in LANGUAGES if scores[language] == best)

    @staticmethod
    def _first_bucket(buckets: dict[str, dict[str, list[str]]], normalized: str) -> str | None:
        """First bucket whose terms appear, or None when the text names none.

        None is a real answer, not a failure: it is what makes the missing
        attribute visible to the rubric instead of silently passing.
        """
        for name, by_language in buckets.items():
            if any(term in normalized for terms in by_language.values() for term in terms):
                return name
        return None


def _tally(values) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts
