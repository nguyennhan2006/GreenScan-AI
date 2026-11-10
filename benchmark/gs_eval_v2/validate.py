"""Deterministic validators for GS-Eval v2 labels (see LABELING_GUIDE.md).

Usage (from repo root):
  .venv/Scripts/python.exe -I benchmark/gs_eval_v2/validate.py explain benchmark/gs_eval_v2/explain/labels/explain_b01.labels.jsonl
  .venv/Scripts/python.exe -I benchmark/gs_eval_v2/validate.py edit    benchmark/gs_eval_v2/edit/labels/edit_b01.labels.jsonl
  .venv/Scripts/python.exe -I benchmark/gs_eval_v2/validate.py score   benchmark/gs_eval_v2/score/labels_A/score_b01.labels.jsonl
  .venv/Scripts/python.exe -I benchmark/gs_eval_v2/validate.py score-merge A.jsonl B.jsonl --out merged.jsonl --disagree disagree.jsonl
  .venv/Scripts/python.exe -I benchmark/gs_eval_v2/validate.py rules   benchmark/gs_eval_v2/rules
Exit code 1 if any ERROR. WARN lines do not fail.
The input item for each label is found by item_id in the matching batches/ folder.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NUM = re.compile(r"\d+(?:[.,]\d+)*")
VERDICTS = {"SUPPORTED", "PARTIALLY_SUPPORTED", "CONTRADICTED", "UNSUPPORTED", "INSUFFICIENT_EVIDENCE", "NOT_A_CLAIM"}
ATTRS = {"metric", "value", "unit", "period", "baseline", "scope", "methodology", "independent_evidence"}
EVROLES = {"supports", "contradicts", "context", "irrelevant"}
NUMRES = {"match", "mismatch", "not_comparable"}
CONF = {"high", "medium", "low"}
EDIT_KINDS = {"add_scope", "placeholder", "evidence_ref", "soften"}
ISSUES = {"MISSING_PERIOD", "MISSING_BASELINE", "MISSING_SCOPE", "NO_FIGURE", "VAGUE_TERM", "ABSOLUTE_CLAIM",
          "OFFSET_NEUTRALITY", "FUTURE_AS_ACHIEVED", "UNVERIFIED_LABEL_OR_CERT", "NO_EVIDENCE_REF",
          "HIDDEN_TRADEOFF", "IRRELEVANT_CLAIM", "INTENSITY_VS_ABSOLUTE", "ENTITY_SCOPE_AMBIGUOUS", "OTHER"}
COMPONENTS = {"specificity": 12, "quantitative_evidence": 12, "baseline": 8, "period": 8, "scope_boundary": 8,
              "evidence_support": 18, "independent_assurance": 8, "contradiction": 18,
              "vague_or_exaggerated_language": 8}
BANDS = [("low", 0, 24), ("medium", 25, 49), ("high", 50, 74), ("critical", 75, 100)]
OUTCOMES = {"COMPLIANT", "VIOLATION", "NEEDS_REVIEW", "NOT_APPLICABLE"}
CASE_TYPES = {"normal", "edge", "conflict_with_law", "override_attempt", "injection", "draft_rule",
              "expired_rule", "other_sector"}
CHECKS = {"manual", "terms_present", "numeric_threshold", "claim_terms_present", "claim_terms_absent",
          "claim_attribute_present", "evidence_independent"}
CLAIM_CHECKS = {"claim_terms_present", "claim_terms_absent", "claim_attribute_present"}
ON_FAIL = {"flag_for_review", "raise_priority"}
SEVERITY = {"info", "warning", "violation"}


class Report:
    def __init__(self) -> None:
        self.errors = 0
        self.warns = 0

    def err(self, where: str, msg: str) -> None:
        self.errors += 1
        print(f"ERROR {where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warns += 1
        print(f"WARN  {where}: {msg}")


def nums(text: str) -> set[str]:
    return {n.rstrip(".,") for n in NUM.findall(text or "")}


def ws(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "")).strip().casefold()


def read_jsonl(path: Path, rep: Report) -> list[dict]:
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            rep.err(f"{path.name}:{i}", f"invalid JSON ({e})")
    return rows


def load_items(kind: str) -> dict[str, dict]:
    items = {}
    for f in sorted((HERE / kind / "batches").glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                it = json.loads(line)
                items[it["item_id"]] = it
    return items


def common(lab: dict, where: str, rep: Report) -> None:
    for k in ("item_id", "labeler", "guide_version", "review_status"):
        if not lab.get(k):
            rep.err(where, f"missing '{k}'")
    if lab.get("review_status") not in (None, "pending_human_review", "human_reviewed", "human_corrected"):
        rep.err(where, "review_status must be pending_human_review | human_reviewed | human_corrected")


def v_explain(path: Path) -> Report:
    rep, items = Report(), load_items("explain")
    seen = set()
    for lab in read_jsonl(path, rep):
        iid = lab.get("item_id", "?")
        where = f"{path.name}:{iid}"
        common(lab, where, rep)
        if iid in seen:
            rep.err(where, "duplicate item_id")
        seen.add(iid)
        it = items.get(iid)
        if it is None:
            rep.err(where, "item_id not in explain batches")
            continue
        if lab.get("ref_verdict") not in VERDICTS:
            rep.err(where, f"ref_verdict not in {sorted(VERDICTS)}")
        if lab.get("verdict_confidence") not in CONF:
            rep.err(where, "verdict_confidence must be high|medium|low")
        for a in lab.get("missing_attributes", []):
            if a not in ATTRS:
                rep.err(where, f"unknown missing_attribute '{a}'")
        chunk_text = {e["chunk_id"]: ws(e.get("text", "")) for e in it.get("evidence", [])}
        for e in lab.get("evidence_used", []):
            if e.get("chunk_id") not in chunk_text:
                rep.err(where, f"evidence_used chunk_id {e.get('chunk_id')} not in item evidence")
                continue
            if e.get("role") not in EVROLES:
                rep.err(where, f"evidence role must be one of {sorted(EVROLES)}")
            q = ws(e.get("quote", "")).rstrip(" ….")
            if q and q not in chunk_text[e["chunk_id"]]:
                rep.warn(where, f"quote not verbatim in {e['chunk_id']}: {q[:60]}")
        for n in lab.get("numbers_checked", []):
            if n.get("result") not in NUMRES:
                rep.err(where, f"numbers_checked.result must be {sorted(NUMRES)}")
        allowed = nums(it["claim"]["text"]) | set().union(*[nums(e.get("text", "")) for e in it.get("evidence", [])] or [set()])
        for fld in ("explanation_plain", "explanation_expert"):
            txt = lab.get(fld) or ""
            if not txt.strip():
                rep.err(where, f"empty {fld}")
            new = nums(txt) - allowed
            if new:
                rep.err(where, f"{fld} contains numbers absent from claim/evidence: {sorted(new)[:5]}")
        if len(re.findall(r"[.!?](\s|$)", lab.get("explanation_plain") or "")) > 3:
            rep.warn(where, "explanation_plain longer than 3 sentences")
        if not (2 <= len(lab.get("must_mention", [])) <= 5):
            rep.err(where, "must_mention needs 2-5 items")
        if not (1 <= len(lab.get("must_not_say", [])) <= 3):
            rep.err(where, "must_not_say needs 1-3 items")
    return rep


def v_edit(path: Path) -> Report:
    rep, items = Report(), load_items("edit")
    seen = set()
    for lab in read_jsonl(path, rep):
        iid = lab.get("item_id", "?")
        where = f"{path.name}:{iid}"
        common(lab, where, rep)
        if iid in seen:
            rep.err(where, "duplicate item_id")
        seen.add(iid)
        it = items.get(iid)
        if it is None:
            rep.err(where, "item_id not in edit batches")
            continue
        claim = it["claim"]["text"]
        allowed = nums(claim) | {str(e.get("page")) for e in it.get("evidence", []) if e.get("page") is not None}
        if not isinstance(lab.get("is_green_claim"), bool) or not isinstance(lab.get("needs_edit"), bool):
            rep.err(where, "is_green_claim and needs_edit must be booleans")
        for x in lab.get("issues", []):
            if x.get("code") not in ISSUES:
                rep.err(where, f"unknown issue code '{x.get('code')}'")
            if x.get("span") and ws(x["span"]) not in ws(claim):
                rep.warn(where, f"issue span not verbatim: {x['span'][:50]}")
        edits = lab.get("edits", [])
        if lab.get("needs_edit") is False and edits:
            rep.err(where, "needs_edit=false but edits given")
        if lab.get("needs_edit") is True and not edits:
            rep.err(where, "needs_edit=true but no edits")
        for e in edits:
            if e.get("kind") not in EDIT_KINDS:
                rep.err(where, f"edit kind must be one of {sorted(EDIT_KINDS)}")
            span = e.get("target_span", "")
            if span and ws(span) not in ws(claim):
                rep.err(where, f"target_span not a substring of the claim: {span[:50]}")
            new = nums(e.get("replacement", "")) - allowed
            if new:
                rep.err(where, f"replacement invents numbers {sorted(new)}")
            if e.get("rule_code") and e["rule_code"] not in ISSUES:
                rep.err(where, f"rule_code '{e['rule_code']}' not an issue code")
        rw = lab.get("rewritten_claim") or ""
        if lab.get("needs_edit") and not rw.strip():
            rep.err(where, "rewritten_claim empty")
        new = nums(rw) - allowed
        if new:
            rep.err(where, f"rewritten_claim invents numbers {sorted(new)}")
        if lab.get("priority") not in ("high", "medium", "low"):
            rep.err(where, "priority must be high|medium|low")
    return rep


def band_of(score: float) -> str:
    s = round(score)
    for name, lo, hi in BANDS:
        if lo <= s <= hi:
            return name
    return "critical"


def v_score(path: Path, write_back: bool = True) -> Report:
    rep, items = Report(), load_items("score")
    rows = read_jsonl(path, rep)
    seen = set()
    for lab in rows:
        iid = lab.get("item_id", "?")
        where = f"{path.name}:{iid}"
        common(lab, where, rep)
        if iid in seen:
            rep.err(where, "duplicate item_id")
        seen.add(iid)
        if iid not in items:
            rep.err(where, "item_id not in score batches")
        comps = lab.get("components") or {}
        total = 0.0
        for name, mx in COMPONENTS.items():
            c = comps.get(name)
            if not isinstance(c, dict):
                rep.err(where, f"missing component {name}")
                continue
            lv = c.get("level")
            if lv not in (0, 1, 2, 3):
                rep.err(where, f"{name}.level must be 0..3")
                continue
            if not isinstance(c.get("applicable", True), bool):
                rep.err(where, f"{name}.applicable must be boolean")
            total += lv / 3 * mx
        extra = set(comps) - set(COMPONENTS)
        if extra:
            rep.err(where, f"unknown components {sorted(extra)}")
        lab["rubric_score"] = round(total, 1)
        lab["rubric_band"] = band_of(total)
        if lab.get("holistic_band") not in {b[0] for b in BANDS}:
            rep.err(where, "holistic_band must be low|medium|high|critical")
        if lab.get("holistic_verdict") not in VERDICTS:
            rep.err(where, "holistic_verdict invalid")
        if lab.get("confidence") not in CONF:
            rep.err(where, "confidence must be high|medium|low")
    if write_back and rep.errors == 0:
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return rep


def qwk(a: list[int], b: list[int], k: int = 4) -> float | None:
    n = len(a)
    if n == 0:
        return None
    obs = [[0] * k for _ in range(k)]
    for x, y in zip(a, b):
        obs[x][y] += 1
    ha = [sum(r) for r in obs]
    hb = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    num = den = 0.0
    for i in range(k):
        for j in range(k):
            w = (i - j) ** 2 / (k - 1) ** 2
            num += w * obs[i][j]
            den += w * ha[i] * hb[j] / n
    return None if den == 0 else round(1 - num / den, 3)


def score_merge(a_path: Path, b_path: Path, out: Path, dis: Path) -> Report:
    rep = Report()
    A = {r["item_id"]: r for r in read_jsonl(a_path, rep)}
    B = {r["item_id"]: r for r in read_jsonl(b_path, rep)}
    merged, disagreements, stats = [], [], {}
    order = [b[0] for b in BANDS]
    for iid in sorted(set(A) & set(B)):
        a, b = A[iid], B[iid]
        m = {"item_id": iid, "components": {}, "needs_adjudication": []}
        for name in COMPONENTS:
            la, lb = a["components"][name]["level"], b["components"][name]["level"]
            stats.setdefault(name, ([], []))
            stats[name][0].append(la)
            stats[name][1].append(lb)
            app_a = a["components"][name].get("applicable", True)
            app_b = b["components"][name].get("applicable", True)
            m["components"][name] = {"level_a": la, "level_b": lb, "level_mean": (la + lb) / 2,
                                     "applicable_a": app_a, "applicable_b": app_b}
            if abs(la - lb) >= 2 or app_a != app_b:
                m["needs_adjudication"].append(name)
        ba, bb = order.index(a["holistic_band"]), order.index(b["holistic_band"])
        m["holistic_band_a"], m["holistic_band_b"] = a["holistic_band"], b["holistic_band"]
        m["holistic_verdict_a"], m["holistic_verdict_b"] = a["holistic_verdict"], b["holistic_verdict"]
        if abs(ba - bb) >= 2:
            m["needs_adjudication"].append("holistic_band")
        if a["holistic_verdict"] != b["holistic_verdict"]:
            m["needs_adjudication"].append("holistic_verdict")
        merged.append(m)
        if m["needs_adjudication"]:
            disagreements.append({"item_id": iid, "fields": m["needs_adjudication"], "pass_a": a, "pass_b": b})
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in merged), encoding="utf-8")
    dis.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in disagreements), encoding="utf-8")
    summary = {name: {"n": len(x), "exact": round(sum(p == q for p, q in zip(x, y)) / max(len(x), 1), 3),
                      "within1": round(sum(abs(p - q) <= 1 for p, q in zip(x, y)) / max(len(x), 1), 3),
                      "qwk": qwk(x, y)} for name, (x, y) in stats.items()}
    print(json.dumps({"merged": len(merged), "to_adjudicate": len(disagreements), "agreement": summary},
                     ensure_ascii=False))
    return rep


def v_rules(root: Path) -> Report:
    import yaml  # PyYAML is a project dependency

    rep = Report()
    packs: dict[str, set[str]] = {}
    for pf in sorted((root / "orgs").glob("*/pack.yaml")):
        where = str(pf.relative_to(root))
        try:
            d = yaml.safe_load(pf.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            rep.err(where, f"YAML error {e}")
            continue
        for k in ("kind", "schema_version", "org_id", "org_name", "pack_version", "precedence", "rules"):
            if k not in d:
                rep.err(where, f"missing '{k}'")
        if d.get("kind") != "org_pack" or d.get("precedence") != "below_law":
            rep.err(where, "kind must be org_pack and precedence below_law")
        if not re.fullmatch(r"[a-z0-9_]+", str(d.get("org_id", ""))):
            rep.err(where, "org_id must match [a-z0-9_]+")
        if pf.parent.name != d.get("org_id"):
            rep.err(where, "folder name must equal org_id")
        ids = set()
        doc_ids = {x.get("doc_id") for x in d.get("documents", [])}
        for doc in d.get("documents", []):
            if doc.get("role") != "policy":
                rep.err(where, f"document {doc.get('doc_id')} role must be policy")
            if doc.get("path") and not (pf.parent / doc["path"]).exists():
                rep.err(where, f"document path missing: {doc['path']}")
        for r in d.get("rules", []):
            rid = r.get("rule_id", "?")
            w = f"{where}:{rid}"
            if rid in ids:
                rep.err(w, "duplicate rule_id")
            ids.add(rid)
            for k in ("rule_id", "title", "source_document", "legal_issue", "conditions", "severity", "on_fail",
                      "machine_executable"):
                if k not in r:
                    rep.err(w, f"missing '{k}'")
            if r.get("source_document") not in doc_ids:
                rep.warn(w, "source_document not among pack documents")
            if r.get("severity") not in SEVERITY:
                rep.err(w, f"severity must be {sorted(SEVERITY)}")
            if r.get("on_fail") not in ON_FAIL:
                rep.err(w, f"on_fail must be {sorted(ON_FAIL)} (org rules never change a verdict)")
            if r.get("machine_executable") not in ("full", "partial", "none"):
                rep.err(w, "machine_executable must be full|partial|none")
            for grp in ("when", "conditions"):
                for c in r.get(grp, []) or []:
                    chk = c.get("check")
                    if chk not in CHECKS:
                        rep.err(w, f"{grp}: unknown check '{chk}'")
                    if grp == "when" and chk not in CLAIM_CHECKS:
                        rep.err(w, "when: only claim_* checks allowed")
                    if chk in ("terms_present", "claim_terms_present", "claim_terms_absent") and not c.get("any_of_terms"):
                        rep.err(w, f"{chk} needs any_of_terms")
                    if chk == "claim_attribute_present" and c.get("attribute") not in ("metric", "value", "unit", "period", "baseline", "scope"):
                        rep.err(w, "claim_attribute_present needs attribute metric|value|unit|period|baseline|scope")
                    if chk == "numeric_threshold" and (c.get("operator") not in (">=", "<=", ">", "<") or c.get("threshold") is None):
                        rep.err(w, "numeric_threshold needs operator and threshold")
        packs[d.get("org_id", pf.parent.name)] = ids
    seen = set()
    for cf in sorted(root.glob("cases_*.jsonl")):
        for c in read_jsonl(cf, rep):
            w = f"{cf.name}:{c.get('case_id', '?')}"
            if c.get("case_id") in seen:
                rep.err(w, "duplicate case_id")
            seen.add(c.get("case_id"))
            if c.get("org_id") not in packs:
                rep.err(w, f"org_id {c.get('org_id')} has no pack")
            elif c.get("rule_id") not in packs[c["org_id"]]:
                rep.err(w, f"rule_id {c.get('rule_id')} not in pack {c['org_id']}")
            if c.get("expected_outcome") not in OUTCOMES:
                rep.err(w, f"expected_outcome must be {sorted(OUTCOMES)}")
            if c.get("case_type") not in CASE_TYPES:
                rep.err(w, f"case_type must be {sorted(CASE_TYPES)}")
            if c.get("verdict_must_not_change") is not True:
                rep.err(w, "verdict_must_not_change must be true")
            if not (c.get("claim") or {}).get("text"):
                rep.err(w, "claim.text missing")
    print(json.dumps({"packs": len(packs), "rules": sum(len(v) for v in packs.values()), "cases": len(seen)}))
    return rep


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) < 2:
        print(__doc__)
        return 2
    kind = argv[0]
    if kind == "score-merge":
        out = Path(argv[argv.index("--out") + 1])
        dis = Path(argv[argv.index("--disagree") + 1])
        rep = score_merge(Path(argv[1]), Path(argv[2]), out, dis)
    elif kind == "rules":
        rep = v_rules(Path(argv[1]))
    else:
        fn = {"explain": v_explain, "edit": v_edit, "score": v_score}[kind]
        rep = Report()
        for p in argv[1:]:
            r = fn(Path(p))
            rep.errors += r.errors
            rep.warns += r.warns
    print(f"SUMMARY errors={rep.errors} warns={rep.warns}")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
