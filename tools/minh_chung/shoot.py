"""Chụp ảnh minh chứng: giao diện thật (app chạy ở localhost:8000) và các thẻ HTML do build_cards.py dựng.

    python tools/minh_chung/shoot.py ui    <thư_mục_làm_việc> <thư_mục_ảnh>
    python tools/minh_chung/shoot.py cards <thư_mục_làm_việc> <thư_mục_ảnh>
Cần Python có playwright và Chromium cục bộ (như tools/capture_all_screens.py).
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
MODE, WORK, OUT = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)
CHROME = r"C:\Users\ASUS\AppData\Local\ms-playwright\chromium-1228\chrome-win64\chrome.exe"
URL, RUN = "http://localhost:8000", "/#/runs/ad323c772d064015"


def go(page, path, wait=2500):
    page.goto(URL + path, wait_until="networkidle")
    page.wait_for_timeout(wait)
    page.evaluate("window.scrollTo(0,0)")


with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    if MODE == "ui":
        page = b.new_page(viewport={"width": 1366, "height": 900}, locale="vi-VN")
        go(page, "/", 1500)
        start = page.get_by_role("button", name="Bắt đầu phiên làm việc")
        if start.count():
            page.locator("input").first.fill("Nhân")
            start.first.click()
            page.wait_for_timeout(1500)
        go(page, RUN)
        page.screenshot(path=str(OUT / "viec-27.png"))
        print("[shot] viec-27 hàng đợi (trang, câu gốc, lý do)", flush=True)
        page.screenshot(path=str(OUT / "viec-34.png"), clip={"x": 0, "y": 0, "width": 1366, "height": 330})
        print("[shot] viec-34 câu lưu ý đầu trang", flush=True)
        go(page, RUN + "/claims", 2000)
        page.screenshot(path=str(OUT / "viec-57.png"))
        print("[shot] viec-57 danh sách tuyên bố (tên kết luận, số kiểu Việt)", flush=True)
        go(page, RUN)
        opener = page.locator("li button, li a").filter(has_text="Mở")
        if not opener.count():
            print("buttons on queue page:", [t[:30] for t in page.locator("button, a").all_inner_texts()][:40], flush=True)
        opener.first.click()
        page.wait_for_timeout(2500)
        page.screenshot(path=str(WORK / "ui_ai_detail.png"))
        print("[shot] ui_ai_detail (chi tiết mục 1 hàng đợi, lượt có AI)", flush=True)
    else:
        page = b.new_page(viewport={"width": 1120, "height": 800}, device_scale_factor=1)
        for h in sorted((WORK / "cards").glob("*.html")):
            page.goto(h.as_uri(), wait_until="load")
            page.wait_for_timeout(200)
            page.locator(".card").screenshot(path=str(OUT / f"viec-{h.stem}.png"))
            print("[shot] viec-" + h.stem, flush=True)
    b.close()
