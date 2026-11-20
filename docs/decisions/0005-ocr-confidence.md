# ADR 0005 — How sure the system is of what it read: OCR confidence, measured and enforced

Status: proposed — 2026-11-11

## Context

A scanned page reaches the analysis only as Tesseract's reading of an image.
Until now that reading carried no measure of its own reliability: a "30%" read
as "80%" produced a confident CONTRADICTED, and nothing in result.json, the
gates or the Studio report told a reviewer that the figure came from OCR, let
alone how sure OCR was. Two more gaps showed up while measuring:

* `read_page` asked Tesseract for its `txt tsv` config files. Those live under
  `TESSDATA_PREFIX/configs`; the GreenScan tessdata folder holds only the
  language models, so Tesseract silently wrote the text alone. Every word
  confidence was missing (all 60 pages of the first calibration run read 0).
  The outputs are now requested as variables
  (`-c tessedit_create_txt=1 -c tessedit_create_tsv=1`), which need no file.
* A PDF typeset in a legacy Vietnamese font (TCVN3, VNI) has a text layer that
  extracts as "hi~u lµc", "Bé Tµi chÝnh". Every character is a valid code point,
  so the page was never sent to OCR and the analysis read mojibake.

## Measurement

`tools/measure_ocr_confidence.py` grades OCR against pages whose true text is
known: born-digital pages (at least 800 characters, under 2% garbled words),
rendered at the pipeline's 220 dpi and read with its settings (vie+eng, psm 6).
An OCR word counts as right when it occurs among the page's own words
(multiset, order-free). Run of 2026-11-11: 60 pages from 52 VN30 reports,
187 s; raw output in `benchmark/ocr_calibration_2026-11-11.json`.

| Tesseract confidence | Words right | Numbers right |
|---|---|---|
| 0–50 | 7.8% of 3,328 | 11.7% of 514 |
| 50–70 | 16.2% of 1,479 | 18.6% of 354 |
| 70–80 | 30.6% of 891 | 21.3% of 202 |
| 80–90 | 49.8% of 1,633 | 47.9% of 332 |
| 90–95 | 77.1% of 4,758 | 82.7% of 591 |
| 95–100 | 91.5% of 22,376 | 91.1% of 1,092 |

| Page mean confidence | Pages | Mean share of words right |
|---|---|---|
| below 50 | 2 | 9.7% |
| 50–70 | 2 | 13.5% |
| 70–80 | 3 | 55.1% |
| 80–90 | 25 | 74.2% |
| 90–95 | 25 | 83.7% |
| 95–100 | 3 | 97.5% |

Median page: confidence 89.4, 81% of words right, 85% of the page's numbers
found.

These shares are lower bounds. Text inside images (diagrams, infographics) is
read by OCR but absent from the text layer, so it counts as wrong; table rules
are read as "=", "—" or "1". The ordering by confidence is what the thresholds
rest on, and it is monotonic in every column.

Confidence misses one error class that matters here: stylised upper-case
Vietnamese loses its diacritics with high confidence ("CHIEN LUOC PHAT TRIEN
BEN VUNG" at 91–97). Numbers carry no diacritics, so the number thresholds are
unaffected; for words, confidence is necessary but not sufficient.

## Decision

1. **Thresholds** (`parsers/ocr.py`), read off the tables:
   * `LOW_NUMBER_CONF = 90`. Below it a number was right at most 48% of the
     time; from 90 it was right 83–91%.
   * `LOW_WORD_CONF = 80`. Below it a word was right at most 31% of the time.
     `ocr_low_share` is the share of such words on a page.
   * `LOW_PAGE_CONF = 80`. Pages below it matched their text on 55% of words
     or fewer. Only 7 of 60 pages fell there, so this cut is the least
     supported of the three.
2. **Recorded per page and per passage.** Each OCR'd or garbled page gets a
   record (`AnalysisResult.reading`): mean confidence, low-confidence share,
   doubtful numbers, garbled share, and `unread` for a scan or garbled page
   that no OCR could read. Each passage keeps only the doubtful numbers it
   contains; each claim from an OCR'd page carries the page confidence and its
   own doubtful numbers.
3. **A doubtful number decides nothing.** A numeric SUPPORTS or CONTRADICTS
   whose compared values include a doubtful number (any of the claim's, or one
   of the passage's that is actually compared) becomes PARTIAL with the number
   named, and the verification is marked `doubtful_reading`, which the scorer
   counts towards human review (`agents/verifier.py` `_unless_misread`).
4. **Gate G9 "Chất lượng đọc tài liệu"** lists OCR pages with their confidence
   range, weak pages, garbled pages, unread pages and claims resting on doubtful
   numbers. It holds the release only for unread pages and doubtful numbers:
   a weak page is reported, and its numbers are already kept out of verdicts.
5. **Garbled text layers are read by OCR** when 15% or more of a page's words
   are garbled (`parsers/text_quality.py`), in the analysis and in Studio alike.
6. **Studio** caches OCR readings with their measures, and the change report
   gives each paragraph from an OCR'd page its confidence and doubtful numbers.

## Not decided here: a second reader

Confidence says where OCR may be wrong; it cannot say what the right reading
is, and it misses diacritic loss. A second reader on the few regions that
matter (doubtful numbers that a claim or a compared passage depends on) would
close both gaps: crop the word box from the 220 dpi render (the boxes are
already in page points), and ask a vision-language model or a second OCR
engine for the digits. Agreement lifts the doubt; disagreement goes to a
person with both readings; neither ever replaces the text silently. None of
the configured providers takes images today, and a cloud model would see
document images, which document class C forbids. Options: a local VLM in the
`gpu` profile, or a cloud model limited to class A documents. To be decided
with its cost measured on the doubtful-number counts this ADR now records.

## Consequences

* Verdicts on scanned reports move from SUPPORTED/CONTRADICTED to PARTIAL
  wherever they rested on a doubtful number. That is the intended trade: fewer
  automatic verdicts, none of them about the scanner.
* result.json is unchanged for born-digital input: every new field is written
  only when set.
* Re-run `tools/measure_ocr_confidence.py` on real scans (not rendered
  born-digital pages) before relying on the page threshold; real scans will
  score lower.
