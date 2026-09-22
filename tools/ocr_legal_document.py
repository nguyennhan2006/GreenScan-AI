#!/usr/bin/env python3
"""OCR a scanned legal original, keeping the OCR output separate from the source.

Authoritative Vietnamese legal PDFs are frequently scans of the signed copy —
21/2025/QĐ-TTg is 32 pages carrying 148 characters of text, all of it the
digital-signature block. Without OCR no clause of it can be cited.

Two rules this enforces:

* **The original is never modified.** OCR text is written beside it as
  `ocr.txt`, with `ocr_used`, engine version, languages and per-page confidence
  in `ocr_metadata.json`. A later reader can always tell whether a clause came
  from a text layer or from a recognition model.
* **OCR text is lower-trust than a text layer.** Diacritics are where Vietnamese
  OCR fails, and a wrong dấu changes the word. The metadata records mean
  confidence per page so review can target the weak pages.

    python tools/ocr_legal_document.py --id QD21-2025-QD-TTg
    python tools/ocr_legal_document.py --pdf data/legal/raw/X/signed.pdf --out data/legal/raw/X
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

REGISTRY = REPO / "configs/legal/LEGAL_SOURCE_REGISTRY.yaml"
RAW = REPO / "data/legal/raw"

DEFAULT_TESSERACT_DIRS = [
    r"C:\Program Files\Tesseract-OCR",
    r"C:\Program Files (x86)\Tesseract-OCR",
]


def find_tesseract() -> str | None:
    exe = shutil.which("tesseract")
    if exe:
        return exe
    for d in DEFAULT_TESSERACT_DIRS:
        candidate = Path(d) / "tesseract.exe"
        if candidate.is_file():
            return str(candidate)
    return None


def tessdata_prefix() -> str | None:
    """Where the language files live.

    The winget installer writes to Program Files, which a non-elevated process
    cannot add `vie.traineddata` to, so the user-local copy is checked first.
    """
    env = os.environ.get("TESSDATA_PREFIX")
    if env and (Path(env) / "vie.traineddata").is_file():
        return env
    local = Path.home() / "tessdata"
    if (local / "vie.traineddata").is_file():
        return str(local)
    for d in DEFAULT_TESSERACT_DIRS:
        if (Path(d) / "tessdata" / "vie.traineddata").is_file():
            return str(Path(d) / "tessdata")
    return None


def ocr_pdf(pdf: Path, out_dir: Path, langs: str, dpi: int, exe: str,
            prefix: str | None) -> dict:
    import fitz

    env = {**os.environ}
    if prefix:
        env["TESSDATA_PREFIX"] = prefix

    pages: list[dict] = []
    chunks: list[str] = []
    with fitz.open(pdf) as doc:
        total = doc.page_count
        for i, page in enumerate(doc, start=1):
            png = out_dir / f".page-{i:03d}.png"
            page.get_pixmap(dpi=dpi).save(png)
            # TSV gives per-word confidence, which is what makes weak pages
            # findable instead of hidden inside one big blob of text.
            #
            # Use `-c tessedit_create_tsv=1`, not the `tsv` config-file argument:
            # as a positional it is silently ignored when options follow it, and
            # placing it before `-l` drops the language entirely — the output
            # then comes back as unaccented English ("Gti van ban"), which looks
            # like bad OCR rather than a wrong command.
            r = subprocess.run(
                [exe, str(png), "stdout", "-l", langs, "--psm", "3",
                 "-c", "tessedit_create_tsv=1"],
                capture_output=True, encoding="utf-8", errors="replace", env=env,
            )
            # Rebuild physical lines from the TSV geometry columns.
            #
            # Joining every word with a space instead destroys the line breaks,
            # and the clause parser anchors on them: `^Điều \d+`, `^\d+\.`,
            # `^[a-z])`. Flattened text yielded 5 clauses from 62,000 characters
            # of a decision that plainly contains far more.
            confs = []
            lines: dict[tuple[int, int, int], list[str]] = {}
            for row in r.stdout.split("\n")[1:]:
                cols = row.split("\t")
                if len(cols) < 12 or not cols[11].strip():
                    continue
                try:
                    conf = float(cols[10])
                    key = (int(cols[2]), int(cols[3]), int(cols[4]))  # block, par, line
                except ValueError:
                    continue
                if conf < 0:
                    continue
                confs.append(conf)
                lines.setdefault(key, []).append(cols[11])
            words = [w for ws in lines.values() for w in ws]
            text = "\n".join(" ".join(ws) for _, ws in sorted(lines.items()))
            chunks.append(text)
            pages.append({
                "page": i, "words": len(words),
                "mean_confidence": round(sum(confs) / len(confs), 2) if confs else 0.0,
                "chars": len(text),
            })
            png.unlink(missing_ok=True)
            print(f"    page {i:>3}/{total}  {len(words):>5} words  "
                  f"conf {pages[-1]['mean_confidence']:>5.1f}")
    return {"pages": pages, "text": "\n\n".join(chunks)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", help="document id from the legal source registry")
    ap.add_argument("--all-scanned", action="store_true",
                    help="OCR every registry entry marked scanned_no_text")
    ap.add_argument("--pdf", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--langs", default="vie+eng")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--update-registry", action="store_true")
    args = ap.parse_args()

    if args.all_scanned:
        # Every datafiles.chinhphu.vn signed PDF observed so far is a scan, so
        # this is the normal path rather than an exception.
        reg = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        pending = [e["id"] for e in reg["documents"]
                   if e.get("text_acquisition") == "scanned_no_text"]
        print(f"{len(pending)} scanned document(s) to OCR: {pending}\n")
        failures = []
        for doc_id in pending:
            rc = subprocess.call(
                [sys.executable, __file__, "--id", doc_id, "--langs", args.langs,
                 "--dpi", str(args.dpi)] + (["--update-registry"] if args.update_registry else []),
            )
            if rc != 0:
                failures.append(doc_id)
        print(f"\nOCR complete. Failed: {failures or 'none'}")
        return 1 if failures else 0

    exe = find_tesseract()
    if not exe:
        print("tesseract not found. Install it, e.g.\n"
              "  winget install --id UB-Mannheim.TesseractOCR --source winget",
              file=sys.stderr)
        return 2
    prefix = tessdata_prefix()
    if "vie" in args.langs and not prefix:
        print("vie.traineddata not found. Download it from tessdata_best and put it in\n"
              "  %USERPROFILE%\\tessdata\\vie.traineddata", file=sys.stderr)
        return 2

    if args.id:
        raw = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        entry = next((e for e in raw["documents"] if e["id"] == args.id), None)
        if entry is None:
            print(f"{args.id} is not in the registry", file=sys.stderr)
            return 2
        out_dir = args.out or (RAW / args.id)
        pdf = args.pdf or next((p for p in out_dir.glob("*.pdf")), None)
    else:
        raw = entry = None
        pdf, out_dir = args.pdf, args.out
    if not pdf or not Path(pdf).is_file():
        print(f"No source PDF found ({pdf})", file=sys.stderr)
        return 2

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    version = subprocess.run([exe, "--version"], capture_output=True,
                             encoding="utf-8", errors="replace").stdout.split("\n")[0].strip()
    print(f"OCR {pdf.name}  langs={args.langs}  dpi={args.dpi}\n  {version}")

    result = ocr_pdf(Path(pdf), out_dir, args.langs, args.dpi, exe, prefix)
    text = result["text"]

    # Beside the original, never over it.
    (out_dir / "ocr.txt").write_text(text, encoding="utf-8")
    confs = [p["mean_confidence"] for p in result["pages"] if p["words"]]
    meta = {
        "ocr_used": True,
        "engine": version,
        "languages": args.langs,
        "dpi": args.dpi,
        "tessdata_prefix": prefix,
        "pages": len(result["pages"]),
        "total_chars": len(text),
        "mean_confidence": round(sum(confs) / len(confs), 2) if confs else 0.0,
        "low_confidence_pages": [p["page"] for p in result["pages"]
                                 if p["words"] and p["mean_confidence"] < 75],
        "per_page": result["pages"],
        "ocr_at": datetime.now(UTC).isoformat(),
        "source_pdf": str(Path(pdf).relative_to(REPO)),
        "note": ("OCR output, not a publisher text layer. Diacritics are the weak "
                 "point for Vietnamese; verify low-confidence pages before citing."),
    }
    (out_dir / "ocr_metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n  chars {len(text):,}  mean confidence {meta['mean_confidence']}")
    print(f"  low-confidence pages: {meta['low_confidence_pages'] or 'none'}")
    print(f"  wrote {out_dir / 'ocr.txt'}")

    # A failed run must never be recorded as usable text. Marking an empty OCR
    # `ok` would let the checker cite a document nobody can read -- exactly the
    # failure the acquisition status exists to prevent.
    healthy = len(text) > 200 * len(result["pages"]) and meta["mean_confidence"] >= 60
    if not healthy:
        print("\n  OCR FAILED health check "
              f"({len(text):,} chars over {len(result['pages'])} pages, "
              f"confidence {meta['mean_confidence']}). Registry NOT updated.")
        return 1

    if args.update_registry and entry is not None:
        entry["text_acquisition"] = "ok_ocr"
        entry["ocr_used"] = True
        entry["text_acquisition_note"] = (
            f"OCR ({args.langs}, {version}), mean confidence {meta['mean_confidence']}. "
            "Lower trust than a publisher text layer; verify before binding a rule."
        )
        REGISTRY.write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False,
                                           width=100), encoding="utf-8")
        print(f"  updated {REGISTRY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
