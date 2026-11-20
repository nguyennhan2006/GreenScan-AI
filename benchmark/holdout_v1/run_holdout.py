"""Holdout v1 (HOLDOUT_2026-11-15.md): one run, label-free protocol, on two companies never used before.

1. Original run: claims, verdicts, queue, flags; every CONTRADICTED is written out for reading by hand.
2. Planted run: for every claim with a numeric match in some passage, the first measured figure of the
   claim sentence is doubled inside the report text (built from the run's clean layer); the evidence
   document is unchanged. Detection = CONTRADICTED or a review flag; queue recall = mutated claims in queue.

usage (repo root): .venv/Scripts/python.exe -I benchmark/holdout_v1/run_holdout.py
writes benchmark/holdout_v1/results.json and contradicted_to_read.jsonl
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

os.environ["QUANTUM_PROFILE"] = "offline"
os.environ.setdefault("QUANTUM_RUNS_DIR", tempfile.mkdtemp(prefix="gs-holdout-"))
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "benchmark" / "gs_mutation_v1"))

from build import _scaled  # noqa: E402  (same figure scaling as GS-Mutation M1)

from quantum_gw.agents.orchestrator import OrchestratorAgent  # noqa: E402
from quantum_gw.domain.enums import DocumentRole, SourceType  # noqa: E402
from quantum_gw.domain.models import DocumentInput  # noqa: E402
from quantum_gw.settings import load_settings  # noqa: E402

OBJ = ROOT / "data" / "crawl" / "vn30" / "raw" / "objects" / "sha256"
HOLDOUT = {
    "PAN": {"claim": OBJ / "90" / "90da9a635f95b47d72357232f4c1bd0dc24190237eb86dfb36ea222817ee3e37.pdf",
            "evidence": OBJ / "da" / "dae2855175aa4014d347bbbd9c70a2333f764dfac2c32afe3b10b1fa318ab3ef.pdf",
            "claim_type": SourceType.INTERNAL, "evidence_type": SourceType.FINANCIAL,
            "claim_name": "PAN_SR_2020_EN.pdf", "evidence_name": "PAN_AR_2020_EN.pdf"},
    "DPR": {"claim": OBJ / "40" / "40d75353104099c6e86d2112e2c25dbe6c998c3f1d31af294a03e0c445e765a8.pdf",
            "evidence": OBJ / "07" / "073868c104a3307d0b61ff99da88825f97ac3dced18cc36ca6bf0286408e12c2.pdf",
            "claim_type": SourceType.INTERNAL, "evidence_type": SourceType.FINANCIAL,
            "claim_name": "DPR_BCTN.pdf", "evidence_name": "DPR_BCTC.pdf"},
}


def run(docs):
    t = time.time()
    result = OrchestratorAgent(load_settings()).run(docs)
    return result, round(time.time() - t, 1)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    out, to_read = {}, []
    # Optional: company subset and an output tag (a re-run after fixes is no longer out-of-sample: tag it).
    tag = os.environ.get("HOLDOUT_TAG", "")
    chosen = sys.argv[1:] or list(HOLDOUT)
    for company, h in ((c, HOLDOUT[c]) for c in chosen):
        docs = [DocumentInput(path=str(h["claim"]), name=h["claim_name"], role=DocumentRole.CLAIM_SOURCE, source_type=h["claim_type"]),
                DocumentInput(path=str(h["evidence"]), name=h["evidence_name"], role=DocumentRole.EVIDENCE, source_type=h["evidence_type"])]
        result, secs = run(docs)
        vs = result.verifications
        queued = {p["item_id"] for p in result.priorities if p.get("item_type") == "claim" and p.get("in_queue")}
        for v in vs:
            if v.status.value == "CONTRADICTED":
                to_read.append({"company": company, "claim": v.claim.text, "page": v.claim.source_page,
                                "rationale": v.rationale,
                                "passage": next((e.text[:600] for e in v.evidence if e.relation == "CONTRADICTS"), "")})
        # planted run: figures doubled in the report text, evidence unchanged
        run_dir = Path(result.output_directory)
        units = [json.loads(line) for line in (run_dir / "contract" / "clean.jsonl").open(encoding="utf-8")]
        text = "\n\n".join(u["text"] for u in units if u.get("role") == "claim_source")
        targets = [v for v in vs if any(e.relation == "SUPPORTS" and e.relation_method == "numeric" for e in v.evidence)]
        planted = {}
        for v in targets:
            new = _scaled(v.claim.text, 1)  # factor 2.0
            if new and v.claim.text in text:
                text = text.replace(v.claim.text, new, 1)
                planted[new] = v.claim.text
        caught, in_queue, found = 0, 0, 0
        if planted:
            docs2 = [DocumentInput(name=h["claim_name"] + ".planted.txt", text=text, role=DocumentRole.CLAIM_SOURCE, source_type=h["claim_type"]),
                     docs[1]]
            result2, secs2 = run(docs2)
            queued2 = {p["item_id"] for p in result2.priorities if p.get("item_type") == "claim" and p.get("in_queue")}
            for v in result2.verifications:
                if v.claim.text in planted:
                    found += 1
                    caught += v.status.value == "CONTRADICTED" or bool(v.review_flags)
                    in_queue += v.claim.claim_id in queued2
        else:
            secs2 = 0
        out[company] = {
            "seconds_original": secs, "seconds_planted": secs2,
            "claims": len(vs), "verdicts": dict(Counter(v.status.value for v in vs)),
            "claim_types": dict(Counter(v.claim.claim_type for v in vs)),
            "queue": len(queued), "review_flags": dict(Counter(f for v in vs for f in v.review_flags)),
            "contradicted_to_read": sum(1 for r in to_read if r["company"] == company),
            "planted": len(planted), "planted_found_again": found,
            "planted_caught_contradicted_or_flag": caught, "planted_in_queue": in_queue,
        }
        print(f"[holdout] {company}: {json.dumps(out[company], ensure_ascii=False)}", flush=True)
    (HERE / f"results{tag}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    with (HERE / f"contradicted_to_read{tag}.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for r in to_read:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("[holdout] done")


if __name__ == "__main__":
    main()
