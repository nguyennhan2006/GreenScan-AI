"""Pipeline step that runs the legal layer over a verified claim.

The legal modules (corpus, rules, checker, gates) were complete and unit-tested
but nothing in the pipeline called them — only `tools/legal_vertical_slice.py`
did. So a run produced a greenwashing risk score with no statement of which
instrument governs the claim, and the scope limits attached to adjudicated
sources never reached the output at all.

This agent is the missing edge. It is deliberately failure-tolerant: a missing
registry or an unparsable rule pack disables the step and is recorded, rather
than failing a run that is otherwise complete. A legal check that could not run
is a gap in coverage, not a verdict about a company.
"""

from __future__ import annotations

from datetime import date

from quantum_gw.domain.models import VerificationResult
from quantum_gw.legal.checker import LegalChecker
from quantum_gw.legal.corpus import CHECK_MODES, LegalCorpus
from quantum_gw.legal.qualifiers import merge as merge_qualifiers
from quantum_gw.legal.rules import RulePack
from quantum_gw.settings import LegalSettings
from quantum_gw.storage.audit import AuditLogger


class LegalCheckAgent:
    def __init__(self, settings: LegalSettings, audit: AuditLogger):
        self.settings = settings
        self.audit = audit
        self.checker: LegalChecker | None = None
        self.unavailable_reason = ""
        if not settings.enabled:
            self.unavailable_reason = "Legal layer disabled in configuration."
            return
        if settings.check_mode not in CHECK_MODES:
            self.unavailable_reason = (
                f"Unknown check_mode {settings.check_mode!r}; expected one of {CHECK_MODES}."
            )
            return
        try:
            corpus = LegalCorpus.from_registry(settings.registry_file)
            pack = RulePack.from_yaml(settings.rule_pack_file)
        except (OSError, ValueError, KeyError) as exc:
            self.unavailable_reason = f"Could not load legal corpus or rule pack: {exc}"
        else:
            self.checker = LegalChecker(corpus, pack)
        self.audit.write(
            "legal_layer_initialised",
            {"available": self.checker is not None, "reason": self.unavailable_reason},
        )

    @property
    def available(self) -> bool:
        return self.checker is not None

    def run(self, verification: VerificationResult) -> dict | None:
        if self.checker is None:
            return None
        claim = verification.claim
        evidence = [
            {"chunk_id": item.chunk_id, "text": item.text, "source_type": item.source_type.value}
            for item in verification.evidence
        ]
        result = self.checker.check(
            claim={"claim_id": claim.claim_id, "claim_type": claim.claim_type},
            evidence=evidence,
            check_mode=self.settings.check_mode,
            claim_published=_published(claim.period),
        )
        record = result.to_json()
        # The finding must never be read without the limits its sources carry.
        record["source_qualifiers"] = merge_qualifiers(
            [item.source_qualifiers for item in verification.evidence]
        )
        self.audit.write(
            "legal_checked",
            {
                "claim_id": claim.claim_id,
                "issue": record["issue"],
                "legal_finding": record["legal_finding"],
                "rules_applied": record["rules_applied"],
                "blocked_sources": [b["document"] for b in record["blocked_sources"]],
            },
        )
        return record


def _published(period: str | None) -> date | None:
    """Publication date implied by the claim's period, for historical checks.

    Only the year is known, so 31 December is used: it is the latest date the
    claim could belong to, which is the conservative choice when deciding which
    amendments were already in force.
    """
    if not period:
        return None
    try:
        return date(int(period), 12, 31)
    except ValueError:
        return None
