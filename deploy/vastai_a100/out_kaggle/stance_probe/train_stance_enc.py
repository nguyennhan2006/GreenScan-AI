"""Offline stance model (CPU): mDeBERTa-v3-base-xnli fine-tuned as a 4-relation cross-encoder (claim, passage).

    python -u train_stance_enc.py [--epochs 4] [--folds 5]

Labels: pairs_labels.jsonl (Claude A/B + adjudication, CAP v1.0). Pairs whose claim overlaps GS-Eval are dropped so S5
stays an external test. Loss: class-weighted cross-entropy (∝ 1/sqrt(frequency)); temperature fitted on out-of-fold
logits. A relation the labels never contain (CONTRADICTS is almost absent) is never predicted alone: the model abstains
to CONTEXT unless P(CONTRADICTS) >= 0.9.
Reported (out/stance/metrics.json): out-of-company CV on the pairs (macro-F1, per class, confusion, risk-coverage),
baselines on the same pairs (rules, zero-shot NLI), S5 external test (macro-F1 over S and O, PARTIAL counted as S,
false C per 100) against the rules, CPU ms per pair. Model of the final fit: out/stance/mdeberta-stance-final/.
"""
from __future__ import annotations

import argparse
import math
import random
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (Timer, boot_ci, cell, company_folds, confusion, has, jl, log, out_dir, prf,  # noqa: E402
                    save_json, seed_all)

BASE = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
LABELS = ["SUPPORTS", "PARTIAL", "CONTRADICTS", "CONTEXT"]
L2I = {l: i for i, l in enumerate(LABELS)}
MAX_LEN, BATCH = 384, 16
TO_SCO = {"SUPPORTS": "S", "PARTIAL": "S", "CONTRADICTS": "C", "CONTEXT": "O",
          "entailment": "S", "neutral": "O", "contradiction": "C"}
# --nli-head: keep the checkpoint's NLI head (id 0 entailment, 1 neutral, 2 contradiction) instead of a new 4-way head
NLI_LABELS = ["entailment", "neutral", "contradiction"]
NLI_MAP = {"SUPPORTS": "entailment", "PARTIAL": "entailment", "CONTEXT": "neutral", "CONTRADICTS": "contradiction"}
C_LABEL, O_LABEL = "CONTRADICTS", "CONTEXT"


def encode(tok, claims, passages, dev):
    return tok(claims, passages, truncation="only_second", max_length=MAX_LEN, padding=True, return_tensors="pt").to(dev)


PROBE = False   # --probe: freeze the encoder, train only the classification head (linear probe)


def fit(rows, epochs, lr, seed, hist, tag):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup
    seed_all(seed)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE, num_labels=len(LABELS), id2label=dict(enumerate(LABELS)), label2id=L2I, ignore_mismatched_sizes=True).float().to(dev)
    cnt = Counter(L2I[r["relation"]] for r in rows)
    w = torch.tensor([1 / math.sqrt(cnt[i]) if cnt.get(i) else 0.0 for i in range(len(LABELS))], device=dev)
    lossf = torch.nn.CrossEntropyLoss(weight=w * (sum(1 for x in w if x > 0)) / w.sum())
    if PROBE:
        for name, prm in model.named_parameters():
            prm.requires_grad = name.startswith(("classifier", "pooler"))
    steps = epochs * math.ceil(len(rows) / BATCH)
    if epochs == 0:   # zero-shot: the checkpoint as it is
        return model.eval(), tok
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=lr, weight_decay=0.01)
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    scaler = torch.amp.GradScaler(enabled=dev == "cuda")
    model.train()
    for ep in range(epochs):
        order = list(range(len(rows)))
        random.shuffle(order)
        tot = 0.0
        for i in range(0, len(order), BATCH):
            b = [rows[j] for j in order[i:i + BATCH]]
            x = encode(tok, [r["claim"] for r in b], [r["passage"] for r in b], dev)
            y = torch.tensor([L2I[r["relation"]] for r in b], device=dev)
            with torch.autocast(dev, dtype=torch.float16, enabled=dev == "cuda"):
                loss = lossf(model(**x).logits.float(), y)
            opt.zero_grad()
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(opt)
            scaler.update()
            sch.step()
            tot += loss.item() * len(b)
        hist.append({"run": tag, "epoch": ep + 1, "loss": round(tot / len(rows), 4)})
        log(f"[stance] {tag} epoch {ep + 1} loss {tot / len(rows):.4f}")
    return model.eval(), tok


