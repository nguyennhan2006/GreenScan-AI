"""Score GS-Issue: finding issues (per code) and proposing correct fixes, for every system that has outputs.

    python -I -X utf8 benchmark/gs_issue/score_issue.py            # -> results/score_issue.json, results/SCORE_ISSUE.md

Systems: every out/<tag>__<input>.jsonl (rules from run_rules.py; models from Kaggle, downloaded into out/), plus
derived systems: hybrid (rules U q3-4b, model fix kept only when it invents no number), and <tag>+guard (same guard
on the model alone). Datasets: layer A (exact labels + fix oracle), D-EDIT (Claude labels), layer B (silver = the
14B and 32B readers agree; only when both outputs exist; those two are then not scored on B).
Registered predictions: configs/measurement_decisions.yaml, gs_issue_v1. Metric catalogue:
docs/04-data-ai/DO_DO_DANH_GIA_2026-11-11.md.
"""
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from taxonomy import CODES, KIND_OK, family, numbers, oracle, slot_filled  # noqa: E402

OUT, RES = HERE / "out", HERE / "results"
SLOT_OF = {"MISSING_PERIOD": "period", "MISSING_BASELINE": "baseline", "MISSING_SCOPE": "scope", "ENTITY_SCOPE_AMBIGUOUS": "scope",
           "NO_FIGURE": "figure", "NO_EVIDENCE_REF": "source", "UNVERIFIED_LABEL_OR_CERT": "issuer"}
SILVER_READERS = ("q3-14b-awq", "q3-32b-awq")


def jl(p):
    return [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]


def wilson(k, n, z=1.96):
    if not n:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0, c - h), 3), round(min(1, c + h), 3)]


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f = 2 * p * r / (p + r) if p and r else (0.0 if (p is not None or r is not None) and tp == 0 else None)
    return {"tp": tp, "fp": fp, "fn": fn, "p": rnd(p), "r": rnd(r), "f1": rnd(f), "p_ci": wilson(tp, tp + fp), "r_ci": wilson(tp, tp + fn)}


def rnd(x, k=3):
    return None if x is None else round(x, k)


def chrf(a, b, n=4, beta=2):
    a, b = re.sub(r"\s+", " ", a or ""), re.sub(r"\s+", " ", b or "")
    ps, rs = [], []
    for k in range(1, n + 1):
        ga = Counter(a[i:i + k] for i in range(len(a) - k + 1))
        gb = Counter(b[i:i + k] for i in range(len(b) - k + 1))
        m = sum((ga & gb).values())
        if sum(ga.values()) and sum(gb.values()):
            ps.append(m / sum(ga.values()))
            rs.append(m / sum(gb.values()))
    if not ps:
        return 0.0
    p, r = sum(ps) / len(ps), sum(rs) / len(rs)
    return 0.0 if p + r == 0 else (1 + beta ** 2) * p * r / (beta ** 2 * p + r)


def pred_codes(parsed):
    if not isinstance(parsed, dict):
        return set()
    out = set()
    for i in parsed.get("issues") or []:
        c = (i.get("code") if isinstance(i, dict) else str(i)) or ""
        c = c.strip().upper()
        if c in CODES:
            out.add(c)
    return out


def pred_spans(parsed):
    if not isinstance(parsed, dict):
        return {}
    return {(i.get("code") or "").upper(): i.get("span") or "" for i in parsed.get("issues") or [] if isinstance(i, dict)}


def rewritten(parsed, claim):
    if not isinstance(parsed, dict):
        return claim
    t = parsed.get("rewritten_claim")
    if isinstance(t, str) and t.strip():
        return t.strip()
    text = claim
    for e in parsed.get("edits") or []:
        if isinstance(e, dict) and e.get("target_span") and e["target_span"] in text and isinstance(e.get("replacement"), str):
            text = text.replace(e["target_span"], e["replacement"], 1)
    return text


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip())


