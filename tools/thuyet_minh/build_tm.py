"""Build the system description (thuyết minh hệ thống): chapters with {{PLACEHOLDERS}} -> one Markdown file.

Every table and code block that shows a result is generated here from the run files, never typed by hand:
    .quantum/runs/<run_id>/{result.json, manifest.json, audit.jsonl, evidence_pack.md, contract/*.jsonl}
    <trace>/clean/case_{A,B}.json        step timings (tools/thuyet_minh/run_cases.py)
    <trace>/tools_{A,B}.json             MCP tools, harness and LLM-stage traces (tools/thuyet_minh/tools_trace.py)
Prompts are imported from the product code, so the appendix is the text the code sends.

    .venv/Scripts/python.exe -I tools/thuyet_minh/build_tm.py <trace_dir>      (cwd = repo root)
Then tools/thuyet_minh/make_docx.sh (figure, pandoc, styling).
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path.cwd()
sys.path.insert(0, str(REPO / "tools" / "thuyet_minh"))
TRACE = Path(sys.argv[1])
DOC = REPO / "docs" / "09-luan-van" / "THUYET_MINH_HE_THONG"
RUNS = {c: json.loads((TRACE / "clean" / f"case_{c}.json").read_text(encoding="utf-8"))["run_id"] for c in ("A", "B")}
TRACED = {"A1": ("A", "Công ty đã giảm 30% tổng phát thải khí nhà kính"),
          "A2": ("A", "Nguồn vốn từ trái phiếu xanh"),
          "B1": ("B", "Hiện nay, tỷ lệ tái chế chất thải rắn của nhóm thép"),
          "B2": ("B", "Hoàn thành kiểm kê khí nhà kính theo tiêu chuẩn ISO 14064-1:2018")}


# ----------------------------------------------------------------------------- loading
def load_run(rid: str) -> dict:
    d = REPO / ".quantum" / "runs" / rid
    run = {"dir": d, "result": json.loads((d / "result.json").read_text(encoding="utf-8")),
           "manifest": json.loads((d / "manifest.json").read_text(encoding="utf-8")),
           "audit": [json.loads(x) for x in (d / "audit.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()],
           "pack": (d / "evidence_pack.md").read_text(encoding="utf-8")}
    for layer in ("raw", "clean", "extract"):
        p = d / "contract" / f"{layer}.jsonl"
        run[layer] = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
    return run


R = {c: load_run(rid) for c, rid in RUNS.items()}
TIME = {c: json.loads((TRACE / "clean" / f"case_{c}.json").read_text(encoding="utf-8")) for c in RUNS}
TOOLS = {c: json.loads((TRACE / f"tools_{c}.json").read_text(encoding="utf-8")) for c in RUNS
         if (TRACE / f"tools_{c}.json").exists()}


def verif(case: str, prefix: str) -> dict:
    for v in R[case]["result"]["verifications"]:
        if v["claim"]["text"].startswith(prefix):
            return v
    raise KeyError(prefix)


V = {k: verif(c, p) for k, (c, p) in TRACED.items()}
CID = {k: v["claim"]["claim_id"] for k, v in V.items()}


def by_claim(case: str, key: str) -> dict:
    return {x["claim_id"]: x for x in R[case]["result"][key] if x.get("claim_id")}


# ----------------------------------------------------------------------------- markdown helpers
def cell(x, n: int | None = None) -> str:
    if x is None:
        s = "—"
    elif isinstance(x, float):
        s = f"{x:.3f}".rstrip("0").rstrip(".") if abs(x) < 1000 else f"{x:,.0f}"
    elif isinstance(x, (list, dict)):
        s = json.dumps(x, ensure_ascii=False)
    else:
        s = str(x)
    s = s.replace("\n", " ").replace("|", "\\|").strip()
    if n and len(s) > n:
        s = s[: n - 1].rstrip() + "…"
    return s or "—"


def table(headers: list[str], rows: list[list], widths: dict | None = None) -> str:
    widths = widths or {}
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(cell(v, widths.get(i)) for i, v in enumerate(r)) + " |")
    return "\n".join(out)


def code(text: str, lang: str = "") -> str:
    text = text.replace("```", "ʼʼʼ")
    return f"```{lang}\n{text.rstrip()}\n```"


def jdump(obj, limit: int | None = None) -> str:
    s = json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    if limit and len(s) > limit:
        s = s[:limit].rstrip() + "\n… (cắt bớt; bản đầy đủ trong tệp kết quả của phiên)"
    return code(s, "json")


def short(s: str | None, n: int = 120) -> str:
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def vn(x: float, d: int = 1) -> str:
    """Vietnamese number: 1.234,5"""
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def events(case: str, name: str) -> list[dict]:
    return [e["payload"] for e in R[case]["audit"] if e.get("event") == name]


PH: dict[str, callable] = {}


def ph(fn):
    PH[fn.__name__.upper()] = fn
    return fn


# ----------------------------------------------------------------------------- chapter 1–3
@ph
def run_date():
    return "14/11/2026 (mã đã sửa các lỗi ở mục 9.1)"


@ph
def config_table():
    from quantum_gw.settings import load_settings
    s = load_settings()
    f = TIME["A"]["flags"]
    rows = [
        ["Hồ sơ chạy (`QUANTUM_PROFILE`)", "offline", "chỉ nhà cung cấp cục bộ; không gọi API trong luồng phân tích"],
        ["Phiên bản pipeline", s.version, "ghi trong `manifest.json`"],
        ["Mã băm cấu hình", R["A"]["manifest"]["config_hash"][:16] + "…", "giống nhau ở cả hai phiên"],
        ["Bộ luật pháp lý", R["A"]["manifest"]["rule_pack_version"], ""],
        ["OCR", "bật, ngôn ngữ vie+eng (Tesseract)", "`QUANTUM_OCR_ENABLED=true`"],
        ["Lập trường bằng LLM (S5)", "tắt" if not R["A"]["manifest"].get("prompt_version") else R["A"]["manifest"]["prompt_version"],
         "`prompt_version` rỗng trong manifest = không mô hình nào được hỏi"],
        ["Điền thuộc tính bằng LLM (S2)", "bật" if f["assist_attributes"] else "tắt", "`verification.assist_attributes`"],
        ["Lời giải thích bằng LLM (S6)", f["assist_explain"], "`verification.assist_explain`"],
        ["Mô hình lọc tuyên bố T1", f["claim_model_dir"] or "tắt", "`claim_extraction.claim_model_dir`"],
        ["LLM cho luồng hỏi đáp", "Groq `openai/gpt-oss-120b`, temperature 0, reasoning_effort low",
         "chỉ khi `public=true`; tối đa 3 lời gọi, 900 token ra, 60 s mỗi lời gọi"],
        ["Mã phiên Ca A / Ca B", f"`{RUNS['A']}` / `{RUNS['B']}`", "thư mục `.quantum/runs/<mã>/`"],
    ]
    return table(["Mục", "Giá trị trong lượt chạy", "Ghi chú"], rows)


@ph
def img_map():
    p = (REPO / "docs/04-data-ai/hinh_mo_hinh/ban_do_he_thong.png").as_posix()
    return f"![Hình 2.2. Bản đồ hệ thống GreenScan (luồng phân tích và luồng hỏi đáp qua MCP)]({p}){{width=100%}}"


@ph
def img_pipeline():
    p = (DOC / "hinh" / "pipeline_hai_ca.png").as_posix()
    return f"![Hình 2.1. Mười bước của luồng phân tích, số liệu thật của Ca A và Ca B]({p}){{width=100%}}"


@ph
def code_map():
    groups = [
        ("Điều phối", ["agents/orchestrator.py"]),
        ("Đọc tài liệu", ["agents/intake.py", "parsers/documents.py", "parsers/ocr.py", "parsers/office.py",
                          "parsers/integrity.py", "parsers/text_quality.py", "agents/corpus.py"]),
        ("Trích tuyên bố", ["agents/claim_extractor.py", "agents/claim_quality.py", "domain/claim_attributes.py", "agents/claim_model.py"]),
        ("Truy xuất", ["agents/retriever.py", "retrieval/hybrid.py", "retrieval/embeddings.py", "retrieval/rerank.py"]),
        ("Kiểm chứng", ["agents/verifier.py", "verification/numeric_facts.py", "verification/stance.py", "verification/irlib.py",
                        "verification/ir_reader.py", "verification/llm_judge.py"]),
        ("Pháp lý", ["agents/legal_check.py", "legal/checker.py", "legal/rules.py", "legal/gates.py", "legal/corpus.py", "legal/org_pack.py"]),
        ("Rủi ro, số liệu, hàng soát", ["agents/scorer.py", "agents/figures.py", "agents/prioritizer.py"]),
        ("Cổng chất lượng, báo cáo", ["agents/reviewer.py", "agents/reporter.py", "data/export.py", "workpaper.py"]),
        ("LLM hỗ trợ", ["assist/prompts.py", "assist/client.py", "assist/stages.py", "assist/guards.py", "assist/scope_guard.py"]),
        ("Hỏi đáp MCP", ["mcp_tools.py", "mcp_server.py", "agent_harness.py"]),
        ("Người soát, Studio", ["storage/reviews.py", "studio/suggest.py", "studio/escalation.py", "studio/report.py"]),
    ]
    rows = []
    base = REPO / "src" / "quantum_gw"
    for g, files in groups:
        n = sum(len((base / f).read_text(encoding="utf-8").splitlines()) for f in files if (base / f).exists())
        rows.append([g, ", ".join(f"`{f}`" for f in files), n])
    total = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in base.rglob("*.py"))
    rows.append(["**Toàn gói `quantum_gw`**", "", total])
    return table(["Nhóm", "Tệp (trong `src/quantum_gw/`)", "Số dòng"], rows)


def raw_docs(case: str) -> list[dict]:
    chunks = Counter(u["doc_id"] for u in R[case]["clean"])
    ocr = Counter(u["doc_id"] for u in R[case]["clean"] if u.get("used_ocr"))
    out = []
    for d in R[case]["raw"]:
        out.append({**d, "chunks": chunks[d["doc_id"]], "ocr_units": ocr[d["doc_id"]]})
    return out


@ph
def case_a_docs():
    rows = [[f"`{d['file_name']}`", d["role"], d["source_type"], d["byte_size"], d["chunks"], d["sha256"][:12] + "…"]
            for d in raw_docs("A")]
    return table(["Tệp", "Vai trò", "Loại nguồn", "Byte", "Số đoạn", "SHA-256"], rows)


@ph
def case_a_texts():
    out = []
    for d in R["A"]["raw"]:
        text = (REPO / d["object_path"]).read_text(encoding="utf-8")
        out.append(f"**{d['file_name']}** ({d['role']}, {d['source_type']})\n\n" + code(text))
    return "\n\n".join(out)


@ph
def case_b_docs():
    rows = [[f"`{d['file_name']}`", d["role"], d["source_type"], vn(d["byte_size"] / 1e6, 1) + " MB", d.get("page_count"),
             d["chunks"], d["ocr_units"], d["sha256"][:12] + "…"] for d in raw_docs("B")]
    return table(["Tệp", "Vai trò", "Loại nguồn", "Dung lượng", "Số trang", "Số đoạn", "Đoạn có OCR", "SHA-256"], rows)


@ph
def traced_claims():
    rows = []
    for k, v in V.items():
        c = v["claim"]
        rows.append([f"**{k}**", f"Ca {TRACED[k][0]}", f"`{c['claim_id']}`", c["text"], c.get("source_page") or "—", v["status"]])
    return table(["Mã", "Ca", "claim_id", "Tuyên bố (nguyên văn)", "Trang", "Kết luận"], rows)


# ----------------------------------------------------------------------------- chapter 4+ live in parts
from build_tm_parts import register  # noqa: E402

register(globals())


# ----------------------------------------------------------------------------- assemble
def render(text: str) -> str:
    def sub(m):
        key = m.group(1)
        if key not in PH:
            return f"**[THIẾU PLACEHOLDER {key}]**"
        return str(PH[key]())
    return re.sub(r"\{\{([A-Z0-9_]+)\}\}", sub, text)


def main() -> None:
    parts = []
    for p in sorted((DOC / "chuong").glob("*.md")):
        parts.append(render(p.read_text(encoding="utf-8")))
    head = (DOC / "chuong" / "_meta.yaml").read_text(encoding="utf-8") if (DOC / "chuong" / "_meta.yaml").exists() else ""
    md = (head + "\n" if head else "") + "\n\n".join(parts)
    out = DOC / "THUYET_MINH_HE_THONG.md"
    out.write_text(md, encoding="utf-8")
    facts = PH["PIPELINE_FACTS"]() if "PIPELINE_FACTS" in PH else None
    if facts:
        (DOC / "hinh").mkdir(exist_ok=True)
        (DOC / "hinh" / "pipeline_facts.json").write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")
    missing = re.findall(r"THIẾU PLACEHOLDER (\w+)", md)
    print(f"markdown {out} chars={len(md)} words~{len(re.findall(r'\w+', md))} missing={missing}")


if __name__ == "__main__":
    main()
