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
    candidate_k: int = 20
    lexical_weight: float = 0.55
    semantic_weight: float = 0.45
    minimum_score: float = 0.12
    exclude_same_chunk: bool = True


class VerificationSettings(BaseModel):
    numeric_relative_tolerance: float = 0.12
    strong_support_score: float = 0.46
    partial_support_score: float = 0.22
    injection_policy: str = "exclude"


class ReviewSettings(BaseModel):
    high_risk_threshold: int = 50
    critical_risk_threshold: int = 75
    require_human_for_legal_conflict: bool = True


class AppSettings(BaseModel):
    version: str = "pipeline-v1"
    language: str = "vi"
    runs_dir: str = ".quantum/runs"
    intake: IntakeSettings = Field(default_factory=IntakeSettings)
    claim_extraction: ClaimSettings = Field(default_factory=ClaimSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
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
    return settings
