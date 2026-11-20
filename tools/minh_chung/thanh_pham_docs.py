"""Dựng tài liệu thành phẩm (Google Docs, gộp theo nhóm) cho các việc đã hoàn thành trong checklist AQ2026-119.

Bước 1, dựng HTML (cần openpyxl, chạy bằng .venv):
    .venv/Scripts/python.exe -I tools/minh_chung/thanh_pham_docs.py build <thư_mục_làm_việc> "<kết quả bài kiểm>"
Bước 2, đẩy lên Drive, tự đổi sang Google Docs (cần google-api-python-client, chạy bằng Python có thư viện Google):
    python tools/minh_chung/thanh_pham_docs.py upload <thư_mục_làm_việc> <token.json> <id_thư_mục_root>
    -> docs/00-project/minh-chung/thanh_pham_drive_2026-11-12.json (link từng tài liệu, dùng để điền cột Thành phẩm)

Nguồn chữ: cột "Việc cần làm" lấy từ bản xlsx 11/11 trong repo, cột "Tiến độ" lấy từ cap_nhat_bang_2026-11-12.json
(đã ghi lên Google Sheet 12/11), cộng ghi chú đối chiếu tệp của thành viên ngày 12/11.
"""
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MC = ROOT / "docs/00-project/minh-chung"
RAW = "https://raw.githubusercontent.com/nguyennhan2006/GreenScan-AI/minh-chung/docs/00-project/minh-chung/viec-{:02d}.png"
SHEET = "https://docs.google.com/spreadsheets/d/18r2JLcgvSxvJwlMSlpaepjpE6jmhBxbaEO4_pGQalJY/edit?gid=1676970004"
ME = "nguyenchonnhan@gmail.com"
FOLDER = "Thành phẩm các việc đã hoàn thành (AQ2026-119)"

