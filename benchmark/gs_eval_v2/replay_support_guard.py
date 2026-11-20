"""Offline replay of the support guard (independent_support_v1) on stored runs.

The verdict step (`VerificationAgent._status`) reads only the claim, the stored
passages with their stances and the stored figure comparison, so it can be re-run
on a finished run without reading any document again. For every verification of
the current runs (same selection and text matching as refresh_system_outputs.py)
this script replays the verdict twice:

  off  support_requires_independent_source = false (shipped behaviour)
  on   support_requires_independent_source = true

and reports (1) whether the "off" replay reproduces the stored verdict (it must,
or the replay is not the product), (2) every verdict the flag changes, with the
source type of the passage that confirmed it, and (3) the GS-Eval v2 "decisive"
numbers on the labelled explain sample before and after.

Run:  .venv/Scripts/python.exe benchmark/gs_eval_v2/replay_support_guard.py
Writes benchmark/gs_eval_v2/results/replay_support_guard.json.
This is a replay, not the registered end-to-end rerun (see the block in
configs/measurement_decisions.yaml for the commands of that).
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))
from build_inputs import norm  # noqa: E402

from quantum_gw.agents.verifier import INDEPENDENT_SOURCE_TYPES, VerificationAgent  # noqa: E402
from quantum_gw.domain.models import Claim, RetrievedEvidence  # noqa: E402
from quantum_gw.settings import load_settings  # noqa: E402
from quantum_gw.storage.audit import AuditLogger  # noqa: E402

CURRENT_FROM = os.environ.get("GS_CURRENT_FROM", "2026-11-09")
DECISIVE = {"SUPPORTED", "CONTRADICTED"}


def current_runs() -> list[Path]:
    out = []
    for rdir in sorted((ROOT / ".quantum" / "runs").iterdir()):
        if not (rdir / "result.json").exists() or not (rdir / "manifest.json").exists():
            continue
        m = json.loads((rdir / "manifest.json").read_text(encoding="utf-8"))
        if str(m.get("created_at", "")) >= CURRENT_FROM:
            out.append(rdir)
    return out


def agents():
    base = load_settings(str(ROOT / "configs" / "default.yaml")).verification
    tmp = Path(tempfile.mkdtemp())
    make = lambda guard: VerificationAgent(  # noqa: E731
        base.model_copy(update={"support_requires_independent_source": guard}),
        AuditLogger(tmp / f"audit_{guard}.jsonl"), taxonomy_path=str(ROOT / "configs" / "taxonomy.yaml"))
    return make(False), make(True)


def replay(agent, v: dict) -> str:
    evidence = [RetrievedEvidence.model_validate(e) for e in v.get("evidence") or []]
    if not evidence:
        return v["status"]  # no passage: the verdict step never ran
    return agent._status(Claim.model_validate(v["claim"]), evidence, v.get("computed_values") or {})[0].value


def confirming_source(v: dict) -> str:
    own = v["claim"].get("source_doc_id")
    types = [e.get("source_type") for e in v.get("evidence") or []
             if e.get("relation") == "SUPPORTS" and not (own and e.get("doc_id") == own)]
    return ",".join(sorted(set(t or "?" for t in types))) or "none"


def labelled_explain() -> dict[str, dict]:
    items, labels = {}, {}
    for f in (HERE / "explain" / "batches").glob("*.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                it = json.loads(line)
                items[it["item_id"]] = it
    for f in (HERE / "explain" / "labels").glob("*.labels.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                lab = json.loads(line)
                labels[lab["item_id"]] = lab
    return {i: {"item": items[i], "lab": labels[i]} for i in labels if i in items}


def decisive(rows: list[dict], key: str) -> dict:
    dec = [r for r in rows if r[key] in DECISIVE]
    false_s = [r for r in rows if r[key] == "SUPPORTED" and r["ref"] != "SUPPORTED"]
    return {"n_system_decisive": len(dec),
            "precision_vs_reference": round(sum(r[key] == r["ref"] for r in dec) / len(dec), 3) if dec else None,
            "false_supported": len(false_s),
            "false_supported_ref_breakdown": dict(Counter(r["ref"] for r in false_s)),
            "verdicts": dict(Counter(r[key] for r in rows))}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    off, on = agents()
    index: dict[str, tuple[str, dict, str]] = {}
    for rdir in current_runs():
        d = json.loads((rdir / "result.json").read_text(encoding="utf-8"))
        stamp = d["manifest"].get("created_at", "")
        for v in d.get("verifications", []):
            k = norm(v["claim"].get("text"))
            if k not in index or stamp > index[k][0]:
                index[k] = (stamp, v, rdir.name)

    replayed, mismatch, changes = {}, [], []
    for k, (_, v, run) in index.items():
        a, b = replay(off, v), replay(on, v)
        replayed[k] = (a, b)
        if a != v["status"]:
            mismatch.append({"run": run, "stored": v["status"], "replay_off": a, "text": v["claim"]["text"][:120]})
        if a != b:
            changes.append({"run": run, "from": a, "to": b, "confirming_source": confirming_source(v),
                            "text": v["claim"]["text"][:160]})

    keys = list(index)
    rows = []
    for iid, x in sorted(labelled_explain().items()):
        k = norm(x["item"]["claim"]["text"])
        if k not in index:
            cands = [y for y in keys if (k in y or y in k) and min(len(k), len(y)) / max(len(k), len(y)) >= 0.8]
            if not cands:
                continue
            k = max(cands, key=len)
        a, b = replayed[k]
        rows.append({"item_id": iid, "ref": x["lab"]["ref_verdict"], "off": a, "on": b,
                     "stored": index[k][1]["status"], "confirming_source": confirming_source(index[k][1])})

    out = {
        "what": "offline replay of VerificationAgent._status with support_requires_independent_source off/on",
        "runs_from": CURRENT_FROM, "independent_source_types": sorted(INDEPENDENT_SOURCE_TYPES),
        "pool": {"verifications": len(index), "replay_off_reproduces_stored": len(index) - len(mismatch),
                 "mismatches": mismatch[:20],
                 "verdicts_off": dict(Counter(a for a, _ in replayed.values())),
                 "verdicts_on": dict(Counter(b for _, b in replayed.values())),
                 "changed": len(changes), "changes": changes},
        "explain_labelled": {"n_matched": len(rows), "off": decisive(rows, "off"), "on": decisive(rows, "on"),
                             "supported_cases": [r for r in rows if "SUPPORTED" in (r["off"], r["on"])]},
    }
    path = HERE / "results" / "replay_support_guard.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    p = out["pool"]
    print(f"pool {p['verifications']} verifications; replay(off) reproduces stored: {p['replay_off_reproduces_stored']}")
    print(f"verdicts off {p['verdicts_off']}\nverdicts on  {p['verdicts_on']}\nchanged {p['changed']}")
    for c in changes:
        print(f"  {c['run']} {c['from']} -> {c['to']} [{c['confirming_source']}] {c['text'][:90]}")
    e = out["explain_labelled"]
    print(f"explain labelled matched {e['n_matched']}\n  off {e['off']}\n  on  {e['on']}")
    print(f"-> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