# ---------------------------------------------------------------- systems
def load_systems(stem):
    sys_out = {}
    for p in sorted(OUT.glob(f"*__{stem}.jsonl")):
        tag = p.name.split("__")[0]
        sys_out[tag] = {r["id"]: r.get("parsed") for r in jl(p)}
    # Layer B was read in three parts on Kaggle (gsi_layer_b1..b3)
    if stem == "gsi_layer_b":
        for p in sorted(OUT.glob("*__gsi_layer_b[123].jsonl")):
            tag = p.name.split("__")[0]
            sys_out.setdefault(tag, {}).update({r["id"]: r.get("parsed") for r in jl(p)})
    return sys_out


def derive(sys_out, claims):
    """hybrid = rules U q3-4b; '+guard' = model fix rejected (claim left as is) when it invents a number."""
    def guarded(parsed, claim):
        if not isinstance(parsed, dict):
            return parsed
        new = numbers(rewritten(parsed, claim)) - numbers(claim)
        return parsed if not new else dict(parsed, rewritten_claim=claim, guard_rejected=sorted(new))
    out = dict(sys_out)
    for tag in list(sys_out):
        if tag.startswith("q3-"):
            out[tag + "+guard"] = {i: guarded(p, claims[i]) for i, p in sys_out[tag].items() if i in claims}
    if "rules" in sys_out and "q3-4b" in sys_out:
        hy = {}
        for i, claim in claims.items():
            r, m = sys_out["rules"].get(i) or {}, guarded(sys_out["q3-4b"].get(i), claim) or {}
            issues = (m.get("issues") or []) + [x for x in (r.get("issues") or []) if x.get("code") not in pred_codes(m)]
            fix = m.get("rewritten_claim") if m.get("rewritten_claim") and not m.get("guard_rejected") else None
            if not fix or norm(fix) == norm(claim):
                fix = rewritten(r, claim)
            hy[i] = {"issues": issues, "rewritten_claim": fix, "edits": []}
        out["hybrid"] = hy
    return out


# ---------------------------------------------------------------- detection
def detection(gold, preds, codes_universe):
    """gold: id -> set of codes (None = unlabelled for this id). preds: id -> parsed."""
    ids = [i for i in gold if i in preds]
    per = {}
    for c in codes_universe:
        tp = sum(c in gold[i] and c in pred_codes(preds[i]) for i in ids)
        fp = sum(c not in gold[i] and c in pred_codes(preds[i]) for i in ids)
        fn = sum(c in gold[i] and c not in pred_codes(preds[i]) for i in ids)
        if tp + fn:
            per[c] = prf(tp, fp, fn)
    fams = sorted({family(c) for c in codes_universe})
    perf = {}
    for f in fams:
        g = lambda i: {family(c) for c in gold[i]}
        pr = lambda i: {family(c) for c in pred_codes(preds[i])}
        tp = sum(f in g(i) and f in pr(i) for i in ids)
        fp = sum(f not in g(i) and f in pr(i) for i in ids)
        fn = sum(f in g(i) and f not in pr(i) for i in ids)
        if tp + fn:
            perf[f] = prf(tp, fp, fn)
    tp = sum(len(gold[i] & pred_codes(preds[i])) for i in ids)
    fp = sum(len(pred_codes(preds[i]) - gold[i]) for i in ids)
    fn = sum(len(gold[i] - pred_codes(preds[i])) for i in ids)
    pos = [i for i in ids if gold[i]]
    neg = [i for i in ids if not gold[i]]
    tpr = sum(bool(pred_codes(preds[i])) for i in pos) / len(pos) if pos else None
    fa = sum(bool(pred_codes(preds[i])) for i in neg)
    f1s = [v["f1"] for v in per.values() if v["f1"] is not None]
    ff1 = [v["f1"] for v in perf.values() if v["f1"] is not None]
    return {"n": len(ids), "n_with_issue": len(pos), "n_clean": len(neg),
            "macro_f1": rnd(sum(f1s) / len(f1s)) if f1s else None, "macro_f1_family": rnd(sum(ff1) / len(ff1)) if ff1 else None,
            "micro": prf(tp, fp, fn), "per_code": per, "per_family": perf,
            "needs_edit_recall": rnd(tpr), "clean_false_alarm": rnd(fa / len(neg)) if neg else None,
            "clean_false_alarm_ci": wilson(fa, len(neg)),
            "balanced_accuracy": rnd((tpr + 1 - fa / len(neg)) / 2) if pos and neg else None,
            "exact_set": rnd(sum(gold[i] == pred_codes(preds[i]) for i in ids) / len(ids)) if ids else None,
            "unparsed": sum(preds[i] is None for i in ids)}


