"""Final capture for the demo video: fresh run, every screenshot saved together with the pixel boxes
# Copied from the video capture (05/11/2026). Expects files/HPG_*.pdf next to it and the app on localhost:8000;
# run with a Python that has playwright (executable_path points at a local Chromium build).
of the elements the video points at (boxes.json, image pixels in the 3840x2160 screenshot).

Viewport 1536x864 at scale 2.5 (= browser zoom 125% on a 1920x1080 screen). Workpaper: 1280x720 at 3.
"""
import json, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "final"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = r"C:\Users\ASUS\AppData\Local\ms-playwright\chromium-1228\chrome-win64\chrome.exe"
URL = "http://localhost:8000"
SR = str(HERE / "files" / "HPG_BaoCaoPhatTrienBenVung_2025.pdf")
AR = str(HERE / "files" / "HPG_BaoCaoThuongNien_2024.pdf")
BOX, NOTES = {}, {}
SCALE = {"app": 2.5, "wp": 3.0}


def box(page, name, key, loc, kind="app"):
    try:
        b = loc.first.bounding_box(timeout=4000)
    except Exception as exc:  # noqa: BLE001
        print(f"[nobox] {name}.{key}: {exc!r}"[:160], flush=True); return
    if not b:
        print(f"[nobox] {name}.{key}: none", flush=True); return
    s = SCALE[kind]
    BOX.setdefault(name, {})[key] = [round(b["x"] * s), round(b["y"] * s), round(b["width"] * s), round(b["height"] * s)]


def shot(page, name, boxes=(), kind="app"):
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUT / f"{name}.png"))
    for key, loc in boxes:
        box(page, name, key, loc, kind)
    print(f"[shot] {name} boxes={list(BOX.get(name, {}).keys())}", flush=True)


def scroll_text(page, text, off=-90):
    ok = page.evaluate("""([t, off]) => {
      const el = [...document.querySelectorAll('h1,h2,h3,h4,p,span,button,section,div')].find(e => e.childElementCount < 6 && e.innerText && e.innerText.trim().startsWith(t));
      if (!el) return false; window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY + off); return true }""", [text, off])
    page.wait_for_timeout(700)
    return ok


