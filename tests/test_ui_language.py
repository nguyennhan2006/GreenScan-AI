"""Chữ người dùng nhìn thấy không được lẫn tiếng Anh / mã nội bộ mới (chuẩn: docs/05-ui/CHUAN_NGON_NGU_GIAO_DIEN.md)."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_ui_language  # noqa: E402


def test_no_new_english_in_user_facing_text():
    allow = {
        line.strip() for line in (ROOT / "tools/ui_language_allow.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    new = sorted({f"{rel}\t{tok}" for rel, _line, tok, _kind, _s in check_ui_language.scan()} - allow)
    assert not new, "Từ tiếng Anh / mã nội bộ mới trong giao diện (xem chuẩn ngôn ngữ):\n" + "\n".join(new)
