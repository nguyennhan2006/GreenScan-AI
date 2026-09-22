"""Qualitative stance of one passage towards one claim.

The numeric verifier answers "do these figures agree". That question has no
answer for most real greenwashing findings, which turn on what an organisation
*did* rather than on what it reported:

    KDP-2024  the statement omitted the negative recycler feedback
    BNY-2022  67 of 185 holdings had no ESG quality-review score
    DWS-2023  no formalized controls verified that the ESG Engine was used
    KLM-2024  a court held 15 of 19 environmental statements misleading

None of these involves two numbers in conflict, and none states a direction that
flips. Before this module the pipeline scored all four as INSUFFICIENT_EVIDENCE
or PARTIALLY_SUPPORTED.

The detector is deliberately a lexicon over cue *phrases* rather than a model:
it is reproducible, it can be audited by a domain reviewer who does not read
Python, and it never invents a finding. Where it cannot decide, it says so and
the caller may escalate to a language model — see `LLMStanceJudge`, whose output
is always marked for human review.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from quantum_gw.utils.text import (
    content_bigrams,
    content_tokens,
    normalize_for_match,
    normalize_text,
    split_sentences,
)

# Stance of a passage towards a claim. These are the values carried on
# RetrievedEvidence.relation.
SUPPORTS = "SUPPORTS"
CONTRADICTS = "CONTRADICTS"
PARTIAL = "PARTIAL"
CONTEXT = "CONTEXT"

# Source types whose statements are findings by a third party rather than the
# subject's own account. A refutation from one of these does not need lexical
# overlap with the claim to count.
AUTHORITATIVE_SOURCES = frozenset({"legal", "standard"})

LANGUAGES = ("vi", "en")


@dataclass
class StanceSignal:
    relation: str
    reason: str
    # How the stance was reached, so a reviewer can weigh it and the evaluation
    # harness can report accuracy per method rather than as one blended number.
    method: str
    cues: list[str] = field(default_factory=list)
    authoritative: bool = False


def _has_diacritics(text: str) -> bool:
    return normalize_for_match(text) != normalize_text(text).lower()


# A support cue with one of these within a few words before it is not support:
# "không xác nhận", "no independent assurance", "was not verified". Such a
# sentence is dropped rather than counted as a refutation -- it is usually an
# absence statement, and silence is never refutation.
NEGATIONS = ("không", "chưa", "chẳng", "khong", "chua", "chang",
             "not", "no", "never", "without", "neither", "nor", "lack", "lacked", "lacking", "lacks")
_NEGATION_WINDOW = 4


def _negated(sentence: str, term: str) -> bool:
    """Is any occurrence of `term` in `sentence` preceded by a negation within the window."""
    haystack = normalize_text(sentence).lower()
    folded = normalize_for_match(sentence)
    for text, needle in ((haystack, term), (folded, normalize_for_match(term))):
        for match in re.finditer(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", text):
            before = re.findall(r"[\w]+", text[: match.start()])[-_NEGATION_WINDOW:]
            if any(word in NEGATIONS for word in before):
                return True
    return False


def _phrase_re(term: str) -> re.Pattern[str]:
    # Whole-word: "thiếu" must not fire inside "thiêu kết", nor "not" inside "note".
    return re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.UNICODE)


class StanceLexicon:
    """Cue phrases for refutation, support and adjudicative voice.

    Each cue is compiled twice: on the accented, lower-cased form and on the
    accent-folded form. Accented text is matched accented -- folding turned
    "thiêu kết" (sintering) into "thieu" and had the cue "thiếu" refute every
    claim in a steel producer's report. The folded form is kept only for text
    that carries no diacritics at all (OCR output, transliterated sources).

    `benign` phrases are removed before refutation cues are looked up: "không
    có sự cố" is a positive statement that happens to contain "không có".
    """

    def __init__(self, path: str | Path = "configs/stance_cues.yaml"):
        resolved = Path(path)
        if not resolved.exists():
            resolved = Path(__file__).resolve().parents[3] / str(path)
        raw = yaml.safe_load(resolved.read_text(encoding="utf-8")) or {}
        self.version = raw.get("version", "unversioned")
        self.families: dict[str, list[str]] = {}
        self._accented: dict[str, list[tuple[str, re.Pattern[str]]]] = {}
        self._folded: dict[str, list[tuple[str, re.Pattern[str]]]] = {}
        for family in ("refutes", "supports", "adjudicative", "benign", "statement_nouns"):
            terms = [
                normalize_text(term).lower()
                for language in LANGUAGES
                for term in (raw.get(family) or {}).get(language) or []
            ]
            self.families[family] = [normalize_for_match(t) for t in terms]
            self._accented[family] = [(t, _phrase_re(t)) for t in terms]
            self._folded[family] = [
                (normalize_for_match(t), _phrase_re(normalize_for_match(t))) for t in terms
            ]

    def hits(self, family: str, text: str) -> list[str]:
        """Cue terms present in `text` as whole words, in the text's own orthography."""
        accented = _has_diacritics(text)
        haystack = normalize_text(text).lower() if accented else normalize_for_match(text)
        table = self._accented if accented else self._folded
        return [term for term, pattern in table[family] if pattern.search(haystack)]

    def strip_benign(self, text: str) -> str:
        accented = _has_diacritics(text)
        haystack = normalize_text(text).lower() if accented else normalize_for_match(text)
        for _, pattern in (self._accented if accented else self._folded)["benign"]:
            haystack = pattern.sub(" ", haystack)
        return haystack


