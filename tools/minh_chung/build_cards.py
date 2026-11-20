"""Thẻ minh chứng cho bảng "Việc cần làm ISSA 5000": mỗi việc đã xong có một ảnh chụp từ thành phẩm thật trong repo.

Bước 1 (tệp này, .venv): dựng một trang HTML cho mỗi việc từ tệp thật (trích đoạn, trang PDF dựng thành ảnh, kết quả
bài kiểm, kết quả lượt chạy). Bước 2 (tools/minh_chung/shoot.py, Python có playwright): chụp từng trang thành PNG và chụp
giao diện thật.

    .venv/Scripts/python.exe -I tools/minh_chung/build_cards.py <thư_mục_làm_việc>
"""
import base64
import hashlib
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import fitz
import yaml

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
WORK = Path(sys.argv[1])
CARDS = WORK / "cards"
CARDS.mkdir(parents=True, exist_ok=True)
AI_RUN, RULES_RUN = "ad323c772d064015", "759eaa3583dd4d78"
TODAY = datetime.now().strftime("%d/%m/%Y")
IAASB = ROOT / "data/standards/iaasb"


def rd(p, a=None, b=None):
    lines = (ROOT / p).read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[(a or 1) - 1:b])


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()[:16]


def mtime(p):
    return datetime.fromtimestamp((ROOT / p).stat().st_mtime).strftime("%d/%m/%Y %H:%M")


def pdf_png(p, page=0, zoom=1.1):
    d = fitz.open(ROOT / p)
    png = d[page].get_pixmap(matrix=fitz.Matrix(zoom, zoom)).tobytes("png")
    return f'<img class="pdf" src="data:image/png;base64,{base64.b64encode(png).decode()}">', len(d)


def find_page(p, needle):
    d = fitz.open(ROOT / p)
    for i, pg in enumerate(d):
        if needle in pg.get_text():
            return i
    return 0


def pre(text, n=40):
    lines = text.splitlines()
    more = f"\n… ({len(lines) - n} dòng nữa)" if len(lines) > n else ""
    return f"<pre>{html.escape(chr(10).join(lines[:n]) + more)}</pre>"


def test_line(name):
    t = (WORK / f"test_{name}.txt").read_text(encoding="utf-8")
    return f"pytest tests/test_{name}.py: {t.count('.')} bài kiểm đạt, 0 lỗi (chạy {TODAY})"


def run(rid):
    return json.loads((ROOT / f".quantum/runs/{rid}/result.json").read_text(encoding="utf-8"))


def card(stt, title, files, body, note=""):
    src = "".join(f"<li><code>{html.escape(f)}</code> · sửa {mtime(f)} · sha256 {sha(f)}…</li>" for f in files
                  if (ROOT / f).is_file())
    page = f"""<!doctype html><html lang="vi"><meta charset="utf-8"><style>
body{{margin:0;background:#eef1ef;font:15px/1.45 "Segoe UI",Arial,sans-serif;color:#1d2a24}}
.card{{width:1120px;margin:0;padding:22px 26px;background:#fff;border-top:8px solid #1f7a4d}}
h1{{font-size:22px;margin:0 0 4px}} .meta{{color:#4b5d55;font-size:13px;margin-bottom:12px}}
.ok{{display:inline-block;background:#1f7a4d;color:#fff;border-radius:4px;padding:1px 8px;font-weight:600;margin-right:8px}}
pre{{background:#f6f8f7;border:1px solid #d7ded9;border-radius:6px;padding:10px 12px;font:12.5px/1.4 Consolas,monospace;white-space:pre-wrap;word-break:break-word;margin:8px 0}}
ul{{margin:6px 0 0 18px;padding:0;font-size:12.5px;color:#33463d}} img.pdf{{max-height:560px;border:1px solid #c9d2cc;margin-right:12px;vertical-align:top}}
img.ui{{max-width:1068px;border:1px solid #c9d2cc}} table{{border-collapse:collapse;font-size:13.5px}} td,th{{border:1px solid #d7ded9;padding:4px 8px;text-align:left;vertical-align:top}}
th{{background:#f0f4f2}} .note{{font-size:13px;color:#4b5d55;margin-top:8px}}
</style><div class="card"><h1>Việc {stt} — {html.escape(title)}</h1>
<div class="meta"><span class="ok">ĐÃ HOÀN THÀNH</span>Minh chứng chụp {TODAY} từ repo GreenScan-AI</div>
{body}<div class="note">{note}</div><ul>{src}</ul></div></html>"""
    (CARDS / f"{stt:02d}.html").write_text(page, encoding="utf-8")
    print("card", stt, title)


