"""HTTP routes for intake preview and GreenScan Studio.

Kept out of api.py, which carries the analysis and review routes; mounted by
`app.include_router(router)` there, so it inherits the `/api` prefix handling.
"""

from __future__ import annotations

import json
import tempfile
import threading
import time
import urllib.parse
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, HTMLResponse, Response
from pydantic import BaseModel, Field

from quantum_gw.intake import FetchError, fetch_url, preview_file, sample_file, sample_sets
from quantum_gw.settings import load_settings
from quantum_gw.storage.documents import DocumentStore
from quantum_gw.storage.runs import RunStore
from quantum_gw.studio import escalation
from quantum_gw.studio.document import UNDER_REVIEW, diagnostics, paragraphs, run_documents
from quantum_gw.studio.export import (
    changes,
    docx_from_lines,
    docx_in_place,
    pdf_from_lines,
    review_html,
)
from quantum_gw.studio.session import StudioSession, sha
from quantum_gw.studio.suggest import KIND_LABELS, suggest

router = APIRouter()

_ACCEPTED = {".pdf", ".docx", ".txt", ".md", ".json", ".csv", ".html", ".htm"}


# ---------- intake ----------

@router.post("/v1/intake/preview")
async def intake_preview(files: list[UploadFile] = File(...)) -> dict:
    settings = load_settings()
    previews = []
    for upload in files:
        name = upload.filename or "tai-lieu"
        suffix = Path(name).suffix.lower()
        if suffix not in _ACCEPTED:
            previews.append({"name": name, "kind": suffix.lstrip("."), "error": f"Chưa hỗ trợ tệp {suffix or 'không đuôi'}."})
            continue
        data = await upload.read()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / f"preview{suffix}"
            path.write_bytes(data)
            try:
                preview = await run_in_threadpool(preview_file, path, name, settings.intake)
            except Exception as exc:  # noqa: BLE001 - a broken file is reported per file
                preview = {"name": name, "kind": suffix.lstrip("."), "error": f"Không đọc được tệp: {exc}"}
        preview["bytes"] = len(data)
        previews.append(preview)
    return {"files": previews}


@router.get("/v1/intake/fetch")
def intake_fetch(url: str) -> Response:
    try:
        data, name = fetch_url(url)
    except FetchError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - network errors are the user's to read
        raise HTTPException(status_code=502, detail=f"Không tải được: {exc}") from exc
    return Response(content=data, media_type="application/octet-stream",
                    headers={"X-File-Name": urllib.parse.quote(name)})


@router.get("/v1/intake/samples")
def intake_samples() -> dict:
    return {"samples": sample_sets()}


@router.get("/v1/intake/samples/{sample_id}/{index}")
def intake_sample_file(sample_id: str, index: int):
    path = sample_file(sample_id, index)
    if path is None:
        raise HTTPException(status_code=404, detail="Không có tệp mẫu này trên máy.")
    return FileResponse(path, filename=path.name)


# ---------- studio ----------

_PARAGRAPHS: dict[tuple[str, float], list[dict]] = {}
_LOCK = threading.Lock()


def _paragraphs(path: Path) -> list[dict]:
    key = (str(path), path.stat().st_mtime)
    with _LOCK:
        if key in _PARAGRAPHS:
            return _PARAGRAPHS[key]
    paras = paragraphs(path)
    with _LOCK:
        if len(_PARAGRAPHS) > 16:
            _PARAGRAPHS.clear()
        _PARAGRAPHS[key] = paras
    return paras


def _load(run_id: str):
    store = RunStore(load_settings().runs_dir)
    if not store.exists(run_id):
        raise HTTPException(status_code=404, detail="Không có phiên phân tích này.")
    return store, store.load(run_id)


def _doc(run_id: str, doc_id: str):
    store, result = _load(run_id)
    documents = DocumentStore()
    doc = next((d for d in run_documents(result, documents) if d["doc_id"] == doc_id), None)
    if doc is None:
        raise HTTPException(status_code=404, detail="Tài liệu không thuộc phiên này hoặc không còn trên máy.")
    record = documents.get(doc_id) or documents.find(doc["sha256"], doc["name"])
    paras = _paragraphs(record.path)
    base_text = "\n".join(p["text"] for p in paras)
    return store, result, doc, record, paras, base_text


_CLOUD: dict[str, float | bool] = {}
_UNANCHORED: dict[tuple[str, str, str], set[str]] = {}


