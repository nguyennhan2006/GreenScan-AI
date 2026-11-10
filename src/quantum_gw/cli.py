from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import typer
import uvicorn

from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import DocumentInput, EvidenceChunk
from quantum_gw.evaluation.real_cases import evaluate_real_cases
from quantum_gw.evaluation.runner import evaluate_golden_set
from quantum_gw.legal.org_pack import (
    OUTCOME_VI,
    ClaimFacts,
    OrgPackError,
    describe_claim,
    describe_finding,
    describe_pack,
    evaluate_claim,
    load_org_pack,
)
from quantum_gw.settings import load_settings

app = typer.Typer(help="Evidence-first greenwashing-risk analysis agent")


@app.callback()
def _utf8_output() -> None:
    # Output sent to a file or pipe falls back to the Windows ANSI code page (cp1258),
    # which cannot encode most Vietnamese letters: every command crashed when redirected.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def _csv_values(raw: str, count: int, default: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()] if raw else [default]
    if len(values) == 1:
        return values * count
    if len(values) != count:
        raise typer.BadParameter(f"Expected one value or {count} comma-separated values")
    return values


@app.command()
def analyze(
    paths: list[Path] = typer.Argument(..., exists=True, readable=True),
    roles: str = typer.Option("claim_source", help="One role or comma-separated roles"),
    source_types: str = typer.Option("internal", help="One source type or comma-separated values"),
    config: str = typer.Option("configs/default.yaml"),
) -> None:
    role_values = _csv_values(roles, len(paths), "claim_source")
    type_values = _csv_values(source_types, len(paths), "internal")
    documents = [
        DocumentInput(path=str(path), role=DocumentRole(role_values[i]), source_type=SourceType(type_values[i]))
        for i, path in enumerate(paths)
    ]
    result = OrchestratorAgent(load_settings(config)).run(documents)
    typer.echo(json.dumps(result.summary.model_dump(mode="json"), ensure_ascii=False, indent=2))
    typer.echo(f"Evidence pack: {result.output_directory}/evidence_pack.md")


@app.command()
def demo(config: str = typer.Option("configs/default.yaml")) -> None:
    paths = [
        Path("data/sample/company_esg_2024.txt"),
        Path("data/sample/financial_2024.txt"),
        Path("data/sample/legal_notice_2024.txt"),
    ]
    documents = [
        DocumentInput(path=str(paths[0]), role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL),
        DocumentInput(path=str(paths[1]), role=DocumentRole.EVIDENCE, source_type=SourceType.FINANCIAL),
        DocumentInput(path=str(paths[2]), role=DocumentRole.EVIDENCE, source_type=SourceType.LEGAL),
    ]
    result = OrchestratorAgent(load_settings(config)).run(documents)
    typer.echo(json.dumps(result.summary.model_dump(mode="json"), ensure_ascii=False, indent=2))
    typer.echo(f"Evidence pack: {result.output_directory}/evidence_pack.md")


@app.command()
def evaluate(
    golden_set: str = typer.Option("data/golden/golden_cases.jsonl"),
    config: str = typer.Option("configs/default.yaml"),
) -> None:
    """Evaluate against the synthetic golden set."""
    metrics = evaluate_golden_set(golden_set, load_settings(config))
    typer.echo(json.dumps(metrics, ensure_ascii=False, indent=2))


@app.command()
def evaluate_real(
    pack: str = typer.Option("data/real_cases", help="Root of the adjudicated case pack"),
    config: str = typer.Option("configs/default.yaml"),
) -> None:
    """Evaluate against the adjudicated case pack (regulator and court decisions).

    Reports verification status, per-evidence stance and risk band separately:
    they fail independently and a single blended number hides which one moved.
    """
    metrics = evaluate_real_cases(load_settings(config), pack)
    typer.echo(json.dumps(metrics, ensure_ascii=False, indent=2))


@app.command()
def validate_config(config: str = typer.Option("configs/default.yaml")) -> None:
    settings = load_settings(config)
    typer.echo(json.dumps(settings.model_dump(mode="json"), ensure_ascii=False, indent=2))
    typer.echo(f"Config hash: {settings.stable_hash()}")


