from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class IntakeSettings(BaseModel):
    chunk_size_chars: int = 1400
    chunk_overlap_chars: int = 180
    min_native_text_chars: int = 40
    extract_tables: bool = True
    ocr_enabled: bool = True
    ocr_languages: str = "vie+eng"
    tesseract_command: str = "tesseract"


class ClaimSettings(BaseModel):
    provider: str = "heuristic"
    minimum_confidence: float = 0.4
    include_vague_claims: bool = True


class RetrievalSettings(BaseModel):
    top_k: int = 5
    candidate_k: int = 30
    fusion: str = "rrf"  # rrf | weighted (rrf only changes ranking; scores stay weighted)
    rrf_k: int = 60
    lexical_weight: float = 0.55
    semantic_weight: float = 0.45
    minimum_score: float = 0.12
    exclude_same_chunk: bool = True


class EmbeddingSettings(BaseModel):
    provider: str = "lite"  # lite (char n-gram, no download) | local (BGE-M3) | http (TEI)
    model: str = "BAAI/bge-m3"
    device: str = "cuda"
    batch_size: int = 16
    base_url: str = ""


class RerankerSettings(BaseModel):
    provider: str = "none"  # none | local (bge-reranker-v2-m3) | http (TEI /rerank)
    model: str = "BAAI/bge-reranker-v2-m3"
    device: str = "cuda"
    base_url: str = ""
    candidate_k: int = 30
    final_k: int = 5


class VerificationSettings(BaseModel):
    numeric_relative_tolerance: float = 0.12
    strong_support_score: float = 0.46
    partial_support_score: float = 0.22
    injection_policy: str = "exclude"


class ReviewSettings(BaseModel):
    high_risk_threshold: int = 50
    critical_risk_threshold: int = 75
    require_human_for_legal_conflict: bool = True


class GatewaySettings(BaseModel):
    """Model-gateway configuration. Loaded from environment variables only.

    Every field with a key may stay empty: the application must start and the
    deterministic pipeline must run with all cloud keys blank.
    """

    provider: str = "local"
    fallback_order: list[str] = Field(
        default_factory=lambda: ["local", "fpt", "gemini", "openai", "anthropic"]
    )
    routing_file: str = "configs/routing.yaml"

    local_provider: str = "openai_compatible"  # openai_compatible (vLLM) | ollama
    local_base_url: str = "http://localhost:8000/v1"
    local_api_key: str = ""
    local_model: str = "Qwen/Qwen3-8B"
    local_timeout_seconds: float = 180
    local_max_tokens: int = 4096

    fpt_base_url: str = ""
    fpt_api_key: str = ""
    fpt_model: str = ""
    fpt_api_format: str = "openai_compatible"  # openai_compatible | fpt_native

    gemini_api_key: str = ""
    gemini_model: str = ""
    openai_api_key: str = ""
    openai_model: str = ""
    anthropic_api_key: str = ""
    anthropic_model: str = ""
    openrouter_api_key: str = ""
    openrouter_model: str = ""


def load_gateway_settings() -> GatewaySettings:
    env = os.getenv
    fallback = [
        item.strip()
        for item in env("LLM_FALLBACK_ORDER", "local,fpt,gemini,openai,anthropic").split(",")
        if item.strip()
    ]
    return GatewaySettings(
        provider=env("LLM_PROVIDER", "local"),
        fallback_order=fallback,
        routing_file=env("LLM_ROUTING_FILE", "configs/routing.yaml"),
        local_provider=env("LOCAL_LLM_PROVIDER", "openai_compatible"),
        local_base_url=env("LOCAL_LLM_BASE_URL", "http://localhost:8000/v1"),
        local_api_key=env("LOCAL_LLM_API_KEY", ""),
        local_model=env("LOCAL_LLM_MODEL", "Qwen/Qwen3-8B"),
        local_timeout_seconds=float(env("LOCAL_LLM_TIMEOUT_SECONDS", "180")),
        local_max_tokens=int(env("LOCAL_LLM_MAX_TOKENS", "4096")),
        fpt_base_url=env("FPT_LLM_BASE_URL", ""),
        fpt_api_key=env("FPT_LLM_API_KEY", ""),
        fpt_model=env("FPT_LLM_MODEL", ""),
        fpt_api_format=env("FPT_LLM_API_FORMAT", "openai_compatible"),
        gemini_api_key=env("GEMINI_API_KEY", ""),
        gemini_model=env("GEMINI_MODEL", ""),
        openai_api_key=env("OPENAI_API_KEY", ""),
        openai_model=env("OPENAI_MODEL", ""),
        anthropic_api_key=env("ANTHROPIC_API_KEY", ""),
        anthropic_model=env("ANTHROPIC_MODEL", ""),
        openrouter_api_key=env("OPENROUTER_API_KEY", ""),
        openrouter_model=env("OPENROUTER_MODEL", ""),
    )


