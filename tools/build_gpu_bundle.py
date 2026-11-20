"""Fill deploy/vastai_a100/data/ with every input the training scripts need (Kaggle T4 and a rented A100).

    .venv/Scripts/python.exe -X utf8 tools/build_gpu_bundle.py

Only public-report text and labels go in; no credential, no user document. The same folder is uploaded to a
vast.ai machine (scp) and, as a private dataset, to Kaggle. Writes data/manifest.json (counts + md5).

Files
  t1_train.jsonl      T1 sentences, Claude labels; Q13 v1.2 relabel applied when q13_relabel_v1.2.jsonl exists
  s1_eval.jsonl       the 200 GS-Eval v2 sentences (registered S1 test), with is_claim and extracted
  pairs_pool.jsonl    821 (claim, passage) pairs; pairs_labels.jsonl when training/data/claude/pairs/labels.jsonl exists
  rankings.jsonl      top-10 of each retrieval system per claim (reranker baseline)
  s5_pairs.jsonl      391 GS-Eval pairs (registered stance test, S / C / O)
  explain_train.jsonl explanation inputs from stored product runs, GS-Eval S6 claims removed (distillation)
  s6_explain.jsonl    142 registered S6 items with must_mention
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from quantum_gw.assist.prompts import explain_messages, stance_messages  # noqa: E402

DEST = ROOT / "deploy" / "vastai_a100" / "data"
PAIRS = ROOT / "training" / "data" / "claude" / "pairs"
STAGES = ROOT / "benchmark" / "llm_stages"
RUNS = ROOT / ".quantum" / "runs"
ATTRS = ("metric", "value", "period", "baseline", "scope")
SMALL, LARGE = "Qwen/Qwen3-4B-Instruct-2507", "Qwen/Qwen3-32B-AWQ"
LARGE_STANCE = "openai/gpt-oss-120b"   # any name of the large family: stance-v3 prompt
HPG_RUN = "583ee2e6e6c94501"


def jl(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.open(encoding="utf-8") if x.strip()] if p.exists() else []


def wjl(name: str, rows: list[dict]) -> None:
    (DEST / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def norm60(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower()).strip()[:60]


def t1() -> dict:
    rows = jl(ROOT / "training/data/kaggle/data/train.jsonl")
    relabel = {r["id"]: r for r in jl(ROOT / "training/data/claude/q13/q13_relabel_v1.2.jsonl")}
    out, changed = [], Counter()
    for r in rows:
        new = relabel.get(r["id"])
        label = new["label"] if new else r["label"]
        if new and label != r["label"]:
            changed[label] += 1
        out.append({"id": r["id"], "company_id": r["company_id"], "text": r["text"], "text_masked": r["text_masked"],
                    "label": label, "label_v11": r["label"], "q13_relabelled": bool(new)})
    wjl("t1_train.jsonl", out)
    s2 = {r["id"]: r for r in jl(STAGES / "data/s2_attrs.jsonl")}
    ev = []
    for r in jl(STAGES / "kaggle/inputs/s1_eval.jsonl"):
        a = s2.get(r["id"], {})
        ev.append({**r, "is_claim": a.get("is_claim"), "extracted": a.get("rules_attrs") is not None})
    wjl("s1_eval.jsonl", ev)
    return {"t1_train": len(out), "q13_relabel_rows": len(relabel), "q13_changed_to": dict(changed),
            "labels": dict(Counter(r["label"] for r in out)), "s1_eval": len(ev),
            "s1_extracted": {f"is_claim={k}": v for k, v in Counter(r["is_claim"] for r in ev if r["extracted"]).items()}}


def pairs(held: set[str]) -> dict:
    pool = jl(PAIRS / "pool.jsonl")
    keep = ("id", "origin", "claim_id", "company_id", "claim_label", "claim", "prev", "next", "passage",
            "claim_source", "passage_source", "chunk_id", "systems")
    rows = [{**{k: p.get(k) for k in keep}, "overlaps_gs_eval": norm60(p["claim"]) in held} for p in pool]
    wjl("pairs_pool.jsonl", rows)
    for name in ("rules", "nli-mdeberta"):   # baselines on the same pairs (claude_pairs.py candidates)
        shutil.copy(PAIRS / "candidates" / f"{name}.jsonl", DEST / f"pairs_cand_{name}.jsonl")
    labels = jl(PAIRS / "labels.jsonl")
    if labels:
        wjl("pairs_labels.jsonl", labels)
        by = {r["id"]: r for r in rows}
        sft = []
        for x in labels:   # generative stance SFT for the A100 (product prompt stance-v3, answer {"relation", "reason"})
            p = by.get(x["id"])
            if p and not p["overlaps_gs_eval"] and x.get("decided_by") != "contested":
                sft.append({"id": x["id"], "company": p["company_id"],
                            "messages": stance_messages(LARGE_STANCE, p["claim"], p["passage"]),
                            "target": json.dumps({"relation": x["relation"], "reason": x.get("note") or ""},
                                                 ensure_ascii=False)})
        wjl("stance_sft.jsonl", sft)
    shutil.copy(PAIRS / "rankings.jsonl", DEST / "rankings.jsonl")
    return {"pool": len(rows), "pool_overlapping_gs_eval": sum(r["overlaps_gs_eval"] for r in rows),
            "labels": len(labels), "relations": dict(Counter(x["relation"] for x in labels))}


def missing(claim: dict) -> list[str]:
    return [a for a in ATTRS if not (claim.get(a) or (a == "value" and claim.get("values")))]


def msgs(model: str, claim: str, verdict: str, rationale: str, evidence: list[dict], miss: list[str]) -> list[dict]:
    return explain_messages(model, claim, verdict, rationale, evidence, miss)


def explain() -> dict:
    s6 = jl(STAGES / "data/s6_explain.jsonl")
    held = {x["claim"].strip() for x in s6}
    run_ids = {json.loads(x).get("run_id") for x in open(ROOT / "benchmark/gs_eval_v2/inputs/system_outputs_current.jsonl",
                                                          encoding="utf-8")} - {None}
    out, seen = [], set()
    for rid in sorted(run_ids) + [HPG_RUN]:
        p = RUNS / rid / "result.json"
        if not p.exists():
            continue
        res = json.loads(p.read_text(encoding="utf-8"))
        company = (res.get("company") or {}).get("name") if isinstance(res.get("company"), dict) else res.get("company")
        for v in res.get("verifications", []):
            text = v["claim"]["text"].strip()
            if text in held or text in seen or not v.get("evidence"):
                continue
            seen.add(text)
            ev = [{k: e.get(k) for k in ("source_name", "page", "text", "relation")} for e in v["evidence"]]
            miss = missing(v["claim"])
            out.append({"id": hashlib.sha1(f"{rid}|{text}".encode()).hexdigest()[:16], "run_id": rid,
                        "company": company or rid, "verdict": v["status"],
                        "msgs_large": msgs(LARGE, text, v["status"], v["rationale"], ev, miss),
                        "msgs_small": msgs(SMALL, text, v["status"], v["rationale"], ev, miss)})
    wjl("explain_train.jsonl", out)
    s6_rows = [{**x, "msgs_small": msgs(SMALL, x["claim"], x["verdict"], x["rationale"], x["evidence"], x["missing"]),
                "msgs_large": msgs(LARGE, x["claim"], x["verdict"], x["rationale"], x["evidence"], x["missing"])} for x in s6]
    wjl("s6_explain.jsonl", s6_rows)
    return {"explain_train": len(out), "verdicts": dict(Counter(r["verdict"] for r in out)), "s6": len(s6_rows)}


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    s5 = jl(STAGES / "data/s5_pairs.jsonl")
    wjl("s5_pairs.jsonl", [{**{k: r.get(k) for k in ("id", "item_id", "company", "claim", "evidence", "gold", "gold_role",
                                                      "rules")},
                            "msgs_large": stance_messages(LARGE_STANCE, r["claim"], r["evidence"]),
                            "msgs_small": stance_messages(SMALL, r["claim"], r["evidence"])} for r in s5])
    held = {norm60(r["claim"]) for r in s5} | {norm60(r["claim"]) for r in jl(STAGES / "data/s6_explain.jsonl")}
    shutil.copy(ROOT / "src/quantum_gw/assist/guards.py", DEST.parent / "gs_train" / "guards.py")
    manifest = {"t1": t1(), "pairs": pairs(held), "explain": explain(), "s5_pairs": len(s5), "md5": {}}
    for f in sorted(DEST.glob("*.jsonl")):
        manifest["md5"][f.name] = hashlib.md5(f.read_bytes()).hexdigest()
    (DEST / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "md5"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
