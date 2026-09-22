"""The JSONL escape logic, which broke twice before it was consolidated.

Failure 1: a literal U+2028 written into source was normalised to a space, so
the table mapped space->escape and the separator passed through untouched.
Failure 2: a literal ``\\u2028`` in source was un-escaped into the character it
denotes, so the table mapped the separator to itself — a no-op.

Both were silent. Neither raised; records simply went missing on read. Hence a
test that asserts the *table contents* as well as round-trip behaviour.
"""

import json

import pytest

from quantum_gw.utils.jsonl import (
    JSONL_ESCAPES,
    append_jsonl,
    dumps,
    read_jsonl,
    write_jsonl,
)

SEPARATORS = [chr(0x2028), chr(0x2029), chr(0x85)]


def test_table_keys_are_the_separator_characters():
    """Guards failure 1: keys must not have been normalised to spaces."""
    assert set(JSONL_ESCAPES) == set(SEPARATORS)
    assert " " not in JSONL_ESCAPES


def test_table_values_are_escape_sequences_not_characters():
    """Guards failure 2: values must be six-character text, not the char itself."""
    for key, value in JSONL_ESCAPES.items():
        assert len(value) == 6, f"{value!r} should be a backslash-u sequence"
        assert value[0] == chr(0x5C)
        assert value != key


@pytest.mark.parametrize("sep", SEPARATORS)
def test_separator_never_survives_into_a_line(sep):
    line = dumps({"text": f"a{sep}b"})
    assert sep not in line
    assert len(line.splitlines()) == 1


@pytest.mark.parametrize("sep", SEPARATORS)
def test_round_trip_is_lossless(sep, tmp_path):
    records = [{"text": f"phát thải{sep}giảm 30%"}, {"text": "bình thường"}]
    p = tmp_path / "t.jsonl"
    assert write_jsonl(p, records) == 2
    assert read_jsonl(p) == records


def test_both_reader_styles_agree(tmp_path):
    """The whole point: a naive splitlines() reader must not lose a record."""
    records = [{"i": i, "text": f"x{chr(0x2028)}y"} for i in range(5)]
    p = tmp_path / "t.jsonl"
    write_jsonl(p, records)
    raw = p.read_text(encoding="utf-8")
    assert len(raw.splitlines()) == raw.count("\n") == len(records)
    assert [json.loads(x) for x in raw.splitlines() if x.strip()] == records


def test_vietnamese_is_not_escaped_away(tmp_path):
    p = tmp_path / "t.jsonl"
    write_jsonl(p, [{"text": "Phát thải khí nhà kính giảm 30%"}])
    assert "Phát thải" in p.read_text(encoding="utf-8"), "ensure_ascii must stay False"


def test_append_matches_write(tmp_path):
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    records = [{"n": 1}, {"n": 2}]
    write_jsonl(a, records)
    for r in records:
        append_jsonl(b, r)
    assert a.read_text(encoding="utf-8") == b.read_text(encoding="utf-8")


def test_missing_file_reads_as_empty(tmp_path):
    assert read_jsonl(tmp_path / "nope.jsonl") == []


def test_blank_lines_are_skipped(tmp_path):
    p = tmp_path / "t.jsonl"
    p.write_text('{"a": 1}\n\n   \n{"a": 2}\n', encoding="utf-8")
    assert read_jsonl(p) == [{"a": 1}, {"a": 2}]


def test_write_creates_parent_directories(tmp_path):
    p = tmp_path / "deep" / "nested" / "t.jsonl"
    write_jsonl(p, [{"a": 1}])
    assert p.is_file()
