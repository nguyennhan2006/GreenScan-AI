#!/usr/bin/env python3
"""Package the collected datasets into one folder ready for Kaggle upload.

Three tiers, because the parts of this corpus do not share one legal status:

  metadata  Provenance, coverage, manifests, and sentence-level claim/evidence
            candidates. Short quoted excerpts only. Public-domain regulatory
            originals (SEC orders are US federal works, 17 USC 105; Rechtspraak
            publishes judgments as open data) are included in full.

  derived   (default) metadata + units.jsonl / chunks.jsonl / annotation_pairs,
            which contain full extracted page text of third-party reports.
            Fine for a private dataset or research use; think before making a
            public dataset out of it.

  full      derived + the 3.9 GB of source PDFs. This redistributes copyrighted
            corporate reports. data/real_cases/README.md says the project does
            not do that. Only use with rights you actually hold.

    python tools/package_for_kaggle.py
    python tools/package_for_kaggle.py --tier metadata --out ../greenscan-kaggle
    python tools/package_for_kaggle.py --tier full --zip

The folder gets a dataset-metadata.json so `kaggle datasets create -p <folder>`
works directly. Edit the owner slug in it before uploading.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CRAWL = REPO / "data/crawl"
CASES = REPO / "data/real_cases"

# Regulatory sources that carry no third-party copyright and may be redistributed.
PUBLIC_DOMAIN_ORIGINALS = {
    "KDP_SEC_Order_34-100983.pdf", "KDP_SEC_Press_2024-122.html",
    "BNY_SEC_Order_IA-6032.pdf", "BNY_SEC_Press_2022-86.html",
    "DWS_SEC_Order_IA-6432.pdf", "DWS_SEC_Press_2023-194.html",
    "KLM_Judgment_ECLI-NL-RBAMS-2024-1512.xml",
    "KLM_Judgment_ECLI-NL-RBAMS-2024-1512.html",
}

# Full extracted page text of third-party reports -- excluded from the metadata tier.
FULL_TEXT_FILES = {"units.jsonl", "chunks.jsonl", "annotation_pairs.jsonl"}


def copy(src: Path, dst: Path) -> int:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return src.stat().st_size


def copy_tree(src: Path, dst: Path, skip=lambda p: False) -> tuple[int, int]:
    files = size = 0
    if not src.is_dir():
        return 0, 0
    for p in sorted(src.rglob("*")):
        if not p.is_file() or skip(p):
            continue
        size += copy(p, dst / p.relative_to(src))
        files += 1
    return files, size


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} GB"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", choices=["metadata", "derived", "full"], default="derived")
    ap.add_argument("--out", type=Path, default=REPO.parent / "greenscan-vn-esg-dataset")
    ap.add_argument("--owner", default="YOUR-KAGGLE-USERNAME")
    ap.add_argument("--zip", action="store_true", help="Also produce a .zip next to the folder")
    ap.add_argument("--force", action="store_true", help="Overwrite an existing output folder")
    args = ap.parse_args()

    out = args.out.resolve()
    if out.exists():
        if not args.force:
            print(f"{out} already exists. Pass --force to replace it.", file=sys.stderr)
            return 2
        shutil.rmtree(out)
    out.mkdir(parents=True)

    include_full_text = args.tier in {"derived", "full"}
    include_pdfs = args.tier == "full"
    report: list[tuple[str, int, int]] = []

    # --- 1. Derived VN corpus -------------------------------------------------
    n, s = copy_tree(
        CRAWL / "vn30/normalized", out / "vn30/normalized",
        skip=lambda p: p.name in FULL_TEXT_FILES and not include_full_text,
    )
    report.append(("vn30/normalized", n, s))

    for sub in ("vn30/coverage", "vn30/raw/manifests"):
        n, s = copy_tree(CRAWL / sub, out / sub.replace("raw/", ""))
        report.append((sub.replace("raw/", ""), n, s))

    if include_pdfs:
        n, s = copy_tree(CRAWL / "vn30/raw/objects", out / "vn30/source_pdfs")
        report.append(("vn30/source_pdfs", n, s))

    # --- 2. Labelled real-case pack ------------------------------------------
    for sub in ("cases", "claims", "evidence", "schemas", "training", "reports"):
        n, s = copy_tree(CASES / sub, out / "real_cases" / sub)
        report.append((f"real_cases/{sub}", n, s))

    n, s = copy_tree(CASES / "sources", out / "real_cases/sources",
                     skip=lambda p: p.parent.name == "originals")
    report.append(("real_cases/sources", n, s))

    originals = CASES / "sources/originals"
    if originals.is_dir():
        keep = (lambda p: True) if include_pdfs else (lambda p: p.name in PUBLIC_DOMAIN_ORIGINALS
                                                     or p.name == "download_manifest.json")
        n = s = 0
        for p in sorted(originals.iterdir()):
            if p.is_file() and keep(p):
                s += copy(p, out / "real_cases/sources/originals" / p.name)
                n += 1
        report.append(("real_cases/sources/originals", n, s))

    for name in ("README.md", "LICENSE_AND_USAGE.md"):
        if (CASES / name).is_file():
            copy(CASES / name, out / "real_cases" / name)

    # --- 3. Docs and reproducibility -----------------------------------------
    for src, dst in [
        (CRAWL / "README.md", out / "docs/CRAWL_README.md"),
        (CRAWL / "COLLECTION_REPORT_20260807.md", out / "docs/COLLECTION_REPORT.md"),
        (REPO / "data/README.md", out / "docs/DATA_LAYOUT.md"),
    ]:
        if src.is_file():
            copy(src, dst)

    crawler = REPO / "outside_resource/greenscan_vn30_dataset_crawler_2021_2025"
    for rel in ["configs/companies.yml", "scripts/probe_attachment_hosts.py",
                "scripts/discover_ir_urls.py", "scripts/harvest_js_listings.py",
                "scripts/merge_data_roots.py"]:
        if (crawler / rel).is_file():
            copy(crawler / rel, out / "collection_tools" / Path(rel).name)

    # --- 4. Checksums over everything shipped --------------------------------
    lines = []
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name != "MANIFEST.sha256":
            rel = p.relative_to(out).as_posix()
            lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel}")
    (out / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")

    total = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    count = sum(1 for p in out.rglob("*") if p.is_file())

    # --- 5. Kaggle metadata ---------------------------------------------------
    (out / "dataset-metadata.json").write_text(json.dumps({
        "title": "GreenScan VN — Vietnamese ESG Claim-Evidence Corpus 2021-2025",
        "id": f"{args.owner}/greenscan-vn-esg-claim-evidence-2021-2025",
        "licenses": [{"name": "other"}],
        "keywords": ["nlp", "finance", "sustainability", "vietnamese",
                     "claim-verification", "esg", "greenwashing"],
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    write_readme(out, args.tier, count, total, report)

    print(f"\nTier: {args.tier}")
    for name, n, s in report:
        if n:
            print(f"  {name:34} {n:>5} files  {human(s):>10}")
    print(f"\n  {'TOTAL':34} {count:>5} files  {human(total):>10}")
    print(f"\nFolder: {out}")

    if args.zip:
        archive = shutil.make_archive(str(out), "zip", root_dir=out)
        print(f"Zip   : {archive}  ({human(Path(archive).stat().st_size)})")

    print("\nUpload:")
    print(f"  1. Edit \"id\" in {out / 'dataset-metadata.json'} (replace {args.owner})")
    print(f"  2. kaggle datasets create -p \"{out}\" --dir-mode zip")
    return 0


def write_readme(out: Path, tier: str, count: int, total: int, report) -> None:
    has_pdfs = tier == "full"
    has_text = tier in {"derived", "full"}
    (out / "README.md").write_text(f"""# GreenScan VN — Vietnamese ESG Claim–Evidence Corpus (2021–2025)

