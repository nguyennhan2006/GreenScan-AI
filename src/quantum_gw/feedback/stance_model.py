"""A small stance model that runs on the 8 GB profile (feedback-loop-v1, tier 4).

`hashed-linear-v1`: accent-folded word unigrams and bigrams of the passage,
character 4-grams, the words claim and passage share, number agreement and
length buckets, hashed into 2^18 slots, and one multinomial logistic regression
on top. It trains in seconds on a laptop and predicts with numpy alone, so the
offline profile can run it in shadow on every claim.

It is the CPU challenger. A GPU challenger (a Vietnamese cross-encoder trained
on Kaggle, tools/feedback/train_stance_gpu.py) goes through the same dataset,
the same metrics and the same promotion gate (registry.py).

Weights are saved as .npz and loaded with allow_pickle=False, and the metadata
as JSON: a model file is data, never code, so loading one cannot run anything.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import zlib
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from quantum_gw.utils.text import fold, normalize_text

KIND = "hashed-linear-v1"
DIM = 2 ** 18
_WORD = re.compile(r"[0-9a-z]+(?:[.,][0-9]+)*%?")
_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


def _words(text: str) -> list[str]:
    return _WORD.findall(fold(normalize_text(text or "")))


def _bucket(value: float, edges: tuple[float, ...]) -> int:
    return sum(1 for edge in edges if value >= edge)


def features(claim: str, passage: str) -> dict[int, float]:
    cw, pw = _words(claim), _words(passage)
    names: Counter = Counter()
    names.update(f"p1:{w}" for w in pw)
    names.update(f"p2:{a}_{b}" for a, b in zip(pw, pw[1:]))
    joined = " ".join(pw)
    names.update(f"c4:{joined[i:i + 4]}" for i in range(0, max(0, len(joined) - 3), 2))
    shared = set(cw) & set(pw)
    names.update(f"s:{w}" for w in shared)
    overlap = len(shared) / max(1, len(set(cw)))
    names[f"ov:{_bucket(overlap, (0.1, 0.2, 0.35, 0.5, 0.7))}"] += 1
    claim_numbers = {n.replace(",", ".") for n in _NUMBER.findall(claim or "")}
    passage_numbers = {n.replace(",", ".") for n in _NUMBER.findall(passage or "")}
    if claim_numbers:
        names["num:shared" if claim_numbers & passage_numbers else "num:claim_only"] += 1
    else:
        names["num:none"] += 1
    names[f"len:{_bucket(len(pw), (15, 40, 80, 160))}"] += 1
    vector: dict[int, float] = {}
    for name in names:
        index = zlib.crc32(name.encode("utf-8")) % DIM
        vector[index] = 1.0  # binary presence; collisions merge
    norm = math.sqrt(len(vector)) or 1.0
    return {k: v / norm for k, v in vector.items()}


class HashedLinearStance:
    def __init__(self, labels: list[str], coef: np.ndarray, intercept: np.ndarray, meta: dict | None = None):
        self.labels = list(labels)
        self.coef = coef.astype(np.float32)
        self.intercept = intercept.astype(np.float32)
        self.meta = meta or {}

    def predict_proba(self, claim: str, passage: str) -> dict[str, float]:
        vector = features(claim, passage)
        index = np.fromiter(vector.keys(), dtype=np.int64)
        value = np.fromiter(vector.values(), dtype=np.float32)
        scores = self.coef[:, index] @ value + self.intercept
        scores = scores - scores.max()
        exp = np.exp(scores)
        probs = exp / exp.sum()
        return {label: float(p) for label, p in zip(self.labels, probs)}

    def predict(self, claim: str, passage: str) -> tuple[str, float]:
        probs = self.predict_proba(claim, passage)
        label = max(probs, key=probs.get)
        return label, probs[label]

    # ------------------------------------------------------------- files

    def save(self, folder: str | Path) -> dict:
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        weights = folder / "weights.npz"
        np.savez_compressed(weights, coef=self.coef, intercept=self.intercept)
        meta = {**self.meta, "kind": KIND, "labels": self.labels, "dim": DIM,
                "weights_sha256": hashlib.sha256(weights.read_bytes()).hexdigest()}
        (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        self.meta = meta
        return meta

    @classmethod
    def load(cls, folder: str | Path) -> HashedLinearStance:
        folder = Path(folder)
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        if meta.get("kind") != KIND or meta.get("dim") != DIM:
            raise ValueError(f"{folder}: not a {KIND} model with dim {DIM}")
        with np.load(folder / "weights.npz", allow_pickle=False) as data:
            return cls(meta["labels"], data["coef"], data["intercept"], meta)


def train(pairs: list[dict], c: float = 4.0, seed: int = 0) -> HashedLinearStance:
    """Fit on the `train` split. Needs scikit-learn and scipy (training only; predicting needs numpy)."""
    from scipy.sparse import csr_matrix
    from sklearn.linear_model import LogisticRegression

    rows = [p for p in pairs if p.get("split", "train") == "train"]
    if len({p["relation"] for p in rows}) < 2:
        raise ValueError("need at least two relations in the training split")
    data, indices, indptr = [], [], [0]
    for pair in rows:
        vector = features(pair["claim"], pair["passage"])
        indices.extend(vector.keys())
        data.extend(vector.values())
        indptr.append(len(indices))
    x = csr_matrix((np.array(data, dtype=np.float32), np.array(indices), np.array(indptr)), shape=(len(rows), DIM))
    y = [p["relation"] for p in rows]
    model = LogisticRegression(C=c, max_iter=3000, class_weight="balanced", random_state=seed)
    model.fit(x, y, sample_weight=[float(p.get("weight", 1.0)) for p in rows])
    coef = model.coef_
    intercept = model.intercept_
    labels = list(model.classes_)
    if len(labels) == 2:  # sklearn returns one row for two classes
        coef = np.vstack([-coef[0], coef[0]])
        intercept = np.array([-intercept[0], intercept[0]])
    meta = {"trained_at": datetime.now(UTC).isoformat(), "train_pairs": len(rows), "c": c,
            "train_relations": dict(Counter(y))}
    return HashedLinearStance(labels, np.asarray(coef), np.asarray(intercept), meta)


def evaluate(pairs: list[dict], predict) -> dict:
    """Pair-level metrics; `predict(pair) -> relation or None` (None = no answer, counted as abstain)."""
    gold, pred = [], []
    abstain = 0
    for pair in pairs:
        p = predict(pair)
        if p is None:
            abstain += 1
            continue
        gold.append(pair["relation"])
        pred.append(p)
    labels = sorted(set(gold) | set(pred))
    per = {}
    for label in labels:
        tp = sum(1 for g, p in zip(gold, pred) if g == label and p == label)
        fp = sum(1 for g, p in zip(gold, pred) if g != label and p == label)
        fn = sum(1 for g, p in zip(gold, pred) if g == label and p != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per[label] = {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4),
                      "gold": sum(1 for g in gold if g == label), "predicted": sum(1 for p in pred if p == label)}
    gold_labels = sorted(set(gold))
    return {
        "pairs": len(pairs), "answered": len(gold), "abstained": abstain,
        "accuracy": round(sum(1 for g, p in zip(gold, pred) if g == p) / len(gold), 4) if gold else None,
        # Macro-F1 over the relations the gold data contains: a relation nobody labelled
        # (CONTRADICTS in the Claude set) cannot be scored and is not averaged in.
        "macro_f1": round(sum(per[label]["f1"] for label in gold_labels) / len(gold_labels), 4) if gold_labels else None,
        # The two errors the team counts first, at pair level:
        "false_contradicts": sum(1 for g, p in zip(gold, pred) if p == "CONTRADICTS" and g != "CONTRADICTS"),
        "false_supports": sum(1 for g, p in zip(gold, pred) if p == "SUPPORTS" and g in ("CONTEXT", "CONTRADICTS")),
        "overclaimed_support": sum(1 for g, p in zip(gold, pred) if p == "SUPPORTS" and g == "PARTIAL"),
        "per_relation": per,
    }


def champion_metrics(pairs: list[dict]) -> dict:
    """The rules, scored on the same pairs (pairs without a rules relation count as abstentions)."""
    return evaluate(pairs, lambda pair: pair.get("champion") or None)


def challenger_metrics(model: HashedLinearStance, pairs: list[dict]) -> dict:
    return evaluate(pairs, lambda pair: model.predict(pair["claim"], pair["passage"])[0])