def boot_macro(gold, preds, groups, codes_universe, n=500, seed=0):
    rng = random.Random(seed)
    keys = sorted(set(groups.values()))
    vals = []
    for _ in range(n):
        pick = [rng.choice(keys) for _ in keys]
        ids = [i for k in pick for i in gold if groups.get(i) == k]
        g2 = {}
        for j, i in enumerate(ids):
            g2[f"{i}#{j}"] = gold[i]
        p2 = {f"{i}#{j}": preds[i] for j, i in enumerate(ids) if i in preds}
        m = detection(g2, p2, codes_universe)["macro_f1"]
        if m is not None:
            vals.append(m)
    vals.sort()
    return [rnd(vals[int(0.025 * len(vals))]), rnd(vals[int(0.975 * len(vals)) - 1])] if vals else [None, None]


# ---------------------------------------------------------------- fix (layer A oracle)
def fixes_layer_a(cases, preds):
    rows = []
    for c in cases:
        p = preds.get(c["id"])
        after = rewritten(p, c["claim"])
        if not c["codes"]:
            rows.append({"id": c["id"], "clean": True, "changed": norm(after) != norm(c["claim"]),
                         "new_numbers": sorted(numbers(after) - numbers(c["claim"]))})
            continue
        o = oracle(c, c["claim"], after)
        kinds = {e.get("kind") for e in (p or {}).get("edits") or [] if isinstance(e, dict)}
        rows.append({"id": c["id"], "clean": False, "codes": c["codes"], "split": c["split"], "detected": bool(set(c["codes"]) & pred_codes(p)),
                     "resolves": o["resolves"], "keeps": o["keeps_numbers"], "invents": bool(o["new_numbers"]),
                     "correct": o["resolves"] and o["keeps_numbers"] and not o["new_numbers"],
                     "kind_ok": bool(kinds & set(c["fix_kinds_ok"])), "chrf_ref": rnd(chrf(after, c["reference_fix"])),
                     "guard_rejected": bool((p or {}).get("guard_rejected"))})
    iss = [r for r in rows if not r["clean"]]
    cln = [r for r in rows if r["clean"]]
    single = [r for r in iss if r["split"] == "A-single"]
    per = {}
    for code in CODES:
        rs = [r for r in single if r["codes"] == [code]]
        if rs:
            k = sum(r["correct"] for r in rs)
            per[code] = {"n": len(rs), "correct": rnd(k / len(rs)), "ci": wilson(k, len(rs)),
                         "resolves": rnd(sum(r["resolves"] for r in rs) / len(rs))}
    f = lambda key, rs: rnd(sum(r[key] for r in rs) / len(rs)) if rs else None
    k = sum(r["correct"] for r in single)
    return {"n_issue_cases": len(iss), "single": len(single),
            "funnel_single": {"detected": f("detected", single), "resolves": f("resolves", single), "keeps_numbers": f("keeps", single),
                              "invents_number": f("invents", single), "correct": f("correct", single), "correct_ci": wilson(k, len(single)),
                              "kind_ok": f("kind_ok", single), "chrf_to_reference": f("chrf_ref", single)},
            "multi_correct": f("correct", [r for r in iss if r["split"] == "A-multi"]),
            "useful_suggestion_rate": rnd(sum(r["detected"] and r["correct"] for r in single) / max(1, sum(r["detected"] for r in single))),
            "clean_changed": f("changed", cln), "clean_invents": rnd(sum(bool(r["new_numbers"]) for r in cln) / len(cln)) if cln else None,
            "guard_rejected": sum(r.get("guard_rejected", False) for r in iss), "per_code": per}


