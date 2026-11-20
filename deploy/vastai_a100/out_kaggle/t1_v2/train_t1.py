"""T1 claim detector (offline product, CPU): multilingual-e5 sequence classifier, 4 classes, numbers masked.

    python -u train_t1.py [--models e5-small,e5-base] [--losses ce,wce] [--folds 5]

Labels: t1_train.jsonl (Claude, codebook v1.1 + Q13 v1.2 relabel). Sentences overlapping GS-Eval (first 60 normalised
characters) are removed. Two losses:
  ce   plain cross-entropy (the 11/11 recipe of s1_final.py)
  wce  class-weighted cross-entropy (weights ∝ 1/sqrt(frequency)) + label smoothing 0.05
Reported: out-of-company 5-fold CV (macro-F1, claim recall), then a fit on all rows (2 seeds, probabilities averaged)
scored on the registered S1 test: among GS-Eval sentences the product extracts, NOT_A_CLAIM caught and true claims
wrongly flagged, for thresholds 0.5..0.95. Writes out/t1/metrics.json, out/t1/history.json, out/t1/<model>-<loss>-final/.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Timer, cell, company_folds, confusion, jl, log, norm60, out_dir, prf, save_json, seed_all  # noqa: E402

LABELS = ["NOT_CLAIM", "QUALITATIVE_CLAIM", "QUANTIFIED_CLAIM", "VAGUE"]
L2I = {l: i for i, l in enumerate(LABELS)}
MODELS = {"e5-small": "intfloat/multilingual-e5-small", "e5-base": "intfloat/multilingual-e5-base"}
HP = {"e5-small": dict(lr=5e-5, epochs=6), "e5-base": dict(lr=3e-5, epochs=6)}
MAX_LEN, BATCH, SEEDS = 160, 16, [13, 29]
THRESHOLDS = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]


def fit(key, loss_kind, texts, labels, seed, hist=None, tag=""):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup
    seed_all(seed)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(MODELS[key])
    model = AutoModelForSequenceClassification.from_pretrained(
        MODELS[key], num_labels=4, id2label=dict(enumerate(LABELS)), label2id=L2I).float().to(dev)
    hp = HP[key]
    y = [L2I[l] for l in labels]
    if loss_kind == "wce":
        cnt = Counter(y)
        w = torch.tensor([1 / math.sqrt(cnt.get(i, 1)) for i in range(4)], dtype=torch.float, device=dev)
        lossf = torch.nn.CrossEntropyLoss(weight=w * 4 / w.sum(), label_smoothing=0.05)
    else:
        lossf = torch.nn.CrossEntropyLoss()
    steps = hp["epochs"] * math.ceil(len(texts) / BATCH)
    opt = torch.optim.AdamW(model.parameters(), lr=hp["lr"], weight_decay=0.01)
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    scaler = torch.amp.GradScaler(enabled=dev == "cuda")
    import random
    model.train()
    for ep in range(hp["epochs"]):
        order = list(range(len(texts)))
        random.shuffle(order)
        tot, n = 0.0, 0
        for i in range(0, len(order), BATCH):
            b = order[i:i + BATCH]
            x = tok(["query: " + texts[j] for j in b], truncation=True, max_length=MAX_LEN, padding=True,
                    return_tensors="pt").to(dev)
            with torch.autocast(dev, dtype=torch.float16, enabled=dev == "cuda"):
                loss = lossf(model(**x).logits.float(), torch.tensor([y[j] for j in b], device=dev))
            opt.zero_grad()
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            sch.step()
            tot, n = tot + loss.item() * len(b), n + len(b)
        if hist is not None:
            hist.append({"run": tag, "epoch": ep + 1, "loss": round(tot / n, 4)})
        log(f"[t1] {tag} epoch {ep + 1} loss {tot / n:.4f}")
    return model.eval(), tok


def probs(model, tok, texts):
    import torch
    dev = next(model.parameters()).device
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), 64):
            x = tok(["query: " + t for t in texts[i:i + 64]], truncation=True, max_length=MAX_LEN, padding=True,
                    return_tensors="pt").to(dev)
            out += torch.softmax(model(**x).logits.float(), -1).cpu().tolist()
    return out


def gate(ev, p_not):
    """S1 gate (llm_stages_v1): among extracted GS-Eval sentences, NOT_A_CLAIM caught / true claims flagged."""
    rows = [(r["is_claim"], p) for r, p in zip(ev, p_not) if r.get("extracted") and r.get("is_claim") is not None]
    out = {}
    for t in THRESHOLDS:
        out[str(t)] = {"not_claim_caught": sum((not c) and p >= t for c, p in rows),
                       "not_claim_total": sum(not c for c, _ in rows),
                       "true_claims_flagged": sum(c and p >= t for c, p in rows),
                       "true_claims_total": sum(c for c, _ in rows)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="e5-small,e5-base")
    ap.add_argument("--losses", default="ce,wce")
    ap.add_argument("--folds", type=int, default=5)
    args = ap.parse_args()
    import numpy as np
    import torch

    cell("t1 data")
    train = jl("t1_train.jsonl")
    ev = jl("s1_eval.jsonl")
    if os.environ.get("LIMIT"):
        train = train[: int(os.environ["LIMIT"])]
    held = {r["norm60"] for r in ev}
    kept = [r for r in train if norm60(r["text"]) not in held and r["label"] in L2I]
    log(f"[t1] train {len(train)} -> {len(kept)} after GS-Eval overlap; labels {dict(Counter(r['label'] for r in kept))}; "
        f"q13 relabelled {sum(r['q13_relabelled'] for r in kept)}, changed {sum(r['label'] != r['label_v11'] for r in kept)}")
    texts = [r["text_masked"] for r in kept]
    labels = [r["label"] for r in kept]
    groups = [r["company_id"] for r in kept]
    od = out_dir("t1")
    metrics = {"train_rows": len(kept), "label_counts": dict(Counter(labels)), "runs": {}}
    hist = []
    for key in args.models.split(","):
        for lk in args.losses.split(","):
            name = f"{key}-{lk}"
            cell(f"t1 cv {name}")
            t = Timer()
            oof = [None] * len(kept)
            for f, (tr, te) in enumerate(company_folds(groups, args.folds)):
                model, tok = fit(key, lk, [texts[i] for i in tr], [labels[i] for i in tr], SEEDS[0], hist, f"{name}-fold{f}")
                for i, p in zip(te, probs(model, tok, [texts[i] for i in te])):
                    oof[i] = p
                del model
                torch.cuda.empty_cache()
            pred = [LABELS[int(np.argmax(p))] for p in oof]
            cv = prf(labels, pred, LABELS)
            is_c = [l != "NOT_CLAIM" for l in labels]
            cv["claim_recall"] = round(sum(c and p != "NOT_CLAIM" for c, p in zip(is_c, pred)) / max(1, sum(is_c)), 4)
            cv["confusion"] = confusion(labels, pred, LABELS)
            cell(f"t1 final {name}")
            acc = None
            for s in SEEDS:
                model, tok = fit(key, lk, texts, labels, s, hist, f"{name}-final-s{s}")
                p = np.array(probs(model, tok, [r["text_masked"] for r in ev]))
                acc = p if acc is None else acc + p
                if s == SEEDS[0]:
                    model.save_pretrained(od / f"{name}-final")
                    tok.save_pretrained(od / f"{name}-final")
                    import time
                    cpu = model.to("cpu")
                    torch.set_num_threads(4)
                    t0 = time.time()
                    probs(cpu, tok, [r["text_masked"] for r in ev[:64]])
                    cpu_ms = round((time.time() - t0) / 64 * 1000, 1)
                del model
                torch.cuda.empty_cache()
            acc /= len(SEEDS)
            with open(od / f"s1_{name}.jsonl", "w", encoding="utf-8") as fh:   # per sentence, for error analysis
                for r, pr in zip(ev, acc.tolist()):
                    fh.write(json.dumps({"id": r["id"], "company": r.get("company"), "is_claim": r.get("is_claim"),
                                         "extracted": r.get("extracted"), "text_masked": r["text_masked"],
                                         "probs": dict(zip(LABELS, [round(x, 4) for x in pr]))}, ensure_ascii=False) + "\n")
            metrics["runs"][name] = {"cv": cv, "s1_gate": gate(ev, acc[:, 0].tolist()), "seconds": t(),
                                     "cpu_ms_per_sentence_4threads": cpu_ms}
            log(f"[t1] {name}: CV macro-F1 {cv['macro_f1']} claim recall {cv['claim_recall']} · gate@0.5 "
                f"{metrics['runs'][name]['s1_gate']['0.5']} · {t()} s")
            save_json(od / "metrics.json", metrics)
            save_json(od / "history.json", hist)
    log("[t1] DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
