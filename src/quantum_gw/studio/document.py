"""Run documents as lines of text, and the analysis findings anchored in them.

The editor shows a document one paragraph per line. A PDF paragraph is a text
block of its page, so every line keeps the page it came from; a DOCX paragraph
is a `w:p`, numbered as `parsers/office.py` numbers them, so the export can
write tracked changes back into the same paragraph.

A document is either under review (the report whose claims were extracted --
editable) or evidence (financial statements, law, third-party data --
read-only, always). Decided by Nhân on 14/10: evidence is never edited, so the
role is derived conservatively: only documents that produced claims are
editable.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import fitz

from quantum_gw.agents.verifier import INDEPENDENT_SOURCE_TYPES, missing_attributes
from quantum_gw.domain.models import AnalysisResult
from quantum_gw.labels_vi import VERDICT
from quantum_gw.parsers.documents import GARBLED_PAGE
from quantum_gw.parsers.integrity import visible_blocks
from quantum_gw.parsers.ocr import TesseractOCR, contains_number
from quantum_gw.parsers.office import docx_paragraphs, html_text
from quantum_gw.parsers.text_quality import garbled_share
from quantum_gw.settings import IntakeSettings
from quantum_gw.storage.documents import DocumentStore

# `fold` lives in utils.text so the legal layer can use it without the PDF stack;
# studio.suggest and the tests still import it from this module.
from quantum_gw.utils.text import fold, join_wrapped_lines, normalize_text

UNDER_REVIEW = "under_review"
EVIDENCE = "evidence"

# The queue, the claim page and Studio name a verdict the same way (labels_vi.VERDICT):
# "Ủng hộ một phần" in one place and "Khớp một phần" in another was seen in the demo video.
STATUS_LABELS = VERDICT
INDEPENDENT_SOURCES = INDEPENDENT_SOURCE_TYPES  # one definition with the verifier's support guard


def _one_line(text: str) -> str:
    text = join_wrapped_lines(normalize_text(text))
    return re.sub(r"\s+", " ", text).strip()


def _ocr_reading(ocr: TesseractOCR, page: fitz.Page, digest: str, page_number: int,
                 cache_dir: str | Path | None) -> dict:
    """Tesseract's reading of one page and how sure it was, cached by file hash, page and languages.

    `{"text", "ocr_confidence", "ocr_doubtful_numbers"}`, the same measures the
    analysis records (parsers/ocr.py OcrReading.summary).
    """
    cache = None
    if cache_dir is not None:
        cache = Path(cache_dir) / f"{digest[:24]}_{page_number}_{ocr.languages.replace('+', '-')}.json"
        if cache.is_file():
            try:
                return json.loads(cache.read_text(encoding="utf-8"))
            except ValueError:
                pass
    reading = ocr.read_page(page)
    out = {"text": reading.text, **reading.summary()} if reading.text.strip() else {"text": ""}
    if cache is not None and out["text"]:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def _ocr_paragraphs(text: str) -> list[str]:
    """OCR lines grouped into paragraphs: a blank line or a line ending a sentence closes one."""
    out, current = [], []
    for line in normalize_text(text).split("\n"):
        if not line.strip():
            if current:
                out.append(_one_line("\n".join(current)))
                current = []
            continue
        current.append(line)
        if re.search(r"[.!?:;]\s*$", line):
            out.append(_one_line("\n".join(current)))
            current = []
    if current:
        out.append(_one_line("\n".join(current)))
    return [p for p in out if p]


def paragraphs(path: str | Path, intake: IntakeSettings | None = None, cache_dir: str | Path | None = None) -> list[dict]:
    """`{"text", "page", "index"}` per paragraph, `"ocr": True` on a page read by OCR; texts never contain a newline.

    A PDF is read the way the analysis read it (parsers/documents.py): text no
    reader can see is left out, and with `intake` given, a page with too little
    native text is read by OCR. Without that, every claim found on a scanned page
    was "not located" here and could not be edited. OCR output is cached per
    file and page under `cache_dir`, so a document is read by Tesseract once.
    """
    path = Path(path)
    suffix = path.suffix.lower()
    out: list[dict] = []
    if suffix == ".pdf":
        pdf = fitz.open(path)
        ocr = None
        if intake is not None and intake.ocr_enabled:
            ocr = TesseractOCR(intake.tesseract_command, intake.ocr_languages)
        digest = None
        for page_number, page in enumerate(pdf, start=1):
            blocks, _hidden = visible_blocks(page)
            texts = [_one_line(b[4]) for b in sorted(blocks, key=lambda b: (round(b[1], 1), round(b[0], 1)))
                     if b[6] == 0]  # 1 = image block
            texts = [t for t in texts if t]
            native_text = "\n".join(normalize_text(b[4]) for b in blocks if b[6] == 0 and normalize_text(b[4]))
            # The analysis' rule (parsers/documents.py): too little text, or a garbled
            # legacy-font layer, and the page is read by OCR.
            needs_ocr = len(native_text) < intake.min_native_text_chars if intake is not None else False
            if intake is not None and not needs_ocr:
                needs_ocr = garbled_share(native_text) >= GARBLED_PAGE
            if ocr is not None and needs_ocr and ocr.available:
                digest = digest or hashlib.sha256(path.read_bytes()).hexdigest()
                reading = _ocr_reading(ocr, page, digest, page_number, cache_dir)
                read = _ocr_paragraphs(reading["text"])
                if read:
                    for text in read:
                        doubtful = [n for n in reading.get("ocr_doubtful_numbers", []) if contains_number(text, n)]
                        out.append({"text": text, "page": page_number, "index": len(out), "ocr": True,
                                    "ocr_confidence": reading.get("ocr_confidence"),
                                    **({"doubtful_numbers": doubtful} if doubtful else {})})
                    continue
            for text in texts:
                out.append({"text": text, "page": page_number, "index": len(out)})
        pdf.close()
        return out
    if suffix == ".docx":
        return [{"text": _one_line(p["text"]) if p["text"].strip() else "", "page": None, "index": p["index"],
                 "style": p["style"]} for p in docx_paragraphs(path)]
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if suffix in {".html", ".htm"}:
        raw = html_text(raw)
    for block in re.split(r"\n\s*\n", normalize_text(raw)):
        text = _one_line(block)
        if text:
            out.append({"text": text, "page": None, "index": len(out)})
    return out


def run_documents(result: AnalysisResult, store: DocumentStore) -> list[dict]:
    """Every input document of the run, located in the document store, with its role."""
    claim_doc_ids = {c.source_doc_id for c in result.claims}
    claim_names = {c.source_name for c in result.claims}
    docs = []
    for key, sha in result.manifest.input_hashes.items():
        name = key.split(":", 1)[1] if ":" in key else key
        record = store.find(sha, name)
        if record is None:
            docs.append({"doc_id": None, "name": name, "role": EVIDENCE, "available": False, "kind": Path(name).suffix.lstrip(".")})
            continue
        role = UNDER_REVIEW if (record.doc_id in claim_doc_ids or name in claim_names) else EVIDENCE
        docs.append({
            "doc_id": record.doc_id, "name": name, "role": role, "available": True,
            "kind": record.path.suffix.lstrip(".").lower(), "sha256": record.sha256,
            "claims": sum(1 for c in result.claims if c.source_doc_id == record.doc_id or c.source_name == name),
        })
    return docs


# ---------- locating claims in the text ----------

def _collapse(text: str) -> tuple[str, list[int]]:
    """Folded text with whitespace runs collapsed, plus each output char's offset in the input."""
    out, where = [], []
    folded = fold(text)
    previous_space = False
    for i, char in enumerate(folded):
        if char.isspace():
            if previous_space:
                continue
            out.append(" ")
            previous_space = True
        else:
            out.append(char)
            previous_space = False
        where.append(i)
    return "".join(out), where


