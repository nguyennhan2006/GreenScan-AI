"""Soạn bản cập nhật bảng "Việc cần làm ISSA 5000" (Google Sheets) từng dòng: Trạng thái, Tiến độ, ảnh minh chứng.

Nguồn: bản tải về của Google Sheet (thứ tự dòng hiện tại), bản xlsx tối 11/11 trong repo (ghi chú [11/11 tối]), các ghi
chú 12/11 bên dưới, và ảnh docs/00-project/minh-chung/viec-XX.png đã đẩy lên nhánh minh-chung (link công khai).

    .venv/Scripts/python.exe -I tools/minh_chung/plan_sheet.py <google_sheet.xlsx>
      -> docs/00-project/minh-chung/cap_nhat_bang_2026-11-12.json
"""
import json
import re
import sys
from pathlib import Path

import openpyxl

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
RAW = "https://raw.githubusercontent.com/nguyennhan2006/GreenScan-AI/minh-chung/docs/00-project/minh-chung/viec-{:02d}.png"
IMGS = {int(p.stem.split("-")[1]) for p in (ROOT / "docs/00-project/minh-chung").glob("viec-*.png")}
DONE = "Ðã hoàn thành"   # đúng ký tự Ð mà bảng đang dùng, để danh sách thả xuống vẫn khớp

OVERRIDE = {  # 12/11/2026
    3: (None, "Thảo đã có thành phẩm “GreenScan - Phan Thanh Thảo - Báo cáo đảm bảo độc lập & đối chứng AI” (tệp không nằm "
              "trong repo: Thảo bổ sung ảnh minh chứng). Lưu ý: việc 47 (phân loại chuẩn của tờ xác nhận) vẫn chưa làm."),
    39: (None, "[12/11] Đã chạy hệ mới nhất có AI trên Hòa Phát (Kaggle T4, Qwen3-4B Q4, cùng tệp mô hình của sản phẩm): "
               "713 cặp luật bỏ ngỏ do mô hình đọc, bộ đọc kép 13 đoạn, 8 lời giải thích cho 8 mục hàng đợi; 0 kết luận "
               "“được ủng hộ” hay “mâu thuẫn” mới. Còn: chạy trên các báo cáo mẫu khác."),
    61: (DONE, "[12/11] Xong: từng tầng AI đo so với luật (khối llm_stages_v1, nhãn Claude): chấm quan hệ (S5) và lời giải "
               "thích (S6) qua cổng; thuộc tính (S2) và mô hình lọc câu (S1) không qua nên tắt. Hòa Phát hai nhánh trên cùng "
               "máy T4: chỉ luật 159,9 s, có AI 678,4 s (gấp 4,24); 8 tuyên bố mơ hồ hạ về “chưa đủ bằng chứng”; "
               "evaluate-real giống nhau 4/4. Cờ AI vẫn mặc định tắt trong sản phẩm."),
}

gs = openpyxl.load_workbook(sys.argv[1]).worksheets[0]
local = openpyxl.load_workbook(ROOT / "docs/00-project/Viec_can_lam_ISSA5000_cap-nhat_2026-11-11_chieu.xlsx").worksheets[0]
notes = {int(r[0]): str(r[7] or "") for r in local.iter_rows(min_row=2, values_only=True) if isinstance(r[0], (int, float))}
rows = []
for i, r in enumerate(gs.iter_rows(min_row=2, values_only=True), start=2):
    if not isinstance(r[0], (int, float)):
        continue
    stt, status, old = int(r[0]), r[4], str(r[7] or "")
    new = notes.get(stt, old)
    if status == DONE and "[11/11 tối]" in new:            # bỏ chữ "Chưa làm." cũ, giữ phần đã xong
        new = new.split("[11/11 tối]")[-1].strip()
    new_status, text = OVERRIDE.get(stt, (None, None))
    if text:
        new = text if stt != 39 else (old + "\n" + text)
    status2 = new_status or status
    img = f'=IMAGE("{RAW.format(stt)}")' if stt in IMGS and status2 == DONE else (
        "Cần Thảo bổ sung ảnh thành phẩm" if stt == 3 else "")
    new = re.sub(r"\n{2,}", "\n", new).strip()
    if new != old.strip() or status2 != status or img:
        rows.append({"row": i, "stt": stt, "trang_thai_cu": status, "trang_thai": status2, "tien_do": new, "anh": img})
out = ROOT / "docs/00-project/minh-chung/cap_nhat_bang_2026-11-12.json"
out.write_text(json.dumps({"sheet": "Trang tính3", "cot_anh": "I", "tieu_de_cot_anh": "Minh chứng (ảnh)", "dong": rows},
                          ensure_ascii=False, indent=1), encoding="utf-8")
print(len(rows), "dòng đổi;", sum(1 for x in rows if x["anh"].startswith("=IMAGE")), "ảnh;",
      "đổi trạng thái:", [(x["stt"], x["trang_thai_cu"], x["trang_thai"]) for x in rows if x["trang_thai"] != x["trang_thai_cu"]])
print("->", out)
