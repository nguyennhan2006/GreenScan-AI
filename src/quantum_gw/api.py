from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from quantum_gw import __version__
from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.agents.suggester import SuggestionAgent
from quantum_gw.api_studio import router as studio_router
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import AnalysisResult, ClaimSuggestion, DocumentInput
from quantum_gw.jobs import JobRunner
from quantum_gw.parsers.ocr import TesseractOCR
from quantum_gw.providers import ModelGateway
from quantum_gw import model_mode
from quantum_gw.settings import load_settings
from quantum_gw.storage.documents import (
    DocumentStore,
    highlight_rects,
    page_count,
    render_page_png,
)
from quantum_gw.storage.reviews import ReviewError, ReviewStore
from quantum_gw.storage.runs import RunStore

app = FastAPI(title="AI Quantum Greenwashing Agent", version=__version__)


class _ApiPrefix:
    """Serve every route under `/api` as well as at the root.

    The web UI calls `/api/v1/...` (the Vite dev server strips the prefix on its
    way to port 8000). When this process serves the built UI itself there is no
    proxy in between, so the prefix is removed here and one port does both.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in {"http", "websocket"}:
            path = scope.get("path", "")
            if path == "/api" or path.startswith("/api/"):
                scope = dict(scope)
                scope["path"] = path[4:] or "/"
                raw = scope.get("raw_path")
                if raw:
                    scope["raw_path"] = raw[4:] or b"/"
        await self.app(scope, receive, send)


app.add_middleware(_ApiPrefix)


class _DemoAuth:
    """Password protection for a publicly deployed prototype (off unless configured).

    QUANTUM_DEMO_USERS="giamkhao:matkhau;doi:matkhau2" turns on HTTP Basic
    authentication for every route except /health, so a demo link given to a
    jury is not an open upload endpoint for the internet. Unset (the default,
    and every local run) means no authentication at all.
    """

    def __init__(self, app):
        self.app = app
        import base64

        pairs = [p.strip() for p in os.environ.get("QUANTUM_DEMO_USERS", "").replace(",", ";").split(";")]
        self.allowed = {
            "Basic " + base64.b64encode(pair.encode("utf-8")).decode("ascii")
            for pair in pairs if ":" in pair
        }

    async def __call__(self, scope, receive, send):
        if not self.allowed or scope["type"] != "http" or scope.get("path") in {"/health", "/api/health"}:
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers") or [])
        if headers.get(b"authorization", b"").decode("latin-1") in self.allowed:
            await self.app(scope, receive, send)
            return
        await send({
            "type": "http.response.start", "status": 401,
            "headers": [(b"www-authenticate", b'Basic realm="GreenScan", charset="UTF-8"'),
                        (b"content-type", b"text/plain; charset=utf-8")],
        })
        await send({"type": "http.response.body", "body": "Cần tài khoản thử nghiệm (xem tài liệu hướng dẫn).".encode("utf-8")})


app.add_middleware(_DemoAuth)

cors_origins = [
    origin.strip()
    for origin in os.environ.get("QUANTUM_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # The page viewer reads how many highlight boxes were drawn (dev server runs cross-origin).
    expose_headers=["X-Highlight-Rects"],
)


class InlineDocument(BaseModel):
    name: str
    text: str
    role: DocumentRole = DocumentRole.EVIDENCE
    source_type: SourceType = SourceType.INTERNAL
    # Accepted so a caller can state the document's language; the extractor
    # detects it per claim regardless. Without the field the value was silently
    # dropped from request bodies that set it.
    language: str = "vi"
    metadata: dict = Field(default_factory=dict)


class AnalyzeTextRequest(BaseModel):
    documents: list[InlineDocument]
    # Optional, for a background job: the session label shown in History and
    # the reporting entity's name (read into every document's metadata).
    label: str = ""
    company: str = ""
    # Uploaded org packs for this run (legal/org_registry.resolve): "org_id" = its
    # latest approved version, "org_id@version" = that stored version.
    org_packs: list[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    # run_id is duplicated at the top level so clients can route on it
    # without reaching into the result payload.
    run_id: str
    result: AnalysisResult
    suggestions: list[ClaimSuggestion]
    # The session name a reviewer gave the run (History, sidebar); empty when
    # the run was never named or has only just been produced.
    label: str = ""


def _org_paths(selectors: list[str] | str | None) -> list[str]:
    """Folders of the uploaded org packs a request chose; 400 when one is unknown or retired."""
    from quantum_gw.legal.org_registry import resolve

    if isinstance(selectors, str):
        selectors = [s for s in selectors.replace(";", ",").split(",")]
    try:
        return resolve(selectors or [])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _settings_for(org_paths: list[str] | None = None):
    """The run's settings: QUANTUM_ORG_PACKS plus the packs this request chose."""
    settings = load_settings()
    if org_paths:
        settings.legal.org_packs = list(dict.fromkeys([*settings.legal.org_packs, *org_paths]))
    return settings


