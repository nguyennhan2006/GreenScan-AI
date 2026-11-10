"""The product IR reader must be the reader AG-1 / AG-2 measured (registration agentic_ag2_product)."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import pytest

from quantum_gw.providers.base import LLMProvider, LLMResponse
from quantum_gw.verification import ir_reader
from quantum_gw.verification.ir_reader import IRReader, dual

ROOT = Path(__file__).resolve().parents[1]


def _worker_prompt() -> str:
    tree = ast.parse((ROOT / "experiments/AG-1/ag1_worker.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "PROMPT":
            return node.value.value
    raise AssertionError("PROMPT not found in ag1_worker.py")


def test_prompt_is_the_measured_one():
    assert ir_reader.PROMPT == _worker_prompt()


@pytest.mark.parametrize("copy", ["experiments/AG-1/irlib.py", "benchmark/gs_bench_v1/irlib.py"])
def test_irlib_is_the_measured_one(copy):
    digest = lambda p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()  # noqa: E731
    assert digest("src/quantum_gw/verification/irlib.py") == digest(copy)


@pytest.mark.parametrize("rules, ir, want", [
    ("S", "S", "S"), ("S", "N", "N"), ("S", "C", "N"),   # an S the rules path gives alone is dropped
    ("C", "C", "C"), ("C", "N", "C"), ("C", "S", "N"),
    ("N", "S", "S"), ("N", "C", "C"), ("N", "N", "N"),
])
def test_dual_is_union_noloneS(rules, ir, want):
    assert dual(rules, ir) == want


class _Fixed(LLMProvider):
    name = "fixed"
    model = "fixed"

    def __init__(self, reply):
        self.reply, self.seen = reply, 0

    def generate(self, messages, response_schema=None):
        self.seen += 1
        return LLMResponse(text=self.reply, provider=self.name, model=self.model)

    def healthcheck(self):
        return True

    def model_info(self):
        raise NotImplementedError


def test_reader_grounds_and_caches(tmp_path):
    reply = ('{"figures": [{"metric": "ghg_emissions", "metric_text": "phát thải", "value_text": "10.730", '
             '"multiplier_text": "nghìn", "unit_text": "tCO2e", "value_kind": "absolute", "status": "actual"}]}')
    provider = _Fixed(reply)
    sentence = "Năm 2024, phát thải của công ty là 10.730 tCO2e."
    figs = IRReader(provider, tmp_path).read(sentence)
    assert [(f.value_text, f.multiplier_text) for f in figs] == [("10.730", "")]   # ground drops the invented 'nghìn'
    again = IRReader(provider, tmp_path)
    again.read(sentence)
    again.read("Công ty cam kết bảo vệ môi trường.")   # no digit: never sent
    assert provider.seen == 1
