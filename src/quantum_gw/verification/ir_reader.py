"""IR reader path behind QUANTUM_VERIFY=dual (registration agentic_ag2_product, gate ag2_dual_path_to_product).

A model fills one IR per environmental figure of a sentence, with the AG-1 prompt unchanged
(experiments/AG-1/ag1_worker.py; a test asserts they match). irlib.ground holds each reading to what the sentence
writes, and irlib.decide gives S / C / N by arithmetic in code (invariant 5). The path is a reviewer aid: it never
changes a verification's status. `dual` is the AG-2 v1 policy union_noloneS: a decisive label both paths give
without conflict, except an S that only the rules path gives. Readings are cached per (model, sentence).
"""
from __future__ import annotations

import hashlib
import json
import re
import threading
from pathlib import Path

from quantum_gw.providers.base import LLMProvider

from .irlib import IR, METRICS, SCOPES, VALUE_KINDS, decide, ground

PROMPT = """Bạn trích số liệu môi trường từ MỘT câu trong báo cáo của doanh nghiệp Việt Nam.
Với MỖI con số mô tả một chỉ số môi trường (không lấy số năm, số điều luật, số thứ tự, số tiền), trả về một đối tượng:
- "metric": một mã trong {metrics}
- "metric_text": cụm từ gọi tên chỉ số, chép NGUYÊN VĂN từ câu
- "value_text": con số, chép NGUYÊN VĂN từ câu (giữ dấu chấm, phẩy), không kèm chữ
- "multiplier_text": "nghìn", "triệu", "tỷ" nếu câu viết chữ đó ngay sau số, ngược lại ""
- "unit_text": đơn vị nguyên văn (vd "tCO2e", "kWh", "m3", "tấn", "%", "tCO2e/tấn sản phẩm"); "" nếu không có
- "value_kind": một trong {kinds} (share = tỷ lệ phần trăm của một tổng; change = mức tăng/giảm so với kỳ trước hoặc năm gốc; intensity = trên một đơn vị sản phẩm/doanh thu)
- "change_direction": "decrease" | "increase" | null (chỉ khi value_kind = change)
- "baseline_year": năm gốc nếu là change và câu có nêu, ngược lại null
- "period": năm của số liệu nếu câu NÊU RÕ; null nếu câu không nêu
- "status": "actual" (đã thực hiện) | "target" (mục tiêu, kế hoạch, cam kết)
- "scope": một trong {scopes} nếu là phát thải khí nhà kính và câu nêu phạm vi, ngược lại null
- "boundary": "group" (tập đoàn, hợp nhất) | "parent" (công ty mẹ) | "facility" (nhà máy, cơ sở cụ thể) | "unspecified"
Câu không có số liệu môi trường thì trả về danh sách rỗng.

CÂU: {sentence}

Chỉ trả lời đúng một đối tượng JSON: {{"figures": [ ... ]}}"""

_DIGIT = re.compile(r"\d")


def parse(text: str | None) -> dict | None:
    """First JSON object in the reply; None when there is none."""
    if not text:
        return None
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M)
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            if depth == 0:
                try:
                    obj = json.loads(text[start:i + 1])
                    return obj if isinstance(obj, dict) else None
                except json.JSONDecodeError:
                    break
        start = text.find("{", start + 1)
    return None


def to_irs(figures, sentence: str) -> list[IR]:
    """Readable figures, each first held to what the sentence writes (irlib.ground)."""
    out = []
    for f in figures or []:
        if isinstance(f, dict) and f.get("value_text") not in (None, ""):
            if (f := ground(f, sentence)) is None:
                continue
            try:
                ir = IR.from_dict({**f, "value_text": str(f["value_text"])})
                ir.quantity()  # unreadable number -> dropped
                out.append(ir)
            except (TypeError, ValueError):
                pass
    return out


def verdict(claim_irs: list[IR], ev_irs: list[IR], ev_text: str) -> tuple[str, list[str]]:
    """Any C -> C; every claim figure S -> S; else N."""
    if not claim_irs:
        return "N", ["không đọc được số liệu trong tuyên bố"]
    labels, why = [], []
    for c in claim_irs:
        label, steps = decide(c, ev_irs, ev_text)
        labels.append(label)
        why.append(f"{c.value_text} {c.unit_text}: {label} " + "; ".join(s[1] for s in steps)[:300])
    if "C" in labels:
        return "C", why
    return ("S" if all(x == "S" for x in labels) else "N"), why


def dual(rules_label: str, ir_label: str) -> str:
    """AG-2 v1 union_noloneS over the rules path and one IR path."""
    decisive = {lab for lab in (rules_label, ir_label) if lab in ("S", "C")}
    if len(decisive) != 1:
        return "N"
    lab = decisive.pop()
    return "N" if lab == "S" and ir_label != "S" else lab


class IRReader:
    """Reads sentences into IR figures through one provider; replies are cached in a JSONL file."""

    def __init__(self, provider: LLMProvider, cache_dir: str | Path | None = None):
        self.provider = provider
        self.model = getattr(provider, "model", provider.name)
        self.cache_path = Path(cache_dir) / "ir_reader.jsonl" if cache_dir else None
        self._cache: dict[str, str] = {}
        self._lock = threading.Lock()
        self.calls = 0
        if self.cache_path and self.cache_path.exists():
            for line in self.cache_path.open(encoding="utf-8"):
                rec = json.loads(line)
                self._cache[rec["key"]] = rec["raw"]

    def _key(self, sentence: str) -> str:
        return hashlib.sha1(f"{self.model}\n{sentence}".encode()).hexdigest()

    def raw(self, sentence: str) -> str:
        """The model's reply for one sentence; a sentence without a digit is not sent (ground keeps no figure of it)."""
        if not _DIGIT.search(sentence):
            return '{"figures": []}'
        key = self._key(sentence)
        if key in self._cache:
            return self._cache[key]
        prompt = PROMPT.format(metrics=list(METRICS), kinds=list(VALUE_KINDS), scopes=list(SCOPES), sentence=sentence)
        reply = self.provider.generate([{"role": "user", "content": prompt}]).text
        with self._lock:
            self.calls += 1
            self._cache[key] = reply
            if self.cache_path:
                self.cache_path.parent.mkdir(parents=True, exist_ok=True)
                with self.cache_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps({"key": key, "model": self.model, "raw": reply}, ensure_ascii=False) + "\n")
        return reply

    def read(self, sentence: str) -> list[IR]:
        obj = parse(self.raw(sentence)) or {}
        figures = obj.get("figures") if isinstance(obj.get("figures"), list) else []
        return to_irs(figures, sentence)

    def label(self, claim: str, evidence: str) -> tuple[str, list[str]]:
        return verdict(self.read(claim), self.read(evidence), evidence)
