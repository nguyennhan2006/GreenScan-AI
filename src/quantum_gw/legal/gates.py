"""Release gates for the legal pipeline.

Two predicates, stated so that a missing document can never quietly become
"no applicable law":

    LEGAL_SOURCE_READY = official_source AND full_text_available
                         AND clause_parse_valid AND effective_date_known
                         AND amendment_chain_resolved AND provenance_complete

    LEGAL_RULE_ACTIVE  = source_clause_bound AND human_reviewed
                         AND unit_tests_pass AND temporal_scope_defined

The distinction these enforce is the one the whole layer rests on:

    "no instrument governs this"        -> a real legal answer
    "we could not read the instrument"  -> a collection failure

Both currently produce INSUFFICIENT_EVIDENCE downstream, but they demand
completely different follow-up, so the gate reports *which* condition failed
rather than a single boolean.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from .corpus import LegalCorpus, LegalDocument
from .parser import parse_document
from .rules import Rule, RulePack

# Hosts we accept as the issuing or publishing authority. A mirror may point the
# way to one of these but never substitutes for it.
OFFICIAL_HOSTS = (
    "vanban.chinhphu.vn", "datafiles.chinhphu.vn",
    "congbao.chinhphu.vn", "congbaocdn.chinhphu.vn",
    "vbpl.vn", "quochoi.vn", "sbv.gov.vn", "mof.gov.vn", "monre.gov.vn",
)


@dataclass
class GateResult:
    subject: str
    ready: bool
    conditions: dict[str, bool] = field(default_factory=dict)
    reasons: dict[str, str] = field(default_factory=dict)

    @property
    def failed(self) -> list[str]:
        return [k for k, v in self.conditions.items() if not v]

    def to_json(self) -> dict[str, Any]:
        return {
            "subject": self.subject, "ready": self.ready,
            "conditions": self.conditions,
            "failed": self.failed,
            "reasons": {k: v for k, v in self.reasons.items() if k in self.failed},
        }


def _is_official(url: str | None) -> bool:
    if not url:
        return False
    return any(host in url for host in OFFICIAL_HOSTS)


def check_source(
    doc: LegalDocument,
    corpus: LegalCorpus,
    *,
    repo_root: Path | None = None,
    as_of: date | None = None,
) -> GateResult:
    """LEGAL SOURCE READY for one instrument."""
    repo_root = repo_root or Path.cwd()
    as_of = as_of or date.today()
    cond: dict[str, bool] = {}
    why: dict[str, str] = {}

    cond["official_source"] = _is_official(doc.raw.get("original_url")) or _is_official(
        doc.raw.get("congbao_url")) or _is_official(doc.landing_url)
    why["official_source"] = "No URL on an issuing or publishing authority host."

    # `ok_ocr` satisfies availability: the text exists and is citable. Trust is a
    # separate axis, carried on the result and enforced by the rule gate's
    # human_reviewed condition — an OCR diacritic error must be caught by a
    # reviewer, not by pretending the document was never collected.
    cond["full_text_available"] = doc.usable
    why["full_text_available"] = (
        f"text_acquisition={doc.text_acquisition}. "
        + (doc.text_acquisition_note or "Full text not extracted.")
    )

    # Parse must actually yield addressable clauses. A file that extracts to
    # prose but produces no Điều is not usable for citation.
    clauses_file = doc.raw.get("clauses_file")
    parsed = 0
    if clauses_file and (repo_root / clauses_file).is_file():
        parsed = sum(1 for line in (repo_root / clauses_file)
                     .read_text(encoding="utf-8").split("\n") if line.strip())
    elif cond["full_text_available"]:
        raw_dir = repo_root / "data/legal/raw" / doc.id
        text_file = raw_dir / "fulltext.txt"
        if text_file.is_file():
            parsed = len(parse_document(doc.id, text_file.read_text(encoding="utf-8")))
    cond["clause_parse_valid"] = parsed > 0
    why["clause_parse_valid"] = f"{parsed} clause(s) parsed; need at least one addressable Điều."

    cond["effective_date_known"] = doc.effective_from is not None
    why["effective_date_known"] = "effective_from missing — cannot decide what was in force."

    # Every amending instrument named must itself be registered, otherwise the
    # chain silently stops and an outdated rule stays in force.
    amenders = doc.relations.get("amended_by", [])
    unknown = [a for a in amenders if a not in corpus.documents]
    cond["amendment_chain_resolved"] = not unknown
    why["amendment_chain_resolved"] = f"Amending instruments not in registry: {unknown}"

    prov = doc.raw
    missing = [k for k in ("document_number", "authority", "issued_date") if not prov.get(k)]
    has_artifact = bool(prov.get("original_url") or prov.get("congbao_url"))
    cond["provenance_complete"] = not missing and has_artifact
    why["provenance_complete"] = (
        f"Missing fields: {missing}." if missing else "No retrievable artifact URL recorded."
    )

    return GateResult(subject=doc.id, ready=all(cond.values()), conditions=cond, reasons=why)


def check_rule(
    rule: Rule,
    corpus: LegalCorpus,
    *,
    known_clause_ids: set[str] | None = None,
    unit_tests_pass: bool | None = None,
) -> GateResult:
    """LEGAL RULE ACTIVE for one rule.

    `unit_tests_pass` is passed in rather than inferred: a rule pack claiming its
    own tests pass is not evidence, and this module must not shell out to pytest.
    """
    cond: dict[str, bool] = {}
    why: dict[str, str] = {}

    bound = bool(rule.source_clauses) and not any(
        "UNBOUND" in c for c in rule.source_clauses)
    if bound and known_clause_ids is not None:
        unresolved = [c for c in rule.source_clauses if c not in known_clause_ids]
        bound = not unresolved
        why["source_clause_bound"] = f"Clause ids not found in parsed corpus: {unresolved}"
    else:
        why["source_clause_bound"] = (
            "source_clauses is empty or contains UNBOUND placeholders."
        )
    cond["source_clause_bound"] = bound

    cond["human_reviewed"] = bool(rule.reviewed_by.strip())
    why["human_reviewed"] = "reviewed_by is empty — no human signed off on this rule."

    cond["unit_tests_pass"] = bool(unit_tests_pass)
    why["unit_tests_pass"] = (
        "Unit-test status not supplied." if unit_tests_pass is None
        else "Rule unit tests are failing."
    )

    cond["temporal_scope_defined"] = rule.effective_from is not None
    why["temporal_scope_defined"] = (
        "effective_from missing — the rule would apply to claims from any period."
    )

    # A rule may not outlive the instrument it cites.
    src = corpus.documents.get(rule.source_document)
    if src is None:
        cond["source_clause_bound"] = False
        why["source_clause_bound"] = (
            f"source_document {rule.source_document!r} is not in the registry."
        )

    return GateResult(subject=rule.rule_id, ready=all(cond.values()),
                      conditions=cond, reasons=why)


def audit_corpus(corpus: LegalCorpus, *, repo_root: Path | None = None) -> list[GateResult]:
    return [check_source(d, corpus, repo_root=repo_root) for d in corpus.documents.values()]


def audit_rules(pack: RulePack, corpus: LegalCorpus, **kw) -> list[GateResult]:
    return [check_rule(r, corpus, **kw) for r in pack.rules]
