from __future__ import annotations

import csv
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

import fitz

from quantum_gw.utils.text import parse_numbers

# The Windows installer (UB Mannheim) does not add tesseract to PATH.
WINDOWS_TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")

# Tesseract confidence (0-100) below which a reading is reported as uncertain.
# Measured on 60 born-digital pages of 52 VN30 reports, where the true text is
# known (tools/measure_ocr_confidence.py, benchmark/ocr_calibration_2026-11-11.json;
# table in docs/decisions/0005-ocr-confidence.md):
#   a number read below 90 was right at most 48% of the time, from 90 on 83-91%;
#   a word read below 80 was right at most 31% of the time;
#   a page whose mean is below 80 matched its text on 55% of words or fewer.
LOW_WORD_CONF = 80.0
LOW_NUMBER_CONF = 90.0
LOW_PAGE_CONF = 80.0  # gate G9 reports such a page as weak


def resolve_command(command: str) -> str | None:
    """`command` found on PATH or as a path, else the default Windows install; None when absent."""
    found = shutil.which(command)
    if found is None and command == "tesseract" and WINDOWS_TESSERACT.exists():
        found = str(WINDOWS_TESSERACT)
    return found


@cache
def installed_languages(command: str) -> frozenset[str]:
    """Languages tesseract can load (TESSDATA_PREFIX is honoured); empty when it cannot run."""
    try:
        completed = subprocess.run(
            [command, "--list-langs"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return frozenset()
    # The first line is a header: List of available languages in "...tessdata/" (N):
    return frozenset(line.strip() for line in completed.stdout.splitlines()[1:] if line.strip())


def contains_number(text: str, token: str) -> bool:
    """`token` ("30", "1.936") occurs in `text` as a whole number, not inside "2030" or "1.9365"."""
    return re.search(r"(?<![\d.,])" + re.escape(token) + r"(?![\d]|[.,]\d)", text or "") is not None


def matches_value(token: str, values) -> bool:
    """`token` ("1,2", "30%") read as a quantity equals one of `values`, allowing for nghìn/triệu/tỷ after it.

    A doubtful token is a page-level fact; this ties it to a figure a claim or a
    comparison actually uses, so "Phạm vi 1" or a page number does not cast
    doubt on a "1.936 tấn" read with confidence.
    """
    return any(abs(value * scale - other) <= 1e-9 * max(1.0, abs(other))
               for value, _ in parse_numbers(token) for scale in (1, 1e3, 1e6, 1e9) for other in values)


@dataclass
class OcrReading:
    """What Tesseract read on one page, and how sure it was."""

    text: str = ""
    # {"text", "conf", "bbox": [x0, y0, x1, y1] in page points}
    words: list[dict] = field(default_factory=list)
    mean_conf: float = 0.0          # length-weighted mean word confidence, 0-100
    low_share: float = 0.0          # share of words below LOW_WORD_CONF
    doubtful_numbers: list[str] = field(default_factory=list)   # numbers read below LOW_NUMBER_CONF

    def summary(self) -> dict:
        return {"ocr_confidence": round(self.mean_conf, 1), "ocr_low_share": round(self.low_share, 3),
                "ocr_doubtful_numbers": self.doubtful_numbers[:50]}


def parse_tsv(tsv: str, scale: float = 1.0) -> OcrReading:
    """Word-level records of Tesseract's TSV output, and the page measures built on them."""
    words = []
    for row in csv.DictReader(tsv.splitlines(), delimiter="\t", quoting=csv.QUOTE_NONE):
        text = (row.get("text") or "").strip()
        try:
            conf = float(row.get("conf") or -1)
        except ValueError:
            continue
        if row.get("level") != "5" or not text or conf < 0:
            continue
        left, top = float(row["left"]) * scale, float(row["top"]) * scale
        words.append({"text": text, "conf": conf,
                      "bbox": [round(left, 1), round(top, 1), round(left + float(row["width"]) * scale, 1),
                               round(top + float(row["height"]) * scale, 1)],
                      # Tesseract's own line: parsers/layout.py rebuilds rows of a scanned table from it.
                      "line": f'{row.get("block_num")}-{row.get("par_num")}-{row.get("line_num")}'})
    reading = OcrReading(words=words)
    weight = sum(len(w["text"]) for w in words)
    if weight:
        reading.mean_conf = sum(w["conf"] * len(w["text"]) for w in words) / weight
        reading.low_share = sum(1 for w in words if w["conf"] < LOW_WORD_CONF) / len(words)
    seen: set[str] = set()
    for w in words:
        token = w["text"].strip(".,;:()[]%")
        if any(c.isdigit() for c in token) and w["conf"] < LOW_NUMBER_CONF and token not in seen:
            seen.add(token)
            reading.doubtful_numbers.append(token)
    return reading


class TesseractOCR:
    def __init__(self, command: str = "tesseract", languages: str = "vie+eng"):
        self.command = command
        self.languages = languages

    @property
    def available(self) -> bool:
        # A missing vie.traineddata makes every call fail, which used to look like a blank page.
        resolved = resolve_command(self.command)
        return resolved is not None and set(self.languages.split("+")) <= installed_languages(resolved)

    def ocr_page(self, page: fitz.Page, dpi: int = 220) -> str:
        return self.read_page(page, dpi).text

    def read_page(self, page: fitz.Page, dpi: int = 220) -> OcrReading:
        """The page's text, exactly as the plain-text output gives it, with word confidences beside it.

        One Tesseract run writes both outputs (text and TSV), so the text is what
        `ocr_page` always returned and the confidences cost no second pass.
        """
        if not self.available:
            return OcrReading()
        pixmap = page.get_pixmap(dpi=dpi, alpha=False)
        with tempfile.TemporaryDirectory(prefix="quantum-ocr-") as tmp:
            image_path = Path(tmp) / "page.png"
            output_base = Path(tmp) / "out"
            pixmap.save(str(image_path))
            command = [
                resolve_command(self.command),
                str(image_path),
                str(output_base),
                "-l",
                self.languages,
                "--psm",
                "6",
                # Output switches as variables, not as the config files "txt" and
                # "tsv": those are looked up under TESSDATA_PREFIX/configs, which a
                # tessdata folder holding only the language models does not have,
                # and Tesseract then silently writes the text alone.
                "-c",
                "tessedit_create_txt=1",
                "-c",
                "tessedit_create_tsv=1",
            ]
            completed = subprocess.run(command, capture_output=True, text=True, timeout=120)
            if completed.returncode != 0:
                return OcrReading()
            text_path, tsv_path = output_base.with_suffix(".txt"), output_base.with_suffix(".tsv")
            text = text_path.read_text(encoding="utf-8", errors="ignore") if text_path.exists() else ""
            tsv = tsv_path.read_text(encoding="utf-8", errors="ignore") if tsv_path.exists() else ""
        # TSV boxes are in pixels of the rendered image; page points are pixels * 72 / dpi.
        reading = parse_tsv(tsv, scale=72 / dpi) if tsv else OcrReading()
        reading.text = text
        return reading
