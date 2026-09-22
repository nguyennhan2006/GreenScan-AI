"""L2 — the temporal and relational layer over registered legal documents.

The failure this exists to prevent:

    A claim published in 2022 is checked against the law as it stands in 2026,
    and the system reports the 2022 statement as non-compliant.

That is not a compliance finding; it is an anachronism. So every check must
declare which question it is asking:

    HISTORICAL_COMPLIANCE   what was in force when the claim was published?
    CURRENT_POLICY_ALIGNMENT  how does it read against today's criteria?

Both are legitimate and they are not interchangeable — a company can be fully
compliant historically and misaligned with current taxonomy at the same time.
The two results are kept apart all the way to the output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

HISTORICAL = "historical_compliance"
CURRENT = "current_policy_alignment"
CHECK_MODES = (HISTORICAL, CURRENT)

# Registry relation -> (edge name, direction is from this document)
RELATIONS = {
    "amends": "amends",
    "amended_by": "amended_by",
    "implements": "implements",
    "legal_basis": "legal_basis",
    "repeals": "repeals",
    "repealed_by": "repealed_by",
}


def _as_date(value: Any) -> date | None:
    if value in (None, "", "null"):
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


@dataclass
class LegalDocument:
    id: str
    document_number: str
    title: str
    doc_type: str
    authority: str
    issued_date: date | None
    effective_from: date | None
    effective_to: date | None
    status: str
    legal_issues: list[str] = field(default_factory=list)
    text_acquisition: str = "not_attempted"
    text_acquisition_note: str = ""
    landing_url: str | None = None
    original_url: str | None = None
    relations: dict[str, list[str]] = field(default_factory=dict)
    raw: dict = field(default_factory=dict)

    def in_force_on(self, when: date) -> bool:
        if self.effective_from and when < self.effective_from:
            return False
        if self.effective_to and when > self.effective_to:
            return False
        return True

    # Statuses that mean citable text exists. `ok_ocr` is included: the text is
    # real and addressable, only lower-trust. Trust is a separate axis, enforced
    # by the rule gate's human_reviewed condition.
    #
    # This set is the single definition of "usable" — the release gate and the
    # checker previously disagreed, so a document could pass LEGAL SOURCE READY
    # and still be reported as blocked in the finding it produced.
    USABLE_STATUSES = frozenset({"ok", "ok_ocr"})

    @property
    def usable(self) -> bool:
        """Whether clause text exists. A registered document is not a usable one."""
        return self.text_acquisition in self.USABLE_STATUSES

    @property
    def text_is_ocr(self) -> bool:
        """Citable, but recognised rather than published — verify before binding."""
        return self.text_acquisition == "ok_ocr"


class LegalCorpus:
    def __init__(self, documents: list[LegalDocument]):
        self.documents = {d.id: d for d in documents}

    # ---------- loading ----------

    @classmethod
    def from_registry(cls, path: str | Path) -> LegalCorpus:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        docs = []
        for entry in raw.get("documents", []):
            relations = {
                key: list(entry.get(key) or [])
                for key in RELATIONS
                if entry.get(key)
            }
            docs.append(LegalDocument(
                id=entry["id"],
                document_number=entry["document_number"],
                title=" ".join(str(entry.get("title", "")).split()),
                doc_type=entry.get("doc_type", ""),
                authority=entry.get("authority", ""),
                issued_date=_as_date(entry.get("issued_date")),
                effective_from=_as_date(entry.get("effective_from")),
                effective_to=_as_date(entry.get("effective_to")),
                status=entry.get("status", "unknown"),
                legal_issues=list(entry.get("legal_issues") or []),
                text_acquisition=entry.get("text_acquisition", "not_attempted"),
                text_acquisition_note=entry.get("text_acquisition_note", ""),
                landing_url=entry.get("landing_url"),
                original_url=entry.get("original_url"),
                relations=relations,
                raw=entry,
            ))
        return cls(docs)

    # ---------- selection ----------

    def applicable(
        self,
        legal_issue: str,
        as_of: date,
        *,
        require_text: bool = True,
    ) -> list[LegalDocument]:
        """Documents covering `legal_issue` and in force on `as_of`.

        `require_text=True` by default: a document whose clauses were never
        extracted cannot support a finding, and returning it would let the
        checker cite an instrument it has not read.
        """
        out = [
            d for d in self.documents.values()
            if legal_issue in d.legal_issues and d.in_force_on(as_of)
        ]
        if require_text:
            out = [d for d in out if d.usable]
        # Most recent first: an amending instrument usually carries the operative text.
        return sorted(out, key=lambda d: (d.effective_from or date.min), reverse=True)

    def blocked(self, legal_issue: str, as_of: date) -> list[LegalDocument]:
        """In-force documents that *would* apply but have no usable text.

        Surfaced deliberately: "we could not read the governing instrument" is a
        different answer from "the instrument does not cover this", and only the
        first one is fixable by collecting a document.
        """
        return [
            d for d in self.documents.values()
            if legal_issue in d.legal_issues and d.in_force_on(as_of) and not d.usable
        ]

    def resolve_as_of(self, mode: str, claim_published: date | None, today: date) -> date:
        if mode == HISTORICAL:
            if claim_published is None:
                raise ValueError(
                    "historical_compliance needs the claim's publication date; "
                    "without it the applicable law cannot be determined"
                )
            return claim_published
        if mode == CURRENT:
            return today
        raise ValueError(f"Unknown check mode {mode!r}; expected one of {CHECK_MODES}")

    # ---------- graph ----------

    def related(self, document_id: str, depth: int = 1) -> dict[str, list[str]]:
        """Neighbours by relation, expanded `depth` hops.

        Used to pull in the amending instrument alongside the base one — the
        registry states these edges, so they are followed rather than guessed by
        a model.
        """
        seen = {document_id}
        frontier = [document_id]
        edges: dict[str, list[str]] = {}
        for _ in range(max(depth, 0)):
            nxt = []
            for node in frontier:
                doc = self.documents.get(node)
                if not doc:
                    continue
                for relation, targets in doc.relations.items():
                    edges.setdefault(relation, [])
                    for t in targets:
                        if t not in edges[relation]:
                            edges[relation].append(t)
                        if t not in seen:
                            seen.add(t)
                            nxt.append(t)
            frontier = nxt
        return edges

    def effective_chain(self, document_id: str, as_of: date) -> list[LegalDocument]:
        """The base document plus any amendment in force on `as_of`.

        Reading a base decree without its amendment is how a system ends up
        applying a rule that was changed years ago.
        """
        base = self.documents.get(document_id)
        if base is None:
            return []
        chain = [base]
        for amender in base.relations.get("amended_by", []):
            doc = self.documents.get(amender)
            if doc and doc.in_force_on(as_of):
                chain.append(doc)
        return chain

    def coverage(self) -> dict:
        by_status: dict[str, int] = {}
        for d in self.documents.values():
            by_status[d.text_acquisition] = by_status.get(d.text_acquisition, 0) + 1
        issues: dict[str, dict[str, int]] = {}
        for d in self.documents.values():
            for issue in d.legal_issues:
                bucket = issues.setdefault(issue, {"registered": 0, "usable": 0})
                bucket["registered"] += 1
                bucket["usable"] += int(d.usable)
        return {
            "documents": len(self.documents),
            "usable": sum(1 for d in self.documents.values() if d.usable),
            "by_text_acquisition": by_status,
            "by_legal_issue": issues,
        }
