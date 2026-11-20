# ADR 0004 — Change report instead of a rebuilt PDF; text aimed at the grader

Status: proposed — 2026-11-11

## 1. Studio hands back a change report, not a rebuilt PDF

### Context

Studio exported a "clean PDF + appendix" rebuilt from the extracted text. That
file is not the company's report: extraction drops the layout, and on a scanned
page the text is only OCR's reading of an image. Studio also read PDFs without
OCR, so every claim on a scanned page was "not located" and could not be edited
at all, although the analysis had read that page.

### Decision

- The `pdf` export is removed. Every source gets the **change report**
  (`studio/report.py`; PDF, Word and HTML): for each changed paragraph, its page
  in the original, the original and proposed wording with the edit marked, the
  finding GreenScan raised there, and the reason, which is the rule and its basis for an
  accepted suggestion and the reviewer's words for an edit made by hand.
- A paragraph edited by hand has no reason until the reviewer writes one: a new
  log action `note` (`paragraph_key`, `reason`), entered in the export tab.
  Export with reasons missing asks first and prints "Chưa ghi lý do".
- Entries undone by a restore are dropped from the report (restore entries now
  carry `version`; older ones are read from their text).
- Studio reads a PDF as the analysis does: OCR for pages with too little native
  text (cached in `.quantum/ocr_cache`), hidden text left out. An unedited session
  moves to the new reading; an edited one keeps its text and reports the conflict.
- DOCX sources keep the tracked-changes and clean exports, which edit the
  original file in place.

## 2. Text written for the grader

### Context

The company under review writes the report and often supplies the evidence.
The detector was ten substring patterns, applied only to retrieved evidence;
claim text went to the model unfenced; and text a reader cannot see (white on
white, sub-2 pt, invisible over an empty area) was extracted like any other.

The structural defences already held: a model's stance is never decisive, and
SUPPORTED needs a figure or confirming sentence from a document other than the
claim's own. What was missing was keeping such text away from the model and
putting it in front of a person.

### Decision

- `utils/security.py`: five categories (override, chat-role tokens, addressing
  the machine, asking for a verdict, asking to hide), Vietnamese and English,
  matched on a diacritic-keeping copy where Vietnamese words collide ("hãy/hay",
  "đừng/dùng", "AI/ai") and on a folded copy otherwise; zero-width characters,
  Cyrillic/Greek look-alikes and spaced-out letters normalised first.
- `parsers/integrity.py`: hidden spans are removed before chunking (analysis and
  Studio, including table extraction); a page without one parses exactly as before.
- A claim that addresses the grader is never sent to the model; a passage that
  does is excluded; both set `suspected_injection` and require human review.
- The stance prompt (`stance-v2`) fences claim and passage as data with a random
  tag per call and asks the model to report text addressed to it; such an answer
  is replaced by the rules' reading.
- Gate **G8 "Toàn vẹn tài liệu"** holds the run (PENDING_HUMAN_REVIEW) for a
  planted sentence or for background-coloured/invisible text, naming file and page.
  Print below 2 pt alone does not hold it.

### Measured (2026-11-11)

- Patterns on 645 real PDFs, 42,001 pages: 1 page flagged, a law forbidding
  "che giấu thông tin"; that pattern was narrowed, leaving 0. All 18 test
  attacks caught, including obfuscated ones.
- Hidden text on 120 real PDFs, 9,687 pages: 19 files with some, of which 9 had a
  sentence or more. Most was below 2 pt: digital-signature stamps, packshot
  labels, 0.8 pt page thumbnails. That is why tiny print does not hold G8.
  Background-coloured text with a sentence or more: 2 files (a template footer,
  "TABLE UNDER DEVELOPMENT").
- Parsing cost: `get_text("dict")` adds 1–3 s per 100–150-page report.

### Not covered

Text inside images on pages that have native text (it is not read at all; on
scanned pages OCR reads it and the scan applies), PDF metadata and annotations,
and a supplied document that falsely claims to be independent.
Provenance of "external" evidence is a separate decision.