def logits(model, tok, claims, passages):
    import torch
    dev = next(model.parameters()).device
    out = []
    with torch.no_grad():
        for i in range(0, len(claims), 32):
            x = encode(tok, claims[i:i + 32], passages[i:i + 32], dev)
            out += model(**x).logits.float().cpu().tolist()
    return out


def softmax(z, t=1.0):
    m = max(z)
    e = [math.exp((v - m) / t) for v in z]
    s = sum(e)
    return [v / s for v in e]


def decide(p, c_min=0.9):
    i = max(range(len(LABELS)), key=lambda k: p[k])
    if LABELS[i] == C_LABEL and p[i] < c_min:
        return O_LABEL
    return LABELS[i]


def fit_temperature(z, y):
    best = (1e9, 1.0)
    for t in [0.5 + 0.1 * k for k in range(46)]:
        nll = -sum(math.log(max(softmax(zi, t)[yi], 1e-12)) for zi, yi in zip(z, y)) / len(y)
        best = min(best, (nll, t))
    return round(best[1], 2), round(best[0], 4)


def risk_coverage(p, gold):
    """Accuracy of the most confident fraction, for coverage 10% .. 100%."""
    order = sorted(range(len(p)), key=lambda i: -max(p[i]))
    out = []
    for c in range(1, 11):
        k = max(1, round(len(order) * c / 10))
        sel = order[:k]
        out.append({"coverage": c / 10, "accuracy": round(sum(decide(p[i]) == gold[i] for i in sel) / k, 4),
                    "min_conf": round(max(p[sel[-1]]), 4)})
    return out


