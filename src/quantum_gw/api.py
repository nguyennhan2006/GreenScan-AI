from __future__ import annotations

import os

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from quantum_gw import __version__
from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.agents.suggester import SuggestionAgent
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import AnalysisResult, ClaimSuggestion, DocumentInput
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


class AnalyzeResponse(BaseModel):
    # run_id is duplicated at the top level so clients can route on it
    # without reaching into the result payload.
    run_id: str
    result: AnalysisResult
    suggestions: list[ClaimSuggestion]


def _analyze(documents: list[DocumentInput]) -> AnalyzeResponse:
    result = OrchestratorAgent(load_settings()).run(documents)
    return AnalyzeResponse(run_id=result.run_id, result=result, suggestions=SuggestionAgent().run(result))


def _run_store() -> RunStore:
    return RunStore(load_settings().runs_dir)


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
    role_values = [item.strip() for item in roles.split(",") if item.strip()]
    type_values = [item.strip() for item in source_types.split(",") if item.strip()]
    if len(role_values) not in {1, len(files)} or len(type_values) not in {1, len(files)}:
        raise HTTPException(status_code=400, detail="roles/source_types must contain one value or one per file")
    try:
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
        return _analyze(documents)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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
    return AnalyzeResponse(run_id=result.run_id, result=result, suggestions=SuggestionAgent().run(result))


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
