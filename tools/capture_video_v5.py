"""Chụp màn hình cho video demo bản chậm (greenscan-demo-ck-cham): phiên mới, mỗi ảnh kèm toạ độ phần tử (boxes.json).

Mở rộng tools/capture_demo_screens.py (v4) — giữ tên ảnh và khoá box của v4, thêm: hướng dẫn lần đầu, tab ngoài hàng đợi,
trang Tất cả tuyên bố + bộ lọc, tab Pháp lý, tab Rủi ro, Studio.
Cần: app ở localhost:8000 chạy với QUANTUM_ORG_PACKS=configs/org_packs/demo_ngan_hang_xanh; Python có playwright.
Chạy:  python tools/capture_video_v5.py <thư_mục_ra>      (ảnh PNG 3840x2160 + boxes.json; workpaper 1280x720 tỉ lệ 3)
"""
import json, re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
CHROME = r"C:\Users\ASUS\AppData\Local\ms-playwright\chromium-1228\chrome-win64\chrome.exe"
URL = "http://localhost:8000"
SRC = ROOT / "data" / "real_cases" / "sources" / "originals"
SR, AR = str(SRC / "HPG_Sustainability_Report_2025.pdf"), str(SRC / "HPG_Annual_Report_2024.pdf")
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


def shot(page, name, boxes=(), kind="app", wait=450):
    page.wait_for_timeout(wait)
    page.screenshot(path=str(OUT / f"{name}.png"))
    for key, loc in boxes:
        box(page, name, key, loc, kind)
    print(f"[shot] {name} boxes={list(BOX.get(name, {}).keys())}", flush=True)


def step(title, fn):
    try:
        fn()
    except Exception as exc:  # noqa: BLE001
        print(f"[skip] {title}: {exc!r}"[:300], flush=True)


def scroll_text(page, text, off=-90):
    ok = page.evaluate("""([t, off]) => {
      const el = [...document.querySelectorAll('h1,h2,h3,h4,p,span,button,section,div')].find(e => e.childElementCount < 6 && e.innerText && e.innerText.trim().startsWith(t));
      if (!el) return false; window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY + off); return true }""", [text, off])
    page.wait_for_timeout(700)
    return ok


def txt(page, t, exact=False):
    return page.get_by_text(t, exact=exact)


def starts(page, label, tag="button"):
    return page.locator(tag).filter(has_text=re.compile(r"^\s*" + re.escape(label)))


