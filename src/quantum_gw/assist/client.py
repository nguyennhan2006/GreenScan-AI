"""One language-model stage: provider from configs/routing.yaml, prompt by model family, answers cached on disk.

    stage = StageModel("explain", "claim_explanation", cache_dir=".quantum/llm_cache")
    parsed = stage.ask(lambda model: explain_messages(model, ...), key_parts=[claim, verdict, rationale])

Never fatal: no provider configured, a transport error or an unparseable reply all return None, and the caller keeps
the rules' answer. The cache key is (prompt version @ model, input), so a reply to one prompt or model is never served
for another (as verification/llm_judge.py does for the stance stage).
"""
from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from typing import Callable

from .guards import parse_json
from .prompts import version


class StageModel:
    def __init__(self, stage: str, task_type: str, gateway=None, cache_dir: str | Path | None = None):
        if gateway is None:
            from quantum_gw.providers.router import ModelGateway
            gateway = ModelGateway()
        self.stage, self.task_type, self.gateway = stage, task_type, gateway
        provider = gateway.resolve(task_type)
        self.provider_name = getattr(provider, "name", None) if provider else None
        self.model = getattr(provider, "model", None) if provider else None
        self.version = version(stage, self.model) if self.model else None
        self.stats = {"asked": 0, "cached": 0, "failed": 0}
        self._lock = threading.Lock()
        self._cache: dict[str, dict] = {}
        self._file = Path(cache_dir) / f"assist_{stage}.jsonl" if cache_dir else None
        if self._file and self._file.exists():
            for line in self._file.read_text(encoding="utf-8").splitlines():
                try:
                    row = json.loads(line)
                    self._cache[row["key"]] = row
                except (json.JSONDecodeError, KeyError):
                    continue

    @property
    def available(self) -> bool:
        return self.model is not None

    def route(self) -> str:
        return f"{self.provider_name}:{self.model}" if self.model else "none"

    def ask(self, build: Callable[[str], list[dict]], key_parts: list[str]) -> dict | None:
        if not self.available:
            return None
        key = hashlib.sha256(json.dumps([self.version, *key_parts], ensure_ascii=False).encode("utf-8")).hexdigest()
        with self._lock:
            hit = self._cache.get(key)
        if hit is not None:
            self.stats["cached"] += 1
            return hit["parsed"]
        try:
            response = self.gateway.generate(build(self.model), response_schema=None, task_type=self.task_type)
        except Exception:  # noqa: BLE001 - an outage must leave the rules' answer standing
            self.stats["failed"] += 1
            return None
        parsed = parse_json(response.text)
        if parsed is None:
            self.stats["failed"] += 1
            return None  # not cached: the next run asks again
        row = {"key": key, "parsed": parsed, "version": self.version, "provider": response.provider,
               "model": response.model}
        with self._lock:
            self.stats["asked"] += 1
            self._cache[key] = row
            if self._file:
                self._file.parent.mkdir(parents=True, exist_ok=True)
                with self._file.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        return parsed
