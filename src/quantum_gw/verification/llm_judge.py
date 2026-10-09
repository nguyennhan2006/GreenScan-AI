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

Measured on the HPG run of 25/09: 713 of 780 claim-evidence pairs reached this
point, at 4-6 s per call to GLM-5.2. Called one at a time from inside the
verifier that is an hour per run and the same hour again on every re-run, so
answers are cached on disk (keyed by prompt version, serving model, claim and
passage) and `prefetch` asks for the whole batch concurrently before the
verifier walks the claims. A re-run of the same documents calls nothing, which
is also what lets a demo run without the network.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from quantum_gw.providers.router import ModelGateway

from .stance import CONTEXT, CONTRADICTS, PARTIAL, SUPPORTS, StanceSignal

TASK_TYPE = "qualitative_stance"
# Bump when SYSTEM_PROMPT or the message layout changes: cached answers to the
# old prompt must stop being served.
PROMPT_VERSION = "stance-v1"

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
    def __init__(
        self,
        gateway: ModelGateway | None = None,
        cache_dir: str | Path | None = None,
        workers: int = 8,
    ):
        self.gateway = gateway or ModelGateway()
        self.workers = max(1, workers)
        self.route = "|".join(self.gateway.route(TASK_TYPE)) or "none"
        self._cache: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._cache_file = Path(cache_dir) / "stance_cache.jsonl" if cache_dir else None
        if self._cache_file and self._cache_file.exists():
            for line in self._cache_file.read_text(encoding="utf-8").splitlines():
                try:
                    entry = json.loads(line)
                    self._cache[entry["key"]] = entry
                except (json.JSONDecodeError, KeyError):
                    continue
        self.stats: Counter = Counter()

    @property
    def version(self) -> str:
        """What the run manifest records: the prompt and the models that may answer it."""
        return f"{PROMPT_VERSION}@{self.route}"

    def _key(self, claim_text: str, evidence_text: str) -> str:
        payload = json.dumps([PROMPT_VERSION, self.route, claim_text, evidence_text], ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def judge(self, claim_text: str, evidence_text: str) -> StanceSignal | None:
        key = self._key(claim_text, evidence_text)
        with self._lock:
            entry = self._cache.get(key)
        if entry is None:
            entry = self._ask(claim_text, evidence_text, key)
        else:
            self.stats["cache_hit"] += 1
        if entry is None:
            return None
        return StanceSignal(
            relation=entry["relation"],
            reason=f"[{entry['provider']}/{entry['model']}] {entry['reason']}",
            method="llm",
        )

    def prefetch(self, pairs: list[tuple[str, str]]) -> dict:
        """Ask for every uncached pair at once, so `judge` later only reads the cache."""
        started = time.perf_counter()
        todo, seen = [], set()
        for claim_text, evidence_text in pairs:
            key = self._key(claim_text, evidence_text)
            if key in seen or key in self._cache:
                continue
            seen.add(key)
            todo.append((claim_text, evidence_text, key))
        before = Counter(self.stats)
        if todo:
            with ThreadPoolExecutor(max_workers=self.workers) as pool:
                list(pool.map(lambda job: self._ask(*job, retries=1), todo))
        called = self.stats - before
        return {
            "pairs": len(pairs),
            "not_asked": len(pairs) - len(todo),   # cached, or a repeat within this batch
            "asked": len(todo),
            "answered": called["answered"],
            "failed": called["failed"],
            "served_by": {k[3:]: v for k, v in called.items() if k.startswith("by:")},
            # What the provider billed, as it reported it. Without these the
            # cost of a run could only ever be estimated.
            "tokens": {"prompt": called["prompt_tokens"], "completion": called["completion_tokens"]},
            "seconds": round(time.perf_counter() - started, 1),
            "route": self.route,
        }

    def _ask(self, claim_text: str, evidence_text: str, key: str, retries: int = 0) -> dict | None:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"TUYÊN BỐ:\n{claim_text}\n\nĐOẠN BẰNG CHỨNG:\n{evidence_text}",
            },
        ]
        for attempt in range(retries + 1):
            try:
                response = self.gateway.generate(
                    messages, response_schema=RESPONSE_SCHEMA, task_type=TASK_TYPE
                )
            except Exception:  # noqa: BLE001
                # Deliberately broad: no provider configured, a transport error and
                # a provider SDK raising something of its own must all leave the
                # deterministic verdict standing rather than fail the run.
                if attempt < retries:
                    time.sleep(2 * (attempt + 1))
                    continue
                self._count("failed")
                return None
            parsed = response.parsed or {}
            relation = str(parsed.get("relation", "")).strip().upper()
            if relation not in VALID:
                # An unparseable answer is not cached: the next run asks again.
                self._count("failed")
                return None
            entry = {
                "key": key,
                "relation": relation,
                "reason": str(parsed.get("reason", "")).strip() or "Không có giải thích.",
                "provider": response.provider,
                "model": response.model,
                "prompt_version": PROMPT_VERSION,
            }
            self._store(entry)
            self._count("answered", f"by:{response.provider}/{response.model}")
            usage = response.usage or {}
            with self._lock:
                self.stats["prompt_tokens"] += int(usage.get("prompt_tokens") or 0)
                self.stats["completion_tokens"] += int(usage.get("completion_tokens") or 0)
            return entry
        return None

    def _count(self, *names: str) -> None:
        with self._lock:
            for name in names:
                self.stats[name] += 1

    def _store(self, entry: dict) -> None:
        with self._lock:
            self._cache[entry["key"]] = entry
            if self._cache_file:
                self._cache_file.parent.mkdir(parents=True, exist_ok=True)
                with self._cache_file.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
