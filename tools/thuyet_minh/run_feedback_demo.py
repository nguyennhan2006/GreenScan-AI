"""Chương 10 của thuyết minh: chạy thật vòng tuỳ biến theo tổ chức và học từ phản hồi, ghi kết quả ra JSON.

Usage (repo root): .venv/Scripts/python.exe -I tools/thuyet_minh/run_feedback_demo.py <trace_dir> [--bench-limit N]

Mọi thứ ghi vào thư mục tạm (kho quyết định, kho org pack, phiên chạy, sổ mô hình), không đụng kho thật.
Kết quả: <trace_dir>/feedback_demo.json, đọc bởi tools/thuyet_minh/build_tm_feedback.py.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
TRACE = Path(sys.argv[1])
BENCH_LIMIT = int(sys.argv[sys.argv.index("--bench-limit") + 1]) if "--bench-limit" in sys.argv else 453
TMP = Path(tempfile.mkdtemp(prefix="tm-feedback-"))
os.environ.update({
    "QUANTUM_REVIEWS_FILE": str(TMP / "reviews" / "decisions.jsonl"),
    "QUANTUM_RUNS_DIR": str(TMP / "runs"),
    "QUANTUM_DOCUMENTS_DIR": str(TMP / "documents"),
    "QUANTUM_ORG_PACK_STORE": str(TMP / "org_packs"),
    "QUANTUM_LLM_STANCE": "off",
    "QUANTUM_ORG_PACKS": "",
})
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from quantum_gw.agents.orchestrator import OrchestratorAgent  # noqa: E402
from quantum_gw.domain.enums import DocumentRole, SourceType  # noqa: E402
from quantum_gw.domain.models import DocumentInput  # noqa: E402
from quantum_gw.feedback import dataset, registry  # noqa: E402
from quantum_gw.feedback.bench import build_cases, check_ratchet, run_cases  # noqa: E402
from quantum_gw.feedback.hygiene import QAStore, agreement, clean_labels  # noqa: E402
from quantum_gw.feedback.miner import measure_cue, mine  # noqa: E402
from quantum_gw.feedback.stance_model import KIND, challenger_metrics, champion_metrics, train  # noqa: E402
from quantum_gw.legal import org_registry  # noqa: E402
from quantum_gw.legal.org_draft import draft  # noqa: E402
from quantum_gw.settings import load_settings  # noqa: E402
from quantum_gw.storage.reviews import ReviewStore  # noqa: E402

CASES = {
    "A": [("data/sample/company_esg_2024.txt", "claim_source", "internal"),
          ("data/sample/financial_2024.txt", "evidence", "financial"),
          ("data/sample/legal_notice_2024.txt", "evidence", "legal")],
    "B": [("data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf", "claim_source", "internal"),
          ("data/real_cases/sources/originals/HPG_Annual_Report_2024.pdf", "evidence", "financial")],
}
OUT: dict = {"tmp": str(TMP)}


def docs(case):
    return [DocumentInput(path=p, role=DocumentRole(r), source_type=SourceType(t)) for p, r, t in CASES[case]]


def log(msg):
    print(f"[fb-demo] {msg}", flush=True)


# ------------------------------------------------------------------ 1. Ca A: phản hồi -> tiền lệ -> hàng soát
t = time.perf_counter()
first = OrchestratorAgent(load_settings()).run(docs("A"))
store = ReviewStore()
decisions = []
for v in first.verifications:
    ev = [e.model_dump(mode="json") for e in v.evidence]
    claim = v.claim.model_dump(mode="json")
    if "trái phiếu xanh" in v.claim.text:
        decisive = [e["chunk_id"] for e in ev if "180" in e["text"]][:1]
        rec = store.record(run_id=first.run_id, claim_id=v.claim.claim_id, reviewer="Hà (kiểm toán viên)",
                           decision="OVERRIDE", reviewer_status="CONTRADICTED", override_reason="MODEL_MISREAD",
                           ai_status=v.status.value, evidence=ev, claim=claim, decisive_chunk_ids=decisive,
                           reviewer_role="auditor",
                           comment="BCTC ghi 180 tỷ đồng trái phiếu xanh chưa được phân bổ: 'sử dụng hoàn toàn' là sai.")
        OUT["a2"] = {"claim_id": v.claim.claim_id, "text": v.claim.text, "ai_status": v.status.value,
                     "decisive_rank": next((e["rank"] for e in rec.evidence_snapshot if e["chunk_id"] in decisive), None),
                     "decisive_preview": next((e["text_preview"] for e in rec.evidence_snapshot if e["chunk_id"] in decisive), ""),
                     "error_stage": rec.error_stage}
    else:
        rec = store.record(run_id=first.run_id, claim_id=v.claim.claim_id, reviewer="Hà (kiểm toán viên)",
                           decision="CONFIRM", ai_status=v.status.value, evidence=ev, claim=claim,
                           decisive_chunk_ids=[ev[0]["chunk_id"]] if ev else [], reviewer_role="auditor")
    decisions.append({"claim_id": v.claim.claim_id, "decision": rec.decision, "ai": v.status.value,
                      "label": rec.reviewer_status or v.status.value, "stage": rec.error_stage,
                      "text": v.claim.text})
OUT["decisions"] = decisions
OUT["stats"] = store.stats()

second = OrchestratorAgent(load_settings()).run(docs("A"))
OUT["rerun"] = {
    "same_verdicts": [v.status.value for v in second.verifications] == [v.status.value for v in first.verifications],
    "manifest_feedback": second.manifest.feedback,
    "precedents": {cid: [{k: c[k] for k in ("similarity", "ai_status", "label", "overridden", "comment", "shared_words")}
                         for c in cards] for cid, cards in (second.precedents or {}).items()},
    "raised": [{"claim_id": p["item_id"], "raised_by": p.get("raised_by"), "score": p["priority_score"], "rank": p["rank"]}
               for p in second.priorities if p.get("raised_by")],
    "queue_first": sorted(p["item_id"] for p in first.priorities if p["in_queue"]),
    "queue_second": sorted(p["item_id"] for p in second.priorities if p["in_queue"]),
}
OUT["seconds_a"] = round(time.perf_counter() - t, 2)
log(f"Ca A xong ({OUT['seconds_a']} s): {len(OUT['rerun']['precedents'])} tuyên bố có tiền lệ")

# ------------------------------------------------------------------ 2. GS-Feedback + bánh cóc
qa = QAStore(reviews=store)
cases = build_cases(store.gold_records(), qa.all())
results = run_cases(cases)
OUT["bench"] = {"results": results, "report": check_ratchet(results, TMP / "ratchet.json", update=True, note="thuyết minh")}
log(f"GS-Feedback: {OUT['bench']['report']['passed']}/{len(results)} qua")

# ------------------------------------------------------------------ 3. Máy đào luật + đo trên GS-Bench
t = time.perf_counter()
proposals = mine()
OUT["proposals"] = {"cues": [{k: c[k] for k in ("term", "family", "support", "against", "note")} for c in proposals["cues"]],
                    "rules": len(proposals["rules"]), "queries": len(proposals["queries"]),
                    "org_rules": len(proposals["org_rules"])}
if proposals["cues"]:
    top = proposals["cues"][0]
    OUT["measure"] = measure_cue(top["term"], top["family"], cases, BENCH_LIMIT)
OUT["seconds_miner"] = round(time.perf_counter() - t, 1)
log(f"Máy đào xong ({OUT['seconds_miner']} s): {OUT.get('measure', {}).get('gs_bench')}")

# ------------------------------------------------------------------ 4. Hai người soát
qa.record_second(run_id=first.run_id, claim_id=OUT["a2"]["claim_id"], reviewer="Lan (kiểm toán viên 2)",
                 status="CONTRADICTED", first_reviewer="Hà (kiểm toán viên)")
OUT["agreement"] = {k: v for k, v in agreement(store.gold_records(), qa.all()).items() if k != "disagreements"}

# ------------------------------------------------------------------ 5. Org pack: soạn nháp, tải lên, duyệt bốn mắt, Ca B
policy = Path("configs/org_packs/demo_ngan_hang_xanh/internal_policy.md").read_text(encoding="utf-8")
drafted = draft(policy, "ngan_hang_xanh_nhap", "Ngân hàng TMCP Xanh Demo (bản nháp tự soạn)", "bank")
OUT["draft"] = {"method": drafted["method"], "errors": drafted["errors"], "notes": drafted["notes"],
                "rules": [{"rule_id": r["rule_id"], "clause": r["source_clauses"][0], "check": r["conditions"][0]["check"],
                           "attribute": r["conditions"][0].get("attribute"),
                           "terms": r["conditions"][0].get("any_of_terms"), "when": bool(r.get("when")),
                           "severity": r["severity"], "title": r["title"]} for r in drafted["pack"]["rules"]]}
folder = Path("configs/org_packs/demo_ngan_hang_xanh")
upload = org_registry.ingest([(f.name, f.read_bytes()) for f in folder.iterdir() if f.is_file()], "Lan (Khối Rủi ro)")
try:
    org_registry.approve(upload["org_id"], upload["version"], "lan (khối rủi ro)")
    same_person = "không bị chặn"
except ValueError as exc:
    same_person = str(exc)
approved = org_registry.approve(upload["org_id"], upload["version"], "Minh (Phòng Tuân thủ)")
OUT["upload"] = {"status": upload["status"], "version": upload["version"], "n_rules": upload["n_rules"],
                 "self_approval_removed": upload["self_approval_removed"], "same_person": same_person,
                 "approved_by": approved["approved_by"], "resolved": org_registry.resolve([upload["org_id"]])}

t = time.perf_counter()
settings_b = load_settings()
settings_b.legal.org_packs = org_registry.resolve([upload["org_id"]])
settings_b.feedback.precedents = False
run_b = OrchestratorAgent(settings_b).run(docs("B"))
traced_b = json.loads((Path(".quantum/runs") / json.loads((TRACE / "clean" / "case_B.json").read_text(encoding="utf-8"))["run_id"]
                       / "result.json").read_text(encoding="utf-8"))
findings = [f for r in run_b.org_findings or [] for f in r["findings"]]
OUT["case_b"] = {
    "seconds": round(time.perf_counter() - t, 1),
    "claims": len(run_b.verifications),
    "status_counts": run_b.summary.status_counts,
    "traced_status_counts": traced_b["summary"]["status_counts"],
    "same_verdicts": [v.status.value for v in run_b.verifications] == [v["status"] for v in traced_b["verifications"]],
    "outcomes": dict(Counter(f["outcome"] for f in findings)),
    "by_rule": {rid: dict(Counter(f["outcome"] for f in findings if f["rule_id"] == rid))
                for rid in sorted({f["rule_id"] for f in findings})},
    "titles": {f["rule_id"]: f["title"] for f in findings},
    "on_fail": {f["rule_id"]: f["on_fail"] for f in findings},
    "raised": sum(1 for p in run_b.priorities if any(r.startswith("org_rule:") for r in p.get("raised_by", []))),
    "queued": sum(1 for p in run_b.priorities if p["in_queue"]),
    "traced_queued": sum(1 for p in traced_b["priorities"] if p["in_queue"]),
    "example": next(({"text": v.claim.text, "status": v.status.value,
                      "findings": [{k: f[k] for k in ("rule_id", "outcome", "reason")} for f in r["findings"]
                                   if f["outcome"] in ("VIOLATION", "NEEDS_REVIEW")]}
                     for v, r in zip(run_b.verifications, run_b.org_findings or [])
                     if any(f["rule_id"] == "NHXD_003" and f["outcome"] == "VIOLATION" for f in r["findings"])), None),
}
log(f"Ca B với org pack xong ({OUT['case_b']['seconds']} s): {OUT['case_b']['outcomes']}")

# ------------------------------------------------------------------ 6. Mô hình thách đấu trên 821 cặp Claude + nhãn chỉ chỗ
pairs = dataset.build(store=store)
info = dataset.manifest(pairs)
model = train(pairs)
holdout = [p for p in pairs if p["split"] == "holdout" and p.get("champion")]
folder = TMP / "models" / "hl-thuyet-minh"
model.save(folder)
entry = registry.register(TMP / "models" / "registry.json", folder, champion=champion_metrics(holdout),
                          challenger=challenger_metrics(model, holdout), data=info, trained_by="An (kỹ sư dữ liệu)",
                          kind=KIND)
promotion = None
if entry["gate"]["passed"]:
    promotion = registry.promote(TMP / "models" / "registry.json", entry["model_id"], "Bình (trưởng nhóm)")["status"]
OUT["model"] = {"data": info, "holdout_pairs": len(holdout), "champion": entry["champion"],
                "challenger": entry["challenger"], "gate": entry["gate"], "promotion": promotion,
                "train_relations": model.meta.get("train_relations")}
log(f"Mô hình: gate {entry['gate']['passed']}; F1 luật {entry['champion']['macro_f1']} / mô hình {entry['challenger']['macro_f1']}")

OUT["clean_labels"] = len(clean_labels(store.gold_records(), qa.all()))
(TRACE / "feedback_demo.json").write_text(json.dumps(OUT, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
log(f"Đã ghi {TRACE / 'feedback_demo.json'}")
