"""Offline replay of the three stage-plan rules (14/11/2026) on stored real runs.

The verification step reads only the claim and its retrieved passages, so it can be
re-run on finished runs without reading a document again. Every verification of the
current runs (same selection as replay_support_guard.py) plus the Hòa Phát seed run
is replayed under five configurations:

  pre          everything new off (comparison-policy-v3 stays: it has no switch)
  base         + figure-consistency-v1 (the three other rules off)
  share        + absolute-share-v1
  conflict     + stance-cues-v3 rule layer (absolute vs partial cue)
  internal     + internal-inconsistency-v1 in "flag" mode
  contradict   internal-inconsistency-v1 in "contradict" mode

and reports, per configuration: verdict counts, review flags, every verdict that
differs from `base` (with the reason, for reading by hand), and the GS-Eval v2
"decisive" numbers on the labelled explain sample. `stored_vs_base` counts verdicts
the base replay does not reproduce (comparison-policy-v3 and code drift since the run).

Run:  .venv/Scripts/python.exe -I benchmark/gs_eval_v2/replay_stage_rules.py
Writes benchmark/gs_eval_v2/results/replay_stage_rules.json.
"""
from __future__ import annotations

import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))
from build_inputs import norm  # noqa: E402
from replay_support_guard import current_runs, decisive, labelled_explain  # noqa: E402

from quantum_gw.agents.verifier import VerificationAgent  # noqa: E402
from quantum_gw.domain.models import Claim, RetrievedEvidence  # noqa: E402
from quantum_gw.settings import load_settings  # noqa: E402
from quantum_gw.storage.audit import AuditLogger  # noqa: E402

CONFIGS = {
    "pre": {"figure_consistency_check": False, "absolute_share_check": False, "absolute_conflict_cues": False, "internal_inconsistency": "off"},
    "base": {"absolute_share_check": False, "absolute_conflict_cues": False, "internal_inconsistency": "off"},
    "share": {"absolute_share_check": True, "absolute_conflict_cues": False, "internal_inconsistency": "off"},
    "conflict": {"absolute_share_check": True, "absolute_conflict_cues": True, "internal_inconsistency": "off"},
    "internal": {"absolute_share_check": True, "absolute_conflict_cues": True, "internal_inconsistency": "flag"},
    "contradict": {"absolute_share_check": True, "absolute_conflict_cues": True, "internal_inconsistency": "contradict"},
}
EXTRA_RUNS = ("409344b041b64787",)  # Hòa Phát seed run, 14/11 (Ca B)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    base = load_settings(str(ROOT / "configs" / "default.yaml")).verification
    tmp = Path(tempfile.mkdtemp())
    agents = {name: VerificationAgent(base.model_copy(update=upd), AuditLogger(tmp / f"{name}.jsonl"),
                                      taxonomy_path=str(ROOT / "configs" / "taxonomy.yaml"))
              for name, upd in CONFIGS.items()}

    runs = current_runs() + [ROOT / ".quantum" / "runs" / r for r in EXTRA_RUNS
                             if (ROOT / ".quantum" / "runs" / r / "result.json").exists()]
    index: dict[str, tuple[str, dict, str]] = {}
    for rdir in dict.fromkeys(runs):
        d = json.loads((rdir / "result.json").read_text(encoding="utf-8"))
        stamp = d["manifest"].get("created_at", "")
        for v in d.get("verifications", []):
            k = norm(v["claim"].get("text"))
            if k not in index or stamp > index[k][0]:
                index[k] = (stamp, v, rdir.name)

    replayed: dict[str, dict[str, tuple[str, list, str]]] = {}
    for k, (_, v, run) in index.items():
        evidence = [e for e in v.get("evidence") or []]
        out = {}
        for name, agent in agents.items():
            if not evidence:
                out[name] = (v["status"], [], "")
                continue
            r = agent.run(Claim.model_validate(v["claim"]), [RetrievedEvidence.model_validate(e) for e in evidence])
            out[name] = (r.status.value, list(r.review_flags), r.rationale)
        replayed[k] = out

    report = {"n_verifications": len(index), "n_runs": len(set(x[2] for x in index.values())),
              "stored_vs_pre": sum(1 for k, (_, v, _) in index.items() if replayed[k]["pre"][0] != v["status"]),
              "configs": {}}
    seed = {k for k, (_, _, run) in index.items() if run in EXTRA_RUNS}
    labelled = labelled_explain()
    keys = list(index)
    for name in CONFIGS:
        changes = []
        for k, out in replayed.items():
            if out[name][:2] != out["pre"][:2]:
                changes.append({"run": index[k][2], "from": out["pre"][0], "to": out[name][0], "flags": out[name][1],
                                "text": index[k][1]["claim"]["text"][:200], "reason": out[name][2][:400]})
        rows = []
        for iid, x in sorted(labelled.items()):
            k = norm(x["item"]["claim"]["text"])
            if k not in index:
                cands = [y for y in keys if (k in y or y in k) and min(len(k), len(y)) / max(len(k), len(y)) >= 0.8]
                if not cands:
                    continue
                k = max(cands, key=len)
            rows.append({"item_id": iid, "ref": x["lab"]["ref_verdict"], name: replayed[k][name][0]})
        false_c = [r for r in rows if r[name] == "CONTRADICTED" and r["ref"] != "CONTRADICTED"]
        report["configs"][name] = {
            "verdicts": dict(Counter(out[name][0] for out in replayed.values())),
            "flags": dict(Counter(f for out in replayed.values() for f in out[name][1])),
            "hpg_seed": {"verdicts": dict(Counter(replayed[k][name][0] for k in seed)),
                         "flags": dict(Counter(f for k in seed for f in replayed[k][name][1]))},
            "changed_vs_pre": len(changes),
            "changes": changes[:80],
            "gs_eval_v2_explain": {**decisive(rows, name), "n_rows": len(rows), "false_contradicted": len(false_c)},
        }
        c = report["configs"][name]
        print(f"[{name}] changed {c['changed_vs_pre']}, flags {c['flags']}, HPG {c['hpg_seed']}, "
              f"GS-Eval decisive {c['gs_eval_v2_explain']['n_system_decisive']} "
              f"prec {c['gs_eval_v2_explain']['precision_vs_reference']} falseC {c['gs_eval_v2_explain']['false_contradicted']}",
              flush=True)
    out = HERE / "results" / "replay_stage_rules.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[replay] {report['n_verifications']} verifications from {report['n_runs']} runs; "
          f"stored_vs_pre {report['stored_vs_pre']}; wrote {out}")


if __name__ == "__main__":
    main()
