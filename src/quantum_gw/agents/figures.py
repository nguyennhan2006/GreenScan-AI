"""Disclosed figures: the numbers a company publishes, as auditable items.

A claim is a sentence. A *disclosed figure* is a row of a disclosure table --
"Phạm vi 1 · 22.540.603 · tCO2e · 2025" -- and for an auditor it is the more
important of the two: prose is the presentation assertion, but the published
number is the accuracy assertion, and it is what a substantive procedure tests.

The claim extractor rejects these rows on purpose (`table_row`): they have no
subject and no verb, so they cannot be verified the way a sentence is. Rejecting
them was right and also left the system blind -- on the Hòa Phát 2025 report only
4 of 156 claims carried an absolute quantity, and the group's total emissions
figure was not among them (ISSUES P2). So the rows come back here as their own
kind of object, with their own procedures.

Two procedures run on them, both deterministic and both standard audit work:

    cross-foot      re-perform the company's own arithmetic: do the components
                    add up to the total it printed? On HPG 2025 the answer is
                    22,540,603 + 933,876 = 23,474,479 against a disclosed
                    23,474,480 -- a one-tonne rounding difference, which is the
                    kind of thing an auditor wants stated rather than hidden.
    corroboration   does the same indicator appear in another document of the
                    same period, and does it agree?

Neither asks a model anything. The figures are read by pattern, the arithmetic is
arithmetic, and every check carries the calculation it performed.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

import yaml

from quantum_gw.domain.models import DisclosedFigure, EvidenceChunk, FigureCheck
from quantum_gw.storage.audit import AuditLogger
from quantum_gw.utils import vn_format as vn
from quantum_gw.utils.text import (
    YEAR_RE,
    emission_scopes,
    normalize_for_match,
    normalize_text,
    parse_quantities,
    stable_id,
)

# Row labels that mark a component or a total of a disclosure table. Scope rows
# and total rows are what make the cross-foot possible.
#
# The scope label is matched on folded text (`normalize_for_match`): "phạm vi"
# has no accent-fold twin that could be mistaken for it.
_SCOPE_LABEL = r"(?:pham vi|scope)\s*[123](?:\s*(?:va|and|\+|,|-)\s*[123])*"

# The total label is matched on the label's OWN orthography (lower-cased, accents
# kept). Folded, "cộng" (total) and "công" (công suất, công ty, công nghiệp) are
# the same string "cong", and "tổng" opens "Tổng công ty" (a corporation): on the
# Hòa Phát 2025 run 25 of 57 "disclosed figures" were subsidiaries' ownership
# shares, gender ratios and plant capacities read as table totals -- the
# "thiếu"/"thiêu" collision of 17/09 again, in a different module.
_TOTAL_RE = re.compile(
    r"^(?:tổng\s+cộng|tổng\s+số|grand\s+total|total|cộng(?!\s+đồng)"
    r"|tổng(?!\s+(?:công\s+ty|cục|giám\s+đốc|quan|hợp|thể|kết|thống|biên\s+tập)))(?!\w)"
)
# A label typed without any diacritics (OCR output, an English report) can only
# be read safely in its unambiguous forms: a bare "cong"/"tong" is "công"/"tổng"
# as often as it is "cộng".
_TOTAL_ASCII_RE = re.compile(r"^(?:tong\s+cong|tong\s+so|grand\s+total|total)(?!\w)")

# "nước" is water and also country: "cả nước", "trong và ngoài nước", "nhà nước".
# The country senses are removed before a label is read for its metric.
_NOT_WATER_RE = re.compile(
    r"(?:\b(?:cả|trong|ngoài|nhà|đất|các|mọi|nhiều|xuất\s+khẩu\s+ra)\s+nước\b|\bnước\s+(?:ngoài|bạn|ta|sở\s+tại)\b)"
)

# Units that name an environmental quantity by themselves. "tấn" and "%" do not:
# a tonne may be steel, a percentage may be a gender ratio, so a row in those
# units must also name what it measures.
_ENVIRONMENTAL_UNITS = {"tco2e", "kgco2e", "gj", "mj", "tj", "kwh", "mwh", "gwh", "m3"}

# A multiplier word between a figure and its unit: "5,6 triệu tấn".
_MULTIPLIER_RE = re.compile(r"^\s*(nghin|ngan|trieu|ty|thousand|million|billion)(?!\w)")
_MULTIPLIER_VALUE = {
    "nghin": 1e3, "ngan": 1e3, "thousand": 1e3,
    "trieu": 1e6, "million": 1e6,
    "ty": 1e9, "billion": 1e9,
}

# Where the next number starts. A digit inside a unit ("CO2", "m3") is not one:
# "2,32 tấn CO2/tấn thép" keeps its unit.
_NEXT_NUMBER_RE = re.compile(r"(?<![^\W\d_])\d")

# The end of the sentence before a row label. A label is the tail of the text
# before its figure, and that tail must not reach back into the previous
# sentence: "…điều chỉnh carbon. GIỚI TÍNH QUỐC TỊCH 100 %" is a headcount row,
# not an emissions row.
_SENTENCE_END_RE = re.compile(r"[.!?;]\s+(?=\S)")


def is_total_label(label: str) -> bool:
    """True for a table's total row ("Tổng cộng", "Cộng", "Tổng", "Total")."""
    text = normalize_text(label).lower().strip(" .·-–—|:")
    if _TOTAL_RE.match(text):
        return True
    return text == normalize_for_match(text) and bool(_TOTAL_ASCII_RE.match(text))

