"""GreenScan T1 on a Kaggle GPU: baselines, two fine-tuned students, CV by company,
learning curve, ablations, final models on the lot-1 comparison set.

The reference labels are Claude's (two blind passes + adjudication,
training/claude_labels.py). Until human gold exists every number written here is
agreement with that reference — how well a student imitates its teacher — not
accuracy. results.json says so, and the report must too.

Run 1 (2026-10-13, training/runs/kaggle_t1_v1) taught three things, fixed here:
  * mDeBERTa-xnli predicted NOT_CLAIM for all 498 sentences in every fold and seed
    (150 optimizer steps at lr 2e-5 was too little for DeBERTa-v3 to leave the
    majority class). Now 15 epochs at 3e-5, and a collapse guard: if a trained
    model puts > 95 % of its own training sentences in one class, it is retrained
    once with the fallback recipe. The guard looks only at training data; every
    retry is counted in results.json.
  * The learning curve held epochs fixed, so 25 % of the data also meant 25 % of the
    optimizer steps; data and training length were confounded. Now each fraction
    gets the same number of steps.
  * One seed per CV model hid a spread of 0.50–0.62 macro-F1 between seeds. Now
    CV runs 3 seeds; out-of-fold probabilities are averaged over seeds and each
    seed's score is kept.

Experiments (masked sentence unless stated):
  zero-shot      mDeBERTa-xnli as an NLI classifier, one hypothesis per class, no training
  e5-base        intfloat/multilingual-e5-base fine-tuned
  mdeberta-xnli  MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 fine-tuned
  CV             GroupKFold(5) by company × 3 seeds on the 498 training sentences
  ablations      best student, seed 13: raw text instead of masked; previous sentence as a pair
  learning curve best student, seed 13, 25 / 50 / 75 % of each training fold, equal steps
  final          each student on all 498 × 3 seeds, probabilities averaged → comparison set
  CPU latency    best final model, batch 1, 4 threads, on the Kaggle CPU

Run 4 (2026-10-16) is a candidate sweep for step 4, under the rules registered the same day
(configs/measurement_decisions.yaml, model_selection_v2.t1_claim_detection), on ~2,150 training labels:
  * students: e5-small, e5-base, e5-large (gradient checkpointing; v3 ran out of memory), bge-m3,
    Qwen3-0.6B and Qwen3-1.7B as classifiers with LoRA (the "Qwen3 1.7B" TARGET_PIPELINE proposed and
    nobody measured). Same folds, same seeds, same input for all of them.
  * 2 seeds instead of 3 (four times the data; the time budget is the binding limit), cheapest model
    first, a time guard that skips (and records) what would not finish inside the Kaggle session.
  * the raw/pair ablations are dropped (inconclusive in v3); the learning curve stays on the best.
  * CPU latency for every final model, not only the best (the laptop number comes from
    training/latency_t1.py: the decision limit is ms on the team's i7-1355U).

Outputs in /kaggle/working: results.json, preds_cv.jsonl, preds_compare.jsonl, log.txt
"""
import gc
import glob
import json
import os
import random
import time

import numpy as np
import torch
from sklearn.metrics import (accuracy_score, cohen_kappa_score, confusion_matrix, f1_score,
                             precision_recall_fscore_support)
from sklearn.model_selection import GroupKFold
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup,
                          pipeline)

OUT = os.environ.get("T1_OUT", "/kaggle/working")
DATA = os.environ.get("T1_DATA") or os.path.dirname(glob.glob("/kaggle/input/**/train.jsonl", recursive=True)[0])
SMOKE = bool(os.environ.get("T1_SMOKE"))      # local check of the code path: tiny model, few rows, no zero-shot
LABELS = ["NOT_CLAIM", "QUALITATIVE_CLAIM", "QUANTIFIED_CLAIM", "VAGUE"]
L2I = {l: i for i, l in enumerate(LABELS)}
CLAIMS = {1, 2, 3}
# v3: mdeberta-xnli is out of the students. It collapsed to all-NOT_CLAIM in 18 of 18 runs in v2,
# whatever the lr, and needs its own diagnosis. multilingual-e5-large takes its slot. The NLI model stays
# as the zero-shot baseline.
ZS_MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
# v4: cheapest first, so a time-out costs the most expensive candidate, never the baseline
MODELS = {"e5-small": "intfloat/multilingual-e5-small",
          "e5-base": "intfloat/multilingual-e5-base",
          "qwen3-0.6b": "Qwen/Qwen3-0.6B",
          "e5-large": "intfloat/multilingual-e5-large",
          "bge-m3": "BAAI/bge-m3",
          "qwen3-1.7b": "Qwen/Qwen3-1.7B"}
