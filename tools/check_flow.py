"""Đi hết chuỗi “Việc tiếp theo” trong trình duyệt thật như một người mở lần đầu, và báo lỗi nếu chuỗi hỏng.

Chuỗi đúng (frontend/src/lib/flow.js): trang đầu → mở một phiên → bước 2 chốt từng mục → bước 3 Sửa báo cáo
→ bước 4 Giấy làm việc → gợi ý một phiên KHÁC. Công cụ dừng với mã 1 khi gặp một trong các trường hợp:
  - trang ném lỗi JavaScript, hoặc một yêu cầu trả mã ≥ 400;
  - ngõ cụt: trang không còn nút đi tiếp trước khi hết chuỗi;
  - vòng lặp: cùng một trang với cùng một nút xuất hiện lần thứ ba;
  - hết chuỗi mà phiên được gợi ý lại chính là phiên vừa làm xong;
  - thanh “Việc tiếp theo” cao bất thường (chữ bị bóp thành từng từ một dòng trên màn hình hẹp).

    C:/Python314/python.exe tools/check_flow.py http://127.0.0.1:8000 --shots <thư mục ảnh>
    C:/Python314/python.exe tools/check_flow.py https://<bản trực tuyến> --width 390 --height 844

Cần: playwright (pip) và Microsoft Edge. Trên bản cài đặt, hãy chạy trên một BẢN SAO kho phiên: công cụ ghi quyết định thật.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--width", type=int, default=1366)
    ap.add_argument("--height", type=int, default=768)
    ap.add_argument("--shots", default="", help="thư mục lưu ảnh từng bước (tuỳ chọn)")
    ap.add_argument("--name", default="Giám khảo")
    args = ap.parse_args()
    from playwright.sync_api import sync_playwright

    base = args.url.rstrip("/") + "/"
    shots = Path(args.shots) if args.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    problems: list[str] = []
    errors: list[str] = []
    studio_next = "studio-next" if args.width >= 768 else "studio-next-small"   # màn hình hẹp: trang báo cần màn hình rộng

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=EDGE)
        ctx = browser.new_context(viewport={"width": args.width, "height": args.height},
                                  is_mobile=args.width < 600, has_touch=args.width < 600)
        page = ctx.new_page()
        ctx.on("page", lambda popup: popup.close() if popup is not page else None)   # giấy làm việc mở trang mới

        def route() -> str:
            return page.url.split("#", 1)[1] if "#" in page.url else "(gốc)"

        def pause(seconds: float) -> None:
            # Not time.sleep: the browser's events (a route change after a click) are only taken in
            # while a Playwright call is running, so a plain sleep would leave page.url stale.
            page.wait_for_timeout(int(seconds * 1000))

        page.on("pageerror", lambda e: errors.append(f"lỗi trang @{route()}: {str(e)[:200]}"))
        page.on("console", lambda m: errors.append(f"console @{route()}: {m.text[:200]}") if m.type == "error" else None)
        ctx.on("response", lambda r: errors.append(f"HTTP {r.status} {r.url[-90:]}") if r.status >= 400 else None)

        def look(n: int) -> str:
            pause(1.5)
            if shots:
                page.screenshot(path=str(shots / f"{n:02d}.png"))
            bar = page.get_by_test_id("next-step")
            kicker = text = label = "-"
            if bar.count():
                ps = bar.first.locator("p")
                kicker = ps.nth(0).inner_text() if ps.count() else "-"
                text = ps.nth(1).inner_text() if ps.count() > 1 else "-"
                act = bar.first.get_by_test_id("next-step-action")
                label = act.inner_text() if act.count() else "(không có nút)"
                box = bar.first.bounding_box()
                if box and box["height"] > 0.6 * args.height:
                    problems.append(f"bước {n}: thanh “Việc tiếp theo” cao {box['height']:.0f}px trên màn hình {args.height}px ở {route()}")
            elif page.get_by_test_id(studio_next).count():
                kicker, label = "(trang Sửa báo cáo)", page.get_by_test_id(studio_next).inner_text()
            if page.evaluate("Math.max(document.documentElement.scrollWidth, window.innerWidth)") > args.width + 4:   # điện thoại nới trang theo nội dung rộng
                problems.append(f"bước {n}: trang {route()} tràn ngang màn hình {args.width}px")
            print(f"{n:02d} | {route()[:44]:44} | {kicker[:34]:34} | NÚT: {label[:30]:30} | {text[:90]}")
            return label

        page.goto(base, wait_until="networkidle", timeout=90000)
        look(0)
        start = page.get_by_role("button", name="Bắt đầu phiên làm việc")
        if not start.count():
            problems.append("trang đầu không có nút “Bắt đầu phiên làm việc”")
        else:
            box = page.get_by_placeholder("Ví dụ: Quỳnh, Thảo, Nhân")
            if not box.input_value().strip():
                start.click()                                   # bấm khi chưa nhập tên: phải có lời nhắc
                pause(0.4)
                if not page.get_by_test_id("start-nudge").count():
                    problems.append("trang đầu: bấm khi chưa nhập tên mà không có phản hồi nào")
                box.fill(args.name)
            start.click()

        seen: dict[tuple[str, str], int] = {}
        finished_run = None
        done = False
        for n in range(1, 60):
            label = look(n)
            here = route()
            key = (here, label)
            seen[key] = seen.get(key, 0) + 1
            if seen[key] > 2:
                problems.append(f"vòng lặp: “{label}” ở {here} xuất hiện lần thứ ba")
                break
            if here == "/runs" and finished_run:                # hết chuỗi: quay về lịch sử sau khi xong một phiên
                target = page.get_by_test_id("next-step-action")
                href = target.get_attribute("href") if target.count() else ""
                if finished_run in (href or ""):
                    problems.append(f"hết chuỗi nhưng gợi ý lại chính phiên vừa xong ({finished_run})")
                done = True
                break
            if "/studio" in here:
                skip = page.get_by_role("button", name="Bỏ qua")
                if skip.count() and args.width >= 768:
                    skip.first.click()
                    pause(0.4)
                nxt = page.get_by_test_id(studio_next)
                if not nxt.count():
                    problems.append("ngõ cụt: trang Sửa báo cáo không có nút sang bước 4")
                    break
                nxt.click()
                continue
            act = page.get_by_test_id("next-step-action")
            if here == "/new" and not act.count():              # bản cài đặt, bước 1: chọn bộ mẫu rồi mới có nút phân tích
                sample = page.locator("[data-sample]").first
                if sample.count():
                    sample.click()
                    pause(3.0)
                    continue
            if not act.count():
                problems.append(f"ngõ cụt: {here} không còn nút đi tiếp")
                break
            if here == "/new":                                  # bấm phân tích rồi chờ hàng đợi tự mở (bộ mẫu nhỏ: vài giây)
                act.first.click()
                for _ in range(240):
                    if route().startswith("/runs/"):
                        break
                    pause(1.0)
                else:
                    problems.append("bước 1: bấm “Bắt đầu phân tích” nhưng hàng đợi không mở sau 4 phút")
                    break
                continue
            if "/export" in here:
                finished_run = here.split("/")[2]
            before = here
            act.first.click()
            pause(1.0)
            if route() == before and "/claims/" in before:      # nút chỉ cuộn tới phần quyết định: chốt như người dùng
                ok = page.get_by_role("button", name="Xác nhận gợi ý của máy")
                if ok.count() and ok.first.is_enabled():
                    ok.first.click()
                    pause(0.8)
                else:
                    problems.append(f"{before}: không bấm được “Xác nhận gợi ý của máy”")
                    break
        if not done and not problems:
            problems.append("chưa đi hết chuỗi sau 60 bước")
        browser.close()

    for e in dict.fromkeys(errors):
        problems.append(e)
    print("-" * 60)
    if problems:
        print(f"HỎNG: {len(problems)} vấn đề")
        for x in problems:
            print("  -", x)
        return 1
    print("ĐẠT: đi hết chuỗi, không lỗi trang, không vòng lặp, không ngõ cụt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
