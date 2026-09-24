"""Camera-ready 16:9 pipeline diagram, drawn as vector — not generated as an image.

    python tools/make_pipeline_diagram.py            # vi + en, SVG + PNG
    python tools/make_pipeline_diagram.py --lang vi

Why vector and not an image model: the diagram's value is that its text and its
topology are exactly right. Image models rewrite labels, drop connectors, invent
arrows and cannot render Vietnamese diacritics. Here the copy is data, the
geometry is code, and both are reviewable in a diff.

Information model (the reason the layout looks the way it does):

  * three input lanes, not one pile of PDFs — corporate reports enter at READ,
    independent evidence enters at RETRIEVAL, law enters at the legal check.
    This is what separates the system from a chatbot reading one file.
  * a horizontal phase divider: models above, rules below. That boundary is the
    architectural message, so it is drawn, not implied.
  * per-card badges (MODEL / RULE / RULE + MODEL / RULE + HUMAN) instead of
    colouring whole blocks by layer, because stage 1 is parser + model and
    stage 5 is rules with a model fallback. Colouring by block would be a
    simplification the technical audience would catch.
  * the comparability gate is the hero: it is the one idea worth remembering,
    and it is what stops "two different numbers" from becoming "a contradiction".
  * insufficient evidence gets its own branch and its own colour — abstaining is
    a differentiator, not a fifth status chip.
  * the feedback loop is a four-step chain (decisions -> curated labels ->
    train/eval set -> periodic update), dotted, never a human wired into a model.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "07-presentation" / "diagrams"

W, H = 1920, 1080

# Technical / compliance palette: no neon, no gradients, no glow.
PAPER = "#F7F7F4"
NAVY = "#16283B"
NAVY_SOFT = "#2B4055"
GREEN = "#1F7A52"
GREEN_SOFT = "#E7F0EA"
AMBER = "#B8792B"
AMBER_SOFT = "#FBF1DF"
RED = "#A32C1E"
LINE = "#C3CDC7"
MUTED = "#5B6B7B"
INK = "#16283B"

FONT = "Segoe UI, Inter, IBM Plex Sans, Aptos, sans-serif"

TEXT = {
    "vi": {
        "title": "GreenScan AI",
        "subtitle": "Kiểm chứng từng tuyên bố bằng bằng chứng, con số và pháp luật",
        "chips": ["Mô hình đọc", "Luật quyết định", "Người duyệt"],
        "phase_up": "MÔ HÌNH ĐỌC",
        "phase_down": "LUẬT QUYẾT ĐỊNH",
        "inputs": [
            ("BÁO CÁO DOANH NGHIỆP", "phát triển bền vững · thường niên · tài chính · bản scan"),
            ("BẰNG CHỨNG ĐỘC LẬP", "kiểm toán · cơ quan quản lý · quyết định xử phạt"),
            ("VĂN BẢN PHÁP LUẬT", "luật · nghị định · thông tư · ngày hiệu lực"),
        ],
        "stages": [
            ("ĐỌC TÀI LIỆU", "PARSER + MÔ HÌNH", "trang · bảng · OCR"),
            ("LỌC TUYÊN BỐ", "MÔ HÌNH", "kiểm chứng được · mơ hồ ·\nkhông phải tuyên bố · văn mẫu"),
            ("CẤU TRÚC HOÁ", "MÔ HÌNH", "chỉ số · kỳ · năm gốc ·\nphạm vi · giá trị"),
            ("TÌM BẰNG CHỨNG", "MÔ HÌNH", "30 → xếp hạng lại → 5"),
        ],
        "gate_title": "CỔNG KHẢ NĂNG SO SÁNH",
        "gate_badge": "LUẬT",
        "gate_q": "Hai con số này có được phép so với nhau không?",
        "gate_in_claim": "Số trong tuyên bố\ngiảm 30%",
        "gate_in_evidence": "Số trong bằng chứng\n1,2 triệu tCO₂e",
        "gate_checks": [
            "loại giá trị", "ranh giới tổ chức", "công nghệ",
            "chỉ số con", "phạm vi phát thải", "mục tiêu / thực hiện",
        ],
        "gate_yes": "ĐƯỢC SO",
        "gate_yes_sub": "tính toán · dung sai theo độ chính xác đã công bố",
        "gate_no": "KHÔNG SO ĐƯỢC",
        "gate_no_sub": "không kết luận mâu thuẫn · chuyển người xem",
        "law_title": "ĐỐI CHIẾU PHÁP LUẬT",
        "law_badge": "LUẬT",
        "law_sub": "văn bản áp dụng · ngày hiệu lực · nghĩa vụ đã chứng minh chưa",
        "verdict_title": "KẾT LUẬN TỪNG TUYÊN BỐ",
        "verdict_badge": "LUẬT",
        "verdict_chips": ["Khớp", "Khớp một phần", "Bị bác bỏ", "Không được chứng minh"],
        "verdict_abstain": "CHƯA ĐỦ BẰNG CHỨNG",
        "verdict_abstain_sub": "thiếu: năm gốc · phạm vi · nguồn độc lập",
        "risk_title": "Hồ sơ rủi ro",
        "risk_sub": "độ mạnh bằng chứng · mức mâu thuẫn · mức trọng yếu",
        "gates_title": "CỔNG KIỂM SOÁT + NGƯỜI DUYỆT",
        "gates_badge": "LUẬT + NGƯỜI",
        "gates_sub": "8 cổng: nguồn · trích dẫn · phép tính tất định · tái lập\nrủi ro cao → bắt buộc người duyệt",
        "dossier_title": "HỒ SƠ KIỂM CHỨNG",
        "dossier_items": ["kết luận", "nguồn tr.47", "phép tính", "điều luật", "thiếu gì"],
        "loop": ["Quyết định người duyệt", "Nhãn đã tuyển", "Tập huấn luyện / đánh giá",
                 "Cập nhật mô hình định kỳ"],
        "loop_back": "quay lại bước CẤU TRÚC HOÁ",
        "legend_title": "KÝ HIỆU",
        "legend": [
            (GREEN, "MÔ HÌNH — học từ dữ liệu"),
            (NAVY, "LUẬT — mã tất định, tái lập được"),
            (AMBER, "ABSTAIN — từ chối kết luận"),
            (MUTED, "NGƯỜI — quyết định cuối"),
        ],
        "note": "Đơn vị đánh giá là một tuyên bố, không phải một doanh nghiệp.",
    },
    "en": {
        "title": "GreenScan AI",
        "subtitle": "Verify each claim against evidence, numbers and law",
        "chips": ["Models read", "Rules decide", "Humans review"],
        "phase_up": "MODELS READ",
        "phase_down": "RULES DECIDE",
        "inputs": [
            ("CORPORATE REPORTS", "sustainability · annual · financial · scanned"),
            ("INDEPENDENT EVIDENCE", "audit · regulator · penalty decisions"),
            ("LAW", "acts · decrees · circulars · effective dates"),
        ],
        "stages": [
            ("READ", "PARSER + MODEL", "pages · tables · OCR"),
            ("FILTER CLAIMS", "MODEL", "verifiable · vague ·\nnon-claim · boilerplate"),
            ("STRUCTURE CLAIM", "MODEL", "metric · period · baseline ·\nscope · value"),
            ("FIND EVIDENCE", "MODEL", "30 → rerank → 5"),
        ],
        "gate_title": "COMPARABILITY GATE",
        "gate_badge": "RULE",
        "gate_q": "May these two figures be compared at all?",
        "gate_in_claim": "Claim value\n−30%",
        "gate_in_evidence": "Evidence value\n1.2 MtCO₂e",
        "gate_checks": [
            "value type", "organisational boundary", "technology",
            "sub-metric", "emission scope", "target / actual",
        ],
        "gate_yes": "COMPARABLE",
        "gate_yes_sub": "compute · tolerance from published precision",
        "gate_no": "NOT COMPARABLE",
        "gate_no_sub": "no contradiction asserted · send to reviewer",
        "law_title": "CHECK LAW",
        "law_badge": "RULE",
        "law_sub": "applicable instrument · effective date · obligation evidenced?",
        "verdict_title": "PER-CLAIM VERDICT",
        "verdict_badge": "RULE",
        "verdict_chips": ["Supported", "Partially supported", "Contradicted", "Unsupported"],
        "verdict_abstain": "INSUFFICIENT EVIDENCE",
        "verdict_abstain_sub": "missing: baseline · scope · independent source",
        "risk_title": "Risk profile",
        "risk_sub": "evidence strength · contradiction strength · materiality",
        "gates_title": "QUALITY GATES + HUMAN REVIEW",
        "gates_badge": "RULE + HUMAN",
        "gates_sub": "8 gates: provenance · citation · deterministic maths · reproducibility\nhigh risk → reviewer required",
        "dossier_title": "CLAIM EVIDENCE DOSSIER",
        "dossier_items": ["verdict", "source p.47", "calculation", "law", "what is missing"],
        "loop": ["Reviewer decisions", "Curated labels", "Training / evaluation set",
                 "Periodic model update"],
        "loop_back": "back to STRUCTURE CLAIM",
        "legend_title": "LEGEND",
        "legend": [
            (GREEN, "MODEL — learned from data"),
            (NAVY, "RULE — deterministic, reproducible"),
            (AMBER, "ABSTAIN — declines to conclude"),
            (MUTED, "HUMAN — final decision"),
        ],
        "note": "The unit of assessment is one claim, never a company.",
    },
}


# --------------------------------------------------------------------------- svg


def t(text: str) -> str:
    return escape(text)


def txt(x, y, s, *, size=16, fill=INK, weight="400", anchor="start", spacing="0"):
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
        f'font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{spacing}">{t(s)}</text>'
    )


def multiline(x, y, s, *, size=14, fill=MUTED, leading=19, anchor="start"):
    return "".join(
        txt(x, y + i * leading, line, size=size, fill=fill, anchor=anchor)
        for i, line in enumerate(s.split("\n"))
    )


def card(x, y, w, h, *, fill="#FFFFFF", stroke=LINE, width=1.4, radius=10, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" ry="{radius}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{width}"{d}/>'
    )


def accent_bar(x, y, h, colour, w=5):
    """The left rail that says which layer a card belongs to."""
    return (
        f'<path d="M{x + w} {y} h-{w - 5} a5 5 0 0 0 -5 5 v{h - 10} a5 5 0 0 0 5 5 h{w - 5} z" '
        f'fill="{colour}"/>'
    )


def badge(x, y, label, colour):
    width = 9.2 * len(label) + 20
    return (
        f'<rect x="{x}" y="{y}" width="{width:.0f}" height="22" rx="11" ry="11" '
        f'fill="none" stroke="{colour}" stroke-width="1.2"/>'
        + txt(x + width / 2, y + 15.5, label, size=11, fill=colour, weight="600",
              anchor="middle", spacing="0.6")
    )


def arrow(points, *, colour=NAVY_SOFT, width=2.0, dash=None, head=True):
    path = " ".join(f"{'M' if i == 0 else 'L'}{x} {y}" for i, (x, y) in enumerate(points))
    d = f' stroke-dasharray="{dash}"' if dash else ""
    marker = ' marker-end="url(#head)"' if head else ""
    if dash:
        marker = ' marker-end="url(#head-dot)"' if head else ""
    return (
        f'<path d="{path}" fill="none" stroke="{colour}" stroke-width="{width}" '
        f'stroke-linejoin="round" stroke-linecap="round"{d}{marker}/>'
    )


def chip(x, y, label, *, colour=NAVY, fill="#FFFFFF", size=13, pad=14, height=28):
    width = size * 0.62 * len(label) + pad * 2
    return (
        f'<rect x="{x}" y="{y}" width="{width:.0f}" height="{height}" rx="{height / 2}" '
        f'ry="{height / 2}" fill="{fill}" stroke="{colour}" stroke-width="1.2"/>'
        + txt(x + width / 2, y + height / 2 + size * 0.36, label, size=size, fill=colour,
              anchor="middle", weight="500"),
    ), width


def tick(x, y, colour=GREEN):
    return (
        f'<path d="M{x} {y} l4 4 l7 -9" fill="none" stroke="{colour}" stroke-width="2.2" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
    )


# --------------------------------------------------------------------------- build


def build(lang: str) -> str:
    L = TEXT[lang]
    s: list[str] = []
    add = s.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">')
    add('<defs>'
        f'<marker id="head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0 0 L10 5 L0 10 z" fill="{NAVY_SOFT}"/></marker>'
        f'<marker id="head-dot" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0 0 L10 5 L0 10 z" fill="{MUTED}"/></marker>'
        '</defs>')
    add(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>')

    # ---------- header
    add(txt(56, 78, L["title"], size=40, weight="700", fill=NAVY, spacing="-0.5"))
    add(txt(56, 110, L["subtitle"], size=17, fill=MUTED))
    cx = W - 56
    for label in reversed(L["chips"]):
        markup, width = chip(0, 0, label, colour=NAVY, size=14, pad=16, height=32)
        cx -= width
        add(f'<g transform="translate({cx:.0f},62)">' + "".join(markup) + "</g>")
        cx -= 12
    add(f'<line x1="56" y1="136" x2="{W - 56}" y2="136" stroke="{LINE}" stroke-width="1.4"/>')

    # ---------- input lanes (three doors, not one pile)
    lanes = [(160, 290), (310, 390), (410, 490)]
    for (top, bottom), (name, sub) in zip(lanes, L["inputs"], strict=True):
        h = bottom - top
        add(card(56, top, 344, h, fill="#FFFFFF"))
        add(accent_bar(56, top, h, MUTED))
        add(txt(78, top + 30, name, size=14, weight="700", fill=NAVY, spacing="0.8"))
        add(multiline(78, top + 54, sub, size=12.5, fill=MUTED, leading=17))

    # ---------- band: models read
    stage_x = [440, 794, 1148, 1502]
    stage_w, stage_top, stage_h = 330, 160, 130
    for x, (name, badge_label, sub) in zip(stage_x, L["stages"], strict=True):
        add(card(x, stage_top, stage_w, stage_h))
        add(accent_bar(x, stage_top, stage_h, GREEN))
        add(txt(x + 22, stage_top + 34, name, size=17, weight="700", fill=NAVY))
        add(badge(x + 22, stage_top + 46, badge_label, GREEN))
        add(multiline(x + 22, stage_top + 96, sub, size=12.5, fill=MUTED, leading=16))

    # retrieval funnel inside the last stage: 30 -> 5, shown not written
    fx, fy = stage_x[3] + 232, stage_top + 44
    for i in range(6):
        for j in range(5):
            add(f'<rect x="{fx + i * 9}" y="{fy + j * 7}" width="6" height="4.5" rx="1" '
                f'fill="{GREEN}" opacity="0.28"/>')
    add(f'<path d="M{fx} {fy + 42} L{fx + 51} {fy + 42} L{fx + 34} {fy + 58} '
        f'L{fx + 17} {fy + 58} z" fill="none" stroke="{GREEN}" stroke-width="1.6"/>')
    for j in range(5):
        add(f'<rect x="{fx + 17 + j * 7}" y="{fy + 64}" width="5" height="9" rx="1" fill="{GREEN}"/>')

    # arrows between stages
    for x in stage_x[:-1]:
        add(arrow([(x + stage_w, stage_top + stage_h / 2), (x + stage_w + 22, stage_top + stage_h / 2)]))
    # corporate reports -> READ
    add(arrow([(400, 225), (438, 225)]))
    # independent evidence -> retrieval (routed under the model band)
    add(arrow([(400, 350), (1667, 350), (1667, stage_top + stage_h + 4)]))

    # ---------- phase divider: the architectural message
    add(f'<line x1="440" y1="412" x2="{W - 56}" y2="412" stroke="{NAVY}" stroke-width="1.6" '
        f'stroke-dasharray="2 7" opacity="0.55"/>')
    add(txt(448, 402, L["phase_up"], size=12, weight="700", fill=GREEN, spacing="1.6"))
    add(txt(448, 432, L["phase_down"], size=12, weight="700", fill=NAVY, spacing="1.6"))

    # law -> legal check (routed above the divider, then crosses it)
    add(arrow([(400, 450), (424, 450), (424, 390), (1600, 390), (1600, 448)]))

    # ---------- hero: comparability gate
    gx, gy, gw, gh = 440, 452, 680, 344
    add(card(gx, gy, gw, gh, fill="#FFFFFF", stroke=NAVY, width=2.0))
    add(accent_bar(gx, gy, gh, NAVY))
    add(txt(gx + 24, gy + 36, L["gate_title"], size=20, weight="700", fill=NAVY))
    add(badge(gx + 24, gy + 48, L["gate_badge"], NAVY))
    add(txt(gx + 24, gy + 96, L["gate_q"], size=13.5, fill=MUTED))

    # the two figures entering
    for i, key in enumerate(("gate_in_claim", "gate_in_evidence")):
        bx = gx + 40 + i * 330
        add(card(bx, gy + 112, 290, 52, fill=GREEN_SOFT, stroke=GREEN, width=1.2, radius=8))
        add(multiline(bx + 16, gy + 132, L[key], size=12.5, fill=NAVY, leading=17))
    add(arrow([(gx + 185, gy + 164), (gx + 185, gy + 184), (gx + 340, gy + 184), (gx + 340, gy + 196)],
              width=1.8))
    add(arrow([(gx + 515, gy + 164), (gx + 515, gy + 184), (gx + 340, gy + 184)],
              width=1.8, head=False))

    # six checks, two columns
    add(card(gx + 40, gy + 196, 600, 76, fill="#FBFCFB", stroke=LINE, radius=8))
    for i, label in enumerate(L["gate_checks"]):
        col, row = i % 3, i // 3
        px = gx + 58 + col * 200
        py = gy + 222 + row * 28
        add(tick(px, py - 5))
        add(txt(px + 20, py, label, size=12.5, fill=NAVY))

    # outcomes
    add(arrow([(gx + 200, gy + 272), (gx + 200, gy + 292)], width=1.8))
    add(arrow([(gx + 480, gy + 272), (gx + 480, gy + 292)], width=1.8))
    add(card(gx + 40, gy + 292, 290, 40, fill="#FFFFFF", stroke=GREEN, width=1.6, radius=8))
    add(txt(gx + 58, gy + 311, L["gate_yes"], size=13, weight="700", fill=GREEN))
    add(txt(gx + 58, gy + 327, L["gate_yes_sub"], size=11, fill=MUTED))
    add(card(gx + 350, gy + 292, 290, 40, fill="#FFFFFF", stroke=RED, width=1.6, radius=8))
    add(txt(gx + 368, gy + 311, L["gate_no"], size=13, weight="700", fill=RED))
    add(txt(gx + 368, gy + 327, L["gate_no_sub"], size=11, fill=MUTED))

    # retrieval -> comparability gate, entering from the top
    add(arrow([(1667, stage_top + stage_h), (1667, 432), (gx + 200, 432), (gx + 200, gy - 4)],
              width=1.8))

    # ---------- legal check
    lx, ly, lw, lh = 1180, 452, W - 56 - 1180, 104
    add(card(lx, ly, lw, lh))
    add(accent_bar(lx, ly, lh, NAVY))
    add(txt(lx + 24, ly + 34, L["law_title"], size=17, weight="700", fill=NAVY))
    add(badge(lx + 24, ly + 46, L["law_badge"], NAVY))
    add(txt(lx + 24, ly + 92, L["law_sub"], size=12.5, fill=MUTED))
    add(arrow([(gx + gw, gy + 60), (lx - 4, gy + 60)], width=1.8))

    # ---------- verdict + risk
    vx, vy, vw, vh = 1180, 588, lw, 208
    add(card(vx, vy, vw, vh))
    add(accent_bar(vx, vy, vh, NAVY))
    add(txt(vx + 24, vy + 34, L["verdict_title"], size=17, weight="700", fill=NAVY))
    add(badge(vx + 24, vy + 46, L["verdict_badge"], NAVY))
    add(arrow([(lx + lw / 2, ly + lh), (lx + lw / 2, vy - 4)], width=1.8))

    px = vx + 24
    for label in L["verdict_chips"]:
        markup, width = chip(0, 0, label, colour=NAVY_SOFT, size=12, pad=11, height=25)
        add(f'<g transform="translate({px:.0f},{vy + 84})">' + "".join(markup) + "</g>")
        px += width + 8

    # abstain gets its own branch and its own colour
    add(f'<line x1="{vx + 24}" y1="{vy + 124}" x2="{vx + vw - 24}" y2="{vy + 124}" '
        f'stroke="{LINE}" stroke-width="1.2"/>')
    add(card(vx + 24, vy + 136, 300, 52, fill=AMBER_SOFT, stroke=AMBER, width=1.6, radius=8))
    add(txt(vx + 40, vy + 160, L["verdict_abstain"], size=13.5, weight="700", fill=AMBER))
    add(txt(vx + 40, vy + 178, L["verdict_abstain_sub"], size=11, fill=MUTED))
    add(txt(vx + 350, vy + 158, L["risk_title"], size=13, weight="700", fill=NAVY))
    add(txt(vx + 350, vy + 178, L["risk_sub"], size=11, fill=MUTED))

    # ---------- control band
    cx0, cy0, cw, ch = 440, 830, 680, 118
    add(card(cx0, cy0, cw, ch))
    add(accent_bar(cx0, cy0, ch, MUTED))
    add(txt(cx0 + 24, cy0 + 34, L["gates_title"], size=17, weight="700", fill=NAVY))
    add(badge(cx0 + 24, cy0 + 46, L["gates_badge"], MUTED))
    add(multiline(cx0 + 24, cy0 + 92, L["gates_sub"], size=12, fill=MUTED, leading=16))
    add(arrow([(vx, vy + vh - 40), (1150, vy + vh - 40), (1150, 812), (cx0 + cw - 140, 812),
               (cx0 + cw - 140, cy0 - 4)], width=1.8))

    dx, dy, dw, dh = 1180, 830, lw, 118
    add(card(dx, dy, dw, dh, fill=NAVY, stroke=NAVY))
    add(txt(dx + 24, dy + 38, L["dossier_title"], size=18, weight="700", fill="#FFFFFF"))
    px = dx + 24
    for label in L["dossier_items"]:
        markup, width = chip(0, 0, label, colour="#FFFFFF", fill=NAVY, size=12, pad=11, height=26)
        add(f'<g transform="translate({px:.0f},{dy + 60})">' + "".join(markup) + "</g>")
        px += width + 8
    add(arrow([(cx0 + cw, cy0 + ch / 2), (dx - 4, cy0 + ch / 2)], width=1.8))

    # ---------- feedback chain: never a human wired straight into a model
    fy0 = 982
    add(arrow([(cx0 + 140, cy0 + ch), (cx0 + 140, fy0 - 4)], colour=MUTED, width=1.6, dash="3 5"))
    px = 440
    for i, label in enumerate(L["loop"]):
        markup, width = chip(0, 0, label, colour=MUTED, size=12, pad=13, height=28)
        add(f'<g transform="translate({px:.0f},{fy0})">' + "".join(markup) + "</g>")
        px += width
        if i < len(L["loop"]) - 1:
            add(arrow([(px + 4, fy0 + 14), (px + 22, fy0 + 14)], colour=MUTED, width=1.4, dash="3 4"))
            px += 26
    add(arrow([(px + 6, fy0 + 14), (px + 30, fy0 + 14)], colour=MUTED, width=1.4, dash="3 4"))
    add(txt(px + 40, fy0 + 19, L["loop_back"], size=12, fill=MUTED))

    # ---------- legend + standing note
    add(txt(56, 560, L["legend_title"], size=12, weight="700", fill=NAVY, spacing="1.4"))
    for i, (colour, label) in enumerate(L["legend"]):
        y = 590 + i * 30
        add(f'<rect x="56" y="{y - 11}" width="14" height="14" rx="3" fill="{colour}"/>')
        add(txt(80, y, label, size=12.5, fill=MUTED))
    add(f'<line x1="56" y1="736" x2="400" y2="736" stroke="{LINE}" stroke-width="1.2"/>')
    add(multiline(56, 764, L["note"], size=13, fill=NAVY, leading=19))

    add("</svg>")
    return "\n".join(s)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=["vi", "en", "both"], default="both")
    parser.add_argument("--no-png", action="store_true")
    args = parser.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    langs = ["vi", "en"] if args.lang == "both" else [args.lang]
    for lang in langs:
        svg = build(lang)
        path = OUT_DIR / f"pipeline_16x9_{lang}.svg"
        path.write_text(svg, encoding="utf-8")
        print(f"written: {path.relative_to(ROOT)}  ({len(svg) // 1024} KB)")
        if not args.no_png:
            try:
                import cairosvg
            except ImportError:
                print("  (cairosvg not installed — SVG only; `pip install -e \".[docs]\"`)")
                continue
            png = OUT_DIR / f"pipeline_16x9_{lang}.png"
            cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(png),
                             output_width=W * 2, output_height=H * 2)
            print(f"written: {png.relative_to(ROOT)}  ({png.stat().st_size // 1024} KB, 2x)")


if __name__ == "__main__":
    main()
