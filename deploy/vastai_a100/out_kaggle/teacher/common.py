"""Shared helpers for GreenScan training on Kaggle (T4) and on a rented A100 (vast.ai).

Data is looked up in $GS_DATA, ./data, ../data, then /kaggle/input (a private dataset). Outputs go to $GS_OUT
(default ./out). Every script prints "[cell] ..." at each stage and flushes, so a log shows where a run is.
"""
from __future__ import annotations

import json
import os
import random
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def cell(name: str) -> None:
    print(f"[cell] {name}", flush=True)


def log(*a) -> None:
    print(*a, flush=True)


def find(name: str) -> Path:
    for root in (os.environ.get("GS_DATA", ""), "data", "../data", "/kaggle/input"):
        if root and Path(root).exists():
            hit = next(iter(sorted(Path(root).rglob(name))), None)
            if hit:
                return hit
    raise FileNotFoundError(name)


def has(name: str) -> bool:
    try:
        find(name)
        return True
    except FileNotFoundError:
        return False


def jl(path) -> list[dict]:
    p = Path(path) if not isinstance(path, str) or Path(path).exists() else find(path)
    return [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]


def wjl(path, rows) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def out_dir(sub: str = "") -> Path:
    p = Path(os.environ.get("GS_OUT", "out")) / sub
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_json(path, obj) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def norm60(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower()).strip()[:60]


def company_folds(groups: list[str], k: int = 5, seed: int = 13) -> list[tuple[list[int], list[int]]]:
    """Out-of-company folds: every company sits in exactly one test fold; folds balanced by row count."""
    count = Counter(groups)
    comps = sorted(count, key=lambda c: (-count[c], c))
    rng = random.Random(seed)
    rng.shuffle(comps)
    comps.sort(key=lambda c: -count[c])
    load, fold_of = [0] * k, {}
    for c in comps:
        f = min(range(k), key=lambda i: load[i])
        fold_of[c] = f
        load[f] += count[c]
    out = []
    for f in range(k):
        test = [i for i, g in enumerate(groups) if fold_of[g] == f]
        train = [i for i, g in enumerate(groups) if fold_of[g] != f]
        if test and train:
            out.append((train, test))
    return out


def prf(gold: list[str], pred: list[str], labels: list[str]) -> dict:
    per = {}
    for l in labels:
        tp = sum(g == l and p == l for g, p in zip(gold, pred))
        fp = sum(g != l and p == l for g, p in zip(gold, pred))
        fn = sum(g == l and p != l for g, p in zip(gold, pred))
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        per[l] = {"precision": round(pr, 4), "recall": round(rc, 4),
                  "f1": round(2 * pr * rc / (pr + rc), 4) if pr + rc else 0.0, "support": tp + fn, "predicted": tp + fp}
    present = [l for l in labels if per[l]["support"]]
    macro = sum(per[l]["f1"] for l in present) / len(present) if present else 0.0
    acc = sum(g == p for g, p in zip(gold, pred)) / len(gold) if gold else 0.0
    return {"macro_f1": round(macro, 4), "accuracy": round(acc, 4), "per_class": per, "n": len(gold)}


def confusion(gold: list[str], pred: list[str], labels: list[str]) -> list[list[int]]:
    idx = {l: i for i, l in enumerate(labels)}
    m = [[0] * len(labels) for _ in labels]
    for g, p in zip(gold, pred):
        if g in idx and p in idx:
            m[idx[g]][idx[p]] += 1
    return m


def boot_ci(items: list, groups: list[str], stat, n: int = 1000, seed: int = 7) -> list[float] | None:
    """95% interval of stat(items) resampling whole companies (cluster bootstrap)."""
    by = defaultdict(list)
    for it, g in zip(items, groups):
        by[g].append(it)
    keys = sorted(by)
    if len(keys) < 2:
        return None
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        sample = [it for _ in keys for it in by[rng.choice(keys)]]
        try:
            vals.append(stat(sample))
        except ZeroDivisionError:
            continue
    vals.sort()
    return [round(vals[int(0.025 * len(vals))], 4), round(vals[int(0.975 * len(vals)) - 1], 4)] if vals else None


class Timer:
    def __init__(self):
        self.t0 = time.time()

    def __call__(self) -> float:
        return round(time.time() - self.t0, 1)
