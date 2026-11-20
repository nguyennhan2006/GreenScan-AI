"""The feedback layer inside one run (feedback-loop-v1): what the orchestrator calls.

`FeedbackMemory` is built once per run from `settings.feedback`. It reads the
decision store at the start (so the manifest can record exactly which memory
the run consulted), may provide a promoted local stance judge and stance
examples for the LLM, and after prioritisation adds precedents, shadow-model
predictions, learning values and raise-only queue places.

Every step is wrapped: a broken store or model file is written to the audit log
and the run carries on as if the feedback layer were off. Nothing here reads or
writes a verdict, a risk score or a release status.
"""

from __future__ import annotations

from pathlib import Path

from quantum_gw.settings import FeedbackSettings


class FeedbackMemory:
    def __init__(self, settings: FeedbackSettings, audit):
        self.settings = settings
        self.audit = audit
        self.index = None
        self.store_info: dict | None = None
        self.clean: list[dict] = []
        self.shadow = None
        self.judge_info: dict | None = None
        if settings.precedents or settings.active_learning_slots or settings.stance_examples:
            self._load_store()
        if settings.shadow_model:
            try:
                from .local_judge import ShadowRunner

                self.shadow = ShadowRunner(settings.shadow_model)
            except Exception as exc:  # noqa: BLE001 - a missing model must not stop a run
                audit.write("shadow_model_unavailable", {"path": settings.shadow_model, "error": str(exc)[:300]})

    def _load_store(self) -> None:
        try:
            from quantum_gw.storage.reviews import ReviewStore

            from .hygiene import QAStore, clean_labels
            from .precedents import PrecedentIndex, store_fingerprint

            store = ReviewStore()
            qa = QAStore(reviews=store)
            self.index = PrecedentIndex.from_store(store, self.settings.org_id, qa)
            scope = f"org:{self.settings.org_id}" if self.settings.org_id else "core"
            self.clean = clean_labels(store.gold_records(), qa.all(), scope)
            if len(self.index):
                self.store_info = {**store_fingerprint(store), "visible_labels": len(self.index),
                                   "org_id": self.settings.org_id}
        except Exception as exc:  # noqa: BLE001
            self.index = None
            self.audit.write("feedback_store_unavailable", {"error": str(exc)[:300]})

    # ------------------------------------------------------------ before verification

    def local_judge(self):
        """A promoted local stance model as the judge, or None. A non-promoted model is refused, not used."""
        if not self.settings.local_stance_model:
            return None
        try:
            from .local_judge import LocalStanceJudge

            judge = LocalStanceJudge(self.settings.local_stance_model, self.settings.model_registry)
            self.judge_info = {"model_id": judge.entry["model_id"], "approved_by": judge.entry["approved_by"]}
            return judge
        except Exception as exc:  # noqa: BLE001
            self.judge_info = {"refused": str(exc)[:300], "path": self.settings.local_stance_model}
            self.audit.write("local_stance_model_refused", self.judge_info)
            return None

    def attach_examples(self, judge) -> None:
        """Give the LLM stance judge past pointer labels as examples (S5), when switched on."""
        k = self.settings.stance_examples
        if not k or judge is None or self.index is None or not len(self.index) or not hasattr(judge, "examples_for"):
            return
        index = self.index
        judge.examples_for = lambda claim_text: index.stance_examples(claim_text, k)
        judge.prompt_version = f"{judge.prompt_version}+p{k}"

    def manifest(self) -> dict | None:
        info = {}
        if self.store_info:
            info["store"] = self.store_info
            info["precedent_min_similarity"] = self.settings.precedent_min_similarity
        if self.shadow is not None:
            info["shadow_model"] = self.shadow.model_id
        if self.judge_info:
            info["local_stance_model"] = self.judge_info
        if self.settings.active_learning_slots:
            info["active_learning_slots"] = self.settings.active_learning_slots
        return info or None

    # ------------------------------------------------------------ after prioritisation

    def apply(self, verifications, priorities, org_findings, output_dir: str | Path) -> dict | None:
        from .queue import raise_queue

        precedents: dict[str, list] = {}
        if self.settings.precedents and self.index is not None and len(self.index):
            try:
                for verification in verifications:
                    cards = self.index.find(verification.claim, k=3,
                                            min_similarity=self.settings.precedent_min_similarity)
                    if cards:
                        precedents[verification.claim.claim_id] = cards
            except Exception as exc:  # noqa: BLE001
                precedents = {}
                self.audit.write("precedents_failed", {"error": str(exc)[:300]})

        shadow_by_claim: dict[str, int] = {}
        if self.shadow is not None:
            try:
                summary = self.shadow.run(verifications, Path(output_dir) / "shadow.jsonl")
                shadow_by_claim = summary.pop("by_claim")
                self.audit.write("shadow_model", summary)
            except Exception as exc:  # noqa: BLE001
                self.audit.write("shadow_model_failed", {"error": str(exc)[:300]})

        learning = None
        if self.settings.active_learning_slots:
            from .active import label_counts, learning_values

            learning = learning_values(verifications, precedents, label_counts(self.clean), shadow_by_claim)
            for priority in priorities:
                if priority.item_type == "claim" and priority.item_id in learning:
                    priority.learning = learning[priority.item_id]

        summary = raise_queue(
            priorities, org_findings=org_findings,
            precedents=precedents if self.settings.precedent_raise_queue else None,
            precedent_similarity=self.settings.precedent_raise_similarity,
            learning=learning, slots=self.settings.active_learning_slots,
            flags={v.claim.claim_id: list(v.review_flags) for v in verifications if v.review_flags},
        )
        if precedents or summary["raised"] or summary["already_queued"]:
            self.audit.write("feedback_applied", {"claims_with_precedents": len(precedents), **summary})
        return precedents or None
