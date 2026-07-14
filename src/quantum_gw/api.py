from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from quantum_gw import __version__
from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.agents.suggester import SuggestionAgent
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import AnalysisResult, ClaimSuggestion, DocumentInput
from quantum_gw.settings import load_settings

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
    metadata: dict = Field(default_factory=dict)


class AnalyzeTextRequest(BaseModel):
    documents: list[InlineDocument]


class AnalyzeResponse(BaseModel):
    result: AnalysisResult
    suggestions: list[ClaimSuggestion]


def _analyze(documents: list[DocumentInput]) -> AnalyzeResponse:
    result = OrchestratorAgent(load_settings()).run(documents)
    return AnalyzeResponse(result=result, suggestions=SuggestionAgent().run(result))


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


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
        with tempfile.TemporaryDirectory(prefix="quantum-upload-") as tmp:
            documents = []
            for index, upload in enumerate(files):
                target = Path(tmp) / (upload.filename or f"upload-{index}.txt")
                target.write_bytes(await upload.read())
                documents.append(
                    DocumentInput(
                        path=str(target),
                        name=upload.filename,
                        role=DocumentRole(role_values[index] if len(role_values) > 1 else role_values[0]),
                        source_type=SourceType(type_values[index] if len(type_values) > 1 else type_values[0]),
                    )
                )
            return _analyze(documents)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
