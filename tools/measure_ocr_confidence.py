"""How far can Tesseract's word confidence be trusted on Vietnamese reports? A calibration, not a test.

OCR is graded against the text layer of born-digital pages. Each sampled page is
rendered at the pipeline's 220 dpi and read by Tesseract with the pipeline's
settings (vie+eng, psm 6), asking for word confidences (TSV) as well as text.
Every OCR word is then checked against the page's own text: it counts as read
correctly when it occurs among the page's native words (a multiset, order-free,
because reading order differs on multi-column pages). Numbers are scored apart:
a verdict is computed from them, and one misread digit turns "giảm 30%" into
"giảm 80%".

The output says, per confidence band, how often a word and a number were read
right, and how page-level mean confidence tracks page accuracy. Thresholds in
parsers/ocr.py are read off this table, not chosen by taste.

Usage:
  python tools/measure_ocr_confidence.py [--pages 60] [--per-file 5] [--seed 7] [--out FILE.json] PDF_OR_DIR...

Needs tesseract with vie.traineddata (TESSDATA_PREFIX as in .env).
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import re
import sys
import time
import unicodedata
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from quantum_gw.parsers.ocr import TesseractOCR  # noqa: E402
from quantum_gw.parsers.text_quality import garbled_share  # noqa: E402

BANDS = [(0, 50), (50, 70), (70, 80), (80, 90), (90, 95), (95, 101)]
_EDGE = re.compile(r"^[\W_]+|[\W_]+$")


def norm(token: str) -> str:
    return _EDGE.sub("", unicodedata.normalize("NFC", token).lower())


def native_words(page: fitz.Page) -> list[str]:
    return [w for w in (norm(t) for t in page.get_text().split()) if w]


def band_of(conf: float) -> str:
    for lo, hi in BANDS:
        if lo <= conf < hi:
            return f"{lo}-{min(hi, 100)}"
    return "?"


def pick_pages(paths: list[Path], per_file: int, total: int, seed: int) -> list[tuple[Path, int]]:
    rng = random.Random(seed)
    chosen: list[tuple[Path, int]] = []
    for path in paths:
        try:
            doc = fitz.open(path)
        except Exception:  # noqa: BLE001 - a broken file is skipped
            continue
        good = [p.number for p in doc
                if len(p.get_text()) >= 800 and garbled_share(p.get_text()) < 0.02]
        rng.shuffle(good)
        chosen += [(path, n) for n in good[:per_file]]
    rng.shuffle(chosen)
    return chosen[:total]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--pages", type=int, default=60)
    ap.add_argument("--per-file", type=int, default=5)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    paths: list[Path] = []
    for item in args.inputs:
        p = Path(item)
        paths += sorted(p.rglob("*.pdf")) if p.is_dir() else [p]
    ocr = TesseractOCR()
    if not ocr.available:
        sys.exit("tesseract with vie+eng is not available (set TESSDATA_PREFIX)")

    sample = pick_pages(paths, args.per_file, args.pages, args.seed)
    words = collections.defaultdict(lambda: [0, 0])     # band -> [correct, total]
    numbers = collections.defaultdict(lambda: [0, 0])
    pages_out = []
    started = time.perf_counter()
    for i, (path, number) in enumerate(sample, start=1):
        page = fitz.open(path)[number]
        reading = ocr.read_page(page)
        truth = collections.Counter(native_words(page))
        truth_numbers = collections.Counter(w for w in truth.elements() if any(c.isdigit() for c in w))
        remaining = truth.copy()
        right = total = 0
        for word in reading.words:
            token = norm(word["text"])
            if not token:
                continue
            ok = remaining[token] > 0
            if ok:
                remaining[token] -= 1
            band = band_of(word["conf"])
            words[band][0] += ok
            words[band][1] += 1
            right += ok
            total += 1
            if any(c.isdigit() for c in token):
                numbers[band][0] += ok
                numbers[band][1] += 1
        found_numbers = collections.Counter(
            t for t in (norm(w["text"]) for w in reading.words) if any(c.isdigit() for c in t))
        recall = (sum((found_numbers & truth_numbers).values()) / sum(truth_numbers.values())) if truth_numbers else None
        pages_out.append({"file": path.name[:40], "page": number + 1, "mean_conf": reading.mean_conf,
                          "word_accuracy": round(right / total, 4) if total else None, "words": total,
                          "number_recall": round(recall, 4) if recall is not None else None,
                          "low_conf_share": reading.low_share})
        print(f"[{i}/{len(sample)}] {path.name[:24]} p{number + 1}: conf {reading.mean_conf:.1f} "
              f"acc {pages_out[-1]['word_accuracy']} numbers {pages_out[-1]['number_recall']}", flush=True)

    def table(counts):
        return {b: {"correct": c, "total": t, "accuracy": round(c / t, 4) if t else None}
                for b, (c, t) in sorted(counts.items(), key=lambda kv: float(kv[0].split("-")[0]))}

    page_bands = collections.defaultdict(list)
    for p in pages_out:
        if p["word_accuracy"] is not None:
            page_bands[band_of(p["mean_conf"])].append(p["word_accuracy"])
    report = {
        "measured": time.strftime("%Y-%m-%d"), "pages": len(pages_out),
        "files": len({p["file"] for p in pages_out}), "seconds": round(time.perf_counter() - started),
        "settings": {"languages": ocr.languages, "dpi": 220, "psm": 6},
        "word_accuracy_by_confidence": table(words),
        "number_accuracy_by_confidence": table(numbers),
        "page_accuracy_by_mean_confidence": {b: {"pages": len(v), "mean_accuracy": round(sum(v) / len(v), 4)}
                                             for b, v in sorted(page_bands.items())},
        "pages_detail": pages_out,
    }
    text = json.dumps(report, ensure_ascii=False, indent=1)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k != "pages_detail"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
