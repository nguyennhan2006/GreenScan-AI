"""Check one GS-Claims v1 label file against items.jsonl and LABELING_GUIDE.md (gs-claims-v1.0).

usage: .venv/Scripts/python.exe -I benchmark/gs_claims_v1/validate_labels.py <labels.jsonl>
Exit code 0 and "OK" when every item is labelled once with allowed values; else every problem is listed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALLOWED = {
    "is_claim": {"yes", "no"},
    "claim_kind": {"metric_disclosure", "performance", "commitment", "practice", "promotional", "na"},
    "has_figure": {"yes", "no"},
    "has_period": {"yes", "implicit", "no"},
    "has_baseline": {"yes", "no", "na"},
    "has_ghg_scope": {"yes", "no", "na"},
    "has_boundary": {"yes", "no"},
    "cites_independent_source": {"yes", "no"},
    "promotional_language": {"yes", "no"},
}


def problems(path: Path) -> list[str]:
    sys.stdout.reconfigure(encoding="utf-8")
    ids = [json.loads(line)["item_id"] for line in (HERE / "items.jsonl").open(encoding="utf-8") if line.strip()]
    out, seen = [], {}
    for n, line in enumerate(path.open(encoding="utf-8"), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            out.append(f"line {n}: not JSON ({exc})")
            continue
        iid = row.get("item_id")
        if iid in seen:
            out.append(f"line {n}: {iid} labelled twice")
        seen[iid] = row
        if row.get("guide_version") != "gs-claims-v1.0":
            out.append(f"line {n}: guide_version must be gs-claims-v1.0")
        for field, allowed in ALLOWED.items():
            if row.get(field) not in allowed:
                out.append(f"line {n} {iid}: {field}={row.get(field)!r} not in {sorted(allowed)}")
        if row.get("is_claim") == "no" and row.get("claim_kind") != "na":
            out.append(f"line {n} {iid}: is_claim=no needs claim_kind=na")
        if row.get("is_claim") == "yes" and row.get("claim_kind") == "na":
            out.append(f"line {n} {iid}: is_claim=yes needs a claim_kind")
    missing = [i for i in ids if i not in seen]
    extra = [i for i in seen if i not in ids]
    if missing:
        out.append(f"missing {len(missing)} items, e.g. {missing[:5]}")
    if extra:
        out.append(f"unknown item_ids {extra[:5]}")
    return out


if __name__ == "__main__":
    errs = problems(Path(sys.argv[1]))
    print("OK" if not errs else "\n".join(errs[:60]))
    sys.exit(1 if errs else 0)
