"""irlib.ground: a reader's figure is held to what the sentence writes (AG-1 error attribution, 31/10/2026).

Each case is a failure seen on the AG-1 Kaggle runs (experiments/AG-1/README.md section 5).
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmark" / "gs_bench_v1"))
from irlib import IR, decide, ground  # noqa: E402

WATER = "Tổng lượng nước sử dụng: 10.730 m3"


def fig(value, mult="", unit="m3", **kw):
    return {"metric": "water_use", "value_text": value, "multiplier_text": mult, "unit_text": unit, **kw}


def test_multiplier_not_written_is_dropped():
    # Qwen3-32B read "10.730 m3" as "10.730 ngàn m3": 11 wrong verdicts on B-b
    assert ground(fig("10.730", "ngàn"), WATER)["multiplier_text"] == ""


def test_multiplier_written_is_kept_or_restored():
    s = "phát thải phạm vi 1 và 2 là 23,5 triệu tCO2e"
    assert ground(fig("23,5", "triệu", "tCO2e"), s)["multiplier_text"] == "triệu"
    assert ground(fig("23,5", "", "tCO2e"), s)["multiplier_text"] == "triệu"


def test_packed_value_text_is_split():
    # Qwen3-4B wrote "23,5 triệu tCO2e" into value_text: the figure was dropped, 50 claims unread
    got = ground(fig("23,5 triệu tCO2e", "", ""), "tổng phát thải là khoảng 23,5 triệu tCO2e.")
    assert (got["value_text"], got["multiplier_text"], got["unit_text"]) == ("23,5", "triệu", "tCO2e")


def test_number_absent_from_sentence_is_dropped():
    assert ground(fig("10.800"), WATER) is None


def test_same_value_other_spelling_keeps_sentence_spelling():
    assert ground(fig("10730"), WATER)["value_text"] == "10.730"


def test_year_not_written_is_nulled():
    got = ground(fig("10.730", period=2025), WATER)
    assert got["period"] is None
    assert ground(fig("10.730", period=2025), "Năm 2025, " + WATER)["period"] == 2025


def test_word_starting_like_a_multiplier_is_not_one():
    # "tỷ lệ" (ratio) after a number is not "tỷ" (billion)
    got = ground({"metric": "waste_recycled", "value_text": "85", "unit_text": "%"}, "đạt 85 tỷ lệ tái chế")
    assert got.get("multiplier_text") in ("", None)


def test_grounded_reading_restores_verdict():
    claim = IR.from_dict(ground(fig("10.730"), "Tổng lượng nước sử dụng của Công ty là 10.730 m3."))
    evidence = IR.from_dict(ground(fig("10.730", "ngàn"), WATER))
    assert decide(claim, [evidence])[0] == "S"


BENCH = ROOT / "benchmark" / "gs_bench_v1" / "gs_bench_v1.jsonl"


@pytest.mark.skipif(not BENCH.exists(), reason="GS-Bench not built")
def test_gold_irs_survive_ground():
    """Gold IRs keep number and multiplier. Known exception: N2 claims inherit the evidence's baseline year."""
    for c in map(json.loads, BENCH.open(encoding="utf-8")):
        for side in ("claim", "evidence"):
            gold = c.get(f"{side}_ir")
            if not gold:
                continue
            gold = ast.literal_eval(gold) if isinstance(gold, str) else gold
            got = ground(gold, c[side])
            assert got is not None, (c["id"], side)
            assert (got["value_text"], got["multiplier_text"] or "") == (gold["value_text"], gold.get("multiplier_text") or ""), c["id"]


def test_count_and_absolute_compare():
    # v1.2: Qwen3-4B wrote "absolute" where the gold IR has "count" for tree counts (27 held-out claims lost)
    a = IR.from_dict({"metric": "land_trees", "value_text": "8.000", "unit_text": "cây", "value_kind": "count"})
    b = IR.from_dict({"metric": "land_trees", "value_text": "8.000", "unit_text": "cây", "value_kind": "absolute"})
    assert decide(a, [b])[0] == "S"


def test_no_contradiction_when_evidence_writes_the_claimed_number():
    # v1.2: evidence lists 10.175 and 8.000 trees, the reader extracted only 10.175 -> false C before the guard
    text = "Năm 2024 trồng 10.175 cây, trong đó 8.000 cây tại khu vực rừng đặc dụng."
    claim = IR.from_dict({"metric": "land_trees", "value_text": "8.000", "unit_text": "cây", "period": 2024})
    read = IR.from_dict({"metric": "land_trees", "value_text": "10.175", "unit_text": "cây", "period": 2024})
    assert decide(claim, [read])[0] == "C"
    assert decide(claim, [read], text)[0] == "N"


def test_guard_keeps_magnitude_and_direction_contradictions():
    claim = IR.from_dict(ground(fig("10.730", "nghìn"), "Tổng lượng nước sử dụng của Công ty là 10.730 nghìn m3."))
    evidence = IR.from_dict(ground(fig("10.730"), WATER))
    assert decide(claim, [evidence], WATER)[0] == "C"
    up = IR.from_dict({"metric": "water_use", "value_text": "14", "unit_text": "%", "value_kind": "change", "change_direction": "increase"})
    down = IR.from_dict({"metric": "water_use", "value_text": "14", "unit_text": "%", "value_kind": "change", "change_direction": "decrease"})
    assert decide(up, [down], "lượng nước giảm 14%")[0] == "C"