def _analyze(documents: list[DocumentInput], org_paths: list[str] | None = None) -> AnalyzeResponse:
    result = OrchestratorAgent(_settings_for(org_paths)).run(documents)
    return AnalyzeResponse(run_id=result.run_id, result=result, suggestions=SuggestionAgent().run(result))


def _run_store() -> RunStore:
    return RunStore(load_settings().runs_dir)


# One worker: the pipeline is CPU-bound and two runs side by side on a laptop
# finish later than the same two in a row (QUANTUM_JOB_WORKERS to change).
JOBS = JobRunner(workers=int(os.environ.get("QUANTUM_JOB_WORKERS", "1")))


@app.on_event("startup")
def _install_demo_seed() -> None:
    """Seeded demo runs (deploy/seed/) into the store, so a jury sees finished analyses at once."""
    try:
        from quantum_gw.storage.seed import install

        copied = install(load_settings().runs_dir)
        if copied["runs"] or copied["documents"]:
            _console(f"[phiên mẫu] đã cài {copied['runs']} phiên, {copied['documents']} tài liệu vào kho")
    except Exception as exc:  # seeding must never stop the server
        _console(f"[phiên mẫu] bỏ qua: {exc}")


def _console(message: str) -> None:
    """Print a startup line without crashing on a console that cannot show Vietnamese (Windows cp1258)."""
    try:
        print(message, flush=True)
    except UnicodeEncodeError:
        print(message.encode("ascii", "replace").decode("ascii"), flush=True)


def _with_company(documents: list[DocumentInput], company: str) -> list[DocumentInput]:
    name = (company or "").strip()
    if not name:
        return documents
    return [d.model_copy(update={"metadata": {**d.metadata, "company": name}}) for d in documents]


def _job(documents: list[DocumentInput], label: str, org_paths: list[str] | None = None):
    def work(progress) -> str:
        result = OrchestratorAgent(_settings_for(org_paths)).run(documents, progress=progress)
        if label.strip():
            _run_store().set_label(result.run_id, label.strip())
        return result.run_id

    return work


async def _stored_uploads(files: list[UploadFile], roles: str, source_types: str) -> list[DocumentInput]:
    role_values = [item.strip() for item in roles.split(",") if item.strip()]
    type_values = [item.strip() for item in source_types.split(",") if item.strip()]
    if len(role_values) not in {1, len(files)} or len(type_values) not in {1, len(files)}:
        raise HTTPException(status_code=400, detail="roles/source_types must contain one value or one per file")
    # Persist to the document store rather than a temp dir: a citation must
    # still resolve after the request ends, and the parser derives doc_id
    # from the file path, so a stable path is what makes the id reproducible.
    store = DocumentStore()
    documents = []
    # A deployed demo shares one CPU between every visitor: cap what one upload
    # can cost. QUANTUM_MAX_UPLOAD_MB (default 80) per file; 0 = no limit.
    limit_mb = float(os.environ.get("QUANTUM_MAX_UPLOAD_MB", "80") or 0)
    for index, upload in enumerate(files):
        data = await upload.read()
        if limit_mb and len(data) > limit_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"Tệp {upload.filename} lớn hơn giới hạn {limit_mb:.0f} MB của bản chạy thử.",
            )
        record = store.put(data, upload.filename or f"upload-{index}.txt")
        documents.append(
            DocumentInput(
                path=str(record.path),
                name=upload.filename,
                role=DocumentRole(role_values[index] if len(role_values) > 1 else role_values[0]),
                source_type=SourceType(type_values[index] if len(type_values) > 1 else type_values[0]),
            )
        )
    return documents


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.get("/v1/gateway/health")
def gateway_health(live: bool = False) -> dict:
    """Model-gateway status. `live=true` also pings each configured provider."""
    gateway = ModelGateway()
    return {
        "active_provider": gateway.settings.provider,
        "fallback_order": gateway.settings.fallback_order,
        "providers": gateway.healthcheck() if live else gateway.describe(),
    }


@app.post("/v1/analyze/text", response_model=AnalyzeResponse)
def analyze_text(request: AnalyzeTextRequest) -> AnalyzeResponse:
    org_paths = _org_paths(request.org_packs)
    try:
        docs = [DocumentInput(**item.model_dump()) for item in request.documents]
        return _analyze(docs, org_paths)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/analyze/files", response_model=AnalyzeResponse)
