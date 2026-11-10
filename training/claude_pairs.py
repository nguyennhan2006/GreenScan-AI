"""Claude labels for the two model choices after T1: evidence retrieval (step 6) and stance (step 7).

One labelled (claim, passage) pair answers both questions:
  relation  SUPPORTS | PARTIAL | CONTRADICTS | CONTEXT   (stance-v1: the product's four relations)
  related   for CONTEXT only: same subject (true) or unrelated (false)
  → relevance 2 (S/P/C: an auditor would cite it for this claim), 1 (CONTEXT, same subject), 0 (unrelated)

Pool (`pool`), built so that every candidate is judged on the same pairs:
  lib   real claim sentences Claude labelled in T1, from the 10 companies whose whole library is in the
        crawl (data/crawl/vn30/normalized/chunks.jsonl) and whose FPT vectors are cached. Each retrieval
        candidate searches the company's library (pages published no later than the claim's report,
        never the claim's own page); the top 5 of every candidate are pooled, so recall@k, MRR@5 and
        nDCG@5 are exact for every candidate, not estimated.
  hpg   (claim, passage) pairs the product itself produced on the HPG run (583ee2e6e6c94501, the
        PDF parser's blocks), stratified by the relation it reached: every CONTRADICTS, a sample of
        the rest, and some pairs the rules decided.
Labelling repeats the T1 r2 discipline: passes A and B blind to each other, `merge` (review list:
disagreement, any CONTRADICTS, confidence 1, a hard-to-read table, a 10% spot sample; blind audit input), an
adjudicator, a blind auditor; a decision the audit contradicts is "contested" and kept out of the
headline numbers.
Candidates (`candidates`): the rules (verifier with the model off; and whether the pair would be
escalated to the model), every FPT model asked with the production prompt (stance-v1, one pair per
call, cached), and an offline NLI model when torch is available.
`report`: step 6 recall@k / MRR@5 / nDCG@5 per retriever; step 7 accuracy, macro-F1, precision of
CONTRADICTS and SUPPORTS per stance candidate; company-cluster bootstrap; each against today's choice;
then every rule in configs/measurement_decisions.yaml (v2, registered before any of this was measured).

usage:
  python training/claude_pairs.py pool [--per-company 5] [--hpg 130]
  python training/claude_pairs.py validate --batch p03 --file out/A_p03.jsonl
  python training/claude_pairs.py merge --batch p03
  python training/claude_pairs.py finalize
  python training/claude_pairs.py candidates [--models GLM-5.2,gemma-4-31B-it] [--workers 6]
  python training/claude_pairs.py report
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import evaluate_gold as ev  # noqa: E402

DIR = ROOT / "training" / "data" / "claude" / "pairs"
CODEBOOK = DIR / "CODEBOOK_CAP.md"
HPG_RUN = ROOT / ".quantum" / "runs" / "583ee2e6e6c94501" / "result.json"
OUT = ROOT / "benchmark" / "model_selection"
RELATIONS = ["SUPPORTS", "PARTIAL", "CONTRADICTS", "CONTEXT"]
FLAGS = ["lap_lai", "khac_ky", "khac_pham_vi", "muc_tieu", "can_tinh", "bang_kho_doc"]
CLAIMS = ("QUANTIFIED_CLAIM", "QUALITATIVE_CLAIM", "VAGUE")
QUOTA = {"QUANTIFIED_CLAIM": 2, "QUALITATIVE_CLAIM": 2, "VAGUE": 1}
LIBRARY_COMPANIES = ["bvh", "ctd", "dhg", "dpr", "pan", "pnj", "pow", "sab", "tra", "vnm"]
# name -> (embedding provider, reranker provider, fusion, lexical weight, semantic weight)
SYSTEMS = {
    "bm25": ("lite", "none", "weighted", 1.0, 0.0),
    "lite": ("lite", "none", "rrf", 0.55, 0.45),              # offline product today
    "dense-vn": ("fpt", "none", "weighted", 0.0, 1.0),        # FPT Vietnamese_Embedding alone
    "hybrid-vn": ("fpt", "none", "rrf", 0.55, 0.45),
    "lite+rerank": ("lite", "fpt", "rrf", 0.55, 0.45),        # FPT bge-reranker-v2-m3
    "hybrid-vn+rerank": ("fpt", "fpt", "rrf", 0.55, 0.45),
}
TODAY_RETRIEVAL = "lite"
TODAY_STANCE = "GLM-5.2"
LLMS = ["GLM-5.2", "gemma-4-31B-it", "gemma-4-26B-A4B-it", "Llama-3.3-70B-Instruct", "Qwen3.6-27B",
        "DeepSeek-V4-Flash"]
NLI_MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
POOL_DEPTH, RANK_DEPTH, BATCH = 5, 10, 80
FIELDS = ("relation", "related", "flag", "confidence", "note")


def _read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()] if path.exists() else []


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def _id(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def relevance(x: dict) -> int:
    if x["relation"] in ("SUPPORTS", "PARTIAL", "CONTRADICTS"):
        return 2
    return 1 if x.get("related") else 0


# ----------------------------------------------------------------------------- pool
def _settings(system: str):
    from quantum_gw.settings import load_settings

    embedding, reranker, fusion, lex, sem = SYSTEMS[system]
    s = load_settings("configs/default.yaml")
    s.verification.llm_stance = "off"
    s.embedding.provider = embedding
    s.reranker.provider = reranker
    s.retrieval.fusion = fusion
    s.retrieval.lexical_weight, s.retrieval.semantic_weight = lex, sem
    s.retrieval.top_k = RANK_DEPTH
    s.retrieval.candidate_k = 30
    s.retrieval.minimum_score = 0.0   # rank everything; a threshold is a separate question
    s.runs_dir = str(ROOT / ".quantum" / "eval_runs")
    return s


def _claims(per_company: int, seed: int) -> list[dict]:
    rows = _read(ROOT / "training" / "data" / "claude" / "claude_train.jsonl") + \
        _read(ROOT / "training" / "data" / "gold_t1" / "ai" / "claude_compare.jsonl")
    by: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        if r["label"] in CLAIMS and r["company_id"] in LIBRARY_COMPANIES and r.get("decided_by") != "contested":
            by[r["company_id"]].append(r)
    rng = random.Random(seed)
    quota = {k: round(v * per_company / sum(QUOTA.values())) for k, v in QUOTA.items()}
    chosen = []
    for company in LIBRARY_COMPANIES:
        rs = sorted(by[company], key=lambda r: r["id"])
        rng.shuffle(rs)
        take = []
        for label, n in quota.items():
            take += [r for r in rs if r["label"] == label][:n]
        rest = [r for r in rs if r not in take]
        take += rest[:max(0, per_company - len(take))]   # a company short of one label gives another
        chosen += take[:per_company]
    return chosen


def _own_page(row: dict, pages: list[dict]) -> dict | None:
    """The library page the claim sentence was cut from: same document, sentence inside the page."""
    head = _norm(row["text"])[:80]
    same_doc = [p for p in pages if p["document_id"] == row["doc"]]
    for p in same_doc:
        if head and head in _norm(p["text"]):
            return p
    words = _norm(row["text"]).split()
    grams = {" ".join(words[i:i + 6]) for i in range(max(1, len(words) - 5))}
    best = max(same_doc, key=lambda p: sum(g in _norm(p["text"]) for g in grams), default=None)
    return best if best and sum(g in _norm(best["text"]) for g in grams) >= max(2, len(grams) // 2) else None


def pool(args) -> int:
    from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
    from quantum_gw.agents.retriever import EvidenceRetrievalAgent
    from quantum_gw.domain.enums import DocumentRole, SourceType
    from quantum_gw.domain.models import EvidenceChunk
    from quantum_gw.retrieval.embeddings import build_embedder
    from quantum_gw.retrieval.rerank import build_reranker

    if (DIR / "pool.jsonl").exists() and not args.force:
        print("pool.jsonl exists (labels may already point at it); --force to rebuild")
        return 1
    claims = _claims(args.per_company, args.seed)
    library = ev._library(set(LIBRARY_COMPANIES))
    year_of = {p["document_id"]: p.get("publication_year") for ps in library.values() for p in ps}
    base = _settings("lite")
    extractor = ClaimExtractionAgent(base.claim_extraction, ev._NullAudit())
    models = {}
    for name in SYSTEMS:
        s = _settings(name)
        emb = build_embedder(s.embedding, strict=True) if s.embedding.provider != "lite" else None
        rr = build_reranker(s.reranker, strict=True) if s.reranker.provider != "none" else None
        models[name] = (s, emb, rr)
    agents, rankings, seconds, pairs = {}, {}, defaultdict(list), {}
    for n, row in enumerate(claims, 1):
        pages = library[row["company_id"]]
        year = year_of.get(row["doc"])
        visible = [p for p in pages if not (year and p.get("publication_year") and p["publication_year"] > year)]
        own = _own_page(row, pages)
        chunk = EvidenceChunk(chunk_id=own["chunk_id"] if own else f"claim:{row['id']}", doc_id=row["doc"],
                              source_name=row["source"], role=DocumentRole.CLAIM_SOURCE,
                              source_type=SourceType.INTERNAL, text=row["text"],
                              page=own.get("unit_index") if own else None)
        claim = extractor.describe(row["text"], chunk)
        by_chunk = {p["chunk_id"]: p for p in visible}
        for name, (s, emb, rr) in models.items():
            key = (name, row["company_id"], year)
            if key not in agents:
                chunks = [EvidenceChunk(chunk_id=p["chunk_id"], doc_id=p["document_id"],
                                        source_name=f"{p['ticker']} {p['document_type']} {p.get('publication_year')}",
                                        role=DocumentRole.EVIDENCE, source_type=SourceType.INTERNAL,
                                        text=p["text"], page=p.get("unit_index")) for p in visible]
                agents[key] = EvidenceRetrievalAgent(chunks, s, ev._NullAudit(), embedder=emb, reranker=rr)
            started = time.perf_counter()
            ranked = [e.chunk_id for e in agents[key].run(claim)][:RANK_DEPTH]
            seconds[name].append(time.perf_counter() - started)
            rankings[(row["id"], name)] = ranked
            for cid in ranked[:POOL_DEPTH]:
                p = by_chunk[cid]
                pid = _id(row["id"], cid)
                pairs.setdefault(pid, {
                    "id": pid, "origin": "lib", "claim_id": row["id"], "company_id": row["company_id"],
                    "claim_label": row["label"], "claim": row["text"], "prev": row.get("prev_text") or "",
                    "next": row.get("next_text") or "", "claim_source": row["source"],
                    "chunk_id": cid, "passage": p["text"],
                    "passage_source": f"{p['ticker']} · {p['document_type']} {p.get('publication_year')} · "
                                      f"trang {p.get('unit_index')}",
                    "own_page_found": own is not None, "systems": {}})
                pairs[pid]["systems"][name] = ranked.index(cid) + 1
        print(f"  {n}/{len(claims)} {row['company_id']} {row['label'][:5]} · pairs so far {len(pairs)}", flush=True)
    hpg = _hpg_pairs(args.hpg, args.seed)
    rows = list(pairs.values()) + hpg
    _write(DIR / "pool.jsonl", rows)
    _write(DIR / "rankings.jsonl", [{"claim_id": c, "system": s, "ranked": r} for (c, s), r in rankings.items()])
    _write(DIR / "pool_timing.jsonl", [{"system": s, "seconds": v} for s, v in seconds.items()])
    _batches(rows, args.seed)
    union = Counter(r["claim_id"] for r in rows if r["origin"] == "lib")
    print(f"pool: {len(claims)} claims · {len(pairs)} library pairs (union of top-{POOL_DEPTH}: "
          f"mean {sum(union.values()) / max(1, len(union)):.1f}/claim) + {len(hpg)} HPG pairs = {len(rows)}")
    print("  own page found:", sum(r["own_page_found"] for r in pairs.values()), "of", len(pairs))
    return 0


def _hpg_pairs(n: int, seed: int) -> list[dict]:
    if n <= 0 or not HPG_RUN.exists():
        return []
    res = json.loads(HPG_RUN.read_text(encoding="utf-8"))
    every = []
    for v in res["verifications"]:
        c = v["claim"]
        for e in v["evidence"]:
            every.append((c, e))
    rng = random.Random(seed)
    rng.shuffle(every)
    contradicts = [x for x in every if x[1]["relation"] == "CONTRADICTS"]
    rules = [x for x in every if x[1]["relation_method"] != "llm" and x not in contradicts]
    llm = [x for x in every if x[1]["relation_method"] == "llm" and x not in contradicts]
    left = n - len(contradicts)
    take = contradicts + rules[:left // 6]
    per = (n - len(take)) // 3
    for rel in ("SUPPORTS", "PARTIAL", "CONTEXT"):
        take += [x for x in llm if x[1]["relation"] == rel][:per]
    out = []
    for c, e in take:
        pid = _id("hpg", c["claim_id"], e["chunk_id"])
        out.append({"id": pid, "origin": "hpg", "claim_id": "hpg:" + c["claim_id"], "company_id": "hpg",
                    "claim_label": c.get("claim_type"), "claim": c["text"], "prev": "", "next": "",
                    "claim_source": f"HPG · {c.get('source_name')} · trang {c.get('source_page')}",
                    "chunk_id": e["chunk_id"], "passage": e["text"],
                    "passage_source": e.get("citation") or e.get("source_name"),
                    "product": {"relation": e["relation"], "method": e["relation_method"]},
                    "claim_obj": c, "systems": {}})
    return out


def _blind(r: dict) -> dict:
    return {"id": r["id"], "tuyen_bo": r["claim"], "cau_truoc": r["prev"], "cau_sau": r["next"],
            "nguon_tuyen_bo": r["claim_source"], "doan": r["passage"], "nguon_doan": r["passage_source"]}


def _batches(rows: list[dict], seed: int) -> None:
    """Pairs of one claim stay together (the claim is read once), in shuffled order within it."""
    rng = random.Random(seed)
    by: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by[r["claim_id"]].append(r)
    keys = sorted(by)
    rng.shuffle(keys)
    batches, cur = [], []
    for k in keys:
        group = sorted(by[k], key=lambda r: r["id"])
        rng.shuffle(group)
        if cur and len(cur) + len(group) > BATCH:
            batches.append(cur)
            cur = []
        cur += group
    if cur:
        batches.append(cur)
    for i, b in enumerate(batches, 1):
        _write(DIR / "batches" / f"p{i:02d}.jsonl", [_blind(r) for r in b])
    print(f"  {len(batches)} batches: {[len(b) for b in batches]}")


# ----------------------------------------------------------------------------- validate / merge
def check(x: dict) -> list[str]:
    e = []
    if x.get("relation") not in RELATIONS:
        return [f"relation {x.get('relation')!r}"]
    if x["relation"] == "CONTEXT" and not isinstance(x.get("related"), bool):
        e.append("related must be true/false when relation is CONTEXT")
    if x["relation"] != "CONTEXT" and x.get("related") is not None:
        e.append("related must be null unless relation is CONTEXT")
    if x.get("flag") not in (None, *FLAGS):
        e.append(f"flag {x.get('flag')!r}")
    if x.get("confidence") not in (1, 2, 3):
        e.append(f"confidence {x.get('confidence')!r}")
    if (x["relation"] == "CONTRADICTS" or x.get("confidence") == 1 or x.get("flag")) \
            and not (x.get("note") or "").strip():
        e.append("note missing")
    return e


def validate(args) -> int:
    path = Path(args.file) if Path(args.file).is_absolute() else DIR / args.file
    source = (Path(args.expect) if Path(args.expect).is_absolute() else DIR / args.expect) if args.expect \
        else DIR / "batches" / f"{args.batch}.jsonl"
    expected = [r["id"] for r in _read(source)]
    if not expected:
        print(f"! no expected rows in {source}")
        return 1
    try:
        got = _read(path)
    except json.JSONDecodeError as e:
        print(f"! {path.name}: not JSON lines ({e})")
        return 1
    problems = [f"line {i} {x.get('id')}: {e}" for i, x in enumerate(got, 1) for e in check(x)]
    ids = [x.get("id") for x in got]
    missing = [i for i in expected if i not in set(ids)]
    extra = [i for i in ids if i not in set(expected)]
    dup = [i for i, n in Counter(ids).items() if n > 1]
    for p in problems[:30]:
        print("  !", p)
    print(f"{path.name}: {len(got)} rows for {len(expected)} expected · schema problems {len(problems)} · "
          f"missing {len(missing)} {missing[:3]} · extra {len(extra)} {extra[:3]} · duplicated {len(dup)} {dup[:3]}")
    return 1 if problems or missing or extra or dup else 0


def _kappa(pairs: list[tuple]) -> float | None:
    if not pairs:
        return None
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0


def merge(args) -> int:
    rows = {r["id"]: r for r in _read(DIR / "batches" / f"{args.batch}.jsonl")}
    A = {x["id"]: x for x in _read(DIR / "out" / f"A_{args.batch}.jsonl")}
    B = {x["id"]: x for x in _read(DIR / "out" / f"B_{args.batch}.jsonl")}
    problems = [f"{p} {x['id']}: {e}" for p, d in (("A", A), ("B", B)) for x in d.values() for e in check(x)]
    missing = [i for i in rows if i not in A or i not in B]
    for p in problems[:30]:
        print("  !", p)
    both = [i for i in rows if i in A and i in B]
    rel = [(A[i]["relation"], B[i]["relation"]) for i in both]
    grade = [(relevance(A[i]), relevance(B[i])) for i in both if not check(A[i]) and not check(B[i])]
    print(f"[{args.batch}] A {len(A)} · B {len(B)} · both {len(both)}/{len(rows)} · schema problems {len(problems)}")
    print(f"  κ A–B quan hệ {_kappa(rel)} · độ liên quan {_kappa(grade)} · "
          f"đồng ý quan hệ {sum(a == b for a, b in rel)}/{len(rel)}")
    rng = random.Random(args.seed + int(args.batch[1:]))
    review = []
    for i in both:
        a, b = A[i], B[i]
        why = []
        if a["relation"] != b["relation"]:
            why.append("quan hệ khác")
        elif a["relation"] == "CONTEXT" and a.get("related") != b.get("related"):
            why.append("độ liên quan khác")
        if "CONTRADICTS" in (a["relation"], b["relation"]):
            why.append("có CONTRADICTS")
        if 1 in (a.get("confidence"), b.get("confidence")):
            why.append("không chắc")
        if "bang_kho_doc" in (a.get("flag"), b.get("flag")):   # other flags classify; this one doubts
            why.append("bảng khó đọc")
        if not why and rng.random() < args.spot:
            why.append("soát ngẫu nhiên")
        if why:
            review.append({**rows[i], "why": why, "A": {k: a.get(k) for k in FIELDS}, "B": {k: b.get(k) for k in FIELDS}})
    _write(DIR / "review" / f"{args.batch}.jsonl", review)
    audit = [rows[x["id"]] for x in review]
    rng.shuffle(audit)
    _write(DIR / "audit" / f"{args.batch}_in.jsonl", audit)
    print(f"  cần đọc lại: {len(review)} · {dict(Counter(w for x in review for w in x['why']))} "
          f"-> review/{args.batch}.jsonl + audit/{args.batch}_in.jsonl")
    return 1 if missing or problems else 0


# ----------------------------------------------------------------------------- finalize
def finalize(args) -> int:
    pool_rows = {r["id"]: r for r in _read(DIR / "pool.jsonl")}
    out, open_, unaudited = [], [], []
    for bf in sorted((DIR / "batches").glob("p*.jsonl")):
        b = bf.stem
        A = {x["id"]: x for x in _read(DIR / "out" / f"A_{b}.jsonl")}
        B = {x["id"]: x for x in _read(DIR / "out" / f"B_{b}.jsonl")}
        review = {x["id"]: x for x in _read(DIR / "review" / f"{b}.jsonl")}
        decided = {x["id"]: x for x in _read(DIR / "adj" / f"{b}.jsonl")}
        audit = {x["id"]: x for x in _read(DIR / "audit" / f"{b}_out.jsonl")}
        if not (A and B):
            print(f"  {b}: passes missing, skipped")
            continue
        open_ += sorted(set(review) - set(decided))
        unaudited += sorted(set(review) - set(audit))
        for r in _read(bf):
            i = r["id"]
            a, bb = A.get(i), B.get(i)
            if not (a and bb):
                continue
            if i in decided:
                final, how = decided[i], "adjudicated"
                if i in audit and (audit[i]["relation"] != final["relation"] or relevance(audit[i]) != relevance(final)):
                    how = "contested"
            elif a["relation"] == bb["relation"] and relevance(a) == relevance(bb):
                final, how = a, "agree"
            else:
                continue
            p = pool_rows[i]
            out.append({"id": i, "batch": b, "origin": p["origin"], "claim_id": p["claim_id"],
                        "company_id": p["company_id"], **{k: final.get(k) for k in FIELDS},
                        "relevance": relevance(final), "pass_a": a["relation"], "pass_b": bb["relation"],
                        "decided_by": how, "audit_relation": audit[i]["relation"] if i in audit else None})
    if open_ or (unaudited and not args.audit_optional):
        print(f"  ! {len(open_)} review rows without a decision, {len(unaudited)} without a blind audit")
        if not args.force:
            return 1
    _write(DIR / "labels.jsonl", out)
    print(f"labels: {len(out)} -> {(DIR / 'labels.jsonl').relative_to(ROOT)} · "
          f"{dict(Counter(x['decided_by'] for x in out))} · quan hệ {dict(Counter(x['relation'] for x in out))} · "
          f"độ liên quan {dict(Counter(x['relevance'] for x in out))}")
    aud = [x for x in out if x["audit_relation"]]
    if aud:
        print(f"  soát mù khớp quyết định: {sum(x['audit_relation'] == x['relation'] for x in aud)}/{len(aud)}")
    return 0


# ----------------------------------------------------------------------------- candidates
def _claim_obj(p: dict, extractor):
    from quantum_gw.domain.enums import DocumentRole, SourceType
    from quantum_gw.domain.models import Claim, EvidenceChunk

    if p["origin"] == "hpg":
        return Claim.model_validate(p["claim_obj"])
    chunk = EvidenceChunk(chunk_id=f"claim:{p['claim_id']}", doc_id="", source_name=p["claim_source"],
                          role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL, text=p["claim"])
    return extractor.describe(p["claim"], chunk)


def _evidence_obj(p: dict):
    from quantum_gw.domain.enums import SourceType
    from quantum_gw.domain.models import RetrievedEvidence

    return RetrievedEvidence(chunk_id=p["chunk_id"], doc_id=p["chunk_id"].split(":")[0],
                             source_name=p["passage_source"], source_type=SourceType.INTERNAL,
                             text=p["passage"], score=0.5, citation=p["passage_source"])


def _rules(pool_rows: list[dict]) -> list[dict]:
    """The verifier with the model off, pair by pair; and whether the model would have been asked."""
    from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
    from quantum_gw.agents.verifier import VerificationAgent, _RecordingJudge

    off = _settings("lite")
    on = _settings("lite")
    on.verification.llm_stance = "on_ambiguous"
    extractor = ClaimExtractionAgent(off.claim_extraction, ev._NullAudit())
    v_off = VerificationAgent(off.verification, ev._NullAudit())
    v_on = VerificationAgent(on.verification, ev._NullAudit())
    out = []
    for p in pool_rows:
        claim = _claim_obj(p, extractor)
        item = v_off.run(claim, [_evidence_obj(p)]).evidence
        recorder = _RecordingJudge()
        v_on._llm_judge = recorder
        v_on.run(claim, [_evidence_obj(p)])
        out.append({"id": p["id"], "relation": item[0].relation if item else "CONTEXT",
                    "method": item[0].relation_method if item else "none", "escalated": bool(recorder.asked)})
    return out


def _ask(provider, claim_text: str, evidence_text: str) -> dict:
    from quantum_gw.verification.llm_judge import RESPONSE_SCHEMA, SYSTEM_PROMPT

    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"TUYÊN BỐ:\n{claim_text}\n\nĐOẠN BẰNG CHỨNG:\n{evidence_text}"}]
    started, err = time.perf_counter(), ""
    for attempt in range(3):
        try:
            resp = provider.generate(messages, response_schema=RESPONSE_SCHEMA)
            parsed = resp.parsed or {}
            rel = str(parsed.get("relation", "")).strip().upper()
            return {"relation": rel if rel in RELATIONS else "?", "reason": str(parsed.get("reason", ""))[:300],
                    "seconds": round(time.perf_counter() - started, 2), "usage": resp.usage}
        except Exception as exc:  # noqa: BLE001
            err = repr(exc)[:200]
            time.sleep(3 * (attempt + 1))
    return {"relation": "?", "reason": "ERROR " + err, "seconds": round(time.perf_counter() - started, 2)}


def _production_cache() -> dict[str, dict]:
    path = ROOT / ".quantum" / "llm_cache" / "stance_cache.jsonl"
    return {x["key"]: x for x in _read(path)}


def candidates(args) -> int:
    pool_rows = _read(DIR / "pool.jsonl")
    if not pool_rows:
        print("no pool.jsonl; run pool first")
        return 1
    cdir = DIR / "candidates"
    cdir.mkdir(parents=True, exist_ok=True)
    if "rules" in args.models:
        rows = _rules(pool_rows)
        _write(cdir / "rules.jsonl", rows)
        print(f"rules: {dict(Counter(r['relation'] for r in rows))} · escalated {sum(r['escalated'] for r in rows)}")
    llms = [m for m in args.models if m in LLMS or m.startswith("fpt:")]
    if llms:
        from quantum_gw.providers.router import ModelGateway
        from quantum_gw.verification.llm_judge import PROMPT_VERSION

        fpt = ModelGateway()._provider("fpt")
        cache = _production_cache()
    for model in llms:
        model = model.removeprefix("fpt:")
        path = cdir / f"{model}.jsonl"
        done = {x["id"]: x for x in _read(path) if x["relation"] != "?"}
        todo = [p for p in pool_rows if p["id"] not in done]
        reused = 0
        if model == "GLM-5.2":   # the product already asked GLM some of these, with this exact prompt
            for p in list(todo):
                key = hashlib.sha256(json.dumps([PROMPT_VERSION, "fpt:GLM-5.2", p["claim"], p["passage"]],
                                                ensure_ascii=False).encode("utf-8")).hexdigest()
                if key in cache:
                    done[p["id"]] = {"id": p["id"], "relation": cache[key]["relation"],
                                     "reason": cache[key].get("reason", "")[:300], "seconds": None, "cached": True}
                    todo.remove(p)
                    reused += 1
        if args.cache_only:
            todo = []
        provider = fpt.bind_model(model)
        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            answers = list(ex.map(lambda p: _ask(provider, p["claim"], p["passage"]), todo))
        for p, a in zip(todo, answers):
            done[p["id"]] = {"id": p["id"], **a}
        _write(path, [done[p["id"]] for p in pool_rows if p["id"] in done])
        bad = sum(done[p["id"]]["relation"] == "?" for p in pool_rows if p["id"] in done)
        print(f"{model}: asked {len(todo)} in {time.perf_counter() - started:.0f}s · reused {reused} · "
              f"unparsed/errors {bad} · {dict(Counter(x['relation'] for x in done.values()))}", flush=True)
    if "nli" in args.models:
        _nli(pool_rows, cdir)
    return 0


def _nli(pool_rows: list[dict], cdir: Path) -> None:
    """Offline candidate: multilingual NLI, zero-shot. entailment → SUPPORTS, contradiction → CONTRADICTS."""
    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError as exc:
        print(f"nli: skipped ({exc})")
        return
    tok = AutoTokenizer.from_pretrained(NLI_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(NLI_MODEL).eval()
    names = [model.config.id2label[i].lower() for i in range(model.config.num_labels)]
    out, started = [], time.perf_counter()
    for p in pool_rows:
        enc = tok(p["passage"], p["claim"], truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            prob = torch.softmax(model(**enc).logits[0], -1).tolist()
        top = names[max(range(len(prob)), key=prob.__getitem__)]
        rel = {"entailment": "SUPPORTS", "contradiction": "CONTRADICTS"}.get(top, "CONTEXT")
        out.append({"id": p["id"], "relation": rel, "probs": dict(zip(names, [round(x, 3) for x in prob]))})
    _write(cdir / "nli-mdeberta.jsonl", out)
    print(f"nli: {len(out)} pairs in {time.perf_counter() - started:.0f}s · {dict(Counter(x['relation'] for x in out))}")


# ----------------------------------------------------------------------------- report
def _f1(gold: list[str], pred: list[str], labels: list[str]) -> dict:
    per = {}
    for k in labels:
        tp = sum(g == k and p == k for g, p in zip(gold, pred))
        fp = sum(g != k and p == k for g, p in zip(gold, pred))
        fn = sum(g == k and p != k for g, p in zip(gold, pred))
        prec = tp / (tp + fp) if tp + fp else None
        rec = tp / (tp + fn) if tp + fn else None
        f1 = 2 * prec * rec / (prec + rec) if prec and rec else 0.0
        per[k] = {"precision": None if prec is None else round(prec, 3), "recall": None if rec is None else round(rec, 3),
                  "f1": round(f1, 3), "predicted": tp + fp, "true": tp + fn}
    present = [k for k in labels if per[k]["true"] or per[k]["predicted"]]
    return {"macro_f1": round(sum(per[k]["f1"] for k in present) / len(present), 4) if present else None,
            "accuracy": round(sum(g == p for g, p in zip(gold, pred)) / len(gold), 4) if gold else None,
            "per_class": per, "n": len(gold)}


def _boot_metric(items: list[tuple], groups: list[str], fn, samples: int = 1000) -> list[float] | None:
    clusters = defaultdict(list)
    for g, it in zip(groups, items):
        clusters[g].append(it)
    names = sorted(clusters)
    if len(names) < 3:
        return None
    rng = random.Random(0)
    vals = []
    for _ in range(samples):
        drawn = [x for _ in names for x in clusters[rng.choice(names)]]
        v = fn(drawn)
        if v is not None:
            vals.append(v)
    vals.sort()
    return [round(vals[int(0.025 * len(vals))], 4), round(vals[int(0.975 * len(vals)) - 1], 4)] if vals else None


def report(args) -> int:
    pool_rows = {r["id"]: r for r in _read(DIR / "pool.jsonl")}
    labels = {x["id"]: x for x in _read(DIR / "labels.jsonl")}
    if not labels:
        print("no labels.jsonl; finalize first")
        return 1
    headline = {i: x for i, x in labels.items() if x["decided_by"] != "contested"}
    result = {"labels": len(labels), "contested": len(labels) - len(headline),
              "labels_by": dict(Counter(x["decided_by"] for x in labels.values())),
              "note": "Nhãn Claude (2 lượt mù + phân xử + soát mù), chưa phải gold người."}

    # step 6 ---------------------------------------------------------------- retrieval
    grade = defaultdict(dict)
    for i, x in headline.items():
        p = pool_rows[i]
        if p["origin"] == "lib":
            grade[p["claim_id"]][p["chunk_id"]] = x["relevance"]
    rankings = defaultdict(dict)
    for r in _read(DIR / "rankings.jsonl"):
        rankings[r["claim_id"]][r["system"]] = r["ranked"]
    company = {p["claim_id"]: p["company_id"] for p in pool_rows.values()}
    timing = {r["system"]: r["seconds"] for r in _read(DIR / "pool_timing.jsonl")}
    per_claim = defaultdict(dict)
    for cid, systems in rankings.items():
        g = grade.get(cid, {})
        relevant = {c for c, v in g.items() if v == 2}
        ideal = sorted(g.values(), reverse=True)[:POOL_DEPTH]
        idcg = sum((2 ** v - 1) / math.log2(k + 2) for k, v in enumerate(ideal))
        for name, ranked in systems.items():
            top = ranked[:POOL_DEPTH]
            first = next((k for k, c in enumerate(top, 1) if g.get(c) == 2), None)
            per_claim[cid][name] = {
                "has_evidence": bool(relevant),
                **{f"recall@{k}": (sum(c in relevant for c in top[:k]) / len(relevant)) if relevant else None
                   for k in (1, 3, 5)},
                "hit@5": 1.0 if first else 0.0, "mrr@5": 1.0 / first if first else 0.0,
                "ndcg@5": (sum((2 ** g.get(c, 0) - 1) / math.log2(k + 2) for k, c in enumerate(top)) / idcg) if idcg else None,
            }
    retr = {}
    claims = sorted(per_claim)
    for name in SYSTEMS:
        block = {"seconds_per_claim": round(sum(timing.get(name, [0])) / max(1, len(timing.get(name, [1]))), 3)}
        for m in ("recall@1", "recall@3", "recall@5", "hit@5", "mrr@5", "ndcg@5"):
            vals = [(per_claim[c][name][m], company[c]) for c in claims if name in per_claim[c] and per_claim[c][name][m] is not None]
            if not vals:
                continue
            block[m] = ev._cluster_mean_ci([v for v, _ in vals], [g for _, g in vals])
            if name != TODAY_RETRIEVAL:
                both = [(per_claim[c][name][m], per_claim[c][TODAY_RETRIEVAL][m], company[c]) for c in claims
                        if per_claim[c].get(name, {}).get(m) is not None and per_claim[c].get(TODAY_RETRIEVAL, {}).get(m) is not None]
                block[f"delta_vs_{TODAY_RETRIEVAL}:{m}"] = ev._cluster_mean_ci([a - b for a, b, _ in both], [g for *_, g in both])
        retr[name] = block
    result["retrieval"] = {"claims": len(claims), "claims_with_evidence": sum(
        1 for c in claims if per_claim[c].get(TODAY_RETRIEVAL, {}).get("has_evidence")), "systems": retr}

    # step 7 ---------------------------------------------------------------- stance
    cands = {f.stem: {x["id"]: x for x in _read(f)} for f in sorted((DIR / "candidates").glob("*.jsonl"))}
    stance = {}
    subsets = {
        "all": lambda i: True,
        "relevant": lambda i: headline[i]["relevance"] >= 1,
        "hpg_production": lambda i: pool_rows[i]["origin"] == "hpg",
        "escalated_by_rules": lambda i: cands.get("rules", {}).get(i, {}).get("escalated", False),
    }
    for name, answers in cands.items():
        block = {}
        for sname, keep in subsets.items():
            ids = [i for i in headline if i in answers and keep(i)]
            if not ids:
                continue
            gold = [headline[i]["relation"] for i in ids]
            pred = [answers[i]["relation"] if answers[i]["relation"] in RELATIONS else "CONTEXT" for i in ids]
            m = _f1(gold, pred, RELATIONS)
            groups = [pool_rows[i]["company_id"] for i in ids]
            items = list(zip(gold, pred))
            m["macro_f1_ci95"] = _boot_metric(items, groups, lambda d: _f1([g for g, _ in d], [p for _, p in d], RELATIONS)["macro_f1"])
            m["false_contradicts_per_100"] = round(100 * sum(p == "CONTRADICTS" and g != "CONTRADICTS" for g, p in items) / len(items), 2)
            m["unparsed"] = sum(answers[i]["relation"] not in RELATIONS for i in ids)
            secs = [answers[i].get("seconds") for i in ids if answers[i].get("seconds")]
            m["seconds_per_pair"] = round(sum(secs) / len(secs), 2) if secs else None
            if name != TODAY_STANCE and TODAY_STANCE in cands:
                both = [i for i in ids if i in cands[TODAY_STANCE]
                        and cands[TODAY_STANCE][i]["relation"] in RELATIONS]
                norm = lambda r: r if r in RELATIONS else "CONTEXT"  # noqa: E731
                trip = [(headline[i]["relation"], norm(answers[i]["relation"]), cands[TODAY_STANCE][i]["relation"]) for i in both]
                mf = lambda d: _f1([g for g, _, _ in d], [x for _, x, _ in d], RELATIONS)["macro_f1"] -                     _f1([g for g, _, _ in d], [t for _, _, t in d], RELATIONS)["macro_f1"]  # noqa: E731
                if trip:
                    m[f"delta_macro_f1_vs_{TODAY_STANCE}"] = {
                        "mean": round(mf(trip), 4), "n": len(trip),
                        "ci95": _boot_metric(trip, [pool_rows[i]["company_id"] for i in both], mf)}
                ok = lambda ans, i: 1.0 if (ans[i]["relation"] if ans[i]["relation"] in RELATIONS else "CONTEXT") == headline[i]["relation"] else 0.0  # noqa: E731
                m[f"delta_accuracy_vs_{TODAY_STANCE}"] = ev._cluster_mean_ci(
                    [ok(answers, i) - ok(cands[TODAY_STANCE], i) for i in both], [pool_rows[i]["company_id"] for i in both])
            block[sname] = m
        stance[name] = block
    result["stance"] = stance
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "stage67_report.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {(OUT / 'stage67_report.json').relative_to(ROOT)}")
    for name, b in retr.items():
        print(f"  ⑥ {name:18s} recall@5 {b.get('recall@5', {}).get('mean')} {b.get('recall@5', {}).get('ci95')} · "
              f"MRR@5 {b.get('mrr@5', {}).get('mean')} · nDCG@5 {b.get('ndcg@5', {}).get('mean')} · {b['seconds_per_claim']} s")
    for name, b in stance.items():
        a = b.get("all", {})
        c = a.get("per_class", {}).get("CONTRADICTS", {})
        s = a.get("per_class", {}).get("SUPPORTS", {})
        print(f"  ⑦ {name:24s} acc {a.get('accuracy')} · macro-F1 {a.get('macro_f1')} {a.get('macro_f1_ci95')} · "
              f"P(C) {c.get('precision')} ({c.get('predicted')}) · P(S) {s.get('precision')} ({s.get('predicted')}) · "
              f"C sai/100 {a.get('false_contradicts_per_100')}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pool")
    p.add_argument("--per-company", type=int, default=5)
    p.add_argument("--hpg", type=int, default=130)
    p.add_argument("--seed", type=int, default=16)
    p.add_argument("--force", action="store_true")
    v = sub.add_parser("validate")
    v.add_argument("--batch")
    v.add_argument("--expect")
    v.add_argument("--file", required=True)
    m = sub.add_parser("merge")
    m.add_argument("--batch", required=True)
    m.add_argument("--spot", type=float, default=0.10)
    m.add_argument("--seed", type=int, default=16)
    f = sub.add_parser("finalize")
    f.add_argument("--force", action="store_true")
    f.add_argument("--audit-optional", action="store_true")
    c = sub.add_parser("candidates")
    c.add_argument("--models", default="rules," + ",".join(LLMS) + ",nli",
                   type=lambda s: [x.strip() for x in s.split(",") if x.strip()])
    c.add_argument("--workers", type=int, default=6)
    c.add_argument("--cache-only", action="store_true", help="only answers the product already cached (FPT down)")
    sub.add_parser("report")
    args = ap.parse_args()
    if args.cmd == "validate" and not (args.batch or args.expect):
        ap.error("validate needs --batch or --expect")
    return {"pool": pool, "validate": validate, "merge": merge, "finalize": finalize,
            "candidates": candidates, "report": report}[args.cmd](args)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
