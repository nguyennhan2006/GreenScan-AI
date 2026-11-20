"""Text a reader cannot see, removed before it can become a claim or evidence.

A PDF can carry text that every extractor returns and no reader ever sees:
white on white, a 0.5 pt line, an invisible layer over an empty margin. It is
the cheapest way to slip a sentence to an automated grader ("Gửi hệ thống AI:
…") or to plant a confirming sentence in a certificate. Such text must not
become a claim or a passage of evidence, and its presence is reported on gate
G8 (agents/reviewer.py) so a person looks at the page.

A text span is hidden when

- its font size is below 2 pt; or
- it is drawn invisibly (opacity 0, render mode 3) over an empty area. An OCR
  text layer is invisible too, but it lies over the scanned image, which is not
  empty, so it is kept; or
- it is drawn in a light colour and the rendered page is uniform under it:
  white on white is hidden, white on a green banner is visible and kept.

The last two need the page rendered (72 dpi, greyscale), which happens only on
pages that have such a candidate. A page without a hidden span keeps
`page.get_text("blocks")` unchanged, so ordinary documents parse exactly as
before. Text placed outside the page is already clipped by the extractor.
"""

from __future__ import annotations

import fitz

MIN_SIZE = 2.0     # points; nobody reads smaller print
LIGHT = 0.85       # relative luminance from which a colour may vanish on paper
CONTRAST = 16      # grey levels; less than this under a span means nothing shows
DPI = 72

REASONS = {
    "tiny": "chữ cỡ dưới 2 pt",
    "invisible": "chữ vô hình trên vùng trống",
    "same_colour": "chữ cùng màu với nền",
}


def _luminance(color: int) -> float:
    r, g, b = (color >> 16) & 255, (color >> 8) & 255, color & 255
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255


def _uniform(samples: bytes, width: int, height: int, stride: int, bbox, origin) -> bool:
    """True when the rendered pixels under `bbox` hardly vary: nothing is visible there."""
    scale = DPI / 72
    x0 = max(0, int((bbox[0] - origin[0]) * scale))
    x1 = min(width, int((bbox[2] - origin[0]) * scale + 0.999))
    y0 = max(0, int((bbox[1] - origin[1]) * scale))
    y1 = min(height, int((bbox[3] - origin[1]) * scale + 0.999))
    if x1 <= x0 or y1 <= y0:
        return True
    lo, hi = 255, 0
    for y in range(y0, y1):
        row = samples[y * stride + x0: y * stride + x1]
        lo, hi = min(lo, min(row)), max(hi, max(row))
        if hi - lo >= CONTRAST:
            return False
    return True


def hidden_spans(page: fitz.Page) -> list[dict]:
    """`{"page", "reason", "label", "text", "bbox"}` for every span on `page` a reader cannot see."""
    found: list[dict] = []
    candidates: list[tuple[dict, str]] = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if not span.get("text", "").strip():
                    continue
                if span.get("size", MIN_SIZE) < MIN_SIZE:
                    found.append(_record(page, span, "tiny"))
                elif span.get("alpha", 255) == 0:
                    candidates.append((span, "invisible"))
                elif _luminance(int(span.get("color", 0))) >= LIGHT:
                    candidates.append((span, "same_colour"))
    if candidates:
        pix = page.get_pixmap(dpi=DPI, colorspace=fitz.csGRAY, alpha=False)
        samples, origin = pix.samples, (page.rect.x0, page.rect.y0)
        for span, reason in candidates:
            if _uniform(samples, pix.width, pix.height, pix.stride, span["bbox"], origin):
                found.append(_record(page, span, reason))
    return found


def _record(page: fitz.Page, span: dict, reason: str) -> dict:
    return {"page": page.number + 1, "reason": reason, "label": REASONS[reason], "text": span["text"],
            "bbox": [round(v, 1) for v in span["bbox"]]}


def inside(bbox, rect) -> bool:
    x, y = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
    return rect[0] - 1 <= x <= rect[2] + 1 and rect[1] - 1 <= y <= rect[3] + 1


def visible_blocks(page: fitz.Page) -> tuple[list[tuple], list[dict]]:
    """`page.get_text("blocks")` without the hidden spans, and the spans removed."""
    blocks = page.get_text("blocks")
    hidden = hidden_spans(page)
    if not hidden:
        return blocks, []
    out = []
    for block in blocks:
        if block[6] != 0:
            out.append(block)
            continue
        text = block[4]
        for span in hidden:
            if inside(span["bbox"], block[:4]) and span["text"] in text:
                text = text.replace(span["text"], "", 1)
        lines = [line for line in text.split("\n") if line.strip()]
        if lines:
            out.append((*block[:4], "\n".join(lines) + "\n", *block[5:]))
    return out, hidden


def merge(hidden: list[dict]) -> list[dict]:
    """One record per page and reason, with the hidden words joined: what a reviewer reads."""
    by_key: dict[tuple[int, str], dict] = {}
    for span in hidden:
        key = (span["page"], span["reason"])
        if key not in by_key:
            by_key[key] = {"page": span["page"], "reason": span["reason"], "label": span["label"], "text": "",
                           "bboxes": []}
        record = by_key[key]
        record["text"] = (record["text"] + " " + span["text"].strip()).strip()
        record["bboxes"].append(span["bbox"])
    return list(by_key.values())
