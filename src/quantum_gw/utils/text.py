from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path


TOKEN_RE = re.compile(r"[\w%+./-]+", re.UNICODE)
NUMBER_RE = re.compile(r"(?<!\w)(\d[\d.,]*)(?:\s*)(%|tco2e|co2e|kg|tấn|tan|mj|kwh|mwh|vnd|đồng|ty|tỷ|triệu|million|billion)?", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(20\d{2}|19\d{2})\b")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_for_match(text: str) -> str:
    text = normalize_text(text).lower()
    text = "".join(
        char for char in unicodedata.normalize("NFD", text) if unicodedata.category(char) != "Mn"
    )
    return text


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(normalize_for_match(text)) if len(token) > 1]


def stable_id(*parts: str, length: int = 16) -> str:
    digest = hashlib.sha256("||".join(parts).encode("utf-8", errors="ignore")).hexdigest()
    return digest[:length]


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def parse_numbers(text: str) -> list[tuple[float, str | None]]:
    values: list[tuple[float, str | None]] = []
    for raw, unit in NUMBER_RE.findall(normalize_for_match(text)):
        cleaned = raw.strip().rstrip(".,")
        if cleaned.count(",") and cleaned.count("."):
            if cleaned.rfind(",") > cleaned.rfind("."):
                cleaned = cleaned.replace(".", "").replace(",", ".")
            else:
                cleaned = cleaned.replace(",", "")
        elif cleaned.count(",") == 1 and len(cleaned.split(",")[-1]) <= 2:
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
        try:
            value = float(cleaned)
        except ValueError:
            continue
        multiplier = 1.0
        unit_norm = unit.lower() if unit else None
        if unit_norm in {"triệu", "million"}:
            multiplier = 1_000_000
        elif unit_norm in {"tỷ", "ty", "billion"}:
            multiplier = 1_000_000_000
        values.append((value * multiplier, unit_norm))
    return values


def split_sentences(text: str) -> list[str]:
    text = normalize_text(text)
    parts = re.split(r"(?<=[.!?])\s+|\n+|(?<=;)\s+", text)
    return [part.strip(" •\t") for part in parts if len(part.strip()) >= 12]


def path_name(path: str) -> str:
    return Path(path).name