def anc(loc, n):
    return loc.locator(f"xpath=ancestor::div[{n}]")


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    ctx = browser.new_context(viewport={"width": 1536, "height": 864}, device_scale_factor=2.5, locale="vi-VN")
    page = ctx.new_page()
    S = {}

    # ---- bắt đầu + hướng dẫn lần đầu
    page.goto(URL, wait_until="networkidle"); page.wait_for_timeout(800)
    name_in = page.get_by_placeholder("Ví dụ: Quỳnh, Thảo, Nhân")
    shot(page, "a01_start", [("name_input", name_in), ("start_btn", page.locator("button[type=submit]"))])
    name_in.fill("Nhân")
    shot(page, "a02_start_named", [("name_input", name_in), ("start_btn", page.locator("button[type=submit]"))])
    page.locator("button[type=submit]").first.click(); page.wait_for_timeout(1800)
    shot(page, "a00_guide", [("title", page.locator("main h1, h1").first), ("steps", page.locator("main ol, main ul").first),
                             ("main", page.locator("main").first)])
    page.evaluate("try { localStorage.setItem('gs.guide.seen', '1') } catch (e) {}")

    # ---- bước 1
    page.goto(URL + "/#/new", wait_until="networkidle"); page.wait_for_timeout(1200)
    shot(page, "a03_new_empty", [("dropzone", txt(page, "Kéo thả tệp")), ("company", page.get_by_placeholder("Ví dụ: Hòa Phát", exact=True)),
                                 ("label", page.get_by_placeholder("Ví dụ: Hòa Phát – báo cáo bền vững 2025 + báo cáo thường niên 2024")),
                                 ("offline_chip", txt(page, "Ngoại tuyến — không gửi tài liệu ra ngoài")),
                                 ("sidebar_steps", txt(page, "Quy trình", exact=True))])
    page.get_by_placeholder("Ví dụ: Hòa Phát", exact=True).fill("Tập đoàn Hòa Phát")
    page.get_by_placeholder("Ví dụ: Hòa Phát – báo cáo bền vững 2025 + báo cáo thường niên 2024").fill(
        "DEMO bản chậm — Hòa Phát: báo cáo bền vững 2025 + thường niên 2024")
    page.locator("input[type=file]").set_input_files([SR, AR]); page.wait_for_timeout(2500)
    rows = page.locator("ul li:has(button[aria-label^='Bỏ'])")
    rows.nth(1).get_by_role("button", name="Đối chiếu").click(); page.wait_for_timeout(800)
    shot(page, "a04_new_filled", [("row_sr", rows.nth(0)), ("row_ar", rows.nth(1)),
                                  ("role_sr_canKiem", rows.nth(0).get_by_role("button", name="Cần kiểm")),
                                  ("role_ar_doiChieu", rows.nth(1).get_by_role("button", name="Đối chiếu")),
                                  ("offline_note", txt(page, "Ngoại tuyến — không gửi tài liệu ra ngoài").last),
                                  ("start_btn", page.get_by_role("button", name="Bắt đầu phân tích"))])
    page.get_by_role("button", name="Bắt đầu phân tích").click()
    t0 = time.time(); marks = [4, 25, 60, 110]
    for _ in range(400):
        page.wait_for_timeout(1000)
        el = int(time.time() - t0)
        if marks and el >= marks[0]:
            marks.pop(0)
            if page.locator("text=Đang phân tích").count():
                shot(page, f"a05_progress_{el:03d}s", [("progress_card", txt(page, "Đang phân tích"))], wait=0)
        if "#/runs/" in page.url and page.locator("text=Đang phân tích").count() == 0:
            break
    NOTES["analysis_seconds"] = round(time.time() - t0, 1)
    run_url = page.url.split("?")[0]; run_id = run_url.rsplit("/", 1)[-1]; NOTES["run_id"] = run_id
    RUN = "/#/runs/" + run_id
    print(f"[run] {run_id} {NOTES['analysis_seconds']}s", flush=True)

    # ---- bước 2: hàng đợi
    page.wait_for_timeout(2500); page.evaluate("window.scrollTo(0,0)")
    items = page.locator("li:has(button:text-is('Mở'))")
    shot(page, "b01_queue", [("kpi_row", anc(txt(page, "Kiểm trước nhất"), 3)),
                             ("tab_queue", starts(page, "Cần soát")), ("tab_seen", starts(page, "Đã xem, chưa chốt")),
                             ("tab_done", starts(page, "Đã chốt")), ("tab_outside", starts(page, "Ngoài hàng đợi")),
                             ("item1", items.nth(0)), ("item2", items.nth(1)), ("item3", items.nth(2)),
                             ("item2_open", items.nth(1).get_by_role("button", name="Mở")),
                             ("score_item2", items.nth(1).locator("p.font-mono")),
                             ("order_note", txt(page, "Thứ tự là thứ tự nên mở")),
                             ("offline_chip", txt(page, "Ngoại tuyến — không gửi tài liệu ra ngoài")),
                             ("sidebar_steps", txt(page, "Quy trình", exact=True)),
                             ("nav_claims", page.get_by_text("Tất cả tuyên bố").first)])
    NOTES["tabs"] = page.locator("button").filter(has_text=re.compile(r"\(\d+\)")).all_inner_texts()[:8]
    NOTES["queue_item_texts"] = [items.nth(i).inner_text()[:220] for i in range(min(3, items.count()))]
    def rest():
        starts(page, "Ngoài hàng đợi").first.click(); page.wait_for_timeout(1000)
        ri = page.locator("li").filter(has=page.locator("button:text-is('Mở')"))
        shot(page, "b03_queue_rest", [("tab_outside", starts(page, "Ngoài hàng đợi")), ("rest1", ri.nth(0)), ("rest2", ri.nth(1)), ("rest3", ri.nth(2))])
        NOTES["rest_texts"] = [ri.nth(i).inner_text()[:200] for i in range(min(2, ri.count()))]
        starts(page, "Cần soát").first.click(); page.wait_for_timeout(700)
    step("rest", rest)
    scroll_text(page, "Phạm vi lượt soát này")
    shot(page, "b02_queue_scope", [("scope_box", txt(page, "Phạm vi lượt soát này").locator("xpath=..")),
                                   ("procedures_box", txt(page, "Thủ tục trên số liệu công bố").locator("xpath=.."))])
    page.evaluate("window.scrollTo(0,0)"); page.wait_for_timeout(400)

    # ---- tất cả tuyên bố
    def claims():
        page.goto(URL + RUN + "/claims", wait_until="networkidle"); page.wait_for_timeout(1800)
        filt = page.locator("button").filter(has_text=re.compile(r"\(\d+\)\s*$"))
        table = page.locator("table").first
        search = page.get_by_placeholder(re.compile("Tìm")).first
        shot(page, "e01_claims_all", [("filters", anc(filt.first, 1)), ("table", table), ("search", search),
                                      ("f_unresolved", starts(page, "Chưa xử lý")), ("f_contra", starts(page, "Có mâu thuẫn")),
                                      ("f_noev", starts(page, "Thiếu bằng chứng"))])
        NOTES["claim_filters"] = filt.all_inner_texts()
        starts(page, "Thiếu bằng chứng").first.click(); page.wait_for_timeout(900)
        shot(page, "e02_claims_filter", [("filters", anc(filt.first, 1)), ("f_noev", starts(page, "Thiếu bằng chứng")), ("table", table)])
        starts(page, "Tất cả").first.click(); page.wait_for_timeout(600)
        search.fill("năng lượng"); page.wait_for_timeout(900)
        shot(page, "e03_claims_search", [("search", search), ("table", table)])
    step("claims", claims)

    # ---- mục #2
    page.goto(run_url, wait_until="networkidle"); page.wait_for_timeout(2200); page.evaluate("window.scrollTo(0,0)")
    items = page.locator("li:has(button:text-is('Mở'))")
    items.nth(1).get_by_role("button", name="Mở").click(); page.wait_for_timeout(2200)
    NOTES["item_url"] = page.url
    shot(page, "c01_item_top", [("claim_card", page.locator("article").first), ("verdict_badge", txt(page, "Ủng hộ một phần")),
                                ("quote", page.locator("article blockquote, article p").first), ("tabs", page.locator("nav").last)])
    tabs = page.locator("nav button")
    tabs.filter(has_text="Thuộc tính").first.click(); page.wait_for_timeout(1200)
    shot(page, "c02_attributes", [("attr_list", txt(page, "Thuộc tính bắt buộc").locator("xpath=..")),
                                  ("attr_metric", txt(page, "Chỉ số cụ thể")), ("attr_baseline", txt(page, "Năm gốc").first),
                                  ("attr_period", txt(page, "Kỳ báo cáo").first), ("attr_scope", txt(page, "Phạm vi / ranh giới")),
                                  ("attr_evidence", txt(page, "Bằng chứng & phương pháp")),
                                  ("values_panel", txt(page, "Giá trị trích xuất").locator("xpath=.."))])
    def evidence():
        tabs.filter(has_text="Bằng chứng").first.click(); page.wait_for_timeout(1200)
        ev_card = page.locator("li, article, div.rounded-lg").filter(has_text="TỰ CHỦ 90%").last
        open_btn = ev_card.get_by_role("button", name="Mở nguồn")
        open_btn.scroll_into_view_if_needed(); page.evaluate("window.scrollBy(0,-300)"); page.wait_for_timeout(600)
        shot(page, "c03_evidence", [("evidence_card_p86", ev_card), ("open_source_btn", open_btn), ("evidence_header", txt(page, "5 đoạn").first)])
        open_btn.click(); page.wait_for_timeout(4000)
        shot(page, "c04_source", [("viewer", page.locator("[role=dialog], .fixed").last),
                                  ("page_image", page.locator("[role=dialog] img, .fixed img").first),
                                  ("highlight", page.locator(".fixed [class*='yellow'], .fixed [class*='amber'], .fixed mark, [role=dialog] [class*='yellow']").first),
                                  ("sha256", txt(page, "sha256").last), ("page_label", txt(page, "trang 86").first),
                                  ("quote_panel", txt(page, "ĐOẠN TRÍCH").first)])
        page.keyboard.press("Escape"); page.wait_for_timeout(800)
        if page.get_by_role("button", name="Đóng").count():
            page.get_by_role("button", name="Đóng").first.click(); page.wait_for_timeout(600)
    step("evidence", evidence)
    def numeric():
        tabs.filter(has_text="Kiểm tra số").first.click(); page.wait_for_timeout(1000)
        shot(page, "c05_numeric", [("numeric_box", txt(page, "Kiểm tra số liệu").locator("xpath=../.."))])
    step("numeric", numeric)
    def legal():
        tabs.filter(has_text="Pháp lý").first.click(); page.wait_for_timeout(1100)
        lb = txt(page, "Bối cảnh pháp lý").locator("xpath=../..")
        shot(page, "c05b_legal", [("legal_box", lb), ("legal_issue", txt(page, "Vấn đề pháp lý").first),
                                  ("legal_mode", txt(page, "Chế độ").first), ("legal_docs", lb.locator("ul, ol").first),
                                  ("legal_note", lb.get_by_text(re.compile("chưa có")).first)])
        NOTES["legal_text"] = lb.inner_text()[:900]
    step("legal", legal)
    def org():
        tabs.filter(has_text="Quy tắc nội bộ").first.click(); page.wait_for_timeout(1200)
        o = page.locator("#sec-org")
        shot(page, "c06_org", [("org_section", o), ("org_notice", o.locator("p").first),
                               ("org_f1_violation", o.locator("li").nth(0)), ("org_f2_review", o.locator("li").nth(1)),
                               ("org_f3_ok", o.locator("li").nth(2))])
        NOTES["org_text"] = o.inner_text()[:700]
    step("org", org)
    def risk():
        tabs.filter(has_text="Rủi ro").first.click(); page.wait_for_timeout(1200)
        rb = txt(page, "Phân rã rủi ro").locator("xpath=../..")
        tb = txt(page, "Việc cần làm để tuyên bố kiểm chứng được").locator("xpath=../..")
        shot(page, "c07_risk_todo", [("risk_box", rb), ("todo_box", tb),
                                     ("risk_attrs", txt(page, "5 thuộc tính bắt buộc").locator("xpath=..")),
                                     ("risk_signals", txt(page, "Tín hiệu cần lưu ý").last.locator("xpath=..")),
                                     ("risk_footer", rb.get_by_text(re.compile("^Tổng")).first),
                                     ("todo_item1", tb.locator("li").first), ("todo_fix", tb.locator("li p.font-mono").first)])
        NOTES["risk_text"] = rb.inner_text()[:700]
    step("risk", risk)
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
    starts(page, "Đã xem, chưa chốt").first.click(); page.wait_for_timeout(900)
    shot(page, "d01_queue_after", [("tab_reviewed", starts(page, "Đã xem, chưa chốt")),
                                   ("item_reviewed", page.locator("li:has(button:text-is('Mở'))").first)])

    # ---- bước 3: Studio
    def studio():
        page.goto(URL + RUN + "/studio", wait_until="networkidle"); page.wait_for_timeout(3500)
        for i in range(6):
            card = page.locator("div.fixed").filter(has_text="Hướng dẫn").last
            shot(page, f"s0{i + 1}_studio_tour", [("tour_card", card), ("explorer", page.locator("[data-tour=explorer]")),
                                                  ("editor", page.locator("[data-tour=editor]")), ("bottom", page.locator("[data-tour=bottom]")),
                                                  ("target", page.locator(".gs-tour-target"))])
            nxt = page.locator("button").filter(has_text=re.compile(r"^\s*Tiếp\s*$"))
            if nxt.count():
                nxt.first.click(); page.wait_for_timeout(700); continue
            page.locator("button").filter(has_text=re.compile(r"^\s*Bắt đầu\s*$")).first.click(); page.wait_for_timeout(1000)
            break
        insp = anc(txt(page, "Bảng chi tiết", exact=False).first, 1)
        shot(page, "s10_studio_main", [("explorer", page.locator("[data-tour=explorer]")), ("editor", page.locator("[data-tour=editor]")),
                                       ("bottom", page.locator("[data-tour=bottom]")), ("inspector", insp),
                                       ("docs", txt(page, "Tài liệu (2)").locator("xpath=..")),
                                       ("problems", txt(page, "Vấn đề phát hiện").locator("xpath=../..")),
                                       ("first_item", page.locator("[data-tour=explorer] li").nth(2)),
                                       ("open_first", page.get_by_role("button", name=re.compile("Mở mục đầu tiên")))])
        page.get_by_role("button", name=re.compile("Mở mục đầu tiên")).first.click(); page.wait_for_timeout(1800)
        acc = page.locator("[title^='Áp dụng đề xuất vào văn bản']").first
        card = acc.locator("xpath=ancestor::div[contains(@class,'rounded')][1]")
        shot(page, "s11_studio_item", [("editor", page.locator("[data-tour=editor]")), ("inspector", insp),
                                       ("sugg_card", card), ("btn_accept", acc),
                                       ("btn_reject", page.locator("[title^='Bỏ đề xuất này']").first),
                                       ("btn_edit", page.locator("[title^='Sửa câu đề xuất']").first),
                                       ("reason", txt(page, "Lý do:").first.locator("xpath=..")),
                                       ("verdict_head", insp.locator("h2, h3, p.text-2xl, p.text-xl").first),
                                       ("mark", page.locator("[data-tour=editor] .cm-gs-sel, [data-tour=editor] mark, [data-tour=editor] [class*='sel']").first)])
        acc.click(); page.wait_for_timeout(1800)
        shot(page, "s12_studio_applied", [("editor", page.locator("[data-tour=editor]")), ("bottom", page.locator("[data-tour=bottom]")),
                                          ("log_row", page.locator("[data-tour=bottom] tr").nth(1))])
        starts(page, "Bằng chứng").last.click(); page.wait_for_timeout(1200)
        shot(page, "s13_studio_evidence", [("inspector", insp), ("view_btn", page.locator("[title^='Xem trang gốc của bằng chứng']").first)])
        page.locator("[title^='Xem trang gốc của bằng chứng']").first.click(); page.wait_for_timeout(3500)
        shot(page, "s14_studio_viewer", [("viewer", page.locator("div.fixed").last), ("readonly", txt(page, "chỉ đọc").last)])
        page.keyboard.press("Escape"); page.wait_for_timeout(600)
    step("studio", studio)

    # ---- thư viện pháp lý, xuất, giấy làm việc
    def packs():
        page.goto(URL + "/#/legal", wait_until="networkidle"); page.wait_for_timeout(1500)
        scroll_text(page, "Quy tắc nội bộ của tổ chức", -40)
        pk = page.locator("#org-packs")
        shot(page, "f01_org_packs", [("pack_section", pk), ("pack_status", pk.get_by_text("Đã duyệt, đang áp dụng")),
                                     ("pack_rules", pk.locator("ul").first), ("notice", pk.locator("p").first)])
    step("packs", packs)
    page.goto(URL + RUN + "/export", wait_until="networkidle"); page.wait_for_timeout(1500)
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
        shot(wp, f"h{i + 1:02d}_wp", [("heading", wp.locator("h1,h2,h3").nth(i))], kind="wp")
    wp.evaluate("window.scrollTo(0, document.body.scrollHeight)"); wp.wait_for_timeout(600)
    shot(wp, "h99_wp_signature", [("sign", wp.get_by_text("Người soát xét").last)], kind="wp")
    wctx.close()

    json.dump({"scale_note": "boxes are [x, y, w, h] in screenshot pixels (3840x2160)", "boxes": BOX, "notes": NOTES},
              open(OUT / "boxes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("DONE", json.dumps(NOTES, ensure_ascii=False)[:400], flush=True)
    browser.close()