LORA_TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
HP = {"e5-small": dict(lr=5e-5, epochs=6, fp16=True, prefix="query: "),
      "e5-base": dict(lr=3e-5, epochs=6, fp16=True, prefix="query: "),
      "qwen3-0.6b": dict(lr=2e-4, epochs=4, fp16=True, prefix="", lora=16),
      "e5-large": dict(lr=2e-5, epochs=6, fp16=True, prefix="query: ", ckpt=True),   # v3: OOM without checkpointing
      "bge-m3": dict(lr=2e-5, epochs=6, fp16=True, prefix="", ckpt=True),
      "qwen3-1.7b": dict(lr=2e-4, epochs=4, fp16=True, prefix="", lora=16, ckpt=True)}
RETRY = {k: dict(lr=v["lr"] * 1.5, epochs=v["epochs"] + 4) for k, v in HP.items()}
BUDGET_SECONDS = 10.5 * 3600      # Kaggle stops a GPU session at 12 h; leave room for the curve and latency
HYPOTHESES = {   # zero-shot: one Vietnamese hypothesis per class, same meaning as the codebook
    "NOT_CLAIM": "Câu này không phải là tuyên bố môi trường của doanh nghiệp.",
    "QUALITATIVE_CLAIM": "Câu này là tuyên bố về một hành động môi trường cụ thể của doanh nghiệp, không có số liệu.",
    "QUANTIFIED_CLAIM": "Câu này là tuyên bố môi trường của doanh nghiệp có số liệu cụ thể.",
    "VAGUE": "Câu này là khẩu hiệu hoặc cam kết chung chung về môi trường, phát triển bền vững.",
}
MAX_LEN, BATCH, SEEDS, DEVICE = 160, 16, [13, 29], "cuda" if torch.cuda.is_available() else "cpu"
STARTED = time.time()
if SMOKE:
    MODELS = {k: ("hf-internal-testing/tiny-random-LlamaForCausalLM" if "lora" in HP[k] else
                  "hf-internal-testing/tiny-random-bert") for k in MODELS}
    ZS_MODEL = "hf-internal-testing/tiny-random-bert"
    HP = {k: {**v, "epochs": 1, "fp16": False} for k, v in HP.items()}
    RETRY = {k: {**v, "epochs": 1} for k, v in RETRY.items()}
    SEEDS = [13, 29]
LOG = open(f"{OUT}/log.txt", "a", encoding="utf-8")
STATS = {"retries": {}, "last_epoch_loss": {}}


def log(*a):
    msg = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(msg, flush=True)
    LOG.write(msg + "\n")
    LOG.flush()


def read(name):
    return [json.loads(l) for l in open(f"{DATA}/{name}", encoding="utf-8") if l.strip()]


def seed_all(s):
    random.seed(s)
    np.random.seed(s)
    torch.manual_seed(s)
    torch.cuda.manual_seed_all(s)


def metrics(y, p):
    y, p = np.asarray(y), np.asarray(p)
    pr, rc, f, n = precision_recall_fscore_support(y, p, labels=range(4), zero_division=0)
    yb, pb = np.isin(y, list(CLAIMS)), np.isin(p, list(CLAIMS))
    bp, br, bf, _ = precision_recall_fscore_support(yb, pb, average="binary", zero_division=0)
    return {"n": int(len(y)), "accuracy": float(accuracy_score(y, p)),
            "macro_f1": float(f1_score(y, p, labels=range(4), average="macro", zero_division=0)),
            "kappa": float(cohen_kappa_score(y, p)) if len(set(y) | set(p)) > 1 else None,
            "per_class": {LABELS[i]: {"precision": float(pr[i]), "recall": float(rc[i]), "f1": float(f[i]),
                                      "support": int(n[i])} for i in range(4)},
            "claim_vs_not": {"precision": float(bp), "recall": float(br), "f1": float(bf)},
            "confusion": confusion_matrix(y, p, labels=range(4)).tolist()}


