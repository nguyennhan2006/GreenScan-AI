"""Kho tri thức nền (domain KB): claim chuẩn, bằng chứng cần có, dấu hiệu, cách tính, khái niệm, vụ việc, văn bản pháp lý.

Mục đích: để trợ lý giải thích lĩnh vực có trích nguồn thay vì trả lời từ trí nhớ của LLM.

Ranh giới (D-2026-11-14-02, kiểm bằng tests/test_architecture_invariants.py):
  - kho KHÔNG phải bằng chứng của doanh nghiệp và không đi vào bước kiểm chứng; mọi kết quả mang
    source_type = "tri_thuc_nen" và một câu nhắc điều đó;
  - chỉ công cụ domain_lookup (mcp_tools / mcp_server / agent_harness) được import module này;
  - "cách tính" trỏ vào hàm thật trong code (trường `code`); ví dụ số (trường `check`) được kiểm thử tính lại.

Nguồn dữ liệu, mỗi loại một chỗ:
  data/domain_kb/entries_v1.yaml            khái niệm, dấu hiệu, cách tính, claim chuẩn (viết tay)
  data/real_cases/cases/*/case.json         vụ việc đã có phán quyết / dàn xếp  -> CASE-<case_id>
  configs/legal/LEGAL_SOURCE_REGISTRY.yaml  văn bản pháp lý                      -> LEGAL-<id>

Tra cứu: từ khoá có trọng số theo trường + idf, cộng điểm khi cả cụm từ khoá xuất hiện trong câu hỏi; chạy
ngoại tuyến, không cần mô hình. `python -m quantum_gw.knowledge.domain_kb validate | search "<câu hỏi>"`.
"""
from __future__ import annotations

import ast
import importlib
import json
import math
import operator
import os
import re
import sys
import unicodedata
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
KB_FILE = ROOT / "data" / "domain_kb" / "entries_v1.yaml"
CASES_DIR = ROOT / "data" / "real_cases" / "cases"
LEGAL_REGISTRY = ROOT / "configs" / "legal" / "LEGAL_SOURCE_REGISTRY.yaml"

SOURCE_TYPE = "tri_thuc_nen"
NOTE = ("Tri thức nền của GreenScan (khái niệm, cách tính, vụ việc, văn bản), không phải bằng chứng trong tài liệu "
        "của doanh nghiệp và không dùng để ra kết luận.")
KINDS = ("concept", "signal", "formula", "pattern", "case", "legal")
KIND_VI = {"concept": "khái niệm", "signal": "dấu hiệu", "formula": "cách tính", "pattern": "tuyên bố chuẩn",
           "case": "vụ việc", "legal": "văn bản pháp lý"}
REQUIRED = ("id", "kind", "title", "summary", "sources", "labeler", "review_status")
WEIGHTS = {"id": 3.0, "keywords": 3.0, "codes": 3.0, "title": 2.5, "summary": 1.0, "claim_good": 0.5, "claim_weak": 0.5}
MIN_SCORE = 2.5
STOP = set("la gi cua va cho the nao co khong trong mot cac nhung duoc voi tu den theo hay thi ve nhu nay do de "
           "ban toi hoi giup minh xin vay sao lam can phai biet ro "
           "how what is are the a an of to and in for does do why".split())
CASE_STATUS_VI = {
    "SEC_SETTLEMENT_WITHOUT_ADMISSION_OR_DENIAL": "Ủy ban Chứng khoán Hoa Kỳ dàn xếp; doanh nghiệp không thừa nhận cũng "
                                                  "không phủ nhận",
    "DUTCH_COURT_FOUND_15_OF_19_STATEMENTS_MISLEADING": "Toà Amsterdam kết luận 15/19 câu quảng cáo gây hiểu lầm",
}


def enabled() -> bool:
    return os.environ.get("QUANTUM_DOMAIN_KB", "1").strip().lower() not in ("0", "false", "off", "no")


def norm(text: str) -> str:
    t = unicodedata.normalize("NFD", str(text or "").lower().replace("đ", "d"))
    return re.sub(r"\s+", " ", "".join(c for c in t if unicodedata.category(c) != "Mn")).strip()


def accented(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(text or "").lower())).strip()


def has_accents(text: str) -> bool:
    """A query typed with Vietnamese accents is matched with accents: folding merges 'đấu' (match) and 'dấu' (sign)."""
    return norm(text) != accented(text)


def tokens(text: str, fold: bool = True) -> list[str]:
    return [t for t in re.findall(r"[^\W_]+", norm(text) if fold else accented(text)) if norm(t) not in STOP]