def sco_scores(gold, pred, groups):
    def mf(items):
        g, p = [a for a, _ in items], [b for _, b in items]
        r = prf(g, p, ["S", "O"])
        return r["macro_f1"]
    items = list(zip(gold, pred))
    return {"macro_f1_SO": round(mf(items), 4), "ci95": boot_ci(items, groups, mf),
            "false_C": sum(p == "C" and g != "C" for g, p in items), "C_found": sum(p == "C" and g == "C" for g, p in items),
            "C_gold": sum(g == "C" for g in gold), "false_C_per_100": round(100 * sum(p == "C" and g != "C" for g, p in items) / len(items), 2),
            "n": len(items), "report": prf(gold, pred, ["S", "C", "O"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=4)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--nli-head", action="store_true")
    ap.add_argument("--max-len", type=int, default=384)
    ap.add_argument("--name", default="stance")
    ap.add_argument("--probe", action="store_true")
    args = ap.parse_args()
    import torch
    global LABELS, L2I, C_LABEL, O_LABEL, MAX_LEN, PROBE
    MAX_LEN, PROBE = args.max_len, args.probe
    if args.nli_head:
        LABELS, C_LABEL, O_LABEL = NLI_LABELS, "contradiction", "neutral"
        L2I = {l: i for i, l in enumerate(LABELS)}

    cell("stance data")
    pool = {r["id"]: r for r in jl("pairs_pool.jsonl")}
    labels = jl("pairs_labels.jsonl")
    rel = (lambda r: NLI_MAP[r]) if args.nli_head else (lambda r: r)
    rows = [{**pool[x["id"]], "relation": rel(x["relation"])} for x in labels
            if x["id"] in pool and not pool[x["id"]]["overlaps_gs_eval"] and x.get("decided_by") != "contested"]
    groups = [r["company_id"] for r in rows]
    log(f"[stance] {len(rows)} labelled pairs · {dict(Counter(r['relation'] for r in rows))} · companies {len(set(groups))}")
    od = out_dir(args.name)
    hist, m = [], {"n": len(rows), "relations": dict(Counter(r["relation"] for r in rows))}

    cell("stance cv")
    t = Timer()
    oof = [None] * len(rows)
    for f, (tr, te) in enumerate(company_folds(groups, args.folds)):
        model, tok = fit([rows[i] for i in tr], args.epochs, args.lr, 13, hist, f"fold{f}")
        for i, z in zip(te, logits(model, tok, [rows[i]["claim"] for i in te], [rows[i]["passage"] for i in te])):
            oof[i] = z
        del model
        torch.cuda.empty_cache()
    gold = [r["relation"] for r in rows]
    temp, nll = fit_temperature(oof, [L2I[g] for g in gold])
    probs = [softmax(z, temp) for z in oof]
    pred = [decide(p) for p in probs]
    m["cv"] = {**prf(gold, pred, LABELS), "confusion": confusion(gold, pred, LABELS), "labels": LABELS,
               "temperature": temp, "nll": nll, "risk_coverage": risk_coverage(probs, gold), "seconds": t(),
               "ci95_macro_f1": boot_ci(list(zip(gold, pred)), groups,
                                        lambda it: prf([a for a, _ in it], [b for _, b in it], LABELS)["macro_f1"])}
    base = {}
    for name in ("rules", "nli-mdeberta"):
        if has(f"pairs_cand_{name}.jsonl"):
            cand = {c["id"]: c["relation"] for c in jl(f"pairs_cand_{name}.jsonl")}
            bp = [rel(cand.get(r["id"], "CONTEXT")) for r in rows]
            base[name] = {**prf(gold, bp, LABELS), "confusion": confusion(gold, bp, LABELS)}
    m["cv_baselines"] = base
    log(f"[stance] CV macro-F1 {m['cv']['macro_f1']} (T={temp}) · baselines "
        f"{ {k: v['macro_f1'] for k, v in base.items()} }")

    cell("stance final + S5")
    model, tok = fit(rows, args.epochs, args.lr, 13, hist, "final")
    model.save_pretrained(od / "mdeberta-stance-final")
    tok.save_pretrained(od / "mdeberta-stance-final")
    s5 = jl("s5_pairs.jsonl")
    z = logits(model, tok, [r["claim"] for r in s5], [r["evidence"] for r in s5])
    pm = [TO_SCO[decide(softmax(v, temp))] for v in z]
    pr = [TO_SCO.get(r.get("rules") or "CONTEXT", "O") for r in s5]
    g5 = [r["gold"] for r in s5]
    c5 = [r["company"] for r in s5]
    m["s5"] = {"model": sco_scores(g5, pm, c5), "rules": sco_scores(g5, pr, c5)}
    log(f"[stance] S5 model {m['s5']['model']['macro_f1_SO']} {m['s5']['model']['ci95']} false C "
        f"{m['s5']['model']['false_C']} · rules {m['s5']['rules']['macro_f1_SO']} false C {m['s5']['rules']['false_C']}")

    cell("stance cpu latency")
    cpu = model.to("cpu")
    torch.set_num_threads(4)
    t0 = time.time()
    logits(cpu, tok, [r["claim"] for r in s5[:48]], [r["evidence"] for r in s5[:48]])
    m["cpu_ms_per_pair_4threads"] = round((time.time() - t0) / 48 * 1000, 1)
    m["max_len"], m["nli_head"] = MAX_LEN, args.nli_head
    try:   # dynamic int8 (Linear layers): speed and agreement with fp32 on the same 48 pairs
        q = torch.quantization.quantize_dynamic(cpu, {torch.nn.Linear}, dtype=torch.qint8)
        c48, e48 = [r["claim"] for r in s5[:48]], [r["evidence"] for r in s5[:48]]
        z32 = logits(cpu, tok, c48, e48)
        t0 = time.time()
        z8 = logits(q, tok, c48, e48)
        m["cpu_ms_per_pair_int8"] = round((time.time() - t0) / 48 * 1000, 1)
        m["int8_same_argmax"] = round(sum(max(range(len(a)), key=a.__getitem__) == max(range(len(b)), key=b.__getitem__)
                                          for a, b in zip(z32, z8)) / 48, 3)
    except Exception as e:   # noqa: BLE001
        m["int8_error"] = str(e)[:200]
    save_json(od / "metrics.json", m)
    save_json(od / "history.json", hist)
    log(f"[stance] cpu {m['cpu_ms_per_pair_4threads']} ms/pair · DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
