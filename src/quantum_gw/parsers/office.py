"""Word and HTML documents, read without extra dependencies.

A sustainability report reaches a reviewer as a PDF more often than not, but
the company's own draft is a Word file, and the draft is what GreenScan Studio
edits. DOCX is a zip of XML, so the standard library reads it; python-docx is
only in the `crawl` extra and the Docker image does not carry it.

Paragraphs are numbered in document order over every `w:p`, table cells
included. Studio writes tracked changes back into the same `w:p` by that
number, so the numbering here and in `studio/export.py` must stay one rule.
"""

from __future__ import annotations

import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"


def paragraph_text(p: ET.Element) -> str:
    """Visible text of one `w:p`; deleted runs (`w:del`) are not part of it."""
    parts: list[str] = []
    for node in p.iter():
        if node.tag == f"{W}t":
            parts.append(node.text or "")
        elif node.tag == f"{W}tab":
            parts.append("\t")
        elif node.tag in {f"{W}br", f"{W}cr"}:
            parts.append(" ")
        elif node.tag == f"{W}delText":
            continue
    return "".join(parts)


def read_docx_xml(path: str | Path) -> ET.Element:
    with zipfile.ZipFile(path) as z:
        return ET.fromstring(z.read("word/document.xml"))


def docx_paragraphs(path: str | Path) -> list[dict]:
    """Every `w:p` in document order: index, text, style, whether it sits in a table."""
    root = read_docx_xml(path)
    body = root.find(f"{W}body")
    if body is None:
        return []
    in_table = {id(p) for tbl in body.iter(f"{W}tbl") for p in tbl.iter(f"{W}p")}
    out = []
    for index, p in enumerate(body.iter(f"{W}p")):
        style = p.find(f"{W}pPr/{W}pStyle")
        out.append({
            "index": index,
            "text": paragraph_text(p),
            "style": style.get(f"{W}val") if style is not None else "",
            "in_table": id(p) in in_table,
        })
    return out


def docx_text(path: str | Path) -> str:
    """Analysis text: one paragraph per block, table rows as `a | b | c` under TABLE."""
    root = read_docx_xml(path)
    body = root.find(f"{W}body")
    if body is None:
        return ""
    blocks: list[str] = []
    for child in body:
        if child.tag == f"{W}p":
            text = paragraph_text(child).strip()
            if text:
                blocks.append(text)
        elif child.tag == f"{W}tbl":
            rows = []
            for tr in child.iter(f"{W}tr"):
                cells = [" ".join(paragraph_text(p).strip() for p in tc.iter(f"{W}p")).strip()
                         for tc in tr.iter(f"{W}tc")]
                if any(cells):
                    rows.append(" | ".join(cells))
            if rows:
                blocks.append("TABLE\n" + "\n".join(rows))
    return "\n\n".join(blocks)


_BLOCK_TAGS = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "table", "td", "th"}
_SKIP_TAGS = {"script", "style", "noscript", "nav", "footer", "header", "svg"}


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP_TAGS:
            self.skip += 1
        elif tag in _BLOCK_TAGS:
            self.parts.append("\n\n" if tag not in {"td", "th", "br"} else (" | " if tag != "br" else "\n"))

    def handle_endtag(self, tag):
        if tag in _SKIP_TAGS and self.skip:
            self.skip -= 1
        elif tag in _BLOCK_TAGS:
            self.parts.append("\n\n" if tag not in {"td", "th"} else "")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    text = "".join(parser.parts)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()
