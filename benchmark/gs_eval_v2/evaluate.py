"""Evaluate the current GreenScan system on GS-Eval v2 (deterministic; no model calls).

Run from the repo root:
  .venv/Scripts/python.exe -I benchmark/gs_eval_v2/evaluate.py
Writes benchmark/gs_eval_v2/results/eval_results.json and EVAL_REPORT.md.

Sets:
  explain  system verdict / missing attributes / rationale vs reference labels (pool-A items)
  score    system 9-component risk vs two blind passes + adjudication; inter-pass agreement
  edit     Studio rule-based suggestions (src/quantum_gw/studio/suggest.py) vs reference edits
  rules    org-pack engine (src/quantum_gw/legal/org_pack.py) vs expected outcomes of rule cases
  ux       UX lint (usability/ux_lint_spec.md, computable subset) on real run outputs + bad-pack fixtures
Labels are Claude-made per LABELING_GUIDE.md and reviewed by the author; system outputs come from
offline runs (.quantum/runs/*). Population estimates re-weight the system-verdict strata.
"""
from __future__ import annotations

import json
import random
import re
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
RNG = random.Random(20261105)
TODAY = date(2026, 11, 5)
ORDER_BANDS = ["low", "medium", "high", "critical"]
COMPONENTS = {"specificity": 12, "quantitative_evidence": 12, "baseline": 8, "period": 8, "scope_boundary": 8,
              "evidence_support": 18, "independent_assurance": 8, "contradiction": 18,
              "vague_or_exaggerated_language": 8}
DECISIVE = {"SUPPORTED", "CONTRADICTED"}


# ---------------------------------------------------------------- helpers
def jl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def items_of(kind: str) -> dict[str, dict]:
    out = {}
    for f in sorted((HERE / kind / "batches").glob("*.jsonl")):
        for r in jl(f):
            out[r["item_id"]] = r
    return out


def labels_of(folder: Path) -> dict[str, dict]:
    out = {}
    for f in sorted(folder.glob("*.labels.jsonl")):
        for r in jl(f):
            out[r["item_id"]] = r
    return out


def prf(tp: int, fp: int, fn: int) -> dict:
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f = 2 * p * r / (p + r) if p and r else (0.0 if (p is not None and r is not None) else None)
    return {"tp": tp, "fp": fp, "fn": fn, "precision": rnd(p), "recall": rnd(r), "f1": rnd(f)}


def rnd(x, k: int = 3):
    return None if x is None else round(float(x), k)


def kappa(a: list, b: list) -> float | None:
    n = len(a)
    if not n:
        return None
    cats = sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[c] * cb[c] for c in cats) / n / n
    return rnd((po - pe) / (1 - pe)) if pe < 1 else None


def qwk(a: list[int], b: list[int], k: int = 4) -> float | None:
    n = len(a)
    if not n:
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
    return None if den == 0 else rnd(1 - num / den)


def spearman(x: list[float], y: list[float]) -> float | None:
    from scipy.stats import spearmanr
    if len(x) < 3:
        return None
    r = spearmanr(x, y).statistic
    return None if r != r else rnd(r)


def wilson(k: int, n: int, z: float = 1.96) -> list:
    if not n:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [rnd(c - h), rnd(c + h)]


def cluster_boot(rows: list[dict], stat, key: str = "company", n: int = 1000) -> list:
    groups = defaultdict(list)
    for r in rows:
        groups[r[key]].append(r)
    names = sorted(groups)
    vals = []
    for _ in range(n):
        sample = [r for _ in names for r in groups[RNG.choice(names)]]
        v = stat(sample)
        if v is not None:
            vals.append(v)
    vals.sort()
    if not vals:
        return [None, None]
    return [rnd(vals[int(0.025 * len(vals))]), rnd(vals[int(0.975 * len(vals)) - 1])]


def fold(s: str) -> str:
    from quantum_gw.utils.text import fold as f
    return f(s or "")


def nums(text: str) -> set[str]:
    return {n.rstrip(".,") for n in re.findall(r"\d+(?:[.,]\d+)*", text or "")}


def pool_weights() -> dict[str, float]:
    """Unique claims per system status in the current-code runs (stratum sizes for re-weighting).

    Items were drawn by the status of the run they came from; re-weighting by the current status is
    an approximation, reported next to the plain sample figure.
    """
    st = HERE / "inputs" / "refresh_stats.json"
    if st.exists():
        return json.loads(st.read_text(encoding="utf-8"))["current_pool_status"]
    return dict(Counter(r["system_status"] for r in jl(HERE / "inputs" / "pool_a.jsonl")))


NOT_EXTRACTED: dict[str, dict] = {}


# ---------------------------------------------------------------- explain
ATTR_FROM_SYS = {"chỉ số cụ thể": "metric", "số liệu": "value", "kỳ báo cáo": "period",
                 "năm gốc để so sánh": "baseline", "phạm vi / ranh giới": "scope"}
STOP = set("của và các cho với trong được là có không một những này đó theo từ về khi đã sẽ nên cần phải hay hoặc như "
           "tuyên bố bằng chứng đoạn nêu rằng thiếu chưa".split())


def sys_missing(rationale: str) -> set[str]:
    m = re.search(r"Tuyên bố thiếu: ([^.]*)\.", rationale or "")
    if not m:
        return set()
    return {ATTR_FROM_SYS[x.strip()] for x in m.group(1).split(",") if x.strip() in ATTR_FROM_SYS}


def mention_covered(phrase: str, text: str) -> bool:
    words = [w for w in re.findall(r"\w+", fold(phrase)) if len(w) >= 3 and w not in {fold(s) for s in STOP}]
    if not words:
        return False
    t = set(re.findall(r"\w+", fold(text)))
    return sum(w in t for w in words) / len(words) >= 0.5


