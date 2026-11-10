"""Chụp toàn bộ màn hình giao diện GreenScan (mọi trang, mọi tab, các trạng thái chính) để tổng hợp.

Cần: app đang chạy ở localhost:8000, Python có playwright (C:\\Python314), Chromium cục bộ.
Chạy:  python tools/capture_all_screens.py [thư_mục_ra]
Ra:    các tệp NN_ten.png + README.md (mục lục kèm chú thích) trong thư mục ra.
Mỗi bước bọc try/except: bước nào lỗi thì ghi [skip] và chạy tiếp.
"""
import re, sys, time, unicodedata
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "10-chung-ket-2026-11" / f"anh-chup-giao-dien-{time.strftime('%Y-%m-%d')}"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = r"C:\Users\ASUS\AppData\Local\ms-playwright\chromium-1228\chrome-win64\chrome.exe"
URL = "http://localhost:8000"
SRC = ROOT / "data" / "real_cases" / "sources" / "originals"
SR, AR = str(SRC / "HPG_Sustainability_Report_2025.pdf"), str(SRC / "HPG_Annual_Report_2024.pdf")
INDEX = []  # (section, file, caption)
N = [0]
SECTION = ["Chung"]


def slug(s):
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40]


def shot(page, name, caption, full=False, wait=500):
    page.wait_for_timeout(wait)
    N[0] += 1
    fn = f"{N[0]:02d}_{name}.png"
    page.screenshot(path=str(OUT / fn), full_page=full)
    INDEX.append((SECTION[0], fn, caption))
    print(f"[shot] {fn}", flush=True)


def step(title, fn):
    try:
        fn()
    except Exception as exc:  # noqa: BLE001
        print(f"[skip] {title}: {exc!r}"[:300], flush=True)


def section(s):
    SECTION[0] = s
    print(f"[section] {s}", flush=True)


def go(page, path, wait=1500):
    page.goto(URL + path, wait_until="networkidle"); page.wait_for_timeout(wait); page.evaluate("window.scrollTo(0,0)")


def btn_starting(page, label):
    return page.locator("button").filter(has_text=re.compile(r"^\s*" + re.escape(label)))


def enter_name(page, name="Nhân"):
    inp = page.get_by_placeholder("Ví dụ: Quỳnh, Thảo, Nhân")
    inp.fill(name)
    page.locator("button[type=submit]").first.click(); page.wait_for_timeout(1500)