GROUPS = [
    ("Thành phẩm 1 - Tài liệu đầu vào và nguồn dữ liệu (việc 1, 4)", [1, 4]),
    ("Thành phẩm 2 - Đọc PDF, OCR và làm sạch văn bản (việc 8, 9, 11, 49, 50, 56)", [8, 9, 11, 49, 50, 56]),
    ("Thành phẩm 3 - Chuẩn mực ISSA 5000 và báo cáo đảm bảo mẫu (việc 5, 6, 7, 12, 13, 14, 28, 48)",
     [5, 6, 7, 48, 28, 12, 13, 14]),
    ("Thành phẩm 4 - Nhận diện số liệu và trích dẫn phát hiện (việc 18, 27)", [18, 27]),
    ("Thành phẩm 5 - Đầu ra cho người dùng và tài liệu hướng dẫn (việc 34, 35, 43, 45, 57)", [34, 35, 43, 45, 57]),
    ("Thành phẩm 6 - Kiểm thử và đo lường (việc 58, 61)", [58, 61]),
]
OWNER = {5: "Phan Thanh Thảo (phanthanhthaonb1@gmail.com)", 6: "Lê Diễm Quỳnh", 7: "Lê Diễm Quỳnh"}
DRIVE = {
    5: [("ISSA 5000 bản PDF Thảo tải lên Drive", "https://drive.google.com/file/d/10-DsBMweuEVL554eWMI10LL6B6irHqnH/view")],
    6: [("Thư mục “8 Báo cáo Đảm bảo mẫu” của Quỳnh", "https://drive.google.com/drive/folders/1VsCqdlv7Ok0nBSkc29RgmoxnacDi12tb")],
    7: [("Thư mục “Mục 7” của Quỳnh", "https://drive.google.com/drive/folders/1Kl_wP6nqg3fH0gIFODNHh8jZi9Q__Z1a")],
}
NOTE = {  # đối chiếu 12/11
    5: "Đối chiếu 12/11: bản Thảo đưa lên Drive trùng md5 với bản trong repo.",
    6: "Đối chiếu 12/11: thư mục của Quỳnh có bộ 8 báo cáo này (trùng md5 với repo). Quỳnh gom thêm 4 báo cáo PTBV Việt Nam "
       "có tờ đảm bảo (ACB 2023, Novaland 2021, VPBank 2025, PVCFC 2025) và 2 ảnh tờ đảm bảo Vinamilk 2022; kết quả đọc "
       "từng tờ ghi ở data/standards/assurance_vn/bao_cao_dam_bao_vn.yaml, dùng cho việc 3 và 47.",
    7: "Đối chiếu 12/11: thư mục “Mục 7” của Quỳnh có đúng 2 tệp này, trùng md5 với repo.",
    57: "Lưu ý 12/11: lượt chạy có bật AI (ad323c772d064015) còn 3 chỗ số kiểu Anh (“7,085”) trong lời giải thích do mô hình "
        "viết; bản mặc định (tắt AI) không bị.",
    61: "Bộ kiểm điểm yếu (mục E2) vẫn báo “chưa có” vì chỉ tìm tệp tên *ablation*; số đo nằm ở khối llm_stages_v1.",
}
P = "src/quantum_gw/"
FILES = {
    1: [P + "parsers/documents.py", P + "parsers/ocr.py", P + "parsers/text_quality.py"],
    4: [P + "agents/orchestrator.py", P + "domain/models.py"],
    8: [P + "parsers/documents.py", P + "parsers/ocr.py"],
    9: [P + "parsers/documents.py", P + "storage/documents.py", P + "agents/reporter.py", P + "agents/reviewer.py"],
    11: [P + "parsers/documents.py", P + "studio/document.py"],
    49: [P + "parsers/integrity.py", P + "agents/intake.py", "tests/test_security_prompt_injection.py"],
    50: [P + "parsers/ocr.py", P + "agents/reviewer.py", "tests/test_ocr_confidence.py"],
    56: [P + "agents/claim_quality.py", "tests/test_claim_quality.py"],
    5: ["data/standards/iaasb/IAASB-International-Standard-on-Sustainability-Assurance-ISSA-5000.pdf", "data/standards/iaasb/README.md"],
    6: ["data/standards/iaasb/IAASB-ISSA-5000-Sustainability-Assurance-Illustrative-Reports.pdf",
        "data/standards/assurance_vn/bao_cao_dam_bao_vn.yaml"],
    7: ["data/standards/iaasb/IAASB-ISSA-5000-Sustainability-Frequently-Asked-Questions-FAQ-Materiality.pdf",
        "data/standards/iaasb/IAASB-ISSA-5000-Implementation-Guide-Sustainability-Assurance.pdf"],
    48: ["data/standards/iaasb/IAASB-International-Standard-on-Sustainability-Assurance-ISSA-5000.pdf"],
    28: ["data/standards/iaasb/README.md", "data/standards/iaasb/issa_samples_labels.yaml"],
    12: ["configs/issa5000_report_elements.yaml", "tests/test_issa5000_patterns.py"],
    13: ["configs/issa5000_conclusion_patterns.yaml", "tests/test_issa5000_patterns.py"],
    14: ["configs/issa5000_conclusion_patterns.yaml", "tests/test_issa5000_patterns.py"],
    18: [P + "agents/figures.py", P + "agents/verifier.py"],
    27: [P + "agents/reporter.py", P + "agents/prioritizer.py"],
    34: [P + "labels_vi.py", P + "agents/reporter.py", P + "studio/report.py", "tests/test_disclaimer.py"],
    35: [P + "api.py"],
    43: ["docs/02-product/HUONG_DAN_SU_DUNG_1_TRANG.md"],
    45: ["docs/02-product/HUONG_DAN_SU_DUNG_1_TRANG.md", "docs/02-product/MVP_SCOPE.md"],
    57: ["tests/test_ui_language.py", "tools/check_ui_language.py"],
    58: ["tools/check_weaknesses.py", "benchmark/weakness_check_2026-11-12.json", "docs/10-chung-ket-2026-11/DIEM_YEU_2026-11-11.md"],
    61: ["configs/measurement_decisions.yaml", "benchmark/llm_stages/score.py", "experiments/AI-RUN/make_kaggle.py", "docs/RUNS.md"],
}
CHECK = {
    12: "pytest tests/test_issa5000_patterns.py", 13: "pytest tests/test_issa5000_patterns.py",
    14: "pytest tests/test_issa5000_patterns.py", 34: "pytest tests/test_disclaimer.py",
    49: "pytest tests/test_security_prompt_injection.py", 50: "pytest tests/test_ocr_confidence.py",
    56: "pytest tests/test_claim_quality.py", 57: "pytest tests/test_ui_language.py; python tools/check_ui_language.py",
    58: "python tools/check_weaknesses.py",
}


