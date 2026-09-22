"""CLI smoke tests — catch "the function vanished but the module still imports".

A regex cleanup once deleted `attribute_state` from `tools/benchmark.py`.
`ast.parse` reported syntax OK, every import resolved, and all 116 unit tests
passed — because none of them entered `cmd_sample`. Only running the command
surfaced it.

So these are deliberately shallow: invoke each subcommand as a subprocess,
assert the exit code and one minimal artifact. They are not output tests. Their
whole job is to prove the command paths execute.

Anything needing network is excluded; those tools are covered by `--dry-run`
paths only where that is offline.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / ".quantum/runs"


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Invoke a tool and capture its output as UTF-8.

    `text=True` alone decodes with the *parent's* locale, which is cp1258 on this
    machine, so Vietnamese output raises UnicodeDecodeError inside subprocess's
    reader thread and stdout comes back as None. The child is already told to
    emit UTF-8; the parent has to be told to read it that way.
    """
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, *args], cwd=str(cwd or REPO), env=env,
        capture_output=True, encoding="utf-8", errors="replace", timeout=600,
    )


def latest_run_dir() -> Path | None:
    if not RUNS.is_dir():
        return None
    candidates = [d for d in RUNS.iterdir() if (d / "result.json").is_file()]
    return max(candidates, key=lambda d: d.stat().st_mtime) if candidates else None


# ---------------------------------------------------------------- --help

@pytest.mark.parametrize("tool", [
    "tools/benchmark.py", "tools/eda_corpus.py", "tools/dataset_audit_v2.py",
    "tools/crawl_legal_cases.py", "tools/legal_vertical_slice.py",
    "tools/verify_regressions.py", "tools/check_llm_providers.py",
    "tools/repair_legal_case_lineage.py", "tools/crawl_legal_sources.py",
])
def test_help_executes(tool):
    """--help imports the module and builds the parser: cheapest real execution."""
    r = run(tool, "--help")
    assert r.returncode == 0, f"{tool} --help failed:\n{r.stderr[-600:]}"
    assert "usage" in r.stdout.lower()


# ---------------------------------------------------------------- benchmark

@pytest.mark.skipif(latest_run_dir() is None, reason="no pipeline run available")
def test_benchmark_sample_then_score(tmp_path):
    labels = tmp_path / "labels.jsonl"
    r = run("tools/benchmark.py", "sample", "--run-dir", str(latest_run_dir()),
            "--n", "5", "--out", str(labels))
    assert r.returncode == 0, r.stderr[-800:]
    assert labels.is_file()

    rows = [json.loads(x) for x in labels.read_text(encoding="utf-8").split("\n") if x.strip()]
    assert rows, "sample wrote an empty template"
    assert "human_is_real_claim" in rows[0], "template is missing the human_* fields"

    # Unlabelled input must refuse, not fabricate metrics.
    r = run("tools/benchmark.py", "score", "--labels", str(labels))
    assert r.returncode == 1
    assert "0 labelled" in r.stdout


# ---------------------------------------------------------------- eda

@pytest.mark.skipif(
    not (REPO / "data/crawl/vn30/normalized/claim_candidates.jsonl").is_file(),
    reason="VN corpus not present",
)
def test_eda_report_only():
    r = run("tools/eda_corpus.py", "--report-only")
    assert r.returncode == 0, r.stderr[-800:]
    assert "boilerplate" in r.stdout


# ---------------------------------------------------------------- audit

@pytest.mark.skipif(not (REPO / "data/legal_cases/documents.jsonl").is_file(),
                    reason="legal_cases corpus not present")
def test_dataset_audit_subcommands():
    for sub, needle in [("lineage", "invariants hold"),
                        ("maturity", "L0 RAW"),
                        ("split", "COMPANY-HELD-OUT")]:
        r = run("tools/dataset_audit_v2.py", sub)
        assert r.returncode in (0, 1), f"{sub} crashed:\n{r.stderr[-600:]}"
        assert needle in r.stdout, f"{sub} produced unexpected output"


def test_repair_lineage_dry_run_changes_nothing():
    docs = REPO / "data/legal_cases/documents.jsonl"
    if not docs.is_file():
        pytest.skip("legal_cases corpus not present")
    before = docs.read_bytes()
    r = run("tools/repair_legal_case_lineage.py", "--dry-run")
    assert r.returncode == 0, r.stderr[-600:]
    assert docs.read_bytes() == before, "--dry-run must not write"


# ---------------------------------------------------------------- legal

def test_legal_vertical_slice_both_modes():
    r = run("tools/legal_vertical_slice.py", "--mode", "current_policy_alignment")
    assert r.returncode == 0, r.stderr[-800:]
    assert "legal_finding" in r.stdout

    r = run("tools/legal_vertical_slice.py", "--mode", "historical_compliance",
            "--published", "2023-05-01")
    assert r.returncode == 0, r.stderr[-800:]
    assert '"as_of_date": "2023-05-01"' in r.stdout, "historical mode ignored the claim date"


def test_verify_regressions_reports_all_seven():
    r = run("tools/verify_regressions.py")
    assert r.returncode == 0, f"a regression is failing:\n{r.stdout[-900:]}"
    assert "7/7 regressions holding" in r.stdout


def test_provider_check_runs_without_keys():
    """Must not crash when every cloud key is empty — the default state."""
    r = run("tools/check_llm_providers.py")
    assert r.returncode == 0, r.stderr[-600:]
    assert "provider" in r.stdout.lower()