# --------------------------------------------------------------------------- loading
def _hand_written() -> list[dict]:
    raw = yaml.safe_load(KB_FILE.read_text(encoding="utf-8")) or {}
    defaults = raw.get("defaults") or {}
    return [{**defaults, **e} for e in raw.get("entries") or []]


def _cases() -> list[dict]:
    out = []
    for p in sorted(CASES_DIR.glob("*/case.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        if not c.get("adjudication_date"):   # VN control documents are not cases against anyone
            continue
        status = CASE_STATUS_VI.get(c.get("case_status", ""), c.get("case_status", ""))
        out.append({
            "id": f"CASE-{c['case_id']}", "kind": "case",
            "title": f"{c['organization']} ({c['adjudication_date'][:4]}): {c.get('case_type', '')}",
            "summary": f"{status}. {c.get('evidence_summary', '')}",
            "claim_weak": c.get("claim_text"),
            "method": " ".join(c.get("expected_reasoning") or []),
            "caution": c.get("legal_caution"),
            "keywords": [c["organization"], c.get("sector", ""), c.get("case_type", ""), c["case_id"], c.get("jurisdiction", "")],
            "sources": [f"[NGOÀI] {s}" for s in c.get("source_ids") or []] + [f"data/real_cases/cases/{p.parent.name}"],
            "labeler": "đội GreenScan (data/real_cases)",
            "review_status": c.get("training_eligibility", "unknown"),
        })
    return out


def _legal() -> list[dict]:
    raw = yaml.safe_load(LEGAL_REGISTRY.read_text(encoding="utf-8")) or {}
    out = []
    for d in raw.get("documents") or []:
        num = d.get("document_number", "")
        short = re.match(r"(\d+/\d{4})", num)
        dtype = {"nghi_dinh": "nghị định", "quyet_dinh": "quyết định", "thong_tu": "thông tư", "luat": "luật"}.get(
            d.get("doc_type", ""), d.get("doc_type", ""))
        valid = f"hiệu lực từ {d.get('effective_from')}" + (f" đến {d['effective_to']}" if d.get("effective_to") else "")
        ocr = " Chữ của văn bản được nhận dạng từ bản quét; kiểm lại bản gốc trước khi trích điều khoản." if d.get("ocr_used") else ""
        out.append({
            "id": f"LEGAL-{d['id']}", "kind": "legal",
            "title": f"{num}: {' '.join(str(d.get('title', '')).split())}",
            "summary": (f"{d.get('authority', '')}, ban hành {d.get('issued_date')}, {valid}; tình trạng {d.get('status')}. "
                        f"Vấn đề: {', '.join(d.get('legal_issues') or [])}.{ocr} Mục này chỉ cho biết văn bản là gì; việc "
                        "áp dụng cho một tuyên bố do lớp pháp lý quyết định theo ngày hiệu lực."),
            "keywords": [num, d["id"], *(d.get("legal_issues") or [])] + ([f"{dtype} {short.group(1)}", short.group(1)] if short else []),
            "sources": [f"[NGOÀI] {d.get('original_url') or d.get('landing_url') or num}", "configs/legal/LEGAL_SOURCE_REGISTRY.yaml"],
            "labeler": "đội GreenScan (sổ đăng ký pháp lý)",
            "review_status": d.get("text_acquisition", "unknown"),
        })
    return out


@lru_cache(maxsize=1)
def entries() -> tuple[dict, ...]:
    return tuple(_hand_written() + _cases() + _legal())


@lru_cache(maxsize=2)
def _index(fold: bool) -> tuple[list[dict], dict[str, float], list[list[str]]]:
    rows, phrases = [], []
    df: dict[str, int] = {}
    key = norm if fold else accented
    for e in entries():
        tf: dict[str, float] = {}
        for field, w in WEIGHTS.items():
            v = e.get(field)
            text = " ".join(map(str, v)) if isinstance(v, list) else str(v or "")
            if field == "id":
                text = text.replace("-", " ")
            for t in tokens(text, fold):
                tf[t] = max(tf.get(t, 0.0), w)
        rows.append(tf)
        for t in tf:
            df[t] = df.get(t, 0) + 1
        phrases.append([key(x) for x in (e.get("keywords") or []) + (e.get("codes") or []) if len(key(x)) >= 3])
    n = len(rows)
    idf = {t: math.log(1 + n / c) for t, c in df.items()}
    return rows, idf, phrases


def get(entry_id: str) -> dict | None:
    want = (entry_id or "").strip().upper()
    return next((e for e in entries() if e["id"].upper() == want), None)


def search(query: str, k: int = 3, kind: str | None = None) -> list[tuple[float, dict]]:
    exact = get(query)
    if exact is not None:
        return [(100.0, exact)]
    fold = not has_accents(query)
    rows, idf, phrases = _index(fold)
    q, qn = set(tokens(query, fold)), f" {norm(query) if fold else accented(query)} "
    scored = []
    for e, tf, ph in zip(entries(), rows, phrases):
        if kind and e["kind"] != kind:
            continue
        hit = [t for t in q if t in tf]
        s = sum(tf[t] * idf[t] for t in hit)
        ph_hit = [p for p in ph if re.search(rf"(?<![^\W_]){re.escape(p)}(?![^\W_])", qn)]
        s += sum(4.0 * len(p.split()) for p in ph_hit)
        # One shared word is not a match ("tuần" in "lịch thi đấu tuần sau" vs "tuần hoàn nước"): need a keyword
        # phrase, two query words, or half of a short query.
        covered = ph_hit or len(hit) >= 2 or (q and len(hit) / len(q) >= 0.5)
        if covered and s >= MIN_SCORE:
            scored.append((round(s, 2), e))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    return scored[: max(1, min(k, 5))]


BRIEF_FIELDS = ("id", "kind", "title", "summary", "claim_good", "claim_weak", "attributes", "evidence", "signals", "method",
                "code", "system", "codes", "caution", "related", "sources", "labeler", "review_status")


def brief(e: dict) -> dict:
    out = {f: e[f] for f in BRIEF_FIELDS if e.get(f)}
    out["kind_vi"] = KIND_VI.get(e["kind"], e["kind"])
    out["summary"] = str(out.get("summary", ""))[:900]
    if e.get("check"):
        out["examples"] = [c.get("note") or f"{c['expr']} = {c['expect']}" for c in e["check"]]
    return out


def lookup(query: str, kind: str | None = None, k: int = 3) -> dict:
    hits = search(query, k, kind if kind in KINDS else None)
    return {"source_type": SOURCE_TYPE, "note": NOTE, "query": query, "found": len(hits),
            "entries": [{**brief(e), "score": s} for s, e in hits]}


# --------------------------------------------------------------------------- validation
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}


def arith(expr: str) -> float:
    """Evaluate a numeric example: numbers, + - * / **, parentheses and abs(); nothing else."""
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.operand))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "abs" and len(n.args) == 1:
            return abs(ev(n.args[0]))
        raise ValueError(f"biểu thức không được phép: {ast.dump(n)[:80]}")
    return float(ev(ast.parse(expr, mode="eval")))


