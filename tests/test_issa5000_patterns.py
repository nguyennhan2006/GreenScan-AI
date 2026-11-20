"""ISSA 5000 configs (việc 12–14): each conclusion pattern matches its own source sentence
and no sentence of another conclusion type; the report elements cover paragraph 190 (a)–(l)."""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = yaml.safe_load((ROOT / "configs" / "issa5000_conclusion_patterns.yaml").read_text(encoding="utf-8"))
ELEMENTS = yaml.safe_load((ROOT / "configs" / "issa5000_report_elements.yaml").read_text(encoding="utf-8"))


def _hits(pattern: dict, text: str) -> bool:
    text = " ".join(text.split())
    if not re.search(pattern["pattern"], text, re.IGNORECASE):
        return False
    return not any(word in text.lower() for word in pattern.get("not_if", []))


def test_each_pattern_matches_its_own_span():
    for p in PATTERNS["patterns"]:
        for span in [p["pattern_span"], *p.get("extra_spans", [])]:
            assert _hits(p, span), (p["pattern_id"], span[:60])


def test_no_pattern_matches_another_conclusion_type():
    for p in PATTERNS["patterns"]:
        for other in PATTERNS["patterns"]:
            if (other["conclusion_type"], other["assurance_level"]) == (p["conclusion_type"], p["assurance_level"]):
                continue
            if other["language"] != p["language"]:
                continue
            assert not _hits(p, other["pattern_span"]), (p["pattern_id"], other["pattern_id"])


def test_all_twelve_illustrations_are_sourced():
    sources = {s for p in PATTERNS["patterns"] for s in p["source_id"]}
    assert sources == {f"IR-{c}" for c in "ABCDEFGH"} | {f"APP3-{i}" for i in range(1, 5)}


def test_report_elements_cover_paragraph_190():
    paras = {e["para"] for e in ELEMENTS["elements"]}
    for letter in "abcdefghijkl":
        assert f"190({letter})" in paras, letter
    assert {e["applies"] for e in ELEMENTS["elements"]} <= {"always", "limited", "reasonable", "modified", "listed", "if_applicable"}
