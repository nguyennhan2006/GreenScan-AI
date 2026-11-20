from __future__ import annotations

import hashlib
import json
import os
import re
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
        # llm_stages_v1 gate s6 met by Qwen3-4B / 32B (configs/measurement_decisions.yaml): an explanation beside
        # the rules rationale for the review queue. Not in offline (81 s per claim on the laptop) nor in cloud
        # (Groq is allowed for public documents only, and the profile cannot tell).
        "QUANTUM_ASSIST_EXPLAIN": "queue",
        "LLM_PROVIDER": "local",
        "LLM_FALLBACK_ORDER": "local,fpt",
        "LOCAL_LLM_PROVIDER": "openai_compatible",
        "LOCAL_LLM_BASE_URL": "http://localhost:8001/v1",
        "EMBEDDING_PROVIDER": "local",
        "LOCAL_EMBEDDING_DEVICE": "cuda",
        "RERANKER_PROVIDER": "local",
        "LOCAL_RERANKER_DEVICE": "cuda",
    },
    # Phương án 2 (13/11/2026): GreenScan stays on the laptop; a rented GPU (vast.ai A100,
    # deploy/vastai_a100/30_serve.sh) serves the reader through vLLM's OpenAI API. Retrieval stays local (lite), so
    # only claim/evidence text of the review path leaves the machine. Point it with QUANTUM_SELFHOST_URL
    # (http://<ip>:8001/v1), QUANTUM_SELFHOST_KEY (the server's --api-key) and QUANTUM_SELFHOST_MODEL (its
    # --served-model-name). Same reader flags as "gpu"; the offline profile is untouched.
    "selfhost": {
        "QUANTUM_LLM_STANCE": "on_ambiguous",
        "QUANTUM_ASSIST_EXPLAIN": "queue",
        "LLM_PROVIDER": "local",
        "LLM_FALLBACK_ORDER": "local",
        "LOCAL_LLM_PROVIDER": "openai_compatible",
        "EMBEDDING_PROVIDER": "lite",
        "RERANKER_PROVIDER": "none",
    },
}
SELFHOST_ENV = {"QUANTUM_SELFHOST_URL": "LOCAL_LLM_BASE_URL", "QUANTUM_SELFHOST_KEY": "LOCAL_LLM_API_KEY",
                "QUANTUM_SELFHOST_MODEL": "LOCAL_LLM_MODEL"}
SELFHOST_DEFAULT_MODEL = "openai/gpt-oss-120b"


def apply_profile(name: str | None = None) -> str:
    """Fill unset variables from `QUANTUM_PROFILE`; returns the profile applied."""
    profile = (name or os.environ.get("QUANTUM_PROFILE") or "").strip().lower()
    if not profile:
        return ""
    if profile not in PROFILES:
        raise ValueError(f"QUANTUM_PROFILE must be one of {sorted(PROFILES)}, not {profile!r}")
    for key, value in PROFILES[profile].items():
        os.environ.setdefault(key, value)
    if profile == "selfhost":
        for src, dst in SELFHOST_ENV.items():
            if os.environ.get(src):
                os.environ.setdefault(dst, os.environ[src])
        os.environ.setdefault("LOCAL_LLM_MODEL", SELFHOST_DEFAULT_MODEL)
        if not os.environ.get("LOCAL_LLM_BASE_URL"):
            raise ValueError("QUANTUM_PROFILE=selfhost needs QUANTUM_SELFHOST_URL (e.g. http://<vast-ip>:8001/v1)")
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
    # table-shape-v1 (16/11/2026): pdfplumber reports the frame of an infographic page as a one-cell "table"
    # and reads it line by line across columns ("...theo tiêu 90%"). Keep a table only when at least two rows
    # have two filled cells and no cell runs over a dozen lines. Env QUANTUM_TABLE_SHAPE_FILTER=off.
    table_shape_filter: bool = True
    # page-regions-v1 (17/11/2026): read each PDF page as typed regions (parsers/layout.py): prose in column
    # order, ruled and unruled tables as rows with caption, column headers, unit and period, on the text layer
    # and on a scan alike. Env QUANTUM_LAYOUT_REGIONS=off restores block order and pdfplumber tables.
    layout_regions: bool = True
    ocr_enabled: bool = True
    ocr_languages: str = "vie+eng"
    tesseract_command: str = "tesseract"