_SPLIT_TERMS = {"phát thải", "khí thải", "chất thải", "nước thải", "tiêu thụ", "năng lượng", "tái tạo", "nhà kính"}

# A label sits immediately before its figure on the same line of the table.
# Keeping the label short is what stops a whole sentence being read as one.
_LABEL_VALUE_RE = re.compile(
    r"(?P<label>[^\n|]{2,70}?)\s*[:|]?\s+(?P<value>\d[\d.,]{2,})(?=\D|$)",
    re.IGNORECASE,
)

# Unit declared for a block of rows rather than on each row: "(tCO2e)", "Đơn vị: GJ".
_UNIT_HINT_RE = re.compile(
    r"[(（]\s*(?P<unit>[^)）]{1,14})\s*[)）]|đơn vị\s*[:：]\s*(?P<unit2>[^\s,.;]{1,14})",
    re.IGNORECASE,
)
_UNIT_WORD_RE = re.compile(
    r"(?:tco2e?|tấn\s*co2e?|co2e|gj|mj|tj|kwh|mwh|gwh|m3|m³|tấn|kg|%)", re.IGNORECASE
)


# A row labelled only "Cộng" still says what it is a total of, through its unit.
# Without this the group's own emissions total scored as an unclassified number
# and fell below the prose it was meant to outrank.
_UNIT_METRIC = {
    "tco2e": "emissions",
    "kgco2e": "emissions",
    "gj": "energy",
    "mj": "energy",
    "tj": "energy",
    "kwh": "energy",
    "mwh": "energy",
    "gwh": "energy",
    "m3": "water",
}


def _load_taxonomy(path: str) -> dict:
    resolved = Path(path)
    if not resolved.exists():
        resolved = Path(__file__).resolve().parents[3] / path
    try:
        return yaml.safe_load(resolved.read_text(encoding="utf-8")) or {}
    except OSError:
        return {}


