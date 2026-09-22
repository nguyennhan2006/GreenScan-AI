#!/usr/bin/env python3
"""Vertical slice: a company claim through the whole legal layer, end to end.

    claim -> legal issue -> applicable law at a date -> clauses -> rules
          -> conditions -> legal finding + citations

Run it two ways to see the layer's central property — the same claim checked
historically and against today's criteria are different questions with different
answers:

    python tools/legal_vertical_slice.py --mode current_policy_alignment
    python tools/legal_vertical_slice.py --mode historical_compliance --published 2023-05-01

`--demo-text` parses a short fixture statute so the L1->L3 mechanism can be seen
working while the authoritative text is still unavailable. The fixture is
labelled as such everywhere it appears; it is never presented as law.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from quantum_gw.legal import LegalChecker, LegalCorpus, RulePack, parse_document  # noqa: E402
from quantum_gw.legal.corpus import CHECK_MODES, CURRENT  # noqa: E402
from quantum_gw.legal.parser import structure_summary  # noqa: E402

REGISTRY = REPO / "configs/legal/LEGAL_SOURCE_REGISTRY.yaml"
RULE_PACK = REPO / "configs/legal/rule_pack_vn_green_v0.1.yaml"

# A real claim shape taken from the crawled VN corpus, with evidence passages of
# the kind the retriever returns.
CLAIM = {
    "claim_id": "DEMO-C001",
    "claim_type": "green_project",
    "text": "Dự án nhà máy tái chế của Công ty đáp ứng tiêu chí dự án xanh.",
    "source_name": "BaoCao_PTBV_2025.pdf",
    "source_page": 42,
}
EVIDENCE = [
    {"chunk_id": "e1", "page": 45, "source_name": "BaoCao_PTBV_2025.pdf",
     "text": "Dự án nhà máy tái chế công suất 200 tấn/ngày đi vào vận hành năm 2025."},
    {"chunk_id": "e2", "page": 46, "source_name": "BaoCao_PTBV_2025.pdf",
     "text": "Tỷ lệ tái chế chất thải đạt 62% trong năm 2025."},
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=CHECK_MODES, default=CURRENT)
    ap.add_argument("--published", help="claim publication date, YYYY-MM-DD")
    ap.add_argument("--today", default="2026-08-09")
    ap.add_argument("--demo-text", action="store_true",
                    help="parse a labelled fixture statute to exercise L1->L3")
    args = ap.parse_args()

    corpus = LegalCorpus.from_registry(REGISTRY)
    pack = RulePack.from_yaml(RULE_PACK)

    print("=" * 74)
    print("LEGAL LAYER — VERTICAL SLICE")
    print("=" * 74)
    print(f"\nL0 registry: {len(corpus.documents)} documents")
    cov = corpus.coverage()
    print(f"   usable (full text extracted): {cov['usable']}/{cov['documents']}")
    print(f"   by acquisition status: {cov['by_text_acquisition']}")

    if args.demo_text:
        fixture = (REPO / "tests/fixtures/legal/QD21_demo_excerpt.txt")
        clauses = parse_document("QD21-2025-DEMO", fixture.read_text(encoding="utf-8"))
        print("\nL1 clause parsing — FIXTURE TEXT, NOT THE REAL DECISION")
        print(f"   {structure_summary(clauses)}")
        for c in clauses[:6]:
            print(f"   {c.clause_id:52} {c.citation:26} {c.text[:44]!r}")

    print(f"\nL2 temporal resolution — mode: {args.mode}")
    published = date.fromisoformat(args.published) if args.published else None
    today = date.fromisoformat(args.today)
    as_of = corpus.resolve_as_of(args.mode, published, today)
    print(f"   as_of = {as_of}")
    print(f"   QD 21/2025 in force on that date: "
          f"{corpus.documents['QD21-2025-QD-TTg'].in_force_on(as_of)}")
    chain = corpus.effective_chain("ND08-2022-ND-CP", as_of)
    print(f"   NĐ 08/2022 effective chain: {[d.document_number for d in chain]}")

    print(f"\nL3 rule pack: {pack.version} ({len(pack.rules)} rule)")

    result = LegalChecker(corpus, pack).check(
        claim=CLAIM, evidence=EVIDENCE, check_mode=args.mode,
        claim_published=published, today=today,
    )

    print("\nLEGAL CHECK RESULT")
    print("-" * 74)
    print(json.dumps(result.to_json(), ensure_ascii=False, indent=2))
    print("-" * 74)
    print("\nĐây là hồ sơ kiểm tra pháp lý có căn cứ, không phải kết luận doanh nghiệp vi phạm.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
