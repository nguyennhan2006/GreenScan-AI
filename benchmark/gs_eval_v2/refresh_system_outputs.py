"""Map every labeled pool-A item to the CURRENT system's output (runs on or after CURRENT_FROM).

Items were sampled from all runs in .quantum/runs, some made by older code (July–September).
This script keeps item ids and labels unchanged and re-attaches system outputs from current runs
only, matching on the normalised claim text (exact first, then containment with length ratio ≥ 0.8).
Items the current extractor no longer extracts are kept with match = "not_extracted".

Writes inputs/system_outputs_current.jsonl and inputs/refresh_stats.json.
"""
from __future__ import annotations

import os
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from build_inputs import compact_cv, norm, system_claim_attrs  # noqa: E402

CURRENT_FROM = os.environ.get("GS_CURRENT_FROM", "2026-10-22")


def current_runs() -> list[Path]:
    out = []
    for rdir in sorted((ROOT / ".quantum" / "runs").iterdir()):
        f = rdir / "result.json"
        if not f.exists():
            continue
        m = json.loads((rdir / "manifest.json").read_text(encoding="utf-8")) if (rdir / "manifest.json").exists() else {}
        if str(m.get("created_at", "")) >= CURRENT_FROM:
            out.append(rdir)
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    index: dict[str, tuple[str, dict, dict | None, str]] = {}
    pool_status: Counter = Counter()
    for rdir in current_runs():
        d = json.loads((rdir / "result.json").read_text(encoding="utf-8"))
        stamp = d["manifest"].get("created_at", "")
        risks = {r["claim_id"]: r for r in d.get("risks", [])}
        for v in d.get("verifications", []):
            k = norm(v["claim"].get("text"))
            if k not in index or stamp > index[k][0]:
                index[k] = (stamp, v, risks.get(v["claim"]["claim_id"]), rdir.name)
    for _, v, _, _ in index.values():
        pool_status[v["status"]] += 1
    keys = list(index)

    legacy = {json.loads(l)["item_id"]: json.loads(l) for l in (HERE / "inputs/system_outputs.jsonl").open(encoding="utf-8")}
    items = {}
    for kind in ("explain", "score", "edit"):
        for f in (HERE / kind / "batches").glob("*.jsonl"):
            for l in f.open(encoding="utf-8"):
                it = json.loads(l)
                if it["item_id"].startswith("A-"):
                    items[it["item_id"]] = it
    rows, how = [], Counter()
    for iid, it in sorted(items.items()):
        k = norm(it["claim"]["text"])
        hit, match = index.get(k), "exact"
        if hit is None:
            cands = [x for x in keys if (k in x or x in k) and min(len(k), len(x)) / max(len(k), len(x)) >= 0.8]
            if cands:
                hit, match = index[max(cands, key=len)], "containment"
        lg = legacy.get(iid, {})
        if hit is None:
            how["not_extracted"] += 1
            rows.append({"item_id": iid, "match": "not_extracted", "legacy_run_id": lg.get("run_id"),
                         "legacy_status": lg.get("system_status")})
            continue
        how[match] += 1
        _, v, risk, rid = hit
        rows.append({
            "item_id": iid, "match": match, "run_id": rid, "legacy_run_id": lg.get("run_id"),
            "legacy_status": lg.get("system_status"), "system_status": v["status"],
            "system_rationale": v.get("rationale"), "system_warnings": v.get("warnings"),
            "computed": compact_cv(v.get("computed_values")), "claim_attrs": system_claim_attrs(v["claim"]),
            "risk": None if risk is None else {
                "risk_score": risk.get("risk_score"), "severity": risk.get("severity"),
                "severity_cap_reason": risk.get("severity_cap_reason"),
                "components": [{"name": x["name"], "score": x["score"], "max_score": x["max_score"]}
                               for x in risk.get("components", [])]},
        })
    (HERE / "inputs/system_outputs_current.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    changed = Counter((r["legacy_status"], r.get("system_status", "not_extracted")) for r in rows
                      if r.get("system_status") != r["legacy_status"])
    stats = {"current_from": CURRENT_FROM, "current_runs": [p.name for p in current_runs()],
             "current_pool_unique_claims": len(index), "current_pool_status": dict(pool_status),
             "items": len(rows), "match": dict(how),
             "status_changed_legacy_to_current": {f"{a} -> {b}": n for (a, b), n in changed.most_common()}}
    (HERE / "inputs/refresh_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