def txt(page, t, exact=False):
    return page.get_by_text(t, exact=exact)


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    ctx = browser.new_context(viewport={"width": 1536, "height": 864}, device_scale_factor=2.5, locale="vi-VN")
    ctx.add_init_script("try { localStorage.setItem('gs.guide.seen', '1') } catch (e) {}")  # bỏ qua trang hướng dẫn lần đầu
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle"); page.wait_for_timeout(800)
    name_in = page.get_by_placeholder("Ví dụ: Quỳnh, Thảo, Nhân")
    shot(page, "a01_start", [("name_input", name_in), ("start_btn", page.locator("button[type=submit]"))])
    name_in.fill("Nhân")
    shot(page, "a02_start_named", [("name_input", name_in), ("start_btn", page.locator("button[type=submit]"))])
    page.locator("button[type=submit]").first.click(); page.wait_for_timeout(1500)
    shot(page, "a03_new_empty", [("dropzone", txt(page, "Kéo thả tệp")), ("company", page.get_by_placeholder("Ví dụ: Hòa Phát", exact=True)),
                                 ("label", page.get_by_placeholder("Ví dụ: Hòa Phát – báo cáo bền vững 2025 + báo cáo thường niên 2024")),
                                 ("offline_chip", txt(page, "Ngoại tuyến — không gửi tài liệu ra ngoài")),
                                 ("steps_strip", txt(page, "Soát theo hàng đợi").last)])
    page.get_by_placeholder("Ví dụ: Hòa Phát", exact=True).fill("Tập đoàn Hòa Phát")
    page.get_by_placeholder("Ví dụ: Hòa Phát – báo cáo bền vững 2025 + báo cáo thường niên 2024").fill("DEMO Chung kết — Hòa Phát: báo cáo bền vững 2025 + thường niên 2024")
    page.locator("input[type=file]").set_input_files([SR, AR]); page.wait_for_timeout(2500)
    rows = page.locator("ul li:has(button[aria-label^='Bỏ'])")
    rows.nth(1).get_by_role("button", name="Đối chiếu").click(); page.wait_for_timeout(800)
    shot(page, "a04_new_filled", [("row_sr", rows.nth(0)), ("row_ar", rows.nth(1)),
                                  ("role_sr_canKiem", rows.nth(0).get_by_role("button", name="Cần kiểm")),
                                  ("role_ar_doiChieu", rows.nth(1).get_by_role("button", name="Đối chiếu")),
                                  ("offline_note", txt(page, "Ngoại tuyến — không gửi tài liệu ra ngoài").last),
                                  ("start_btn", page.get_by_role("button", name="Bắt đầu phân tích"))])
    page.get_by_role("button", name="Bắt đầu phân tích").click()
    started = time.time()
    for k in range(300):
        page.wait_for_timeout(2000)
        if k in (1, 10, 25, 50):
            shot(page, f"a05_progress_{int(time.time() - started):03d}s", [("progress_card", txt(page, "Đang phân tích"))])
        if "#/runs/" in page.url and page.locator("text=Đang phân tích").count() == 0:
            break
    NOTES["analysis_seconds"] = round(time.time() - started, 1)
    run_url = page.url.split("?")[0]; run_id = run_url.rsplit("/", 1)[-1]; NOTES["run_id"] = run_id
    page.wait_for_timeout(2500); page.evaluate("window.scrollTo(0,0)")
    items = page.locator("li:has(button:text-is('Mở'))")
    shot(page, "b01_queue", [("kpi_row", txt(page, "Kiểm trước nhất").locator("xpath=ancestor::div[3]")),
                             ("tab_queue", page.get_by_role("button", name="Cần soát (9)")),
                             ("tab_outside", page.get_by_role("button", name="Ngoài hàng đợi (163)")),
                             ("item1", items.nth(0)), ("item2", items.nth(1)), ("item3", items.nth(2)),
                             ("item2_open", items.nth(1).get_by_role("button", name="Mở")),
                             ("offline_chip", txt(page, "Ngoại tuyến — không gửi tài liệu ra ngoài")),
                             ("sidebar_steps", txt(page, "Quy trình", exact=True))])
    NOTES["queue_item_texts"] = [items.nth(i).inner_text()[:200] for i in range(min(3, items.count()))]
    scroll_text(page, "Phạm vi lượt soát này")
    shot(page, "b02_queue_scope", [("scope_box", txt(page, "Phạm vi lượt soát này").locator("xpath=..")),
                                   ("procedures_box", txt(page, "Thủ tục trên số liệu công bố").locator("xpath=.."))])
    page.evaluate("window.scrollTo(0,0)"); page.wait_for_timeout(400)

    items.nth(1).get_by_role("button", name="Mở").click(); page.wait_for_timeout(2200)
    NOTES["item_url"] = page.url
    shot(page, "c01_item_top", [("claim_card", page.locator("article").first), ("verdict_badge", txt(page, "Ủng hộ một phần")),
                                ("quote", page.locator("article blockquote, article p").first),
                                ("tabs", page.locator("nav").last)])
    tabs = page.locator("nav button")
    tabs.filter(has_text="Thuộc tính").first.click(); page.wait_for_timeout(1200)
    shot(page, "c02_attributes", [("attr_list", txt(page, "Thuộc tính bắt buộc").locator("xpath=..")),
                                  ("attr_metric", txt(page, "Chỉ số cụ thể")), ("attr_baseline", txt(page, "Năm gốc").first),
                                  ("attr_period", txt(page, "Kỳ báo cáo").first), ("attr_scope", txt(page, "Phạm vi / ranh giới")),
                                  ("attr_evidence", txt(page, "Bằng chứng & phương pháp")),
                                  ("values_panel", txt(page, "Giá trị trích xuất").locator("xpath=.."))])
    tabs.filter(has_text="Bằng chứng").first.click(); page.wait_for_timeout(1200)
    ev_card = page.locator("li, article, div.rounded-lg").filter(has_text="TỰ CHỦ 90%").last
    open_btn = ev_card.get_by_role("button", name="Mở nguồn")
    open_btn.scroll_into_view_if_needed(); page.evaluate("window.scrollBy(0,-300)"); page.wait_for_timeout(600)
    shot(page, "c03_evidence", [("evidence_card_p86", ev_card), ("open_source_btn", open_btn),
                                ("evidence_header", txt(page, "5 đoạn").first)])
    open_btn.click(); page.wait_for_timeout(4000)
    shot(page, "c04_source", [("viewer", page.locator("[role=dialog], .fixed").last),
                              ("page_image", page.locator("[role=dialog] img, .fixed img").first),
                              ("highlight", page.locator(".fixed [class*='yellow'], .fixed [class*='amber'], .fixed mark, [role=dialog] [class*='yellow']").first),
                              ("sha256", txt(page, "sha256").last), ("page_label", txt(page, "trang 86").first),
                              ("quote_panel", txt(page, "ĐOẠN TRÍCH").first)])
    page.keyboard.press("Escape"); page.wait_for_timeout(800)
    if page.get_by_role("button", name="Đóng").count():
        page.get_by_role("button", name="Đóng").first.click(); page.wait_for_timeout(600)
    tabs.filter(has_text="Kiểm tra số").first.click(); page.wait_for_timeout(1000)
    shot(page, "c05_numeric_legal", [("numeric_box", txt(page, "Kiểm tra số liệu").locator("xpath=../..")),
                                     ("legal_box", txt(page, "Bối cảnh pháp lý").locator("xpath=../.."))])
    tabs.filter(has_text="Quy tắc nội bộ").first.click(); page.wait_for_timeout(1200)
    org = page.locator("#sec-org")
    shot(page, "c06_org", [("org_section", org), ("org_notice", org.locator("p").first),
                           ("org_f1_violation", org.locator("li").nth(0)), ("org_f2_review", org.locator("li").nth(1)),
                           ("org_f3_ok", org.locator("li").nth(2))])
    tabs.filter(has_text="Rủi ro").first.click(); page.wait_for_timeout(1200)
    shot(page, "c07_risk_todo", [("risk_box", txt(page, "Phân rã rủi ro").locator("xpath=../..")),
                                 ("todo_box", txt(page, "Việc cần làm để tuyên bố kiểm chứng được").locator("xpath=../.."))])
    tabs.filter(has_text="Xét duyệt").first.click(); page.wait_for_timeout(1000)
    reason = page.get_by_placeholder("Lý do quyết định")
    reason.fill("Câu nêu 'rất cao' nhưng không có số, kỳ, năm gốc. BCTN 2024 tr. 86 ghi tỷ lệ tự chủ điện; "
                "đề nghị doanh nghiệp nêu số liệu năm 2025 và năm gốc.")
    req = page.get_by_role("button", name="Yêu cầu thêm bằng chứng")
    shot(page, "c08_review_filled", [("decision_bar", txt(page, "Quyết định của người xem xét").locator("xpath=../..")),
                                     ("reason", reason), ("btn_request", req),
                                     ("btn_confirm", page.get_by_role("button", name="Xác nhận kết luận AI"))])
    req.click(); page.wait_for_timeout(2200)
    shot(page, "c09_review_saved", [("decision_bar", txt(page, "Quyết định của người xem xét").locator("xpath=../..")),
                                    ("state_chip", txt(page, "Đã có người xem").first), ("history", txt(page, "Lịch sử").last)])
    page.goto(run_url, wait_until="networkidle"); page.wait_for_timeout(1800); page.evaluate("window.scrollTo(0,0)")
    shot(page, "d01_queue_after", [("tab_reviewed", page.locator("button").filter(has_text="Đã xem, chưa chốt"))])
    page.goto(URL + "/#/legal", wait_until="networkidle"); page.wait_for_timeout(1500)
    scroll_text(page, "Quy tắc nội bộ của tổ chức", -40)
    pk = page.locator("#org-packs")
    shot(page, "f01_org_packs", [("pack_section", pk), ("pack_status", pk.get_by_text("Đã duyệt, đang áp dụng")),
                                 ("pack_rules", pk.locator("ul").first), ("notice", pk.locator("p").first)])
    page.goto(run_url + "/export", wait_until="networkidle"); page.wait_for_timeout(1500)
    shot(page, "g01_export", [("open_wp", page.get_by_role("link", name="Mở giấy làm việc").or_(page.get_by_role("button", name="Mở giấy làm việc"))),
                              ("print", page.get_by_role("button", name="In / Lưu PDF").or_(page.get_by_role("link", name="In / Lưu PDF")))])

    wctx = browser.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=3, locale="vi-VN")
    wp = wctx.new_page()
    wp.goto(f"{URL}/api/v1/runs/{run_id}/workpaper", wait_until="networkidle"); wp.wait_for_timeout(1500)
    shot(wp, "h01_wp_top", [("title", wp.locator("h1").first), ("scope_table", wp.locator("table").nth(1))], kind="wp")
    heads = wp.evaluate("() => [...document.querySelectorAll('h1,h2,h3')].map(h => h.innerText.trim())")
    NOTES["workpaper_headings"] = heads
    for i, h in enumerate(heads[1:], 1):
        scroll_text(wp, h, -30)
        shot(wp, f"h{i+1:02d}_wp", [("heading", wp.locator("h1,h2,h3").nth(i))], kind="wp")
    wp.evaluate("window.scrollTo(0, document.body.scrollHeight)"); wp.wait_for_timeout(600)
    shot(wp, "h99_wp_signature", [("sign", wp.get_by_text("Người soát xét").last)], kind="wp")
    wctx.close()

    json.dump({"scale_note": "boxes are [x, y, w, h] in screenshot pixels (3840x2160)", "boxes": BOX, "notes": NOTES},
              open(OUT / "boxes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("DONE", json.dumps(NOTES, ensure_ascii=False)[:500], flush=True)
    browser.close()
