"""`.env` must actually reach the process.

README and .env.example both instruct the operator to configure the model
gateway through `.env`, but nothing read that file — only docker-compose's
`env_file` did. A pasted API key was therefore ignored with no error, which is
the worst possible failure mode for a credential.
"""

import os

import pytest

from quantum_gw.settings import load_dotenv


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "# comment line\n"
        "\n"
        "FPT_LLM_API_KEY=secret-from-file\n"
        'FPT_LLM_MODEL="Qwen/Qwen3-32B"\n'
        "FPT_LLM_BASE_URL='https://mkp-api.fptcloud.com/v1'\n"
        "MALFORMED_NO_EQUALS\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in ("FPT_LLM_API_KEY", "FPT_LLM_MODEL", "FPT_LLM_BASE_URL", "MALFORMED_NO_EQUALS"):
        monkeypatch.delenv(key, raising=False)


def test_values_are_loaded(env_file):
    loaded = load_dotenv(env_file)
    assert loaded == 3
    assert os.environ["FPT_LLM_API_KEY"] == "secret-from-file"


def test_quotes_are_stripped(env_file):
    load_dotenv(env_file)
    assert os.environ["FPT_LLM_MODEL"] == "Qwen/Qwen3-32B"
    assert os.environ["FPT_LLM_BASE_URL"] == "https://mkp-api.fptcloud.com/v1"


def test_comments_blanks_and_malformed_lines_are_skipped(env_file):
    load_dotenv(env_file)
    assert "MALFORMED_NO_EQUALS" not in os.environ


def test_real_environment_wins_by_default(env_file, monkeypatch):
    """`FPT_LLM_API_KEY=... quantum-agent serve` must beat the file."""
    monkeypatch.setenv("FPT_LLM_API_KEY", "from-shell")
    load_dotenv(env_file)
    assert os.environ["FPT_LLM_API_KEY"] == "from-shell"


def test_override_is_opt_in(env_file, monkeypatch):
    monkeypatch.setenv("FPT_LLM_API_KEY", "from-shell")
    load_dotenv(env_file, override=True)
    assert os.environ["FPT_LLM_API_KEY"] == "secret-from-file"


def test_missing_file_is_not_an_error(tmp_path):
    assert load_dotenv(tmp_path / "does-not-exist.env") == 0


def test_u2028_in_a_value_does_not_split_the_line(tmp_path):
    """splitlines() would treat U+2028 as a newline and corrupt the next key."""
    p = tmp_path / ".env"
    p.write_text("A=one two\nB=second\n", encoding="utf-8")
    load_dotenv(p)
    assert os.environ["A"] == "one two"
    assert os.environ["B"] == "second"
