from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from quantum_gw import __version__
from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import AnalysisResult, DocumentInput
from quantum_gw.settings import load_settings

app = FastAPI(title="AI Quantum Greenwashing Agent", version=__version__)


class InlineDocument(BaseModel):
    name: str
    text: str
    role: DocumentRole = DocumentRole.EVIDENCE
    source_type: SourceType = SourceType.INTERNAL
    metadata: dict = Field(default_factory=dict)


class AnalyzeTextRequest(BaseModel):
    documents: list[InlineDocument]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.post("/v1/analyze/text", response_model=AnalysisResult)
def analyze_text(request: AnalyzeTextRequest) -> AnalysisResult:
    try:
        docs = [DocumentInput(**item.model_dump()) for item in request.documents]
        return OrchestratorAgent(load_settings()).run(docs)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/analyze/files", response_model=AnalysisResult)
async def analyze_files(
    files: list[UploadFile] = File(...),
    roles: str = Form("claim_source"),
    source_types: str = Form("internal"),
) -> AnalysisResult:
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
            return OrchestratorAgent(load_settings()).run(documents)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
