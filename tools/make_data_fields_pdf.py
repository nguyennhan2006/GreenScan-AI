"""Build the plain-language data-field guide as a PDF.

    python tools/make_data_fields_pdf.py

The technical contract lives in `docs/04-data-ai/DATA_LAYERS.md` and in
`src/quantum_gw/data/layers.py`. This produces the version a customer, an
auditor or a non-engineer teammate reads: what each field means, why it exists,
and what a real value looks like. When the contract changes, change the wording
here too -- two documents that disagree are worse than one.

Fonts: the built-in ReportLab faces have no Vietnamese diacritics, so a system
TrueType font is registered; the script fails loudly rather than producing a
page of black boxes.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "04-data-ai" / "GreenScan_Mo_ta_truong_du_lieu_v1.pdf"

INK = colors.HexColor("#1B2A3A")
MUTED = colors.HexColor("#5B6B7B")
ACCENT = colors.HexColor("#1F7A52")
LIGHT = colors.HexColor("#EDF3F0")
LINE = colors.HexColor("#C9D6CF")
WARN = colors.HexColor("#FFF6E5")

FONT_CANDIDATES = [
    ("Segoe UI", r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\segoeuib.ttf",
     r"C:\Windows\Fonts\segoeuii.ttf"),
    ("Arial", r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf",
     r"C:\Windows\Fonts\ariali.ttf"),
    ("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
]


def register_font() -> tuple[str, str, str]:
    """Register a Unicode font with Vietnamese coverage; raise if none is available."""
    for name, regular, bold, italic in FONT_CANDIDATES:
        if not Path(regular).exists():
            continue
        pdfmetrics.registerFont(TTFont(name, regular))
        bold_name, italic_name = name, name
        if Path(bold).exists():
            bold_name = f"{name}-Bold"
            pdfmetrics.registerFont(TTFont(bold_name, bold))
        if Path(italic).exists():
            italic_name = f"{name}-Italic"
            pdfmetrics.registerFont(TTFont(italic_name, italic))
        pdfmetrics.registerFontFamily(name, normal=name, bold=bold_name, italic=italic_name)
        return name, bold_name, italic_name
    raise SystemExit(
        "No Unicode font with Vietnamese diacritics found. Install DejaVu Sans or run on "
        "Windows, then re-run; the built-in fonts would render the text as black boxes."
    )


BODY, BOLD, ITALIC = register_font()


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName=BOLD, fontSize=25,
                                leading=30, textColor=INK, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontName=BODY, fontSize=12.5,
                                   leading=18, textColor=MUTED, alignment=TA_CENTER),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName=BOLD, fontSize=15.5,
                             leading=20, textColor=ACCENT, spaceBefore=16, spaceAfter=7),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName=BOLD, fontSize=12,
                             leading=16, textColor=INK, spaceBefore=11, spaceAfter=5),
        "body": ParagraphStyle("body", parent=base["Normal"], fontName=BODY, fontSize=10.3,
                               leading=15.5, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6),
        "lead": ParagraphStyle("lead", parent=base["Normal"], fontName=BODY, fontSize=11.4,
                               leading=17.5, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=8),
        "cell": ParagraphStyle("cell", parent=base["Normal"], fontName=BODY, fontSize=8.9,
                               leading=12.6, textColor=INK),
        "cellb": ParagraphStyle("cellb", parent=base["Normal"], fontName=BOLD, fontSize=8.9,
                                leading=12.6, textColor=INK),
        "cellm": ParagraphStyle("cellm", parent=base["Normal"], fontName=ITALIC, fontSize=8.5,
                                leading=12.2, textColor=MUTED),
        "head": ParagraphStyle("head", parent=base["Normal"], fontName=BOLD, fontSize=9.2,
                               leading=12.5, textColor=colors.white),
        "note": ParagraphStyle("note", parent=base["Normal"], fontName=BODY, fontSize=9.8,
                               leading=14.5, textColor=INK, alignment=TA_JUSTIFY),
        "caption": ParagraphStyle("caption", parent=base["Normal"], fontName=ITALIC, fontSize=9,
                                  leading=13, textColor=MUTED, spaceAfter=8),
    }


S = styles()


def field_table(rows: list[tuple[str, str, str, str]]) -> Table:
    """Table of: plain name · what it means · real example · why it is there."""
    header = [
        Paragraph("Trường dữ liệu", S["head"]),
        Paragraph("Nghĩa là gì", S["head"]),
        Paragraph("Ví dụ thật", S["head"]),
        Paragraph("Vì sao cần", S["head"]),
    ]
    data = [header]
    for name, meaning, example, why in rows:
        data.append([
            Paragraph(name, S["cellb"]),
            Paragraph(meaning, S["cell"]),
            Paragraph(example, S["cellm"]),
            Paragraph(why, S["cell"]),
        ])
    table = Table(data, colWidths=[35 * mm, 52 * mm, 40 * mm, 45 * mm], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for index in range(1, len(data)):
        if index % 2 == 0:
            style.append(("BACKGROUND", (0, index), (-1, index), LIGHT))
    table.setStyle(TableStyle(style))
    return table


def simple_table(header: list[str], rows: list[list[str]], widths: list[float]) -> Table:
    data = [[Paragraph(h, S["head"]) for h in header]]
    for row in rows:
        data.append([Paragraph(str(cell), S["cell"]) for cell in row])
    table = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for index in range(1, len(data)):
        if index % 2 == 0:
            style.append(("BACKGROUND", (0, index), (-1, index), LIGHT))
    table.setStyle(TableStyle(style))
    return table


def callout(title: str, body: str, tone=WARN) -> Table:
    inner = [
        [Paragraph(f"<b>{title}</b>", S["note"])],
        [Paragraph(body, S["note"])],
    ]
    table = Table(inner, colWidths=[172 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), tone),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


# --------------------------------------------------------------------------- content


def story() -> list:
    today = dt.date.today().strftime("%d/%m/%Y")
    flow: list = []

    # --- cover
    flow += [
        Spacer(1, 38 * mm),
        p("GreenScan AI", "title"),
        p("Mô tả các trường dữ liệu<br/>bằng ngôn ngữ thông thường", "subtitle"),
        Spacer(1, 14 * mm),
        callout(
            "Tài liệu này dành cho ai",
            "Người dùng nghiệp vụ, khách hàng, kiểm toán viên, cán bộ tín dụng xanh và các thành viên "
            "không chuyên kỹ thuật trong nhóm. Bạn <b>không cần biết lập trình</b> để đọc hết tài liệu này. "
            "Mục đích: hiểu hệ thống lưu giữ những thông tin gì về mỗi tài liệu và mỗi câu tuyên bố, "
            "vì sao lưu, và nhìn vào đâu để tự kiểm tra một kết luận.",
            LIGHT,
        ),
        Spacer(1, 10 * mm),
        simple_table(
            ["Thông tin", "Giá trị"],
            [
                ["Phiên bản cấu trúc dữ liệu", "data-layers-v1"],
                ["Ngày phát hành", today],
                ["Phạm vi", "Toàn bộ dữ liệu GreenScan xử lý: tài liệu thu thập và mỗi lần chạy phân tích"],
                ["Bản kỹ thuật đi kèm", "docs/04-data-ai/DATA_LAYERS.md (dành cho kỹ sư)"],
                ["Nguyên tắc nền", "Mỗi kết luận phải chỉ được ra bằng chứng; chưa đủ bằng chứng thì không kết luận"],
            ],
            [52 * mm, 120 * mm],
        ),
        PageBreak(),
    ]

    # --- 1
    flow += [
        p("1. Vì sao cần tài liệu này", "h1"),
        p(
            "Một báo cáo phát triển bền vững có thể dài hàng trăm trang. Trong đó có một câu như: "
            "<i>“Tập đoàn đã giảm 30% phát thải khí nhà kính.”</i> Câu hỏi của người kiểm tra không phải "
            "“câu này nghe có xanh không”, mà là: <b>giảm 30% của chỉ số nào, so với năm nào, trong phạm vi "
            "nào, và bằng chứng nằm ở trang mấy?</b>",
            "lead",
        ),
        p(
            "Để trả lời được bốn câu đó cho <i>mọi</i> tuyên bố, hệ thống phải ghi lại một số thông tin cố định "
            "về từng tài liệu và từng câu. Tài liệu này liệt kê chính xác các thông tin đó — gọi là "
            "<b>trường dữ liệu</b> — và giải thích từng thông tin có mặt để làm gì.",
        ),
        p(
            "Cách đọc đơn giản: mỗi bảng dưới đây có bốn cột — <b>tên trường</b>, <b>nghĩa là gì</b>, "
            "<b>ví dụ thật</b> lấy từ dữ liệu đã chạy, và <b>vì sao cần</b>. Nếu chỉ có 10 phút, đọc cột đầu "
            "và cột cuối.",
        ),

        p("2. Ba tầng dữ liệu — một ví von", "h1"),
        p(
            "Hãy hình dung công việc của một kiểm toán viên khi nhận một tập hồ sơ giấy:",
        ),
        simple_table(
            ["Tầng", "Ví von đời thường", "Trong GreenScan là gì", "Có sửa được không"],
            [
                ["Tầng 1 — Bản gốc",
                 "Bản photo có đóng dấu, ghi rõ lấy ở đâu, ngày nào",
                 "Tài liệu nguồn đúng như lúc tải về: tệp PDF, địa chỉ tải, ngày tải, mã kiểm tra toàn vẹn",
                 "Không. Đã lưu là giữ nguyên"],
                ["Tầng 2 — Bản sạch",
                 "Bản đánh máy lại từng đoạn, ghi rõ đoạn này ở trang mấy",
                 "Văn bản đã tách thành từng đoạn/bảng, đã chuẩn hoá, đã bỏ trùng lặp, kèm số trang",
                 "Có, khi đổi cách đọc tài liệu — và ghi rõ đổi ở phiên bản nào"],
                ["Tầng 3 — Ý đã tách",
                 "Phiếu ghi từng ý kiến kèm con số, và cả những câu đã bị loại vì không phải tuyên bố",
                 "Từng tuyên bố, từng con số kèm ý nghĩa của nó, từng câu bị loại kèm lý do",
                 "Có, khi cải tiến cách nhận diện tuyên bố"],
            ],
            [26 * mm, 40 * mm, 66 * mm, 40 * mm],
        ),
        p(
            "Ba tầng nối với nhau thành một chuỗi: <b>mỗi ý ở tầng 3 chỉ được ra đoạn văn ở tầng 2, mỗi đoạn "
            "văn chỉ được ra tài liệu gốc ở tầng 1.</b> Nhờ vậy, từ một kết luận trên màn hình, người dùng "
            "luôn bấm ngược về được đúng trang của đúng tệp.",
            "lead",
        ),
        PageBreak(),
    ]

    # --- raw
    flow += [
        p("3. Tầng 1 — Bản gốc: hệ thống biết gì về một tài liệu", "h1"),
        p(
            "Mỗi tài liệu đi vào hệ thống (báo cáo phát triển bền vững, báo cáo thường niên, báo cáo tài chính, "
            "quyết định của cơ quan nhà nước…) được ghi một phiếu như sau.",
        ),
        p("3.1. Tài liệu này từ đâu ra", "h2"),
        field_table([
            ("Địa chỉ nguồn",
             "Đường dẫn web nơi tải tài liệu, và trang đã dẫn tới nó",
             "hoaphat.com.vn/…/BCPTBV-2025.pdf",
             "Người khác kiểm tra lại được đúng tệp đó, không phải bản chép tay"),
            ("Ngày truy cập",
             "Ngày hệ thống tải tài liệu về",
             "07/08/2026",
             "Doanh nghiệp có thể đổi tài liệu trên website; ngày tải cho biết ta đã đọc bản nào"),
            ("Mã kiểm tra toàn vẹn",
             "Một dãy ký tự sinh ra từ nội dung tệp — đổi một dấu phẩy là dãy này đổi",
             "694452fb0947d002…",
             "Chứng minh tệp chưa bị sửa kể từ lúc tải; đây là bằng chứng chống tranh cãi"),
            ("Cấp độ nguồn",
             "Ai đứng sau tài liệu: cơ quan nhà nước, toà án, kiểm toán, đơn vị đánh giá độc lập, sở giao dịch, "
             "chính doanh nghiệp, hay báo chí",
             "Chính doanh nghiệp",
             "Một con số do doanh nghiệp tự công bố không có cùng trọng lượng với số do kiểm toán xác nhận"),
            ("Điều kiện sử dụng",
             "Vì sao tài liệu này được phép lưu và trích dẫn",
             "Công bố công khai trên trang quan hệ nhà đầu tư",
             "Tránh dùng tài liệu không có quyền sử dụng"),
        ]),

        p("3.2. Tài liệu này của ai, nói về kỳ nào", "h2"),
        field_table([
            ("Doanh nghiệp",
             "Tên, mã chứng khoán, sàn niêm yết, ngành",
             "Hoà Phát · HPG · HOSE · Thép",
             "Gộp được mọi tài liệu của cùng một doanh nghiệp; chia dữ liệu học/kiểm thử theo doanh nghiệp"),
            ("Loại tài liệu",
             "Báo cáo phát triển bền vững, báo cáo thường niên, báo cáo tài chính, quyết định pháp lý…",
             "Báo cáo phát triển bền vững",
             "Quyết định nơi tìm bằng chứng: số liệu khí nhà kính không nằm trong tài liệu đại hội cổ đông"),
            ("Năm báo cáo",
             "Kỳ mà tài liệu nói về (không phải ngày tải)",
             "2025",
             "Một tuyên bố năm 2024 không được đối chiếu bằng số liệu năm 2025"),
            ("Ngôn ngữ · số trang",
             "Tiếng Việt hay tiếng Anh; tài liệu dày bao nhiêu trang",
             "Tiếng Việt · 118 trang",
             "Chọn đúng bộ từ vựng khi đọc; ước lượng thời gian xử lý"),
        ]),

        p("3.3. Chất lượng tệp và vai trò trong phân tích", "h2"),
        field_table([
            ("Lượng chữ đọc được trực tiếp",
             "Tệp có sẵn lớp chữ máy đọc được, hay chỉ là ảnh chụp cần nhận dạng",
             "0 ký tự → là bản scan",
             "Bản scan phải qua nhận dạng chữ, và kết quả cần được đánh dấu là kém chắc chắn hơn"),
            ("Vai trò",
             "Tài liệu này là <b>nguồn tuyên bố</b> (nơi lấy câu cần kiểm chứng), là <b>bằng chứng</b> "
             "(nơi đối chiếu), hay chỉ là tài liệu tham chiếu",
             "Nguồn tuyên bố",
             "Nguyên tắc cốt lõi: một báo cáo không được tự xác nhận chính mình"),
            ("Trạng thái",
             "Tải thành công, tải lỗi, hay bị loại — kèm lý do",
             "Tải lỗi: máy chủ từ chối",
             "Bản ghi lỗi vẫn được giữ để biết đã cố lấy gì mà không được"),
        ]),
        PageBreak(),
    ]

    # --- clean
    flow += [
        p("4. Tầng 2 — Bản sạch: từng đoạn văn, biết nằm ở đâu", "h1"),
        p(
            "Một tài liệu 118 trang được tách thành hàng nghìn đơn vị nhỏ: đoạn văn, bảng số liệu, tiêu đề. "
            "Mỗi đơn vị mang theo đúng vị trí của nó.",
        ),
        field_table([
            ("Nội dung đoạn",
             "Chính đoạn văn hoặc bảng, đã chuẩn hoá chính tả kỹ thuật (bỏ ngắt dòng thừa của PDF)",
             "“Trong năm 2025, tổng lượng phát thải… là 23.474.480 tCO2e.”",
             "Là thứ hiển thị cho người xem khi bấm vào bằng chứng"),
            ("Trang · vị trí trong trang",
             "Đoạn này ở trang mấy, khối thứ mấy",
             "Trang 42, khối 3",
             "Để bấm một cái là mở đúng trang PDF và tô sáng đúng chỗ"),
            ("Loại đơn vị",
             "Đoạn văn thường, bảng số liệu, tiêu đề, dòng bảng, chú thích",
             "Bảng số liệu",
             "Số trong bảng được đọc khác với số trong câu văn"),
            ("Có qua nhận dạng chữ không",
             "Đoạn này đọc trực tiếp từ tệp hay do máy đọc ảnh",
             "Không (đọc trực tiếp)",
             "Chữ do máy đọc ảnh có thể sai; kết luận dựa trên đó phải thận trọng hơn"),
            ("Trùng lặp với đoạn nào",
             "Nếu đoạn này lặp lại y hệt một đoạn khác, ghi rõ giữ bản nào",
             "Trùng đoạn ở trang 9",
             "Tránh đếm hai lần cùng một bằng chứng"),
            ("Nhóm dữ liệu",
             "Đoạn này thuộc phần dùng để xây dựng, để tinh chỉnh hay để kiểm tra độc lập",
             "Kiểm tra độc lập",
             "Bảo đảm con số đánh giá là thật: hệ thống không được kiểm tra trên chính dữ liệu đã dùng để xây"),
            ("Cảnh báo chất lượng",
             "Đoạn quá ít chữ, nghi là bản scan, bảng đọc chưa chắc chắn, hoặc chứa câu lệnh lạ chèn vào tài liệu",
             "Bảng đọc chưa chắc chắn",
             "Người xem biết chỗ nào cần kiểm tra bằng mắt"),
        ]),
        callout(
            "Một chi tiết nhỏ nhưng quan trọng: “trang”",
            "Dữ liệu chạy trực tiếp qua hệ thống luôn có số trang cho mọi đoạn. Kho tài liệu thu thập từ đợt "
            "trước <b>chưa lưu số trang</b> — nghĩa là các cặp dữ liệu lấy từ kho cũ chưa trích dẫn được tới "
            "trang. Đây là khoảng trống đã đo được và đang được xử lý ở đợt thu thập mới, không phải lỗi ẩn.",
        ),
        PageBreak(),
    ]

    # --- extract
    flow += [
        p("5. Tầng 3 — Ý đã tách: tuyên bố, con số, và cả câu bị loại", "h1"),
        p(
            "Đây là tầng gần người dùng nhất. Từ mỗi đoạn văn, hệ thống tách ra: các <b>tuyên bố</b> cần kiểm "
            "chứng, các <b>con số</b> kèm ý nghĩa, và ghi lại các <b>câu bị loại</b> kèm lý do.",
        ),
        p("5.1. Một tuyên bố được mô tả bằng năm thuộc tính", "h2"),
        field_table([
            ("Chỉ số",
             "Tuyên bố nói về cái gì: phát thải khí nhà kính, năng lượng tái tạo, nước, chất thải, tài chính xanh",
             "Phát thải khí nhà kính",
             "Không có chỉ số thì không biết lấy gì đối chiếu"),
            ("Số liệu và đơn vị",
             "Con số nêu trong tuyên bố kèm đơn vị đo",
             "23.474.480 tCO2e",
             "Tuyên bố không có số chỉ kiểm chứng được ở mức định tính"),
            ("Kỳ báo cáo",
             "Tuyên bố nói về năm nào",
             "2025",
             "Số liệu năm khác không xác nhận được tuyên bố năm này"),
            ("Năm gốc",
             "Khi tuyên bố nói “giảm/tăng”, mốc so sánh là năm nào",
             "so với 2020",
             "“Giảm 30%” mà không có năm gốc là câu không kiểm chứng được"),
            ("Phạm vi / ranh giới",
             "Áp cho toàn tập đoàn, một công ty con, hay một nhà máy; và thuộc phạm vi phát thải 1, 2 hay 3",
             "Toàn tập đoàn, phạm vi 1 và 2",
             "Số của một nhà máy không bác bỏ được số của cả tập đoàn"),
        ]),
        p(
            "Ngoài ra hệ thống ghi thêm: tuyên bố có phải <b>cam kết tương lai</b> không (ví dụ “Net Zero 2050”), "
            "ngôn từ có <b>mơ hồ / quảng bá</b> không (“hàng đầu”, “thân thiện môi trường”), và mức độ chắc chắn "
            "khi nhận diện.",
        ),
        p("5.2. Câu bị loại — và vì sao phải giữ lại", "h2"),
        p(
            "Không phải câu nào trong báo cáo cũng là tuyên bố cần kiểm chứng. Tiêu đề mục, mục lục, dòng của "
            "bảng số liệu, câu chào mở đầu của lãnh đạo — hệ thống loại ra. <b>Nhưng không xoá:</b> mỗi câu bị "
            "loại được lưu kèm lý do.",
        ),
        simple_table(
            ["Lý do loại (cách gọi dễ hiểu)", "Ví dụ thật"],
            [
                ["Tiêu đề viết hoa", "“XANH HOÁ SẢN XUẤT”"],
                ["Dòng của bảng số liệu", "“Tấn 131.639 306-4 Chất thải được chuyển giao…”"],
                ["Câu bị cắt giữa chừng do xuống trang", "“quốc gia về giảm phát thải khí nhà kính Duy trì cơ chế…”"],
                ["Nói chung chung, không cam kết gì", "“Phát triển bền vững là ưu tiên hàng đầu”"],
                ["Mục lục, tiêu đề mục đánh số", "“4.1 | Quản trị phát triển bền vững”"],
            ],
            [70 * mm, 102 * mm],
        ),
        p(
            "Lý do giữ lại: câu hỏi <i>“hệ thống đã bỏ qua mất cái gì?”</i> là câu hỏi đầu tiên của một người "
            "kiểm tra nghiêm túc. Nếu loại âm thầm thì không ai trả lời được.",
            "caption",
        ),
        PageBreak(),
    ]

    # --- numeric fact
    flow += [
        p("6. Một con số được mô tả bằng sáu chiều", "h1"),
        p(
            "Đây là phần tạo khác biệt lớn nhất về độ tin cậy, nên xin trình bày bằng một ví dụ thật. "
            "Trong báo cáo Hoà Phát 2025 có hai câu:",
        ),
        callout(
            "Hai con số cùng đơn vị “%” nhưng không so được với nhau",
            "<b>Câu A.</b> “Ngành gang thép <b>chiếm hơn 99%</b> tổng lượng phát thải của Tập đoàn.”<br/>"
            "<b>Câu B.</b> “Tổng sản lượng thép thô <b>tăng 24%</b>.”<br/><br/>"
            "Một máy tính ngây thơ thấy 99 khác 24 và kết luận “mâu thuẫn”. Thực tế: câu A nói về <b>tỷ trọng</b> "
            "(chiếm bao nhiêu phần của tổng), câu B nói về <b>mức thay đổi</b> (tăng bao nhiêu so với kỳ trước). "
            "Hai đại lượng khác nhau hoàn toàn. Trước ngày 22/09/2026, hệ thống mắc đúng lỗi này 5 lần trong "
            "một lần chạy.",
        ),
        Spacer(1, 4),
        p(
            "Vì vậy mỗi con số được ghi kèm sáu chiều dưới đây. Hai con số chỉ được đem so khi <b>không chiều "
            "nào mâu thuẫn</b>; nếu lệch một chiều, hệ thống nói rõ “không so sánh được” thay vì kết luận bừa.",
        ),
        field_table([
            ("Cơ sở đo",
             "Số tuyệt đối, cường độ (trên mỗi tấn sản phẩm), tỷ trọng (% của tổng), hay mức thay đổi (% tăng/giảm)",
             "Tỷ trọng",
             "Phân biệt “chiếm 99%” với “tăng 24%”"),
            ("Ranh giới tổ chức",
             "Toàn tập đoàn, một công ty con, một nhà máy, hay một dự án",
             "Toàn tập đoàn",
             "23.474.480 tấn của tập đoàn không mâu thuẫn với 90.846 tấn của một nhà máy"),
            ("Công nghệ",
             "Số này thuộc dây chuyền nào (lò điện, lò cao…), nguồn điện nào (mặt trời, gió…)",
             "Lò điện hồ quang (Scrap-EAF)",
             "0,70 tấn CO2/tấn thép của lò điện không mâu thuẫn với 1,43 của công nghệ khác"),
            ("Loại chỉ số con",
             "Trong cùng một nhóm: điện lưới hay điện tái tạo; chất thải nguy hại hay không nguy hại; "
             "được tái chế hay bị chôn lấp",
             "Điện tái tạo",
             "4,5% điện lưới và 0,03% điện tái tạo là hai tỷ lệ khác nhau"),
            ("Phạm vi phát thải",
             "Phạm vi 1 (trực tiếp), 2 (điện mua), 3 (chuỗi cung ứng)",
             "Phạm vi 1 và 2",
             "Phạm vi 1+2 không so được với phạm vi 1+2+3"),
            ("Mục tiêu hay thực hiện",
             "Con số này là kết quả đã đạt, hay mục tiêu đặt ra cho tương lai",
             "Thực hiện",
             "Mục tiêu 2030 không phải là kết quả 2025"),
        ]),
        p(
            "Kèm theo là <b>độ chính xác công bố</b>: “12%” được hiểu là 11,5–12,5, còn “12,0%” chỉ là "
            "11,95–12,05. Hệ thống không áp một mức sai số cố định cho mọi con số, mà theo đúng cách doanh "
            "nghiệp đã công bố.",
        ),
        PageBreak(),
    ]

    # --- required + state
    flow += [
        p("7. Thông tin nào bắt buộc phải có", "h1"),
        p(
            "Không phải mọi trường đều bắt buộc. Nhưng thiếu các trường dưới đây thì bản ghi <b>không được "
            "dùng để kết luận</b> — hệ thống báo thiếu chứ không đoán.",
        ),
        simple_table(
            ["Tầng", "Bắt buộc với tài liệu thu thập từ bên ngoài", "Bắt buộc với tài liệu người dùng tự tải lên"],
            [
                ["Bản gốc", "Mã toàn vẹn · ngày truy cập · cấp độ nguồn · loại tài liệu · nơi lưu tệp",
                 "Mã toàn vẹn · loại tài liệu"],
                ["Bản sạch", "Thuộc tài liệu nào · mã nội dung · đã phân nhóm dữ liệu",
                 "Thuộc tài liệu nào · mã nội dung"],
                ["Ý đã tách", "Thuộc đoạn nào · thuộc tài liệu nào · mã nội dung",
                 "Thuộc đoạn nào · thuộc tài liệu nào · mã nội dung"],
            ],
            [26 * mm, 76 * mm, 70 * mm],
        ),
        p(
            "Hệ thống phân biệt rạch ròi hai loại vấn đề, và chỉ loại đầu bị coi là lỗi kỹ thuật:",
        ),
        simple_table(
            ["Loại vấn đề", "Nghĩa là", "Ai xử lý"],
            [
                ["Sai cấu trúc", "Bản ghi không đúng khuôn dạng đã quy ước", "Kỹ thuật — là lỗi phần mềm"],
                ["Thiếu thông tin", "Đúng khuôn dạng nhưng thiếu trường cần thiết để dùng",
                 "Nghiệp vụ — bổ sung bằng thu thập, không phải bằng sửa code"],
            ],
            [34 * mm, 84 * mm, 54 * mm],
        ),

        p("8. Hiện trạng dữ liệu (đo ngày 23/09/2026)", "h1"),
        p(
            "Toàn bộ kho tài liệu doanh nghiệp Việt Nam đã được chuyển sang cấu trúc này. Kết quả kiểm tra tự động:",
        ),
        simple_table(
            ["Tầng", "Số bản ghi", "Tình trạng", "Khoảng trống đã đo"],
            [
                ["Bản gốc", "1.061 tài liệu", "0 bản ghi sai cấu trúc",
                 "37% chưa có đường dẫn tệp đã lưu — phần lớn là bản ghi tải lỗi, vẫn giữ để truy vết"],
                ["Bản sạch", "15.658 đoạn", "0 bản ghi sai cấu trúc",
                 "29% chưa phân nhóm dữ liệu (do chưa xác định được năm); chưa có số trang"],
                ["Ý đã tách", "11.746 mục", "0 bản ghi sai cấu trúc", "—"],
            ],
            [24 * mm, 26 * mm, 36 * mm, 86 * mm],
        ),
        p(
            "Hai khoảng trống trên là việc cần làm của công tác thu thập, đã được ghi vào kế hoạch; chúng "
            "không ảnh hưởng tới các kết luận hiện có, vì bản ghi thiếu thông tin bắt buộc thì không được "
            "dùng để kết luận.",
            "caption",
        ),
        PageBreak(),
    ]

    # --- promises + faq + glossary
    flow += [
        p("9. Ba cam kết về dữ liệu", "h1"),
        simple_table(
            ["Cam kết", "Nghĩa cụ thể", "Kiểm chứng bằng cách nào"],
            [
                ["Truy vết được tận gốc",
                 "Từ một kết luận, bấm ngược về đoạn văn, rồi về tài liệu gốc và mã toàn vẹn của nó",
                 "Mọi bản ghi đều mang mã của nội dung nó; hệ thống có bài kiểm tra tự động cho chuỗi này"],
                ["Không bỏ sót âm thầm",
                 "Câu bị loại được lưu kèm lý do; đoạn văn không được chọn làm bằng chứng vẫn được lưu",
                 "Đếm được số câu bị loại theo từng lý do trong mỗi lần chạy"],
                ["Ghi rõ phiên bản",
                 "Mỗi bản ghi biết nó do phiên bản nào của hệ thống tạo ra",
                 "Hai kết quả từ hai phiên bản khác nhau không bị so như cùng một phép đo"],
            ],
            [34 * mm, 74 * mm, 64 * mm],
        ),

        p("10. Câu hỏi thường gặp", "h1"),
        simple_table(
            ["Câu hỏi", "Trả lời"],
            [
                ["Tài liệu nội bộ của chúng tôi có bị gửi ra ngoài không?",
                 "Hệ thống chạy được hoàn toàn trên máy tại chỗ, không cần gửi tài liệu ra dịch vụ bên ngoài. "
                 "Ở chế độ bảo mật, mọi xử lý diễn ra trong hạ tầng của đơn vị."],
                ["Hệ thống có kết luận doanh nghiệp gian lận không?",
                 "Không. Đơn vị đánh giá là từng tuyên bố, không phải doanh nghiệp. Khi bằng chứng chưa đủ, "
                 "hệ thống trả về “chưa đủ bằng chứng” và chuyển cho người xem xét."],
                ["Nếu hệ thống đọc sai một con số thì sao?",
                 "Mỗi con số hiển thị kèm trang nguồn và sáu chiều mô tả; người xem sửa được và quyết định của "
                 "người xem được lưu lại, không ghi đè lịch sử."],
                ["Dữ liệu của chúng tôi có bị dùng để huấn luyện mô hình không?",
                 "Không. Ở phiên bản hiện tại hệ thống không huấn luyện mô hình từ tài liệu khách hàng."],
                ["Ai sửa được dữ liệu đã lưu?",
                 "Tầng bản gốc không sửa. Hai tầng sau chỉ được tạo lại bởi hệ thống và luôn ghi kèm phiên bản, "
                 "nên mọi thay đổi đều truy được."],
            ],
            [62 * mm, 110 * mm],
        ),

        p("11. Bảng thuật ngữ", "h1"),
        simple_table(
            ["Thuật ngữ", "Giải thích ngắn"],
            [
                ["Tuyên bố (claim)", "Một câu doanh nghiệp tự nói về kết quả, mục tiêu hoặc trạng thái môi trường của mình"],
                ["Bằng chứng (evidence)", "Đoạn văn bản, bảng số liệu hoặc văn bản pháp lý dùng để đối chiếu một tuyên bố"],
                ["Phạm vi 1 / 2 / 3", "Phát thải trực tiếp / từ điện mua / từ chuỗi cung ứng — theo thông lệ kiểm kê khí nhà kính"],
                ["Năm gốc", "Năm được lấy làm mốc khi nói “giảm bao nhiêu phần trăm”"],
                ["Cường độ phát thải", "Lượng phát thải trên mỗi đơn vị sản phẩm (ví dụ: tấn CO2 trên mỗi tấn thép)"],
                ["Chưa đủ bằng chứng", "Kết quả hợp lệ: hệ thống không tìm đủ căn cứ để kết luận — không có nghĩa doanh nghiệp sai"],
                ["Mã toàn vẹn", "Dãy ký tự đại diện cho nội dung tệp, dùng để chứng minh tệp chưa bị sửa"],
                ["Phân nhóm dữ liệu", "Chia dữ liệu thành phần để xây dựng và phần để kiểm tra độc lập, tránh tự chấm điểm mình"],
            ],
            [42 * mm, 130 * mm],
        ),
        PageBreak(),

        p("12. Tóm tắt một trang", "h1"),
        p(
            "Trang này in ra dán cạnh màn hình là đủ dùng. Khi xem một kết luận của GreenScan, "
            "hãy hỏi theo đúng thứ tự sau.",
        ),
        simple_table(
            ["Bước", "Câu hỏi cần trả lời", "Nhìn vào đâu"],
            [
                ["1", "Tuyên bố này lấy từ tài liệu nào, trang mấy?",
                 "Thẻ bằng chứng: tên tệp + số trang, bấm vào mở đúng trang"],
                ["2", "Tài liệu đó ai công bố, kỳ nào, tải ngày nào?",
                 "Thông tin tài liệu: doanh nghiệp, loại báo cáo, năm báo cáo, ngày truy cập"],
                ["3", "Tuyên bố có đủ năm thuộc tính chưa?",
                 "Bảng kiểm năm thuộc tính: chỉ số · số liệu · kỳ · năm gốc · phạm vi"],
                ["4", "Con số được đối chiếu với con số nào, và có cùng loại không?",
                 "Phần đối chiếu số liệu: sáu chiều của mỗi con số và kết luận có so được hay không"],
                ["5", "Nếu hệ thống nói chưa đủ bằng chứng thì thiếu gì?",
                 "Câu giải thích nêu đúng thuộc tính còn thiếu"],
                ["6", "Ai chịu trách nhiệm quyết định cuối?",
                 "Người xem xét. Hệ thống đề xuất, con người quyết định và quyết định đó được lưu"],
            ],
            [12 * mm, 74 * mm, 86 * mm],
        ),
        Spacer(1, 5 * mm),
        callout(
            "Ba câu nên nhớ",
            "<b>1.</b> Đơn vị đánh giá là <b>từng tuyên bố</b>, không phải doanh nghiệp.<br/>"
            "<b>2.</b> “Chưa đủ bằng chứng” là <b>kết quả hợp lệ</b>, không phải lỗi, và không có nghĩa "
            "doanh nghiệp làm sai.<br/>"
            "<b>3.</b> Hai con số khác nhau chỉ là mâu thuẫn khi chúng <b>đo cùng một thứ</b> — cùng cơ sở đo, "
            "cùng ranh giới, cùng công nghệ, cùng chỉ số con, cùng phạm vi phát thải, cùng loại mục tiêu/thực hiện.",
            LIGHT,
        ),
        Spacer(1, 6 * mm),
        p(
            "Mọi định nghĩa trong tài liệu này khớp với bản kỹ thuật <b>docs/04-data-ai/DATA_LAYERS.md</b> và "
            "với cấu trúc dữ liệu đang chạy trong hệ thống. Khi cấu trúc thay đổi, cả hai tài liệu được cập "
            "nhật cùng lúc và phiên bản ở trang bìa được nâng lên.",
            "caption",
        ),
    ]
    return flow




def assert_glyphs(flow) -> None:
    """Fail loudly on a character the font cannot draw, instead of shipping black boxes."""
    from reportlab.pdfbase.pdfmetrics import getFont

    # A TTF face lists every code point it can draw in `charWidths`; anything
    # else is drawn as the "missing glyph" box.
    drawable = set(getFont(BODY).face.charWidths)
    collected: list[str] = []

    def walk(item):
        if isinstance(item, Paragraph):
            collected.append(item.getPlainText())
            return
        for attribute in ("_cellvalues", "_content"):
            for row in getattr(item, attribute, None) or []:
                for cell in (row if isinstance(row, list) else [row]):
                    walk(cell)

    for item in flow:
        walk(item)
    text = "".join(collected)
    missing = sorted({
        char for char in text
        if not char.isspace() and ord(char) not in drawable
    })
    if missing:
        raise SystemExit(f"font {BODY} cannot draw {missing!r} - replace these characters")


def build() -> None:
    doc = BaseDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=19 * mm, rightMargin=19 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
        title="GreenScan AI — Mô tả các trường dữ liệu",
        author="Đội AQ2026-119 (Eco Nexus)",
        subject="Định nghĩa trường dữ liệu bằng ngôn ngữ thông thường",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")

    def decorate(canvas, document):
        canvas.saveState()
        canvas.setFont(BODY, 8)
        canvas.setFillColor(MUTED)
        if canvas.getPageNumber() > 1:
            canvas.drawString(doc.leftMargin, A4[1] - 12 * mm,
                              "GreenScan AI — Mô tả các trường dữ liệu · data-layers-v1")
            canvas.setStrokeColor(LINE)
            canvas.line(doc.leftMargin, A4[1] - 14 * mm, A4[0] - doc.rightMargin, A4[1] - 14 * mm)
        canvas.drawRightString(A4[0] - doc.rightMargin, 11 * mm, str(canvas.getPageNumber()))
        canvas.drawString(doc.leftMargin, 11 * mm, "Tài liệu nội bộ · dùng cho trao đổi với khách hàng")
        canvas.restoreState()

    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=decorate)])
    flow = story()
    assert_glyphs(flow)
    doc.build(flow)
    print(f"written: {OUT.relative_to(ROOT)}  ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build()
