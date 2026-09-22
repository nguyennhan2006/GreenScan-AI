"""What kind of corpus a run had -- the input the verdict UNSUPPORTED depends on.

Open-world problem: "not found" is not "does not exist". A claim about 2024
emissions checked against a single sustainability report has no evidence
because nothing that could carry it was uploaded; the same claim checked
against the annual report, the audited accounts and an assurance statement
has no evidence because it is not there. Only the second is UNSUPPORTED. The
first is INSUFFICIENT_EVIDENCE, and the profile below is how the verifier
tells them apart (issues register B10, ADR 0005).

The profile is computed from what was uploaded and how it was labelled, not
from the claims, so it is the same for every claim in the run and can be
shown once on the overview as "evidence coverage".
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field

from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import DocumentInput, EvidenceChunk
from quantum_gw.utils.text import YEAR_RE

INDEPENDENT = {SourceType.LEGAL, SourceType.EXTERNAL, SourceType.STANDARD}

# The four kinds of material a claim about a reporting year can be checked
# against. `coverage` is the share present; `sufficient_for_absence` needs
# the two that carry figures and third-party findings.
CHECKS = (
    ("claim_source", "Tài liệu chứa tuyên bố"),
    ("comparison", "Tài liệu đối chiếu khác (BCTN/BCTC/kiểm kê)"),
    ("independent", "Nguồn độc lập (pháp lý / bên thứ ba / tiêu chuẩn)"),
    ("period_covered", "Tài liệu thuộc kỳ của tuyên bố"),
)


@dataclass
class CorpusProfile:
    documents: int
    chunks: int
    by_role: dict[str, int]
    by_source_type: dict[str, int]
    years: list[str]
    has_claim_source: bool
    has_comparison: bool
    has_independent: bool
    coverage: float
    # Absence of support may be read as UNSUPPORTED only when both a
    # comparison document and an independent source were searched.
    sufficient_for_absence: bool
    missing: list[str] = field(default_factory=list)
    version: str = "corpus-profile-v1"

    def to_json(self) -> dict:
        return asdict(self)

    def period_covered(self, period: str | None) -> bool:
        """Whether some document is dated to the claim's period (unknown period counts as covered)."""
        return not period or period in self.years


def profile_corpus(documents: list[DocumentInput], chunks: list[EvidenceChunk]) -> CorpusProfile:
    by_role = Counter(d.role.value for d in documents)
    by_type = Counter(d.source_type.value for d in documents)
    evidence_docs = [d for d in documents if d.role != DocumentRole.CLAIM_SOURCE]
    has_claim_source = by_role.get(DocumentRole.CLAIM_SOURCE.value, 0) > 0
    has_comparison = any(
        d.source_type in {SourceType.FINANCIAL, SourceType.ENVIRONMENTAL, SourceType.INTERNAL}
        for d in evidence_docs
    )
    has_independent = any(d.source_type in INDEPENDENT for d in evidence_docs)

    # Years the corpus talks about: the most frequent years across chunks and
    # file names, so a 2024 annual report counts as covering 2024 even when
    # its file name says "2025 edition".
    year_counts: Counter[str] = Counter()
    for chunk in chunks:
        year_counts.update(YEAR_RE.findall(chunk.text))
    for d in documents:
        year_counts.update(YEAR_RE.findall(d.display_name()))
    years = [year for year, _ in year_counts.most_common(6)]

    present = [has_claim_source, has_comparison, has_independent, bool(years)]
    missing = [label for (key, label), ok in zip(CHECKS, present, strict=False) if not ok]
    return CorpusProfile(
        documents=len(documents),
        chunks=len(chunks),
        by_role=dict(by_role),
        by_source_type=dict(by_type),
        years=sorted(years),
        has_claim_source=has_claim_source,
        has_comparison=has_comparison,
        has_independent=has_independent,
        coverage=round(sum(present) / len(present), 2),
        sufficient_for_absence=has_comparison and has_independent,
        missing=missing,
    )