def _cloud_allowed() -> bool:
    """Whether this process may send text out; runtime() costs ~0.6 s, so it is read once a minute."""
    from quantum_gw.api import runtime  # lazy: api imports this module

    now = time.monotonic()
    if not _CLOUD or now - float(_CLOUD["at"]) > 60:
        _CLOUD.update(at=now, value=bool(runtime().get("sends_documents_out")))
    return bool(_CLOUD["value"])


def _unanchored(result, doc: dict, base_text: str) -> set[str]:
    """Claims not found even in the original text; fixed per run and document, so computed once."""
    key = (result.run_id, doc["doc_id"], sha(base_text))
    if key not in _UNANCHORED:
        _UNANCHORED[key] = {g["claim_id"] for g in diagnostics(result, doc, base_text)[1]}
    return _UNANCHORED[key]


@router.get("/v1/studio/{run_id}")
def studio_documents(run_id: str) -> dict:
    store, result = _load(run_id)
    return {
        "run_id": run_id, "label": store.label_of(run_id), "entity": result.entity,
        "documents": run_documents(result, DocumentStore()),
        "kinds": KIND_LABELS, "doc_classes": escalation.DOC_CLASSES,
    }


def _view(result, doc: dict, paras: list[dict], base_text: str, data: dict) -> dict:
    text = data["text"]
    editable = doc["role"] == UNDER_REVIEW
    diags, gone = diagnostics(result, doc, text) if editable else ([], [])
    unanchored_ids = _unanchored(result, doc, base_text) if editable else set()
    tau = escalation.configured_tau()
    cloud = _cloud_allowed()
    # A rule already accepted or rejected for a claim is not offered again; a
    # claim the reviewer accepted a fix for, or dismissed with a reason, is resolved.
    decided: dict[str, set[str]] = {}
    resolution: dict[str, dict] = {}
    for entry in data["log"]:
        claim_id = entry.get("claim_id")
        if not claim_id:
            continue
        if entry.get("action") in {"accept", "reject"} and entry.get("rule_code"):
            decided.setdefault(claim_id, set()).add(entry["rule_code"])
        if entry.get("action") in {"accept", "ignore", "edit", "rework", "reject"}:
            resolution[claim_id] = entry
    for d in diags:
        d["text"] = text[d["from"]:d["to"]]
        done = decided.get(d["claim_id"], set())
        d["suggestions"] = [s.to_json() for s in suggest(d, d["text"]) if s.rule_code not in done]
        last = resolution.get(d["claim_id"])
        # Resolved: dismissed with a reason, edited by hand, or every suggestion decided.
        d["resolved"] = bool(last) and (last["action"] in {"ignore", "edit", "rework"} or not d["suggestions"])
        d["resolution"] = last
        d["escalation"] = escalation.decide(d.get("confidence"), data.get("doc_class", "B"), tau, cloud)
    claims = {c.claim_id: c for c in result.claims}
    return {
        "doc": doc, "editable": editable,
        "paragraphs": [{"page": p.get("page"), "index": p["index"]} for p in paras],
        "base_text": base_text, "text": text,
        "diagnostics": diags,
        "edited": [g for g in gone if g["claim_id"] not in unanchored_ids],
        "unanchored": [{**g, "page": claims[g["claim_id"]].source_page if g["claim_id"] in claims else None}
                       for g in gone if g["claim_id"] in unanchored_ids],
        "log": data["log"], "versions": [{k: v for k, v in x.items() if k != "text"} for x in data["versions"]],
        "doc_class": data.get("doc_class", "B"), "tau": tau, "cloud": cloud,
        "layout_note": _layout_note(doc["kind"]),
    }


def _layout_note(kind: str) -> str:
    if kind == "docx":
        return "Bản DOCX xuất ra sửa trên chính tệp gốc: đoạn không đổi giữ nguyên định dạng."
    if kind == "pdf":
        return "PDF được sửa trên văn bản đã trích; bản xuất dựng lại từ văn bản và KHÔNG giữ bố cục gốc."
    return "Văn bản thuần: bản xuất dựng lại từ văn bản."


@router.get("/v1/studio/{run_id}/doc/{doc_id}")
def studio_doc(run_id: str, doc_id: str) -> dict:
    store, result, doc, _record, paras, base_text = _doc(run_id, doc_id)
    data = StudioSession(store._dir(run_id), doc_id).load(base_text, doc["name"])
    return _view(result, doc, paras, base_text, data)


class StudioSave(BaseModel):
    text: str
    log: list[dict] = Field(default_factory=list)
    snapshot: bool = False
    note: str = ""
    doc_class: str | None = None


