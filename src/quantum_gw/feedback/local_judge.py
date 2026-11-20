"""Trained stance models inside a run: in shadow (always allowed) or as the judge (promoted only).

Shadow: `ShadowRunner` predicts the relation of the top passages of every claim
and writes them to `shadow.jsonl` in the run folder, next to what the rules
said. Nothing reads it back into the verdict; it feeds the disagreement count
in the audit log and the active-learning value (feedback/active.py).

Judge: `LocalStanceJudge` has the LLM judge's interface (verification/llm_judge.py)
and is consulted only for the pairs the rules escalate. It refuses to load a
model the registry does not list as promoted. Its signals carry method "llm",
so every guard written for model stances applies to it unchanged: a model
relation is not decisive unless `llm_stance_decisive` says so, and a
contradiction from a model alone goes to a person.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from quantum_gw.verification.stance import StanceSignal

from .registry import promoted_entry
from .stance_model import HashedLinearStance


class LocalStanceJudge:
    def __init__(self, model_dir: str | Path, registry_path: str | Path, min_confidence: float = 0.6):
        self.entry = promoted_entry(registry_path, model_dir)
        self.model = HashedLinearStance.load(model_dir)
        self.min_confidence = min_confidence
        self.stats: Counter = Counter()

    @property
    def version(self) -> str:
        return f"local:{self.entry['model_id']}@{self.entry['kind']}"

    def judge(self, claim_text: str, evidence_text: str) -> StanceSignal | None:
        relation, p = self.model.predict(claim_text, evidence_text)
        if p < self.min_confidence:
            self.stats["abstained"] += 1
            return None
        self.stats["answered"] += 1
        return StanceSignal(relation=relation, reason=f"[local/{self.entry['model_id']}] p={p:.2f}", method="llm")

    def prefetch(self, pairs: list[tuple[str, str]]) -> dict:
        return {"pairs": len(pairs), "asked": 0, "local_model": self.entry["model_id"]}


class ShadowRunner:
    def __init__(self, model_dir: str | Path, top_k: int = 3):
        self.model = HashedLinearStance.load(model_dir)
        self.model_id = Path(model_dir).name
        self.top_k = top_k

    def run(self, verifications, out_file: str | Path) -> dict:
        """Predict, compare with the rules' relation, write shadow.jsonl; returns per-claim disagreement counts."""
        rows, by_claim = [], {}
        for verification in verifications:
            claim = verification.claim
            disagree = 0
            for item in verification.evidence[: self.top_k]:
                relation, p = self.model.predict(claim.text, item.text)
                rules = getattr(item, "relation", None)
                differs = relation != rules
                disagree += int(differs)
                rows.append({"claim_id": claim.claim_id, "chunk_id": item.chunk_id, "rules": rules,
                             "shadow": relation, "p": round(p, 3), "differs": differs})
            by_claim[claim.claim_id] = disagree
        Path(out_file).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        return {"model_id": self.model_id, "pairs": len(rows),
                "disagreements": sum(1 for r in rows if r["differs"]),
                "by_pair": dict(Counter(f"{r['rules']}->{r['shadow']}" for r in rows if r["differs"])),
                "by_claim": by_claim}
