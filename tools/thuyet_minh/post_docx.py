"""Style the pandoc output: fonts, tables, code blocks, page breaks before chapters, page numbers.

C:/Python314/python.exe -X utf8 tools/thuyet_minh/post_docx.py <in.docx> <out.docx>
"""
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

d = Document(sys.argv[1])
BODY = "Times New Roman"


def set_font(run_or_style, name, size=None):
    f = run_or_style.font
    f.name = name
    el = run_or_style.element
    rpr = el.get_or_add_rPr() if hasattr(el, "get_or_add_rPr") else el.rPr
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), name)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]
    if size:
        f.size = Pt(size)


def insert_before(parent, child, followers):
    """Insert `child` before the first existing element named in `followers` (schema order), else append."""
    for el in parent:
        if el.tag in {qn(f) for f in followers}:
            el.addprevious(child)
            return child
    parent.append(child)
    return child


PPR_AFTER_SHD = ("w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap", "w:overflowPunct", "w:topLinePunct",
                 "w:autoSpaceDE", "w:autoSpaceDN", "w:bidi", "w:adjustRightInd", "w:snapToGrid", "w:spacing", "w:ind",
                 "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap", "w:jc", "w:textDirection",
                 "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr",
                 "w:pPrChange")


names = {s.name for s in d.styles}
for n in ("Source Code", "Verbatim Char"):
    if n in names:
        set_font(d.styles[n], "Consolas", 8.5)
if "Source Code" in names:
    st = d.styles["Source Code"]
    pf = st.paragraph_format
    pf.line_spacing = 1.0
    pf.space_before = Pt(2)
    pf.space_after = Pt(6)
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    ppr = st.element.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "F2F5F3")
    bdr = OxmlElement("w:pBdr")
    for side in ("top", "left", "bottom", "right"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "4")
        b.set(qn("w:space"), "4")
        b.set(qn("w:color"), "C8D3CC")
        bdr.append(b)
    insert_before(ppr, bdr, ("w:shd",) + PPR_AFTER_SHD)
    insert_before(ppr, shd, PPR_AFTER_SHD)


def cell_shade(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    insert_before(tcpr, shd, ("w:noWrap", "w:tcMar", "w:textDirection", "w:tcFitText", "w:vAlign", "w:hideMark"))


def table_borders(tbl):
    tblpr = tbl._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "4")
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), "9DB4A6")
        borders.append(b)
    for old in tblpr.findall(qn("w:tblBorders")) + tblpr.findall(qn("w:tblCellMar")):
        tblpr.remove(old)
    insert_before(tblpr, borders, ("w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook", "w:tblCaption", "w:tblDescription"))
    mar = OxmlElement("w:tblCellMar")
    for side, w in (("top", 25), ("left", 70), ("bottom", 25), ("right", 70)):
        m = OxmlElement(f"w:{side}")
        m.set(qn("w:w"), str(w))
        m.set(qn("w:type"), "dxa")
        mar.append(m)
    insert_before(tblpr, mar, ("w:tblLook", "w:tblCaption", "w:tblDescription"))


for tbl in d.tables:
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_borders(tbl)
    ncols = len(tbl.columns)
    size = 9.5 if ncols <= 4 else (8.5 if ncols <= 7 else 7.5)
    for r_i, row in enumerate(tbl.rows):
        for cell in row.cells:
            if r_i == 0:
                cell_shade(cell, "DCEBE2")
            for p in cell.paragraphs:
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.05
                for run in p.runs:
                    is_code = run.style is not None and run.style.name == "Verbatim Char"
                    set_font(run, "Consolas" if is_code else BODY, size - (0.5 if is_code else 0))
                    if r_i == 0:
                        run.font.bold = True
    # repeat header row on each page
    trpr = tbl.rows[0]._tr.get_or_add_trPr()
    h = OxmlElement("w:tblHeader")
    h.set(qn("w:val"), "true")
    trpr.append(h)

# page break before every chapter heading except the first one after the TOC
first = True
for p in d.paragraphs:
    if p.style is not None and p.style.name == "Heading 1":
        if first:
            first = False
        else:
            p.paragraph_format.page_break_before = True
    if p.style is not None and p.style.name in ("Image Caption", "Captioned Figure", "Figure"):
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

# page numbers in the footer
sec = d.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = Cm(2.8), Cm(2.0), Cm(2.3), Cm(2.3)
sec.header_distance, sec.footer_distance, sec.gutter = Cm(1.2), Cm(1.2), Cm(0)
fp = sec.footer.paragraphs[0] if sec.footer.paragraphs else sec.footer.add_paragraph()
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = fp.add_run()
for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
    if kind:
        fc = OxmlElement("w:fldChar")
        fc.set(qn("w:fldCharType"), kind)
        run._r.append(fc)
    else:
        it = OxmlElement("w:instrText")
        it.set(qn("xml:space"), "preserve")
        it.text = text
        run._r.append(it)
set_font(run, BODY, 10)
run.font.color.rgb = RGBColor(0x55, 0x65, 0x5C)

d.save(sys.argv[2])
print("styled", sys.argv[2], "tables", len(d.tables), "paragraphs", len(d.paragraphs))
