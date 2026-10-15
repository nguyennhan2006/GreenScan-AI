"""Fine-tune a small encoder as a sentence or sentence-pair classifier.

Students planned (training/README.md):
  T1 claim detector   text  → QUANTIFIED_CLAIM / QUALITATIVE_CLAIM / VAGUE / NOT_CLAIM
  T2 quantity aligner (claim slot, evidence slot) → SAME / DIFFERENT   (pair input)

Splits are by company (a company never appears in two splits): the crawl's
own `split` field is used when it says train/dev/test, otherwise companies are
hashed into train/dev/test. Reported on dev and test: accuracy, macro-F1,
per-class precision/recall/F1 and the confusion matrix. Never evaluate a
student only against teacher labels — pass --gold for human labels when they
exist (training/README.md §4).

Runs on CPU for a smoke test (tiny model, few examples) and on a Colab/Kaggle
T4 for real training (fp16). Needs: torch, transformers, datasets, accelerate,
scikit-learn (training/requirements-train.txt) — kept out of the product venv.

usage:
  python training/train_classifier.py --data training/data/teacher_claim_gemma-4-31B-it.jsonl \
      --label-field teacher_label --model microsoft/mdeberta-v3-base --out training/runs/t1_mdeberta
  python training/train_classifier.py --data … --text-field text --pair-field evidence_text …   (T2)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def company_split(company: str, ratios=(0.7, 0.15, 0.15)) -> str:
    h = int(hashlib.sha1((company or "?").encode()).hexdigest(), 16) % 1000 / 1000
    return "train" if h < ratios[0] else "dev" if h < ratios[0] + ratios[1] else "test"


def load(args):
    rows = [json.loads(l) for l in open(args.data, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if r.get(args.label_field) not in (None, "")]
    if args.exclude:
        # sentences people labelled for dev/test must not be trained on, even with a teacher label
        held = {line.strip() for line in open(args.exclude, encoding="utf-8") if line.strip()}
        rows = [r for r in rows if r.get("id") not in held]
    for r in rows:
        given = r.get("split")
        r["_split"] = given if given in {"train", "dev", "test"} and not args.rehash else company_split(str(r.get("company_id")))
    if args.limit:
        random.Random(args.seed).shuffle(rows)
        per = {s: [r for r in rows if r["_split"] == s] for s in ("train", "dev", "test")}
        cap = {"train": args.limit, "dev": max(1, args.limit // 4), "test": max(1, args.limit // 4)}
        rows = [r for s in per for r in per[s][: cap[s]]]
    return rows


def metrics(y_true, y_pred, labels):
    from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support
    p, r, f, n = precision_recall_fscore_support(y_true, y_pred, labels=list(range(len(labels))), zero_division=0)
    return {
        "n": len(y_true),
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, average="macro", labels=list(range(len(labels))), zero_division=0),
        "per_class": {lab: {"precision": float(p[i]), "recall": float(r[i]), "f1": float(f[i]), "support": int(n[i])}
                      for i, lab in enumerate(labels)},
        "confusion": confusion_matrix(y_true, y_pred, labels=list(range(len(labels)))).tolist(),
        "majority_baseline": max(Counter(y_true).values()) / len(y_true) if y_true else 0.0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True)
    ap.add_argument("--label-field", default="teacher_label")
    ap.add_argument("--text-field", default="text")
    ap.add_argument("--pair-field", default=None, help="second text for pair classification (T2)")
    ap.add_argument("--model", default="intfloat/multilingual-e5-small")
    ap.add_argument("--out", default=str(ROOT / "training/runs/smoke"))
    ap.add_argument("--epochs", type=float, default=3)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=160)
    ap.add_argument("--limit", type=int, default=0, help="cap train rows (dev/test = limit/4) — smoke tests")
    ap.add_argument("--rehash", action="store_true", help="ignore the data's split field, hash companies")
    ap.add_argument("--exclude", help="file of sentence ids to drop (training/data/gold_t1/exclude_from_training.txt)")
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--fp16", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    import numpy as np
    import torch
    from datasets import Dataset
    from transformers import (AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding,
                              Trainer, TrainingArguments, set_seed)

    set_seed(args.seed)
    rows = load(args)
    labels = sorted({r[args.label_field] for r in rows}, key=str)
    lab2id = {l: i for i, l in enumerate(labels)}
    by = {s: [r for r in rows if r["_split"] == s] for s in ("train", "dev", "test")}
    print({s: len(v) for s, v in by.items()}, "labels", dict(Counter(r[args.label_field] for r in rows)))
    if not by["train"] or not by["dev"]:
        raise SystemExit("need train and dev rows — add data or use --rehash")

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model, num_labels=len(labels), id2label={i: str(l) for l, i in lab2id.items()},
        label2id={str(l): i for l, i in lab2id.items()})

    def encode(split):
        ds = Dataset.from_list([{"a": r[args.text_field], "b": r.get(args.pair_field) if args.pair_field else None,
                                 "label": lab2id[r[args.label_field]]} for r in by[split]])
        def tokenize(batch):
            if args.pair_field:
                return tok(batch["a"], batch["b"], truncation=True, max_length=args.max_len)
            return tok(batch["a"], truncation=True, max_length=args.max_len)
        return ds.map(tokenize, batched=True, remove_columns=["a", "b"])

    train, dev = encode("train"), encode("dev")
    test = encode("test") if by["test"] else None
    counts = Counter(r[args.label_field] for r in by["train"])
    weights = torch.tensor([len(by["train"]) / (len(labels) * counts.get(l, 1)) for l in labels], dtype=torch.float)

    class WeightedTrainer(Trainer):
        def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
            y = inputs.pop("labels")
            out = model(**inputs)
            loss = torch.nn.functional.cross_entropy(out.logits, y, weight=weights.to(out.logits.device))
            return (loss, out) if return_outputs else loss

    def compute(eval_pred):
        logits, y = eval_pred
        m = metrics(list(y), list(np.argmax(logits, axis=-1)), labels)
        return {"accuracy": m["accuracy"], "macro_f1": m["macro_f1"]}

    out = Path(args.out)
    import math
    warmup = int(0.06 * math.ceil(len(train) / args.batch) * args.epochs)  # 6% warm-up (warmup_ratio is gone in transformers 5)
    targs = TrainingArguments(
        output_dir=str(out / "checkpoints"), num_train_epochs=args.epochs, learning_rate=args.lr,
        per_device_train_batch_size=args.batch, per_device_eval_batch_size=args.batch * 2,
        eval_strategy="epoch", save_strategy="epoch", load_best_model_at_end=True,
        metric_for_best_model="macro_f1", save_total_limit=1, logging_steps=20, report_to=[],
        fp16=args.fp16, seed=args.seed, warmup_steps=warmup, weight_decay=0.01)
    trainer = WeightedTrainer(model=model, args=targs, train_dataset=train, eval_dataset=dev,
                              data_collator=DataCollatorWithPadding(tok), compute_metrics=compute)
    t0 = time.time()
    trainer.train()
    seconds = time.time() - t0

    report = {"model": args.model, "data": args.data, "label_field": args.label_field, "labels": labels,
              "train_rows": len(by["train"]), "seconds": round(seconds, 1), "args": vars(args)}
    for name, ds in (("dev", dev), ("test", test)):
        if ds is None:
            continue
        pred = trainer.predict(ds)
        report[name] = metrics(list(pred.label_ids), list(np.argmax(pred.predictions, axis=-1)), labels)
    out.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(out / "model"))
    tok.save_pretrained(str(out / "model"))
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    for name in ("dev", "test"):
        if name in report:
            r = report[name]
            print(f"{name}: n={r['n']} acc={r['accuracy']:.3f} macroF1={r['macro_f1']:.3f} "
                  f"(majority baseline {r['majority_baseline']:.3f})")
    print(f"trained in {seconds:.0f}s → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