class DisclosedFigureAgent:
    """Reads published indicator rows out of the parsed document."""

    def __init__(self, audit: AuditLogger, taxonomy_path: str = "configs/taxonomy.yaml"):
        self.audit = audit
        taxonomy = _load_taxonomy(taxonomy_path)
        self.metric_terms: dict[str, list[str]] = {}
        for metric, entry in (taxonomy.get("metrics") or {}).items():
            terms = [
                normalize_for_match(term)
                for language in ("vi", "en")
                for term in (entry or {}).get(language) or []
            ]
            self.metric_terms[metric] = [t for t in terms if len(t) > 2]

    # ------------------------------------------------------------------ read

    def run(self, chunks: list[EvidenceChunk]) -> list[DisclosedFigure]:
        by_page: dict[tuple[str, int | None], list[EvidenceChunk]] = defaultdict(list)
        for chunk in chunks:
            by_page[(chunk.doc_id, chunk.page)].append(chunk)

        figures: list[DisclosedFigure] = []
        for (_doc_id, page), page_chunks in by_page.items():
            # The unit and the period are usually printed once, in a heading above
            # the rows, and the chunker puts that heading in a different chunk.
            # Resolving them per page is what makes a bare "Phạm vi 1 22.540.603"
            # readable as tCO2e for 2025.
            page_unit = _page_unit(page_chunks)
            page_period = _page_period(page_chunks)
            for chunk in page_chunks:
                if (chunk.metadata or {}).get("table"):
                    figures.extend(self._from_table(chunk, page))
                else:
                    figures.extend(self._from_chunk(chunk, page, page_unit, page_period))

        deduped = _dedupe(figures)
        self.audit.write(
            "disclosed_figures_extracted",
            {
                "count": len(deduped),
                "by_unit": _tally(f.unit for f in deduped),
                "with_period": sum(1 for f in deduped if f.period),
                "totals": sum(1 for f in deduped if f.is_total),
            },
        )
        return deduped

    def _from_chunk(
        self, chunk: EvidenceChunk, page: int | None, page_unit: str | None, page_period: str | None
    ) -> list[DisclosedFigure]:
        figures: list[DisclosedFigure] = []
        for line in chunk.text.split("\n"):
            for match in _LABEL_VALUE_RE.finditer(line):
                label = self._trim_label(match.group("label"))
                if label is None:
                    continue
                quantities = parse_quantities(match.group("value"))
                if not quantities:
                    continue
                value, unit, _ = quantities[0]
                if 1900 <= value <= 2100 and unit is None:
                    continue  # a year standing next to a label is not a measurement
                # Only what stands between this figure and the next number belongs
                # to it: in "Cộng 23.474.480 100%" the per cent is the next
                # column's share, not the unit of 23 million.
                tail = line[match.end("value"): match.end("value") + 24]
                head = _NEXT_NUMBER_RE.split(tail, maxsplit=1)[0]
                value *= _multiplier_in(head)  # "5,6 triệu tấn" is 5,600,000 t
                unit = unit or _unit_in(head) or _hinted_unit(label) or page_unit
                if unit is None:
                    continue  # a number with no unit anywhere is not a disclosed figure
                metric = (
                    self._metric_of(label)
                    or self._metric_of(chunk.text[:400])
                    or _UNIT_METRIC.get(unit)
                )
                if metric is None and unit not in _ENVIRONMENTAL_UNITS:
                    # A tonnage or a percentage that names no environmental
                    # indicator: plant capacity, an ownership share, a headcount.
                    continue
                figures.append(
                    DisclosedFigure(
                        figure_id=stable_id(chunk.chunk_id, label, str(value), unit),
                        label=label,
                        value=value,
                        unit=unit,
                        period=_period_in(line) or page_period,
                        scopes=sorted(emission_scopes(label)),
                        is_total=is_total_label(label),
                        metric=metric,
                        source_doc_id=chunk.doc_id,
                        source_chunk_id=chunk.chunk_id,
                        source_name=chunk.source_name,
                        source_page=page,
                        raw_line=line.strip()[:200],
                    )
                )
        return figures

    def _from_table(self, chunk: EvidenceChunk, page: int | None) -> list[DisclosedFigure]:
        """Every cell of a laid-out table that has a value and a unit (page-regions-v1, parsers/layout.py).

        The row label, the column header, the unit and the period were read from the table's own geometry,
        so a cell needs no pattern to be understood: "Số tiền còn lại chưa được phân bổ | Giá trị (tỷ VND): 51"
        is 51 billion VND, and "7,085" under "(Nghìn tấn)" is 7,085,000 t.
        """
        table = chunk.metadata["table"]
        caption = table.get("caption") or ""
        figures: list[DisclosedFigure] = []
        for row_index, row in enumerate(table.get("rows") or []):
            row_label = normalize_text(row.get("label") or "")
            raw = row_label + " | " + " | ".join(c.get("text") or "" for c in row.get("cells") or [])
            for cell in row.get("cells") or []:
                value, unit = cell.get("value"), cell.get("unit")
                if value is None or not unit:
                    continue
                header = normalize_text(cell.get("header") or "")
                label = row_label or header or caption
                if header and row_label and header.lower() not in row_label.lower() and len(header) <= 60:
                    label = f"{row_label} · {header}"
                label = label[:160]
                figures.append(
                    DisclosedFigure(
                        figure_id=stable_id(chunk.chunk_id, str(row_index), label, str(value), unit),
                        label=label,
                        value=value,
                        unit=unit,
                        period=cell.get("period") or table.get("period"),
                        scopes=sorted(emission_scopes(row_label)),
                        is_total=is_total_label(row_label),
                        metric=(self._metric_of(row_label) or self._metric_of(header) or self._metric_of(caption)
                                or _UNIT_METRIC.get(unit.lower())),
                        source_doc_id=chunk.doc_id,
                        source_chunk_id=chunk.chunk_id,
                        source_name=chunk.source_name,
                        source_page=page,
                        raw_line=raw[:200],
                    )
                )
        return figures

    def _trim_label(self, raw: str) -> str | None:
        """The row label is the tail of the text before the figure, not the whole line.

        A PDF puts a table row and the prose around it on one line, so a match
        arrives as "...thích ứng với biến đổi khí hậu Cộng". The label is the
        last few words; the longest tail that reads as an indicator wins, so
        "Tổng lượng chất thải nguy hại" is preferred over "nguy hại".
        """
        raw = _SENTENCE_END_RE.split(raw)[-1]
        words = raw.strip(" .·-–—|:").split()
        for size in range(min(7, len(words)), 0, -1):
            if size < len(words) and _NOT_WATER_RE.match(
                normalize_text(f"{words[-size - 1]} {words[-size]}").lower()
            ):
                continue  # the label would start inside "cả nước" and read as water
            candidate = " ".join(words[-size:]).strip(" .·-–—|:")
            if candidate and self._is_indicator_label(candidate):
                # The seven-word tail can start in the middle of a two-word term: "(phát) thải Scope 1 và
                # Scope 2 là". Take the head word back so the label reads as written.
                if size < len(words) and f"{words[-size - 1]} {words[-size]}".lower() in _SPLIT_TERMS:
                    candidate = f"{words[-size - 1]} {candidate}"
                return candidate
        return None

    def _is_indicator_label(self, label: str) -> bool:
        """A row label, not a sentence: a scope, a total, or a named indicator."""
        folded = normalize_for_match(label)
        if len(folded.split()) > 9:
            return False
        if re.search(_SCOPE_LABEL, folded) or is_total_label(label):
            return True
        # A unit is not an indicator name: "tCO2e, chiếm 0,39 %" names nothing.
        return self._metric_of(_UNIT_WORD_RE.sub(" ", label)) is not None

    def _metric_of(self, text: str) -> str | None:
        folded = normalize_for_match(_NOT_WATER_RE.sub(" ", normalize_text(text).lower()))
        for metric, terms in self.metric_terms.items():
            if any(term in folded for term in terms):
                return metric
        return None


