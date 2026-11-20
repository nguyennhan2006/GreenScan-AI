"""Run GreenScan's own rule-based issue finder and fixer (studio.suggest) on GS-Issue inputs.

    .venv/Scripts/python.exe -I -X utf8 benchmark/gs_issue/run_rules.py

Same path as benchmark/gs_eval_v2/evaluate.py for D-EDIT pool B: the product's rule-based extractor describes the claim,
studio.document._missing_attributes lists the missing slots, studio.suggest proposes edits. Rule codes map to issue
codes as in evaluate.py (CODE_OF_RULE, SLOT_CODE). Every suggestion is applied in turn to get the rewritten claim.
Output: benchmark/gs_issue/out/rules__<input>.jsonl in the worker's format ({id, parsed: {issues, edits, rewritten_claim}}).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "benchmark" / "gs_eval_v2"))
import evaluate as ev  # noqa: E402  (puts src/ on the path)

INPUTS = {"gsi_layer_a": HERE / "data/layer_a.jsonl", "gsi_d_edit": HERE / "data/d_edit.jsonl",
          "gsi_layer_b": HERE / "data/layer_b_all.jsonl"}


def main():
    from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
    from quantum_gw.settings import load_settings
    from quantum_gw.studio.suggest import apply

    class _NoAudit:
        def __getattr__(self, name):
            return lambda *a, **k: None

    extractor = ClaimExtractionAgent(load_settings(str(ROOT / "configs/default.yaml")).claim_extraction, _NoAudit())
    out_dir = HERE / "out"
    out_dir.mkdir(exist_ok=True)
    for stem, path in INPUTS.items():
        rows = [json.loads(line) for line in open(path, encoding="utf-8")]
        with open(out_dir / f"rules__{stem}.jsonl", "w", encoding="utf-8") as fh:
            for r in rows:
                item = {"item_id": r["id"], "claim": {"text": r["claim"]}}
                sugg = ev.product_suggestions(item, None, extractor)
                issues, edits, text = [], [], r["claim"]
                for s in sugg:
                    codes = []
                    if s.rule_code == "SC-01":
                        codes = [c for slot, c in ev.SLOT_CODE.items() if slot in s.replacement]
                    elif ev.CODE_OF_RULE.get(s.rule_code):
                        codes = [ev.CODE_OF_RULE[s.rule_code]]
                    for c in codes:
                        issues.append({"code": c, "span": s.target or ""})
                    edits.append({"kind": s.kind, "rule_code": s.rule_code, "target_span": s.target, "replacement": s.replacement})
                    text = apply(text, s) or text
                parsed = {"is_green_claim": True, "issues": issues, "edits": edits, "rewritten_claim": text}
                fh.write(json.dumps({"id": r["id"], "parsed": parsed}, ensure_ascii=False) + "\n")
        print(stem, len(rows), "->", out_dir / f"rules__{stem}.jsonl")


if __name__ == "__main__":
    main()
