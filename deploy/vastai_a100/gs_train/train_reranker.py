"""Offline reranker (CPU): bge-reranker-v2-m3 fine-tuned on the pair relevance labels (2 / 1 / 0).

    python -u train_reranker.py [--epochs 3] [--folds 5]

Each claim of the pool comes with the passages every retriever put in its top 5 (labelled: 2 = an auditor would cite it,
1 = same subject, 0 = unrelated). Loss: listwise softmax cross-entropy, one relevance-2 passage against up to 7
passages of relevance 0/1 from the same claim. Out-of-company folds; each held-out claim's pooled passages are
re-ordered by the model and scored: nDCG@5 (gain 2^rel - 1), MRR@5 and hit@5 of a relevance-2 passage, against the
lite order (offline product), bm25, and the zero-shot reranker. Writes out/reranker/metrics.json and the final model.
"""
from __future__ import annotations

import argparse
import ast
import math
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Timer, boot_ci, cell, company_folds, jl, log, out_dir, save_json, seed_all  # noqa: E402

BASE = "BAAI/bge-reranker-v2-m3"   # 13/11 11:00: gte remote code crashed twice (CUDA assert); same reranker as the FPT product path
MAX_LEN, NEG = 384, 7


def ndcg5(rels):
    dcg = sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(rels[:5]))
    ideal = sorted(rels, reverse=True)
    idcg = sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(ideal[:5]))
    return dcg / idcg if idcg else None


def mrr5(rels):
    return next((1 / (i + 1) for i, r in enumerate(rels[:5]) if r == 2), 0.0)


def scores_of(groups, order_fn):
    rows = []
    for g in groups:
        order = order_fn(g)
        rels = [p["relevance"] for p in order]
        if max(rels) == 0:
            continue
        rows.append({"company": g["company"], "ndcg5": ndcg5(rels), "mrr5": mrr5(rels),
                     "hit5": float(any(r == 2 for r in rels[:5])) if 2 in rels else None})
    def mean(k):
        def f(rs):
            v = [r[k] for r in rs if r[k] is not None]
            return sum(v) / len(v) if v else 0.0
        return f
    comp = [r["company"] for r in rows]
    return {k: {"mean": round(mean(k)(rows), 4), "ci95": boot_ci(rows, comp, mean(k))} for k in ("ndcg5", "mrr5", "hit5")} | \
        {"claims": len(rows)}


def system_order(name):
    def f(g):
        def rank(p):
            s = p["systems"]
            return s.get(name, 99) if isinstance(s, dict) else 99
        return sorted(g["pairs"], key=lambda p: (rank(p), p["id"]))
    return f


def load_model(path):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
    model = AutoModelForSequenceClassification.from_pretrained(path, trust_remote_code=True, num_labels=1).float().to(dev)
    return model, tok, dev


def score_pairs(model, tok, dev, claim, passages):
    import torch
    with torch.no_grad():
        x = tok([claim] * len(passages), passages, truncation=True, max_length=MAX_LEN, padding=True,
                return_tensors="pt").to(dev)
        x.pop("token_type_ids", None)   # gte: type_vocab_size 1; segment ids of a pair overflow it (device assert)
        return model(**x).logits.view(-1).float().cpu().tolist()


def model_order(model, tok, dev):
    def f(g):
        s = score_pairs(model, tok, dev, g["claim"], [p["passage"] for p in g["pairs"]])
        return [p for _, p in sorted(zip(s, g["pairs"]), key=lambda t: -t[0])]
    return f


