"""prompt_router_v1 gate (CPU): multilingual-e5-small with 8 sigmoid outputs (out + 7 tasks), BCE loss.

    python -u train_router_gate.py [--epochs 5]

Train on router_train, choose the thresholds on router_dev: tau_out is the largest value whose dev OOS recall is still
>= 0.98 (a request stops when P(out) >= tau_out or no task reaches 0.3), then score router_test once with
router_metrics.score. Writes out/router_gate/metrics.json, history.json and the model (gate-final).
"""
from __future__ import annotations

import argparse
import math
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import cell, jl, log, out_dir, save_json, seed_all  # noqa: E402
from router_metrics import TASKS, score  # noqa: E402

BASE = "intfloat/multilingual-e5-small"
OUTS = ["out"] + TASKS
MAX_LEN, BATCH, TASK_MIN = 192, 32, 0.3


def target(r):
    return [0.0 if r["in_scope"] else 1.0] + [1.0 if t in (r.get("tasks") or []) else 0.0 for t in TASKS]


def probs(model, tok, texts, dev):
    import torch
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), 64):
            x = tok(["query: " + t for t in texts[i:i + 64]], truncation=True, max_length=MAX_LEN, padding=True,
                    return_tensors="pt").to(dev)
            out += torch.sigmoid(model(**x).logits.float()).cpu().tolist()
    return out


def to_pred(p, tau_out):
    if p[0] >= tau_out or max(p[1:]) < TASK_MIN:
        return {"in_scope": False, "tasks": [], "slots": {}}
    return {"in_scope": True, "tasks": [t for t, v in zip(TASKS, p[1:]) if v >= TASK_MIN],
            "slots": {"claim": "x"}}   # the gate does not extract slots: need_info is the planner's / rules' call


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--lr", type=float, default=5e-5)
    a = ap.parse_args()
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup
    seed_all(13)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    cell("router gate data")
    tr, dv, te = jl("router_train.jsonl"), jl("router_dev.jsonl"), jl("router_test.jsonl")
    log(f"[gate] train {len(tr)} dev {len(dv)} test {len(te)}")
    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForSequenceClassification.from_pretrained(BASE, num_labels=len(OUTS),
                                                               problem_type="multi_label_classification").float().to(dev)
    steps = a.epochs * math.ceil(len(tr) / BATCH)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    lossf = torch.nn.BCEWithLogitsLoss()
    hist = []
    cell("router gate train")
    for ep in range(a.epochs):
        model.train()
        random.shuffle(tr)
        tot = 0.0
        for i in range(0, len(tr), BATCH):
            b = tr[i:i + BATCH]
            x = tok(["query: " + r["request"] for r in b], truncation=True, max_length=MAX_LEN, padding=True,
                    return_tensors="pt").to(dev)
            loss = lossf(model(**x).logits.float(), torch.tensor([target(r) for r in b], device=dev))
            opt.zero_grad()
            loss.backward()
            opt.step()
            sch.step()
            tot += loss.item() * len(b)
        model.eval()
        pd = probs(model, tok, [r["request"] for r in dv], dev)
        dl = -sum(sum(t * math.log(max(p, 1e-7)) + (1 - t) * math.log(max(1 - p, 1e-7)) for t, p in zip(target(r), q)) / len(OUTS)
                  for r, q in zip(dv, pd)) / max(1, len(dv))
        hist.append({"run": "final", "epoch": ep + 1, "loss": round(tot / len(tr), 4), "dev_loss": round(dl, 4)})
        log(f"[gate] epoch {ep + 1} loss {tot / len(tr):.4f} dev {dl:.4f}")
    cell("router gate thresholds + test")
    pd = probs(model, tok, [r["request"] for r in dv], dev)
    cands = sorted({round(x / 100, 2) for x in range(5, 96)}, reverse=True)
    tau = next((t for t in cands if score(dv, [to_pred(p, t) for p in pd])["oos_recall"] >= 0.98), 0.05)
    pt = probs(model, tok, [r["request"] for r in te], dev)
    m = {"tau_out": tau, "task_min": TASK_MIN, "dev": score(dv, [to_pred(p, tau) for p in pd]),
         "test": score(te, [to_pred(p, tau) for p in pt]), "test_at_0.5": score(te, [to_pred(p, 0.5) for p in pt])}
    od = out_dir("router_gate")
    model.save_pretrained(od / "gate-final")
    tok.save_pretrained(od / "gate-final")
    cpu = model.to("cpu")
    torch.set_num_threads(4)
    t0 = time.time()
    probs(cpu, tok, [r["request"] for r in te[:64]], "cpu")
    m["cpu_ms_per_request_4threads"] = round((time.time() - t0) / 64 * 1000, 1)
    save_json(od / "metrics.json", m)
    save_json(od / "history.json", hist)
    t = m["test"]
    log(f"[gate] tau {tau} · test OOS recall {t['oos_recall']} {t['oos_recall_ci95']} · false refusal {t['false_refusal']} "
        f"· task macro-F1 {t['task_macro_f1']} · cpu {m['cpu_ms_per_request_4threads']} ms · DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
