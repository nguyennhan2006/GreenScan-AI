from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


def load_dotenv(path: str | Path = ".env", *, override: bool = False) -> int:
    """Read a .env file into os.environ.

    README and .env.example both tell the operator to configure the gateway via
    .env, but nothing in the process ever read that file -- only docker-compose's
    `env_file` did. Pasting an API key into .env and starting the API locally
    therefore did nothing, silently, which is the worst way for a credential to
    fail.

    Deliberately stdlib-only (no python-dotenv dependency) and real environment
    variables win by default, so `FPT_LLM_API_KEY=... quantum-agent serve` still
    beats the file.
    """
    p = Path(path)
    if not p.is_file():
        return 0
    loaded = 0
    # split("\n"): a value may legitimately contain U+2028 and splitlines() would
    # break the line in two.
    for raw in p.read_text(encoding="utf-8").split("\n"):
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            continue
        if override or key not in os.environ:
            os.environ[key] = value
            loaded += 1
    return loaded


# Load once at import so every entry point (CLI, API, scripts) sees the same
# configuration without each having to remember to call this.
load_dotenv(os.environ.get("QUANTUM_ENV_FILE", ".env"))


# One switch instead of twenty variables. Choosing the hardware tier is the only
# decision most operators should have to make; a profile fills in what the
# environment and .env leave unset, so any variable written explicitly still wins.
# Throughput behind each tier: docs/04-data-ai/MODEL_ROUTING_AND_HARDWARE.md.
PROFILES: dict[str, dict[str, str]] = {
    # Any laptop, no key, no network: rules, arithmetic and lexical retrieval.
    # Measured 2026-10-05 on an i7-1355U without GPU: HPG BCPTBV 2025 + BCTN 2024
    # in 116 s, 1.3 GB peak memory.
    "offline": {
        "QUANTUM_LLM_STANCE": "off",
        "EMBEDDING_PROVIDER": "lite",
        "RERANKER_PROVIDER": "none",
        "LOCAL_LLM_BASE_URL": "",
    },
    # The same laptop plus a key for FPT AI Marketplace (Vietnamese cloud): a
    # model reads only the claim-evidence pairs the rules could not decide, and
    # answers are cached so a re-run calls nothing.
    "cloud": {
        "QUANTUM_LLM_STANCE": "on_ambiguous",
        "LLM_PROVIDER": "fpt",
        "LLM_FALLBACK_ORDER": "fpt",
        "LOCAL_LLM_BASE_URL": "",
        "EMBEDDING_PROVIDER": "lite",
        "RERANKER_PROVIDER": "none",
    },
    # A server with one GPU serving an open model through vLLM on port 8001
    # (8000 is GreenScan's own API), with local BGE-M3 and reranker on CUDA.
    "gpu": {
        "QUANTUM_LLM_STANCE": "on_ambiguous",
        "LLM_PROVIDER": "local",
        "LLM_FALLBACK_ORDER": "local,fpt",
        "LOCAL_LLM_PROVIDER": "openai_compatible",
        "LOCAL_LLM_BASE_URL": "http://localhost:8001/v1",
        "EMBEDDING_PROVIDER": "local",
        "LOCAL_EMBEDDING_DEVICE": "cuda",
        "RERANKER_PROVIDER": "local",
        "LOCAL_RERANKER_DEVICE": "cuda",
    },
}


def apply_profile(name: str | None = None) -> str:
    """Fill unset variables from `QUANTUM_PROFILE`; returns the profile applied."""
    profile = (name or os.environ.get("QUANTUM_PROFILE") or "").strip().lower()
    if not profile:
        return ""
    if profile not in PROFILES:
        raise ValueError(f"QUANTUM_PROFILE must be one of {sorted(PROFILES)}, not {profile!r}")
    for key, value in PROFILES[profile].items():
        os.environ.setdefault(key, value)
    return profile


apply_profile()


class IntakeSettings(BaseModel):
    # A passage is a few sentences of one paragraph: small enough to be about
    # one thing, so a stance cue or a figure in it belongs to the claim it is
    # retrieved for. 1,400 characters made a whole page one passage.
    chunk_size_chars: int = 600
    chunk_overlap_chars: int = 0
    max_sentences_per_chunk: int = 3
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
    # Best candidates always returned even when they score below minimum_score,
    # marked `below_threshold`. Separates "no passage speaks to this claim" from
    # "no passage looked like this claim" — see HybridRetriever._admissible.
    floor_k: int = 3
    exclude_same_chunk: bool = True


