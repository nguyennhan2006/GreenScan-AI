from __future__ import annotations

import json
from pathlib import Path

import typer
import uvicorn

from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.domain.models import DocumentInput
from quantum_gw.evaluation.real_cases import evaluate_real_cases
from quantum_gw.evaluation.runner import evaluate_golden_set
from quantum_gw.settings import load_settings

app = typer.Typer(help="Evidence-first greenwashing-risk analysis agent")


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
