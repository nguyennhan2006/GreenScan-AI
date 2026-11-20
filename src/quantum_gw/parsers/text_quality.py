"""Is this text really text? Mojibake from legacy Vietnamese fonts, measured per page.

A PDF made with a TCVN3 or VNI font carries a text layer that extracts as
"hi~u lµc", "Bé Tµi chÝnh": every character is a valid code point, so nothing
fails, and the run quietly reads garbage (Luật 78/2025/QH15 in data/legal/raw has
such a page). OCR does not help a page the parser never sends to OCR. This
module gives the share of words that cannot be Vietnamese or English, so a page
can be flagged, and read by OCR instead when OCR is available.

A word is garbled when it has a letter outside the Vietnamese alphabet (µ, ß,
Greek, Cyrillic), a legacy-font symbol between letters (¬ § ¸ ~ …), or an
accented capital after a lower-case letter ("chÝnh"), which TCVN3 produces for
tone marks.
"""

from __future__ import annotations

import re
import unicodedata

# Marks a Vietnamese vowel can carry: circumflex, breve, horn and the five tones.
_VN_MARKS = {"̀", "́", "̂", "̃", "̆", "̉", "̛", "̣"}
_SYMBOLS_IN_WORD = set("¬§¸¹®©¶¦÷~^`|¤¢£¥ª«»¯±´¼½¾¿×ØÞðþ¦µ")
_TOKEN = re.compile(r"\S+")


def _vietnamese_letter(char: str) -> bool:
    if char.isascii():
        return char.isalpha()
    if char in "đĐ":
        return True
    parts = unicodedata.normalize("NFD", char)
    return parts[0].isascii() and parts[0].isalpha() and all(m in _VN_MARKS for m in parts[1:]) and len(parts) > 1


def garbled(word: str) -> bool:
    letters = [c for c in word if c.isalpha()]
    if not letters:
        return False
    if any(not _vietnamese_letter(c) for c in letters):
        return True
    core = word.strip(".,;:!?()[]{}\"'“”‘’-–—…")
    if any(c in _SYMBOLS_IN_WORD for c in core) and any(c.isalpha() for c in core):
        return True
    # "chÝnh", "vÒ": an accented capital right after a lower-case letter.
    return any(a.islower() and b.isupper() and not b.isascii() for a, b in zip(core, core[1:], strict=False))


def garbled_share(text: str) -> float:
    """Share of words with letters that cannot be Vietnamese or English; 0 for text without words."""
    words = [w for w in _TOKEN.findall(unicodedata.normalize("NFC", text or "")) if any(c.isalpha() for c in w)]
    if not words:
        return 0.0
    return sum(1 for w in words if garbled(w)) / len(words)
