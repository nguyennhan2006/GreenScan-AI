#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_jsonl(path: Path):
    # split("\n") not splitlines(): splitlines() also breaks on U+2028/U+2029/
    # U+0085, which appear in text extracted from Vietnamese PDFs and are legal
    # inside a JSON string.
    return [json.loads(x) for x in path.read_text(encoding="utf-8").split("\n") if x.strip()]

def main() -> int:
    claims = load_jsonl(ROOT / "claims/claims.jsonl")
    evidence = load_jsonl(ROOT / "evidence/evidence.jsonl")
    by_case = {}
    for ev in evidence:
        by_case.setdefault(ev["case_id"], []).append(ev)

    out = ROOT / "training/claim_evidence_pairs.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for cl in claims:
            row = {
                "case_id": cl["case_id"],
                "claim_id": cl["claim_id"],
                "claim_text": cl["text"],
                "evidence": by_case.get(cl["case_id"], []),
                "label": cl["expected_status"],
                "case_status": cl["case_status"],
                "adjudication_scope": cl["adjudication_scope"],
                "training_eligibility": cl["training_eligibility"],
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
