"""GS-Claims v1: agreement between two blind labellers, control accuracy, disagreements, merge, extractor P/R.

usage (repo root):
  .venv/Scripts/python.exe -I benchmark/gs_claims_v1/score_labels.py agree     # kappa + controls + disagreements.jsonl
  .venv/Scripts/python.exe -I benchmark/gs_claims_v1/score_labels.py merge     # agreed + adjudication.jsonl -> gold.jsonl
  .venv/Scripts/python.exe -I benchmark/gs_claims_v1/score_labels.py eval      # extractor before (stored runs) / after (current code)
"""
from __future__ import annotations

import json
import math
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIELDS = ["is_claim", "claim_kind", "has_figure", "has_period", "has_baseline", "has_ghg_scope", "has_boundary",
          "cites_independent_source", "promotional_language"]
A, B = "sonnet-A", "sonnet-B"


def jl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def kappa(x: list[str], y: list[str]) -> float | None:
    n = len(x)
    if not n:
        return None
    po = sum(a == b for a, b in zip(x, y)) / n
    cx, cy = Counter(x), Counter(y)
    pe = sum(cx[k] * cy.get(k, 0) for k in cx) / (n * n)
    return None if pe == 1 else round((po - pe) / (1 - pe), 3)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if not n:
        return (0.0, 0.0)
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (round(max(0, c - h), 3), round(min(1, c + h), 3))


def load():
    items = {r["item_id"]: r for r in jl(HERE / "items.jsonl")}
    key = {r["item_id"]: r for r in jl(HERE / "_key" / "key.jsonl")}
    la = {r["item_id"]: r for r in jl(HERE / "labels" / f"labels_{A}.jsonl")}
    lb = {r["item_id"]: r for r in jl(HERE / "labels" / f"labels_{B}.jsonl")}
    return items, key, la, lb


def agree() -> None:
    items, key, la, lb = load()
    report = {"controls": {}, "kappa": {}, "raw_agreement": {}}
    controls = [i for i in key if key[i]["control"]]
    for name, lab in ((A, la), (B, lb)):
        checks = [(i, f, v, lab[i][f]) for i in controls for f, v in key[i]["control"].items()]
        wrong = [c for c in checks if c[2] != c[3]]
        report["controls"][name] = {"fields_checked": len(checks), "correct": len(checks) - len(wrong),
                                    "wrong": [{"item": items[i]["text"][:80], "field": f, "expected": v, "got": g}
                                              for i, f, v, g in wrong]}
    real = [i for i in items if not key[i]["control"]]
    for f in FIELDS:
        x, y = [la[i][f] for i in real], [lb[i][f] for i in real]
        report["kappa"][f] = kappa(x, y)
        report["raw_agreement"][f] = round(sum(a == b for a, b in zip(x, y)) / len(real), 3)
    dis = []
    for i in items:
        diff = {f: {"A": la[i][f], "B": lb[i][f]} for f in FIELDS if la[i][f] != lb[i][f]}
        if diff:
            dis.append({"item_id": i, "text": items[i]["text"], "context": items[i]["context"], "A": {f: la[i][f] for f in FIELDS},
                        "B": {f: lb[i][f] for f in FIELDS}, "differ": sorted(diff), "note_A": la[i].get("note", ""),
                        "note_B": lb[i].get("note", "")})
    with (HERE / "disagreements.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for d in dis:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    report["n_items_with_disagreement"] = len(dis)
    report["n_field_disagreements"] = sum(len(d["differ"]) for d in dis)
    report["by_field"] = dict(Counter(f for d in dis for f in d["differ"]))
    (HERE / "agreement.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))


def merge() -> None:
    items, key, la, lb = load()
    adj = {r["item_id"]: r for r in jl(HERE / "adjudication.jsonl")} if (HERE / "adjudication.jsonl").exists() else {}
    out, unresolved = [], []
    for i in items:
        row = {"item_id": i, "company": items[i]["company"], "text": items[i]["text"], "guide_version": "gs-claims-v1.0",
               "provenance": {"labelers": [A, B], "adjudicator": None, "fields_adjudicated": []},
               "review_status": "pending_human_review"}
        for f in FIELDS:
            if la[i][f] == lb[i][f]:
                row[f] = la[i][f]
            elif i in adj and f in adj[i].get("labels", {}):
                row[f] = adj[i]["labels"][f]
                row["provenance"]["fields_adjudicated"].append(f)
                row["provenance"]["adjudicator"] = adj[i].get("adjudicator")
            else:
                unresolved.append((i, f))
                row[f] = None
        if row["is_claim"] == "no":
            row["claim_kind"] = "na"
        out.append(row)
    with (HERE / "gold.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for r in out:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[merge] {len(out)} items -> gold.jsonl; unresolved fields: {len(unresolved)} {unresolved[:6]}")


def eval_extractor() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
    from quantum_gw.domain.enums import DocumentRole, SourceType
    from quantum_gw.domain.models import EvidenceChunk
    from quantum_gw.settings import load_settings
    from quantum_gw.storage.audit import AuditLogger

    gold = {r["item_id"]: r for r in jl(HERE / "gold.jsonl")}
    key = {r["item_id"]: r for r in jl(HERE / "_key" / "key.jsonl")}
    real = [i for i in gold if not key[i]["control"] and gold[i]["is_claim"] in ("yes", "no")]

    def extracted_now(text: str, fallback: bool) -> bool:
        settings = load_settings(str(ROOT / "configs" / "default.yaml"))
        settings.claim_extraction.fallback_types = fallback
        agent = ClaimExtractionAgent(settings.claim_extraction, AuditLogger(Path(tempfile.mkdtemp()) / "a.jsonl"),
                                     taxonomy_path=str(ROOT / "configs" / "taxonomy.yaml"))
        chunk = EvidenceChunk(chunk_id="c", doc_id="d", source_name="x.txt", role=DocumentRole.CLAIM_SOURCE,
                              source_type=SourceType.INTERNAL, text=text)
        return bool(agent.run([chunk]))

    res = {}
    for name, pred in (
        ("stored_run (pipeline 14/11, in document context)", {i: bool(key[i]["system_extracted"]) for i in real}),
        ("sentence alone, fallback off", {i: extracted_now(gold[i]["text"], False) for i in real}),
        ("sentence alone, fallback on (claim-typing-v2)", {i: extracted_now(gold[i]["text"], True) for i in real}),
    ):
        tp = sum(pred[i] and gold[i]["is_claim"] == "yes" for i in real)
        fp = sum(pred[i] and gold[i]["is_claim"] == "no" for i in real)
        fn = sum((not pred[i]) and gold[i]["is_claim"] == "yes" for i in real)
        res[name] = {"tp": tp, "fp": fp, "fn": fn,
                     "precision": round(tp / (tp + fp), 3) if tp + fp else None, "precision_ci95": wilson(tp, tp + fp),
                     "recall": round(tp / (tp + fn), 3) if tp + fn else None, "recall_ci95": wilson(tp, tp + fn)}
    res["n_items"] = len(real)
    res["note"] = ("Sampling frame: per report 18 sentences the 14/11 pipeline extracted + 17 it did not, among sentences "
                   "with a non-year figure or an environmental word. Recall is within that frame, not over every sentence.")
    (HERE / "extractor_eval.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    {"agree": agree, "merge": merge, "eval": eval_extractor}[sys.argv[1] if len(sys.argv) > 1 else "agree"]()