@app.command("org-validate")
def org_validate(
    paths: list[Path] = typer.Argument(..., help="Thư mục org pack hoặc tệp pack.yaml, một hay nhiều"),
) -> None:
    """Kiểm org pack: in OK kèm tóm tắt, hoặc toàn bộ lỗi. Pack lỗi không bao giờ được áp dụng."""
    failed = 0
    for path in paths:
        try:
            pack = load_org_pack(path)
        except OrgPackError as exc:
            failed += 1
            typer.echo(f"LỖI {exc.path}: {len(exc.problems)} lỗi, pack sẽ KHÔNG được áp dụng.")
            for problem in exc.problems:
                typer.echo(f"  - {problem}")
            continue
        typer.echo(f"OK  {pack.path}")
        for line in describe_pack(pack):
            typer.echo(f"    {line}")
    if failed:
        raise typer.Exit(code=1)


class _NoAudit:
    """`ClaimExtractionAgent.describe` writes no event; a preview keeps no run log."""

    def write(self, event: str, payload: dict | None = None) -> None:
        return None


@app.command("org-preview")
def org_preview(
    path: Path = typer.Argument(..., help="Thư mục org pack hoặc tệp pack.yaml"),
    text: str = typer.Option(..., "--text", help="Câu tuyên bố cần thử"),
    sector: str = typer.Option("", help="Ngành của doanh nghiệp, ví dụ steel; để trống = không rõ"),
    as_of: str = typer.Option("", "--as-of", help="Ngày xét hiệu lực quy tắc (YYYY-MM-DD); mặc định hôm nay"),
    config: str = typer.Option("configs/default.yaml"),
) -> None:
    """Thử pack trên một câu: bộ trích luật lấy thuộc tính, rồi chạy từng quy tắc, không có bằng chứng."""
    try:
        pack = load_org_pack(path)
    except OrgPackError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from None
    try:
        day = date.fromisoformat(as_of) if as_of else None
    except ValueError:
        raise typer.BadParameter("--as-of phải là ngày dạng YYYY-MM-DD") from None
    chunk = EvidenceChunk(chunk_id="org-preview", doc_id="org-preview", source_name="org-preview",
                          role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL, text=text)
    claim = ClaimExtractionAgent(load_settings(config).claim_extraction, _NoAudit()).describe(text, chunk)
    facts = ClaimFacts.from_claim(claim, sector.strip() or None)
    typer.echo(f"Câu: “{text}”")
    typer.echo(f"Thuộc tính (bộ trích luật): {describe_claim(facts)}")
    if pack.draft:
        typer.echo("Pack đang là bản nháp: dưới đây là xem thử như đã duyệt; khi chạy thật, pack nháp KHÔNG được áp dụng.")
    typer.echo("Xem thử không có bằng chứng: điều kiện cần bằng chứng sẽ là “chưa xác định” (?).\n")
    findings = evaluate_claim([pack], facts, [], day, preview=True)
    for finding in findings:
        typer.echo("\n".join(describe_finding(finding)) + "\n")
    tally = Counter(f.outcome for f in findings)
    typer.echo("Tóm tắt: " + " · ".join(f"{n} {OUTCOME_VI[o].lower()}" for o, n in tally.most_common()))


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1"),
    port: int = typer.Option(8000),
    reload: bool = typer.Option(False),
) -> None:
    uvicorn.run("quantum_gw.api:app", host=host, port=port, reload=reload)


@app.command("app")
def run_app(
    host: str = typer.Option("127.0.0.1"),
    port: int = typer.Option(8000),
    browser: bool = typer.Option(True, "--browser/--no-browser", help="Open the web UI when ready"),
) -> None:
    """Start GreenScan for a reviewer: API and web UI on one port, browser opened.

    The web UI is served from frontend/dist when it has been built
    (`cd frontend && npm ci && npm run build`, done once by GreenScan.bat).
    """
    import threading
    import webbrowser

    from quantum_gw.api import ui_dir

    url = f"http://{'localhost' if host in {'127.0.0.1', '0.0.0.0'} else host}:{port}/"
    if ui_dir() is None:
        typer.echo("Chưa có giao diện đã build (frontend/dist). Chạy một lần: cd frontend && npm ci && npm run build")
        url += "docs"
    typer.echo(f"GreenScan đang chạy tại {url}  — Ctrl+C để dừng.")
    if browser:
        threading.Timer(1.5, webbrowser.open, args=(url,)).start()
    uvicorn.run("quantum_gw.api:app", host=host, port=port)


if __name__ == "__main__":
    app()
