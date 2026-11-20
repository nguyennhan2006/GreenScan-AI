"""Đẩy prototype lên Hugging Face Space (Docker) để Ban Giám khảo chạy thử qua một đường dẫn.

Cách dùng (thư mục gốc repo, cần token Hugging Face có quyền GHI: `hf auth login`):

    python tools/deploy_hf_space.py --space <user>/greenscan-ai --demo-users "giamkhao:<mật khẩu>"
    python tools/deploy_hf_space.py --space <user>/greenscan-ai --dry-run     # chỉ dựng thư mục, không đẩy

Tệp đưa lên lấy đúng bộ lọc của gói nộp (tools/package_submission.py): không bí mật, không kho crawl 4 GB,
không tệp quá 3 MB trừ PDF phiên mẫu và giao diện đã build. Đầu README được thêm khối khai báo Space
(sdk docker, cổng 8000). Mật khẩu demo đi vào *secret* của Space (`QUANTUM_DEMO_USERS`), không nằm trong mã.

Space miễn phí ngủ khi không ai truy cập và mất dữ liệu khi khởi động lại; phiên mẫu Hòa Phát được cài lại
tự động (deploy/seed). Đánh thức Space trước 20/11 và trước buổi thi 28–29/11 (gọi /health).
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from package_submission import candidate_files, scan_secrets, select  # noqa: E402

FRONT_MATTER = """---
title: GreenScan AI
emoji: 🌿
colorFrom: green
colorTo: gray
sdk: docker
app_port: 8000
pinned: true
short_description: Sàng lọc rủi ro tẩy xanh, đội AQ2026-119
---

"""


def build_folder(out: Path) -> tuple[int, int]:
    files, skipped = select(candidate_files())
    leaks = scan_secrets(files)
    if leaks:
        raise SystemExit("Dừng: nghi có bí mật trong " + ", ".join(leaks[:10]))
    total = 0
    for rel in files:
        src = ROOT / rel
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        total += src.stat().st_size
    readme = out / "README.md"
    readme.write_text(FRONT_MATTER + readme.read_text(encoding="utf-8"), encoding="utf-8")
    return len(files), total


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--space", required=True, help="<user hoặc org>/<tên space>")
    ap.add_argument("--demo-users", default="", help='"giamkhao:matkhau" (để trống = không đặt mật khẩu)')
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="hf-space-") as tmp:
        out = Path(tmp)
        n, size = build_folder(out)
        print(f"Thư mục Space: {n} tệp, {size / 1e6:.1f} MB")
        if args.dry_run:
            return
        from huggingface_hub import HfApi

        api = HfApi()
        role = (api.whoami().get("auth", {}).get("accessToken", {}) or {}).get("role")
        if role == "read":
            raise SystemExit("Token Hugging Face hiện tại chỉ có quyền ĐỌC. Tạo token quyền Write ở "
                             "https://huggingface.co/settings/tokens rồi chạy `hf auth login`.")
        api.create_repo(args.space, repo_type="space", space_sdk="docker", private=False, exist_ok=True)
        if args.demo_users:
            api.add_space_secret(args.space, "QUANTUM_DEMO_USERS", args.demo_users)
        api.upload_folder(folder_path=str(out), repo_id=args.space, repo_type="space",
                          commit_message="GreenScan AI: bản nộp Vòng 2")
        owner, name = args.space.split("/", 1)
        print(f"Đã đẩy. Trang Space: https://huggingface.co/spaces/{args.space}")
        print(f"Đường dẫn ứng dụng: https://{owner.lower()}-{name.lower().replace('_', '-')}.hf.space/")
        print("Lần dựng đầu mất khoảng 10–15 phút; log khởi động phải có dòng [phiên mẫu] đã cài 1 phiên.")


if __name__ == "__main__":
    main()