def eval_explain(sysout: dict) -> dict:
    items = items_of("explain")
    labs = labels_of(HERE / "explain" / "labels")
    pool = pool_weights()
    rows = []
    for iid, lab in labs.items():
        so = sysout.get(iid)
        if not so:
            continue
        rows.append({"item_id": iid, "company": items[iid]["company"], "sys": so["system_status"],
                     "ref": lab["ref_verdict"], "conf": lab.get("verdict_confidence"), "lab": lab, "so": so,
                     "item": items[iid]})
    n = len(rows)
    samp = Counter(r["sys"] for r in rows)
    w = {s: pool.get(s, 0) / samp[s] for s in samp}
    gone = [labs[i] for i in labs if i in NOT_EXTRACTED]
    not_extracted = {"n": len(gone), "reference_verdicts": dict(Counter(g["ref_verdict"] for g in gone)),
                     "legacy_status": dict(Counter(NOT_EXTRACTED[g["item_id"]].get("legacy_status") for g in gone))}

    # extraction: reference says the extracted sentence is not a green claim
    nac = [r for r in rows if r["ref"] == "NOT_A_CLAIM"]
    nac_by_sys = {s: f"{sum(r['ref'] == 'NOT_A_CLAIM' for r in rows if r['sys'] == s)}/{samp[s]}" for s in samp}
    nac_pop = sum(w[r["sys"]] for r in nac) / sum(w[r["sys"]] for r in rows)

    claims = [r for r in rows if r["ref"] != "NOT_A_CLAIM"]
    labels = ["SUPPORTED", "PARTIALLY_SUPPORTED", "CONTRADICTED", "UNSUPPORTED", "INSUFFICIENT_EVIDENCE"]
    conf = {s: Counter(r["ref"] for r in rows if r["sys"] == s) for s in sorted(samp)}
    acc = sum(r["sys"] == r["ref"] for r in claims) / len(claims) if claims else None
    acc_pop = (sum(w[r["sys"]] for r in claims if r["sys"] == r["ref"]) / sum(w[r["sys"]] for r in claims)) if claims else None
    per_class = {}
    for c in labels:
        tp = sum(r["sys"] == c and r["ref"] == c for r in claims)
        fp = sum(r["sys"] == c and r["ref"] != c for r in claims)
        fn = sum(r["sys"] != c and r["ref"] == c for r in claims)
        per_class[c] = prf(tp, fp, fn)
    f1s = [v["f1"] for v in per_class.values() if v["f1"] is not None and (v["tp"] + v["fn"]) > 0]
    # dangerous errors (on all rows: a verdict on a non-claim is also an error)
    false_c = [r for r in rows if r["sys"] == "CONTRADICTED" and r["ref"] != "CONTRADICTED"]
    false_s = [r for r in rows if r["sys"] == "SUPPORTED" and r["ref"] not in ("SUPPORTED",)]
    false_c_claims = [r for r in false_c if r["ref"] != "NOT_A_CLAIM"]
    dec = [r for r in rows if r["sys"] in DECISIVE]

    # missing attributes (only on claims the system did not decide and the reference treats as claims)
    attr_stats = {}
    for a in ("metric", "value", "period", "baseline", "scope"):
        tp = fp = fn = 0
        for r in claims:
            s = a in sys_missing(r["so"]["system_rationale"])
            g = a in set(r["lab"].get("missing_attributes", []))
            tp += s and g
            fp += s and not g
            fn += g and not s
        attr_stats[a] = prf(tp, fp, fn)

    # rationale quality proxies
    words = [len((r["so"]["system_rationale"] or "").split()) for r in rows]
    cover = []
    bad_num = 0
    for r in rows:
        rat = r["so"]["system_rationale"] or ""
        mm = r["lab"].get("must_mention", [])
        if mm:
            cover.append(sum(mention_covered(m, rat) for m in mm) / len(mm))
        allowed = nums(r["item"]["claim"]["text"]) | set().union(*[nums(e.get("text", "")) for e in r["item"].get("evidence", [])] or [set()])
        bad_num += bool(nums(rat) - allowed)
    ref_words = [len((r["lab"].get("explanation_plain") or "").split()) for r in rows]

    def acc_stat(sample):
        c = [x for x in sample if x["ref"] != "NOT_A_CLAIM"]
        return sum(x["sys"] == x["ref"] for x in c) / len(c) if c else None

    def nac_stat(sample):
        return sum(x["ref"] == "NOT_A_CLAIM" for x in sample) / len(sample) if sample else None

    return {
        "n_labeled": len(labs), "n_with_current_output": n, "not_extracted_by_current_system": not_extracted,
        "sample_by_system_status": dict(samp), "pool_by_system_status": pool,
        "reference_verdicts": dict(Counter(r["ref"] for r in rows)),
        "reference_confidence": dict(Counter(r["conf"] for r in rows)),
        "extraction_not_a_claim": {"k": len(nac), "n": n, "rate_sample": rnd(len(nac) / n), "wilson95": wilson(len(nac), n),
                                   "rate_population_weighted": rnd(nac_pop), "by_system_status": nac_by_sys,
                                   "company_bootstrap95": cluster_boot(rows, nac_stat)},
        "verdict_on_claims": {"n": len(claims), "accuracy_sample": rnd(acc), "accuracy_population_weighted": rnd(acc_pop),
                              "accuracy_company_bootstrap95": cluster_boot(rows, acc_stat),
                              "cohen_kappa": kappa([r["sys"] for r in claims], [r["ref"] for r in claims]),
                              "macro_f1_present_classes": rnd(sum(f1s) / len(f1s)) if f1s else None,
                              "per_class": per_class},
        "confusion_system_rows_reference_cols": {k: dict(v) for k, v in conf.items()},
        "decisive": {"n_system_decisive": len(dec),
                     "precision_vs_reference": rnd(sum(r["sys"] == r["ref"] for r in dec) / len(dec)) if dec else None,
                     "false_contradicted": len(false_c), "false_contradicted_on_real_claims": len(false_c_claims),
                     "false_contradicted_ref_breakdown": dict(Counter(r["ref"] for r in false_c)),
                     "false_supported": len(false_s), "false_supported_ref_breakdown": dict(Counter(r["ref"] for r in false_s))},
        "missing_attributes_vs_reference": attr_stats,
        "rationale": {"words_mean": rnd(sum(words) / n, 1) if n else None, "words_max": max(words), "over_80_words": sum(x > 80 for x in words),
                      "reference_plain_words_mean": rnd(sum(ref_words) / n, 1),
                      "must_mention_coverage_proxy_mean": rnd(sum(cover) / len(cover)) if cover else None,
                      "share_items_coverage_ge_half": rnd(sum(c >= 0.5 for c in cover) / len(cover)) if cover else None,
                      "rationales_with_ungrounded_numbers": bad_num,
                      "distinct_rationales": len({r["so"]["system_rationale"] for r in rows})},
        "examples_false_contradicted": [{"item_id": r["item_id"], "company": r["company"], "ref": r["ref"],
                                         "claim": r["item"]["claim"]["text"][:160]} for r in false_c[:8]],
    }



