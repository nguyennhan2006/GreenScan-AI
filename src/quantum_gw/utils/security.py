from __future__ import annotations

from quantum_gw.utils.text import normalize_for_match

SUSPICIOUS_PATTERNS = tuple(normalize_for_match(pattern) for pattern in (
    "ignore previous instructions",
    "ignore all previous",
    "system prompt",
    "developer message",
    "do not cite",
    "hide this evidence",
    "bỏ qua hướng dẫn trước",
    "bỏ qua mọi chỉ dẫn",
    "không được trích dẫn",
    "che giấu bằng chứng",
))


def contains_prompt_injection(text: str) -> bool:
    normalized = normalize_for_match(text)
    return any(pattern in normalized for pattern in SUSPICIOUS_PATTERNS)