async def analyze_files(
    files: list[UploadFile] = File(...),
    roles: str = Form("claim_source"),
    source_types: str = Form("internal"),
    org_packs: str = Form(""),
) -> AnalyzeResponse:
    org_paths = _org_paths(org_packs)
    try:
        documents = await _stored_uploads(files, roles, source_types)
        # The pipeline is CPU-bound and synchronous: run on the event loop it
        # froze every other request, /health included, for the whole analysis.
        return await run_in_threadpool(_analyze, documents, org_paths)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ---------- background analyses with progress ----------


@app.post("/v1/jobs/analyze/files", status_code=202)
async def start_analysis_files(
    files: list[UploadFile] = File(...),
    roles: str = Form("claim_source"),
    source_types: str = Form("internal"),
    label: str = Form(""),
    company: str = Form(""),
    org_packs: str = Form(""),
) -> dict:
    """Start an analysis and return at once; poll `GET /v1/jobs/{job_id}`."""
    org_paths = _org_paths(org_packs)
    try:
        documents = _with_company(await _stored_uploads(files, roles, source_types), company)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    job = JOBS.submit(_job(documents, label, org_paths), label=label)
    return JOBS.status(job.job_id) or {}


@app.post("/v1/jobs/analyze/text", status_code=202)
def start_analysis_text(request: AnalyzeTextRequest) -> dict:
    org_paths = _org_paths(request.org_packs)
    try:
        documents = [DocumentInput(**item.model_dump()) for item in request.documents]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    job = JOBS.submit(_job(_with_company(documents, request.company), request.label, org_paths),
                      label=request.label)
    return JOBS.status(job.job_id) or {}


@app.get("/v1/jobs/{job_id}")
def job_status(job_id: str) -> dict:
    status = JOBS.status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found (jobs are kept in memory until restart)")
    return status


# ---------- what this installation actually runs ----------


_RETRIEVAL_DETAIL = {
    "lite": "Tìm theo từ khoá và theo cụm ký tự, gộp hai bảng xếp hạng (chạy trên CPU, không tải mô hình).",
    "fpt": "BM25 + vector {fpt} qua FPT AI Marketplace.",
    "local": "Tìm theo từ khoá và theo nghĩa bằng mô hình {model} chạy trên máy ({device}).",
    "http": "Tìm theo từ khoá và theo nghĩa qua dịch vụ nội bộ.",
}