def eval_judge() -> dict:
    """Aggregate the rubric judgement of system rationales (explain/judge/judge_output.jsonl)."""
    rows = jl(HERE / "explain" / "judge" / "judge_output.jsonl")
    if not rows:
        return {}
    labs = labels_of(HERE / "explain" / "labels")
    cur = {r["item_id"]: r for r in jl(HERE / "inputs" / "system_outputs_current.jsonl")}
    def agg(rs):
        n = len(rs)
        if not n:
            return {}
        return {"n": n,
                "must_mention_coverage": rnd(sum(r["mm_covered"] for r in rs) / max(1, sum(r["mm_total"] for r in rs))),
                "items_violating_must_not_say": sum(r["mns_violated"] > 0 for r in rs),
                "faithful_share": rnd(sum(bool(r["faithful"]) for r in rs) / n),
                "actionable_share": rnd(sum(bool(r["actionable"]) for r in rs) / n),
                "clarity_mean": rnd(sum(r["clarity"] for r in rs) / n, 2)}
    by_status = defaultdict(list)
    by_ref = defaultdict(list)
    for r in rows:
        by_status[cur.get(r["item_id"], {}).get("system_status", "?")].append(r)
        by_ref[labs.get(r["item_id"], {}).get("ref_verdict", "?")].append(r)
    k = sum(bool(r["faithful"]) for r in rows)
    return {"overall": agg(rows), "faithful_wilson95": wilson(k, len(rows)),
            "by_system_status": {s: agg(v) for s, v in sorted(by_status.items())},
            "by_reference_verdict": {s: agg(v) for s, v in sorted(by_ref.items())},
            "judge": "claude-sonnet-5-5 per explain/judge (rubric: must_mention, must_not_say, faithful, actionable, clarity 1-5)"}