def _resolves(ref: str) -> bool:
    mod, _, attr = ref.partition(":")
    try:
        return hasattr(importlib.import_module(mod), attr)
    except ImportError:
        return False


def validate() -> list[str]:
    problems, seen = [], set()
    ids = {e.get("id") for e in entries()}
    for e in entries():
        eid = e.get("id", "?")
        if eid in seen:
            problems.append(f"{eid}: trùng id")
        seen.add(eid)
        problems += [f"{eid}: thiếu {f}" for f in REQUIRED if not e.get(f)]
        if e.get("kind") not in KINDS:
            problems.append(f"{eid}: loại mục lạ {e.get('kind')}")
        for f in ("related", "signals"):
            problems += [f"{eid}: {f} trỏ tới mục không có {r}" for r in e.get(f) or [] if r not in ids]
        problems += [f"{eid}: hàm không tồn tại {r}" for r in e.get("code") or [] if not _resolves(r)]
        for c in e.get("check") or []:
            try:
                got = arith(c["expr"])
            except (ValueError, SyntaxError, ZeroDivisionError) as exc:
                problems.append(f"{eid}: ví dụ không tính được {c['expr']}: {exc}")
                continue
            if abs(got - float(c["expect"])) > float(c.get("tol", 1e-9)):
                problems.append(f"{eid}: ví dụ sai {c['expr']} = {got:g}, ghi {c['expect']}")
    return problems


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if argv[:1] == ["validate"]:
        p = validate()
        kinds = {k: sum(e["kind"] == k for e in entries()) for k in KINDS}
        print(f"{len(entries())} mục {kinds}; {len(p)} lỗi")
        print("\n".join(p))
        return 1 if p else 0
    if argv[:1] == ["search"] and len(argv) > 1:
        for s, e in search(" ".join(argv[1:]), k=5):
            print(f"{s:6.2f}  {e['id']:28s} {e['title']}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
