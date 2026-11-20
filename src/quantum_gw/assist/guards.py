"""Checks applied in code to every model reply before it is used (registration llm_stages_v1).

A model may read and may phrase; it may not invent. These are the two ways it could, and both are caught here
rather than trusted to the prompt.
"""
from __future__ import annotations

import json
import re
import unicodedata

_NUM = re.compile(r"\d+(?:[.,]\d+)*")


def fold(text: str) -> str:
    text = unicodedata.normalize("NFC", text or "").lower()
    return re.sub(r"\s+", " ", text).strip()


def numbers(text: str) -> set[str]:
    """Digits as written, with separators removed: '1.250.000' and '1,250,000' are the same number."""
    return {re.sub(r"[.,]", "", m) for m in _NUM.findall(text or "")}


# Digits that name a thing rather than measure it: "Scope 3", "phạm vi 1 và 2", "ISO 14064-1:2018",
# "GRI 305-1", "TCVN 7391". Taken out of the reply before the check, so an explanation that says
# "phạm vi 3" is not rejected as an invented number (limitation #9). Figures are never exempt.
_LABEL_NUMBERS = re.compile(
    r"(?i)\b(?:scope|ph[aạ]m vi)\s*[123](?:\s*(?:,|&|\+|và|va|and)\s*[123])*\b"
    r"|\b(?:iso|tcvn|iec|gri)\s*\d+(?:[-.]\d+)*(?::\s*(?:19|20)\d{2})?\b"
)


def new_numbers(reply: str, *sources: str) -> set[str]:
    """Numbers in `reply` that no source writes. Non-empty means the reply is rejected."""
    allowed: set[str] = set()
    for s in sources:
        allowed |= numbers(s)
    return numbers(_LABEL_NUMBERS.sub(" ", reply or "")) - allowed


def verbatim(span, sentence: str) -> str | None:
    """`span` if the sentence writes it (case, spacing and Unicode form ignored), else None."""
    if not isinstance(span, str) or not span.strip():
        return None
    return span.strip() if fold(span) in fold(sentence) else None


def parse_json(text: str | None) -> dict | None:
    """First JSON object in a reply (fences and text around it ignored)."""
    if not text:
        return None
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M)
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            if depth == 0:
                try:
                    obj = json.loads(text[start:i + 1])
                    return obj if isinstance(obj, dict) else None
                except json.JSONDecodeError:
                    break
        start = text.find("{", start + 1)
    return None
