"""Tải lại HTML thật vào tests/fixtures/ để hiệu chỉnh selector và chạy test chẩn đoán.

Chạy khi có mạng sạch:
    python scripts/refresh_fixtures.py

Fixture là ảnh chụp trang công khai, chỉ dùng để kiểm thử parser. Script chỉ GET,
không tải tài liệu, và tôn trọng robots.txt của từng site.
"""

from __future__ import annotations

import argparse
import sys
import urllib.robotparser
from pathlib import Path

import httpx

UA = "VNReportResearchBot/0.2 (+contact: research@example.org)"

PAGES = {
    # Đối chứng dương: listing render bằng JS
    "vietstock_bctc.html": "https://finance.vietstock.vn/tai-lieu/bao-cao-tai-chinh.htm",
    "vietstock_btn.html": "https://finance.vietstock.vn/tai-lieu/bao-cao-thuong-nien.htm",
    "cafef_cbtt.html": "https://cafef.vn/du-lieu/cong-bo-thong-tin.chn",
    # Đối chứng âm: HTML tĩnh có tài liệu thật
    "hoaphat_ptbv.html": "https://www.hoaphat.com.vn/quan-he-co-dong/bao-cao-phat-trien-ben-vung",
    "vinamilk_sustainability.html": "https://www.vinamilk.com.vn/investor/reports/sustainability",
}

OUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures"


def allowed(client: httpx.Client, url: str) -> bool:
    origin = "/".join(url.split("/")[:3])
    try:
        response = client.get(f"{origin}/robots.txt")
        if response.status_code in (404, 410):
            return True
        parser = urllib.robotparser.RobotFileParser()
        parser.parse(response.text.splitlines())
        return parser.can_fetch(UA, url)
    except Exception as exc:  # noqa: BLE001
        print(f"  ! không đọc được robots.txt của {origin}: {exc}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Tắt xác thực TLS. CHỈ dùng sau proxy MITM của môi trường phát triển.",
    )
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    client = httpx.Client(
        verify=not args.insecure,
        timeout=30,
        follow_redirects=True,
        headers={"User-Agent": UA},
    )

    failures = 0
    for name, url in PAGES.items():
        if not allowed(client, url):
            print(f"  SKIP {name}: robots.txt không cho phép")
            failures += 1
            continue
        try:
            response = client.get(url)
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            print(f"  FAIL {name}: {type(exc).__name__}: {exc}")
            failures += 1
            continue
        (OUT / name).write_text(response.text, encoding="utf-8")
        print(f"  OK   {name}  {len(response.content)} bytes")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
