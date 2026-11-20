import sys
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
d = Document(sys.argv[1] if len(sys.argv) > 1 else "ref_default.docx")
def font(st, name="Times New Roman", size=None, bold=None, color=None, italic=None):
    f = st.font; f.name = name
    rpr = st.element.get_or_add_rPr(); rf = rpr.find(qn("w:rFonts"))
    if rf is None: rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): rf.set(qn(a), name)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
    if size: f.size = Pt(size)
    if bold is not None: f.bold = bold
    if italic is not None: f.italic = italic
    if color: f.color.rgb = RGBColor.from_string(color)
S = d.styles
for n in ("Normal", "Body Text", "First Paragraph", "Compact"):
    if n in [s.name for s in S]:
        st = S[n]; font(st, size=13)
        pf = st.paragraph_format; pf.line_spacing = 1.3; pf.space_after = Pt(6); pf.space_before = Pt(0)
        if n != "Compact": pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
for n, sz, col in (("Title", 22, "1B4332"), ("Subtitle", 14, "2D6A4F"), ("Heading 1", 17, "1B4332"), ("Heading 2", 14.5, "2D6A4F"),
                   ("Heading 3", 13.5, "2D6A4F"), ("Heading 4", 13, "40916C")):
    st = S[n]; font(st, size=sz, bold=True, color=col, italic=False)
    pf = st.paragraph_format; pf.space_before = Pt(14 if n == "Heading 1" else 10); pf.space_after = Pt(6); pf.keep_with_next = True
    if n in ("Title", "Subtitle"): pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
for n in ("Source Code", "Verbatim Char"):
    if n in [s.name for s in S]:
        font(S[n], name="Consolas", size=9)
names = [x.name for x in S]
if "Source Code" in names:
  st = S["Source Code"]; pf = st.paragraph_format; pf.line_spacing = 1.0; pf.space_after = Pt(0); pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
  ppr = st.element.get_or_add_pPr(); shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), "F1F5F2"); ppr.append(shd)
for n in ("Block Text",):
    font(S[n], size=12, italic=False, color="1F2937")
for n in ("Caption", "Image Caption", "Table Caption"):
    if n in [s.name for s in S]: font(S[n], size=11.5, italic=True, color="374151")
sec = d.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = Cm(3), Cm(2), Cm(2.5), Cm(2.5)
d.save(sys.argv[2] if len(sys.argv) > 2 else "ref.docx"); print("ref ok", [s.name for s in S if s.type == 1][:40])