def fixes_real(gold, claims, preds):
    """Real sentences: no oracle. Invented numbers on every rewrite; slot codes: a new placeholder names the slot."""
    inv, n, slot_ok, slot_n = 0, 0, 0, 0
    for i, codes in gold.items():
        if i not in preds:
            continue
        after = rewritten(preds[i], claims[i])
        n += 1
        inv += bool(numbers(after) - numbers(claims[i]))
        for c in codes:
            if c in SLOT_OF:
                slot_n += 1
                slot_ok += slot_filled(claims[i], after, SLOT_OF[c])
    return {"rewrites": n, "invents_number": rnd(inv / n) if n else None, "invents_ci": wilson(inv, n),
            "slot_fix_rate": rnd(slot_ok / slot_n) if slot_n else None, "slot_fix_ci": wilson(slot_ok, slot_n), "slot_n": slot_n}


def kappa(a, b):
    n = len(a)
    if not n:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return rnd((po - pe) / (1 - pe)) if pe < 1 else None


# ---------------------------------------------------------------- main
def main():
    RES.mkdir(exist_ok=True)
    report = {"registered": "configs/measurement_decisions.yaml gs_issue_v1", "datasets": {}}
    # layer A
    A = jl(HERE / "data/layer_a.jsonl")
    claims = {c["id"]: c["claim"] for c in A}
    sysA = derive(load_systems("gsi_layer_a"), claims)
    gold = {c["id"]: set(c["codes"]) for c in A}
    groups = {c["id"]: c["sector"] for c in A}
    ra = {}
    for tag, preds in sorted(sysA.items()):
        d = detection(gold, preds, list(CODES))
        d["macro_f1_ci_sector_boot"] = boot_macro(gold, preds, groups, list(CODES))
        ra[tag] = {"detection": d, "fix": fixes_layer_a(A, preds)}
    report["datasets"]["layer_a"] = {"n": len(A), "systems": ra}
    # D-EDIT
    E = {r["id"]: r for r in jl(HERE / "data/d_edit.jsonl")}
    labs = {}
    for f in sorted((ROOT / "benchmark/gs_eval_v2/edit/labels").glob("*.jsonl")):
        for r in jl(f):
            if r.get("is_green_claim"):
                labs[r["item_id"]] = {x["code"] for x in r.get("issues") or [] if x["code"] in CODES}
    claimsE = {i: E[i]["claim"] for i in labs}
    sysE = derive(load_systems("gsi_d_edit"), claimsE)
    groupsE = {i: E[i]["company"] for i in labs}
    re_ = {}
    for tag, preds in sorted(sysE.items()):
        d = detection(labs, preds, list(CODES))
        d["macro_f1_ci_company_boot"] = boot_macro(labs, preds, groupsE, list(CODES))
        re_[tag] = {"detection": d, "fix": fixes_real(labs, claimsE, preds)}
    report["datasets"]["d_edit"] = {"n_green": len(labs), "labels": "Claude (pending human review)", "systems": re_}
    # layer B (silver)
    B = {r["id"]: r for r in jl(HERE / "data/layer_b_all.jsonl")}
    sysB = load_systems("gsi_layer_b")
    if all(t in sysB for t in SILVER_READERS):
        a, b = (sysB[t] for t in SILVER_READERS)
        silver, agree = {}, {}
        for i in B:
            if i not in a or i not in b or a[i] is None or b[i] is None:
                continue
            ca, cb = pred_codes(a[i]), pred_codes(b[i])
            silver[i] = ca & cb if (ca & cb) or (not ca and not cb) else None
        agree = {c: kappa([c in pred_codes(a[i]) for i in B if i in a and i in b and a[i] and b[i]],
                          [c in pred_codes(b[i]) for i in B if i in a and i in b and a[i] and b[i]]) for c in CODES}
        silver = {i: s for i, s in silver.items() if s is not None}
        claimsB = {i: B[i]["claim"] for i in silver}
        sysB2 = derive({t: p for t, p in sysB.items() if t not in SILVER_READERS} | {"rules": sysB.get("rules", {})}, claimsB)
        rb = {}
        for tag, preds in sorted(sysB2.items()):
            d = detection(silver, preds, list(CODES))
            d["macro_f1_ci_company_boot"] = boot_macro(silver, preds, {i: B[i]["company"] for i in silver}, list(CODES))
            rb[tag] = {"detection": d, "fix": fixes_real(silver, claimsB, preds)}
        dist = Counter(c for s in silver.values() for c in (s or {"CLEAN"}))
        report["datasets"]["layer_b"] = {"n_read": len(B), "n_silver": len(silver), "silver_label_counts": dict(dist.most_common()),
                                         "reader_kappa_per_code": agree, "systems": rb}
        with open(HERE / "data/layer_b_silver.jsonl", "w", encoding="utf-8") as fh:
            for i, s in silver.items():
                fh.write(json.dumps({"id": i, "company": B[i]["company"], "claim": B[i]["claim"], "evidence": B[i]["evidence"],
                                     "codes": sorted(s), "label_source": "silver: q3-14b-awq AND q3-32b-awq",
                                     "review_status": "pending_human_review"}, ensure_ascii=False) + "\n")
    # reader reliability vs Claude on D-EDIT
    rel = {}
    for tag, preds in sysE.items():
        if tag.startswith("q3-") and "+" not in tag:
            ids = [i for i in labs if i in preds and preds[i] is not None]
            rel[tag] = {c: kappa([c in labs[i] for i in ids], [c in pred_codes(preds[i]) for i in ids]) for c in CODES}
    report["reader_vs_claude_kappa_d_edit"] = rel
    json.dump(report, open(RES / "score_issue.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = to_md(report)
    (RES / "SCORE_ISSUE.md").write_text(md, encoding="utf-8")
    print(md[:6000])


def to_md(r):
    L = ["# GS-Issue: tìm lỗ hổng và đề xuất sửa (tự sinh bởi score_issue.py)", "",
         "Đăng ký trước: `configs/measurement_decisions.yaml` khối `gs_issue_v1`. Lớp A là ca đột biến có đáp án; "
         "D-EDIT là nhãn Claude; lớp B là nhãn bạc (14B và 32B cùng gán). Chưa nhãn nào là nhãn người.", ""]
    for ds, d in r["datasets"].items():
        L += [f"## {ds}", ""]
        L += ["| Hệ thống | macro-F1 | CI95 | F1 theo họ | micro-F1 | Bắt câu cần sửa | Báo nhầm câu sạch | Không parse |", "|---|---|---|---|---|---|---|---|"]
        for tag, s in d["systems"].items():
            x = s["detection"]
            ci = x.get("macro_f1_ci_sector_boot") or x.get("macro_f1_ci_company_boot")
            L.append(f"| {tag} | {x['macro_f1']} | {ci} | {x['macro_f1_family']} | {x['micro']['f1']} | {x['needs_edit_recall']} | "
                     f"{x['clean_false_alarm']} | {x['unparsed']} |")
        L.append("")
        if ds == "layer_a":
            L += ["| Hệ thống | Phát hiện | Sửa giải quyết | Giữ số | Bịa số | **Sửa đúng** | CI95 | Hai lỗi: sửa đúng | Sửa câu sạch | Gợi ý dùng được |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
            for tag, s in d["systems"].items():
                f = s["fix"]["funnel_single"]
                L.append(f"| {tag} | {f['detected']} | {f['resolves']} | {f['keeps_numbers']} | {f['invents_number']} | **{f['correct']}** | "
                         f"{f['correct_ci']} | {s['fix']['multi_correct']} | {s['fix']['clean_changed']} | {s['fix']['useful_suggestion_rate']} |")
            L.append("")
            codes = list(CODES)
            tags = list(d["systems"])
            L += ["Recall theo mã (lớp A, ca một lỗi và hai lỗi):", "", "| Mã | " + " | ".join(tags) + " |", "|---" * (len(tags) + 1) + "|"]
            for c in codes:
                L.append(f"| {c} | " + " | ".join(str((d["systems"][t]["detection"]["per_code"].get(c) or {}).get("r")) for t in tags) + " |")
            L.append("")
        else:
            L += ["| Hệ thống | Bịa số khi sửa | Sửa đúng chỗ trống (mã thiếu thông tin) |", "|---|---|---|"]
            for tag, s in d["systems"].items():
                f = s["fix"]
                L.append(f"| {tag} | {f['invents_number']} {f['invents_ci']} | {f['slot_fix_rate']} {f['slot_fix_ci']} (n {f['slot_n']}) |")
            L.append("")
        if ds == "layer_b":
            L += [f"Nhãn bạc: {d['n_silver']}/{d['n_read']} câu; phân bố {d['silver_label_counts']}.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