@app.get("/v1/runtime")
def runtime() -> dict:
    """Which engine serves which task right now, in words a reviewer can read.

    The header used to list every provider holding a key, e.g. "fpt
    (Qwen3.6-27B)", whether or not anything called it, and a fresh checkout
    listed a local Qwen3-8B that did not exist. This reports what a run would do.
    """
    settings = load_settings()
    stance_on = settings.verification.llm_stance == "on_ambiguous"
    route = ModelGateway().route("qualitative_stance") if stance_on else []
    embedding = settings.embedding
    retrieval = _RETRIEVAL_DETAIL.get(embedding.provider, embedding.provider).format(
        fpt=embedding.fpt_model, model=embedding.model, device=embedding.device
    )
    if settings.reranker.provider != "none":
        retrieval += f" Xếp hạng lại bằng mô hình chuyên xếp hạng ({settings.reranker.provider})."
    if stance_on and route:
        stance = (
            f"Mô hình {route[0].split(':', 1)[-1]} đọc những cặp tuyên bố–bằng chứng mà luật và "
            "phép tính không quyết được; mọi kết luận của nó chuyển người xác nhận."
        )
    elif stance_on:
        stance = "Đã bật nhưng chưa cấu hình nhà cung cấp mô hình nào: các cặp này giữ kết quả của luật."
    else:
        stance = "Tắt: các cặp luật chưa quyết được dừng ở “khớp một phần” hoặc “chưa đủ bằng chứng”."
    tasks = [
        {"task": "claim_extraction", "label": "Trích tuyên bố", "engine": "rules",
         "detail": "Luật tất định trên câu và dòng bảng (không dùng mô hình)."},
        {"task": "retrieval", "label": "Tìm bằng chứng", "engine": embedding.provider, "detail": retrieval},
        {"task": "quantitative_verification", "label": "So sánh số liệu", "engine": "deterministic",
         "detail": "Phép tính bằng mã, không bao giờ giao cho mô hình ngôn ngữ."},
        {"task": "qualitative_stance", "label": "Đọc các cặp khó",
         "engine": "llm" if stance_on and route else "rules", "route": route, "detail": stance},
    ]
    # llm_stages_v1: every stage that is on and has a route is listed, and any non-local route makes the run "cloud".
    v = settings.verification
    gateway = ModelGateway()
    for on, task, label, detail in (
        (v.verify_mode == "dual", "ir_reading", "Bộ đọc số liệu (tuyên bố trong hàng đợi)",
         "Mô hình đọc số liệu thành cấu trúc; mã so sánh; chỉ là ghi chú cho người soát."),
        (v.assist_attributes, "claim_normalization", "Điền thuộc tính tuyên bố",
         "Mô hình chép nguyên văn kỳ, năm gốc, phạm vi mà luật bỏ sót; chuỗi không có trong câu bị loại."),
        (v.assist_explain != "off", "claim_explanation", "Lời giải thích dễ hiểu",
         "Mô hình viết lời giải thích cạnh lý do của luật; lời có con số mới bị loại."),
    ):
        if on:
            stage_route = gateway.route(task)
            route = route + stage_route
            tasks.append({"task": task, "label": label, "engine": "llm" if stage_route else "rules",
                          "route": stage_route, "detail": detail if stage_route else "Đã bật nhưng chưa có mô hình."})
    if settings.claim_extraction.claim_model_dir:
        tasks.append({"task": "claim_model", "label": "Lọc câu không phải tuyên bố", "engine": "local",
                      "detail": "Bộ phân loại e5 chạy trên máy, chỉ đánh dấu."})
    cloud = any(not r.startswith("local:") for r in route) or "fpt" in {
        embedding.provider, settings.reranker.provider
    }
    hardware: dict = {"cpu_count": os.cpu_count()}
    try:
        import psutil

        hardware["ram_gb"] = round(psutil.virtual_memory().total / 1e9, 1)
    except Exception:  # noqa: BLE001 - optional dependency
        pass
    return {
        "profile": os.environ.get("QUANTUM_PROFILE", "") or "custom",
        "model_mode": model_mode.current_mode(),
        "model_modes": [
            {"id": mode, "label": model_mode.LABELS[mode][0], "detail": model_mode.LABELS[mode][1], **state}
            for mode, state in model_mode.availability().items()
        ],
        "mode": "cloud" if cloud else "offline",
        "label": "Có dùng mô hình trên đám mây cho phần khó" if cloud else "Ngoại tuyến — không gửi tài liệu ra ngoài",
        "sends_documents_out": cloud,
        "tasks": tasks,
        "ocr": {
            "enabled": settings.intake.ocr_enabled,
            "available": TesseractOCR(settings.intake.tesseract_command, settings.intake.ocr_languages).available,
            "languages": settings.intake.ocr_languages,
        },
        "hardware": hardware,
    }


class ModelModeRequest(BaseModel):
    mode: str


@app.post("/v1/runtime/model-mode")
def set_model_mode(request: ModelModeRequest) -> dict:
    """Turn the language-model stages on or off for the runs started from now on (model-mode-v1).

    A model never writes SUPPORTED or CONTRADICTED on its own; it adds a reading and an explanation, and a claim it
    reads differently from the rules goes to a person.
    """
    try:
        model_mode.set_mode(request.mode)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return runtime()


@app.post("/v1/runtime/model-test")
def test_model() -> dict:
    """One short live call to the model that is switched on, with the time it took."""
    return model_mode.test_call()