class Locator:
    """Finds a claim sentence in the editor text, tolerating whitespace, accents and line wraps."""

    def __init__(self, text: str):
        self.text = text
        self.collapsed, self.where = _collapse(text)

    def find(self, needle: str, start: int = 0) -> tuple[int, int] | None:
        target, _ = _collapse(needle.strip())
        target = target.strip()
        if len(target) < 8:
            return None
        cstart = next((i for i, w in enumerate(self.where) if w >= start), 0) if start else 0
        index = self.collapsed.find(target, cstart)
        if index < 0 and cstart:
            index = self.collapsed.find(target)
        if index < 0:
            return None
        end = index + len(target) - 1
        return self.where[index], self.where[end] + 1

    def find_prefix(self, needle: str, size: int = 60) -> tuple[int, int] | None:
        """A claim that crossed a PDF block boundary: anchor its opening words, up to the end of that line."""
        target, _ = _collapse(needle.strip())
        target = target.strip()
        if len(target) < 24:
            return None
        index = self.collapsed.find(target[:size])
        if index < 0:
            return None
        start = self.where[index]
        line_end = self.text.find("\n", start)
        line_end = len(self.text) if line_end < 0 else line_end
        return start, min(line_end, start + len(needle))


def _line_starts(lines: list[str]) -> list[int]:
    starts, offset = [], 0
    for line in lines:
        starts.append(offset)
        offset += len(line) + 1
    return starts


# ---------- diagnostics ----------

_ATTRIBUTE_NAMES = (("metric", "chỉ số"), ("values", "giá trị"), ("period", "kỳ"), ("baseline", "năm gốc"),
                    ("scope", "phạm vi"))


def _missing_attributes(claim) -> list[str]:
    """The verifier's definition (agents/verifier.py missing_attributes), named the way the report names them."""
    gaps = set(missing_attributes(claim))
    return [name for key, name in _ATTRIBUTE_NAMES if key in gaps]


