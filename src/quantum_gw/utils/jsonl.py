"""JSONL read/write that survives Unicode line separators.

`str.splitlines()` breaks on U+2028 (LINE SEPARATOR), U+2029 (PARAGRAPH
SEPARATOR) and U+0085 (NEL) in addition to `\\n`. All three are legal inside a
JSON string and all three occur in text extracted from Vietnamese PDFs, so a
reader built on `splitlines()` loses one record per occurrence — silently, in
the common case.

Both halves of the fix live here because they must agree:

* the writer escapes those code points, so every physical line is one record;
* the reader splits on `\\n` only, so it stays correct even for files written
  by something else.

The escape table is built from code points rather than literal characters. A
literal U+2028 in source can be normalised to a space by an editor, and a
literal ``\\u2028`` can be un-escaped into the character it denotes; either
turns the table into a silent no-op. That is not hypothetical — it happened to
four separate copies of this logic before it was consolidated here.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

_BS = chr(0x5C)
JSONL_ESCAPES = {
    chr(0x2028): _BS + "u2028",
    chr(0x2029): _BS + "u2029",
    chr(0x85): _BS + "u0085",
}
_TABLE = str.maketrans(JSONL_ESCAPES)


def dumps(record: Any) -> str:
    """One JSONL line: UTF-8 readable, with separators escaped."""
    return json.dumps(record, ensure_ascii=False).translate(_TABLE)


def write_jsonl(path: str | Path, records: Iterable[Any]) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(dumps(record) + "\n")
            count += 1
    return count


def append_jsonl(path: str | Path, record: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(dumps(record) + "\n")


def read_jsonl(path: str | Path) -> list[Any]:
    """Parse a JSONL file. Splits on `\\n` only -- never `splitlines()`."""
    path = Path(path)
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").split("\n")
        if line.strip()
    ]
