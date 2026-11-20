"""GreenScan tools shared by the MCP server (mcp_server.py) and the harness (agent_harness.py).

Bounded for the minimum machine (8–16 GB RAM, no GPU): the offline profile (rules, arithmetic, lexical retrieval),
at most 5 files / 80 MB per analysis, short outputs. Measured on the i7-1355U laptop: HPG BCPTBV 2025 + BCTN 2024
in 116 s, 1.3 GB peak memory (settings.py). No tool writes a verdict of its own: verdicts come from the pipeline
(`analyze_documents`) and are only read back; claim attributes, evidence search and assurance patterns are the
product's own code. Every free-text input passes the scope guard first.
"""
from __future__ import annotations

import difflib
import json
import os
import re
from pathlib import Path

os.environ.setdefault("QUANTUM_PROFILE", "offline")   # before quantum_gw.settings is imported anywhere

from quantum_gw.assist.scope_guard import arg_guard, plain, route, scope  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
_AGENTS: dict = {}
LIMITS = {"max_files": 5, "max_mb": 80, "max_list": 50, "max_k": 10, "max_text": 6000, "passage_chars": 700}


def _runs_dir() -> Path:
    from quantum_gw.settings import load_settings
    d = Path(load_settings().runs_dir)
    return d if d.is_absolute() else ROOT / d


def _guard(text: str, field: str = "yêu cầu") -> dict | None:
    """Stop a tool call whose free text is out of scope (injection, write-a-claim, investment...)."""
    if len(text or "") > LIMITS["max_text"]:
        return {"stop": True, "warning": f"{field} dài quá {LIMITS['max_text']} ký tự; hãy chép riêng câu cần xét."}
    cat = arg_guard(text)
    if cat:
        sc = scope()
        return {"stop": True, "category": cat, "warning": f"{sc['warning_prefix']} {sc['out_of_scope'][cat]}"}
    return None


def check_scope(request: str) -> dict:
    r = route(request)
    return {"status": r.status, "stop": r.stop, "category": r.category, "warning": r.warning, "tasks": r.tasks,
            "slots": r.slots, "source": r.source}


