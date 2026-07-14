from __future__ import annotations

import json
import os
import re
from typing import Any, Protocol

import httpx


class LLMProvider(Protocol):
    def structured(self, system: str, user: str, schema_hint: dict[str, Any]) -> dict[str, Any]: ...


class OpenAICompatibleProvider:
    """Minimal adapter for providers exposing a chat-completions-compatible endpoint."""

    def __init__(self) -> None:
        self.base_url = os.getenv("QUANTUM_LLM_BASE_URL", "").rstrip("/")
        self.api_key = os.getenv("QUANTUM_LLM_API_KEY", "")
        self.model = os.getenv("QUANTUM_LLM_MODEL", "")
        if not all([self.base_url, self.api_key, self.model]):
            raise ValueError("LLM base URL, API key and model are required")

    def structured(self, system: str, user: str, schema_hint: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": user + "\nReturn JSON matching this shape:\n" + json.dumps(schema_hint),
                },
            ],
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=90) as client:
            response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise ValueError("Provider did not return a JSON object")
        return json.loads(match.group(0))
