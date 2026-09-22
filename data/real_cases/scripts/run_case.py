#!/usr/bin/env python3
"""Run cases from this pack through the AI-QUANTUM pipeline.

This is a thin front end. The pack-to-pipeline mapping it used to own now lives
in `quantum_gw.evaluation.real_cases`, inside the package, where the test suite
and `quantum-agent evaluate-real` reach it too. While that logic lived only
here, the real dataset could not gate anything: the unit suite was green at the
same time as the pipeline scored 0/4 on every adjudicated case.

    python scripts/run_case.py --list
    python scripts/run_case.py --all
    python scripts/run_case.py --case-id KDP-2024
    python scripts/run_case.py --case-id KDP-2024 --to-request body.json

Control cases (VN-*) need the original documents first:
    python scripts/download_sources.py --case-id VN-HPG-CONTROL
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # data/real_cases
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO / "src"))

# Windows console (cp1258) cannot print Vietnamese output otherwise.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from quantum_gw.evaluation.real_cases import RealCasePack, evaluate_real_cases  # noqa: E402
from quantum_gw.settings import load_settings  # noqa: E402


def control_documents(pack: RealCasePack, case: dict) -> list[dict]:
    """Originals on disk for a control case, matched by source id."""
    originals = pack.root / "sources" / "originals"
    files = sorted(originals.glob("*")) if originals.exists() else []
    # Match on the full source id stem rather than its first underscore-separated
    # token: "BVH" alone matches any filename containing those letters, so a
    # Hoa Phat document could be fed to the Bao Viet case.
    matched = [f for f in files if any(sid.lower() in f.stem.lower() for sid in case["source_ids"])]
    if not matched:
        raise SystemExit(
            f"{case['case_id']} là control case: cần tài liệu gốc.\n"
            f"Chạy trước: python {ROOT / 'scripts' / 'download_sources.py'} "
            f"--case-id {case['case_id']}"
        )
    return [
        {"path": str(f), "role": "claim_source" if i == 0 else "evidence",
         "source_type": "internal"}
        for i, f in enumerate(matched)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id")
    parser.add_argument("--all", action="store_true", help="run every adjudicated case")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--to-request", metavar="OUT.json",
                        help="write an API request body instead of running")
    args = parser.parse_args()

    pack = RealCasePack(ROOT)
    by_id = {c["case_id"]: c for c in pack.cases}

    if args.list:
        for c in pack.cases:
            print(f"{c['case_id']:16s} split={c['split']:8s} "
                  f"expected={c['expected_verification']:35s} {c['organization']}")
        return 0

    if args.case_id and args.case_id not in by_id:
        raise SystemExit(f"Không có case '{args.case_id}'. Dùng --list để xem danh sách.")

    if args.to_request:
        if not args.case_id:
            raise SystemExit("--to-request cần --case-id")
        case = by_id[args.case_id]
        documents = (
            control_documents(pack, case) if case["split"] == "control"
            else [d.model_dump(mode="json", exclude_none=True) for d in pack.documents(case)]
        )
        Path(args.to_request).write_text(
            json.dumps({"documents": documents}, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Đã ghi {args.to_request} — gửi thử:")
        print(f'  curl -X POST http://localhost:8010/v1/analyze/text '
              f'-H "Content-Type: application/json" -d @{args.to_request}')
        return 0

    if not (args.all or args.case_id):
        parser.print_help()
        return 1

    if args.case_id and by_id[args.case_id]["split"] == "control":
        raise SystemExit(
            f"{args.case_id} là control case và không có nhãn để chấm. "
            "Chạy qua API hoặc CLI với tài liệu gốc."
        )

    metrics = evaluate_real_cases(load_settings(), ROOT)
    selected = [
        c for c in metrics["cases"]
        if args.all or c["case_id"] == args.case_id
    ]
    for report in selected:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    if len(selected) > 1:
        matched = sum(1 for r in selected if r["outcome"] == "MATCH")
        print(f"\nTổng kết: {matched}/{len(selected)} case khớp kỳ vọng")
        print(f"  verification status : {metrics['verification_status_accuracy']}")
        print(f"  evidence stance     : {metrics['evidence_stance_accuracy']}")
        print(f"  risk band           : {metrics['risk_band_accuracy']}")
        print(f"  legal check coverage: {metrics['legal_check_coverage']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
