from __future__ import annotations

import re
from pathlib import Path

import yaml

from quantum_gw.agents.claim_quality import suspect_reason
from quantum_gw.domain.enums import DocumentRole
from quantum_gw.domain.models import Claim, EvidenceChunk
from quantum_gw.parsers.ocr import contains_number, matches_value
from quantum_gw.settings import ClaimSettings
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.utils.text import (
    YEAR_RE,
    normalize_for_match,
    parse_numbers,
    parse_quantities,
    split_sentences,
    stable_id,
)

# Lexicon languages, in the order used to break a tie when a sentence matches
# both equally. Vietnamese first: the deployment target is Vietnamese issuers.
LANGUAGES = ("vi", "en")

# Section enumerators and separators that mark a heading or a table-of-contents
# line: "4.1 | PHÁT THẢI", "2) Năng lượng", "III. Môi trường", "Chương 3 –".
# A year inside a standard or legal-document code is the code's edition, not the period the claim reports:
# "ISO 14064-1:2018", "14001:2015", "Nghị định 08/2022/NĐ-CP", "21/2025/QĐ-TTg" (found on HPG, 13/11/2026).
_CODE_YEAR_RE = re.compile(
    r"\b(?!(?:19|20)\d{2}\b)\d{3,}(?:[.\-]\d+)*\s*:\s*(?:19|20)\d{2}\b"   # 14064-1:2018, ISO 14001:2015 (not 2024:2025)
    r"|\b\d{1,4}/(?:19|20)\d{2}/[^\s,;.]+")   # 08/2022/NĐ-CP, 21/2025/QĐ-TTg
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
    r"là|có|không|chiếm|đóng góp|góp phần|mua|bán|ký|tham gia|mở rộng|nâng cao|cải thiện|tối ưu|"
    r"tự chủ|ở mức|tương đương|trồng)(?!\w)"
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


# A clause boundary that can carry its own assertion. Splitting on anything
# looser turns one statement into fragments; splitting on nothing gives a single
# blurred verdict for a sentence making three separate claims (P7).
# "và" is deliberately NOT here. It joins measurements as often as it joins
# clauses -- "Phạm vi 1 và 2", "nước và chất thải" -- and splitting on it cut a
# scope in half and broke eight tests. Only connectors that cannot appear inside
# a single measurement are used.
_CLAUSE_SPLIT_RE = re.compile(r"\s*;\s+|\s+(?:đồng thời|trong khi đó|mặt khác)\s+(?=[^,;]{12,})")
_MEASURED_RE = re.compile(r"\d")


def split_assertions(sentence: str) -> list[str]:
    """One sentence, one or more checkable assertions.

    "Phát thải giảm 20% và tỷ lệ tái chế đạt 99%" is two claims with two
    verdicts, not one claim with a blurred one. A split is only made when each
    side carries its own figure: without that, the parts are a subject and its
    continuation, and separating them destroys the statement.

    The original sentence is returned unchanged whenever the test fails, so the
    default behaviour of the extractor is untouched.
    """
    parts = [part.strip(" ,;") for part in _CLAUSE_SPLIT_RE.split(sentence) if part and part.strip()]
    if len(parts) < 2:
        return [sentence]
    if not all(len(part.split()) >= 6 and _MEASURED_RE.search(part) for part in parts):
        return [sentence]
    if any(re.match(r"^\d", part) for part in parts):
        return [sentence]  # a part starting with a digit is the tail of a figure
    return parts