Corpus for verifying environmental claims made by Vietnamese listed companies
against evidence in their own reports. Collected {datetime.now(UTC):%Y-%m-%d}.
Package tier: **{tier}** — {count} files, {human(total)}.

## What this is

Two datasets that serve different purposes.

**1. `vn30/` — unlabelled Vietnamese corpus.** 670 documents (442 PDF) from 21
listed companies, 2021–2025, harvested from official investor-relations sites.
Normalised into:

| File | Rows | What it is |
| --- | ---: | --- |
| `documents.jsonl` | 1,061 | Provenance ledger, including failed fetches |
| `claim_candidates.jsonl` | 7,960 | Sentences that look like environmental claims |
| `evidence_candidates.jsonl` | 3,786 | Sentences carrying numeric environmental evidence |
{"| `chunks.jsonl` | 15,658 | ~1800-char passages |" if has_text else ""}
{"| `units.jsonl` | 19,512 | Page-level extracted text |" if has_text else ""}
{"| `annotation_pairs.jsonl` | 39,592 | Top-k claim x evidence pairs to annotate |" if has_text else ""}

**2. `real_cases/` — labelled adjudicated cases.** Four enforcement cases with
regulator or court decisions (Keurig Dr Pepper 2024, BNY Mellon 2022, DWS 2023,
KLM 2024) plus two Vietnamese control documents.

## Temporal splits

2021–2022 `train` · 2023 `dev` · 2024 `test` · 2025 `future_holdout` ·
unknown year `review`.

196 documents have no detected year and land in `review`. **Do not default them
into train.** `leakage_report.json` lists one cross-split duplicate hash; resolve
it before annotating.

## Honest limits

- **These are candidates, not labels.** 7,960 claim candidates come from keyword
  rules. They include navigation boilerplate and need human review. Only
  `real_cases/` carries verified labels, and only 4 pairs so far.
- **No greenwashing labels exist here.** The corpus records what companies said
  and what evidence sits nearby. Absence of evidence is not misconduct.
- **Sector skew.** The 21 companies span 11 sectors but only 2 are high-emission
  (power, construction). No steel, cement or textiles.
- **Coverage is uneven.** 8 companies have documents across 3+ years; the rest
  have less. Older years are thin because IR sites keep only recent filings.
- The SEC matters were settled *without admitting or denying* the findings. Keep
  that qualifier on any quotation.

## Licensing — read before redistributing

Mixed status, and it matters:

- **Derived JSONL** (this package's core) is factual metadata plus extracted
  text. Copyright in the underlying reports stays with the issuers.
- **`real_cases/sources/originals/`** here holds only US SEC orders and press
  releases (US federal works, 17 U.S.C. § 105) and a Netherlands judgment
  published as open data.
{"- **`vn30/source_pdfs/`** contains third-party corporate reports included at the packager's request. Redistributing them may require rights you do not have." if has_pdfs else "- **Source PDFs are deliberately excluded.** Re-run the crawler to obtain them; `MANIFEST.sha256` and `documents.jsonl` carry the SHA-256 of every file so the corpus is reproducible without redistribution."}
{"- **`units.jsonl` / `chunks.jsonl`** reproduce substantial verbatim text from copyrighted reports. Consider a private dataset, or ship the `metadata` tier instead." if has_text else ""}

Collection respected robots.txt and rate limits and bypassed no login, paywall
or anti-bot control.

## Reproducing

`collection_tools/` holds the company config and the four scripts that made this
corpus possible; `docs/COLLECTION_REPORT.md` explains the seven bugs that had to
be fixed first — including a robots.txt handling error that silently discarded
177 public PDFs.
""", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