class EmbeddingSettings(BaseModel):
    provider: str = "lite"  # lite (char n-gram, no download) | local (BGE-M3) | http (TEI)
    model: str = "BAAI/bge-m3"
    device: str = "cuda"
    batch_size: int = 16
    base_url: str = ""
    max_length: int = 512
    # Encoded passages are kept here by (model, text); empty disables the cache.
    cache_dir: str = ".quantum/emb_cache"
    # provider "fpt": the model served by FPT Marketplace /embeddings.
    fpt_model: str = "Vietnamese_Embedding"


class RerankerSettings(BaseModel):
    provider: str = "none"  # none | local (bge-reranker-v2-m3) | http (TEI /rerank)
    model: str = "BAAI/bge-reranker-v2-m3"
    device: str = "cuda"
    base_url: str = ""
    candidate_k: int = 30
    final_k: int = 5
    # provider "fpt": the cross-encoder served by FPT Marketplace /rerank.
    fpt_model: str = "bge-reranker-v2-m3"


class VerificationSettings(BaseModel):
    # Upper bound on the precision-derived tolerance (policy precision-v1 in
    # the verifier). Not a tolerance itself any more: two figures agree when
    # they differ by no more than the coarser published precision, capped here.
    numeric_relative_tolerance: float = 0.10
    # Relative error at or above which two comparable figures contradict. Kept as a
    # named setting (was a literal 0.35 in two places) so it can be swept on the
    # numeric-pair gold set; the value itself is not yet evidence-based (ISSUES N1).
    numeric_contradiction_error: float = 0.35
    # A cue-phrase support (no figure) becomes SUPPORTED only when this many of
    # the claim's stated attributes (metric, period, baseline, scopes, direction)
    # appear in the confirming sentences. Hypothesis pending the gold sweep (RQ7).
    support_min_attributes: int = 2
    strong_support_score: float = 0.46
    partial_support_score: float = 0.22
    injection_policy: str = "exclude"
    # Lexical overlap a passage needs before a stance cue counts. Passages from
    # an authority (a regulator's order, a court judgment) bypass this: BNY-2022's
    # refutation shares only "esg" and "the" with the claim it refutes.
    qualitative_min_overlap: float = 0.20
    # off | on_ambiguous. `on_ambiguous` lets a language model rule on passages
    # the deterministic layers declined, and marks every such claim for human
    # review. Off by default so the shipped pipeline stays reproducible.
    llm_stance: str = "off"
    llm_stance_min_overlap: float = 0.12
    # Concurrent calls when the whole batch is asked up front, and where answers
    # are kept so a re-run of the same documents calls nothing.
    llm_workers: int = 8
    llm_cache_dir: str = ".quantum/llm_cache"
    # May a model's stance alone make a claim SUPPORTED or CONTRADICTED? No,
    # until the gold set measures its precision per relation: unguarded on HPG
    # (28/09) it produced 10 CONTRADICTED and 2 CRITICAL on a control company.
    llm_stance_decisive: bool = False


class LegalSettings(BaseModel):
    enabled: bool = True
    registry_file: str = "configs/legal/LEGAL_SOURCE_REGISTRY.yaml"
    rule_pack_file: str = "configs/legal/rule_pack_vn_green_v0.1.yaml"
    # historical_compliance (law as it stood when the claim was published) or
    # current_policy_alignment (today's criteria). They are different questions
    # and a company can be compliant on one and misaligned on the other, so the
    # mode is explicit rather than inferred.
    check_mode: str = "current_policy_alignment"


