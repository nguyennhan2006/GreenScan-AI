"""Scope limits that travel with a source and must survive into the output.

An adjudicated case carries qualifiers that change what may be said about it:

    case_status        SEC_SETTLEMENT_WITHOUT_ADMISSION_OR_DENIAL
    adjudication_scope "Do not generalize this finding to every current K-Cup
                        product or every jurisdiction."
    legal_caution      "Use the SEC order for the adjudicated claim; treat the
                        2023 report as post-remediation control."

Dropping these turns "a regulator found this statement incomplete, settled
without admission" into "the company lied", which is both wrong and actionable
against the wrong party. They are collected from document metadata, carried on
the evidence, and reproduced on the legal check record so the finding is never
read without them.
"""

from __future__ import annotations

from typing import Any

# Metadata keys treated as legal scope limits. Anything else in a document's
# metadata is descriptive and does not constrain what the finding may claim.
QUALIFIER_KEYS = (
    "case_status",
    "adjudication_scope",
    "legal_caution",
    "jurisdiction",
    "training_eligibility",
)


def from_metadata(metadata: dict[str, Any] | None) -> list[str]:
    """Qualifier strings for one document, as `key: value` pairs."""
    if not metadata:
        return []
    return [
        f"{key}: {metadata[key]}"
        for key in QUALIFIER_KEYS
        if metadata.get(key) not in (None, "", [])
    ]


def merge(qualifier_lists: list[list[str]]) -> list[str]:
    """Unique qualifiers across several sources, order preserved."""
    seen: set[str] = set()
    merged: list[str] = []
    for qualifiers in qualifier_lists:
        for qualifier in qualifiers:
            if qualifier not in seen:
                seen.add(qualifier)
                merged.append(qualifier)
    return merged