class ClaimSettings(BaseModel):
    provider: str = "heuristic"
    minimum_confidence: float = 0.4
    include_vague_claims: bool = True
    # claim-quality-v1 (2026-11-09): mark sentences that are probably not claims
    # (layout glue, a standard's title, a quoted decree). Marking only: verdicts
    # unchanged, the sentence leaves the queue and the risk score.
    flag_suspect_non_claims: bool = True
    # claim-precision-v1 (15/11/2026): a generic sustainability sentence needs an environmental word
    # (môi trường, phát thải, năng lượng, nước, chất thải, xanh...) to be a claim. Env QUANTUM_REQUIRE_ENV_ANCHOR.
    require_environment_anchor: bool = True
    # S1 of llm_stages_v1: folder of a fine-tuned T1 claim detector (training/kaggle/s1_final.py). When set,
    # a sentence it reads as NOT_CLAIM is marked like claim-quality does (mark, never remove). Env QUANTUM_CLAIM_MODEL.
    claim_model_dir: str = ""
    claim_model_threshold: float = 0.5
    # claim-typing-v2 (15/11/2026): when no claim_type matches, try fallback_claim_types (resource use)
    # then metric_disclosure (known metric + a figure that is not a year). Env QUANTUM_CLAIM_FALLBACK.
    fallback_types: bool = True


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
    # Contradiction guard (05/11/2026, GS-Eval v2). On 146 real sentences of 8
    # companies, 35 of 38 CONTRADICTED were wrong: 19 of 20 numeric ones put two
    # figures about different objects side by side inside one report, and every
    # cue-based one read its cue out of the company's own prose ("không ghi nhận
    # trường hợp nào vi phạm", a GRI index listing "Nghị định ... xử phạt vi
    # phạm"). False (default): a passage from the claim's own document never
    # contradicts it, and a cue phrase in the company's own documents
    # (internal / financial) contradicts only when it sits in a ruling on
    # statements. True restores the earlier behaviour.
    # Env QUANTUM_SELF_EVIDENCE_CAN_CONTRADICT.
    self_evidence_can_contradict: bool = False
    # Support guard (11/11/2026, independent_support_v1 in configs/measurement_decisions.yaml).
    # False (default, behaviour of GS-Eval v2): a confirming passage from any document other
    # than the claim's own makes it SUPPORTED, including the company's annual report restating
    # its sustainability report. True: only a legal, external or standard source can; the
    # company's own echo stays PARTIALLY_SUPPORTED and says so. Off until the registered
    # GS-Bench and GS-Eval v2 reruns are read. Env QUANTUM_SUPPORT_REQUIRES_INDEPENDENT_SOURCE.
    # 15/11/2026: on by default (expert review + replay: GS-Eval v2 precision 0.33 -> 0.75, false SUPPORTED 5 -> 0).
    support_requires_independent_source: bool = True
    # Kế hoạch theo stage, 14/11/2026 (docs/03-architecture/ABSOLUTE_AND_INTERNAL.md).
    #   absolute_share_check   absolute-share-v1: "hoàn toàn / toàn bộ / 100%" about green-bond proceeds is
    #                          checked against used / total computed from one passage.     QUANTUM_ABSOLUTE_SHARE
    #   absolute_conflict_cues stance-cues-v3: an absolute claim against a sentence saying "chưa phân bổ /
    #                          một phần / giai đoạn 1" -> PARTIALLY_SUPPORTED + review flag.  QUANTUM_ABSOLUTE_CONFLICT
    #   internal_inconsistency internal-inconsistency-v1: off | flag | contradict. A same-document figure in a
    #                          data table may disagree with the prose under strict conditions; "flag" makes it
    #                          PARTIALLY_SUPPORTED + review flag, "contradict" CONTRADICTED. QUANTUM_INTERNAL_INCONSISTENCY
    #   figure_consistency_check  figure-consistency-v1 (GS-Mutation v1): a matched figure going the other way
    #                          (giảm vs tăng) contradicts; a claim whose second figure is far off is PARTIAL. QUANTUM_FIGURE_CONSISTENCY
    figure_consistency_check: bool = True
    absolute_share_check: bool = True
    absolute_conflict_cues: bool = True
    internal_inconsistency: str = "off"
    # Language-model stages (registration llm_stages_v1, 11/11/2026). Each is off until its gate in
    # configs/measurement_decisions.yaml is read; none may set a verdict (src/quantum_gw/assist/).
    #   verify_mode    "rules" | "dual": the IR reader (verification/ir_reader.py) reads the figures of
    #                  claims with a number and their passages; its S / C / N is a reviewer note.   QUANTUM_VERIFY
    #   assist_attributes  fill period / baseline / scope a claim writes but the rules missed, from
    #                  verbatim spans only.                                                QUANTUM_ASSIST_ATTRIBUTES
    #   assist_explain "off" | "queue" | "all": a plain-language explanation beside the rules
    #                  rationale, rejected when it adds a number.                          QUANTUM_ASSIST_EXPLAIN
    verify_mode: str = "rules"
    assist_attributes: bool = False
    assist_explain: str = "off"