class ReviewSettings(BaseModel):
    require_human_for_legal_conflict: bool = True
    # A claim nothing contradicts may not exceed this band, whatever the
    # missing-attribute penalties add up to (ISSUES N5, D-2026-09-22-03).
    # Lift only when the bands are calibrated on the gold set.
    severity_cap_without_contradiction: str = "medium"


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
    # Empty = not configured. The old default, http://localhost:8000/v1, is the
    # port GreenScan's own API listens on: a fresh checkout reported a local
    # Qwen3-8B as configured and, with the stance model on, sent its prompts to
    # itself. A local model is something an operator starts and names.
    local_base_url: str = ""
    local_api_key: str = ""
    local_model: str = "Qwen/Qwen3-8B"
    local_timeout_seconds: float = 180
    local_max_tokens: int = 4096

    fpt_base_url: str = ""
    fpt_api_key: str = ""
    fpt_model: str = ""
    fpt_api_format: str = "openai_compatible"  # openai_compatible | fpt_native
    fpt_timeout_seconds: float = 180
    fpt_max_tokens: int = 4096

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
        local_base_url=env("LOCAL_LLM_BASE_URL", ""),
        local_api_key=env("LOCAL_LLM_API_KEY", ""),
        local_model=env("LOCAL_LLM_MODEL", "Qwen/Qwen3-8B"),
        local_timeout_seconds=float(env("LOCAL_LLM_TIMEOUT_SECONDS", "180")),
        local_max_tokens=int(env("LOCAL_LLM_MAX_TOKENS", "4096")),
        fpt_base_url=env("FPT_LLM_BASE_URL", ""),
        fpt_api_key=env("FPT_LLM_API_KEY", ""),
        fpt_model=env("FPT_LLM_MODEL", ""),
        fpt_api_format=env("FPT_LLM_API_FORMAT", "openai_compatible"),
        fpt_timeout_seconds=float(env("FPT_LLM_TIMEOUT_SECONDS", "180")),
        fpt_max_tokens=int(env("FPT_LLM_MAX_TOKENS", "4096")),
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
    # Where a reviewer should start (agents/prioritizer.py). Separate file from the
    # risk rubric because they answer different questions and change at different times.
    priority_policy: str = "configs/priority_v1.yaml"
    # Which body of documents a run searched. Recorded in the manifest so a
    # re-run can be told apart from a run over a different corpus (P11).
    corpus_version: str = "run-inputs"
    review: ReviewSettings = Field(default_factory=ReviewSettings)
    legal: LegalSettings = Field(default_factory=LegalSettings)
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
    settings.embedding.max_length = int(
        os.getenv("LOCAL_EMBEDDING_MAX_LENGTH", str(settings.embedding.max_length))
    )
    settings.embedding.cache_dir = os.getenv("EMBEDDING_CACHE_DIR", settings.embedding.cache_dir)
    settings.embedding.fpt_model = os.getenv("FPT_EMBEDDING_MODEL", settings.embedding.fpt_model)
    settings.reranker.fpt_model = os.getenv("FPT_RERANKER_MODEL", settings.reranker.fpt_model)
    settings.reranker.provider = os.getenv("RERANKER_PROVIDER", settings.reranker.provider)
    settings.reranker.model = os.getenv("LOCAL_RERANKER_MODEL", settings.reranker.model)
    settings.reranker.device = os.getenv("LOCAL_RERANKER_DEVICE", settings.reranker.device)
    settings.reranker.base_url = os.getenv("RERANKER_BASE_URL", settings.reranker.base_url)
    settings.reranker.candidate_k = int(
        os.getenv("RERANK_CANDIDATE_K", str(settings.reranker.candidate_k))
    )
    settings.reranker.final_k = int(os.getenv("RERANK_FINAL_K", str(settings.reranker.final_k)))
    # The deployment decides whether a language model is consulted; the YAML
    # default stays off so a checkout without .env runs deterministically.
    stance = os.getenv("QUANTUM_LLM_STANCE", settings.verification.llm_stance).strip().lower()
    if stance not in {"off", "on_ambiguous"}:
        raise ValueError(f"QUANTUM_LLM_STANCE must be off or on_ambiguous, not {stance!r}")
    settings.verification.llm_stance = stance
    settings.verification.llm_workers = int(
        os.getenv("QUANTUM_LLM_WORKERS", str(settings.verification.llm_workers))
    )
    settings.verification.llm_cache_dir = os.getenv(
        "QUANTUM_LLM_CACHE_DIR", settings.verification.llm_cache_dir
    )
    return settings
