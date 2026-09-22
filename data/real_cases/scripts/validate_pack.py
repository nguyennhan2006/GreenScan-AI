#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_jsonl(path: Path):
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise AssertionError(f"{path}:{n}: {exc}") from exc
    return rows

def main() -> int:
    with (ROOT / "sources/source_registry.csv").open(encoding="utf-8-sig") as f:
        sources = list(csv.DictReader(f))
    claims = load_jsonl(ROOT / "claims/claims.jsonl")
    evidence = load_jsonl(ROOT / "evidence/evidence.jsonl")
    cases = [json.loads(p.read_text(encoding="utf-8"))
             for p in sorted((ROOT / "cases").glob("*/case.json"))]

    source_ids = [x["source_id"] for x in sources]
    assert len(source_ids) == len(set(source_ids)), "duplicate source ids"
    case_ids = [x["case_id"] for x in cases]
    assert len(case_ids) == len(set(case_ids)), "duplicate case ids"

    for c in cases:
        for sid in c["source_ids"]:
            assert sid in source_ids, (c["case_id"], sid)
        packet = ROOT / "cases" / c["case_id"] / f"{c['case_id']}_case_packet.pdf"
        assert packet.exists() and packet.stat().st_size > 1000, packet

    for cl in claims:
        assert cl["case_id"] in case_ids
        assert cl["expected_status"] in {"CONTRADICTED", "SUPPORTED", "PARTIALLY_SUPPORTED",
                                         "UNSUPPORTED", "INSUFFICIENT_EVIDENCE"}

    for ev in evidence:
        assert ev["case_id"] in case_ids
        assert ev["source_id"] in source_ids

    control = [c for c in cases if c["split"] == "control"]
    assert all(c["case_status"] == "NOT_ADJUDICATED_NO_GREENWASHING_LABEL" for c in control)

    print("VALID")
    print("cases:", len(cases))
    print("adjudicated demo/eval:", len([c for c in cases if c["split"] != "control"]))
    print("control cases:", len(control))
    print("sources:", len(sources))
    print("claims:", len(claims))
    print("evidence records:", len(evidence))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