def _severity(status: str, risk, legal: dict | None, claim) -> str:
    if status == "CONTRADICTED":
        return "error"
    if risk is not None and str(risk.severity) in {"HIGH", "CRITICAL", "Severity.HIGH", "Severity.CRITICAL"}:
        return "error"
    if legal and legal.get("legal_risk") == "HIGH" and legal.get("rules_applied"):
        return "error"
    if status != "SUPPORTED" or claim.is_vague:
        return "warning"
    return "info"


def _legal_view(legal: dict | None) -> dict | None:
    if not legal:
        return None
    sources = []
    for s in legal.get("applicable_sources", [])[:4]:
        sources.append({
            "document": s.get("document"), "title": s.get("title"), "url": s.get("source_url"),
            "effective_from": s.get("effective_from"),
            "verified": bool(s.get("reviewed_by")),
            "verification_label": f"Đã xác minh bởi {s['reviewed_by']}" if s.get("reviewed_by") else "Chưa có người xác minh",
        })
    return {
        "finding": legal.get("legal_finding"), "risk": legal.get("legal_risk"),
        "rules_applied": legal.get("rules_applied", []), "notes": legal.get("notes", ""),
        "rule_pack": legal.get("rule_pack_version"), "sources": sources,
        "requires_human_review": legal.get("requires_human_review", True),
    }


def diagnostics(result: AnalysisResult, doc: dict, text: str) -> tuple[list[dict], list[dict]]:
    """Diagnostics for claims found in `text`, and the claims no longer found (edited away)."""
    verifications = {v.claim.claim_id: v for v in result.verifications}
    risks = {r.claim_id: r for r in result.risks}
    priorities = {p.get("claim_id"): p for p in result.priorities if p.get("claim_id")}
    legal = {lc.get("claim_id"): lc for lc in (getattr(result, "legal_checks", None) or [])}
    locator = Locator(text)
    found, gone = [], []
    for claim in result.claims:
        if not (claim.source_doc_id == doc.get("doc_id") or claim.source_name == doc.get("name")):
            continue
        span = locator.find(claim.text) or locator.find_prefix(claim.text)
        if span is None:
            gone.append({"claim_id": claim.claim_id, "text": claim.text})
            continue
        verification = verifications.get(claim.claim_id)
        status = verification.status.value if verification else "INSUFFICIENT_EVIDENCE"
        risk = risks.get(claim.claim_id)
        lc = legal.get(claim.claim_id)
        missing = _missing_attributes(claim)
        evidence = []
        for e in (verification.evidence if verification else [])[:4]:
            evidence.append({
                "source_name": e.source_name, "page": e.page, "text": e.text[:400],
                "relation": getattr(e, "relation", None), "relation_reason": getattr(e, "relation_reason", None),
                "independent": e.source_type.value in INDEPENDENT_SOURCES, "doc_id": e.doc_id,
                "citation": e.citation, "source_type": e.source_type.value,
                "score": e.score, "lexical_score": e.lexical_score, "semantic_score": e.semantic_score,
                "is_table": e.is_table,
            })
        priority = priorities.get(claim.claim_id) or {}
        parts = [STATUS_LABELS.get(status, status)]
        if missing:
            parts.append("thiếu " + ", ".join(missing))
        if claim.vague_terms_matched:
            parts.append("mơ hồ")
        if evidence and not any(e["independent"] for e in evidence):
            parts.append("không có nguồn độc lập")
        found.append({
            "id": claim.claim_id,
            "claim_id": claim.claim_id,
            "from": span[0], "to": span[1],
            "severity": _severity(status, risk, lc, claim),
            "message": " · ".join(parts),
            "status": status, "status_label": STATUS_LABELS.get(status, status),
            "rationale": verification.rationale if verification else "",
            "claim_type": claim.claim_type, "page": claim.source_page,
            "missing": missing, "vague_terms": claim.vague_terms_matched,
            "risk_score": risk.risk_score if risk else None,
            "risk_severity": str(risk.severity.value if hasattr(risk.severity, "value") else risk.severity) if risk else None,
            "priority_rank": priority.get("rank"), "in_queue": bool(priority.get("in_queue")),
            "priority_reasons": priority.get("reasons", [])[:4],
            "evidence": evidence,
            "legal": _legal_view(lc),
            "confidence": claim.confidence,
        })
    found.sort(key=lambda d: d["from"])
    return found, gone


def document_view(result: AnalysisResult, doc: dict, path: Path) -> dict:
    base = paragraphs(path)
    return {"paragraphs": base, "base_text": "\n".join(p["text"] for p in base)}


def line_pages(paras: list[dict]) -> list[int | None]:
    return [p.get("page") for p in paras]


__all__ = [
    "EVIDENCE", "UNDER_REVIEW", "Locator", "diagnostics", "document_view", "fold",
    "line_pages", "paragraphs", "run_documents", "_line_starts",
]