# ---------------------------------------------------------------- score
def consensus(a: dict, b: dict, adj: dict | None) -> dict:
    res = (adj or {}).get("resolved", {})
    comps = {}
    for c in COMPONENTS:
        la, lb = a["components"][c]["level"], b["components"][c]["level"]
        aa, ab = a["components"][c].get("applicable", True), b["components"][c].get("applicable", True)
        lvl, app = (la + lb) / 2, (aa if aa == ab else True)
        r = res.get(c)
        if r is not None:
            v = r.get("value") if isinstance(r, dict) else r
            if isinstance(v, dict):
                lvl = v.get("level", lvl)
                app = v.get("applicable", app)
            elif isinstance(v, bool):
                app = v
            elif isinstance(v, (int, float)):
                lvl = v
        for key in (f"{c}.level", f"{c}.applicable"):
            if key in res:
                v = res[key].get("value") if isinstance(res[key], dict) else res[key]
                if key.endswith("level"):
                    lvl = v
                else:
                    app = v
        comps[c] = {"level": float(lvl), "applicable": bool(app)}
    band = None
    if "holistic_band" in res:
        v = res["holistic_band"]
        band = v.get("value") if isinstance(v, dict) else v
    if band not in ORDER_BANDS:
        ia, ib = ORDER_BANDS.index(a["holistic_band"]), ORDER_BANDS.index(b["holistic_band"])
        band = ORDER_BANDS[-(-(ia + ib) // 2)]
    verdict = None
    if "holistic_verdict" in res:
        v = res["holistic_verdict"]
        verdict = v.get("value") if isinstance(v, dict) else v
    verdict = verdict or (a["holistic_verdict"] if a["holistic_verdict"] == b["holistic_verdict"] else None)
    total = sum(comps[c]["level"] / 3 * m for c, m in COMPONENTS.items())
    return {"components": comps, "band": band, "verdict": verdict, "total": total}


def band_of(score: float) -> str:
    s = round(score)
    return "low" if s <= 24 else "medium" if s <= 49 else "high" if s <= 74 else "critical"


def eval_score(sysout: dict) -> dict:
    items = items_of("score")
    A = labels_of(HERE / "score" / "labels_A")
    Bl = labels_of(HERE / "score" / "labels_B")
    adj = {}
    for f in sorted((HERE / "score").glob("adjudicated_b*.jsonl")):
        for r in jl(f):
            adj[r["item_id"]] = r
    both = sorted(set(A) & set(Bl))
    iaa = {}
    for c in COMPONENTS:
        a = [A[i]["components"][c]["level"] for i in both]
        b = [Bl[i]["components"][c]["level"] for i in both]
        iaa[c] = {"qwk": qwk(a, b), "exact": rnd(sum(x == y for x, y in zip(a, b)) / len(both)) if both else None,
                  "within1": rnd(sum(abs(x - y) <= 1 for x, y in zip(a, b)) / len(both)) if both else None}
    ta = [A[i].get("rubric_score", 0) for i in both]
    tb = [Bl[i].get("rubric_score", 0) for i in both]
    iaa_total = {"spearman": spearman(ta, tb),
                 "holistic_band_qwk": qwk([ORDER_BANDS.index(A[i]["holistic_band"]) for i in both],
                                          [ORDER_BANDS.index(Bl[i]["holistic_band"]) for i in both]),
                 "holistic_verdict_kappa": kappa([A[i]["holistic_verdict"] for i in both], [Bl[i]["holistic_verdict"] for i in both])}

    rows = []
    for i in both:
        so = sysout.get(i)
        if not so or not so.get("risk"):
            continue
        cons = consensus(A[i], Bl[i], adj.get(i))
        sc = {c["name"]: c for c in so["risk"]["components"]}
        rows.append({"item_id": i, "company": items[i]["company"], "cons": cons, "sys": so, "sc": sc})
    comp = {}
    for c, mx in COMPONENTS.items():
        s_lvl = [min(3, round(r["sc"][c]["score"] / r["sc"][c]["max_score"] * 3)) for r in rows if c in r["sc"]]
        g_lvl = [min(3, int(r["cons"]["components"][c]["level"] + 0.5)) for r in rows if c in r["sc"]]
        na = [r for r in rows if c in r["sc"] and not r["cons"]["components"][c]["applicable"]]
        comp[c] = {"n": len(s_lvl), "qwk_system_vs_consensus": qwk(s_lvl, g_lvl),
                   "exact": rnd(sum(x == y for x, y in zip(s_lvl, g_lvl)) / len(s_lvl)) if s_lvl else None,
                   "system_mean_level": rnd(sum(s_lvl) / len(s_lvl), 2) if s_lvl else None,
                   "reference_mean_level": rnd(sum(g_lvl) / len(g_lvl), 2) if g_lvl else None,
                   "not_applicable_by_reference": len(na),
                   "system_penalised_when_not_applicable": sum(r["sc"][c]["score"] > 0 for r in na)}
    sys_t = [r["sys"]["risk"]["risk_score"] for r in rows]
    ref_t = [r["cons"]["total"] for r in rows]
    sys_band = [(r["sys"]["risk"]["severity"] or "").lower() for r in rows]
    ref_band = [r["cons"]["band"] for r in rows]
    ok = [(s, g) for s, g in zip(sys_band, ref_band) if s in ORDER_BANDS and g in ORDER_BANDS]
    return {
        "n_pass_A": len(A), "n_pass_B": len(Bl), "n_both": len(both), "n_adjudicated_items": len(adj),
        "inter_pass_agreement": {"components": iaa, "total": iaa_total},
        "system_vs_consensus": {
            "n": len(rows), "components": comp,
            "total_spearman": spearman(sys_t, ref_t),
            "total_mean_system": rnd(sum(sys_t) / len(sys_t), 1) if sys_t else None,
            "total_mean_reference": rnd(sum(ref_t) / len(ref_t), 1) if ref_t else None,
            "severity_vs_holistic_band": {"n": len(ok), "exact": rnd(sum(s == g for s, g in ok) / len(ok)) if ok else None,
                                          "within1": rnd(sum(abs(ORDER_BANDS.index(s) - ORDER_BANDS.index(g)) <= 1 for s, g in ok) / len(ok)) if ok else None,
                                          "qwk": qwk([ORDER_BANDS.index(s) for s, _ in ok], [ORDER_BANDS.index(g) for _, g in ok]),
                                          "system_bands": dict(Counter(s for s, _ in ok)), "reference_bands": dict(Counter(g for _, g in ok))},
            "rubric_band_reference_vs_holistic": rnd(sum(band_of(r["cons"]["total"]) == r["cons"]["band"] for r in rows) / len(rows)) if rows else None,
            "spearman_company_bootstrap95": cluster_boot(rows, lambda s: spearman([x["sys"]["risk"]["risk_score"] for x in s],
                                                                                  [x["cons"]["total"] for x in s]), n=500),
        },
    }


# ---------------------------------------------------------------- edit
CODE_OF_RULE = {"OC-01": "OFFSET_NEUTRALITY", "OC-02": "ABSOLUTE_CLAIM", "OC-03": "ABSOLUTE_CLAIM",
                "OC-04": "VAGUE_TERM", "OC-05": "ABSOLUTE_CLAIM", "VG-01": "VAGUE_TERM", "VG-02": "NO_FIGURE",
                "EV-02": "NO_EVIDENCE_REF", "EV-01": None}
SLOT_CODE = {"kỳ báo cáo": "MISSING_PERIOD", "năm gốc": "MISSING_BASELINE", "phạm vi": "MISSING_SCOPE"}
EVAL_CODES = ["MISSING_PERIOD", "MISSING_BASELINE", "MISSING_SCOPE", "NO_FIGURE", "VAGUE_TERM", "ABSOLUTE_CLAIM",
              "OFFSET_NEUTRALITY", "NO_EVIDENCE_REF"]


def product_suggestions(item: dict, so: dict | None, extractor) -> list:
    from quantum_gw.domain.enums import DocumentRole, SourceType
    from quantum_gw.domain.models import EvidenceChunk
    from quantum_gw.studio.document import _missing_attributes
    from quantum_gw.studio.suggest import suggest

    text = item["claim"]["text"]
    if so:  # pool A: the attributes the real run extracted
        a = so["claim_attrs"]

        class C:  # noqa: D401 - attribute bag for _missing_attributes
            pass
        c = C()
        c.metric, c.values, c.period, c.baseline, c.scope = a.get("metric"), a.get("values") or [], a.get("period"), a.get("baseline"), a.get("scope")
        c.direction, c.is_future_commitment = a.get("direction"), a.get("is_future_commitment")
        missing, vague, ctype, status = _missing_attributes(c), a.get("vague_terms_matched") or [], a.get("claim_type"), so["system_status"]
    else:  # pool B: no run exists; extract attributes with the product's rule-based extractor
        chunk = EvidenceChunk(chunk_id="eval", doc_id="eval", source_name="eval", role=DocumentRole.CLAIM_SOURCE,
                              source_type=SourceType.INTERNAL, text=text)
        c = extractor.describe(text, chunk)
        missing, vague, ctype, status = _missing_attributes(c), c.vague_terms_matched, c.claim_type, "INSUFFICIENT_EVIDENCE"
    diag = {"claim_id": item["item_id"], "missing": missing, "vague_terms": vague, "claim_type": ctype,
            "status": status, "evidence": []}
    return suggest(diag, text)


def eval_edit(sysout: dict) -> dict:
    from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
    from quantum_gw.settings import load_settings
    from quantum_gw.studio.suggest import apply

    class _NoAudit:
        def log(self, *a, **k):
            pass

        def __getattr__(self, name):
            return lambda *a, **k: None

    extractor = ClaimExtractionAgent(load_settings(str(ROOT / "configs/default.yaml")).claim_extraction, _NoAudit())
    items = items_of("edit")
    labs = labels_of(HERE / "edit" / "labels")
    rows = []
    for iid, lab in labs.items():
        sugg = product_suggestions(items[iid], sysout.get(iid), extractor)
        codes = set()
        for s in sugg:
            if s.rule_code == "SC-01":
                for slot, code in SLOT_CODE.items():
                    if slot in s.replacement:
                        codes.add(code)
            elif CODE_OF_RULE.get(s.rule_code):
                codes.add(CODE_OF_RULE[s.rule_code])
        new_nums = 0
        for s in sugg:
            after = apply(items[iid]["claim"]["text"], s) or ""
            new_nums += bool(nums(after) - nums(items[iid]["claim"]["text"]))
        rows.append({"item_id": iid, "company": items[iid]["company"], "src": iid[:1], "lab": lab, "sugg": sugg,
                     "codes": codes, "ref_codes": {x["code"] for x in lab.get("issues", [])},
                     "ref_kinds": {e["kind"] for e in lab.get("edits", [])}, "kinds": {s.kind for s in sugg},
                     "new_nums": new_nums})
    n = len(rows)
    green = [r for r in rows if r["lab"].get("is_green_claim")]
    det = prf(sum(bool(r["sugg"]) and r["lab"]["needs_edit"] for r in green),
              sum(bool(r["sugg"]) and not r["lab"]["needs_edit"] for r in green),
              sum(not r["sugg"] and r["lab"]["needs_edit"] for r in green))
    per_code = {c: prf(sum(c in r["codes"] and c in r["ref_codes"] for r in green),
                       sum(c in r["codes"] and c not in r["ref_codes"] for r in green),
                       sum(c not in r["codes"] and c in r["ref_codes"] for r in green)) for c in EVAL_CODES}
    per_kind = {k: prf(sum(k in r["kinds"] and k in r["ref_kinds"] for r in green),
                       sum(k in r["kinds"] and k not in r["ref_kinds"] for r in green),
                       sum(k not in r["kinds"] and k in r["ref_kinds"] for r in green))
                for k in ("add_scope", "placeholder", "evidence_ref", "soften")}
    ref_only = Counter(c for r in green for c in r["ref_codes"] - r["codes"])
    f1 = [v["f1"] for v in per_code.values() if v["f1"] is not None]
    return {
        "n_labeled": n, "by_source": dict(Counter(r["src"] for r in rows)),
        "reference": {"is_green_claim": sum(r["lab"].get("is_green_claim", False) for r in rows),
                      "needs_edit": sum(r["lab"].get("needs_edit", False) for r in rows),
                      "issue_codes": dict(Counter(c for r in rows for c in r["ref_codes"])),
                      "edit_kinds": dict(Counter(k for r in rows for k in r["ref_kinds"])),
                      "priority": dict(Counter(r["lab"].get("priority") for r in rows))},
        "system": {"suggestions_total": sum(len(r["sugg"]) for r in rows),
                   "kinds": dict(Counter(s.kind for r in rows for s in r["sugg"])),
                   "rule_codes": dict(Counter(s.rule_code for r in rows for s in r["sugg"])),
                   "suggestions_on_non_green_sentences": sum(len(r["sugg"]) for r in rows if not r["lab"].get("is_green_claim")),
                   "suggestions_introducing_new_numbers": sum(r["new_nums"] for r in rows)},
        "needs_edit_detection_on_green_claims": det,
        "issue_codes_on_green_claims": per_code, "macro_f1_issue_codes": rnd(sum(f1) / len(f1)) if f1 else None,
        "edit_kinds_on_green_claims": per_kind,
        "reference_issues_outside_product_vocabulary": dict(ref_only.most_common()),
    }


# ---------------------------------------------------------------- rules
SRC_MAP = {"independent": "external", "third_party": "external", "regulator": "external"}


def eval_rules() -> dict:
    from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
    from quantum_gw.domain.enums import DocumentRole, SourceType
    from quantum_gw.domain.models import EvidenceChunk
    from quantum_gw.legal.org_pack import ClaimFacts, evaluate_claim, load_org_pack
    from quantum_gw.settings import load_settings

    class _NoAudit:
        def __getattr__(self, name):
            return lambda *a, **k: None

    extractor = ClaimExtractionAgent(load_settings(str(ROOT / "configs/default.yaml")).claim_extraction, _NoAudit())
    packs, load_errors = {}, {}
    for d in sorted((HERE / "rules" / "orgs").iterdir()):
        try:
            p = load_org_pack(d)
            packs[p.org_id] = p
        except Exception as e:  # noqa: BLE001
            load_errors[d.name] = str(e)[:300]
    cases = [c for f in sorted((HERE / "rules").glob("cases_*.jsonl")) for c in jl(f)]
    out_rows = []
    for c in cases:
        pack = packs.get(c["org_id"])
        if not pack:
            continue
        text = c["claim"]["text"]
        chunk = EvidenceChunk(chunk_id="case", doc_id="case", source_name="case", role=DocumentRole.CLAIM_SOURCE,
                              source_type=SourceType.INTERNAL, text=text)
        ext = extractor.describe(text, chunk)
        a = c.get("claim_attrs") or {}

        def as_list(v):
            return [] if v in (None, "", []) else (v if isinstance(v, list) else [v])
        labeled = ClaimFacts(claim_id=c["case_id"], text=text, claim_type=ext.claim_type,
                             sector=c["claim"].get("company_sector"),
                             attributes={"metric": a.get("metric"), "value": as_list(a.get("value")), "unit": as_list(a.get("unit")),
                                         "period": a.get("period"), "baseline": a.get("baseline"), "scope": a.get("scope")})
        e2e = ClaimFacts.from_claim(ext, c["claim"].get("company_sector"))
        ev = [{"chunk_id": f"ev{i}", "text": e.get("text", ""), "source_type": SRC_MAP.get(e.get("source_type"), e.get("source_type", "internal"))}
              for i, e in enumerate(c.get("evidence") or [])]
        rule = next((r for r in pack.rules if r.rule_id == c["rule_id"]), None)
        if rule is None:
            continue
        one = type(pack)(**{**pack.__dict__, "rules": [rule]}) if hasattr(pack, "__dict__") else pack

        def run(facts):
            f = evaluate_claim([one], facts, ev, TODAY)
            return f[0].outcome if f else None
        out_rows.append({"case_id": c["case_id"], "org": c["org_id"], "type": c["case_type"], "exp": c["expected_outcome"],
                         "got": run(labeled), "got_e2e": run(e2e)})
    labels = ["COMPLIANT", "VIOLATION", "NEEDS_REVIEW", "NOT_APPLICABLE"]

    def summary(key: str) -> dict:
        if not out_rows:
            return {}
        per = {l: prf(sum(r[key] == l and r["exp"] == l for r in out_rows), sum(r[key] == l and r["exp"] != l for r in out_rows),
                      sum(r[key] != l and r["exp"] == l for r in out_rows)) for l in labels}
        f1 = [v["f1"] for v in per.values() if v["f1"] is not None]
        k = sum(r[key] == r["exp"] for r in out_rows)
        return {"accuracy": rnd(k / len(out_rows)), "wilson95": wilson(k, len(out_rows)), "macro_f1": rnd(sum(f1) / len(f1)) if f1 else None,
                "per_class": per,
                "confusion_expected_rows": {e: dict(Counter(r[key] for r in out_rows if r["exp"] == e)) for e in labels},
                "accuracy_by_case_type": {t: f"{sum(r[key] == r['exp'] for r in out_rows if r['type'] == t)}/{sum(r['type'] == t for r in out_rows)}"
                                          for t in sorted({r["type"] for r in out_rows})}}
    unsafe = [r for r in out_rows if r["type"] in ("injection", "override_attempt", "draft_rule", "expired_rule") and r["got"] != r["exp"]]
    return {"packs_loaded": len(packs), "pack_load_errors": load_errors, "n_rules": sum(len(p.rules) for p in packs.values()),
            "n_cases": len(cases), "n_evaluated": len(out_rows),
            "expected_outcomes": dict(Counter(r["exp"] for r in out_rows)), "case_types": dict(Counter(r["type"] for r in out_rows)),
            "labeled_attributes": summary("got"), "end_to_end_extractor_attributes": summary("got_e2e"),
            "safety_case_mismatches": [{k: r[k] for k in ("case_id", "type", "exp", "got")} for r in unsafe],
            "verdict_changes": "0 by construction: evaluate_claim reads claims/evidence and returns findings only; "
                               "tests/test_org_pack.py checks pipeline verdict invariance"}


# ---------------------------------------------------------------- UX lint (computable subset)
FORBIDDEN = ["vi phạm", "gian lận", "sai phạm", "lừa dối", "phát hiện greenwashing", "điểm trung thực", "fraud", "illegal", "false claim"]
NEG_OK = re.compile(r"không (có nghĩa|đồng nghĩa|nhằm kết luận)")
NEUTRAL = ["chưa đủ bằng chứng", "chưa đủ để kết luận", "không thấy trong kho", "kho tài liệu chưa đủ", "chưa đủ để suy ra",
           "chưa xác minh", "không đủ bằng chứng"]
EN_FUNC = {"the", "and", "of", "with", "must", "should", "claim", "evidence", "page", "supports", "source", "value", "retrieved"}
SNAKE = re.compile(r"\b[a-z]+_[a-z0-9_]+\b")
ENUM = re.compile(r"\b[A-Z]{3,}(?:_[A-Z]+)+\b")


def lint_strings(strings: list[str]) -> dict:
    sent_long = over80 = leak = forb = english = 0
    for s in strings:
        if len(s.split()) > 80:
            over80 += 1
        if any(len(x.split()) > 40 for x in re.split(r"[.;!?]\s", s)):
            sent_long += 1
        t = re.sub(r"\S+\.(pdf|docx|xlsx)\b|\b\d+/\d{4}/[\w-]+\b|\b[A-Z]{2}-\d{2}\b", "", s)
        if SNAKE.search(t) or ENUM.search(t):
            leak += 1
        if len(EN_FUNC & set(re.findall(r"[a-z]+", t.casefold()))) >= 2 and not re.search(r"[À-ỹđ]", t):
            english += 1
        low = s.casefold()
        if any(w in low for w in FORBIDDEN) and not NEG_OK.search(low):
            forb += 1
    return {"strings": len(strings), "over_80_words": over80, "sentence_over_40_words": sent_long,
            "internal_code_leaks": leak, "english_strings": english, "forbidden_terms": forb}


def eval_ux(edit_res: dict) -> dict:
    st = HERE / "inputs" / "refresh_stats.json"
    runs = json.loads(st.read_text(encoding="utf-8"))["current_runs"] if st.exists() else ["c892c13727c24bb9"]
    per_run, totals = {}, Counter()
    for rid in runs:
        f = ROOT / ".quantum" / "runs" / rid / "result.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        v = d.get("verifications", [])
        rats = [x.get("rationale") or "" for x in v]
        reasons = [e.get("relation_reason") or "" for x in v for e in x.get("evidence", []) if e.get("relation_reason")]
        lint = lint_strings(rats + reasons)
        ev = [e for x in v for e in x.get("evidence", [])]
        no_page = sum(not e.get("source_name") or e.get("page") in (None, "") for e in ev)
        ins = [x for x in v if x.get("status") in ("INSUFFICIENT_EVIDENCE", "UNSUPPORTED")]
        neutral_ok = sum(any(p in (x.get("rationale") or "").casefold() for p in NEUTRAL) for x in ins)
        per_run[rid] = {**lint, "evidence_items": len(ev), "evidence_without_doc_or_page": no_page,
                        "insufficient_or_unsupported": len(ins), "insufficient_with_neutral_phrase": neutral_ok}
        totals.update({k: v for k, v in per_run[rid].items() if isinstance(v, int)})
    checks = {
        "UXL-01_length": "PASS" if totals["over_80_words"] == 0 else "FAIL",
        "UXL-03_code_leak": "PASS" if totals["internal_code_leaks"] == 0 and totals["english_strings"] == 0 else "FAIL",
        "UXL-04_doc_and_page": "PASS" if totals["evidence_without_doc_or_page"] == 0 else "FAIL",
        "UXL-06a_neutral_phrase": "PASS" if totals["insufficient_with_neutral_phrase"] == totals["insufficient_or_unsupported"] else "FAIL",
        "UXL-07_forbidden_terms": "PASS" if totals["forbidden_terms"] == 0 else "FAIL",
        "UXL-10_safe_suggestions": "PASS" if edit_res.get("system", {}).get("suggestions_introducing_new_numbers", 1) == 0 else "FAIL",
    }
    return {"runs": per_run, "totals": dict(totals), "checks": checks, "UXL-13_bad_packs": bad_pack_fixtures()}


def bad_pack_fixtures() -> dict:
    import yaml
    from quantum_gw.legal.org_pack import OrgPackError, load_org_pack

    base = ROOT / "configs" / "org_packs" / "demo_ngan_hang_xanh"
    good = yaml.safe_load((base / "pack.yaml").read_text(encoding="utf-8"))

    def mutate(code):
        d = json.loads(json.dumps(good, default=str))
        r = d["rules"][0]
        if code == "E1":
            r["conditions"][0]["check"] = "regex_match"
        elif code == "E3":
            r.pop("severity", None)
        elif code == "E4":
            d["org_id"] = "Ngan-Hang X"
        elif code == "E5":
            d["precedence"] = "above_law"
        elif code == "E6":
            r["on_fail"] = "set_verdict_contradicted"
        elif code == "E7":
            r["effective_from"], r["effective_to"] = "2026-06-01", "2026-01-01"
        elif code == "E8":
            r["source_document"] = "POL-99"
        elif code == "E9":
            d["approved_by"] = ""
        return d
    res = {}
    tmp = Path(tempfile.mkdtemp(prefix="gs_badpack_"))
    try:
        for code in ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9"]:
            folder = tmp / good["org_id"]
            if folder.exists():
                shutil.rmtree(folder)
            shutil.copytree(base, folder)
            if code == "E2":
                (folder / "pack.yaml").write_text("kind: org_pack\nrules: [\n  - rule_id: X\n bad_indent", encoding="utf-8")
            else:
                (folder / "pack.yaml").write_text(yaml.safe_dump(mutate(code), allow_unicode=True, sort_keys=False), encoding="utf-8")
            try:
                p = load_org_pack(folder)
                res[code] = {"rejected": False, "draft": bool(getattr(p, "draft", False))}
            except OrgPackError as e:
                msg = str(e)
                res[code] = {"rejected": True, "vietnamese": bool(re.search(r"[ăâđêôơưạảãáàệểễếề]", msg)),
                             "no_traceback": "Traceback" not in msg, "message_head": msg[:160]}
            except Exception as e:  # noqa: BLE001
                res[code] = {"rejected": True, "unexpected_exception": type(e).__name__, "message_head": str(e)[:160]}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    failed = [c for c in ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"] if not res[c]["rejected"]]
    if res["E9"]["rejected"] or not res["E9"].get("draft"):
        failed.append("E9")
    return {"cases": res, "verdict": "PASS" if not failed else f"FAIL ({', '.join(failed)}; {9 - len(failed)}/9 đạt)",
            "failed": failed,
            "note": "E10 (injection sentence in policy doc) is covered by tests/test_org_pack.py and by rule cases of type injection"}


# ---------------------------------------------------------------- main
def md_report(r: dict) -> str:
    e, s, ed, ru, ux = r["explain"], r["score"], r["edit"], r["rules"], r["ux"]
    L = ["# GS-Eval v2: kết quả đánh giá hệ thống hiện tại (tự sinh bởi evaluate.py)", "",
         f"*Chạy {r['run_date']}. Nhãn: Claude theo `LABELING_GUIDE.md`, tác giả đọc lại. Hệ thống: lượt offline trong `.quantum/runs`.*", ""]
    if e.get("n_labeled"):
        v = e["verdict_on_claims"]
        L += [f"*Nguồn đầu ra hệ thống: {r['system_output_source']}.*", "",
              "## 1. Giải thích và kết luận (D-EXPLAIN)",
              f"- {e['n_labeled']} mẫu có nhãn; {e['n_with_current_output']} mẫu có đầu ra của mã hiện tại "
              f"(theo kết luận hiện tại: {e['sample_by_system_status']}). Mã hiện tại không còn trích {e['not_extracted_by_current_system']['n']} câu "
              f"(nhãn: {e['not_extracted_by_current_system']['reference_verdicts']}).",
              f"- Câu hệ thống trích ra nhưng **không phải tuyên bố**: {e['extraction_not_a_claim']['k']}/{e['n_with_current_output']} "
              f"(Wilson 95 % {e['extraction_not_a_claim']['wilson95']}); ước tính trên toàn kho sau khi trọng số lại: "
              f"{e['extraction_not_a_claim']['rate_population_weighted']}. Theo kết luận hệ thống: {e['extraction_not_a_claim']['by_system_status']}.",
              f"- Trên {v['n']} tuyên bố thật: kết luận trùng nhãn {v['accuracy_sample']} (trọng số toàn kho {v['accuracy_population_weighted']}, "
              f"bootstrap theo công ty {v['accuracy_company_bootstrap95']}), κ = {v['cohen_kappa']}, macro-F1 {v['macro_f1_present_classes']}.",
              f"- Kết luận dứt khoát của hệ thống (S/C): {e['decisive']['n_system_decisive']}, precision so với nhãn {e['decisive']['precision_vs_reference']}; "
              f"CONTRADICTED sai {e['decisive']['false_contradicted']} (trên tuyên bố thật {e['decisive']['false_contradicted_on_real_claims']}; nhãn: {e['decisive']['false_contradicted_ref_breakdown']}); "
              f"SUPPORTED sai {e['decisive']['false_supported']} (nhãn: {e['decisive']['false_supported_ref_breakdown']}).",
              f"- Lời giải thích: trung bình {e['rationale']['words_mean']} từ, {e['rationale']['distinct_rationales']} câu khác nhau trên {e['n_with_current_output']} mẫu; "
              f"độ phủ ý bắt buộc (proxy từ khoá) {e['rationale']['must_mention_coverage_proxy_mean']}; số không có nguồn: {e['rationale']['rationales_with_ungrounded_numbers']}.",
              "", "| Hệ thống \\ Nhãn | " + " | ".join(sorted(e["reference_verdicts"])) + " |", "|---|" + "---|" * len(e["reference_verdicts"])]
        for k, row in e["confusion_system_rows_reference_cols"].items():
            L.append(f"| {k} | " + " | ".join(str(row.get(c, 0)) for c in sorted(e["reference_verdicts"])) + " |")
        L += ["", "| Thuộc tính thiếu | P | R | F1 |", "|---|---|---|---|"]
        L += [f"| {a} | {x['precision']} | {x['recall']} | {x['f1']} |" for a, x in e["missing_attributes_vs_reference"].items()]
        L.append("")
    j = r.get("explain_judge") or {}
    if j.get("overall"):
        o = j["overall"]
        L += ["### Chấm lời giải thích theo danh mục tham chiếu", f"- n = {o['n']}; độ phủ ý bắt buộc {o['must_mention_coverage']}; "
              f"nói điều không được nói: {o['items_violating_must_not_say']} mẫu; trung thực với bằng chứng {o['faithful_share']} (Wilson {j['faithful_wilson95']}); "
              f"chỉ ra việc cần làm {o['actionable_share']}; độ rõ TB {o['clarity_mean']}/5.",
              "", "| Kết luận hệ thống | n | Phủ ý | Trung thực | Chỉ việc | Rõ |", "|---|---|---|---|---|---|"]
        L += [f"| {k} | {v['n']} | {v['must_mention_coverage']} | {v['faithful_share']} | {v['actionable_share']} | {v['clarity_mean']} |" for k, v in j["by_system_status"].items()]
        L.append("")
    if s.get("n_both"):
        sv = s["system_vs_consensus"]
        L += ["## 2. Chấm rủi ro (D-SCORE)", f"- Hai lượt mù: {s['n_both']} mẫu; phân xử {s['n_adjudicated_items']} mẫu.",
              f"- Đồng thuận hai lượt (tổng điểm) Spearman {s['inter_pass_agreement']['total']['spearman']}; dải tổng thể QWK {s['inter_pass_agreement']['total']['holistic_band_qwk']}.",
              f"- Hệ thống so với đồng thuận: Spearman tổng điểm {sv['total_spearman']} (bootstrap công ty {sv['spearman_company_bootstrap95']}); "
              f"trung bình {sv['total_mean_system']} so với {sv['total_mean_reference']}; mức độ so với dải tổng thể: đúng {sv['severity_vs_holistic_band']['exact']}, lệch ≤ 1 bậc {sv['severity_vs_holistic_band']['within1']}.",
              "", "| Thành phần | QWK hai lượt | QWK hệ thống–đồng thuận | Mức TB hệ thống | Mức TB nhãn | Không áp dụng | Hệ thống vẫn phạt |", "|---|---|---|---|---|---|---|"]
        for c in COMPONENTS:
            x = sv["components"][c]
            L.append(f"| {c} | {s['inter_pass_agreement']['components'][c]['qwk']} | {x['qwk_system_vs_consensus']} | {x['system_mean_level']} | {x['reference_mean_level']} | {x['not_applicable_by_reference']} | {x['system_penalised_when_not_applicable']} |")
        L.append("")
    if ed.get("n_labeled"):
        L += ["## 3. Gợi ý sửa (D-EDIT)", f"- n = {ed['n_labeled']}; tuyên bố xanh {ed['reference']['is_green_claim']}, cần sửa {ed['reference']['needs_edit']}.",
              f"- Nhận ra câu cần sửa: {ed['needs_edit_detection_on_green_claims']}.",
              f"- Gợi ý của hệ thống: {ed['system']['suggestions_total']} ({ed['system']['kinds']}); trên câu không phải tuyên bố xanh: {ed['system']['suggestions_on_non_green_sentences']}; thêm số mới: {ed['system']['suggestions_introducing_new_numbers']}.",
              f"- Macro-F1 mã vấn đề: {ed['macro_f1_issue_codes']}. Vấn đề nằm ngoài từ vựng của hệ thống: {ed['reference_issues_outside_product_vocabulary']}.",
              "", "| Mã vấn đề | P | R | F1 | tp/fp/fn |", "|---|---|---|---|---|"]
        L += [f"| {c} | {x['precision']} | {x['recall']} | {x['f1']} | {x['tp']}/{x['fp']}/{x['fn']} |" for c, x in ed["issue_codes_on_green_claims"].items()]
        L.append("")
    if ru.get("n_evaluated"):
        a, b = ru["labeled_attributes"], ru["end_to_end_extractor_attributes"]
        L += ["## 4. Quy tắc nội bộ (D-RULES, org pack)", f"- {ru['packs_loaded']} pack, {ru['n_rules']} quy tắc, {ru['n_evaluated']} ca; kết quả kỳ vọng {ru['expected_outcomes']}.",
              f"- Engine với thuộc tính đúng: accuracy {a['accuracy']} (Wilson {a['wilson95']}), macro-F1 {a['macro_f1']}.",
              f"- Đầu–cuối (thuộc tính do bộ trích luật lấy): accuracy {b['accuracy']} (Wilson {b['wilson95']}), macro-F1 {b['macro_f1']}.",
              f"- Theo loại ca (thuộc tính đúng): {a['accuracy_by_case_type']}.", f"- Ca an toàn lệch kỳ vọng: {len(ru['safety_case_mismatches'])}.", ""]
    L += ["## 5. UX lint", f"- Kiểm: {ux['checks']}", f"- Tổng: {ux['totals']}", f"- UXL-13 pack lỗi: {ux['UXL-13_bad_packs']['verdict']}", ""]
    return "\n".join(L)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    cur = HERE / "inputs" / "system_outputs_current.jsonl"
    if cur.exists():
        rows = jl(cur)
        sysout = {r["item_id"]: r for r in rows if r["match"] != "not_extracted"}
        NOT_EXTRACTED.update({r["item_id"]: r for r in rows if r["match"] == "not_extracted"})
        source = "current-code runs (>= 2026-10-22), see inputs/refresh_stats.json"
    else:
        sysout = {r["item_id"]: r for r in jl(HERE / "inputs" / "system_outputs.jsonl")}
        source = "latest run per claim (mixed code versions)"
    res = {"run_date": str(TODAY), "system_output_source": source,
           "refresh_stats": json.loads((HERE / "inputs/refresh_stats.json").read_text(encoding="utf-8")) if cur.exists() else None}
    res["explain"] = eval_explain(sysout)
    res["explain_judge"] = eval_judge()
    res["score"] = eval_score(sysout)
    res["edit"] = eval_edit(sysout)
    res["rules"] = eval_rules()
    res["ux"] = eval_ux(res["edit"])
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "eval_results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (out / "EVAL_REPORT.md").write_text(md_report(res), encoding="utf-8")
    print(md_report(res))


if __name__ == "__main__":
    main()