class AppSettings(BaseModel):
    version: str = "pipeline-v1"
    language: str = "vi"
    runs_dir: str = ".quantum/runs"
    intake: IntakeSettings = Field(default_factory=IntakeSettings)
    claim_extraction: ClaimSettings = Field(default_factory=ClaimSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    reranker: RerankerSettings = Field(default_factory=RerankerSettings)
    verification: VerificationSettings = Field(default_factory=VerificationSettings)
    scoring: dict[str, Any] = Field(default_factory=lambda: {"rubric_file": "configs/scoring_v1.yaml"})
    review: ReviewSettings = Field(default_factory=ReviewSettings)
    raw: dict[str, Any] = Field(default_factory=dict, exclude=True)

    def stable_hash(self) -> str:
        payload = self.model_dump(exclude={"raw"}, mode="json")
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def load_settings(path: str | None = None) -> AppSettings:
    selected = path or os.getenv("QUANTUM_CONFIG", "configs/default.yaml")
    config_path = Path(selected)
    if not config_path.exists():
        package_root = Path(__file__).resolve().parents[2]
        alternative = package_root / selected
        if alternative.exists():
            config_path = alternative
        else:
            raise FileNotFoundError(f"Configuration not found: {selected}")
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    settings = AppSettings.model_validate(raw)
    settings.raw = raw
    settings.runs_dir = os.getenv("QUANTUM_RUNS_DIR", settings.runs_dir)
    settings.intake.ocr_enabled = os.getenv(
        "QUANTUM_OCR_ENABLED", str(settings.intake.ocr_enabled)
    ).lower() in {"1", "true", "yes"}
    settings.intake.ocr_languages = os.getenv(
        "QUANTUM_OCR_LANGUAGES", settings.intake.ocr_languages
    )
    settings.intake.tesseract_command = os.getenv(
        "QUANTUM_TESSERACT_COMMAND", settings.intake.tesseract_command
    )
    settings.embedding.provider = os.getenv("EMBEDDING_PROVIDER", settings.embedding.provider)
    settings.embedding.model = os.getenv("LOCAL_EMBEDDING_MODEL", settings.embedding.model)
    settings.embedding.device = os.getenv("LOCAL_EMBEDDING_DEVICE", settings.embedding.device)
    settings.embedding.batch_size = int(
        os.getenv("LOCAL_EMBEDDING_BATCH_SIZE", str(settings.embedding.batch_size))
    )
    settings.embedding.base_url = os.getenv("EMBEDDING_BASE_URL", settings.embedding.base_url)
    settings.reranker.provider = os.getenv("RERANKER_PROVIDER", settings.reranker.provider)
    settings.reranker.model = os.getenv("LOCAL_RERANKER_MODEL", settings.reranker.model)
    settings.reranker.device = os.getenv("LOCAL_RERANKER_DEVICE", settings.reranker.device)
    settings.reranker.base_url = os.getenv("RERANKER_BASE_URL", settings.reranker.base_url)
    settings.reranker.candidate_k = int(
        os.getenv("RERANK_CANDIDATE_K", str(settings.reranker.candidate_k))
    )
    settings.reranker.final_k = int(os.getenv("RERANK_FINAL_K", str(settings.reranker.final_k)))
    return settings