# --------------------------------------------------------------------------- runs
def list_runs(limit: int = 10) -> list[dict]:
    out = []
    for d in sorted(_runs_dir().glob("*/result.json"), key=lambda p: p.stat().st_mtime, reverse=True)[: min(limit, LIMITS["max_list"])]:
        try:
            r = json.loads(d.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        docs = [x.get("source_name") for x in (r.get("manifest") or {}).get("documents", [])][:5]
        out.append({"run_id": r.get("run_id") or d.parent.name, "documents": docs, "claims": len(r.get("verifications", [])),
                    "summary": {k: v for k, v in (r.get("summary") or {}).items() if isinstance(v, (int, float, str))}})
    return out


def _result(run_id: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{8,32}", run_id or ""):
        raise ValueError("run_id không hợp lệ")
    p = _runs_dir() / run_id / "result.json"
    if not p.exists():
        raise ValueError(f"không thấy phiên {run_id}; dùng list_runs")
    return json.loads(p.read_text(encoding="utf-8"))


def _brief(v: dict) -> dict:
    c = v["claim"]
    return {"claim": c["text"][:400], "status": v["status"], "page": c.get("source_page"), "source": c.get("source_name"),
            "rationale": (v.get("rationale") or "")[:500], "requires_review": v.get("requires_llm_review")}


def get_claims(run_id: str, status: str | None = None, limit: int = 20, offset: int = 0) -> dict:
    vs = _result(run_id).get("verifications", [])
    if status:
        vs = [v for v in vs if v["status"] == status.upper()]
    limit = min(limit, LIMITS["max_list"])
    return {"run_id": run_id, "total": len(vs), "claims": [_brief(v) for v in vs[offset: offset + limit]]}


def review_queue(run_id: str, limit: int = 10) -> dict:
    """The review queue the pipeline built (priorities: materiality, obligation, risk), highest first; sentences the
    pipeline suspects are not claims (table rows, contents lines) stay out of the queue, as in the product."""
    r = _result(run_id)
    status = {v["claim"]["claim_id"]: v["status"] for v in r.get("verifications", [])}
    sev = {x["claim_id"]: x.get("severity") for x in r.get("risks", [])}
    q = sorted((p for p in r.get("priorities", []) if p.get("in_queue")), key=lambda p: p.get("rank", 1e9))
    out = [{"rank": p.get("rank"), "claim": (p.get("text") or "")[:300], "priority": p.get("priority_score"),
            "status": status.get(p.get("claim_id")), "risk": sev.get(p.get("claim_id")),
            "why": [c["reason"][:160] for c in p.get("components", []) if c.get("score")][:2]} for p in q[: min(limit, LIMITS["max_list"])]]
    held = sum(1 for p in r.get("priorities", []) if not p.get("in_queue"))
    return {"run_id": run_id, "in_queue": len(q), "held_out": held, "queue": out}


def analyze_documents(paths: list[str], roles: list[str] | None = None, source_types: list[str] | None = None) -> dict:
    """Run the offline pipeline (rules + arithmetic + lexical retrieval) on local files; returns the run summary."""
    from quantum_gw.agents.orchestrator import OrchestratorAgent
    from quantum_gw.domain.enums import DocumentRole, SourceType
    from quantum_gw.domain.models import DocumentInput
    from quantum_gw.settings import load_settings
    files = [Path(p) for p in paths]
    if not files or len(files) > LIMITS["max_files"]:
        return {"stop": True, "warning": f"cần 1–{LIMITS['max_files']} tệp"}
    missing = [str(f) for f in files if not f.is_file()]
    if missing:
        return {"stop": True, "warning": f"không thấy tệp: {missing}"}
    mb = sum(f.stat().st_size for f in files) / 1e6
    if mb > LIMITS["max_mb"]:
        return {"stop": True, "warning": f"tổng {mb:.0f} MB vượt giới hạn {LIMITS['max_mb']} MB của máy tối thiểu"}
    roles = roles or ["claim_source"] * len(files)
    source_types = source_types or ["internal"] * len(files)
    docs = [DocumentInput(path=str(f), role=DocumentRole(roles[i]), source_type=SourceType(source_types[i]))
            for i, f in enumerate(files)]
    res = OrchestratorAgent(load_settings()).run(docs)
    rid = Path(res.output_directory).name
    out = get_claims(rid, limit=10)
    return {"run_id": rid, "summary": res.summary.model_dump(mode="json"), "first_claims": out["claims"],
            "evidence_pack": f"{res.output_directory}/evidence_pack.md"}


# --------------------------------------------------------------------------- claim-level tools
def _dummy_chunk(text: str):
    from quantum_gw.domain.enums import DocumentRole, SourceType
    from quantum_gw.domain.models import EvidenceChunk
    return EvidenceChunk(chunk_id="mcp-query", doc_id="mcp-query", source_name="yêu cầu người dùng",
                         role=DocumentRole("claim_source"), source_type=SourceType("internal"), text=text)


def _describe(claim: str):
    from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
    from quantum_gw.settings import load_settings
    from quantum_gw.storage.audit import AuditLogger
    s = load_settings()
    audit = AuditLogger(_runs_dir() / "_mcp" / "audit.jsonl")
    return ClaimExtractionAgent(s.claim_extraction, audit).describe(claim, _dummy_chunk(claim))


def claim_attributes(claim: str) -> dict:
    stop = _guard(claim, "câu tuyên bố")
    if stop:
        return stop
    c = _describe(claim)
    keep = ("claim_type", "metric", "direction", "values", "units", "period", "baseline", "scope", "is_future_commitment",
            "is_vague", "vague_terms_matched", "language")
    d = c.model_dump(mode="json")
    attrs = {k: d.get(k) for k in keep}
    attrs["missing"] = [k for k in ("metric", "values", "period", "baseline", "scope") if not d.get(k)]
    return attrs


def _chunks(run_id: str):
    from quantum_gw.domain.enums import DocumentRole, SourceType
    from quantum_gw.domain.models import EvidenceChunk
    p = _runs_dir() / run_id / "contract" / "clean.jsonl"
    if not p.exists():
        raise ValueError(f"phiên {run_id} không lưu kho đoạn văn")
    out = []
    for line in p.open(encoding="utf-8"):
        r = json.loads(line)
        if r.get("duplicate_of") or not (r.get("text") or "").strip():
            continue
        try:
            out.append(EvidenceChunk(chunk_id=r["unit_id"], doc_id=r["doc_id"], source_name=r["source_name"],
                                     role=DocumentRole(r.get("role") or "claim_source"),
                                     source_type=SourceType(r.get("source_type") or "internal"),
                                     text=r["text"], page=r.get("page"), block_index=r.get("block_index"),
                                     is_table=bool(r.get("is_table"))))
        except ValueError:
            continue
    return out


def find_evidence(claim: str, run_id: str, k: int = 5) -> dict:
    stop = _guard(claim, "câu tuyên bố")
    if stop:
        return stop
    from quantum_gw.agents.retriever import EvidenceRetrievalAgent
    from quantum_gw.settings import load_settings
    from quantum_gw.storage.audit import AuditLogger
    agent = _AGENTS.get(run_id)
    if agent is None:   # one lexical index per run, kept for the next calls (at most 2 runs in memory)
        if len(_AGENTS) >= 2:
            _AGENTS.pop(next(iter(_AGENTS)))
        agent = _AGENTS[run_id] = EvidenceRetrievalAgent(_chunks(run_id), load_settings(),
                                                         AuditLogger(_runs_dir() / "_mcp" / "audit.jsonl"))
    ev = agent.run(_describe(claim))[: min(k, LIMITS["max_k"])]
    return {"run_id": run_id, "passages": [{"source": e.source_name, "page": e.page, "text": e.text[:LIMITS["passage_chars"]],
                                             "score": round(float(getattr(e, "score", 0) or 0), 4)} for e in ev]}


def verify_claim(claim: str, run_id: str) -> dict:
    """The pipeline's verdict for this claim if the run already judged it; otherwise attributes + evidence, no verdict."""
    stop = _guard(claim, "câu tuyên bố")
    if stop:
        return stop
    q = plain(claim)
    best, score = None, 0.0
    for v in _result(run_id).get("verifications", []):
        t = plain(v["claim"]["text"])
        r = 1.0 if (q in t or t in q) and min(len(q), len(t)) >= 20 else difflib.SequenceMatcher(None, q, t).ratio()
        if r > score:
            best, score = v, r
    if best is not None and score >= 0.85:
        out = _brief(best)
        out.update(found=True, match=round(score, 3),
                   evidence=[{"source": e.get("source_name"), "page": e.get("page"), "relation": e.get("relation"),
                              "text": (e.get("text") or "")[:LIMITS["passage_chars"]]} for e in best.get("evidence", [])[:3]])
        return out
    return {"found": False, "note": "Phiên này chưa xét tuyên bố này; dưới đây là thuộc tính và bằng chứng tìm được, "
                                    "không có kết luận. Muốn có kết luận: chạy analyze_documents với tài liệu chứa câu này.",
            "attributes": claim_attributes(claim), "evidence": find_evidence(claim, run_id, 3).get("passages", [])}


def review_assurance(text: str) -> dict:
    """ISSA 5000 / ISAE 3000 conclusion patterns (configs/issa5000_conclusion_patterns.yaml) on an assurance statement."""
    stop = _guard(text[:3000], "tờ đảm bảo")
    if stop:
        return stop
    import yaml
    cfg = yaml.safe_load((ROOT / "configs" / "issa5000_conclusion_patterns.yaml").read_text(encoding="utf-8"))
    low = re.sub(r"\s+", " ", text.lower())
    heads = [h for h in cfg.get("headings", []) if re.search(h["pattern"], low)]
    hits = []
    for p in cfg.get("patterns", []):
        m = re.search(p["pattern"], low)
        if m and not any(x in low[max(0, m.start() - 80): m.end()] for x in p.get("not_if", [])):
            hits.append({"pattern_id": p["pattern_id"], "conclusion_type": p.get("conclusion_type"),
                         "assurance_level": p.get("assurance_level"), "span": text[m.start(): m.end()][:300]})
    return {"headings": [{k: h.get(k) for k in ("id", "assurance_level", "conclusion_type")} for h in heads], "matches": hits,
            "note": None if hits else "không khớp mẫu câu kết luận đã kiểm (mẫu tiếng Anh ISSA 5000); cần người đọc"}


def domain_lookup(query: str, kind: str | None = None, k: int = 3) -> dict:
    """Background knowledge (data/domain_kb, D-2026-11-14-02): concepts, risk signals, calculations, well-formed claims,
    adjudicated cases, legal sources. Never evidence about a company and never an input to a verdict."""
    stop = _guard(query, "câu hỏi")
    if stop:
        return stop
    from quantum_gw.knowledge import domain_kb
    if not domain_kb.enabled():
        return {"stop": True, "warning": "Kho tri thức nền đang tắt (QUANTUM_DOMAIN_KB=0)."}
    return domain_kb.lookup(query, kind, min(int(k or 3), 5))


def explain_claim(claim: str, run_id: str) -> dict:
    """The rules rationale of the pipeline for a judged claim (LLM wording is the harness's job, with guards)."""
    v = verify_claim(claim, run_id)
    if v.get("stop") or not v.get("found"):
        return v
    return {"claim": v["claim"], "status": v["status"], "rationale": v["rationale"], "evidence": v["evidence"]}


def precedents(claim: str, k: int = 3) -> dict:
    """Claims a person already decided that read like `claim` (feedback-loop-v1). Beside a verdict, never a verdict."""
    stop = _guard(claim, "câu tuyên bố")
    if stop:
        return stop
    from quantum_gw.feedback.precedents import PrecedentIndex
    from quantum_gw.settings import load_settings

    index = PrecedentIndex.from_store(org_id=load_settings().feedback.org_id)
    cards = index.find({"text": claim}, k=min(int(k or 3), 5), min_similarity=0.35)
    return {"visible_labels": len(index), "precedents": [
        {key: c[key] for key in ("claim_text", "ai_status", "label", "overridden", "error_stage", "comment",
                                 "reviewer", "decided_at", "similarity")} for c in cards],
            "note": "Tiền lệ là quyết định trước đây của người soát; không phải bằng chứng và không đổi kết luận."}


def org_pack_preview(pack: str, claim: str, sector: str = "") -> dict:
    """One uploaded org pack (org_id@version, or org_id for its approved version) on one sentence, no evidence."""
    stop = _guard(claim, "câu tuyên bố")
    if stop:
        return stop
    from quantum_gw.legal.org_pack import OrgPackError, load_org_pack, preview_sentence
    from quantum_gw.legal.org_registry import resolve
    from quantum_gw.settings import load_settings

    try:
        [path] = resolve([pack])
        result = preview_sentence(load_org_pack(path), claim, sector.strip() or None, load_settings())
    except (ValueError, OrgPackError) as exc:
        return {"stop": True, "warning": str(exc)}
    return {"attributes": result["attributes"], "draft": result["draft"],
            "findings": [{k: f[k] for k in ("rule_id", "title", "outcome", "reason", "source_clauses")}
                         for f in result["findings"]],
            "note": "Quy tắc nội bộ đứng dưới luật, không phải kết luận pháp lý và không đổi kết luận kiểm chứng."}
