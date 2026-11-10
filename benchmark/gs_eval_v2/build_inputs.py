"""Build the input items for GS-Eval v2 (explain / edit / score / rules).

Deterministic (seeded). Reads only local files:
  - .quantum/runs/*/result.json   -> pool A: claims with retrieved evidence and system outputs
  - training/data/claude/claude_train.jsonl -> pool B: claim sentences from 20+ companies (T1 labels)

Writes (benchmark/gs_eval_v2/):
  inputs/pool_a.jsonl              every unique claim of pool A (latest run wins)
  inputs/system_outputs.jsonl      system verdict, rationale, risk components per pool-A item (hidden from labelers)
  {explain,edit,score}/batches/*.jsonl   4 batches x 50 items, labeler-facing (no system outputs)
  rules/claims_pool.jsonl          300 real claim sentences for rule test cases
  inputs/stats.json

Run: .venv/Scripts/python.exe -I benchmark/gs_eval_v2/build_inputs.py
"""
from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RNG = random.Random(20261104)
BATCH = 50
# Synthetic documents written by pytest / smoke runs, not company disclosures.
TEST_FIXTURES = {"claim.txt", "esg.txt", "company_esg_2024.txt", "a.txt", "t"}


def norm(t: str) -> str:
    return re.sub(r"\s+", " ", t or "").strip().casefold()


def _crawl_names() -> dict[str, tuple[str, str]]:
    """Crawl object file name -> (ticker, readable source name)."""
    out: dict[str, tuple[str, str]] = {}
    p = ROOT / "data/crawl/vn30/contract/raw.jsonl"
    if p.exists():
        for line in p.open(encoding="utf-8"):
            r = json.loads(line)
            if r.get("object_path"):
                name = Path(r["object_path"]).name
                label = f"{r.get('ticker')} · {r.get('document_type')} {r.get('reporting_year') or ''}".strip()
                out[name] = (str(r.get("ticker") or "UNK").upper(), label)
    return out


CRAWL = _crawl_names()


def company_of(source_name: str) -> str:
    s = (source_name or "").strip()
    if s in CRAWL:
        return CRAWL[s][0]
    m = re.match(r"([A-Za-z]{2,5})[_\- ]", s)
    return m.group(1).upper() if m else (s[:20] or "UNKNOWN")


def readable(source_name: str) -> str:
    s = (source_name or "").strip()
    return CRAWL[s][1] if s in CRAWL else s


def jl_write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def compact_evidence(ev: list[dict], k: int = 3, cap: int = 900) -> list[dict]:
    out = []
    for e in ev[:k]:
        txt = re.sub(r"\s+", " ", e.get("text") or "").strip()
        out.append({
            "chunk_id": e.get("chunk_id"),
            "source_name": readable(e.get("source_name")),
            "source_type": e.get("source_type"),
            "page": e.get("page") if e.get("page") is not None else e.get("source_page"),
            "text": txt[:cap] + (" …" if len(txt) > cap else ""),
        })
    return out


def claim_view(c: dict) -> dict:
    return {
        "text": re.sub(r"\s+", " ", c.get("text") or "").strip(),
        "source_name": readable(c.get("source_name")),
        "source_page": c.get("source_page"),
    }


def system_claim_attrs(c: dict) -> dict:
    keys = ("claim_type", "metric", "direction", "values", "units", "period", "baseline", "scope",
            "is_future_commitment", "is_vague", "vague_terms_matched", "language")
    return {k: c.get(k) for k in keys}


def compact_cv(cv: dict | None) -> dict:
    cv = cv or {}
    return {k: cv.get(k) for k in ("matched", "contradiction", "closest_pair", "tolerance_used", "policy_id")}


