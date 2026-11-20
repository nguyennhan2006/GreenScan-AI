"""next-step-v1 and portable-v1 (D-2026-11-17-01): the guided first run, and a bundle that carries no secret."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from quantum_gw.intake import SAMPLE_SETS, sample_sets

ROOT = Path(__file__).resolve().parents[1]
FRONT = ROOT / "frontend" / "src"


def _portable():
    spec = importlib.util.spec_from_file_location("build_portable", ROOT / "tools" / "build_portable.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_portable"] = module
    spec.loader.exec_module(module)
    return module


def test_the_small_sample_set_is_offered_first_and_its_files_exist():
    first = SAMPLE_SETS[0]
    assert first["id"] == "minhhoa" and len(first["files"]) == 3
    assert [f["role"] for f in first["files"]] == ["claim_source", "evidence", "evidence"]
    assert all((ROOT / f["path"]).is_file() for f in first["files"])
    offered = {s["id"]: s for s in sample_sets(ROOT)}
    assert "minhhoa" in offered and offered["minhhoa"]["title"] and offered["minhhoa"]["note"]


def test_every_step_of_the_workflow_says_what_to_do_next():
    for page in ("NewAnalysisPage.jsx", "QueuePage.jsx", "ClaimDetailPage.jsx", "ExportPage.jsx"):
        text = (FRONT / "pages" / page).read_text(encoding="utf-8")
        assert "<NextStep" in text, page
    settings = (FRONT / "pages" / "SettingsPage.jsx").read_text(encoding="utf-8")
    assert "setTipsHidden" in settings        # a reviewer who hides the line can bring it back


def test_the_queue_counts_only_what_can_be_decided():
    queue = (FRONT / "pages" / "QueuePage.jsx").read_text(encoding="utf-8")
    assert "queuedClaims" in queue and "item_type === 'claim'" in queue
    app = (FRONT / "App.jsx").read_text(encoding="utf-8")
    assert "i.item_type === 'claim' && reviewStates[i.item_id] !== 'FINALIZED'" in app


def test_portable_launchers_are_plain_ascii_and_name_no_key():
    portable = _portable()
    for text in (portable.LAUNCHER, portable.MODEL_SETUP):
        assert text.isascii()
        assert "API_KEY" not in text and "TOKEN" not in text
    assert portable.OLLAMA_MODEL in portable.MODEL_SETUP.replace("__MODEL__", portable.OLLAMA_MODEL)
    assert not any(portable.SECRET_NAME.search(key) for key in portable.ENV_KEYS)
    assert portable.SECRET_NAME.search("GROQ_API_KEY") and not portable.SECRET_NAME.search("LOCAL_LLM_MAX_TOKENS")


def test_portable_env_never_copies_a_secret(tmp_path, monkeypatch):
    portable = _portable()
    (tmp_path / ".env").write_text(
        "QUANTUM_PROFILE=offline\nGROQ_API_KEY=gsk_secret_value\nFPT_LLM_API_KEY=another_secret\nGROQ_MODEL=some/model\n", encoding="utf-8")
    monkeypatch.setattr(portable, "ROOT", tmp_path)
    out = tmp_path / "bundle"
    (out / "app").mkdir(parents=True)
    portable.app_env(out)
    written = (out / "app" / ".env").read_text(encoding="utf-8")
    assert "gsk_secret_value" not in written and "another_secret" not in written
    assert "GROQ_API_KEY=\n" in written and "GROQ_MODEL=some/model" in written and "QUANTUM_PROFILE=offline" in written