@app.get("/v1/documents/{doc_id}")
def get_document(doc_id: str):
    """The original file, so a reviewer can open the real page in context."""
    record = DocumentStore().get(doc_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Document not found or no longer stored")
    if not DocumentStore().is_servable(record):
        raise HTTPException(status_code=415, detail=f"Refusing to serve {record.path.suffix}")
    return FileResponse(
        record.path,
        media_type=record.content_type,
        # inline so the browser PDF viewer honours #page=N
        headers={"Content-Disposition": f'inline; filename="{record.name}"'},
    )


@app.get("/v1/documents/{doc_id}/meta")
def get_document_meta(doc_id: str) -> dict:
    record = DocumentStore().get(doc_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Document not found or no longer stored")
    meta = record.to_json()
    if record.path.suffix.lower() == ".pdf":
        try:
            meta["page_count"] = page_count(record.path)
        except Exception:  # noqa: BLE001 - a damaged PDF should not 500 the metadata call
            meta["page_count"] = None
    return meta


@app.get("/v1/documents/{doc_id}/page/{page}")
def get_document_page(doc_id: str, page: int, q: str = "", zoom: float = 2.0):
    """One page rendered to PNG, with `q` highlighted where it can be located.

    Server-side rendering keeps a PDF engine out of the browser and behaves the
    same on scanned pages, where a text-layer highlight would find nothing.
    """
    record = DocumentStore().get(doc_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Document not found or no longer stored")
    if record.path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=415, detail="Page rendering is only available for PDF")
    try:
        rects = highlight_rects(record.path, page, q) if q else []
        png = render_page_png(record.path, page, rects, zoom=max(1.0, min(zoom, 4.0)))
    except IndexError as exc:
        raise HTTPException(status_code=404, detail=f"Page {page} out of range") from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Response(
        content=png,
        media_type="image/png",
        # `matched` lets the UI say "highlight not located" instead of implying
        # the quoted text is absent from the page.
        headers={"X-Highlight-Rects": str(len(rects))},
    )


class ReviewRequest(BaseModel):
    run_id: str
    claim_id: str
    reviewer: str
    decision: str
    comment: str = ""
    reviewer_status: str | None = None
    ai_status: str | None = None
    ai_risk_score: float | None = None
    evidence: list[dict] = Field(default_factory=list)
    claim: dict = Field(default_factory=dict)
    # OVERRIDE only: why the AI was wrong (reviews.OVERRIDE_REASONS) and, for a
    # rule reason, which rule.
    override_reason: str | None = None
    rule_ref: str = ""
    # Pointer label (feedback-loop-v1): the passage(s) that decided the case, by
    # chunk id, or quoted when the system did not show it; who the reviewer is.
    decisive_chunk_ids: list[str] = Field(default_factory=list)
    decisive_quote: str = ""
    reviewer_role: str = ""
    reviewer_org: str = ""


def _rule_context(run_id: str) -> dict:
    """The rules in force for a saved run, read from its manifest on the server.

    Taken from disk, not from the request: the label must be tied to the rules
    the run actually used, not to what a client says they were. An unknown run
    gives {} and the label is then visibly unversioned.
    """
    try:
        manifest = _run_store().load(run_id).manifest
    except (KeyError, FileNotFoundError, ValueError):
        return {}
    context: dict = {
        "pipeline_version": manifest.pipeline_version,
        "config_hash": manifest.config_hash,
        "rule_pack_version": manifest.rule_pack_version,
        "prompt_version": manifest.prompt_version,
        "corpus_version": manifest.corpus_version,
    }
    if manifest.org_packs is not None:
        context["org_packs"] = [
            {k: p.get(k) for k in ("org_id", "pack_version", "sha256", "status")}
            for p in manifest.org_packs
        ]
    return context


@app.post("/v1/reviews")
def create_review(request: ReviewRequest) -> dict:
    """Record one human decision. Append-only; never edits an earlier one."""
    try:
        record = ReviewStore().record(**request.model_dump(), rule_context=_rule_context(request.run_id))
    except ReviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return record.to_json()


@app.get("/v1/reviews/{run_id}")
def list_reviews(run_id: str) -> dict:
    store = ReviewStore()
    return {
        "run_id": run_id,
        "states": store.states_for_run(run_id),
        "decisions": [r for r in store.all() if r["run_id"] == run_id],
    }


@app.get("/v1/reviews/{run_id}/{claim_id}")
def claim_history(run_id: str, claim_id: str) -> dict:
    store = ReviewStore()
    return {
        "run_id": run_id,
        "claim_id": claim_id,
        "state": store.state_of(run_id, claim_id),
        "history": store.history(run_id, claim_id),
    }


@app.get("/v1/reviews-export/gold")
def export_gold() -> dict:
    """Human-adjudicated labels only — the seed of the gold set."""
    store = ReviewStore()
    return {"stats": store.stats(), "records": store.gold_records()}


@app.get("/v1/reviews-export/rule-feedback")
def export_rule_feedback() -> dict:
    """Overrides that blame a rule, not the model, grouped by rule: the queue for
    an org-pack exception or a rule-pack fix. Never a model label."""
    return {"groups": ReviewStore().rule_feedback()}


# ---------- saved runs ----------
#
# The pipeline writes every run to disk; these endpoints only read them back so
# the UI can reopen an analysis (and the demo can open a prepared run instead of
# re-parsing a 200-page report on stage).


@app.get("/v1/runs")
def list_runs(limit: int = 50) -> dict:
    return {"runs": _run_store().list(limit=max(1, min(limit, 200)))}


@app.get("/v1/runs/{run_id}", response_model=AnalyzeResponse)
def get_run(run_id: str) -> AnalyzeResponse:
    try:
        result = _run_store().load(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc
    return AnalyzeResponse(
        run_id=result.run_id, result=result, suggestions=SuggestionAgent().run(result),
        label=_run_store().label_of(run_id),
    )


class RunLabelRequest(BaseModel):
    label: str


@app.put("/v1/runs/{run_id}/label")
def set_run_label(run_id: str, request: RunLabelRequest) -> dict:
    try:
        return {"run_id": run_id, "label": _run_store().set_label(run_id, request.label)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc


_EXPORTS = {
    "json": ("result.json", "application/json"),
    "md": ("evidence_pack.md", "text/markdown"),
    "manifest": ("manifest.json", "application/json"),
    "audit": ("audit.jsonl", "application/x-ndjson"),
}


@app.get("/v1/runs/{run_id}/export")
def export_run(run_id: str, format: str = "json"):
    """One artifact of the evidence pack as a download. PDF is not produced yet."""
    if format == "csv":
        from quantum_gw.queue_csv import render_queue_csv

        try:
            result = _run_store().load(run_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Run not found") from exc
        return Response(
            render_queue_csv(result), media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="greenscan-{run_id}-hang-doi.csv"'},
        )
    if format not in _EXPORTS:
        raise HTTPException(status_code=400, detail=f"format must be one of {sorted(_EXPORTS) + ['csv']}")
    name, media_type = _EXPORTS[format]
    try:
        path = _run_store().artifact(run_id, name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Run or artifact not found") from exc
    return FileResponse(
        path,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="greenscan-{run_id}-{name}"'},
    )


@app.get("/v1/runs/{run_id}/workpaper", response_class=HTMLResponse)
def workpaper(run_id: str, print: bool = False) -> HTMLResponse:  # noqa: A002 - query name
    """The working paper in Vietnamese, with the review trail; print it to PDF."""
    from quantum_gw.workpaper import render_workpaper

    store = _run_store()
    try:
        result = store.load(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc
    decisions = [r for r in ReviewStore().all() if r.get("run_id") == run_id]
    return HTMLResponse(render_workpaper(result, decisions, store.label_of(run_id), auto_print=print))


# ---------- legal corpus ----------


@app.get("/v1/legal/corpus")
def legal_corpus() -> dict:
    """The registered instruments, as the legal layer sees them.

    `usable` says whether clause text exists: a registered document the layer
    cannot quote is reported as a coverage gap in every finding it would govern,
    so the UI shows that state rather than implying the instrument was checked.
    """
    from quantum_gw.legal.corpus import LegalCorpus

    settings = load_settings()
    try:
        corpus = LegalCorpus.from_registry(settings.legal.registry_file)
    except (OSError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=503, detail=f"Legal registry unavailable: {exc}") from exc
    documents = []
    for doc in corpus.documents.values():
        documents.append({
            "id": doc.id,
            "document_number": doc.document_number,
            "title": doc.title,
            "doc_type": doc.doc_type,
            "authority": doc.authority,
            "issued_date": doc.issued_date.isoformat() if doc.issued_date else None,
            "effective_from": doc.effective_from.isoformat() if doc.effective_from else None,
            "effective_to": doc.effective_to.isoformat() if doc.effective_to else None,
            "status": doc.status,
            "legal_issues": doc.legal_issues,
            "text_acquisition": doc.text_acquisition,
            "text_acquisition_note": doc.text_acquisition_note,
            "usable": doc.usable,
            "text_is_ocr": doc.text_is_ocr,
            "url": doc.landing_url or doc.original_url,
            "relations": doc.relations,
        })
    documents.sort(key=lambda d: d["effective_from"] or "", reverse=True)
    return {
        "registry_file": settings.legal.registry_file,
        "rule_pack_file": settings.legal.rule_pack_file,
        "enabled": settings.legal.enabled,
        "check_mode": settings.legal.check_mode,
        "documents": documents,
    }


@app.get("/v1/org-packs")
def org_packs() -> dict:
    """The org packs a run would use (QUANTUM_ORG_PACKS): approved, draft or refused, with their rules.

    Read-only. A refused pack is listed with every reason; nothing here applies a rule.
    """
    from quantum_gw.legal.org_pack import OrgPackSet

    settings = load_settings()
    loaded = OrgPackSet(settings.legal.org_packs)
    rules = {
        pack.org_id: [
            {"rule_id": r.rule_id, "title": r.title, "severity": r.severity, "on_fail": r.on_fail,
             "source_clauses": r.source_clauses, "applies_to_sectors": r.applies_to_sectors,
             "effective_from": r.effective_from.isoformat() if r.effective_from else None,
             "effective_to": r.effective_to.isoformat() if r.effective_to else None}
            for r in pack.rules
        ]
        for pack in loaded.packs
    }
    from quantum_gw.legal.org_registry import list_packs

    return {
        "enabled": bool(settings.legal.org_packs),
        "packs": [{**entry, "rules": rules.get(entry["org_id"], []) if entry["status"] != "rejected" else []}
                  for entry in loaded.entries],
        # Packs sent over the API (org-pack-v1): draft until someone other than the
        # uploader approves; a run uses one only when the request names it.
        "uploaded": list_packs(),
    }


@app.post("/v1/org-packs/upload")
async def org_pack_upload(files: list[UploadFile] = File(...), uploaded_by: str = Form(...),
                          note: str = Form("")) -> dict:
    """A zip of a pack folder, or pack.yaml plus its documents. Stored as a draft, or refused with every reason."""
    from quantum_gw.legal.org_registry import ingest

    contents = [(f.filename or "pack.yaml", await f.read()) for f in files]
    result = ingest(contents, uploaded_by, note)
    if result["status"] in ("rejected", "duplicate"):
        raise HTTPException(status_code=400, detail=result)
    return result


class OrgPackDecision(BaseModel):
    by: str
    comment: str = ""


@app.post("/v1/org-packs/{org_id}/{version}/approve")
def org_pack_approve(org_id: str, version: str, request: OrgPackDecision) -> dict:
    """Four-eyes: the approver must not be the uploader. Re-validates the stored copy."""
    from quantum_gw.legal.org_registry import approve

    try:
        return approve(org_id, version, request.by, request.comment)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/org-packs/{org_id}/{version}/retire")
def org_pack_retire(org_id: str, version: str, request: OrgPackDecision) -> dict:
    from quantum_gw.legal.org_registry import retire

    try:
        return retire(org_id, version, request.by, request.comment)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class OrgPackPreviewRequest(BaseModel):
    pack: str  # "org_id@version" of an uploaded pack, or a folder configured in QUANTUM_ORG_PACKS
    text: str
    sector: str = ""


@app.post("/v1/org-packs/preview")
def org_pack_preview(request: OrgPackPreviewRequest) -> dict:
    """Run one pack on one sentence, with no evidence (drafts are previewed as if approved)."""
    from quantum_gw.legal.org_pack import OrgPackError, load_org_pack, preview_sentence

    settings = load_settings()
    if "@" in request.pack:
        [path] = _org_paths([request.pack])
    elif request.pack in settings.legal.org_packs:
        path = request.pack
    else:
        raise HTTPException(status_code=400, detail="chọn pack dạng org_id@phiên_bản, hoặc một pack trong QUANTUM_ORG_PACKS")
    try:
        pack = load_org_pack(path)
    except OrgPackError as exc:
        raise HTTPException(status_code=400, detail={"errors": exc.problems}) from exc
    return preview_sentence(pack, request.text, request.sector.strip() or None, settings)


@app.post("/v1/org-packs/draft")
async def org_pack_draft(
    org_id: str = Form(...), org_name: str = Form(...), uploaded_by: str = Form(...),
    org_type: str = Form("other"), use_llm: bool = Form(False),
    policy_text: str = Form(""), policy_file: UploadFile | None = File(None),
) -> dict:
    """Draft a pack from a policy document and store it as a draft (never applied until approved)."""
    import tempfile

    from quantum_gw.legal.org_draft import draft, write
    from quantum_gw.legal.org_registry import ingest

    text = policy_text
    if policy_file is not None:
        raw = await policy_file.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="tệp chính sách phải là văn bản UTF-8 (.md, .txt)") from exc
    if not text.strip():
        raise HTTPException(status_code=400, detail="cần văn bản chính sách (policy_text hoặc policy_file)")
    drafted = await run_in_threadpool(draft, text, org_id.strip(), org_name.strip(), org_type, "internal_policy.md",
                                      use_llm)
    if drafted["errors"]:
        return {"status": "invalid", **drafted}
    with tempfile.TemporaryDirectory(prefix="org-draft-api-") as tmp:
        folder = write(Path(tmp) / drafted["pack"]["org_id"], drafted["pack"], text)
        files = [(f.name, f.read_bytes()) for f in folder.iterdir()]
    stored = ingest(files, uploaded_by, note=f"soạn nháp tự động ({drafted['method']})")
    return {**drafted, "stored": stored}


# ---------- feedback loop (docs/03-architecture/FEEDBACK_LOOP.md) ----------


@app.get("/v1/feedback/summary")
def feedback_summary() -> dict:
    """Labels by route and stage, QA agreement, the GS-Feedback ratchet and the model registry."""
    from quantum_gw.feedback.bench import read_ratchet
    from quantum_gw.feedback.hygiene import QAStore, agreement, clean_labels
    from quantum_gw.feedback.registry import read as read_registry

    store = ReviewStore()
    gold = store.gold_records()
    qa = QAStore(reviews=store).all()
    settings = load_settings()
    ratchet = read_ratchet()
    return {
        "stats": store.stats(),
        "clean_labels": len(clean_labels(gold, qa)),
        "agreement": agreement(gold, qa),
        "ratchet": {"size": len(ratchet.get("passing", [])), "history": ratchet.get("history", [])[-5:]},
        "models": [{k: m.get(k) for k in ("model_id", "kind", "status", "registered_at", "approved_by", "gate",
                                          "challenger", "champion", "data")}
                   for m in read_registry(settings.feedback.model_registry)["models"]],
        "settings": settings.feedback.model_dump(),
    }


@app.get("/v1/feedback/precedents")
def feedback_precedents(text: str, k: int = 3, min_similarity: float = 0.35) -> dict:
    """Decided claims similar to `text`, visible to this deployment's organisation."""
    from quantum_gw.feedback.precedents import PrecedentIndex

    index = PrecedentIndex.from_store(org_id=load_settings().feedback.org_id)
    return {"visible_labels": len(index),
            "precedents": index.find({"text": text}, k=max(1, min(k, 10)), min_similarity=min_similarity)}


@app.get("/v1/feedback/second-review-sample")
def feedback_second_review_sample(rate: float = 0.10, seed: str = "") -> dict:
    from quantum_gw.feedback.hygiene import sample_for_second_review

    return {"sample": sample_for_second_review(ReviewStore().gold_records(), rate=min(max(rate, 0.0), 1.0), seed=seed)}


class SecondReviewRequest(BaseModel):
    run_id: str
    claim_id: str
    reviewer: str
    status: str
    comment: str = ""
    kind: str = "second_review"  # second_review | adjudication | core_promotion


@app.post("/v1/feedback/qa")
def feedback_qa(request: SecondReviewRequest) -> dict:
    """A blind second review, an adjudication, or a promotion of an organisation's label to the core memory."""
    from quantum_gw.feedback.hygiene import QAStore
    from quantum_gw.storage.reviews import ReviewError

    store = ReviewStore()
    qa = QAStore(reviews=store)
    first = store.latest(request.run_id, request.claim_id)
    if first is None or first.get("new_state") != "FINALIZED":
        raise HTTPException(status_code=400, detail="chỉ áp dụng cho tuyên bố đã chốt")
    try:
        if request.kind == "second_review":
            return qa.record_second(run_id=request.run_id, claim_id=request.claim_id, reviewer=request.reviewer,
                                    status=request.status, first_reviewer=first["reviewer"], comment=request.comment)
        if request.kind == "adjudication":
            return qa.record_adjudication(run_id=request.run_id, claim_id=request.claim_id,
                                          adjudicator=request.reviewer, status=request.status, comment=request.comment)
        if request.kind == "core_promotion":
            return qa.promote_to_core(run_id=request.run_id, claim_id=request.claim_id, approved_by=request.reviewer,
                                      comment=request.comment)
    except ReviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    raise HTTPException(status_code=400, detail="kind phải là second_review, adjudication hoặc core_promotion")


@app.get("/v1/feedback/proposals")
def feedback_proposals() -> dict:
    """The rule miner's proposal sheet, computed now (not measured: measuring is the CLI's --measure)."""
    from quantum_gw.feedback.miner import mine, render_sheet

    proposals = mine()
    return {"proposals": proposals, "markdown": render_sheet(proposals)}


# Intake preview, URL fetch, demo samples and GreenScan Studio (api_studio.py).
app.include_router(studio_router)


# ---------- the built web UI, on the same port ----------
#
# `npm run build` writes frontend/dist; when it is there, http://localhost:8000
# is the whole product and nobody has to run Node or a second terminal. The UI
# routes with `#/...`, so serving `/` and the static assets is all it needs.


def ui_dir() -> Path | None:
    """Where the built web UI is, if it has been built."""
    candidates = [
        os.environ.get("QUANTUM_UI_DIR", ""),
        "frontend/dist",
        str(Path(__file__).resolve().parents[2] / "frontend" / "dist"),
    ]
    for candidate in candidates:
        if candidate and (Path(candidate) / "index.html").is_file():
            return Path(candidate)
    return None


_UI = ui_dir()
if _UI is not None:
    if (_UI / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=_UI / "assets"), name="ui-assets")

    @app.get("/", include_in_schema=False)
    def ui_index() -> HTMLResponse:
        # no-cache: a rebuilt UI must replace the old one on the next reload
        return HTMLResponse((_UI / "index.html").read_text(encoding="utf-8"),
                            headers={"Cache-Control": "no-cache"})

    @app.get("/{asset_name}.svg", include_in_schema=False)
    def ui_icon(asset_name: str):
        path = _UI / f"{asset_name}.svg"
        if not path.is_file() or path.parent != _UI:
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(path, media_type="image/svg+xml")