def load_pool_a() -> tuple[list[dict], dict]:
    best: dict[str, tuple[str, dict, dict | None, str]] = {}
    for rdir in sorted((ROOT / ".quantum" / "runs").iterdir()):
        f = rdir / "result.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        man = d.get("manifest") or {}
        stamp = str(man.get("created_at") or man.get("started_at") or "") or f"{f.stat().st_mtime:.0f}"
        risks = {r["claim_id"]: r for r in d.get("risks", [])}
        for v in d.get("verifications", []):
            t = v["claim"].get("text") or ""
            if not (30 <= len(t) <= 700):
                continue
            if (v["claim"].get("source_name") or "").strip() in TEST_FIXTURES:
                continue
            key = norm(t)
            if key not in best or stamp > best[key][0]:
                best[key] = (stamp, v, risks.get(v["claim"]["claim_id"]), rdir.name)
    items, sysout = [], {}
    for key, (stamp, v, risk, run_id) in best.items():
        c = v["claim"]
        iid = "A-" + c["claim_id"]
        proxy = ("quantified" if c.get("values") else "vague" if c.get("is_vague") else "qualitative")
        items.append({
            "item_id": iid,
            "company": company_of(c.get("source_name")),
            "claim": claim_view(c),
            "evidence": compact_evidence(v.get("evidence") or []),
            "_status": v.get("status"),
            "_proxy": proxy,
        })
        sysout[iid] = {
            "item_id": iid,
            "run_id": run_id,
            "system_status": v.get("status"),
            "system_rationale": v.get("rationale"),
            "system_warnings": v.get("warnings"),
            "computed": compact_cv(v.get("computed_values")),
            "claim_attrs": system_claim_attrs(c),
            "risk": None if risk is None else {
                "risk_score": risk.get("risk_score"),
                "severity": risk.get("severity"),
                "severity_cap_reason": risk.get("severity_cap_reason"),
                "components": [{"name": x["name"], "score": x["score"], "max_score": x["max_score"]}
                               for x in risk.get("components", [])],
            },
        }
    return items, sysout


def round_robin(items: list[dict], n: int, key: str = "company") -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        groups[it[key]].append(it)
    for g in groups.values():
        RNG.shuffle(g)
    order = sorted(groups, key=lambda k: (-len(groups[k]), k))
    out: list[dict] = []
    while len(out) < n and any(groups.values()):
        for k in order:
            if groups[k] and len(out) < n:
                out.append(groups[k].pop())
    return out


TARGETS = {"SUPPORTED": 45, "CONTRADICTED": 50, "INSUFFICIENT_EVIDENCE": 50, "PARTIALLY_SUPPORTED": 55}


def capped_round_robin(items: list[dict], n: int, cap_frac: float = 0.25, avoid: str | None = None) -> list[dict]:
    """Round-robin over companies with a per-company cap; relax the cap only if the stratum runs dry."""
    cap = max(2, int(n * cap_frac + 0.999))
    while True:
        groups: dict[str, list[dict]] = defaultdict(list)
        for it in items:
            groups[it["company"]].append(it)
        for g in groups.values():
            RNG.shuffle(g)
        order = sorted(groups, key=lambda k: (k == avoid, -len(groups[k]), k))
        out: list[dict] = []
        taken: Counter = Counter()
        progress = True
        while len(out) < n and progress:
            progress = False
            for k in order:
                if groups[k] and taken[k] < cap and len(out) < n:
                    out.append(groups[k].pop())
                    taken[k] += 1
                    progress = True
        if len(out) >= n or cap >= n:
            return out
        cap += 2


def balanced_set(pool: list[dict], prefer_not: set[str]) -> list[dict]:
    out: list[dict] = []
    for status, n in TARGETS.items():
        cand = [x for x in pool if x["_status"] == status]
        fresh = [x for x in cand if x["item_id"] not in prefer_not]
        if status == "PARTIALLY_SUPPORTED":  # plentiful: disjoint, HPG last and capped hard
            out += capped_round_robin(fresh, n, cap_frac=0.12, avoid="HPG")
            continue
        pick = capped_round_robin(fresh, min(n, len(fresh)), cap_frac=0.4)
        if len(pick) < n:  # rare stratum: reuse items of the other set
            rest = [x for x in cand if x not in pick]
            pick += capped_round_robin(rest, n - len(pick), cap_frac=0.4)
        out += pick
    return out


def split_stratified(pool: list[dict], caps: dict[str, int], n: int, used: set[str]) -> list[dict]:
    chosen: list[dict] = []
    for status, cap in caps.items():
        cand = [x for x in pool if x["_status"] == status and x["item_id"] not in used]
        chosen += round_robin(cand, cap)
    rest = [x for x in pool if x["item_id"] not in used and x not in chosen and x["_status"] == "PARTIALLY_SUPPORTED"]
    chosen += round_robin(rest, n - len(chosen))
    return chosen[:n]


def batches(name: str, rows: list[dict]) -> list[str]:
    RNG.shuffle(rows)
    paths = []
    for i in range(0, len(rows), BATCH):
        p = OUT / name / "batches" / f"{name}_b{i // BATCH + 1:02d}.jsonl"
        jl_write(p, rows[i:i + BATCH])
        paths.append(str(p.relative_to(ROOT)))
    return paths