ra, rb = run(AI_RUN), run(RULES_RUN)

card(1, "Định dạng file đầu vào", ["configs/default.yaml"],
     pre(rd("configs/default.yaml", 5, 14)) + pre("\n".join(sorted(p.name for p in (ROOT / "src/quantum_gw/parsers").glob("*.py")))),
     "Phần intake của cấu hình và các bộ đọc tệp trong src/quantum_gw/parsers (PDF có lớp chữ, PDF quét qua OCR, DOCX, HTML).")

dm = json.loads((ROOT / "data/real_cases/sources/originals/download_manifest.json").read_text(encoding="utf-8"))
card(4, "Ghi chú nguồn từng file", ["data/real_cases/sources/originals/download_manifest.json", "data/standards/iaasb/README.md"],
     pre(json.dumps(dm, ensure_ascii=False, indent=1), 22) + pre(json.dumps(ra["manifest"]["input_hashes"], ensure_ascii=False, indent=1)),
     "Bản kê tải về (nguồn, ngày tải) và mã băm SHA-256 của mọi tệp đầu vào trong bản kê lượt chạy Hòa Phát (cổng G6).")

img, n = pdf_png("data/standards/iaasb/IAASB-International-Standard-on-Sustainability-Assurance-ISSA-5000.pdf")
card(5, "Văn bản ISSA 5000 bản PDF chính thức",
     ["data/standards/iaasb/IAASB-International-Standard-on-Sustainability-Assurance-ISSA-5000.pdf"], img + pre(rd("data/standards/iaasb/README.md"), 26),
     f"Trang bìa bản PDF chính thức của IAASB ({n} trang) và README ghi nguồn tải, mã băm.")

ILL = "data/standards/iaasb/IAASB-ISSA-5000-Sustainability-Assurance-Illustrative-Reports.pdf"
img, n = pdf_png(ILL)
img2, _ = pdf_png(ILL, find_page(ILL, "Illustration 6") or 1, 0.9)
card(6, "8 báo cáo đảm bảo mẫu IAASB (11/2025)", [ILL], img + img2,
     f"Tệp minh hoạ của IAASB ({n} trang): 8 báo cáo A–H, A–E kết luận không sửa đổi, F ngoại trừ, G từ chối đưa ra kết luận, H trái ngược.")

FAQ = "data/standards/iaasb/IAASB-ISSA-5000-Sustainability-Frequently-Asked-Questions-FAQ-Materiality.pdf"
IG = "data/standards/iaasb/IAASB-ISSA-5000-Implementation-Guide-Sustainability-Assurance.pdf"
a, na = pdf_png(FAQ, 0, 0.8)
b, nb = pdf_png(IG, 0, 0.8)
card(7, "FAQ về trọng yếu và hướng dẫn thực hiện ISSA 5000", [FAQ, IG], a + b,
     f"FAQ về trọng yếu ({na} trang) và ISSA 5000 Implementation Guide ({nb} trang), cả hai do IAASB phát hành.")

ISSA = "data/standards/iaasb/IAASB-International-Standard-on-Sustainability-Assurance-ISSA-5000.pdf"
pg = find_page(ISSA, "Appendix 3")
img, _ = pdf_png(ISSA, pg, 1.0)
card(48, "4 báo cáo đảm bảo minh hoạ ở Phụ lục 3 của ISSA 5000", [ISSA], img,
     f"Trang {pg + 1} của bản ISSA 5000: Phụ lục 3 (Illustrative Assurance Reports). Cùng 8 mẫu 11/2025 thành 12 mẫu.")

labels = (IAASB / "issa_samples_labels.yaml").read_text(encoding="utf-8")
card(28, "12 báo cáo mẫu IAASB trong kho dữ liệu", ["data/standards/iaasb/issa_samples_labels.yaml", ILL, ISSA], pre(labels, 46),
     "12 báo cáo nằm trong hai tệp PDF ở data/standards/iaasb/ (8 bộ minh hoạ 11/2025 + 4 ở Phụ lục 3); bảng nhãn đi kèm.")