@router.put("/v1/studio/{run_id}/doc/{doc_id}")
def studio_save(run_id: str, doc_id: str, body: StudioSave) -> dict:
    store, result, doc, _record, paras, base_text = _doc(run_id, doc_id)
    if doc["role"] != UNDER_REVIEW:
        raise HTTPException(status_code=403, detail="Tài liệu bằng chứng chỉ được đọc, không được sửa.")
    try:
        data = StudioSession(store._dir(run_id), doc_id).save(
            base_text, body.text, body.log, body.note, body.snapshot, body.doc_class, doc["name"])
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _view(result, doc, paras, base_text, data)


class StudioRestore(BaseModel):
    version: int


@router.post("/v1/studio/{run_id}/doc/{doc_id}/restore")
def studio_restore(run_id: str, doc_id: str, body: StudioRestore) -> dict:
    store, result, doc, _record, paras, base_text = _doc(run_id, doc_id)
    if doc["role"] != UNDER_REVIEW:
        raise HTTPException(status_code=403, detail="Tài liệu bằng chứng chỉ được đọc.")
    try:
        data = StudioSession(store._dir(run_id), doc_id).restore(base_text, body.version)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Không có phiên bản này.") from exc
    return _view(result, doc, paras, base_text, data)


_MEDIA = {
    "docx_tracked": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "-da-sua-tracked.docx"),
    "docx_clean": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "-da-sua.docx"),
    "pdf": ("application/pdf", "-da-sua.pdf"),
    "review_html": ("text/html; charset=utf-8", "-bao-cao-ra-soat.html"),
    "audit_json": ("application/json", "-vet-kiem-toan.json"),
}


@router.get("/v1/studio/{run_id}/doc/{doc_id}/export")
def studio_export(run_id: str, doc_id: str, format: str = "docx_tracked", user: str = ""):  # noqa: A002
    if format not in _MEDIA:
        raise HTTPException(status_code=400, detail=f"format phải là một trong {sorted(_MEDIA)}")
    store, result, doc, record, paras, base_text = _doc(run_id, doc_id)
    data = StudioSession(store._dir(run_id), doc_id).load(base_text, doc["name"])
    base_lines = [p["text"] for p in paras]
    new_lines = data["text"].split("\n")
    stem = Path(doc["name"]).stem
    media, suffix = _MEDIA[format]
    filename = urllib.parse.quote(stem + suffix)
    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    notes: list[str] = []
    if format in {"docx_tracked", "docx_clean"}:
        tracked = format == "docx_tracked"
        if doc["kind"] == "docx":
            content, notes = docx_in_place(record.path, base_lines, new_lines, data["log"], user, tracked)
        else:
            content = docx_from_lines(base_lines, new_lines, [p.get("page") for p in paras], data["log"], user,
                                      tracked, title=doc["name"])
        headers["X-Export-Notes"] = urllib.parse.quote(" ".join(notes))
        return Response(content=content, media_type=media, headers=headers)
    change_list = changes(base_lines, new_lines)
    if format == "pdf":
        try:
            content = pdf_from_lines(new_lines, change_list, doc["name"], _layout_note(doc["kind"]))
        except RuntimeError as exc:
            raise HTTPException(status_code=501, detail=str(exc)) from exc
        return Response(content=content, media_type=media, headers=headers)
    view = _view(result, doc, paras, base_text, data)
    exported_at = datetime.now(UTC).isoformat(timespec="seconds")
    if format == "review_html":
        page = review_html({
            "doc_name": doc["name"], "run_id": run_id, "exported_at": exported_at, "user": user,
            "diagnostics": view["diagnostics"], "gone": view["edited"], "log": data["log"],
            "changes": change_list, "layout_note": view["layout_note"],
            "base_sha256": sha(base_text), "final_sha256": sha(data["text"]),
        })
        return HTMLResponse(page, headers=headers)
    trail = {
        "schema": "greenscan-studio-audit-v1", "run_id": run_id, "exported_at": exported_at, "user": user,
        "document": {k: doc.get(k) for k in ("doc_id", "name", "role", "kind", "sha256")},
        "manifest": {"pipeline_version": result.manifest.pipeline_version, "config_hash": result.manifest.config_hash,
                     "input_hashes": result.manifest.input_hashes},
        "base_text_sha256": sha(base_text), "final_text_sha256": sha(data["text"]),
        "doc_class": data.get("doc_class"), "escalation_tau": view["tau"], "cloud_allowed": view["cloud"],
        "log": data["log"], "versions": view["versions"], "changes": change_list,
        "open_findings": [{k: d[k] for k in ("claim_id", "severity", "status", "message", "missing")} for d in view["diagnostics"]],
        "edited_away": view["edited"],
    }
    return Response(content=json.dumps(trail, ensure_ascii=False, indent=2), media_type=media, headers=headers)
