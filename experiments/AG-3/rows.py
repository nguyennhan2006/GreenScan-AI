"""AG-3 v0: rebuild table rows of a PDF page from word coordinates, and cross-foot the rows labelled Cộng / Tổng.

PyMuPDF get_text() emits a table's row labels and its numbers as separate runs (HPG SR 2025 p.39: "Phạm vi 1 |
Phạm vi 2 | Cộng | … | 22.540.603 | 933.876 | 23.474.480"), so a reader pairs a label with the wrong number. Here
every word is placed on a row by its vertical centre; a row that holds a label and at least one number becomes one
"row sentence" in reading order ("Phạm vi 1 22.540.603"). A total row is checked against the rows above it in the
same column: |sum - total| <= half a unit of every figure summed (published precision).

    .venv/Scripts/python.exe -I experiments/AG-3/rows.py PDF PAGE [PAGE ...]      (pages 1-based)
"""
from __future__ import annotations

import re, sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "benchmark" / "gs_bench_v1"))
from irlib import parse_number  # noqa: E402

NUM = re.compile(r"^\(?-?[\d.,]+%?\)?$")
TOTAL = re.compile(r"^(cộng|tổng|total)", re.I)


def rows(page: pymupdf.Page, tol: float = 0.45, cells_only: bool = False) -> list[list[tuple]]:
    """Words grouped into rows: same row when vertical centres differ by < tol x word height.

    cells_only keeps the words of short one-line text blocks: PyMuPDF puts each table cell in its own block,
    while prose of a neighbouring page column is a block of many lines that would glue onto the table rows.
    """
    words = page.get_text("words")
    if cells_only:
        lines, count = {}, {}
        for w in words:
            lines.setdefault(w[5], set()).add(w[6])
            count[w[5]] = count.get(w[5], 0) + 1
        words = [w for w in words if len(lines[w[5]]) <= 2 and count[w[5]] <= 10]
    words = sorted(words, key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    out: list[list[tuple]] = []
    for w in words:
        cy, h = (w[1] + w[3]) / 2, w[3] - w[1]
        if out and abs(cy - out[-1][0][8]) < tol * h:
            out[-1].append((*w, cy))
        else:
            out.append([(*w, cy)])
    return [sorted(r, key=lambda w: w[0]) for r in out]


def segments(row: list[tuple], gap: float = 2.5) -> list[list[tuple]]:
    """Split a row where the horizontal gap exceeds gap x word height: two-column pages hold two rows per line."""
    segs, cur = [], [row[0]]
    for a, b in zip(row, row[1:]):
        if b[0] - a[2] > gap * (a[3] - a[1]):
            segs.append(cur); cur = []
        cur.append(b)
    segs.append(cur)
    return segs


def table_rows(page: pymupdf.Page) -> list[dict]:
    """Row sentences: a label followed by numbers, each number with its x centre (its column)."""
    out = []
    for row in rows(page, cells_only=True):
        # A wide gap separates either two page columns (prose | table) or a table label from its numbers.
        # A segment of numbers only belongs to the label segment before it; a long label is prose, not a table row.
        groups: list[list[tuple]] = []
        for seg in segments(row):
            if any(not NUM.match(w[4]) for w in seg) or not groups:
                groups.append(list(seg))
            else:
                groups[-1].extend(seg)
        for g in groups:
            # a small integer right after the label ("Phạm vi 1") is part of the label, not a value
            words = [w[4] for w in g]
            k = next((i for i, t in enumerate(words) if NUM.match(t)), len(words))
            if 0 < k < len(words) - 1 and re.fullmatch(r"\d", words[k]):
                k += 1
            label = " ".join(t for t in words[:k] if True).strip() + " " + " ".join(t for t in words[k:] if not NUM.match(t))
            label = label.strip()
            nums = [(w[4], (w[0] + w[2]) / 2) for w in g[k:] if NUM.match(w[4]) and re.search(r"\d", w[4])]
            if label and nums and re.search(r"[^\W\d_]", label) and len(label.split()) <= 8:
                out.append({"label": label, "numbers": nums, "y": round(g[0][8])})
    # header rows (only years as numbers) give the year and the unit of the rows below them
    context, unit = "", ""
    for r in out:
        values = [n for n, _ in r["numbers"]]
        if all(is_year(v) for v in values):
            m = re.search(r"\(([^)]+)\)", r["label"])
            context, unit = f"Năm {values[0].strip('.,')}", (m.group(1) if m else unit)
            r["header"] = True
            continue
        shown = "; ".join(v if v.endswith("%") or not unit else f"{v} {unit}" for v in values)
        r["sentence"] = f"{context}, {r['label']}: {shown}" if context else f"{r['label']}: {shown}"
    return [r for r in out if not r.get("header")]


def page_title(page: pymupdf.Page) -> str:
    """The first upper-case heading of the page that names a measured quantity (table title for a reader)."""
    for line in page.get_text().splitlines():
        if len(line.split()) >= 4 and line.strip().isupper() and re.search(r"PHÁT THẢI|TIÊU THỤ|NƯỚC|CHẤT THẢI|NĂNG LƯỢNG", line):
            return line.strip()
    return ""


def is_year(text: str) -> bool:
    return bool(re.fullmatch(r"(19|20)\d\d[.,]?", text))


def cross_foot(trs: list[dict], col_tol: float = 40.0) -> list[dict]:
    """For each total row, sum the numbers of the rows above it (back to the previous total) in the same column."""
    checks, start = [], 0
    for i, r in enumerate(trs):
        if not TOTAL.match(r["label"]):
            continue
        for text, x in r["numbers"]:
            try:
                total, half_t = parse_number(text.strip("()%"))
            except ValueError:
                continue
            parts = []
            for above in trs[start:i]:
                for t2, x2 in above["numbers"]:
                    if abs(x2 - x) < col_tol and not is_year(t2):
                        try:
                            parts.append(parse_number(t2.strip("()%")))
                        except ValueError:
                            pass
            if len(parts) >= 2:
                s, tol = sum(v for v, _ in parts), half_t + sum(h for _, h in parts)
                checks.append({"total_row": r["label"], "total": text, "parts": len(parts), "sum": round(s, 3),
                               "tolerance": tol, "ok": abs(s - total) <= tol})
        start = i + 1
    return checks


def main() -> None:
    doc = pymupdf.open(sys.argv[1])
    sys.stdout.reconfigure(encoding="utf-8")
    for p in map(int, sys.argv[2:]):
        trs = table_rows(doc[p - 1])
        print(f"== page {p}: {len(trs)} row sentences")
        for r in trs:
            print("  ", r["sentence"][:160])
        for c in cross_foot(trs):
            print("   cross-foot", c)


if __name__ == "__main__":
    main()