def fit(train_groups, epochs, lr, seed, hist, tag):
    import torch
    from transformers import get_linear_schedule_with_warmup
    seed_all(seed)
    model, tok, dev = load_model(BASE)
    model.gradient_checkpointing_enable()
    items = []
    for g in train_groups:
        pos = [p for p in g["pairs"] if p["relevance"] == 2]
        neg = [p for p in g["pairs"] if p["relevance"] < 2]
        for p in pos:
            if neg:
                items.append((g["claim"], p, neg))
    steps = max(1, epochs * len(items))
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    model.train()
    for ep in range(epochs):
        random.shuffle(items)
        tot = 0.0
        for claim, pos, neg in items:
            cand = [pos] + random.sample(neg, min(NEG, len(neg)))
            x = tok([claim] * len(cand), [c["passage"] for c in cand], truncation=True, max_length=MAX_LEN,
                    padding=True, return_tensors="pt").to(dev)
            x.pop("token_type_ids", None)
            with torch.autocast(dev, dtype=torch.float16, enabled=dev == "cuda"):
                z = model(**x).logits.view(1, -1).float()
            loss = torch.nn.functional.cross_entropy(z, torch.zeros(1, dtype=torch.long, device=dev))
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            sch.step()
            tot += loss.item()
        hist.append({"run": tag, "epoch": ep + 1, "loss": round(tot / max(1, len(items)), 4), "items": len(items)})
        log(f"[rerank] {tag} epoch {ep + 1} loss {tot / max(1, len(items)):.4f} ({len(items)} lists)")
    return model.eval(), tok, dev


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--folds", type=int, default=5)
    args = ap.parse_args()
    import torch

    cell("rerank data")
    lab = {x["id"]: x for x in jl("pairs_labels.jsonl")}
    by = defaultdict(list)
    for p in jl("pairs_pool.jsonl"):
        if p["id"] in lab and not p["overlaps_gs_eval"]:
            s = p.get("systems")
            if isinstance(s, str):
                try:
                    s = ast.literal_eval(s)
                except (ValueError, SyntaxError):
                    s = {}
            by[p["claim_id"]].append({**p, "systems": s or {}, "relevance": lab[p["id"]]["relevance"]})
    groups = [{"claim_id": c, "claim": ps[0]["claim"], "company": ps[0]["company_id"], "origin": ps[0]["origin"],
               "pairs": ps} for c, ps in by.items()]
    lib = [g for g in groups if g["origin"] == "lib"]
    log(f"[rerank] claims {len(groups)} (lib {len(lib)}), pairs {sum(len(g['pairs']) for g in groups)}")
    od = out_dir("reranker")
    m, hist = {"claims": len(groups), "lib_claims": len(lib)}, []

    cell("rerank baselines")
    m["lite"] = scores_of(lib, system_order("lite"))
    m["bm25"] = scores_of(lib, system_order("bm25"))
    zs, ztok, zdev = load_model(BASE)
    zs.eval()
    m["zero_shot"] = scores_of(lib, model_order(zs, ztok, zdev))
    del zs
    import gc
    gc.collect()
    torch.cuda.empty_cache()
    log(f"[rerank] lite {m['lite']['ndcg5']} · zero-shot {m['zero_shot']['ndcg5']}")

    cell("rerank cv")
    t = Timer()
    comp = [g["company"] for g in groups]
    fold_scores = []
    for f, (tr, te) in enumerate(company_folds(comp, args.folds)):
        model, tok, dev = fit([groups[i] for i in tr], args.epochs, args.lr, 13, hist, f"fold{f}")
        test = [groups[i] for i in te if groups[i]["origin"] == "lib"]
        order = model_order(model, tok, dev)
        for g in test:
            fold_scores.append({**g, "pairs": order(g)})
        del model, order   # the closure holds the model: drop both or the next fold runs out of memory
        import gc
        gc.collect()
        torch.cuda.empty_cache()
    m["fine_tuned_cv"] = scores_of(fold_scores, lambda g: g["pairs"])
    m["cv_seconds"] = t()
    log(f"[rerank] fine-tuned CV {m['fine_tuned_cv']['ndcg5']}")

    cell("rerank final + cpu latency")
    model, tok, dev = fit(groups, args.epochs, args.lr, 13, hist, "final")
    model.save_pretrained(od / "bge-reranker-final")
    tok.save_pretrained(od / "bge-reranker-final")
    cpu = model.to("cpu")
    torch.set_num_threads(4)
    g = lib[0]
    t0 = time.time()
    score_pairs(cpu, tok, "cpu", g["claim"], [p["passage"] for p in g["pairs"]][:10])
    m["cpu_ms_per_passage_4threads"] = round((time.time() - t0) / min(10, len(g["pairs"])) * 1000, 1)
    save_json(od / "metrics.json", m)
    save_json(od / "history.json", hist)
    log(f"[rerank] cpu {m['cpu_ms_per_passage_4threads']} ms/passage · DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
