"""Bản đồ hệ thống GreenScan (bản MCP, máy tối thiểu) dạng ảnh: SVG -> PNG bằng Chrome chạy ngầm.

    C:/Python314/python.exe -X utf8 tools/bao_cao_mo_hinh/ban_do_he_thong.py

Ghi docs/04-data-ai/hinh_mo_hinh/ban_do_he_thong.{svg,png}. Mỗi khối ghi tên mô hình / công cụ thật của công đoạn;
viền đứt = mô hình huấn luyện trên Kaggle, chỉ dùng khi qua cổng. Sửa số liệu ở đây rồi chạy lại.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "04-data-ai" / "hinh_mo_hinh"
CHROME = [r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
W, H = 3060, 1020
SERIF = "'Times New Roman', Georgia, serif"
MONO = "Consolas, 'Courier New', monospace"
RED = "#8b1a1a"


def grad(id_, a, b, vertical=True):
    xy = 'x1="0" y1="0" x2="0" y2="1"' if vertical else 'x1="0" y1="0" x2="1" y2="0"'
    return f'<linearGradient id="{id_}" {xy}><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'


def text(x, y, s, size=22, color="#222", weight="normal", style="normal", anchor="middle", family=SERIF):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'font-style="{style}" text-anchor="{anchor}">{s}</text>')


def box(x, y, w, h, fill, stroke, r=28, sw=4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def pill(x, y, w, h, fill, stroke, s, size=19, color="#333"):
    return box(x, y, w, h, fill, stroke, r=10, sw=2) + text(x + w / 2, y + h / 2 + size * 0.35, s, size, color)


def arrow_right(x, cy, g, stroke, s=1.0):
    pts = [(0, -18), (26, -18), (26, -36), (52, 0), (26, 36), (26, 18), (0, 18)]
    p = " ".join(f"{x + a * s:.1f},{cy + b * s:.1f}" for a, b in pts)
    return f'<polygon points="{p}" fill="url(#{g})" stroke="{stroke}" stroke-width="3" stroke-linejoin="round"/>'


def arrow_down(cx, y, g, stroke, length=110):
    pts = [(-18, 0), (18, 0), (18, length - 40), (38, length - 40), (0, length), (-38, length - 40), (-18, length - 40)]
    p = " ".join(f"{cx + a:.1f},{y + b:.1f}" for a, b in pts)
    return f'<polygon points="{p}" fill="url(#{g})" stroke="{stroke}" stroke-width="3" stroke-linejoin="round"/>'


def label(x, title, color, sub):
    return text(x, 735, title, 31, color, "bold") + text(x, 776, sub, 21, "#777", style="italic")


def lines(x, y0, rows, size, color, step=None, weight="normal", style="normal", family=SERIF, anchor="middle"):
    step = step or size * 1.25
    return "".join(text(x, y0 + i * step, r, size, color, weight, style, anchor, family) for i, r in enumerate(rows))


def pill2(x, y, w, h, fill, stroke, main, code=None, size=18):
    out = box(x, y, w, h, fill, stroke, r=10, sw=2)
    if code:
        out += text(x + w / 2, y + h / 2 - 2, main, size, "#2a2a2a") + text(x + w / 2, y + h / 2 + 18, code, 14, "#888", family=MONO)
    else:
        out += text(x + w / 2, y + h / 2 + size * 0.35, main, size, "#2a2a2a")
    return out


def build() -> str:
    e = []
    defs = "".join([
        grad("gBlue", "#eaf1f8", "#cddff0"), grad("gTeal", "#eef6f3", "#d3e9e0"), grad("gPurple", "#f4eff7", "#e3d7ea"),
        grad("gOrange", "#fdf4e3", "#f9e0b0"), grad("gGold", "#fdf7e6", "#f6e5b0"), grad("gGreen", "#eff6ea", "#d6e7c8"),
        grad("gRed", "#fdeeed", "#f6d6d2"), grad("gPaper", "#ffffff", "#fafafa"),
        grad("aBlue", "#f6f9fc", "#7f9fc2", False), grad("aGray", "#f6f6f6", "#7b7b7b", False),
        grad("aPurple", "#f5f0f8", "#8f6ba9", False), grad("aGold", "#fcf6e6", "#c39a3c", False),
        grad("aPurpleV", "#f5f0f8", "#8f6ba9", True),
        f'<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker>',
        '<marker id="ag" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#888"/></marker>',
    ])
    e.append(f'<defs>{defs}</defs><rect width="{W}" height="{H}" fill="white"/>')
    Y0, Y1 = 300, 680
    CY = (Y0 + Y1) // 2

    # question (top)
    e.append(box(790, 40, 720, 150, "white", "#222", r=48, sw=4))
    e.append(text(1150, 92, "“Báo cáo của Gemadept nói ‘giảm phát thải năm 2024’.", 25, "#222", style="italic"))
    e.append(f'<text x="1150" y="128" font-family="{SERIF}" font-size="25" font-style="italic" text-anchor="middle" fill="#222">'
             f'Điều này <tspan font-weight="bold" fill="#5b3a78">có bằng chứng không</tspan>?”</text>')
    e.append(text(1150, 165, "câu hỏi của người dùng · tài liệu công khai · đã có phiên phân tích", 19, "#777", style="italic"))
    e.append(arrow_down(975, 196, "aPurpleV", "#5b3a78", 100))

    # inputs
    for dx, col, tag in ((0, "#c0392b", "PDF"), (120, "#2b5797", "Word")):
        x0, y0 = 36 + dx, 320
        e.append(f'<path d="M{x0},{y0} h70 l26,26 v96 h-96 z" fill="white" stroke="#888" stroke-width="3"/>')
        e.append(f'<path d="M{x0 + 70},{y0} v26 h26" fill="none" stroke="#888" stroke-width="3"/>')
        e.append(box(x0 + 8, y0 + 64, 80, 30, col, col, r=5, sw=1) + text(x0 + 48, y0 + 86, tag, 19, "white", "bold"))
    e.append(lines(150, 466, ["Báo cáo phát triển bền vững,", "báo cáo thường niên"], 19, "#222", weight="bold"))
    e.append(text(150, 516, "tối đa 5 tệp, 80 MB mỗi lần", 15, "#777", style="italic"))
    e.append('<rect x="38" y="560" width="70" height="90" rx="6" fill="url(#gGold)" stroke="#a07a24" stroke-width="3"/>')
    e.append('<rect x="38" y="560" width="13" height="90" fill="#a07a24"/>')
    for yy in (585, 605, 625):
        e.append(f'<line x1="60" y1="{yy}" x2="98" y2="{yy}" stroke="#a07a24" stroke-width="2.5"/>')
    e.append(text(120, 586, "Bộ quy tắc kiểm tra", 17, "#222", "bold", anchor="start"))
    e.append(lines(120, 610, ["từ khoá môi trường,", "phạm vi xử lý,", "chuẩn đảm bảo ISSA 5000"], 14, "#777",
                   step=19, style="italic", anchor="start"))
    e.append(arrow_right(300, 420, "aBlue", "#2c5d8f", 0.82))
    e.append(arrow_right(302, 605, "aGold", "#a07a24", 0.72))

    # 1. document analysis (no AI)
    X = 360
    e.append(box(X, Y0, 400, Y1 - Y0, "url(#gBlue)", "#2c5d8f", r=34))
    e.append(text(X + 200, 340, "Máy tự kiểm tra tài liệu", 25, "#1f4e79", "bold"))
    e.append(text(X + 200, 366, "theo quy tắc, không dùng AI · OrchestratorAgent", 15, "#5a7898", style="italic"))
    for i, (m, c) in enumerate([("Đọc chữ trong PDF, kể cả trang scan", "PyMuPDF · pdfplumber · Tesseract"),
                                ("Tìm các câu tuyên bố về môi trường", "bộ từ khoá + mẫu câu"),
                                ("Tìm đoạn văn làm bằng chứng", "tìm theo từ khoá (BM25)"),
                                ("So số liệu, chấm rủi ro, xếp hàng cần soát", "luật chấm điểm")]):
        e.append(pill2(X + 18, 384 + i * 60, 364, 52, "white", "#7f9fc2", m, c, 18))
    e.append(f'<ellipse cx="{X + 200}" cy="634" rx="120" ry="11" fill="#dbe7f3" stroke="#2c5d8f" stroke-width="3"/>')
    e.append(f'<path d="M{X + 80},634 v30 a120,11 0 0 0 240,0 v-30" fill="#dbe7f3" stroke="#2c5d8f" stroke-width="3"/>')
    e.append(text(X + 200, 662, "Lưu kết quả phân tích", 17, "#1f3550", "bold"))
    e.append(box(X - 5, 692, 410, 50, "white", "#888", r=8, sw=2, dash="6 5"))
    e.append(text(X + 200, 712, "Mô hình AI đã huấn luyện nhưng chưa dùng:", 14, "#666", style="italic"))
    e.append(text(X + 200, 732, "lọc tuyên bố (chưa đạt, tắt) · xếp hạng bằng chứng (chờ chấm)", 14, "#666", style="italic"))
    e.append(arrow_right(772, CY, "aBlue", "#2c5d8f"))

    # 2. scope check
    X = 840
    e.append(box(X, Y0, 270, Y1 - Y0, "url(#gTeal)", "#1f6f5c"))
    e.append(lines(X + 135, 338, ["Câu hỏi có thuộc việc", "kiểm tra tuyên bố", "môi trường không?"], 20, "#14523f",
                   step=25, weight="bold"))
    e.append(text(X + 135, 416, "scope_guard · quy tắc từ khoá", 14, "#5a8a7a", family=MONO))
    e.append(pill2(X + 15, 436, 240, 52, "#e3f1e6", "#4f8a5b", "Đúng phạm vi", "→ làm tiếp", 18))
    e.append(pill2(X + 15, 498, 240, 52, "#fbf1d8", "#b08a2a", "Thiếu thông tin", "→ hỏi lại người dùng", 18))
    e.append(box(X + 15, 560, 240, 104, "#fbe3e0", "#b8423a", r=10, sw=2))
    e.append(text(X + 135, 586, "Ngoài phạm vi", 18, "#7a1f19", "bold"))
    e.append(text(X + 135, 608, "→ cảnh báo và dừng", 16, "#7a1f19"))
    e.append(lines(X + 135, 632, ["đầu tư, kết luận gian lận,", "viết hộ tuyên bố…"], 13, "#9a4a44", step=17, style="italic"))
    e.append(box(X - 5, 692, 280, 50, "white", "#888", r=8, sw=2, dash="6 5"))
    e.append(text(X + 135, 712, "Mô hình nhỏ sẽ thay quy tắc", 14, "#666", style="italic"))
    e.append(text(X + 135, 732, "khi đạt chuẩn (đang huấn luyện)", 14, "#666", style="italic"))
    e.append(arrow_right(1122, CY, "aGray", "#666"))

    # 3. prompt
    X = 1190
    e.append(f'<path d="M{X},{Y0} h240 l40,40 v{Y1 - Y0 - 40} h-280 z" fill="url(#gPaper)" stroke="#222" stroke-width="3"/>')
    e.append(f'<path d="M{X + 240},{Y0} v40 h40" fill="#eee" stroke="#222" stroke-width="3"/>')
    e.append(text(X + 130, 336, "Lời nhắc gửi cho AI", 19, "#222", "bold"))
    for i, (m, f, st) in enumerate([("11 công cụ được phép dùng", "#efefef", "#888"),
                                    ("Phạm vi + quy định dữ liệu", "#e3edf7", "#7f9fc2"),
                                    ("3 ví dụ lập kế hoạch mẫu", "#e8f1e1", "#7d9e62"),
                                    ("Nêu lý do ngắn, tối đa 3 câu", "#fbf1d8", "#c39a3c"),
                                    ("Câu hỏi + mã phiên phân tích", "#efe6f4", "#8f6ba9")]):
        e.append(pill2(X + 16, 356 + i * 62, 248, 50, f, st, m, None, 17))
    e.append(arrow_right(1482, CY, "aPurple", "#5b3a78"))

    # 4. LLM
    X = 1550
    e.append(f'<polygon points="{X},{Y0} {X + 300},{Y0 + 60} {X + 300},{Y1 - 60} {X},{Y1}" fill="url(#gPurple)" '
             f'stroke="#5b3a78" stroke-width="4"/>')
    e.append(text(X + 138, 392, "Mô hình ngôn ngữ", 19, "#4a2a66"))
    e.append(text(X + 138, 428, "gpt-oss-120b", 29, "#4a2a66", "bold"))
    e.append(text(X + 138, 456, "qua dịch vụ miễn phí Groq", 17, "#6a4a86"))
    e.append(text(X + 138, 498, "Việc 1: chọn công cụ cần gọi", 17, "#3a2050"))
    e.append(text(X + 138, 524, "Việc 2: viết câu trả lời", 17, "#3a2050"))
    e.append(lines(X + 138, 574, ["Tài liệu nội bộ không được", "gửi ra ngoài → máy dùng", "kế hoạch soạn sẵn theo quy tắc"],
                   14, "#777", step=18, style="italic"))
    e.append(arrow_right(1862, CY, "aPurple", "#5b3a78"))

    # 5. tools
    X = 1930
    e.append(box(X, Y0, 400, Y1 - Y0, "url(#gOrange)", "#b07a14"))
    e.append(text(X + 200, 338, "Công cụ được gọi (ví dụ)", 19, "#6b4b0e", "bold"))
    for i, (n, m, c) in enumerate([("1", "Lấy danh sách tuyên bố cần soát", "review_queue"),
                                   ("2", "Tra kết luận của tuyên bố đó", "verify_claim"),
                                   ("3", "Lấy lý do của kết luận", "explain_claim")]):
        y = 382 + i * 70
        e.append(text(X + 26, y, n, 22, "#6b4b0e", "bold", anchor="start"))
        e.append(text(X + 54, y, m, 19, "#3d2a07", anchor="start"))
        e.append(text(X + 54, y + 22, c, 15, "#8a6a2a", anchor="start", family=MONO))
    e.append(lines(X + 200, 612, ["Công cụ khác: tìm bằng chứng, đọc chỉ số", "trong tuyên bố, đọc tờ đảm bảo độc lập…"],
                   15, "#8a6a2a", step=20, style="italic"))
    e.append(arrow_right(2342, CY, "aGold", "#a07a24"))

    # 6. answer check
    X = 2410
    e.append(box(X, Y0, 280, Y1 - Y0, "url(#gGold)", "#a07a24"))
    e.append(text(X + 140, 342, "Kiểm tra bằng code", 22, "#6b5212", "bold"))
    e.append(text(X + 140, 366, "guards.new_numbers", 14, "#8a7232", family=MONO))
    e.append(lines(X + 140, 412, ["✓ Mọi con số đều có trong", "kết quả công cụ"], 17, "#245a2f", step=22))
    e.append(lines(X + 140, 476, ["✓ Kết luận đúng như", "hệ thống đã đưa ra"], 17, "#245a2f", step=22))
    e.append(f'<rect x="{X + 40}" y="530" width="200" height="20" fill="#5c7f3c"/>'
             f'<line x1="{X + 140}" y1="522" x2="{X + 140}" y2="558" stroke="#b8423a" stroke-width="3"/>')
    e.append(lines(X + 140, 596, ["Sai → bỏ câu của AI,", "dùng câu trả lời soạn sẵn"], 16, RED, step=21, style="italic"))
    e.append(arrow_right(2702, 420, "aGold", "#a07a24", 0.7))
    e.append(f'<polygon points="2704,620 2728,632 2704,644" fill="{RED}"/>')

    # 7. outputs
    X = 2760
    e.append(box(X, Y0, 270, 260, "url(#gGreen)", "#5c7f3c", r=24))
    e.append(f'<path d="M{X + 102},344 l22,22 l42,-46" fill="none" stroke="#3d6b27" stroke-width="9" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')
    e.append(lines(X + 135, 406, ["Kết luận:", "hỗ trợ một phần"], 21, "#2f5a1d", step=26, weight="bold"))
    e.append(text(X + 135, 476, "PARTIALLY_SUPPORTED", 14, "#5c7f3c", family=MONO))
    e.append(lines(X + 135, 506, ["kèm lý do, chỉ số còn thiếu", "và việc nên làm tiếp"], 15, "#666", step=20, style="italic"))
    e.append(box(X, 580, 270, 100, "url(#gRed)", "#b8423a", r=20, sw=3))
    e.append(text(X + 135, 614, "Câu trả lời soạn sẵn", 19, "#7a1f19", "bold"))
    e.append(lines(X + 135, 640, ["theo quy tắc, khi AI lỗi", "hoặc câu của AI bị chặn"], 14, "#7a1f19", step=18, style="italic"))

    # feedback loops (top)
    e.append(f'<path d="M2130,{Y0} V256 H1700 V{Y0 + 30}" fill="none" stroke="{RED}" stroke-width="4" '
             f'stroke-dasharray="14 9" marker-end="url(#ah)"/>')
    e.append(text(1915, 244, "Kết quả công cụ gửi lại cho AI (tối đa 5 bước)", 21, RED, style="italic"))
    e.append(f'<text x="1560" y="200" font-family="{SERIF}" font-size="21" font-style="italic" fill="{RED}">'
             f'<tspan font-weight="bold">AI lỗi hoặc kế hoạch sai</tspan> ➜ dùng kế hoạch soạn sẵn</text>')
    e.append(f'<text x="2250" y="200" font-family="{SERIF}" font-size="21" font-style="italic" fill="{RED}">'
             f'<tspan font-weight="bold">Câu trả lời có số bịa / kết luận lạ</tspan> ➜ dùng câu soạn sẵn</text>')

    # labels
    def lab(x, t, c, sub):
        return text(x, 790, t, 28, c, "bold") + text(x, 828, sub, 18, "#777", style="italic")
    e.append(lab(150, "Đầu vào", "#222", "tài liệu + bộ quy tắc"))
    e.append(lab(560, "Phân tích tài liệu", "#1f4e79", "không dùng AI · chạy trên CPU, ≤ 1,6 GB RAM"))
    e.append(lab(975, "Kiểm tra phạm vi", "#14523f", "ngoài phạm vi thì dừng ngay"))
    e.append(lab(1330, "Soạn lời nhắc", "#222", "khoảng 2.000 token"))
    e.append(lab(1700, "AI lập kế hoạch, trả lời", "#4a2a66", "tối đa 3 lần gọi AI / câu hỏi"))
    e.append(lab(2130, "Chạy công cụ", "#6b4b0e", "chỉ đọc kết quả đã phân tích"))
    e.append(lab(2550, "Kiểm tra câu trả lời", "#6b5212", "bằng code, không dùng AI"))
    e.append(lab(2895, "Trả lời người dùng", "#2f5a1d", "hoặc hỏi lại / dừng"))

    # tools read the stored analysis (bottom)
    e.append(f'<path d="M760,{Y1 - 20} H778 V880 H2318 V{Y1 + 6}" fill="none" stroke="#888" stroke-width="3" '
             f'stroke-dasharray="10 8" marker-end="url(#ag)"/>')
    e.append(text(1548, 906, "Các công cụ chỉ đọc lại kết quả phân tích đã lưu — không công cụ nào tự đưa ra kết luận",
                  20, "#777", style="italic"))
    e.append(text(W / 2, 980, "Chạy trên máy tối thiểu: CPU, 8–16 GB RAM, không cần GPU · Khung viền đứt: mô hình AI đã "
                  "huấn luyện trên Kaggle, chỉ dùng khi đạt chuẩn đánh giá · Viết lời giải thích bằng AI chạy trên máy "
                  "(Ollama Qwen3-4B): tuỳ chọn, mặc định tắt", 18, "#999", style="italic"))
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">' + "".join(e) + "</svg>"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    svg = build()
    (OUT / "ban_do_he_thong.svg").write_text(svg, encoding="utf-8")
    html = OUT / "ban_do_he_thong.html"
    html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:#fff}}</style>'
                    f'</head><body>{svg}</body></html>', encoding="utf-8")
    exe = next((c for c in CHROME if Path(c).exists()), None)
    if not exe:
        print("không thấy Chrome/Edge: mở ban_do_he_thong.html rồi chụp")
        return 1
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={prof}",
                        f"--window-size={W},{H}", "--force-device-scale-factor=2",
                        f"--screenshot={OUT / 'ban_do_he_thong.png'}", html.as_uri()], check=True, timeout=120,
                       capture_output=True)
    html.unlink()
    print(f"-> {OUT / 'ban_do_he_thong.png'} ({(OUT / 'ban_do_he_thong.png').stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
