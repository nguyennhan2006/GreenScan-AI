"""Build the measurement sets of registration llm_stages_v1 from GS-Eval v2 explain (Claude labels, silver).

    .venv/Scripts/python.exe -I -X utf8 benchmark/llm_stages/build_sets.py

Writes benchmark/llm_stages/data/:
  s5_pairs.jsonl     (claim, evidence passage) pairs of the 133 labelled claims; gold = role of the passage
                     (supports -> S, contradicts -> C, context / irrelevant -> O); `rules` = the relation the
                     product gave that passage in the run the item came from (None when the run did not retrieve it)
  s2_attrs.jsonl     the 200 labelled sentences; gold attributes (null = not stated) and is_claim
  s6_explain.jsonl   the items the current code still extracts: the system verdict, rationale and passages
                     (with relations), plus the reference checklist (must_mention / must_not_say)
Labels are Claude's (two passes + adjudication), pending human review: every number from these sets is silver.
"""
from __future__ import annotations

import ast
import glob
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EV2 = ROOT / "benchmark" / "gs_eval_v2"
OUT = Path(__file__).resolve().parent / "data"
RUNS = ROOT / ".quantum" / "runs"
ROLE = {"supports": "S", "contradicts": "C", "context": "O", "irrelevant": "O"}
ATTRS = ("metric", "value", "period", "baseline", "scope")


def lit(v):
    if v is None or isinstance(v, (list, dict)):
        return v
    try:
        return ast.literal_eval(v)
    except (ValueError, SyntaxError):
        return v


def rows(pattern: str) -> dict[str, dict]:
    out = {}
    for f in sorted(glob.glob(str(pattern))):
        for line in open(f, encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
                out[d["item_id"]] = d
    return out


_run_cache: dict[str, dict] = {}


def verification(run_id: str | None, claim_text: str) -> dict | None:
    if not run_id:
        return None
    if run_id not in _run_cache:
        p = RUNS / run_id / "result.json"
        _run_cache[run_id] = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    for v in _run_cache[run_id].get("verifications", []):
        if v["claim"]["text"].strip() == claim_text.strip():
            return v
    return None


def main() -> None:
    items = rows(EV2 / "explain" / "batches" / "*.jsonl")
    labs = rows(EV2 / "explain" / "labels" / "*.jsonl")
    sysout = {}
    for line in open(EV2 / "inputs" / "system_outputs_current.jsonl", encoding="utf-8"):
        d = json.loads(line)
        sysout[d["item_id"]] = d
    OUT.mkdir(exist_ok=True)
    s5, s2, s6 = [], [], []
    for iid, lab in sorted(labs.items()):
        it = items[iid]
        claim = lit(it["claim"])
        evidence = lit(it["evidence"]) or []
        so = sysout.get(iid, {})
        ver = verification(so.get("run_id"), claim["text"]) if so.get("match") not in (None, "not_extracted") else None
        by_chunk = {e["chunk_id"]: e for e in (ver or {}).get("evidence", [])}
        attrs = lit(lab.get("claim_attributes")) or {}
        s2.append({"id": iid, "company": it["company"], "sentence": claim["text"],
                   "is_claim": lab["ref_verdict"] != "NOT_A_CLAIM",
                   "gold": {a: attrs.get(a) for a in ATTRS},
                   "gold_missing": [a for a in lit(lab.get("missing_attributes")) or [] if a in ATTRS],
                   "rules_attrs": lit(so.get("claim_attrs")) if so.get("claim_attrs") else None,
                   "rules_rationale": so.get("system_rationale")})
        if lab["ref_verdict"] != "NOT_A_CLAIM":
            chunks = {e["chunk_id"]: e for e in evidence}
            for e in lit(lab.get("evidence_used")) or []:
                ch = chunks.get(e["chunk_id"])
                if not ch:
                    continue
                prod = by_chunk.get(e["chunk_id"])
                s5.append({"id": f"{iid}:{e['chunk_id']}", "item_id": iid, "company": it["company"],
                           "claim": claim["text"], "evidence": ch["text"], "source_type": ch.get("source_type"),
                           "gold": ROLE.get(e["role"], "O"), "gold_role": e["role"],
                           "rules": prod.get("relation") if prod else None,
                           "rules_method": prod.get("relation_method") if prod else None})
        if ver is not None:
            s6.append({"id": iid, "company": it["company"], "claim": claim["text"],
                       "verdict": ver["status"], "rationale": ver["rationale"],
                       "evidence": [{k: e.get(k) for k in ("source_name", "page", "text", "relation")}
                                    for e in ver.get("evidence", [])],
                       "missing": [a for a in ATTRS if not (ver["claim"].get(a) or (a == "value" and ver["claim"].get("values")))],
                       "system_rationale": so.get("system_rationale"),
                       "ref_verdict": lab["ref_verdict"],
                       "must_mention": lit(lab.get("must_mention")) or [],
                       "must_not_say": lit(lab.get("must_not_say")) or [],
                       "explanation_ref": lab.get("explanation_plain")})
    for name, data in (("s5_pairs", s5), ("s2_attrs", s2), ("s6_explain", s6)):
        with open(OUT / f"{name}.jsonl", "w", encoding="utf-8") as fh:
            for r in data:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("s5", len(s5), dict(Counter(r["gold"] for r in s5)), "rules known", sum(r["rules"] is not None for r in s5),
          dict(Counter(r["rules"] for r in s5)))
    print("s2", len(s2), "claims", sum(r["is_claim"] for r in s2), "with rules attrs", sum(r["rules_attrs"] is not None for r in s2))
    print("s6", len(s6), dict(Counter(r["verdict"] for r in s6)))
    print("companies", dict(Counter(r["company"] for r in s2)))


if __name__ == "__main__":
    main()
