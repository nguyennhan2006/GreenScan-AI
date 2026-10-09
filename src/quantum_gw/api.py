from __future__ import annotations

import os
import shutil
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
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import AnalysisResult, ClaimSuggestion, DocumentInput
from quantum_gw.jobs import JobRunner
from quantum_gw.providers import ModelGateway
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


class AnalyzeResponse(BaseModel):
    # run_id is duplicated at the top level so clients can route on it
    # without reaching into the result payload.
    run_id: str
    result: AnalysisResult
    suggestions: list[ClaimSuggestion]
    # The session name a reviewer gave the run (History, sidebar); empty when
    # the run was never named or has only just been produced.
    label: str = ""


def _analyze(documents: list[DocumentInput]) -> AnalyzeResponse:
    result = OrchestratorAgent(load_settings()).run(documents)
    return AnalyzeResponse(run_id=result.run_id, result=result, suggestions=SuggestionAgent().run(result))


def _run_store() -> RunStore:
    return RunStore(load_settings().runs_dir)


# One worker: the pipeline is CPU-bound and two runs side by side on a laptop
# finish later than the same two in a row (QUANTUM_JOB_WORKERS to change).
JOBS = JobRunner(workers=int(os.environ.get("QUANTUM_JOB_WORKERS", "1")))


def _with_company(documents: list[DocumentInput], company: str) -> list[DocumentInput]:
    name = (company or "").strip()
    if not name:
        return documents
    return [d.model_copy(update={"metadata": {**d.metadata, "company": name}}) for d in documents]


def _job(documents: list[DocumentInput], label: str):
    def work(progress) -> str:
        result = OrchestratorAgent(load_settings()).run(documents, progress=progress)
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
    for index, upload in enumerate(files):
        record = store.put(await upload.read(), upload.filename or f"upload-{index}.txt")
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
    try:
        docs = [DocumentInput(**item.model_dump()) for item in request.documents]
        return _analyze(docs)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/analyze/files", response_model=AnalyzeResponse)
async def analyze_files(
    files: list[UploadFile] = File(...),
    roles: str = Form("claim_source"),
    source_types: str = Form("internal"),
) -> AnalyzeResponse:
    try:
        documents = await _stored_uploads(files, roles, source_types)
        # The pipeline is CPU-bound and synchronous: run on the event loop it
        # froze every other request, /health included, for the whole analysis.
        return await run_in_threadpool(_analyze, documents)
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
) -> dict:
    """Start an analysis and return at once; poll `GET /v1/jobs/{job_id}`."""
    try:
        documents = _with_company(await _stored_uploads(files, roles, source_types), company)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    job = JOBS.submit(_job(documents, label), label=label)
    return JOBS.status(job.job_id) or {}


@app.post("/v1/jobs/analyze/text", status_code=202)
def start_analysis_text(request: AnalyzeTextRequest) -> dict:
    try:
        documents = [DocumentInput(**item.model_dump()) for item in request.documents]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    job = JOBS.submit(_job(_with_company(documents, request.company), request.label), label=request.label)
    return JOBS.status(job.job_id) or {}


@app.get("/v1/jobs/{job_id}")
def job_status(job_id: str) -> dict:
    status = JOBS.status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found (jobs are kept in memory until restart)")
    return status


# ---------- what this installation actually runs ----------


_RETRIEVAL_DETAIL = {
    "lite": "BM25 + n-gram ký tự, hợp nhất RRF (chạy trên CPU, không tải mô hình).",
    "fpt": "BM25 + vector {fpt} qua FPT AI Marketplace.",
    "local": "BM25 + vector {model} chạy trên máy ({device}).",
    "http": "BM25 + vector qua dịch vụ nhúng nội bộ.",
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
        retrieval += f" Sắp xếp lại bằng cross-encoder ({settings.reranker.provider})."
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
        "mode": "cloud" if cloud else "offline",
        "label": "Có dùng AI đám mây cho phần khó" if cloud else "Ngoại tuyến — không gửi tài liệu ra ngoài",
        "sends_documents_out": cloud,
        "tasks": tasks,
        "ocr": {
            "enabled": settings.intake.ocr_enabled,
            "available": shutil.which(settings.intake.tesseract_command) is not None,
            "languages": settings.intake.ocr_languages,
        },
        "hardware": hardware,
    }


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


@app.post("/v1/reviews")
def create_review(request: ReviewRequest) -> dict:
    """Record one human decision. Append-only; never edits an earlier one."""
    try:
        record = ReviewStore().record(**request.model_dump())
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
    if format not in _EXPORTS:
        raise HTTPException(status_code=400, detail=f"format must be one of {sorted(_EXPORTS)}")
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
