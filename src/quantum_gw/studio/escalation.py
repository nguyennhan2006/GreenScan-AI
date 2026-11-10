"""When a low-confidence case may be sent to an LLM, and when it must go to a person.

Decided by Nhân on 14/10 (plan §5.3): offline by default. A case is escalated
to the LLM API only if (a) the student's or the verifier's confidence is below
τ, or rules and student disagree, AND (b) the document's confidentiality class
allows it -- class A (public) yes; class B (internal) and C (professional
secrecy) never, those go to a reviewer instead (knowledge doc 02 §6, personal
data law 91/2025).

τ is calibrated on dev in experiment B6 and recorded in
`configs/measurement_decisions.yaml` under `studio_escalation.tau` once the
team agrees. Until then it is None and nothing is escalated: an uncalibrated
threshold would be a number chosen by taste.
"""

from __future__ import annotations

from pathlib import Path

import yaml

DOC_CLASSES = {
    "A": "Công khai (đã công bố)",
    "B": "Nội bộ",
    "C": "Mật nghề nghiệp",
}


def configured_tau(path: str | Path = "configs/measurement_decisions.yaml") -> float | None:
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return None
    value = (data.get("studio_escalation") or {}).get("tau")
    return float(value) if isinstance(value, (int, float)) else None


def decide(confidence: float | None, doc_class: str, tau: float | None, cloud_allowed: bool,
           disagreement: bool = False) -> dict:
    """`{"route": "local" | "llm" | "human", "reason": ...}` for one case."""
    low = disagreement or (tau is not None and confidence is not None and confidence < tau)
    if not low:
        if tau is None and not disagreement:
            return {"route": "local", "reason": "Ngưỡng chưa hiệu chỉnh: không chuyển lên mô hình."}
        return {"route": "local", "reason": "Độ tin cậy đủ; xử lý bằng luật và mẫu."}
    if doc_class != "A":
        return {"route": "human", "reason": f"Tài liệu lớp {doc_class} ({DOC_CLASSES.get(doc_class, '?')}): không gửi ra ngoài, chuyển người duyệt."}
    if not cloud_allowed:
        return {"route": "human", "reason": "Chế độ ngoại tuyến: không gọi mô hình, chuyển người soát xét."}
    return {"route": "llm", "reason": "Độ tin cậy thấp, tài liệu công khai, chế độ có mạng đang bật."}
