"""Chẩn đoán trang listing không cho ra tài liệu nào.

Một trang JS-rendered trả về HTML hợp lệ, HTTP 200, và KHÔNG có tài liệu nào.
Không phát hiện thì crawler báo "chạy xong, 0 tài liệu" -- đúng loại thất bại im
lặng như bug robots.txt cũ. Module này biến nó thành cảnh báo kèm lý do, để biết
nguồn cần adapter API hoặc Playwright chứ không phải selector sai.

Đây CHỈ là chẩn đoán, crawler không tự bật browser automation.

LƯU Ý VỀ TÍN HIỆU
-----------------
Hình dạng HTML một mình thì không đủ. Trang Vinamilk có 202k ký tự script và
KHÔNG có thẻ <tr> nào (layout thẻ), nhưng vẫn là HTML tĩnh với 13 PDF thật.
Ngược lại Vietstock có sẵn vài PDF marketing của chính họ nên "đếm link .pdf"
cũng đánh lừa. Tín hiệu đáng tin duy nhất là kết quả thực tế của adapter: số
ứng viên phân loại được thành một report_type đã biết.
"""

from __future__ import annotations

from bs4 import BeautifulSoup

# Mount node của SPA phổ biến -- rỗng nghĩa là nội dung do JS đổ vào.
_MOUNT_SELECTOR = "#root, #app, #__next, #__nuxt, [data-reactroot], [ng-app], [v-app]"

_MIN_SCRIPT_CHARS = 10_000


def diagnose_empty_listing(html: str, *, candidates: int, typed_candidates: int) -> str | None:
    """Trả về lý do nghi ngờ trang cần render JS, hoặc None nếu không nghi ngờ.

    Chỉ gọi khi adapter không phân loại được ứng viên nào (`typed_candidates == 0`).
    """
    if typed_candidates > 0:
        return None

    soup = BeautifulSoup(html, "lxml")
    script_chars = sum(len(s.get_text() or "") for s in soup.select("script"))
    body = soup.body
    text_chars = len(body.get_text(strip=True)) if body else 0

    reasons: list[str] = []

    mount = soup.select_one(_MOUNT_SELECTOR)
    if mount is not None and not mount.get_text(strip=True):
        reasons.append(f"mount node '{mount.get('id') or mount.name}' rỗng")

    if script_chars > _MIN_SCRIPT_CHARS and script_chars > 2 * text_chars:
        reasons.append(f"tỷ lệ script/text = {script_chars}/{text_chars}")
    elif script_chars > _MIN_SCRIPT_CHARS:
        reasons.append(f"{script_chars} ký tự script")

    if not reasons:
        return None

    detail = "; ".join(reasons)
    if candidates:
        detail += f"; {candidates} link giống file nhưng không phân loại được"
    return detail