class LegalSettings(BaseModel):
    enabled: bool = True
    registry_file: str = "configs/legal/LEGAL_SOURCE_REGISTRY.yaml"
    rule_pack_file: str = "configs/legal/rule_pack_vn_green_v0.1.yaml"
    # historical_compliance (law as it stood when the claim was published) or
    # current_policy_alignment (today's criteria). They are different questions
    # and a company can be compliant on one and misaligned on the other, so the
    # mode is explicit rather than inferred.
    check_mode: str = "current_policy_alignment"
    # Org packs (docs/03-architecture/ORG_PACK.md): an organisation's own rules,
    # applied beside the verdict and never to it. Env QUANTUM_ORG_PACKS. Empty =
    # off, and then the field is left out of the dump, so the config hash, the
    # manifest and result.json are exactly what they were without the feature.
    org_packs: list[str] = Field(default_factory=list, exclude_if=lambda value: not value)


class ReviewSettings(BaseModel):
    require_human_for_legal_conflict: bool = True
    # A claim nothing contradicts may not exceed this band, whatever the
    # missing-attribute penalties add up to (ISSUES N5, D-2026-09-22-03).
    # Lift only when the bands are calibrated on the gold set.
    severity_cap_without_contradiction: str = "medium"
    # audit-sample-v1 (15/11/2026): claims outside the queue drawn at random each run for a person to read,
    # to estimate what the queue misses. 0 turns it off. The queue itself is unchanged.
    audit_sample_size: int = 5


class FeedbackSettings(BaseModel):
    """feedback-loop-v1 (docs/03-architecture/FEEDBACK_LOOP.md): what past reviewer decisions may do to a run.

    Nothing here changes a verdict, a risk score or a release status. Precedents
    are shown next to a verdict; the queue may only gain items, never lose one;
    a trained model runs in shadow (logged, never shown as a verdict) unless it
    has passed the promotion gate and is switched on by name. Left at these
    defaults the block is not dumped, so the config hash is what it was before.
    """

    # Show similar claims a person already decided (feedback/precedents.py).
    # Env QUANTUM_FEEDBACK_PRECEDENTS=off turns it off.
    precedents: bool = True
    precedent_min_similarity: float = 0.55
    # A claim this close to one where a person overrode the machine joins the review queue.
    precedent_raise_similarity: float = 0.75
    precedent_raise_queue: bool = True
    # Whose labels this deployment may see: labels with no organisation, labels
    # promoted to the core memory, and this organisation's own. Env QUANTUM_FEEDBACK_ORG.
    org_id: str = ""
    # Extra review-queue places for the items a label would teach most (feedback/active.py).
    # 0 = off: no learning value is computed. Env QUANTUM_ACTIVE_LEARNING_SLOTS.
    active_learning_slots: int = 0
    # Past pointer labels shown to the stance model as examples (S5). 0 = off. Env QUANTUM_STANCE_EXAMPLES.
    stance_examples: int = 0
    # A challenger stance model run beside the rules and only logged. Env QUANTUM_SHADOW_MODEL.
    shadow_model: str = ""
    # A promoted stance model answering the pairs the rules escalate, in place of
    # the LLM. Refused unless the model registry lists it as promoted. Env QUANTUM_LOCAL_STANCE_MODEL.
    local_stance_model: str = ""
    model_registry: str = "models/stance/registry.json"


class GatewaySettings(BaseModel):
    """Model-gateway configuration. Loaded from environment variables only.

    Every field with a key may stay empty: the application must start and the
    deterministic pipeline must run with all cloud keys blank.
    """

    # QUANTUM_PROFILE at load time. "offline": the router tries local providers only (providers/router.py).
    profile: str = ""

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
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"
    groq_extra_body: str = ""  # JSON of extra request fields, e.g. {"reasoning_effort": "low"}


