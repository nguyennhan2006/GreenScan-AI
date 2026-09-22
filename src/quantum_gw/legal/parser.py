"""L1 — break a Vietnamese legal document into its own structure.

Fixed-size chunking is wrong for statutes. A 500-token window happily cuts
through the middle of:

    Điều 4
     └── khoản 2
           ├── điểm a
           ├── điểm b
           └── điểm c

which destroys exactly the boundary a legal citation depends on. A retrieved
fragment that ends mid-condition cannot be cited, and a condition split across
two chunks can be silently half-evaluated.

So the unit here is the clause, addressed by its legal path:

    QD21-2025:article_3:paragraph_2:item_b

Nothing in this module infers, summarises or rewrites legal text. It only
segments what is already there and records where each piece came from.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field

# Vietnamese legal ordinals. Written to tolerate the ways real documents differ:
# "Điều 3." / "Điều 3:" / "Điều 3 -", and paragraph numbers that begin a line.
ARTICLE_RE = re.compile(r"^\s*Điều\s+(\d+)\s*[.:\-–]?\s*(.*)$", re.M)
CHAPTER_RE = re.compile(r"^\s*Chương\s+([IVXLC]+|\d+)\s*[.:\-–]?\s*(.*)$", re.M | re.I)
SECTION_RE = re.compile(r"^\s*Mục\s+(\d+)\s*[.:\-–]?\s*(.*)$", re.M)
# A paragraph opens with "1." / "2)" at line start.
PARAGRAPH_RE = re.compile(r"^\s*(\d{1,2})\s*[.)]\s+(?=\S)", re.M)
# An item opens with "a)" / "b." — single Vietnamese letter.
ITEM_RE = re.compile(r"^\s*([a-zăâđêôơư])\s*[.)]\s+(?=\S)", re.M | re.I)
ANNEX_RE = re.compile(r"^\s*(PHỤ\s+LỤC|Phụ\s+lục)\s+([IVXLC]+|\d+)?\s*[.:\-–]?\s*(.*)$", re.M)


@dataclass
class Clause:
    clause_id: str
    document_id: str
    text: str
    chapter: str | None = None
    section: str | None = None
    article: int | None = None
    paragraph: int | None = None
    item: str | None = None
    annex: str | None = None
    heading: str | None = None
    parent_path: list[str] = field(default_factory=list)
    char_start: int = 0
    char_end: int = 0

    def to_json(self) -> dict:
        return asdict(self)

    @property
    def citation(self) -> str:
        """Human-readable citation, in the order a Vietnamese lawyer reads it."""
        bits = []
        if self.annex:
            bits.append(f"Phụ lục {self.annex}")
        if self.article is not None:
            bits.append(f"Điều {self.article}")
        if self.paragraph is not None:
            bits.append(f"khoản {self.paragraph}")
        if self.item:
            bits.append(f"điểm {self.item}")
        return ", ".join(bits) or "toàn văn"


def normalise(text: str) -> str:
    """NFC + collapse spaces, without touching line structure.

    Line breaks carry the ordinal structure, so they survive; only intra-line
    whitespace and the separator characters that break JSONL readers are folded.
    """
    text = unicodedata.normalize("NFC", text or "")
    text = text.replace(chr(0x2028), "\n").replace(chr(0x2029), "\n").replace(chr(0x85), "\n")
    text = re.sub(r"[ \t ]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _split_by(pattern: re.Pattern, text: str) -> list[tuple[str, str, int]]:
    """[(marker, body, offset)] for every match of `pattern`, in order."""
    matches = list(pattern.finditer(text))
    out = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((m.group(1), text[m.end():end].strip(), m.start()))
    return out


def parse_document(document_id: str, raw_text: str) -> list[Clause]:
    """Segment a statute into clauses at its own legal boundaries.

    Emits the deepest available level: an article whose paragraphs contain items
    yields item-level clauses, not the whole article, so retrieval can return
    exactly the condition that matters. Every level keeps `parent_path` so a
    reviewer can always walk back up to the full article.
    """
    text = normalise(raw_text)
    if not text:
        return []

    clauses: list[Clause] = []
    annexes = list(ANNEX_RE.finditer(text))
    body_end = annexes[0].start() if annexes else len(text)

    # ---- chapter / section context, resolved by position ----
    chapters = [(m.group(1), m.start()) for m in CHAPTER_RE.finditer(text[:body_end])]
    sections = [(m.group(1), m.start()) for m in SECTION_RE.finditer(text[:body_end])]

    def context_at(offset: int) -> tuple[str | None, str | None]:
        chapter = next((c for c, s in reversed(chapters) if s <= offset), None)
        section = next((c for c, s in reversed(sections) if s <= offset), None)
        return chapter, section

    # ---- articles ----
    articles = list(ARTICLE_RE.finditer(text[:body_end]))
    for i, m in enumerate(articles):
        number = int(m.group(1))
        heading = m.group(2).strip() or None
        start = m.end()
        end = articles[i + 1].start() if i + 1 < len(articles) else body_end
        body = text[start:end].strip()
        chapter, section = context_at(m.start())
        base = f"{document_id}:article_{number}"

        paragraphs = _split_by(PARAGRAPH_RE, body)
        if not paragraphs:
            clauses.append(Clause(
                clause_id=base, document_id=document_id, text=body, chapter=chapter,
                section=section, article=number, heading=heading,
                parent_path=[document_id], char_start=start, char_end=end,
            ))
            continue

        for p_marker, p_body, p_offset in paragraphs:
            p_num = int(p_marker)
            p_id = f"{base}:paragraph_{p_num}"
            items = _split_by(ITEM_RE, p_body)
            if not items:
                clauses.append(Clause(
                    clause_id=p_id, document_id=document_id, text=p_body, chapter=chapter,
                    section=section, article=number, paragraph=p_num, heading=heading,
                    parent_path=[document_id, base], char_start=start + p_offset,
                    char_end=start + p_offset + len(p_body),
                ))
                continue
            # Text before the first item still belongs to the paragraph: it is
            # usually the stem the items complete, so dropping it would leave
            # every item grammatically orphaned.
            stem = p_body[: items[0][2]].strip()
            if stem:
                clauses.append(Clause(
                    clause_id=p_id, document_id=document_id, text=stem, chapter=chapter,
                    section=section, article=number, paragraph=p_num, heading=heading,
                    parent_path=[document_id, base], char_start=start + p_offset,
                    char_end=start + p_offset + len(stem),
                ))
            for i_marker, i_body, i_offset in items:
                clauses.append(Clause(
                    clause_id=f"{p_id}:item_{i_marker.lower()}", document_id=document_id,
                    text=i_body, chapter=chapter, section=section, article=number,
                    paragraph=p_num, item=i_marker.lower(), heading=heading,
                    parent_path=[document_id, base, p_id],
                    char_start=start + p_offset + i_offset,
                    char_end=start + p_offset + i_offset + len(i_body),
                ))

    # ---- annexes: criteria tables usually live here ----
    for i, m in enumerate(annexes):
        label = (m.group(2) or str(i + 1)).strip()
        heading = m.group(3).strip() or None
        start = m.end()
        end = annexes[i + 1].start() if i + 1 < len(annexes) else len(text)
        body = text[start:end].strip()
        a_id = f"{document_id}:annex_{label}"
        paragraphs = _split_by(PARAGRAPH_RE, body)
        if not paragraphs:
            clauses.append(Clause(
                clause_id=a_id, document_id=document_id, text=body, annex=label,
                heading=heading, parent_path=[document_id],
                char_start=start, char_end=end,
            ))
            continue
        # Annexes are usually criteria TABLES, and numbering restarts on every
        # row or sub-section: Phụ lục I of 21/2025/QĐ-TTg repeats "2." 27 times.
        # Numbering them as khoản both collides on clause_id and misdescribes a
        # table row as a paragraph of the decision. Use a running ordinal for the
        # address and keep the printed number as `paragraph` for display.
        for seq, (p_marker, p_body, p_offset) in enumerate(paragraphs, start=1):
            clauses.append(Clause(
                clause_id=f"{a_id}:item_{seq:03d}", document_id=document_id,
                text=p_body, annex=label, paragraph=int(p_marker), heading=heading,
                parent_path=[document_id, a_id], char_start=start + p_offset,
                char_end=start + p_offset + len(p_body),
            ))

    return _ensure_unique_ids(clauses)


def _ensure_unique_ids(clauses: list[Clause]) -> list[Clause]:
    """Guarantee `clause_id` is unique across the document.

    `clause_id` is the citation key a rule binds to, so two clauses sharing one
    makes the binding ambiguous — the rule engine would resolve to whichever
    happened to be first.

    Collisions are real in practice, not hypothetical: a table of contents lists
    "Điều 1" before the article itself, and running headers repeat an article
    number on every page. Distinguishing a TOC line from the operative text is
    unreliable, so nothing is dropped — later occurrences get an explicit
    `#n` suffix and remain fully addressable for review.
    """
    seen: dict[str, int] = {}
    for clause in clauses:
        base = clause.clause_id
        count = seen.get(base, 0) + 1
        seen[base] = count
        if count > 1:
            clause.clause_id = f"{base}#{count}"
    return clauses


def duplicate_id_report(clauses: list[Clause]) -> dict[str, int]:
    """Base ids that occurred more than once, for review after parsing."""
    counts: dict[str, int] = {}
    for c in clauses:
        base = c.clause_id.split("#")[0]
        counts[base] = counts.get(base, 0) + 1
    return {k: v for k, v in counts.items() if v > 1}


def structure_summary(clauses: list[Clause]) -> dict:
    return {
        "clauses": len(clauses),
        "articles": len({c.article for c in clauses if c.article is not None}),
        "with_paragraph": sum(1 for c in clauses if c.paragraph is not None),
        "with_item": sum(1 for c in clauses if c.item),
        "annexes": len({c.annex for c in clauses if c.annex}),
        "chapters": len({c.chapter for c in clauses if c.chapter}),
    }