def qualitative_stance(
    evidence_text: str,
    *,
    source_type: str,
    overlap: float,
    minimum_overlap: float,
    lexicon: StanceLexicon,
    claim_tokens: set[str] | None = None,
    claim_bigrams: set[str] | None = None,
) -> StanceSignal | None:
    """Stance from cue phrases, or None when the passage does not speak to the claim.

    A cue only counts when the passage is connected to the claim, established
    either by lexical overlap or by the passage being an authority's finding.
    Without that guard any document containing the word "inadequate" would
    refute any claim retrieved alongside it.

    With `claim_tokens` the connection is checked per sentence: the cue has to
    sit in a sentence that shares a content word with the claim. A passage can
    be on topic overall and still carry its "thiếu" in a sentence about the
    canteen.

    Returning None is the honest outcome for a passage that mentions the topic
    but takes no position; the caller falls back to its similarity-based reading.
    """
    adjudicative = bool(lexicon.hits("adjudicative", evidence_text))
    authoritative = adjudicative or source_type in AUTHORITATIVE_SOURCES
    on_topic = overlap >= minimum_overlap

    # A refutation from an authority counts without lexical overlap; support
    # never does. The asymmetry is deliberate and matches the consequences: a
    # regulator's order is no less a finding for sharing few words with the
    # marketing copy it refutes, whereas an authoritative document that merely
    # contains "certified" must not clear a claim it is not actually about.
    # Getting this wrong in the permissive direction produces a clean bill of
    # health nobody asked for, which is the one error a reviewer will not catch
    # by reading the flagged items.
    # An authority bypasses the *overlap floor*, not the sentence check: its
    # refutation still has to be about the claim's subject. The demo's legal
    # notice about hazardous-waste storage was refuting a green-bond claim.
    if on_topic or authoritative:
        refuting = _cues_in_claim_sentences(
            lexicon, "refutes", evidence_text, claim_tokens,
            require_shared=True, authoritative=authoritative,
        )
        if refuting:
            return StanceSignal(
                relation=CONTRADICTS,
                reason=_reason("Bằng chứng phủ định tuyên bố", refuting, authoritative),
                method="qualitative_cue",
                cues=refuting[:4],
                authoritative=authoritative,
            )

    # Support is the permissive direction, so its bar is higher: the cue must
    # sit in a sentence that shares a word (a syllable bigram) with the claim's
    # own text, not merely a topic word. "chứng nhận" occurs in every report --
    # appliances are "certified" too -- and "năng lượng" alone let it clear
    # unrelated claims.
    if on_topic:
        supporting = _cues_in_claim_sentences(
            lexicon, "supports", evidence_text, claim_tokens, require_shared=True,
            shared_bigrams=claim_bigrams,
        )
        if supporting:
            return StanceSignal(
                relation=SUPPORTS,
                reason=_reason("Bằng chứng xác nhận tuyên bố", supporting, authoritative),
                method="qualitative_cue",
                cues=supporting[:4],
                authoritative=authoritative,
            )
    return None


def _cues_in_claim_sentences(
    lexicon: StanceLexicon,
    family: str,
    evidence_text: str,
    claim_tokens: set[str] | None,
    *,
    require_shared: bool,
    authoritative: bool = False,
    shared_bigrams: set[str] | None = None,
) -> list[str]:
    """Cue hits, restricted to sentences that are about the claim.

    A sentence is about the claim when it shares a content word with it, or --
    for an authority's finding -- when it is a ruling on the subject's
    statements as such: "the court found 15 of 19 statements misleading" names
    no emission figure and no product, and is still a finding about the claim.
    A fine for hazardous-waste storage in the same order is not.

    Without claim tokens (older callers, unit tests of the lexicon itself) the
    whole passage is one sentence. Benign phrases are removed first so a
    refutation cue is never read out of "không có sự cố".
    """
    sentences = split_sentences(evidence_text) or [evidence_text]
    found: list[str] = []
    for sentence in sentences:
        if require_shared and claim_tokens is not None:
            shared = bool(content_tokens(sentence) & claim_tokens)
            if shared_bigrams is not None:
                shared = bool(content_bigrams(sentence) & shared_bigrams)
            about_statements = authoritative and _rules_on_statements(lexicon, sentence)
            if not (shared or about_statements):
                continue
        cleaned = lexicon.strip_benign(sentence) if family == "refutes" else sentence
        for term in lexicon.hits(family, cleaned):
            if family == "supports" and _negated(sentence, term):
                continue
            if term not in found:
                found.append(term)
    return found


def _rules_on_statements(lexicon: StanceLexicon, sentence: str) -> bool:
    """An adjudicative voice ruling on statements/claims/advertisements."""
    return bool(lexicon.hits("adjudicative", sentence)) and bool(
        lexicon.hits("statement_nouns", sentence)
    )


def _reason(headline: str, cues: list[str], authoritative: bool) -> str:
    voice = " (nguồn có thẩm quyền)" if authoritative else ""
    return f"{headline}{voice}: “{'”, “'.join(cues[:4])}”."
