"""Escalation path for passages the cue lexicon cannot decide.

Reached only when the deterministic layers have both declined: no comparable
figures, no cue phrase, but a passage that retrieval says is about this claim.
That gap is exactly where the pipeline used to answer PARTIALLY_SUPPORTED by
default, which is the failure mode with the worst consequences — it reads
"we could not tell" as "partly true".

Three properties this is built to keep:

    Off by default. `verification.llm_stance: off` in configs/default.yaml, so
    the shipped pipeline stays reproducible and gate G3 keeps its meaning.

    Never decisive on its own. Every stance from here sets
    `requires_llm_review`, and the caller marks the claim for a human. A model
    may point a reviewer at a passage; it may not close a finding.

    Never fatal. No provider configured, a transport error or unparseable
    output all return None and the deterministic reading stands. An LLM outage
    must not change a verdict.
"""

from __future__ import annotations

from quantum_gw.providers.router import ModelGateway

from .stance import CONTEXT, CONTRADICTS, PARTIAL, SUPPORTS, StanceSignal

TASK_TYPE = "qualitative_stance"

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "relation": {"type": "string", "enum": [SUPPORTS, CONTRADICTS, PARTIAL, CONTEXT]},
        "reason": {"type": "string"},
    },
    "required": ["relation", "reason"],
}

SYSTEM_PROMPT = (
    "Bạn là trợ lý kiểm chứng tuyên bố môi trường. Với một TUYÊN BỐ và một ĐOẠN BẰNG CHỨNG, "
    "hãy xác định lập trường của đoạn bằng chứng đối với tuyên bố.\n"
    "SUPPORTS: đoạn văn xác nhận tuyên bố.\n"
    "CONTRADICTS: đoạn văn phủ định tuyên bố, hoặc cho thấy tuyên bố thiếu sót, "
    "sai lệch, chưa được thực hiện hoặc không được kiểm soát.\n"
    "PARTIAL: cùng chủ đề, xác nhận một phần nhưng chưa đủ.\n"
    "CONTEXT: liên quan nhưng không xác nhận cũng không bác bỏ.\n"
    "Chỉ dựa vào đoạn bằng chứng được cung cấp. Im lặng không phải là bác bỏ: nếu đoạn văn "
    "không nói gì về tuyên bố, trả lời CONTEXT. Không suy diễn ngoài văn bản."
)

VALID = {SUPPORTS, CONTRADICTS, PARTIAL, CONTEXT}


class LLMStanceJudge:
    def __init__(self, gateway: ModelGateway | None = None):
        self.gateway = gateway or ModelGateway()

    def judge(self, claim_text: str, evidence_text: str) -> StanceSignal | None:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"TUYÊN BỐ:\n{claim_text}\n\nĐOẠN BẰNG CHỨNG:\n{evidence_text}",
            },
        ]
        try:
            response = self.gateway.generate(
                messages, response_schema=RESPONSE_SCHEMA, task_type=TASK_TYPE
            )
        except Exception:  # noqa: BLE001
            # Deliberately broad: no provider configured, a transport error and a
            # provider SDK raising something of its own must all leave the
            # deterministic verdict standing rather than fail the run.
            return None

        parsed = response.parsed or {}
        relation = str(parsed.get("relation", "")).strip().upper()
        if relation not in VALID:
            return None
        reason = str(parsed.get("reason", "")).strip() or "Không có giải thích."
        return StanceSignal(
            relation=relation,
            reason=f"[{response.provider}/{response.model}] {reason}",
            method="llm",
        )
