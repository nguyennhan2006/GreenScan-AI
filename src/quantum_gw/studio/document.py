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

import re
import unicodedata
from pathlib import Path

import fitz

from quantum_gw.domain.models import AnalysisResult
from quantum_gw.parsers.office import docx_paragraphs, html_text
from quantum_gw.storage.documents import DocumentStore
from quantum_gw.utils.text import join_wrapped_lines, normalize_text

UNDER_REVIEW = "under_review"
EVIDENCE = "evidence"

STATUS_LABELS = {
    "SUPPORTED": "Có bằng chứng xác nhận",
    "PARTIALLY_SUPPORTED": "Khớp một phần",
    "CONTRADICTED": "Mâu thuẫn với bằng chứng",
    "UNSUPPORTED": "Không có bằng chứng",
    "INSUFFICIENT_EVIDENCE": "Chưa đủ bằng chứng",
}
INDEPENDENT_SOURCES = {"legal", "external", "standard"}


def fold(text: str) -> str:
    """Accent-free lower case with the same length as the input, so offsets carry over."""
    out = []
    for char in text:
        base = unicodedata.normalize("NFD", char)[0]
        out.append("d" if base in "đĐ" else base.lower())
    return "".join(out)


def _one_line(text: str) -> str:
    text = join_wrapped_lines(normalize_text(text))
    return re.sub(r"\s+", " ", text).strip()


def paragraphs(path: str | Path) -> list[dict]:
    """`{"text", "page", "index"}` per paragraph; texts never contain a newline."""
    path = Path(path)
    suffix = path.suffix.lower()
    out: list[dict] = []
    if suffix == ".pdf":
        pdf = fitz.open(path)
        for page_number, page in enumerate(pdf, start=1):
            blocks = sorted(page.get_text("blocks"), key=lambda b: (round(b[1], 1), round(b[0], 1)))
            for block in blocks:
                if block[6] != 0:  # image block
                    continue
                text = _one_line(block[4])
                if text:
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

def _missing_attributes(claim) -> list[str]:
    missing = []
    if not claim.metric:
        missing.append("chỉ số")
    if not claim.values:
        missing.append("số liệu")
    if not claim.period:
        missing.append("kỳ")
    if (claim.direction or claim.is_future_commitment) and not claim.baseline:
        missing.append("năm gốc")
    if not claim.scope:
        missing.append("phạm vi")
    return missing


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
