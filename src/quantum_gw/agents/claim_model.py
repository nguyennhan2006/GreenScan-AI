"""S1 of llm_stages_v1: a fine-tuned T1 claim detector marks extracted sentences it reads as NOT_CLAIM.

Trained by training/kaggle/s1_final.py (multilingual-e5, 4 classes, masked numbers, Claude labels). Like
claim-quality it marks and never removes: a marked claim keeps its verdict, leaves the queue and the risk score
(scorer / prioritizer read `quality_flag`). Needs the optional `local` extra (torch, transformers); without it,
or without the folder, the stage reports why and does nothing.
"""
from __future__ import annotations

from pathlib import Path

from quantum_gw.domain.models import Claim

FLAG = "model_not_claim"


class ClaimModel:
    def __init__(self, folder: str, threshold: float = 0.5, predict=None):
        self.folder, self.threshold = folder, threshold
        self._predict = predict          # tests pass a function texts -> [P(NOT_CLAIM)]
        self.unavailable = None
        if predict is None:
            try:
                import torch  # noqa: F401
                from transformers import AutoModelForSequenceClassification, AutoTokenizer
            except ImportError:
                self.unavailable = "máy chưa cài thư viện chạy mô hình (nhóm cài đặt tuỳ chọn cho chế độ cục bộ)"
                return
            if not Path(folder).exists():
                self.unavailable = f"không thấy thư mục mô hình {folder}"
                return
            self._tok = AutoTokenizer.from_pretrained(folder)
            self._model = AutoModelForSequenceClassification.from_pretrained(folder).eval()
            self._not = self._model.config.label2id.get("NOT_CLAIM", 0)

    def p_not_claim(self, texts: list[str]) -> list[float]:
        if self._predict is not None:
            return list(self._predict(texts))
        import torch

        out = []
        with torch.no_grad():
            for i in range(0, len(texts), 32):
                x = self._tok(["query: " + t for t in texts[i:i + 32]], truncation=True, max_length=160,
                              padding=True, return_tensors="pt")
                out += torch.softmax(self._model(**x).logits, -1)[:, self._not].tolist()
        return out

    def mark(self, claims: list[Claim]) -> dict:
        if self.unavailable:
            return {"skipped": self.unavailable}
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "training"))
        try:
            from masking import mask      # the same masking the model was trained on
        except ImportError:
            def mask(text, prefix):      # noqa: E306 - the installed product has no training/ folder
                return text, {}
        todo = [c for c in claims if not c.quality_flag]
        probs = self.p_not_claim([mask(c.text, "E")[0] for c in todo]) if todo else []
        marked = 0
        for claim, p in zip(todo, probs):
            if p >= self.threshold:
                claim.quality_flag = FLAG
                marked += 1
        return {"read": len(todo), "marked": marked, "threshold": self.threshold, "folder": self.folder}