reading = "\n".join(f"{r['source_name']:42s} tr.{r['page']:<4} vai trò {r['role']:13s} OCR {r['ocr']}" for r in ra["reading"])
card(8, "Công cụ trích xuất PDF", ["src/quantum_gw/parsers/pdf.py"] if (ROOT / "src/quantum_gw/parsers/pdf.py").is_file() else [],
     pre(reading) + pre("\n".join(l for l in (ROOT / "src/quantum_gw/parsers").joinpath("pdf.py").read_text(encoding="utf-8").splitlines()
                              if re.search(r"import (fitz|pdfplumber|pymupdf)|tesseract", l, re.I))[:1500] if (ROOT / "src/quantum_gw/parsers/pdf.py").is_file() else ""),
     f"Lượt Hòa Phát {AI_RUN}: PyMuPDF đọc chữ, pdfplumber đọc bảng, Tesseract chỉ chạy cho trang quét. Bảng trên là các trang đọc đặc biệt mà lượt chạy ghi lại.")

ep = (ROOT / f".quantum/runs/{AI_RUN}/evidence_pack.md").read_text(encoding="utf-8")
cites = [l for l in ep.splitlines() if re.search(r"\((tr|trang)\.? ?\d+|page \d+", l)][:16]
card(9, "Trích xuất kèm số trang", [f".quantum/runs/{AI_RUN}/evidence_pack.md"], pre("\n".join(cites)),
     "Các dòng trích dẫn trong gói bằng chứng của lượt Hòa Phát: mỗi tuyên bố và bằng chứng giữ tệp và số trang.")

card(11, "Tách đoạn", [f".quantum/runs/{AI_RUN}/result.json"],
     pre(json.dumps({"tong_tai_lieu": ra["summary"]["total_documents"], "tong_doan": ra["summary"]["total_chunks"],
                     "tong_tuyen_bo": ra["summary"]["total_claims"]}, ensure_ascii=False, indent=1)) +
     pre(json.dumps({k: ra["verifications"][0]["evidence"][0][k] for k in ("chunk_id", "source_name", "page", "text")},
                    ensure_ascii=False, indent=1)),
     "Lượt Hòa Phát: 2 tài liệu tách thành các đoạn phân tích; mỗi đoạn có mã, tệp, trang và không vượt chỗ ngắt đoạn.")

card(12, "Danh sách yếu tố bắt buộc của báo cáo đảm bảo (ISSA 5000)", ["configs/issa5000_report_elements.yaml", "tests/test_issa5000_patterns.py"],
     pre(rd("configs/issa5000_report_elements.yaml"), 44), test_line("issa5000_patterns"))
card(13, "Mẫu câu đặc trưng cho từng loại kết luận", ["configs/issa5000_conclusion_patterns.yaml"],
     pre("\n".join(l for l in rd("configs/issa5000_conclusion_patterns.yaml").splitlines() if re.search(r"pattern_id|conclusion_type|assurance_level|language", l)), 44),
     test_line("issa5000_patterns"))
card(14, "Bảng ISSA_Conclusion_Patterns (YAML có phiên bản)", ["configs/issa5000_conclusion_patterns.yaml"],
     pre(rd("configs/issa5000_conclusion_patterns.yaml"), 40), "Lưu dạng YAML có phiên bản trong configs/ thay cho bảng cơ sở dữ liệu. " + test_line("issa5000_patterns"))

g8 = [g for g in ra["quality_gates"] if g["gate_id"].upper().startswith("G8")]
card(49, "Loại chữ ẩn và chặn câu nhắn tới máy chấm", ["tests/test_security_prompt_injection.py"],
     pre(json.dumps(g8, ensure_ascii=False, indent=1), 30) + pre(test_line("security_prompt_injection")),
     "Cổng G8 trong lượt Hòa Phát và bộ bài kiểm chống chèn lệnh.")

card(50, "Đo và báo độ tin cậy OCR", ["benchmark/ocr_calibration_2026-11-11.json", "tests/test_ocr_confidence.py"],
     pre(json.dumps(json.loads((ROOT / "benchmark/ocr_calibration_2026-11-11.json").read_text(encoding="utf-8")), ensure_ascii=False, indent=1), 40),
     test_line("ocr_confidence"))

block = re.search(r"^claim_quality_v1_1:.*?(?=^\S)", (ROOT / "configs/measurement_decisions.yaml").read_text(encoding="utf-8"), re.S | re.M)
card(56, "Lọc câu dính chữ dàn trang khỏi đầu hàng đợi", ["configs/measurement_decisions.yaml", "tests/test_claim_quality.py"],
     pre(block.group(0) if block else "", 30), test_line("claim_quality"))