def inputs(rows, variant, prefix):
    if variant == "raw":
        return [prefix + r["text"] for r in rows], None
    a = [prefix + r["text_masked"] for r in rows]
    if variant == "pair":
        return [prefix + (r.get("prev_text") or "") for r in rows], a        # (context, sentence)
    return a, None


def encode(tok, a, b):
    return tok(a, b, truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt") if b else \
        tok(a, truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt")


def fit(key, rows, variant, seed, lr, epochs, steps=None):
    """One fine-tuning run; `steps` (if given) fixes the number of optimizer steps."""
    hp = HP[key]
    seed_all(seed)
    tok = AutoTokenizer.from_pretrained(MODELS[key])
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForSequenceClassification.from_pretrained(
        MODELS[key], num_labels=4, ignore_mismatched_sizes=True,
        id2label=dict(enumerate(LABELS)), label2id=L2I)
    model.config.pad_token_id = tok.pad_token_id
    if hp.get("ckpt"):
        model.config.use_cache = False
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    if hp.get("lora"):                                    # decoder as a classifier: LoRA + a trained head
        from peft import LoraConfig, get_peft_model
        targets = [t for t in LORA_TARGETS if any(n.endswith(t) for n, _ in model.named_modules())]
        model = get_peft_model(model, LoraConfig(task_type="SEQ_CLS", r=hp["lora"], lora_alpha=2 * hp["lora"],
                                                 lora_dropout=0.05, target_modules=targets or None))
    model = model.to(DEVICE)
    y = torch.tensor([L2I[r["label"]] for r in rows])
    counts = torch.bincount(y, minlength=4).float().clamp(min=1)
    weight = (counts.sum() / counts).sqrt()
    weight = (weight / weight.mean()).to(DEVICE)              # inverse-sqrt frequency, mean 1
    a, b = inputs(rows, variant, hp["prefix"])
    bs = hp.get("batch", BATCH)
    per_epoch = (len(rows) + bs - 1) // bs
    total = steps or epochs * per_epoch
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * total), total)
    use_fp16 = hp["fp16"] and DEVICE == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_fp16)
    lossf = torch.nn.CrossEntropyLoss(weight=weight)
    model.train()
    done, losses, order = 0, [], list(range(len(rows)))
    while done < total:
        random.shuffle(order)
        losses = []
        for i in range(0, len(order), bs):
            if done >= total:
                break
            idx = order[i:i + bs]
            enc = encode(tok, [a[j] for j in idx], [b[j] for j in idx] if b else None).to(DEVICE)
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=use_fp16):
                loss = lossf(model(**enc).logits.float(), y[idx].to(DEVICE))
            opt.zero_grad()
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(opt)
            scaler.update()
            sch.step()
            losses.append(float(loss))
            done += 1
    return model, tok, float(np.mean(losses)) if losses else None


def collapsed(model, tok, rows, key, variant):
    """True if the model puts > 95 % of (up to 200 of) its own training sentences in one class."""
    sample = rows[:200]
    pred = predict(model, tok, sample, variant, HP[key]["prefix"]).argmax(1)
    share = np.bincount(pred, minlength=4).max() / len(pred)
    truth = np.bincount([L2I[r["label"]] for r in sample], minlength=4).max() / len(sample)
    return share > 0.95 and truth < 0.85


