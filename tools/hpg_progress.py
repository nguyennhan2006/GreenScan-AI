"""Re-run the Hòa Phát control case and diff it against the 2026-09-22 baseline.

    python tools/hpg_progress.py                 # writes benchmark/progress_<today>.json
    python tools/hpg_progress.py --label n1      # benchmark/progress_<today>_n1.json

The baseline file is never rewritten (DECISIONS_LOG D-2026-09-22-01). Every
progress file carries the same fields so the before/after table in
RESEARCH_PROGRAM §12 can be filled from two JSON files. "False" counts are
left for the reviewer to fill: the script lists every CONTRADICTED and
SUPPORTED claim with its rationale so the manual check is a read, not a run.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "benchmark" / "baseline_2026-09-22.json"
INPUTS = [
    ROOT / "data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf",
    ROOT / "data/real_cases/sources/originals/HPG_Annual_Report_2024.pdf",
]


def run_pipeline() -> tuple[dict, float]:
    started = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-m", "quantum_gw.cli", "analyze", *map(str, INPUTS),
         "--roles", "claim_source,evidence", "--source-types", "internal,internal"],
        capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
    )
    elapsed = time.perf_counter() - started
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit(proc.returncode)
    match = re.search(r"Evidence pack: (.+?)[\\/]evidence_pack\.md", proc.stdout)
    if not match:
        raise SystemExit("could not find the run directory in CLI output:\n" + proc.stdout)
    run_dir = ROOT / match.group(1).strip()
    return json.loads((run_dir / "result.json").read_text(encoding="utf-8")), elapsed


def summarise(run: dict, elapsed: float, git_head: str) -> dict:
    claims, ver, risks, legal = run["claims"], run["verifications"], run["risks"], run["legal_checks"]
    def cnt(it):
        return dict(sorted(collections.Counter(it).items()))
    def listed(status):
        return [
            {"claim_id": c["claim_id"], "text": c["text"][:160], "source_page": c.get("source_page"),
             "rationale": (v.get("rationale") or "")[:220],
             "severity": r["severity"]}
            for c, v, r in zip(claims, ver, risks) if v["status"] == status
        ]
    high = [
        {"claim_id": c["claim_id"], "status": v["status"], "text": c["text"][:120],
         "components": {x["name"]: x["score"] for x in r["components"] if x["score"]}}
        for c, v, r in zip(claims, ver, risks) if r["severity"] in ("HIGH", "CRITICAL")
    ]
    rationales = collections.Counter((v.get("rationale") or "")[:60] for v in ver if v["status"] == "PARTIALLY_SUPPORTED")
    return {
        "snapshot_date": dt.date.today().isoformat(),
        "git_head": git_head,
        "run_id": run["run_id"],
        "elapsed_seconds_wall": round(elapsed, 1),
        "total_claims": len(claims),
        "claims_with_digits": sum(1 for c in claims if re.search(r"\d", c.get("text", ""))),
        "claim_type_counts": cnt(c.get("claim_type") for c in claims),
        "status_counts": cnt(v["status"] for v in ver),
        "severity_counts": cnt(r["severity"] for r in risks),
        "legal_finding_counts": cnt(x.get("legal_finding") for x in legal),
        "partial_rationale_variety": len(rationales),
        "contradicted_claims": listed("CONTRADICTED"),
        "supported_claims": listed("SUPPORTED"),
        "high_or_critical": high[:80],
        "manual_review": {"contradicted_judged_wrong": None, "supported_judged_weak": None, "high_judged_wrong": None,
                          "reviewer": "", "note": "điền tay sau khi soát"},
    }


def diff_table(base: dict, now: dict) -> str:
    b = base["hpg_control_run"]
    rows = [
        ("Claims extracted", b["total_claims"], now["total_claims"]),
        ("Claims with digits", b["claims_with_digits"], now["claims_with_digits"]),
        ("PARTIALLY_SUPPORTED", b["status_counts"].get("PARTIALLY_SUPPORTED", 0), now["status_counts"].get("PARTIALLY_SUPPORTED", 0)),
        ("SUPPORTED", b["status_counts"].get("SUPPORTED", 0), now["status_counts"].get("SUPPORTED", 0)),
        ("CONTRADICTED", b["status_counts"].get("CONTRADICTED", 0), now["status_counts"].get("CONTRADICTED", 0)),
        ("INSUFFICIENT_EVIDENCE", b["status_counts"].get("INSUFFICIENT_EVIDENCE", 0), now["status_counts"].get("INSUFFICIENT_EVIDENCE", 0)),
        ("UNSUPPORTED", b["status_counts"].get("UNSUPPORTED", 0), now["status_counts"].get("UNSUPPORTED", 0)),
        ("HIGH", b["severity_counts"].get("HIGH", 0), now["severity_counts"].get("HIGH", 0)),
        ("CRITICAL", b["severity_counts"].get("CRITICAL", 0), now["severity_counts"].get("CRITICAL", 0)),
        ("Legal findings ≠ INSUFFICIENT", 0, sum(v for k, v in now["legal_finding_counts"].items() if k != "INSUFFICIENT_EVIDENCE")),
        ("Distinct PARTIAL rationales", "n/a", now["partial_rationale_variety"]),
        ("Runtime (s)", b["elapsed_seconds_wall"], now["elapsed_seconds_wall"]),
    ]
    width = max(len(r[0]) for r in rows)
    lines = [f"{'Metric':<{width}} | {'22/09':>8} | {now['snapshot_date'][5:].replace('-', '/'):>8}", "-" * (width + 24)]
    lines += [f"{name:<{width}} | {str(a):>8} | {str(c):>8}" for name, a, c in rows]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="")
    args = parser.parse_args()
    git_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    run, elapsed = run_pipeline()
    now = summarise(run, elapsed, git_head)
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    suffix = f"_{args.label}" if args.label else ""
    out = ROOT / "benchmark" / f"progress_{now['snapshot_date']}{suffix}.json"
    out.write_text(json.dumps(now, ensure_ascii=False, indent=2), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(diff_table(base, now))
    print(f"\nwritten: {out.relative_to(ROOT)}")
    print("\nCONTRADICTED:")
    for c in now["contradicted_claims"]:
        print(f"  p{c['source_page']} | {c['text'][:90]} || {c['rationale'][:110]}")
    print("SUPPORTED:")
    for c in now["supported_claims"]:
        print(f"  p{c['source_page']} | {c['text'][:90]} || {c['rationale'][:110]}")


if __name__ == "__main__":
    main()