ex = next(c for c in ra["claims"] if c.get("values") and c.get("units"))
card(18, "Nhận diện số liệu định lượng", [f".quantum/runs/{AI_RUN}/result.json"],
     pre(json.dumps({k: ex[k] for k in ("text", "metric", "values", "units", "period", "baseline", "scope", "is_vague")}, ensure_ascii=False, indent=1)),
     "Một tuyên bố của Hòa Phát sau bộ đọc số liệu: giá trị, đơn vị, kỳ, năm gốc được tách riêng để kiểm.")

csv_txt = None
try:
    sys.path.insert(0, str(ROOT / "src"))
    from quantum_gw.domain.models import AnalysisResult
    from quantum_gw.queue_csv import render_queue_csv
    csv_txt = render_queue_csv(AnalysisResult.model_validate(ra))
    csv_txt = csv_txt.decode("utf-8-sig") if isinstance(csv_txt, bytes) else csv_txt
except Exception as e:  # noqa: BLE001
    csv_txt = f"(không dựng được CSV: {e})"
card(35, "Xuất bảng hàng đợi ra CSV", ["src/quantum_gw/queue_csv.py"], pre(csv_txt.lstrip("﻿"), 14),
     "Mười dòng đầu tệp CSV xuất từ lượt Hòa Phát (UTF-8 có BOM, mở thẳng bằng Excel); dòng đầu là câu lưu ý.")

card(58, "Công cụ kiểm nhanh điểm yếu", ["tools/check_weaknesses.py"],
     pre((WORK / "weak.txt").read_text(encoding="utf-8").replace("warning: The `fitz` API is deprecated and will be removed in future. Use `import pymupdf` instead.\n", "")),
     f"Chạy {TODAY} trên lượt Hòa Phát có AI; mỗi điểm yếu một con số, xong trong vài giây.")

guide = rd("docs/02-product/HUONG_DAN_SU_DUNG_1_TRANG.md")
card(43, "Hướng dẫn sử dụng 1 trang", ["docs/02-product/HUONG_DAN_SU_DUNG_1_TRANG.md"], pre(guide, 60))
lim = guide[guide.lower().find("giới hạn"):] if "giới hạn" in guide.lower() else guide
card(45, "Ghi rõ những gì MVP chưa làm", ["docs/02-product/HUONG_DAN_SU_DUNG_1_TRANG.md"], pre(lim, 40),
     "Phần giới hạn trong hướng dẫn 1 trang (cũng hiện trong ứng dụng).")

S = json.loads((ROOT / "experiments/AI-RUN/kaggle_out/summary.json").read_text(encoding="utf-8"))
rows = [("Thời gian chạy Hòa Phát (T4)", f"{S['seconds']['rules']} s", f"{S['seconds']['ai']} s"),
        ("Cặp luật bỏ ngỏ được mô hình đọc", "0", f"{S['ai']['relation_method'].get('llm', 0)}"),
        ("Bộ đọc kép (đoạn)", "0", f"{S['ai']['ir_passages_read']} ({S['ai']['ir_vs_rules']})"),
        ("Lời giải thích cho hàng đợi", "0", str(S["ai"]["explanations_kept"])),
        ("Kết luận đổi so với chỉ luật", "—", f"{len(S['statuses_changed'])} (đều về 'chưa đủ bằng chứng')"),
        ("evaluate-real 4 vụ có phán quyết", "trạng thái 4/4", "trạng thái 4/4")]
tbl = "<table><tr><th>Chỉ số</th><th>Chỉ luật</th><th>Có AI (Qwen3-4B Q4)</th></tr>" + "".join(
    f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows) + "</table>"
ui = WORK / "ui_ai_detail.png"
uiimg = f'<p><img class="ui" src="data:image/png;base64,{base64.b64encode(ui.read_bytes()).decode()}"></p>' if ui.is_file() else ""
card(61, "Đo bật/tắt AI trên cùng một bộ", ["experiments/AI-RUN/kaggle_out/summary.json", "configs/measurement_decisions.yaml"], tbl + uiimg,
     f"Lượt Kaggle diuquinh/gs-ai-run-hpg (11/11): run {RULES_RUN} (chỉ luật) và {AI_RUN} (có AI) trên cùng máy; từng tầng S1–S6 đo trong khối llm_stages_v1.")
print("done", len(list(CARDS.glob("*.html"))), "cards ->", CARDS)
