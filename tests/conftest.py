from pathlib import Path

import pytest

from quantum_gw.settings import load_settings


@pytest.fixture
def settings(tmp_path: Path):
    value = load_settings("configs/default.yaml")
    value.runs_dir = str(tmp_path / "runs")
    return value
