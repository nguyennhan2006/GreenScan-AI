"""Build the 50-sentence kit a person labels to measure the human ceiling of GS-Claims v1.

Stratified from the 140 non-control sentences: 25 that the merged labels call claims and 25 they do not,
drawn at random within each stratum (hard cases are not over-weighted, so agreement estimates the ceiling). The person sees only the sentence and its context, never the labels.

usage (repo root): .venv/Scripts/python.exe -I benchmark/gs_claims_v1/human/build_human_kit.py
writes human/items_50.csv (UTF-8 with BOM, opens in Excel) and human/items_50.xlsx (drop-down lists)
"""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
FIELDS = {
    "is_claim": ["yes", "no"],
    "claim_kind": ["metric_disclosure", "performance", "commitment", "practice", "promotional", "na"],
    "has_figure": ["yes", "no"],
    "has_period": ["yes", "implicit", "no"],
    "has_baseline": ["yes", "no", "na"],
    "has_ghg_scope": ["yes", "no", "na"],
    "has_boundary": ["yes", "no"],
    "cites_independent_source": ["yes", "no"],
    "promotional_language": ["yes", "no"],
}


def main() -> None:
    gold = [json.loads(line) for line in (BASE / "gold.jsonl").open(encoding="utf-8")]
    items = {json.loads(line)["item_id"]: json.loads(line) for line in (BASE / "items.jsonl").open(encoding="utf-8")}
    key = {json.loads(line)["item_id"]: json.loads(line) for line in (BASE / "_key" / "key.jsonl").open(encoding="utf-8")}
    real = [g for g in gold if not key[g["item_id"]]["control"]]
    rng = random.Random(20261116)
    chosen = []
    for want in ("yes", "no"):
        pool = [g for g in real if g["is_claim"] == want]
        rng.shuffle(pool)  # a plain random draw per stratum: agreement on it estimates the human ceiling fairly
        chosen += pool[:25]
    rng.shuffle(chosen)
    header = ["item_id", "company", "text", "context", *FIELDS, "note"]
    with (HERE / "items_50.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for g in chosen:
            it = items[g["item_id"]]
            w.writerow([g["item_id"], it["company"], it["text"], it["context"], *[""] * len(FIELDS), ""])
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font
        from openpyxl.worksheet.datavalidation import DataValidation
    except ImportError:
        print("[kit] openpyxl not installed: only the CSV was written")
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "gan_nhan"
        ws.append(header)
        for cell in ws[1]:
            cell.font = Font(bold=True)
        for g in chosen:
            it = items[g["item_id"]]
            ws.append([g["item_id"], it["company"], it["text"], it["context"], *[None] * len(FIELDS), None])
        for col, width in zip("ABCD", (16, 9, 70, 40)):
            ws.column_dimensions[col].width = width
        for row in ws.iter_rows(min_row=2, max_col=4):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        for i, (field, values) in enumerate(FIELDS.items(), start=5):
            letter = ws.cell(row=1, column=i).column_letter
            ws.column_dimensions[letter].width = 16
            dv = DataValidation(type="list", formula1='"' + ",".join(values) + '"', allow_blank=True)
            ws.add_data_validation(dv)
            dv.add(f"{letter}2:{letter}{len(chosen) + 1}")
        wb.save(HERE / "items_50.xlsx")
    print(f"[kit] {len(chosen)} items ({sum(g['is_claim'] == 'yes' for g in chosen)} claims by merged labels, "
          f"{sum(bool(g['provenance']['fields_adjudicated']) for g in chosen)} disputed) -> {HERE}")


if __name__ == "__main__":
    main()