def main() -> None:
    pool_a, sysout = load_pool_a()
    st = Counter(x["_status"] for x in pool_a)
    co = Counter(x["company"] for x in pool_a)

    # Balanced strata on the system decision (user 04/11: "độ lệch nhẹ và vẫn cân bằng").
    # The pool has only 45 SUPPORTED (42 HPG) and 74 INSUFFICIENT, so explain and score share
    # the rare strata; PARTIALLY is disjoint and mostly non-HPG to even out companies.
    explain = balanced_set(pool_a, set())
    score = balanced_set(pool_a, {x["item_id"] for x in explain})
    used = {x["item_id"] for x in explain} | {x["item_id"] for x in score}

    # Edit set: 100 pool-A claims (not in explain/score) balanced on the proxy claim class
    # (quantified / qualitative / vague) + 100 pool-B sentences balanced on the T1 label.
    edit_a = []
    for proxy, n in (("quantified", 34), ("qualitative", 33), ("vague", 33)):
        edit_a += capped_round_robin([x for x in pool_a if x["item_id"] not in used and x["_proxy"] == proxy], n, cap_frac=0.2)
    used |= {x["item_id"] for x in edit_a}
    t1 = [json.loads(l) for l in (ROOT / "training/data/claude/claude_train.jsonl").open(encoding="utf-8")]
    t1 = [r for r in t1 if r.get("label") in ("QUANTIFIED_CLAIM", "QUALITATIVE_CLAIM", "VAGUE")
          and 30 <= len(r.get("text") or "") <= 700]
    seen = set()
    pool_b = []
    for r in t1:
        k = norm(r["text"])
        if k in seen:
            continue
        seen.add(k)
        pool_b.append({
            "item_id": "B-" + r["id"],
            "company": (r.get("company_id") or "unk").upper(),
            "claim": {"text": re.sub(r"\s+", " ", r["text"]).strip(), "source_name": r.get("source"),
                      "source_page": None, "prev_text": (r.get("prev_text") or "")[:400],
                      "next_text": (r.get("next_text") or "")[:400]},
            "evidence": [],
            "_t1_label": r["label"],
        })
    edit_b = []
    for lab, n in (("QUANTIFIED_CLAIM", 33), ("QUALITATIVE_CLAIM", 34), ("VAGUE", 33)):
        edit_b += capped_round_robin([x for x in pool_b if x["_t1_label"] == lab], n, cap_frac=0.15)
    edit_b_ids = {x["item_id"] for x in edit_b}
    rules_pool = round_robin([x for x in pool_b if x["item_id"] not in edit_b_ids], 240)
    rules_pool += round_robin([x for x in pool_a if x["item_id"] not in used], 60)

    def public(x: dict) -> dict:  # labeler-facing view: no system outputs, no T1 label
        return {k: v for k, v in x.items() if not k.startswith("_")}

    paths = {
        "explain": batches("explain", [public(x) for x in explain]),
        "score": batches("score", [public(x) for x in score]),
        "edit": batches("edit", [public(x) for x in edit_a + edit_b]),
    }
    rules_file = OUT / "rules" / "claims_pool.jsonl"
    if not rules_file.exists():  # frozen once written: rule cases cite these item_ids
        jl_write(rules_file, [public(x) for x in rules_pool])
    jl_write(OUT / "inputs" / "pool_a.jsonl", [public(x) | {"system_status": x["_status"]} for x in pool_a])
    frozen_rules = [json.loads(l)["item_id"] for l in rules_file.open(encoding="utf-8")]
    wanted = {x["item_id"] for x in explain + score + edit_a if x["item_id"].startswith("A-")}
    wanted |= {i for i in frozen_rules if i.startswith("A-") and i in sysout}
    jl_write(OUT / "inputs" / "system_outputs.jsonl", [sysout[i] for i in sorted(wanted)])
    stats = {
        "pool_a_unique_claims": len(pool_a),
        "pool_a_status": dict(st),
        "pool_a_companies": dict(co),
        "pool_b_claims": len(pool_b),
        "explain_status": dict(Counter(x["_status"] for x in explain)),
        "score_status": dict(Counter(x["_status"] for x in score)),
        "explain_companies": dict(Counter(x["company"] for x in explain)),
        "score_companies": dict(Counter(x["company"] for x in score)),
        "explain_score_overlap": len({x["item_id"] for x in explain} & {x["item_id"] for x in score}),
        "edit_sources": {"pool_a": len(edit_a), "pool_b": len(edit_b),
                         "pool_a_proxy": dict(Counter(x["_proxy"] for x in edit_a)),
                         "pool_b_t1": dict(Counter(x["_t1_label"] for x in edit_b)),
                         "companies": dict(Counter(x["company"] for x in edit_a + edit_b))},
        "rules_pool": len(rules_pool),
        "batches": paths,
        "seed": 20261104,
    }
    (OUT / "inputs").mkdir(parents=True, exist_ok=True)
    (OUT / "inputs" / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({k: v for k, v in stats.items() if k != "batches"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