def _assertions(sentences: list[str]) -> list[tuple[str, bool]]:
    """Each assertion with a flag saying whether it came from splitting a sentence.

    A split part legitimately begins in lower case, so the checks that exist to
    catch sentences cut in half by the PDF chunker must not fire on it.
    """
    out: list[tuple[str, bool]] = []
    previous = ""
    for sentence in sentences:
        # A clause that follows a semicolon is a second assertion, not a line the
        # PDF broke in half: the sentence splitter has already separated them, so
        # the only evidence left is how the previous one ended.
        after_semicolon = previous.rstrip().endswith(";")
        parts = split_assertions(sentence)
        out.extend((part, len(parts) > 1 or after_semicolon) for part in parts)
        previous = sentence
    return out


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
        # claim-typing-v2: tried only when no claim_type matches (configs/taxonomy.yaml v4).
        self.fallback_types = _by_language(self.taxonomy.get("fallback_claim_types") or {})

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
            if (chunk.metadata or {}).get("table"):
                # A laid-out table (page-regions-v1): its rows are read as disclosed figures with their
                # headers and unit (agents/figures.py); as sentences they would be "BẢNG: …" fragments.
                continue
            for index, (sentence, from_split) in enumerate(_assertions(split_sentences(chunk.text))):
                # The first "sentence" of a chunk that opens in lower case is the
                # tail of a sentence cut by the chunker; it cannot be quoted as a
                # claim ("quốc gia về giảm phát thải... Duy trì cơ chế kê khai").
                first = next((c for c in sentence if c.isalpha()), "")
                if index == 0 and not from_split and first and first.islower():
                    self._reject(rejected, chunk, index, sentence, "chunk_boundary_fragment")
                    continue
                normalized = normalize_for_match(sentence)
                claim_type = self._claim_type(normalized)
                if not claim_type:
                    continue
                reason = heading_reason(sentence)
                if reason == "fragment" and from_split:
                    reason = None  # a clause of a split sentence, not a broken line
                if reason:
                    self._reject(rejected, chunk, index, sentence, reason)
                    continue
                numbers, vague_matched, is_vague, future = self._signals(sentence, normalized)
                if is_vague and not self.settings.include_vague_claims:
                    self._reject(rejected, chunk, index, sentence, "vague_without_figure")
                    continue
                # The generic bucket matches on words like "ESG" or "bền vững"
                # alone. Such a sentence is a claim only when it commits to
                # something: a figure, a promotional adjective or a future pledge.
                if claim_type == "generic_sustainability" and not (numbers or vague_matched or future):
                    self._reject(rejected, chunk, index, sentence, "generic_without_commitment")
                    continue
                # claim-precision-v1 (15/11/2026, GS-Claims v1 dev split): 13 of 17 false claims were "bền vững"
                # or "ESG" in a social or governance sense ("mối quan hệ bền vững với khách hàng", "Ban ESG",
                # "mục tiêu phát triển bền vững" of the staff). A generic sentence is an environmental claim only
                # when it names something environmental.
                # Vietnamese only: every false claim of the dev split was Vietnamese, while English marketing such as
                # KLM's "Join us in creating a more sustainable future" is the vague claim a court ruled misleading.
                if (claim_type == "generic_sustainability"
                        and getattr(self.settings, "require_environment_anchor", False)
                        and normalized != sentence.lower()
                        and not _ENV_ANCHOR_RE.search(_SD_PHRASES_RE.sub(" ", normalized))):
                    self._reject(rejected, chunk, index, sentence, "generic_without_environment")
                    continue
                confidence = min(0.96, 0.48 + (0.18 if numbers else 0) + (0.12 if claim_type != "generic_sustainability" else 0))
                if confidence < self.settings.minimum_confidence:
                    self._reject(rejected, chunk, index, sentence, "below_minimum_confidence")
                    continue
                canonical = re.sub(r"\s+", " ", normalized).strip()
                if canonical in seen:
                    continue
                seen.add(canonical)
                claim = self._claim(chunk, sentence, normalized, claim_type, confidence)
                if getattr(self.settings, "flag_suspect_non_claims", False):
                    claim.quality_flag = suspect_reason(sentence)
                claims.append(claim)
        self.audit.write(
            "claims_extracted",
            {
                "count": len(claims),
                "by_language": _tally(claim.language for claim in claims),
                "by_type": _tally(claim.claim_type for claim in claims),
                "rejected": rejected,
                "flagged_suspect_non_claim": _tally(c.quality_flag for c in claims if c.quality_flag),
            },
        )
        return claims

    def _signals(self, sentence: str, normalized: str):
        # A bare year is a label, not a figure: "năm 2025" must not turn the
        # chairman's letter into a quantified claim (ISSUES N3).
        numbers = [(v, u) for v, u in parse_numbers(sentence) if u is not None or not 1900 <= v <= 2100]
        vague_matched = [term for term in self.vague_terms if term in normalized]
        # A figure does not make promotional language honest, but it does
        # make the claim checkable, which is what is_vague is about.
        is_vague = bool(vague_matched) and not numbers
        future = any(term in normalized for term in self.future_terms)
        return numbers, vague_matched, is_vague, future

    def _claim(self, chunk, sentence: str, normalized: str, claim_type: str, confidence: float) -> Claim:
        numbers, vague_matched, is_vague, future = self._signals(sentence, normalized)
        years = YEAR_RE.findall(_CODE_YEAR_RE.sub(" ", sentence))
        period_source = None
        if not years and _RELATIVE_NOW_RE.search(normalized):
            report_year = _report_year(chunk)
            if report_year:
                years, period_source = [report_year], "report_year"
        direction = None
        if any(term in normalized for term in self.reduction_terms):
            direction = "decrease"
        elif any(term in normalized for term in self.increase_terms):
            direction = "increase"
        return Claim(
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
            period_source=period_source,
            baseline=years[-1] if len(years) > 1 else None,
            scope=self._first_bucket(self.scope_buckets, normalized),
            is_future_commitment=future,
            is_vague=is_vague,
            vague_terms_matched=vague_matched,
            language=self._language(normalized),
            confidence=confidence,
            **_reading(chunk, sentence),
        )

    def describe(self, text: str, chunk: EvidenceChunk) -> Claim:
        """The Claim this extractor would build for `text`, with no gate applied.

        For measurement: a human already decided the sentence is a claim, so the
        verifier must be shown it with exactly the attributes (metric, figures,
        period, scope) production would give it, even where the gates here
        would have dropped it.
        """
        normalized = normalize_for_match(text)
        claim_type = self._claim_type(normalized) or "generic_sustainability"
        return self._claim(chunk, text, normalized, claim_type, confidence=0.5)

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
        if best:
            return best[2]
        return self._fallback_type(normalized) if getattr(self.settings, "fallback_types", False) else None

    def _fallback_type(self, normalized: str) -> str | None:
        """A type for a sentence no claim_type matched (claim-typing-v2).

        GS-Mutation v1 (15/11/2026): all 63 of 104 supported sentences that were never extracted
        matched no claim_type -- "tự chủ 90% nhu cầu điện", "phát 3,18 tỷ kWh điện", water use.
        First the resource-use vocabulary; then any sentence that names a known metric and carries
        a figure that is not a year (metric_disclosure). "nước" alone also means a state or a
        country, so "nhà nước", "trong nước", "nước ngoài"... are taken out before the metric test.
        """
        text = _NOT_WATER.sub(" ", normalized)
        for name, by_language in self.fallback_types.items():
            if any(term in text for terms in by_language.values() for term in terms):
                return name
        if self._first_bucket(self.metrics, text) and any(
            not (1900 <= value <= 2100) for value, _unit, _half in parse_quantities(text)
        ):
            return "metric_disclosure"
        return None

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


