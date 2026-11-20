"""The language-model stages wired into the pipeline (registration llm_stages_v1). None of them sets a verdict.

S2 fill_attributes   after extraction: period / baseline / scope that the sentence writes and the rules missed,
                     taken only as verbatim spans (guards.verbatim). The claim records which fields a model filled.
S6 explain_result    after verification: a plain-language explanation beside the rules rationale, dropped when it
                     writes a number that neither the claim, the rationale nor a passage writes (guards.new_numbers).
S4 / S5 live in the verifier (verification/ir_reader.py, verification/llm_judge.py).
"""
from __future__ import annotations

import re

from quantum_gw.domain.models import Claim, VerificationResult

from .client import StageModel
from .guards import new_numbers, verbatim
from .prompts import attr_messages, explain_messages

FILLABLE = ("period", "baseline", "scope")
FILE_ID = re.compile(r"(?:tài liệu\s+)?\b[0-9a-f]{16,}(?:\.pdf)?\b", re.I)


def fill_attributes(claims: list[Claim], stage: StageModel) -> dict:
    """Fill what the sentence writes and the rules left empty. Returns counts for the audit log."""
    filled = {a: 0 for a in FILLABLE}
    dropped = 0
    for claim in claims:
        if all(getattr(claim, a) for a in FILLABLE):
            continue
        parsed = stage.ask(lambda model, text=claim.text: attr_messages(model, text), [claim.text])
        if not parsed:
            continue
        for a in FILLABLE:
            if getattr(claim, a):
                continue
            span = parsed.get(a)
            kept = verbatim(span, claim.text)
            if kept:
                setattr(claim, a, kept)
                claim.assisted_fields.append(a)
                filled[a] += 1
            elif isinstance(span, str) and span.strip():
                dropped += 1
    return {"filled": filled, "non_verbatim_dropped": dropped, "route": stage.route(), "version": stage.version,
            **stage.stats}


def explain_result(result: VerificationResult, stage: StageModel, missing: list[str]) -> bool:
    """Attach `assist.explanation` when the model's text passes the number guard."""
    evidence = [{"source_name": e.source_name, "page": e.page, "text": e.text, "relation": e.relation}
                for e in result.evidence[:3]]
    claim = result.claim
    parsed = stage.ask(
        lambda model: explain_messages(model, claim.text, result.status.value, result.rationale, evidence, missing),
        [claim.text, result.status.value, result.rationale, *[e["text"][:500] for e in evidence]])
    if not parsed:
        return False
    text = str(parsed.get("explanation") or "").strip()
    action = str(parsed.get("next_action") or "").strip()
    # a hashed upload name copied into the text says nothing to a reviewer (5 / 40 with explain-v2): call it "tài liệu"
    text, action = (FILE_ID.sub("tài liệu", x) for x in (text, action))
    if not text:
        return False
    # everything the prompt shows counts as a source, page numbers and file names included: citing "trang 46" or
    # a hashed file name is not inventing a figure (v1 counted them and blocked 40 / 40 gpt-oss explanations)
    sources = [claim.text, result.rationale, *[f"{e.source_name} {e.page} {e.text}" for e in result.evidence]]
    if new_numbers(f"{text} {action}", *sources):
        return False  # a number nobody wrote: the explanation is not shown
    result.assist["explanation"] = {"text": text, "next_action": action, "version": stage.version}
    return True
