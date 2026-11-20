"""S1 of llm_stages_v1: final T1 claim detectors for the product, and their reading of the GS-Eval sentences.

    python -u s1_final.py            (Kaggle T4; inputs in /kaggle/input/gs-llm-stages-v1 and /kaggle/input/greenscan-t1-data)

Recipe = training/kaggle/t1_kaggle.py (HP e5-small / e5-base, MAX_LEN 160, batch 16, masked text, "query: " prefix),
trained on every T1 training sentence EXCEPT those whose first 60 normalised characters match a GS-Eval sentence
(registration llm_stages_v1: 16 overlap). Two seeds per model, probabilities averaged.
Writes out/s1_<model>.jsonl ({id, probs, label}) for the 200 GS-Eval sentences and out/<model>-final/ (weights +
tokenizer, seed 13) for the product (src/quantum_gw/agents/claim_model.py).
"""
import json
import os
import random
import re
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

LABELS = ["NOT_CLAIM", "QUALITATIVE_CLAIM", "QUANTIFIED_CLAIM", "VAGUE"]
L2I = {l: i for i, l in enumerate(LABELS)}
MODELS = {"e5-small": "intfloat/multilingual-e5-small", "e5-base": "intfloat/multilingual-e5-base"}
HP = {"e5-small": dict(lr=5e-5, epochs=6), "e5-base": dict(lr=3e-5, epochs=6)}
MAX_LEN, BATCH, SEEDS = 160, 16, [13, 29]
DEV = "cuda" if torch.cuda.is_available() else "cpu"


def find(name):
    for p in Path("/kaggle/input").rglob(name):
        return p
    return Path(name)


def norm(s):
    return re.sub(r"\s+", " ", s.lower()).strip()


def enc(tok, texts):
    return tok(["query: " + t for t in texts], truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt")


def fit(key, rows, seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    tok = AutoTokenizer.from_pretrained(MODELS[key])
    model = AutoModelForSequenceClassification.from_pretrained(
        MODELS[key], num_labels=len(LABELS), id2label=dict(enumerate(LABELS)), label2id=L2I).to(DEV)
    hp = HP[key]
    steps = hp["epochs"] * ((len(rows) + BATCH - 1) // BATCH)
    opt = torch.optim.AdamW(model.parameters(), lr=hp["lr"], weight_decay=0.01)
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    scaler = torch.amp.GradScaler(enabled=DEV == "cuda")
    model.train()
    for ep in range(hp["epochs"]):
        order = list(range(len(rows)))
        random.shuffle(order)
        total = 0.0
        for i in range(0, len(order), BATCH):
            b = [rows[j] for j in order[i:i + BATCH]]
            x = {k: v.to(DEV) for k, v in enc(tok, [r["text_masked"] for r in b]).items()}
            y = torch.tensor([L2I[r["label"]] for r in b], device=DEV)
            with torch.autocast(DEV, enabled=DEV == "cuda"):
                loss = model(**x, labels=y).loss
            opt.zero_grad(); scaler.scale(loss).backward(); scaler.step(opt); scaler.update(); sch.step()
            total += loss.item()
        print(f"[s1] {key} seed {seed} epoch {ep + 1}/{hp['epochs']} loss {total:.2f}", flush=True)
    return model.eval(), tok


@torch.no_grad()
def probs(model, tok, texts):
    out = []
    for i in range(0, len(texts), 64):
        x = {k: v.to(DEV) for k, v in enc(tok, texts[i:i + 64]).items()}
        out += torch.softmax(model(**x).logits.float(), -1).cpu().tolist()
    return out


def main():
    print("[cell] s1 load data", flush=True)
    train = [json.loads(x) for x in open(find("train.jsonl"), encoding="utf-8")]
    ev = [json.loads(x) for x in open(find("s1_eval.jsonl"), encoding="utf-8")]
    if os.environ.get("LIMIT"):
        train = train[: int(os.environ["LIMIT"])]
    held = {r["norm60"] for r in ev}
    kept = [r for r in train if norm(r["text"])[:60] not in held and r.get("label") in L2I]
    print(f"[s1] train {len(train)} -> {len(kept)} after removing GS-Eval overlap; eval {len(ev)}", flush=True)
    Path("out").mkdir(exist_ok=True)
    summary = {"train_rows": len(kept), "removed_overlap": len(train) - len(kept), "models": {}}
    for key in MODELS:
        t0, acc = time.time(), None
        for seed in SEEDS:
            model, tok = fit(key, kept, seed)
            p = np.array(probs(model, tok, [r["text_masked"] for r in ev]))
            acc = p if acc is None else acc + p
            if seed == SEEDS[0]:
                model.save_pretrained(f"out/{key}-final"); tok.save_pretrained(f"out/{key}-final")
            del model
            torch.cuda.empty_cache()
        acc /= len(SEEDS)
        with open(f"out/s1_{key}.jsonl", "w", encoding="utf-8") as fh:
            for r, pr in zip(ev, acc.tolist()):
                fh.write(json.dumps({"id": r["id"], "probs": dict(zip(LABELS, [round(x, 4) for x in pr])),
                                     "label": LABELS[int(np.argmax(pr))]}) + "\n")
        summary["models"][key] = {"seconds": round(time.time() - t0)}
        print(f"[s1] {key} done in {time.time() - t0:.0f}s", flush=True)
    json.dump(summary, open("out/s1_summary.json", "w"))
    print("[s1] SUMMARY", json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