def studio_items(page):
    """Studio sau tour: mở mục đầu tiên, các tab của Inspector, xem bằng chứng, áp dụng đề xuất, phím tắt."""
    def first():
        page.get_by_role("button", name=re.compile("Mở mục đầu tiên")).first.click(); page.wait_for_timeout(1800)
        shot(page, "studio_mo-muc-dau-tien", "Studio sau khi bấm \"Mở mục đầu tiên\": câu được chọn, Inspector tab Sửa nhanh với đề xuất")
    step("studio first", first)
    for label, key in [("Bằng chứng", "bang-chung"), ("Thuộc tính", "thuoc-tinh"), ("Pháp lý", "phap-ly")]:
        def tab(label=label, key=key):
            btn_starting(page, label).last.click(); page.wait_for_timeout(1200)
            shot(page, f"studio_inspector-{key}", f"Studio, Inspector tab {label}")
            if key == "bang-chung":
                page.locator("[title^='Xem trang gốc của bằng chứng']").first.click(); page.wait_for_timeout(3500)
                shot(page, "studio_xem-bang-chung", "Studio: xem trang gốc của bằng chứng (chỉ đọc), đoạn trích được tô")
                page.keyboard.press("Escape"); page.wait_for_timeout(800)
        step(f"studio tab {key}", tab)
    def apply():
        btn_starting(page, "Sửa nhanh").last.click(); page.wait_for_timeout(900)
        page.locator("[title^='Áp dụng đề xuất vào văn bản']").first.click(); page.wait_for_timeout(1800)
        shot(page, "studio_da-ap-dung-de-xuat", "Studio sau khi áp dụng một đề xuất: văn bản đổi, nhật ký thay đổi ghi lại")
    step("studio apply", apply)
    def showall():
        page.locator("[title='Hiện cả các mục đã xử lý']").first.click(); page.wait_for_timeout(900)
        shot(page, "studio_hien-ca-muc-da-xu-ly", "Studio: bật hiện cả các mục đã xử lý trong danh sách vấn đề")
    step("studio showall", showall)
    def keys():
        page.locator("[title='Phím tắt']").first.click(); page.wait_for_timeout(900)
        shot(page, "studio_phim-tat", "Studio: bảng phím tắt")
        page.mouse.click(8, 400); page.wait_for_timeout(600)  # bấm nền để đóng
    step("studio keys", keys)


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2, locale="vi-VN")
    page = ctx.new_page()
    S = {}

    # ---------------------------------------------------------------- 1. Khởi đầu
    section("1. Màn hình bắt đầu và hướng dẫn lần đầu")
    def s_start():
        go(page, "/", 1000)
        shot(page, "bat-dau_trong", "Màn hình bắt đầu: ô nhập tên người soát, chưa nhập gì")
        page.get_by_placeholder("Ví dụ: Quỳnh, Thảo, Nhân").fill("Nhân")
        shot(page, "bat-dau_da-nhap-ten", "Màn hình bắt đầu sau khi nhập tên")
        page.locator("button[type=submit]").first.click(); page.wait_for_timeout(1800)
        shot(page, "huong-dan_lan-dau", "Lần đầu vào: tự chuyển sang trang Hướng dẫn (khung nhìn đầu)")
        shot(page, "huong-dan_toan-trang", "Trang Hướng dẫn, toàn trang", full=True)
    step("start", s_start)
    page.evaluate("try { localStorage.setItem('gs.guide.seen', '1') } catch (e) {}")

    # ---------------------------------------------------------------- 2. Phân tích mới
    section("2. Bước 1: Tải tài liệu và chạy phân tích")
    def s_new():
        go(page, "/#/new")
        shot(page, "phan-tich-moi_trong", "Trang Phân tích mới khi chưa có tệp")
        page.get_by_placeholder("Ví dụ: Hòa Phát", exact=True).fill("Tập đoàn Hòa Phát")
        page.get_by_placeholder("Ví dụ: Hòa Phát – báo cáo bền vững 2025 + báo cáo thường niên 2024").fill(
            "Ảnh chụp tổng hợp — Hòa Phát: báo cáo bền vững 2025 + thường niên 2024")
        page.locator("input[type=file]").set_input_files([SR, AR]); page.wait_for_timeout(2500)
        shot(page, "phan-tich-moi_da-tai-tep", "Đã thả 2 tệp; mặc định cả hai là \"Cần kiểm\"")
        rows = page.locator("ul li:has(button[aria-label^='Bỏ'])")
        rows.nth(1).get_by_role("button", name="Đối chiếu").click(); page.wait_for_timeout(800)
        shot(page, "phan-tich-moi_da-chon-vai-tro", "Đã chọn vai trò: báo cáo bền vững = Cần kiểm, báo cáo thường niên = Đối chiếu")
        shot(page, "phan-tich-moi_toan-trang", "Trang Phân tích mới đã điền đủ, toàn trang", full=True)
        page.get_by_role("button", name="Bắt đầu phân tích").click()
        t0 = time.time(); marks = [3, 20, 60]
        for _ in range(300):
            page.wait_for_timeout(1000)
            el = int(time.time() - t0)
            if marks and el >= marks[0]:
                marks.pop(0)
                if page.locator("text=Đang phân tích").count():
                    shot(page, f"dang-phan-tich_{el:03d}s", f"Đang phân tích, giây thứ {el}: thanh tiến độ và các bước", wait=0)
            if "#/runs/" in page.url and page.locator("text=Đang phân tích").count() == 0:
                break
        S["secs"] = round(time.time() - t0)
        S["run_url"] = page.url.split("?")[0]
        S["run_id"] = S["run_url"].rsplit("/", 1)[-1]
        print(f"[run] {S['run_id']} xong sau {S['secs']}s", flush=True)
    step("new", s_new)
    if "run_id" not in S:
        print("[fatal] không có phiên phân tích; dừng", flush=True); browser.close(); sys.exit(1)
    RUN = "/#/runs/" + S["run_id"]

    # ---------------------------------------------------------------- 3. Hàng đợi
    section("3. Bước 2: Hàng đợi soát")
    def s_queue():
        go(page, RUN, 2500)
        shot(page, "hang-doi_can-soat", "Hàng đợi soát, tab Cần soát (khung nhìn đầu)")
        shot(page, "hang-doi_toan-trang", "Hàng đợi soát, toàn trang: chỉ số, danh sách, phạm vi lượt soát, thủ tục", full=True)
        for label in ["Đã xem, chưa chốt", "Đã chốt", "Ngoài hàng đợi"]:
            btn_starting(page, label).first.click(); page.wait_for_timeout(900)
            shot(page, f"hang-doi_tab-{slug(label)}", f"Hàng đợi, tab {label}" + (" (chưa có mục nào: trạng thái trống)" if label != "Ngoài hàng đợi" else ""))
        btn_starting(page, "Cần soát").first.click(); page.wait_for_timeout(600)
    step("queue", s_queue)

    # ---------------------------------------------------------------- 4. Danh sách tuyên bố
    section("4. Danh sách mọi tuyên bố và các bộ lọc")
    def s_claims():
        go(page, RUN + "/claims", 2000)
        shot(page, "danh-sach_tat-ca", "Danh sách tuyên bố, bộ lọc Tất cả")
        filt = page.locator("button").filter(has_text=re.compile(r"\(\d+\)\s*$"))
        labels = [re.sub(r"\s*\(\d+\)\s*$", "", t).strip() for t in filt.all_inner_texts()]
        for lab in labels[1:]:
            b = page.locator("button").filter(has_text=re.compile(r"^\s*" + re.escape(lab) + r"\s*\(\d+\)\s*$")).first
            cnt = re.search(r"\((\d+)\)", b.inner_text()).group(1)
            b.click(); page.wait_for_timeout(800)
            shot(page, f"danh-sach_loc-{slug(lab)}", f"Danh sách tuyên bố, bộ lọc {lab} ({cnt} mục)")
        filt.first.click(); page.wait_for_timeout(600)
        page.get_by_placeholder(re.compile("Tìm")).first.fill("năng lượng"); page.wait_for_timeout(800)
        shot(page, "danh-sach_tim-kiem", "Danh sách tuyên bố, ô tìm kiếm với từ \"năng lượng\"")
    step("claims", s_claims)

    # ---------------------------------------------------------------- 5. Chi tiết một mục
    section("5. Bước 3: Soát chi tiết một mục")
    def s_detail():
        go(page, RUN, 2500)
        items = page.locator("li:has(button:text-is('Mở'))")
        items.nth(1).get_by_role("button", name="Mở").click(); page.wait_for_timeout(2200)
        S["item_url"] = page.url
        shot(page, "chi-tiet_dau-trang", "Chi tiết một mục mở từ hàng đợi: thẻ tuyên bố, kết luận AI, các tab")
        tabs = page.locator("nav button")
        for key, label in [("attributes", "Thuộc tính"), ("evidence", "Bằng chứng"), ("numeric", "Kiểm tra số"), ("legal", "Pháp lý"),
                           ("org", "Quy tắc nội bộ"), ("risk", "Rủi ro & việc cần làm")]:
            def one(key=key, label=label):
                tabs.filter(has_text=label).first.click(); page.wait_for_timeout(1200)
                shot(page, f"chi-tiet_tab-{key}", f"Chi tiết, tab {label}")
                if key == "evidence":
                    ob = page.get_by_role("button", name="Mở nguồn").first
                    ob.scroll_into_view_if_needed(); page.evaluate("window.scrollBy(0,-250)")
                    shot(page, "chi-tiet_bang-chung-danh-sach", "Tab Bằng chứng: các đoạn trích kèm nút Mở nguồn")
                    ob.click(); page.wait_for_timeout(4000)
                    shot(page, "chi-tiet_xem-nguon-goc", "Xem nguồn gốc: ảnh trang PDF, đoạn trích được tô sáng, mã sha256")
                    page.keyboard.press("Escape"); page.wait_for_timeout(800)
                    if page.get_by_role("button", name="Đóng").count():
                        page.get_by_role("button", name="Đóng").first.click(); page.wait_for_timeout(500)
            step(f"tab {key}", one)
        tabs.filter(has_text="Xét duyệt").first.click(); page.wait_for_timeout(1000)
        shot(page, "chi-tiet_xet-duyet_trong", "Tab Xét duyệt trước khi quyết định")
        page.get_by_placeholder("Lý do quyết định").fill(
            "Câu nêu 'rất cao' nhưng không có số, kỳ, năm gốc. Đề nghị doanh nghiệp nêu số liệu năm 2025 và năm gốc.")
        shot(page, "chi-tiet_xet-duyet_da-ghi-ly-do", "Tab Xét duyệt đã ghi lý do; các nút quyết định")
        page.get_by_role("button", name="Yêu cầu thêm bằng chứng").click(); page.wait_for_timeout(2200)
        shot(page, "chi-tiet_xet-duyet_da-luu", "Sau khi lưu quyết định: trạng thái \"Đã có người xem\" và lịch sử")
        shot(page, "chi-tiet_toan-trang", "Chi tiết một mục, toàn trang", full=True)
        go(page, RUN, 2000)
        btn_starting(page, "Đã xem, chưa chốt").first.click(); page.wait_for_timeout(900)
        shot(page, "hang-doi_sau-khi-soat", "Hàng đợi sau khi soát: mục vừa xử lý nằm ở tab Đã xem, chưa chốt")
    step("detail", s_detail)

    # ---------------------------------------------------------------- 6. Studio
    section("6. Studio: sửa báo cáo theo đề xuất")
    def s_studio():
        go(page, RUN + "/studio", 3500)
        for i in range(10):
            shot(page, f"studio_tour-{i + 1}", f"Studio lần đầu: hướng dẫn từng bước, bước {i + 1}")
            nxt = page.locator("button").filter(has_text=re.compile(r"^\s*Tiếp\s*$"))
            if nxt.count():
                nxt.first.click(); page.wait_for_timeout(600); continue
            page.locator("button").filter(has_text=re.compile(r"^\s*Bắt đầu\s*$")).first.click(); page.wait_for_timeout(1000)
            break
        shot(page, "studio_chinh", "Studio: tài liệu và vấn đề (trái), báo cáo tô màu theo mức độ (giữa), Inspector (phải)")
        studio_items(page)
    step("studio", s_studio)

    # ---------------------------------------------------------------- 7. Xuất
    section("7. Bước 4: Xuất giấy làm việc")
    def s_export():
        go(page, RUN + "/export", 2000)
        shot(page, "xuat_trang", "Trang Xuất kết quả")
        shot(page, "xuat_toan-trang", "Trang Xuất kết quả, toàn trang", full=True)
        wp = ctx.new_page(); wp.set_viewport_size({"width": 1280, "height": 900})
        wp.goto(f"{URL}/api/v1/runs/{S['run_id']}/workpaper", wait_until="networkidle"); wp.wait_for_timeout(1500)
        shot(wp, "giay-lam-viec_dau-trang", "Giấy làm việc tiếng Việt, phần đầu (bản in / lưu PDF)")
        shot(wp, "giay-lam-viec_toan-trang", "Giấy làm việc, toàn trang", full=True)
        wp.close()
    step("export", s_export)

    # ---------------------------------------------------------------- 8. Trang phụ
    section("8. Lịch sử, Thư viện pháp lý, Cài đặt, lỗi")
    def s_misc():
        go(page, "/#/runs", 1800)
        shot(page, "lich-su", "Lịch sử các phiên phân tích")
        shot(page, "lich-su_toan-trang", "Lịch sử các phiên, toàn trang", full=True)
        go(page, "/#/legal", 1800)
        shot(page, "thu-vien-phap-ly", "Thư viện pháp lý, khung nhìn đầu")
        shot(page, "thu-vien-phap-ly_toan-trang", "Thư viện pháp lý, toàn trang (gồm quy tắc nội bộ của tổ chức)", full=True)
        go(page, "/#/settings", 1800)
        shot(page, "cai-dat", "Cài đặt: tên người soát, chế độ mô hình, trạng thái cổng")
        shot(page, "cai-dat_toan-trang", "Cài đặt, toàn trang", full=True)
        go(page, "/#/guide", 1500)
        shot(page, "huong-dan_mo-lai", "Hướng dẫn mở lại từ thanh bên (khi đã có phiên)")
        go(page, "/#/runs/khong-ton-tai", 2500)
        shot(page, "loi_phien-khong-ton-tai", "Trạng thái lỗi: mở đường dẫn tới phiên không tồn tại")
    step("misc", s_misc)
    ctx.close()

    # ---------------------------------------------------------------- 9. Điện thoại
    section("9. Màn hình hẹp (điện thoại 390 px)")
    def s_mobile():
        m = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, locale="vi-VN", is_mobile=True, has_touch=True)
        m.add_init_script("try { localStorage.setItem('gs.guide.seen', '1'); localStorage.setItem('gs.studio.tour', '1') } catch (e) {}")
        mp = m.new_page()
        go(mp, "/", 1200)
        shot(mp, "dt_bat-dau", "Điện thoại: màn hình bắt đầu")
        enter_name(mp)
        go(mp, "/#/new", 1200)
        shot(mp, "dt_phan-tich-moi", "Điện thoại: trang Phân tích mới", full=True)
        go(mp, RUN, 2500)
        shot(mp, "dt_hang-doi", "Điện thoại: hàng đợi soát (khung nhìn đầu)")
        shot(mp, "dt_hang-doi_toan-trang", "Điện thoại: hàng đợi soát, toàn trang", full=True)
        if "item_url" in S:
            mp.goto(S["item_url"], wait_until="networkidle"); mp.wait_for_timeout(2000)
            shot(mp, "dt_chi-tiet", "Điện thoại: chi tiết một mục", full=True)
        go(mp, RUN + "/studio", 3000)
        shot(mp, "dt_studio", "Điện thoại: Studio")
        go(mp, "/#/legal", 1500)
        shot(mp, "dt_thu-vien-phap-ly", "Điện thoại: thư viện pháp lý (khung nhìn đầu)")
        m.close()
    step("mobile", s_mobile)
    browser.close()

# ---------------------------------------------------------------- mục lục
lines = [f"# Ảnh chụp giao diện GreenScan — {time.strftime('%d/%m/%Y')}", "",
         f"Phiên chụp: `{S.get('run_id')}` (Hòa Phát: báo cáo bền vững 2025 cần kiểm + thường niên 2024 đối chiếu, "
         f"chế độ ngoại tuyến). Phân tích mất khoảng {S.get('secs')} giây.",
         "Máy tính: khung nhìn 1440×900, tỉ lệ 2 (ảnh 2880 px ngang). Điện thoại: 390×844, tỉ lệ 3. "
         "Ảnh \"toàn trang\" là chụp cả trang cuộn.", "",
         "Tạo lại: `python tools/capture_all_screens.py` (app phải chạy ở localhost:8000).", ""]
cur = None
for sec, fn, cap in INDEX:
    if sec != cur:
        lines += ["", f"## {sec}", "", "| Tệp | Nội dung |", "| --- | --- |"]; cur = sec
    lines.append(f"| [{fn}]({fn}) | {cap} |")
(OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"DONE {len(INDEX)} ảnh -> {OUT}", flush=True)
