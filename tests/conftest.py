import atexit
import os
import shutil
import tempfile
from pathlib import Path

import pytest

# .env may switch the stance model on for real runs. The suite must stay
# hermetic and deterministic regardless -- no network, no spend -- unless a
# live check is asked for explicitly with QUANTUM_TEST_LIVE_LLM=1.
if os.environ.get("QUANTUM_TEST_LIVE_LLM") != "1":
    os.environ["QUANTUM_LLM_STANCE"] = "off"

# Everything the suite writes goes to a throw-away directory. Tests that build
# their own OrchestratorAgent, and tools run as subprocesses, used to write into
# the real .quantum/runs: by 2026-10-05 the reviewer's History page listed 697
# runs (1 GB), almost all from the test suite. Set before the settings module
# is imported, so .env (which never overrides the environment) cannot undo it.
_STORE = Path(tempfile.mkdtemp(prefix="greenscan-tests-"))
atexit.register(shutil.rmtree, _STORE, ignore_errors=True)
os.environ["QUANTUM_RUNS_DIR"] = str(_STORE / "runs")
os.environ["QUANTUM_DOCUMENTS_DIR"] = str(_STORE / "documents")
os.environ["QUANTUM_REVIEWS_FILE"] = str(_STORE / "reviews" / "decisions.jsonl")

from quantum_gw.settings import load_settings  # noqa: E402


@pytest.fixture
def settings(tmp_path: Path):
    value = load_settings("configs/default.yaml")
    value.runs_dir = str(tmp_path / "runs")
    return value