def train_predict(key, train_rows, eval_rows, variant="masked", seed=13, frac=1.0, tag=""):
    """Fine-tune with the collapse guard, return probabilities on eval_rows and the model."""
    hp = HP[key]
    steps = None
    if frac < 1.0:                                   # stratified subsample, same number of steps as the full fold
        by = {}
        for r in train_rows:
            by.setdefault(r["label"], []).append(r)
        rng = random.Random(seed)
        bs = hp.get("batch", BATCH)
        steps = hp["epochs"] * ((len(train_rows) + bs - 1) // bs)
        train_rows = [r for rs in by.values() for r in rng.sample(rs, max(1, round(len(rs) * frac)))]
    model, tok, loss = fit(key, train_rows, variant, seed, hp["lr"], hp["epochs"], steps)
    if collapsed(model, tok, train_rows, key, variant):
        STATS["retries"][tag] = STATS["retries"].get(tag, 0) + 1
        log(f"  collapse guard: {tag} retrained with lr {RETRY[key]['lr']}, {RETRY[key]['epochs']} epochs")
        free(model, tok)
        model, tok, loss = fit(key, train_rows, variant, seed, RETRY[key]["lr"], RETRY[key]["epochs"],
                               steps and steps * RETRY[key]["epochs"] // hp["epochs"])
    STATS["last_epoch_loss"].setdefault(tag, []).append(loss)
    return predict(model, tok, eval_rows, variant, hp["prefix"]), model, tok


@torch.no_grad()
def predict(model, tok, rows, variant, prefix, device=DEVICE):
    model.eval()
    a, b = inputs(rows, variant, prefix)
    out = []
    for i in range(0, len(rows), 64):
        enc = encode(tok, a[i:i + 64], b[i:i + 64] if b else None).to(device)
        out.append(torch.softmax(model(**enc).logits.float(), -1).cpu().numpy())
    model.train()
    return np.concatenate(out) if out else np.zeros((0, 4))


def free(*objs):
    for o in objs:
        del o
    gc.collect()
    torch.cuda.empty_cache()


def main():
    train, compare = read("train.jsonl"), read("compare.jsonl")
    if SMOKE:
        train, compare = train[:80], compare[:15] + compare[-15:]
    log(f"device {DEVICE} {torch.cuda.get_device_name(0) if DEVICE == 'cuda' else ''} · train {len(train)} · compare {len(compare)}")
    y_tr = [L2I[r["label"]] for r in train]
    y_cmp = [L2I[r["label"]] for r in compare]
    subsets = {"all": list(range(len(compare))),
               "audit": [i for i, r in enumerate(compare) if r["set"] == "audit"],
               "hpg": [i for i, r in enumerate(compare) if r["set"] == "hpg"]}
    folds = list(GroupKFold(n_splits=5).split(train, y_tr, groups=[r["company_id"] for r in train]))
    res = {"version": 4, "reference": "Claude labels (2 blind passes + adjudication) — agreement, not accuracy",
           "labels": LABELS, "hp": HP, "retry_recipe": RETRY, "seeds": SEEDS, "configs": {}, "learning_curve": {},
           "timings": {}, "env": {"torch": torch.__version__,
                                  "gpu": torch.cuda.get_device_name(0) if DEVICE == "cuda" else None}}
    cvf = open(f"{OUT}/preds_cv.jsonl", "w", encoding="utf-8")
    cmpf = open(f"{OUT}/preds_compare.jsonl", "w", encoding="utf-8")

    def save():
        res["stats"] = STATS
        json.dump(res, open(f"{OUT}/results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def record(name, oof, cmp_probs=None, extra=None):
        entry = {"cv": metrics(y_tr, oof.argmax(1)), **(extra or {})}
        for i, r in enumerate(train):
            cvf.write(json.dumps({"config": name, "id": r["id"], "probs": oof[i].round(4).tolist()}) + "\n")
        if cmp_probs is not None:
            entry["compare"] = {k: metrics([y_cmp[i] for i in ix], cmp_probs[ix].argmax(1))
                                for k, ix in subsets.items() if ix}
            for i, r in enumerate(compare):
                cmpf.write(json.dumps({"config": name, "id": r["id"], "probs": cmp_probs[i].round(4).tolist()}) + "\n")
        res["configs"][name] = entry
        cvf.flush()
        cmpf.flush()
        save()
        log(name, "CV macro-F1", round(entry["cv"]["macro_f1"], 3),
            "· compare", {k: round(v["macro_f1"], 3) for k, v in entry.get("compare", {}).items()})

    def cv(key, seed, variant="masked", frac=1.0):
        oof = np.zeros((len(train), 4))
        for k, (tr, te) in enumerate(folds):
            if time.time() - STARTED > BUDGET_SECONDS:
                raise TimeoutError(f"time budget reached before {key} fold {k} seed {seed}")
            p, m, tk = train_predict(key, [train[i] for i in tr], [train[i] for i in te], variant=variant, seed=seed,
                                     frac=frac, tag=f"{key}·{variant}·s{seed}·f{frac}")
            oof[te] = p
            free(m, tk)
        return oof

    # 1. zero-shot NLI, no training (raw text: nothing is learnt, so nothing to hide)
    if not SMOKE:
        t = time.time()
        zs = pipeline("zero-shot-classification", model=ZS_MODEL, device=0 if DEVICE == "cuda" else -1)
        hyp = [HYPOTHESES[l] for l in LABELS]

        def zshot(rows):
            out = zs([r["text"] for r in rows], candidate_labels=hyp, hypothesis_template="{}", multi_label=False,
                     batch_size=32)
            return np.array([[o["scores"][o["labels"].index(h)] for h in hyp] for o in out])
        record("zero-shot", zshot(train), zshot(compare), {"seconds": round(time.time() - t, 1)})
        free(zs)

    # 2. students: CV × seeds (probabilities averaged), final models × seeds on the comparison set
    best, best_f1 = None, -1
    for key in MODELS:
      if time.time() - STARTED > BUDGET_SECONDS:
          STATS.setdefault("skipped", []).append(key)
          log(f"{key} SKIPPED: time budget ({BUDGET_SECONDS / 3600:.1f} h) used up")
          continue
      try:
        t = time.time()
        per_seed, oof_sum = {}, np.zeros((len(train), 4))
        for s in SEEDS:
            oof = cv(key, s)
            oof_sum += oof
            per_seed[s] = metrics(y_tr, oof.argmax(1))["macro_f1"]
            if s == SEEDS[0]:
                record(f"{key}·masked·s{s}", oof)       # the paired reference for the ablations
            log(f"{key} seed {s} CV macro-F1 {per_seed[s]:.3f}")
        cv_secs = round(time.time() - t, 1)
        cmp, latency = np.zeros((len(compare), 4)), {}
        final_seed = {}
        for s in SEEDS:
            p, m, tk = train_predict(key, train, compare, seed=s, tag=f"{key}·final·s{s}")
            cmp += p / len(SEEDS)
            final_seed[s] = metrics(y_cmp, p.argmax(1))["macro_f1"]
            if not latency:                       # every candidate's CPU cost, batch 1, 4 threads
                m = m.to("cpu")
                torch.set_num_threads(4)
                sample = compare[:100]
                t0 = time.time()
                for r in sample:
                    predict(m, tk, [r], "masked", HP[key]["prefix"], device="cpu")
                latency = {"cpu_ms_per_sentence_batch1_4threads": round(1000 * (time.time() - t0) / len(sample), 1),
                           "parameters_millions": round(sum(x.numel() for x in m.parameters()) / 1e6, 1)}
            free(m, tk)
        record(key, oof_sum / len(SEEDS), cmp, {"cv_seconds": cv_secs, "cv_macro_f1_by_seed": per_seed,
                                                 "compare_macro_f1_by_seed": final_seed, **latency})
        f1 = res["configs"][key]["cv"]["macro_f1"]
        if f1 > best_f1:
            best, best_f1 = key, f1
      except Exception as e:                       # noqa: BLE001
        log(f"{key} FAILED: {type(e).__name__}: {str(e)[:300]}")
        STATS.setdefault("failed", {})[key] = f"{type(e).__name__}: {str(e)[:300]}"
        gc.collect()
        torch.cuda.empty_cache()
    res["best"] = best
    log("best student:", best)

    # 3. learning curve on the best student, seed 13, equal optimizer steps per fraction
    #    (1.0 is `<best>·masked·s13`); v3's raw/pair ablations were inconclusive and are not repeated
    if best is None:
        save()
        log("no student finished")
        return
    res["learning_curve"]["1.0"] = res["configs"][f"{best}·masked·s{SEEDS[0]}"]["cv"]["macro_f1"]
    for frac in (0.25, 0.5, 0.75):
        try:
            res["learning_curve"][str(frac)] = metrics(y_tr, cv(best, SEEDS[0], frac=frac).argmax(1))["macro_f1"]
        except TimeoutError as e:
            STATS.setdefault("skipped", []).append(f"learning curve {frac}: {e}")
            log(f"learning curve {frac} SKIPPED: {e}")
            break
        log("learning curve", frac, round(res["learning_curve"][str(frac)], 3))
        save()
    res["timings"]["total_hours"] = round((time.time() - STARTED) / 3600, 2)
    save()
    log("done", res["timings"], "retries", STATS["retries"], "skipped", STATS.get("skipped"))


if __name__ == "__main__":
    main()