# --------------------------------------------------------------- procedures


def cross_foot(figures: list[DisclosedFigure]) -> list[FigureCheck]:
    """Re-perform the company's own addition: do the parts equal the printed total?

    Grouped per document, page and unit, because that is the boundary of one
    printed table. A difference within half of the total's last published digit
    is reported as rounding, not as an error -- the same precision rule the
    numeric comparator uses.
    """
    checks: list[FigureCheck] = []
    groups: dict[tuple[str, int | None, str], list[DisclosedFigure]] = defaultdict(list)
    for figure in figures:
        groups[(figure.source_doc_id, figure.source_page, figure.unit)].append(figure)

    for (_doc, page, unit), group in groups.items():
        totals = [f for f in group if f.is_total]
        parts = [f for f in group if not f.is_total and f.scopes]
        if not totals or len(parts) < 2:
            continue
        total = max(totals, key=lambda f: f.value)
        # Components must not overlap: Scope 1 and Scope 2 add up, Scope 1 and
        # "Scope 1 and 2" do not.
        chosen: list[DisclosedFigure] = []
        covered: set[int] = set()
        for part in sorted(parts, key=lambda f: len(f.scopes)):
            if covered & set(part.scopes):
                continue
            chosen.append(part)
            covered |= set(part.scopes)
        if len(chosen) < 2:
            continue
        summed = sum(f.value for f in chosen)
        difference = summed - total.value
        tolerance = _rounding_tolerance(total.value, len(chosen))
        calculation = " + ".join(vn.number(f.value) for f in chosen) + f" = {vn.number(summed)}"
        consistent = abs(difference) <= tolerance
        checks.append(
            FigureCheck(
                check_id=stable_id("cross_foot", total.figure_id),
                kind="cross_foot",
                status="CONSISTENT" if consistent else "INCONSISTENT",
                figure_ids=[f.figure_id for f in chosen] + [total.figure_id],
                calculation=f"{calculation}; công bố {vn.number(total.value)} {vn.unit(unit)}",
                difference=round(difference, 4),
                tolerance=tolerance,
                note=(
                    f"Cộng lại các thành phần (phạm vi {'+'.join(str(s) for s in sorted(covered))}) "
                    + (f"trên trang {page}: " if page is not None else ": ")
                    + (
                        f"khớp với số công bố trong sai số làm tròn ({vn.signed(round(difference))} {vn.unit(unit)})."
                        if consistent
                        else f"lệch {vn.signed(round(difference))} {vn.unit(unit)} so với số công bố — cần người xem."
                    )
                ),
            )
        )
    return checks