# claim-precision-v1: words that make a generic sustainability sentence environmental (folded text), and
# the phrases that only name the field ("phát triển bền vững", "báo cáo phát triển bền vững").
_ENV_ANCHOR_RE = re.compile(
    r"(?<!\w)(moi truong|khi hau|phat thai|khi nha kinh|carbon|co2|nang luong|dien|nuoc|chat thai|rac|tai che|"
    r"xanh|sinh thai|da dang sinh hoc|rung|cay|o nhiem|net zero|trung hoa|tai nguyen|sach|tai tao|nhua|bao bi|"
    r"thien nhien|environment\w*|climate|emission\w*|energy|water|waste|recycl\w*|green|eco\w*|biodiversity|"
    r"forest\w*|pollut\w*|renewable|clean|plastic\w*|nature)(?!\w)"
)
_SD_PHRASES_RE = re.compile(r"(?<!\w)(?:bao cao )?phat trien ben vung(?!\w)|sustainability report|sustainable development")


# "hiện nay / hiện tại / năm nay": the period is the report's own year (folded text).
_RELATIVE_NOW_RE = re.compile(r"(?<!\w)(hien nay|hien tai|nam nay|cho den nay|tinh den nay)(?!\w)")


def _report_year(chunk) -> str | None:
    """The report's year: the chunk's reporting_year if intake set one, else the last 20xx in the file name."""
    year = (getattr(chunk, "metadata", None) or {}).get("reporting_year")
    if year:
        return str(year)
    found = re.findall(r"(?<!\d)(20[0-4]\d)(?!\d)", chunk.source_name or "")
    return found[-1] if found else None


# "nước" as state or country, never water (folded text).
_NOT_WATER = re.compile(r"(?<!\w)(nha nuoc|trong nuoc|nuoc ngoai|cac nuoc|dat nuoc|nuoc ta|nhieu nuoc|ca nuoc|tren the gioi)(?!\w)")


def _tally(values) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def _reading(chunk, sentence: str) -> dict:
    """How sure OCR was of this sentence: the page's confidence, and the sentence's own figures OCR doubted.

    A doubtful token counts when it occurs in the sentence as a quantity, not
    as a label ("Phạm vi 1", "ISO 14001"), which parse_numbers leaves out.
    """
    meta = chunk.metadata or {}
    if not meta.get("ocr"):
        return {}
    quantities = [value for value, _ in parse_numbers(sentence)]
    return {"ocr_confidence": meta.get("ocr_confidence"),
            "doubtful_numbers": [n for n in meta.get("ocr_doubtful_numbers") or []
                                 if contains_number(sentence, n) and matches_value(n, quantities)]}
