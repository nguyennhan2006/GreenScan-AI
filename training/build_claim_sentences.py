"""T1 data: sentences from the corpus, with the rule extractor's decision as a weak label.

Reads the clean layer (data/crawl/vn30/contract/clean.jsonl — paragraphs with
company_id and the company-level split), splits every unit into sentences the
same way the extractor does, and runs GreenScan's ClaimExtractionAgent over
them. Each sentence gets:

  rule_label   1 if the rule extractor keeps it as a claim, else 0
  rule_reason  why the rules refused it (heading, fragment, …) or ""
  lexicon_hit  1 if it names an environmental metric/claim term (taxonomy)
  has_figure   1 if it carries a quantity (years excluded)

Weak labels train nothing on their own: they tell the teacher-labelling step
which sentences to sample (rules' positives, environmental sentences the rules
refused or missed, random negatives) so the teacher spends its calls where
rules and truth are likely to disagree.

usage: python training/build_claim_sentences.py [--out training/data/claim_sentences.jsonl]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quantum_gw.agents.claim_extractor import ClaimExtractionAgent  # noqa: E402
from quantum_gw.domain.enums import DocumentRole, SourceType  # noqa: E402
from quantum_gw.domain.models import EvidenceChunk  # noqa: E402
from quantum_gw.settings import load_settings  # noqa: E402
from quantum_gw.utils.text import normalize_for_match, parse_numbers, split_sentences  # noqa: E402


class _NullAudit:
    def write(self, *_args, **_kwargs):
        pass


def _value(raw):
    return None if raw in (None, "None", "") else raw


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--clean", default=str(ROOT / "data/crawl/vn30/contract/clean.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "training/data/claim_sentences.jsonl"))
    ap.add_argument("--min-chars", type=int, default=25)
    ap.add_argument("--max-chars", type=int, default=500)
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    settings = load_settings()
    extractor = ClaimExtractionAgent(settings.claim_extraction, _NullAudit())
    # taxonomy buckets are {name: {language: [normalized terms]}}
    terms = sorted({t for section in (extractor.claim_types, extractor.metrics)
                    for by_lang in section.values() for lang_terms in by_lang.values() for t in lang_terms},
                   key=len, reverse=True)

    rows, seen = [], set()
    for line in open(args.clean, encoding="utf-8"):
        unit = json.loads(line)
        text = unit.get("text") or ""
        if _value(unit.get("duplicate_of")) or not text.strip():
            continue
        chunk = EvidenceChunk(
            chunk_id=unit["unit_id"], doc_id=unit["doc_id"], source_name=unit.get("source_name") or "",
            role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL, text=text,
            page=int(unit["page"]) if _value(unit.get("page")) else None,
            is_table=str(unit.get("is_table")) == "True",
        )
        kept = {normalize_for_match(c.text) for c in extractor.run([chunk])}
        refused = {normalize_for_match(s): reason for _c, _i, s, reason in getattr(extractor, "rejected_sentences", [])}
        for sentence in split_sentences(text):
            sentence = " ".join(sentence.split())
            if not (args.min_chars <= len(sentence) <= args.max_chars):
                continue
            key = hashlib.sha1(normalize_for_match(sentence).encode("utf-8")).hexdigest()[:16]
            if key in seen:
                continue
            seen.add(key)
            norm = normalize_for_match(sentence)
            rows.append({
                "id": key,
                "company_id": unit.get("company_id"),
                "split": unit.get("split"),
                "doc_id": unit["doc_id"],
                "page": _value(unit.get("page")),
                "reporting_year": _value(unit.get("reporting_year")),
                "text": sentence,
                "rule_label": int(norm in kept),
                "rule_reason": refused.get(norm, ""),
                "lexicon_hit": int(any(t and t in norm for t in terms)),
                "has_figure": int(any(u is not None or not 1900 <= v <= 2100 for v, u in parse_numbers(sentence))),
            })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    random.Random(args.seed).shuffle(rows)
    with out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    c = Counter((r["rule_label"], r["lexicon_hit"]) for r in rows)
    print(f"{len(rows)} sentences → {out}")
    print(f"  rule claim & env term: {c[(1, 1)]} · rule claim, no term: {c[(1, 0)]} · "
          f"env term, rules refused/missed: {c[(0, 1)]} · neither: {c[(0, 0)]}")
    print("  by split:", dict(Counter(r["split"] for r in rows)))
    print("  companies:", len({r['company_id'] for r in rows}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