def load_gateway_settings() -> GatewaySettings:
    env = os.getenv
    fallback = [
        item.strip()
        for item in env("LLM_FALLBACK_ORDER", "local,fpt,gemini,openai,anthropic").split(",")
        if item.strip()
    ]
    return GatewaySettings(
        profile=env("QUANTUM_PROFILE", "").strip().lower(),
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
        groq_api_key=env("GROQ_API_KEY", ""),
        groq_model=env("GROQ_MODEL", "openai/gpt-oss-120b"),
        groq_extra_body=env("GROQ_EXTRA_BODY", ""),
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
    feedback: FeedbackSettings = Field(default_factory=FeedbackSettings,
                                       exclude_if=lambda value: value == FeedbackSettings())
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
    settings.intake.table_shape_filter = os.getenv(
        "QUANTUM_TABLE_SHAPE_FILTER", str(settings.intake.table_shape_filter)
    ).lower() in {"1", "true", "yes", "on"}
    settings.intake.layout_regions = os.getenv(
        "QUANTUM_LAYOUT_REGIONS", str(settings.intake.layout_regions)
    ).lower() in {"1", "true", "yes", "on"}
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
    guard = os.getenv("QUANTUM_SELF_EVIDENCE_CAN_CONTRADICT")
    if guard is not None and guard.strip():
        settings.verification.self_evidence_can_contradict = guard.strip().lower() in {"1", "true", "yes", "on"}
    independent = os.getenv("QUANTUM_SUPPORT_REQUIRES_INDEPENDENT_SOURCE")
    if independent is not None and independent.strip():
        settings.verification.support_requires_independent_source = (
            independent.strip().lower() in {"1", "true", "yes", "on"})
    anchor = os.getenv("QUANTUM_REQUIRE_ENV_ANCHOR")
    if anchor is not None and anchor.strip():
        settings.claim_extraction.require_environment_anchor = anchor.strip().lower() in {"1", "true", "yes", "on"}
    fallback = os.getenv("QUANTUM_CLAIM_FALLBACK")
    if fallback is not None and fallback.strip():
        settings.claim_extraction.fallback_types = fallback.strip().lower() in {"1", "true", "yes", "on"}
    for env, attr in (("QUANTUM_ABSOLUTE_SHARE", "absolute_share_check"),
                      ("QUANTUM_FIGURE_CONSISTENCY", "figure_consistency_check"),
                      ("QUANTUM_ABSOLUTE_CONFLICT", "absolute_conflict_cues")):
        value = os.getenv(env)
        if value is not None and value.strip():
            setattr(settings.verification, attr, value.strip().lower() in {"1", "true", "yes", "on"})
    internal = os.getenv("QUANTUM_INTERNAL_INCONSISTENCY", settings.verification.internal_inconsistency).strip().lower()
    if internal not in {"off", "flag", "contradict"}:
        raise ValueError(f"QUANTUM_INTERNAL_INCONSISTENCY must be off, flag or contradict, not {internal!r}")
    settings.verification.internal_inconsistency = internal
    verify = os.getenv("QUANTUM_VERIFY", settings.verification.verify_mode).strip().lower() or "rules"
    if verify not in {"rules", "dual"}:
        raise ValueError(f"QUANTUM_VERIFY must be rules or dual, not {verify!r}")
    settings.verification.verify_mode = verify
    attrs = os.getenv("QUANTUM_ASSIST_ATTRIBUTES")
    if attrs is not None and attrs.strip():
        settings.verification.assist_attributes = attrs.strip().lower() in {"1", "true", "yes", "on"}
    explain = os.getenv("QUANTUM_ASSIST_EXPLAIN", settings.verification.assist_explain).strip().lower() or "off"
    if explain not in {"off", "queue", "all"}:
        raise ValueError(f"QUANTUM_ASSIST_EXPLAIN must be off, queue or all, not {explain!r}")
    settings.verification.assist_explain = explain
    flag = os.getenv("QUANTUM_FLAG_SUSPECT_NON_CLAIMS")
    if flag is not None and flag.strip():
        settings.claim_extraction.flag_suspect_non_claims = flag.strip().lower() in {"1", "true", "yes", "on"}
    settings.claim_extraction.claim_model_dir = os.getenv(
        "QUANTUM_CLAIM_MODEL", settings.claim_extraction.claim_model_dir).strip()
    # Pack folders or pack.yaml files, separated by "," or ";". Set but empty = off.
    org_packs = os.getenv("QUANTUM_ORG_PACKS")
    if org_packs is not None:
        settings.legal.org_packs = [p.strip() for p in re.split(r"[,;]", org_packs) if p.strip()]
    _feedback_env(settings.feedback)
    return settings


def _feedback_env(feedback: FeedbackSettings) -> None:
    """QUANTUM_FEEDBACK_* and friends (feedback-loop-v1). Unset keeps the config value."""
    on = {"1", "true", "yes", "on"}
    value = os.getenv("QUANTUM_FEEDBACK_PRECEDENTS")
    if value is not None and value.strip():
        feedback.precedents = value.strip().lower() in on
    value = os.getenv("QUANTUM_FEEDBACK_ORG")
    if value is not None:
        feedback.org_id = value.strip()
    for env, name in (("QUANTUM_ACTIVE_LEARNING_SLOTS", "active_learning_slots"),
                      ("QUANTUM_STANCE_EXAMPLES", "stance_examples")):
        value = os.getenv(env)
        if value is not None and value.strip():
            try:
                setattr(feedback, name, max(0, int(value)))
            except ValueError as exc:
                raise ValueError(f"{env} must be a whole number, not {value!r}") from exc
    for env, name in (("QUANTUM_SHADOW_MODEL", "shadow_model"), ("QUANTUM_LOCAL_STANCE_MODEL", "local_stance_model")):
        value = os.getenv(env)
        if value is not None:
            setattr(feedback, name, value.strip())