def corroborate(figures: list[DisclosedFigure]) -> list[FigureCheck]:
    """Does the same indicator appear in another document of the same period?

    Agreement across two documents the company published is weak evidence but
    real; disagreement is a finding. Silence is neither, and is reported as
    uncorroborated so a reviewer can decide whether it should have been there.
    """
    checks: list[FigureCheck] = []
    groups: dict[tuple[str, str, str | None], list[DisclosedFigure]] = defaultdict(list)
    for figure in figures:
        key = (normalize_for_match(figure.label), figure.unit, figure.period)
        groups[key].append(figure)

    for (label, unit, period), group in groups.items():
        documents = {f.source_doc_id for f in group}
        if len(documents) < 2:
            continue
        low, high = min(f.value for f in group), max(f.value for f in group)
        tolerance = _rounding_tolerance(high, 1)
        agrees = (high - low) <= tolerance
        checks.append(
            FigureCheck(
                check_id=stable_id("corroborate", label, unit, period or ""),
                kind="cross_document",
                status="CONSISTENT" if agrees else "INCONSISTENT",
                figure_ids=[f.figure_id for f in group],
                calculation=f"{vn.number(low)} so với {vn.number(high)} {vn.unit(unit)}",
                difference=round(high - low, 4),
                tolerance=tolerance,
                note=(
                    f"Chỉ tiêu “{label}” {('kỳ ' + period) if period else ''} xuất hiện ở "
                    f"{len(documents)} tài liệu: "
                    + ("số liệu khớp nhau." if agrees else "số liệu **không khớp** giữa hai tài liệu.")
                ),
            )
        )
    return checks


_SHARE_RE = re.compile(r"tỷ trọng|tỉ trọng|cơ cấu|chiếm|phân bổ")

# A table row label this long is a paragraph that a ruled frame happened to enclose, not a row label.
_MAX_TABLE_LABEL = 120


def keep_material(figures: list[DisclosedFigure], checks: list[FigureCheck]) -> list[DisclosedFigure]:
    """Table figures a reviewer should see: those that name an indicator, or that a procedure used.

    A laid-out annual report has hundreds of cells in units (a financial statement, a list of subsidiaries
    with their charter capital); without this the queue filled with "PHẦN 7 BCTC HỢP NHẤT … Marcegaglia".
    Figures read from prose keep the rules they always had.
    """
    used = {fid for check in checks for fid in check.figure_ids}
    kept = []
    for f in figures:
        from_table = " | " in (f.raw_line or "")
        if from_table and f.figure_id not in used:
            if f.metric is None or len(f.label.split(" · ")[0]) > _MAX_TABLE_LABEL:
                continue
        kept.append(f)
    return kept


