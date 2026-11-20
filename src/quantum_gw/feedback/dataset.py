"""Training data for the stance model (feedback-loop-v1, tier 4): (claim, passage, relation) pairs.

Two sources, kept apart by `provenance` and weighted differently:

* human_pointer (weight 1.0): a finalized, clean decision (hygiene.clean_labels)
  whose reviewer pointed at the passage that decided it. The verdict, read as
  the relation of that passage (SUPPORTED -> SUPPORTS, PARTIALLY_SUPPORTED ->
  PARTIAL, CONTRADICTED -> CONTRADICTS), is the pair's label. A verdict without
  a pointer names no passage and makes no pair.
* claude (weight 0.5): the 821 pairs labelled by Claude per the codebook in two
  passes with adjudication, reviewed by the author (deploy/vastai_a100/data,
  pairs_pool.jsonl + pairs_labels.jsonl). Used as ordinary data, with their
  provenance kept (memory note "claude labels as dataset").

Every pair carries `champion`: what the rules said about the same passage
(the evidence snapshot for human pairs, pairs_cand_rules.jsonl for Claude
pairs), so the challenger is always compared on the same pairs.

The split is by group (the run for human pairs, the company for Claude pairs),
by hash, so one report never sits on both sides of the train / holdout line.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from .hygiene import SCOPE_CORE, QAStore, clean_labels
from .precedents import LABEL_TO_RELATION

RELATIONS = ("SUPPORTS", "PARTIAL", "CONTEXT", "CONTRADICTS")
CLAUDE_DIR = Path("deploy/vastai_a100/data")
WEIGHTS = {"human_pointer": 1.0, "claude": 0.5}


def human_pairs(clean: list[dict]) -> list[dict]:
    out = []
    for g in clean:
        relation = LABEL_TO_RELATION.get(g.get("label") or "")
        if relation is None:
            continue
        evidence = {e.get("chunk_id"): e for e in g.get("evidence_snapshot") or []}
        passages = [(cid, evidence[cid]) for cid in g.get("decisive_chunk_ids") or [] if cid in evidence]
        if g.get("decisive_quote"):
            passages.append((None, {"text": g["decisive_quote"], "relation": None}))
        for cid, item in passages:
            text = item.get("text") or item.get("text_preview") or ""
            if not text:
                continue
            out.append({
                "id": hashlib.sha256(f"{g['run_id']}|{g['claim_id']}|{cid}|{text[:200]}".encode()).hexdigest()[:16],
                "claim": g.get("claim_text") or "", "passage": text, "relation": relation,
                "weight": WEIGHTS["human_pointer"], "provenance": "human_pointer",
                "group": f"run:{g['run_id']}", "champion": item.get("relation"),
                "source_type": item.get("source_type"), "labeler": g.get("reviewer"),
            })
    return out


def claude_pairs(folder: str | Path = CLAUDE_DIR) -> list[dict]:
    folder = Path(folder)
    pool_file, labels_file = folder / "pairs_pool.jsonl", folder / "pairs_labels.jsonl"
    if not pool_file.is_file() or not labels_file.is_file():
        return []
    pool = {r["id"]: r for r in map(json.loads, pool_file.read_text(encoding="utf-8").splitlines()) if r}
    rules_file = folder / "pairs_cand_rules.jsonl"
    rules = ({r["id"]: r.get("relation") for r in map(json.loads, rules_file.read_text(encoding="utf-8").splitlines())}
             if rules_file.is_file() else {})
    out = []
    for label in map(json.loads, labels_file.read_text(encoding="utf-8").splitlines()):
        item = pool.get(label["id"])
        if item is None or label.get("relation") not in RELATIONS:
            continue
        out.append({
            "id": label["id"], "claim": item.get("claim") or "", "passage": item.get("passage") or "",
            "relation": label["relation"], "weight": WEIGHTS["claude"], "provenance": "claude",
            "group": f"company:{item.get('company_id') or label.get('company_id')}",
            "champion": rules.get(label["id"]), "source_type": None, "labeler": "claude",
        })
    return out


def assign_split(pairs: list[dict], holdout: float = 0.2, seed: str = "gs-stance-v1") -> list[dict]:
    for pair in pairs:
        digest = hashlib.sha256(f"{seed}|{pair['group']}".encode()).digest()
        pair["split"] = "holdout" if int.from_bytes(digest[:8], "big") / 2**64 < holdout else "train"
    return pairs


def build(store=None, qa: QAStore | None = None, scope: str = SCOPE_CORE, include_claude: bool = True,
          claude_dir: str | Path = CLAUDE_DIR, holdout: float = 0.2) -> list[dict]:
    from quantum_gw.storage.reviews import ReviewStore

    store = store or ReviewStore()
    clean = clean_labels(store.gold_records(), (qa or QAStore(reviews=store)).all(), scope)
    pairs = human_pairs(clean) + (claude_pairs(claude_dir) if include_claude else [])
    return assign_split(pairs, holdout)


def manifest(pairs: list[dict]) -> dict:
    blob = "".join(json.dumps(p, ensure_ascii=False, sort_keys=True) for p in pairs).encode("utf-8")
    return {
        "pairs": len(pairs),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "by_provenance": dict(Counter(p["provenance"] for p in pairs)),
        "by_relation": dict(Counter(p["relation"] for p in pairs)),
        "by_split": dict(Counter(p["split"] for p in pairs)),
        "groups": len({p["group"] for p in pairs}),
    }


def write(pairs: list[dict], path: str | Path) -> dict:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in pairs), encoding="utf-8")
    info = manifest(pairs)
    path.with_suffix(".manifest.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    return info


def read(path: str | Path) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
