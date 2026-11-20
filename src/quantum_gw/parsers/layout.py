"""Page regions (page-regions-v1, 17/11/2026): what is on a page, where, and in which order to read it.

The Claude spot check of 17/11 (docs/04-data-ai/KIEM_CHUNG_BANG_CLAUDE_2026-11-17.md) found that the text
was read correctly and then interpreted wrongly: blocks sorted by height interleave two columns, a table's
rows never become figures, "7,085" under a "(Nghìn tấn)" heading is read as seven tonnes. This module
returns the page as typed regions before anything is interpreted:

    text     lines of prose, in column order (a band of full-width lines, then each column top to bottom)
    table    a ruled table (PyMuPDF `find_tables`) or an unruled grid of right-aligned figures, as rows of
             cells with the caption, the column headers, the unit and the period printed around it

It works on words, so the same code reads a page's text layer and a scanned page through the boxes
Tesseract gives for each word (parsers/ocr.py). Nothing here asks a model anything.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from quantum_gw.utils.text import normalize_text

# ------------------------------------------------------------------ words and lines


@dataclass
class Line:
    x0: float
    y0: float
    x1: float
    y1: float
    words: list[tuple[float, float, str]]  # (x0, x1, text)

    @property
    def text(self) -> str:
        return " ".join(w[2] for w in self.words)

    @property
    def height(self) -> float:
        return max(1.0, self.y1 - self.y0)


def lines_from_words(words: list[tuple]) -> list[Line]:
    """OCR words (x0, y0, x1, y1, text, line_key) to lines.

    Tesseract's line is a whole row of the page (it reads a scan as one block), which is right for a table
    row and wrong across two columns of prose, so a line is split again where the gap between two words
    is wider than a character's height.
    """
    by_key: dict[str, list[tuple]] = {}
    for w in words:
        if not any(ch.isalnum() for ch in w[4]):
            continue  # a table rule read as "|" or "—": it is a border, and it makes a row look tall
        by_key.setdefault(w[5] if len(w) > 5 else f"{round((w[1] + w[3]) / 20)}", []).append(w)
    lines: list[Line] = []
    for group in by_key.values():
        group.sort(key=lambda w: w[0])
        h = sorted(w[3] - w[1] for w in group)[len(group) // 2] or 1.0
        current: Line | None = None
        for x0, y0, x1, y1, text, *_ in group:
            if current is not None and x0 - current.x1 <= 1.2 * h:
                current.words.append((x0, x1, text))
                current.x1, current.y0, current.y1 = max(current.x1, x1), min(current.y0, y0), max(current.y1, y1)
            else:
                current = Line(x0, y0, x1, y1, [(x0, x1, text)])
                lines.append(current)
    return sorted(lines, key=lambda ln: (ln.y0, ln.x0))


def lines_from_page(page, hidden_boxes=()) -> list[Line]:
    """Units of a text-layer page: a paragraph block as one unit, a row of cells split into its cells.

    A PDF block of several lines is a paragraph and stays one unit, so its lines cannot be taken for the
    labels of a table beside it. A one-line block, or a block whose every line ends in a figure standing
    apart ("Chất thải nguy hại        247"), is split where the gap is wider than a character: those are
    cells, and splitting them is what lets an unruled table be seen. Words inside `hidden_boxes`
    (integrity.visible_blocks) are dropped: text no reader can see stays out of the layout.
    """
    blocks: dict[int, dict[int, list[tuple]]] = {}
    for w in page.get_text("words"):
        cx, cy = (w[0] + w[2]) / 2, (w[1] + w[3]) / 2
        if any(b[0] <= cx <= b[2] and b[1] <= cy <= b[3] for b in hidden_boxes):
            continue
        blocks.setdefault(w[5], {}).setdefault(w[6], []).append((w[0], w[1], w[2], w[3], w[4], f"{w[5]}-{w[6]}"))
    units: list[Line] = []
    for lines in blocks.values():
        cells = {n: lines_from_words(ws) for n, ws in lines.items()}
        row_like = all(len(c) >= 2 and all(is_number(t) for _, _, t in max(c, key=lambda ln: ln.x0).words)
                       for c in cells.values())
        flat = [w for ws in lines.values() for w in ws]
        mids = [(w[1] + w[3]) / 2 for w in flat]
        one_visual_line = max(mids) - min(mids) <= 0.5 * min(w[3] - w[1] for w in flat)
        if one_visual_line and len(lines) > 1:
            # Several PDF lines on one baseline (a label, then its figure written separately): one row.
            units.extend(lines_from_words([(*w[:5], 'row') for w in flat]))
            continue
        if len(lines) == 1 or row_like:
            for c in cells.values():
                units.extend(c)
            continue
        # The PDF's own line and word order: a paragraph set in two sizes ("Tự chủ" small, "90%" large)
        # reads as written, not by the top edge of each word.
        words = [w for n in sorted(lines) for w in lines[n]]
        x0, y0 = min(w[0] for w in words), min(w[1] for w in words)
        x1, y1 = max(w[2] for w in words), max(w[3] for w in words)
        units.append(Line(x0, y0, x1, y1, [(w[0], w[2], w[4]) for w in words]))
    return sorted(units, key=lambda ln: (ln.y0, ln.x0))


def lines_from_blocks(blocks) -> list[Line]:
    """Text-layer blocks (x0, y0, x1, y1, text, ...) as units: a PDF block is already one paragraph or one cell.

    Take them from `integrity.visible_blocks`, so text no reader can see stays out of the layout too.
    """
    out = []
    for b in blocks:
        text = " ".join(normalize_text(b[4]).split())
        if not text:
            continue
        tokens = text.split()
        step = (b[2] - b[0]) / max(1, len(tokens))
        out.append(Line(b[0], b[1], b[2], b[3], [(b[0] + i * step, b[0] + (i + 1) * step, t) for i, t in enumerate(tokens)]))
    return out


def ocr_words(reading) -> list[tuple[float, float, float, float, str]]:
    return [(*w["bbox"], w["text"], w.get("line", "")) for w in reading.words]


# ------------------------------------------------------------------ numbers

_NUM_TOKEN = re.compile(r"^[(\-–]?\d[\d.,]*%?\)?$")
_UNIT_HEAD = re.compile(r"\(([^()]{1,24})\)\s*$|đơn vị\s*(?:tính)?\s*[:：]\s*([^\n,;]{1,24})", re.IGNORECASE)
# Unaccented forms too: an OCR reading or a heading typed without diacritics ("(Nghin tan)").
_MULTIPLIER = {"nghìn": 1e3, "ngàn": 1e3, "nghin": 1e3, "ngan": 1e3, "thousand": 1e3, "triệu": 1e6, "trieu": 1e6,
               "million": 1e6, "tỷ": 1e9, "tỉ": 1e9, "ty": 1e9, "billion": 1e9}
_YEAR = re.compile(r"(?<!\d)(20[0-4]\d)(?!\d)")


def is_number(token: str) -> bool:
    return bool(_NUM_TOKEN.match(token.strip())) and not _YEAR.fullmatch(token.strip("()%"))


def separators(tokens: list[str]) -> str:
    """'vi' when a dot groups thousands (22.540.603, 38,52), 'en' when a comma does (7,085 · 6,982).

    Decided once per table: a lone "7,085" is ambiguous, a column of "7,085 / 6,982 / 103" under
    "(Nghìn tấn)" is not.
    """
    dot_groups = sum(1 for t in tokens if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", t))
    comma_groups = sum(1 for t in tokens if re.fullmatch(r"\d{1,3}(?:,\d{3})+", t))
    comma_decimal = sum(1 for t in tokens if re.fullmatch(r"\d+,\d{1,2}|\d+,\d{4,}", t))
    dot_decimal = sum(1 for t in tokens if re.fullmatch(r"\d+\.\d{1,2}|\d+\.\d{4,}", t))
    if dot_groups or comma_decimal:
        return "vi"
    if comma_groups and not comma_decimal or dot_decimal:
        return "en"
    return "vi"


def parse_number(token: str, style: str) -> tuple[float, bool] | None:
    """(value, is_percent) of one cell, or None. Parentheses are a negative number, as in accounts."""
    raw = token.strip()
    negative = raw.startswith(("(", "-", "–")) and any(c.isdigit() for c in raw)
    raw = raw.strip("()-–")
    percent = raw.endswith("%")
    raw = raw.rstrip("%")
    if not re.fullmatch(r"\d[\d.,]*", raw):
        return None
    if style == "vi":
        raw = raw.replace(".", "").replace(",", ".")
    else:
        raw = raw.replace(",", "")
    try:
        value = float(raw)
    except ValueError:
        return None
    return (-value if negative else value), percent


def unit_of(text: str) -> tuple[str | None, float]:
    """The unit printed in a heading, and the multiplier word in it: "(Nghìn tấn)" -> ("tấn", 1000)."""
    match = _UNIT_HEAD.search(normalize_text(text))
    if not match:
        return None, 1.0
    unit = (match.group(1) or match.group(2) or "").strip()
    low = unit.lower()
    factor = 1.0
    for word, value in _MULTIPLIER.items():
        if low.startswith(word + " "):
            factor, unit = value, unit[len(word) + 1:].strip()
            break
    if unit.lower() in {"vnd", "vnđ", "đồng", "đ"}:
        unit = "VND"
    elif unit.isupper() and unit.lower() not in {"tco2e", "co2e", "kwh", "mwh", "gwh", "gj", "tj"}:
        unit = unit.lower()  # a heading set in capitals: "(NGHÌN TẤN)" is tonnes
    if not unit or len(unit.split()) > 3 or any(ch.isdigit() for ch in unit if unit.lower() not in {"tco2e", "m3", "co2e"}):
        return None, 1.0
    return unit, factor


def period_of(text: str) -> str | None:
    years = _YEAR.findall(text or "")
    return years[-1] if years else None


# ------------------------------------------------------------------ regions


@dataclass
class Cell:
    text: str
    header: str = ""          # column header above it
    value: float | None = None
    percent: bool = False
    unit: str | None = None
    period: str | None = None


@dataclass
class Row:
    label: str
    cells: list[Cell] = field(default_factory=list)


@dataclass
class Table:
    bbox: tuple[float, float, float, float]
    caption: str = ""
    headers: list[str] = field(default_factory=list)
    rows: list[Row] = field(default_factory=list)
    unit: str | None = None
    factor: float = 1.0
    period: str | None = None
    style: str = "vi"
    kind: str = "ruled"      # ruled | grid

    def render(self) -> str:
        """The table as lines a reader and the retriever can use: one row per line, each value with its column."""
        head = [f"BẢNG: {self.caption}" if self.caption else "BẢNG"]
        meta = ", ".join(x for x in [f"đơn vị {_unit_text(self.unit, self.factor)}" if self.unit else "",
                                     f"kỳ {self.period}" if self.period else ""] if x)
        if meta:
            head.append(f"({meta})")
        lines = [" ".join(head)]
        for row in self.rows:
            parts = [f"{c.header}: {c.text}" if c.header else c.text for c in row.cells if c.text]
            lines.append(f"{row.label} | " + " | ".join(parts) if row.label else " | ".join(parts))
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {"kind": self.kind, "caption": self.caption, "headers": self.headers, "unit": self.unit,
                "factor": self.factor, "period": self.period, "style": self.style,
                "bbox": [round(v, 1) for v in self.bbox],
                "rows": [{"label": r.label, "cells": [c.__dict__ for c in r.cells]} for r in self.rows]}


def _unit_text(unit: str | None, factor: float) -> str:
    word = {1e3: "nghìn ", 1e6: "triệu ", 1e9: "tỷ "}.get(factor, "")
    return f"{word}{unit}" if unit else ""


@dataclass
class PageLayout:
    text: str
    tables: list[Table]
    columns: int


def _inside(line: Line, box, pad: float = 2.0) -> bool:
    cx, cy = (line.x0 + line.x1) / 2, (line.y0 + line.y1) / 2
    return box[0] - pad <= cx <= box[2] + pad and box[1] - pad <= cy <= box[3] + pad


def _context_above(lines: list[Line], box, reach: float) -> list[Line]:
    """Lines just above a table, over its width: where the caption, unit and date are printed."""
    return [ln for ln in lines if box[1] - reach <= ln.y1 <= box[1] + 1 and ln.x1 > box[0] - 4 and ln.x0 < box[2] + 4]


_QUANTITY = re.compile(
    r"(?<![\w.,])(?P<num>\d[\d.,]*%?)\s*"
    r"(?P<unit>(?:(?:nghìn|ngàn|triệu|tỷ)\s+)?[^\W\d_](?:[^\W\d_]|[ /]|(?<=[A-Za-z])\d)*)?",
    re.IGNORECASE,
)
# Dates are not quantities: "24-tháng 12-2024", "31/12/2024", "tháng 10/2025".
_DATE = re.compile(r"\d{1,2}\s*[-/.]\s*(?:tháng\s*)?\d{1,2}\s*[-/.]\s*\d{2,4}|tháng\s*\d{1,2}(?:\s*[-/]\s*\d{4})?", re.IGNORECASE)


def _cell_quantities(text: str) -> list[tuple[str, str]]:
    """Numbers inside a text cell, each with the words after it: "⊲ 97.378 xe ô tô điện ⊲ 63.000 xe máy điện"."""
    out = []
    for m in _QUANTITY.finditer(_DATE.sub(" ", text)):
        token = m.group("num").rstrip(".,")
        if _YEAR.fullmatch(token) or not is_number(token):
            continue
        unit = " ".join((m.group("unit") or "").split()[:4]).strip(" ,.")
        out.append((token, unit))
    return out


def _unit_words(words: str) -> tuple[str | None, float]:
    """"tỷ VND" -> ("VND", 1e9); "tấn CO2td" -> ("tấn CO2td", 1)."""
    if not words:
        return None, 1.0
    return unit_of(f"({words})")


def _finish(table: Table, around: str) -> Table:
    """Unit, factor, period and number style of a table, then the value of every cell.

    A unit printed in a column header belongs to that column only: "Số dư (tỷ VND)" does not make
    "Số lượng khoản vay" a sum of money. The table-wide unit comes from the caption or the line above.
    """
    for text in (table.caption, around):
        unit, factor = unit_of(text)
        if unit:
            table.unit, table.factor = unit, factor
            break
    texts = [table.caption, *table.headers, around]
    table.period = next((p for p in (period_of(t) for t in texts) if p), None)
    header_units = any(unit_of(h)[0] for h in table.headers)
    tokens = [c.text for r in table.rows for c in r.cells]
    table.style = separators([q for t in tokens for q, _ in _cell_quantities(t)] or tokens)
    for row in table.rows:
        cells: list[Cell] = []
        for cell in row.cells:
            if not is_number(cell.text):
                # Figures inside a short text cell ("306.356 tấn CO2td", "⊲ 97.378 xe ô tô điện"). A long cell
                # is a sentence of method or explanation, and its small numbers are not disclosures.
                found = [] if len(cell.text) > 140 else [
                    (t, u) for t, u in _cell_quantities(cell.text)
                    if t.endswith("%") or len(re.sub(r"\D", "", t)) >= 3]
                if not found:
                    cells.append(cell)
                    continue
                for token, words in found:
                    parsed = parse_number(token, table.style)
                    if parsed is None:
                        continue
                    unit, factor = _unit_words(words)
                    sub = Cell(text=f"{token} {words}".strip(), header=cell.header, period=period_of(cell.header) or table.period)
                    sub.value, sub.percent = parsed[0] * factor, parsed[1]
                    sub.unit = "%" if parsed[1] else (unit or words or None)
                    cells.append(sub)
                continue
            parsed = parse_number(cell.text, table.style)
            if parsed is None:
                cells.append(cell)
                continue
            cell.value, cell.percent = parsed
            head_unit, head_factor = unit_of(cell.header)
            if cell.percent:
                cell.unit = "%"
            elif head_unit:
                cell.unit, cell.value = head_unit, cell.value * head_factor
            elif table.unit and not (header_units and cell.header):
                cell.unit, cell.value = table.unit, cell.value * table.factor
            cell.period = period_of(cell.header) or table.period
            cells.append(cell)
        row.cells = cells
    return table


def _ruled_tables(page, lines: list[Line]) -> list[Table]:
    from .documents import is_data_table

    out: list[Table] = []
    try:
        found = page.find_tables().tables
    except Exception:
        return out
    for found_table in found:
        grid = [[" ".join(normalize_text(c or "").split()) for c in row] for row in found_table.extract()]
        if not is_data_table(grid):
            continue
        box = tuple(found_table.bbox)
        table = Table(bbox=box, kind="ruled")
        width = max(len(r) for r in grid)
        rows = [r + [""] * (width - len(r)) for r in grid]
        # A first row with a single filled cell is the table's title.
        if rows and sum(1 for c in rows[0] if c) == 1:
            table.caption = next(c for c in rows[0] if c)
            rows = rows[1:]
        header_index = next((i for i, r in enumerate(rows) if sum(1 for c in r if c) >= 2), None)
        if header_index is not None and not any(is_number(c) for c in rows[header_index] if c):
            table.headers = rows[header_index]
            rows = rows[header_index + 1:]
        elif rows and not table.headers and sum(1 for c in rows[0][1:] if c and not is_number(c)) >= 1 \
                and any(is_number(c) for r in rows[1:] for c in r):
            # A header row that also carries the caption in its first cell (Techcombank's summary table).
            table.caption = table.caption or rows[0][0]
            table.headers = [""] + rows[0][1:]
            rows = rows[1:]
        for r in rows:
            label_parts = [c for c in r if c and not is_number(c)]
            label = " ".join(label_parts[:1]) if label_parts else ""
            row = Row(label=label)
            for index, text in enumerate(r):
                if text and text != label:
                    header = table.headers[index] if index < len(table.headers) else ""
                    row.cells.append(Cell(text=text, header=header))
            if row.label or row.cells:
                table.rows.append(row)
        around = " ".join(ln.text for ln in _context_above(lines, box, 3.5 * _line_height(lines)))
        out.append(_finish(table, around))
    return out


def _line_height(lines: list[Line]) -> float:
    heights = sorted(ln.height for ln in lines if len(ln.words) <= 12) or sorted(ln.height for ln in lines)
    return heights[len(heights) // 2] if heights else 10.0


def _grid_tables(lines: list[Line], taken: list[tuple], page_width: float) -> list[Table]:
    """Unruled tables: rows whose label is on the left and whose figures end at the same x on the right.

    Hòa Phát prints its waste table (page 50) as free text: a label at x=1341 and "7,085" at x=2053-2103
    on the same baseline, under "CHỈ TIÊU NĂM 2025 (Nghìn tấn)". Two or more such rows, right edges
    aligned within a character, are a table.
    """
    lh = _line_height(lines)
    free = [ln for ln in lines if not any(_inside(ln, box) for box in taken)]
    numeric = [ln for ln in free if all(is_number(w[2]) for w in ln.words) and len(ln.words) <= 4]
    rows: list[tuple[list[Line], Line]] = []
    for value_line in numeric:
        mid = (value_line.y0 + value_line.y1) / 2
        labels = [ln for ln in free if ln is not value_line and ln.x1 < value_line.x0 - 1.5 * lh
                  and abs((ln.y0 + ln.y1) / 2 - mid) <= 0.6 * max(lh, value_line.height)
                  and not all(is_number(w[2]) for w in ln.words)]
        # Only the cells next to the figure: walk left while the gap stays the width of a table column.
        # A paragraph of the neighbouring column (a tall block) or the page's sidebar is not a cell.
        labels = [ln for ln in labels if ln.height <= 2.6 * lh]
        chosen: list[Line] = []
        edge = value_line.x0
        for ln in sorted(labels, key=lambda ln: -ln.x1):
            if edge - ln.x1 > (max(12 * lh, 0.8 * page_width) if not chosen else max(5 * lh, 0.12 * page_width)):
                break
            chosen.append(ln)
            edge = ln.x0
        if chosen:
            rows.append((sorted(chosen, key=lambda ln: ln.x0), value_line))
    rows.sort(key=lambda r: r[1].y0)
    # Several numeric lines on one row (count, then amount) are one row with several cells.
    merged: list[tuple[list[Line], list[Line]]] = []
    for labels, value in rows:
        if merged and abs(merged[-1][1][0].y0 - value.y0) <= 0.5 * lh:
            merged[-1][1].append(value)
        else:
            merged.append((labels, [value]))
    groups: list[list[tuple[list[Line], list[Line]]]] = []
    for labels, values in merged:
        right = max(v.x1 for v in values)
        last = groups[-1][-1] if groups else None
        if last and abs(max(v.x1 for v in last[1]) - right) <= 1.2 * lh                 and min(v.y0 for v in values) - max(v.y1 for v in last[1]) <= 4.5 * lh:
            groups[-1].append((labels, values))
        else:
            groups.append([(labels, values)])
    out: list[Table] = []
    for group in groups:
        if len(group) < 2:
            continue
        members = [ln for labels, values in group for ln in (*labels, *values)]
        box = (min(ln.x0 for ln in members), min(ln.y0 for ln in members),
               max(ln.x1 for ln in members), max(ln.y1 for ln in members))
        above = sorted((ln for ln in _context_above(free, box, 4 * lh) if ln not in members), key=lambda ln: ln.y0)
        header = " ".join(ln.text for ln in above)
        table = Table(bbox=box, kind="grid", caption=header, headers=[header] if header else [])
        # Columns of figures are right-aligned: cluster the cells by right edge, then give every cell of a
        # column the same header, the lowest heading line over the column's whole span.
        spans: list[list[float]] = []
        for _labels, values in group:
            for value in values:
                for x0, x1, _text in value.words:
                    span = next((sp for sp in spans if abs(sp[1] - x1) <= 1.2 * lh), None)
                    if span is None:
                        spans.append([x0, x1])
                    else:
                        span[0] = min(span[0], x0)
        for labels, values in group:
            row = Row(label=" ".join(ln.text for ln in labels))
            for value in sorted(values, key=lambda v: v.x0):
                for x0, x1, text in value.words:
                    span = next((sp for sp in spans if abs(sp[1] - x1) <= 1.2 * lh), [x0, x1])
                    row.cells.append(Cell(text=text, header=_column_header(above, span, lh)))
            table.rows.append(row)
        out.append(_finish(table, header))
    return out


def _column_header(above: list[Line], span, lh: float) -> str:
    """The text printed above a column of figures: the lowest heading line that overlaps its span."""
    lo, hi = span
    over = [ln for ln in above if ln.x0 - lh <= hi and lo <= ln.x1 + lh]
    return over[-1].text if over else ""


def _columns(lines: list[Line], width: float) -> list[tuple[float, float]]:
    """Column spans from the gaps that no narrow line crosses (a full-width heading crosses all of them)."""
    narrow = [ln for ln in lines if ln.x1 - ln.x0 < 0.55 * width]
    if len(narrow) < 6:
        return [(0.0, width)]
    step = max(1.0, width / 400)
    cover = [0] * (int(width / step) + 2)
    for ln in narrow:
        for i in range(int(ln.x0 / step), int(ln.x1 / step) + 1):
            cover[i] += 1
    occupied = [i for i, c in enumerate(cover) if c]
    if not occupied:
        return [(0.0, width)]
    lo, hi = occupied[0], occupied[-1]
    min_gap = max(3, int(0.012 * width / step))
    spans, start, run = [], lo, 0
    for i in range(lo, hi + 1):
        if cover[i] == 0:
            run += 1
            continue
        if run >= min_gap:
            spans.append((start * step, (i - run) * step))
            start = i
        run = 0
    spans.append((start * step, (hi + 1) * step))
    # A column needs real text in it; a gutter next to a page number is not a column.
    keep = [s for s in spans if sum(1 for ln in narrow if s[0] - 1 <= ln.x0 and ln.x1 <= s[1] + 1) >= 3]
    return keep or [(0.0, width)]


def reading_order(lines: list[Line], width: float) -> tuple[list[Line], int]:
    """Bands split by full-width lines; inside a band, each column top to bottom, left to right."""
    columns = _columns(lines, width)
    if len(columns) == 1:
        return sorted(lines, key=lambda ln: (round(ln.y0, 1), ln.x0)), 1

    def column_of(ln: Line) -> int | None:
        for index, (a, b) in enumerate(columns):
            if a - 2 <= ln.x0 and ln.x1 <= b + 2:
                return index
        return None

    ordered: list[Line] = []
    band: list[Line] = []
    for ln in sorted(lines, key=lambda ln: (ln.y0, ln.x0)):
        if column_of(ln) is None:  # spans a gutter: a heading or a full-width paragraph
            ordered.extend(sorted(band, key=lambda x: (column_of(x), x.y0, x.x0)))
            band = []
            ordered.append(ln)
        else:
            band.append(ln)
    ordered.extend(sorted(band, key=lambda x: (column_of(x), x.y0, x.x0)))
    return ordered, len(columns)


def _paragraphs(lines: list[Line]) -> str:
    """Lines joined into paragraphs; a blank line where the vertical gap or the column changes."""
    out: list[str] = []
    prev: Line | None = None
    lh = _line_height(lines)
    for ln in lines:
        if prev is not None:
            gap = ln.y0 - prev.y1
            new_par = gap > 0.9 * lh or gap < -lh or abs(ln.x0 - prev.x0) > 6 * lh
            out.append("\n\n" if new_par else "\n")
        out.append(ln.text)
        prev = ln
    return normalize_text("".join(out))


def analyze(lines: list[Line], width: float, page=None) -> PageLayout:
    """Typed regions of one page. `page` (PyMuPDF) adds ruled-table detection; OCR lines alone still get grids.

    `lines` come from `lines_from_blocks` (text layer) or `lines_from_words(ocr_words(reading))` (scan).
    """
    tables = _ruled_tables(page, lines) if page is not None else []
    tables += _grid_tables(lines, [t.bbox for t in tables], width)
    boxes = [t.bbox for t in tables]
    prose = [ln for ln in lines if not any(_inside(ln, box) for box in boxes)]
    ordered, columns = reading_order(prose, width)
    return PageLayout(text=_paragraphs(ordered), tables=tables, columns=columns)