def table_checks(figures: list[DisclosedFigure], done: list[FigureCheck] | None = None) -> list[FigureCheck]:
    """Arithmetic a reader does on a laid-out table without being told (page-regions-v1).

        table_sum   one row of a table equals the sum of the others in the same unit
                    (Hòa Phát p.50: 6.982 + 103 = 7.085 nghìn tấn)
        page_sum    the rows of one table add up to a figure printed in another table of the page
                    (Techcombank p.8: 399 + 51 = 450 tỷ VND, allocated + unallocated = issued)
        ratio       a printed percentage equals its row's value over a figure of the same unit on the page
                    (399 / 450 = 88,7 % against 89 % printed; Hòa Phát p.39: 23.369.500 / 23.474.480 = 99,55 %)

    Agreement is reported. A disagreement is reported only against the table's own total row, the one
    place where the company has said what the parts should add up to. A total that `cross_foot` already
    checked is not checked twice.
    """
    checked = {fid for check in done or [] for fid in check.figure_ids}
    table_figures = [f for f in figures if f.raw_line and " | " in f.raw_line]
    by_table: dict[str, list[DisclosedFigure]] = defaultdict(list)
    for f in table_figures:
        by_table[f.source_chunk_id].append(f)
    by_page: dict[tuple[str, int | None], list[DisclosedFigure]] = defaultdict(list)
    for f in table_figures:
        by_page[(f.source_doc_id, f.source_page)].append(f)
    checks: list[FigureCheck] = []
    seen: set[str] = set()

    def add(kind, status, members, calculation, note, difference=0.0, tolerance=0.0):
        check_id = stable_id(kind, *sorted(f.figure_id for f in members))
        if check_id in seen:
            return
        seen.add(check_id)
        checks.append(FigureCheck(check_id=check_id, kind=kind, status=status,
                                  figure_ids=[f.figure_id for f in members], calculation=calculation,
                                  difference=round(difference, 4), tolerance=tolerance, note=note))

    def plus(parts):
        return " + ".join(vn.number(f.value) for f in parts)

    def arith(parts, summed, other, unit, said):
        """The sum as the page prints it: 4.994 + 41.334 = 46.328 triệu lít, not 4.994.000.000 + ..."""
        values = [f.value for f in parts] + [summed, other]
        for factor, word in ((1e9, "tỷ"), (1e6, "triệu"), (1e3, "nghìn")):
            scaled = [v / factor for v in values]
            if all(abs(x - round(x)) < 1e-6 for x in scaled) and min(abs(v) for v in values if v) >= factor:
                terms = " + ".join(vn.number(round(x)) for x in scaled[:-2])
                return (f"{terms} = {vn.number(round(scaled[-2]))}; {said} {vn.number(round(scaled[-1]))} "
                        f"{word} {vn.unit(unit)}")
        return f"{plus(parts)} = {vn.number(summed)}; {said} {vn.number(other)} {vn.unit(unit)}"

    # table_sum
    sums_by_table: dict[str, list[tuple[str, float, list[DisclosedFigure]]]] = defaultdict(list)
    for chunk_id, group in by_table.items():
        # One column of one table: the same unit under the same header ("PHÁT SINH" and "TÁI SỬ DỤNG" are
        # both in tonnes and must not be added together).
        units: dict[tuple[str, str], list[DisclosedFigure]] = defaultdict(list)
        for f in group:
            if f.unit != "%":
                header = f.label.split(" · ", 1)[1] if " · " in f.label else ""
                units[(f.unit, header)].append(f)
        for (unit, _header), members in units.items():
            parts_all = [f for f in members if not f.is_total]
            if len(parts_all) >= 2:
                sums_by_table[chunk_id].append((unit, sum(f.value for f in parts_all), parts_all))
            if len(members) < 3:
                continue
            matched = False
            for total in sorted(members, key=lambda f: (not f.is_total, -f.value)):
                parts = [f for f in members if f is not total and not f.is_total]
                if len(parts) < 2 or total.figure_id in checked:
                    continue
                summed = sum(f.value for f in parts)
                tolerance = _rounding_tolerance(total.value, len(parts))
                if abs(summed - total.value) <= tolerance:
                    matched = True
                    add("table_sum", "CONSISTENT", parts + [total],
                        arith(parts, summed, total.value, unit, "công bố"),
                        f"Các dòng của bảng trang {total.source_page} cộng lại bằng dòng “{total.label[:60]}”.",
                        summed - total.value, tolerance)
                    break
            explicit = [f for f in members if f.is_total and f.figure_id not in checked]
            if not matched and explicit:
                total = max(explicit, key=lambda f: f.value)
                parts = [f for f in members if not f.is_total]
                if len(parts) >= 2:
                    summed = sum(f.value for f in parts)
                    tolerance = _rounding_tolerance(total.value, len(parts))
                    add("table_sum", "INCONSISTENT", parts + [total],
                        arith(parts, summed, total.value, unit, "công bố"),
                        f"Bảng trang {total.source_page}: các dòng không cộng ra dòng tổng "
                        f"(lệch {vn.signed(round(summed - total.value))} {vn.unit(unit)}) — cần người xem, "
                        "có thể bảng có dòng con.",
                        summed - total.value, tolerance)

    # table_sum on a share column: the parts of a "Tỷ trọng" column add up to its printed total row
    # (Hòa Phát p.39: 99,55 + 0,39 + 0,01 + 0,04 + 0,01 = 100 %). Agreement only: shares are rounded
    # to the printed decimals, so a small gap is not a finding.
    for chunk_id, group in by_table.items():
        shares: dict[str, list[DisclosedFigure]] = defaultdict(list)
        for f in group:
            if f.unit == "%":
                shares[f.label.split(" · ", 1)[1] if " · " in f.label else ""].append(f)
        for members in shares.values():
            totals = [f for f in members if f.is_total and f.figure_id not in checked]
            parts = [f for f in members if not f.is_total]
            if not totals or len(parts) < 2:
                continue
            total = max(totals, key=lambda f: f.value)
            summed = sum(f.value for f in parts)
            if abs(summed - total.value) <= 0.01 * len(parts) + 0.05:
                add("table_sum", "CONSISTENT", parts + [total],
                    " + ".join(vn.number(f.value, 2) for f in parts)
                    + f" = {vn.number(summed, 2)} %; công bố {vn.number(total.value, 2)} %",
                    f"Các tỷ trọng của bảng trang {total.source_page} cộng lại bằng dòng “{total.label[:60]}”.",
                    summed - total.value, 0.01 * len(parts) + 0.05)

    # page_sum
    for chunk_id, sums in sums_by_table.items():
        for unit, summed, parts in sums:
            key = (parts[0].source_doc_id, parts[0].source_page)
            for other in by_page[key]:
                if other.source_chunk_id == chunk_id or other.unit != unit:
                    continue
                tolerance = _rounding_tolerance(other.value, len(parts))
                if abs(summed - other.value) <= tolerance:
                    add("page_sum", "CONSISTENT", parts + [other],
                        arith(parts, summed, other.value, unit, "bảng khác ghi"),
                        f"Trang {other.source_page}: các dòng của một bảng cộng lại bằng “{other.label[:60]}” "
                        "ở bảng khác cùng trang.",
                        summed - other.value, tolerance)
                    break

    # ratio
    for f in table_figures:
        if f.unit != "%" or f.value <= 0:
            continue
        row = [g for g in by_table[f.source_chunk_id] if g.raw_line == f.raw_line and g.unit != "%"]
        if len(row) != 1:
            continue
        part = row[0]
        text = repr(float(f.value))
        decimals = len(text.split(".")[1].rstrip("0")) if "." in text else 0
        tol = 0.5 * 10 ** -decimals + 1e-9
        candidates = [g for g in by_page[(f.source_doc_id, f.source_page)]
                      if g.unit == part.unit and g.value > part.value > 0 and g.figure_id != part.figure_id
                      # the denominator is a printed total: against any number on the page a small percentage
                      # matches by chance (Hòa Phát p.41: 230,74 / 193.078 ≈ 0,1 %, the steel row, not the total)
                      and g.is_total]
        candidates.sort(key=lambda g: (g.source_chunk_id != part.source_chunk_id, not g.is_total))
        hit = next((g for g in candidates if abs(part.value / g.value * 100 - f.value) <= tol), None)
        if hit:
            share = part.value / hit.value * 100
            add("ratio", "CONSISTENT", [part, hit, f],
                f"{vn.number(part.value)} / {vn.number(hit.value)} = {vn.number(share, 2)} %; "
                f"công bố {vn.number(f.value, decimals)} %",
                f"Tỷ lệ in ở dòng “{part.label[:50]}” khớp với giá trị chia cho “{hit.label[:50]}”.")
            continue
        own_total = next((g for g in candidates if g.is_total and g.source_chunk_id == part.source_chunk_id), None)
        # A percentage column is not always a share of the total: Hòa Phát p.51 prints a reuse rate
        # ("TÁI SỬ DỤNG 99 %") beside each sector's tonnage. Disagreement is only a finding when the column
        # says it is a share.
        if own_total and _SHARE_RE.search(f.label.split(" · ")[-1].lower()):
            share = part.value / own_total.value * 100
            add("ratio", "INCONSISTENT", [part, own_total, f],
                f"{vn.number(part.value)} / {vn.number(own_total.value)} = {vn.number(share, 2)} %; "
                f"công bố {vn.number(f.value, decimals)} %",
                f"Tỷ lệ in ở dòng “{part.label[:50]}” không khớp với giá trị chia cho dòng tổng của bảng "
                "— cần người xem.",
                share - f.value, tol)
    return checks