def build(work, tests):
    import openpyxl
    work.mkdir(parents=True, exist_ok=True)
    ws = openpyxl.load_workbook(ROOT / "docs/00-project/Viec_can_lam_ISSA5000_cap-nhat_2026-11-11_chieu.xlsx").worksheets[0]
    task = {int(r[0]): str(r[1]) for r in ws.iter_rows(min_row=2, values_only=True) if isinstance(r[0], (int, float))}
    prog = {x["stt"]: x["tien_do"] for x in json.loads((MC / "cap_nhat_bang_2026-11-12.json").read_text("utf-8"))["dong"]}
    imgs = {int(p.stem.split("-")[1]) for p in MC.glob("viec-*.png")}
    e = html.escape
    out = []
    for title, items in GROUPS:
        h = [f"<h1>{e(title)}</h1>",
             f"<p>Đội AQ2026-119, GreenScan AI. Tài liệu ghi lại thành phẩm của các việc đã đánh dấu “Đã hoàn thành” trong "
             f"<a href='{SHEET}'>checklist công việc</a>. Đối chiếu ngày 12/11/2026: việc làm trong mã nguồn được kiểm "
             f"bằng tệp trong repo GreenScan-AI và bài kiểm ({e(tests)}); việc của thành viên được kiểm bằng tệp thành phẩm "
             f"trên Drive (so md5 với bản trong repo).</p>"]
        for n in items:
            h.append(f"<h2>Việc {n}</h2>")
            h.append(f"<p><b>Yêu cầu.</b> {e(task.get(n, ''))}</p>")
            h.append(f"<p><b>Người làm.</b> {e(OWNER.get(n, ME))}</p>")
            body = prog.get(n, "").replace("\n", " ")
            h.append(f"<p><b>Đã làm.</b> {e(body)}</p>")
            if n in NOTE:
                h.append(f"<p><b>Ghi chú.</b> {e(NOTE[n])}</p>")
            fl = [f for f in FILES.get(n, []) if (ROOT / f).exists()]
            miss = [f for f in FILES.get(n, []) if not (ROOT / f).exists()]
            if miss:
                print("THIẾU", n, miss)
            if fl or n in DRIVE:
                h.append("<p><b>Thành phẩm.</b></p><ul>")
                h += [f"<li>{e(t)}: <a href='{u}'>{u}</a></li>" for t, u in DRIVE.get(n, [])]
                h += [f"<li>Repo GreenScan-AI: {e(f)}</li>" for f in fl]
                h.append("</ul>")
            if n in CHECK:
                h.append(f"<p><b>Cách kiểm lại.</b> {e(CHECK[n])}</p>")
            if n in imgs:
                h.append(f"<p><b>Ảnh minh chứng.</b></p><p><img src='{RAW.format(n)}' width='620'></p>")
        name = title
        path = work / (f"nhom_{GROUPS.index((title, items)) + 1}.html")
        path.write_text("<html><head><meta charset='utf-8'></head><body>" + "\n".join(h) + "</body></html>", "utf-8")
        out.append({"name": name, "file": path.name, "items": items})
    (work / "manifest.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), "utf-8")
    print(len(out), "tài liệu ->", work)


def upload(work, tok, root):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build as gbuild
    from googleapiclient.http import MediaFileUpload
    c = Credentials.from_authorized_user_file(tok)
    if not c.valid:
        c.refresh(Request())
        open(tok, "w").write(c.to_json())
    s = gbuild("drive", "v3", credentials=c, cache_discovery=False)

    def find(name, parent, mime):
        q = f"name='{name}' and '{parent}' in parents and mimeType='{mime}' and trashed=false"
        r = s.files().list(q=q, fields="files(id)").execute()["files"]
        return r[0]["id"] if r else None
    fmime, dmime = "application/vnd.google-apps.folder", "application/vnd.google-apps.document"
    fid = find(FOLDER, root, fmime) or s.files().create(
        body={"name": FOLDER, "mimeType": fmime, "parents": [root]}, fields="id").execute()["id"]
    res = {"thu_muc": f"https://drive.google.com/drive/folders/{fid}", "tai_lieu": []}
    for d in json.loads((work / "manifest.json").read_text("utf-8")):
        media = MediaFileUpload(str(work / d["file"]), mimetype="text/html", resumable=False)
        old = find(d["name"].replace("'", "\\'"), fid, dmime)
        if old:  # cập nhật nội dung, giữ nguyên link
            r = s.files().update(fileId=old, media_body=media, fields="id,webViewLink").execute()
        else:
            r = s.files().create(body={"name": d["name"], "mimeType": dmime, "parents": [fid]}, media_body=media,
                                 fields="id,webViewLink").execute()
        res["tai_lieu"].append({"ten": d["name"], "viec": d["items"], "link": r["webViewLink"], "id": r["id"]})
        print("ok", d["name"], flush=True)
    (MC / "thanh_pham_drive_2026-11-12.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), "utf-8")
    print(res["thu_muc"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "build":
        build(Path(sys.argv[2]), sys.argv[3])
    else:
        upload(Path(sys.argv[2]), sys.argv[3], sys.argv[4])