# ------------------------------------------------------------------ helpers


def _rounding_tolerance(value: float, terms: int) -> float:
    """Half of the last published digit, once per term that was added."""
    magnitude = abs(value)
    if magnitude == 0:
        return 0.5
    digits = f"{magnitude:.0f}"
    trailing = len(digits) - len(digits.rstrip("0"))
    return max(0.5, 0.5 * (10**trailing)) * max(1, terms)


def _page_unit(chunks: list[EvidenceChunk]) -> str | None:
    for chunk in chunks:
        for match in _UNIT_HINT_RE.finditer(chunk.text):
            candidate = match.group("unit") or match.group("unit2") or ""
            unit = _unit_in(candidate)
            if unit:
                return unit
    return None


def _page_period(chunks: list[EvidenceChunk]) -> str | None:
    years: list[str] = []
    for chunk in chunks:
        years.extend(YEAR_RE.findall(chunk.text))
    return max(set(years), key=years.count) if years else None


def _hinted_unit(label: str) -> str | None:
    """A unit declared inside the row label itself: "Tỷ trọng điện năng (%)"."""
    for match in _UNIT_HINT_RE.finditer(label):
        unit = _unit_in(match.group("unit") or match.group("unit2") or "")
        if unit:
            return unit
    return None


def _multiplier_in(head: str) -> float:
    match = _MULTIPLIER_RE.match(normalize_for_match(head))
    return _MULTIPLIER_VALUE[match.group(1)] if match else 1.0


def _unit_in(text: str) -> str | None:
    match = _UNIT_WORD_RE.search(text)
    if not match:
        return None
    quantities = parse_quantities("1 " + match.group(0))
    return quantities[0][1] if quantities and quantities[0][1] else None


def _period_in(line: str) -> str | None:
    years = YEAR_RE.findall(line)
    return years[0] if years else None


def _dedupe(figures: list[DisclosedFigure]) -> list[DisclosedFigure]:
    seen: set[tuple] = set()
    kept: list[DisclosedFigure] = []
    for figure in figures:
        key = (figure.source_doc_id, figure.source_page, normalize_for_match(figure.label),
               figure.value, figure.unit)
        if key in seen:
            continue
        seen.add(key)
        kept.append(figure)
    return kept


def _tally(values) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        key = str(value)
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))
