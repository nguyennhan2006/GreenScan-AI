"""Đóng gói GreenScan thành bản chạy ngay cho Windows 64-bit.

Khách hàng chỉ cần tải một tệp .zip, giải nén, nhấp đúp GreenScan.bat: không phải cài Python,
Node.js hay Git. Gói mang theo một bản Python nhúng (python.org "embeddable package"), các thư
viện đã cài sẵn, giao diện web đã dựng và phiên phân tích mẫu Hòa Phát.

Bố cục trong gói giữ nguyên như repo (src/, configs/, data/, deploy/seed, frontend/dist), vì mã
nguồn tìm cấu hình và dữ liệu theo vị trí tương đối với thư mục gốc (Path(__file__).parents[3]).
Gói được nối với src/ qua tệp pythonXY._pth của bản Python nhúng, không cài quantum_gw vào
site-packages.

Máy đóng gói cần: Windows 64-bit, Python cùng phiên bản phụ với bản nhúng (mặc định 3.14),
Node.js 20+ nếu frontend/dist chưa có, và mạng để tải bản nhúng cùng thư viện.

Chạy:   py -3.14 tools/build_windows_portable.py
        py -3.14 tools/build_windows_portable.py --python 3.14.10 --out build/portable
Ra:     build/portable/GreenScan-Windows-x64.zip (thư mục build/ đã nằm trong .gitignore)

Không có trong gói: OCR (Tesseract) cho trang scan, mô hình cục bộ (torch), kho crawl
data/crawl (chỉ dùng khi huấn luyện), tệp .env của máy đóng gói.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tomllib
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PYTHON = "3.14.10"

# Chép vào gói: chỉ tệp git đang theo dõi (đúng bản trên GitHub, không lọt dữ liệu riêng của
# máy đóng gói), cộng giao diện đã dựng frontend/dist (bị .gitignore nên chép nguyên thư mục).
GIT_PATHS = ["src/quantum_gw", "configs", "data", "deploy/seed", ".env.example", "LICENSE"]
SKIP_PREFIXES = ("data/crawl/",)  # kho crawl cho huấn luyện, không dùng khi chạy

LAUNCHER = r"""@echo off
rem GreenScan - ban chay ngay cho Windows. Nhap dup de mo; dong cua so nay de tat.
rem Khong can cai Python hay Node.js. Trinh duyet tu mo http://localhost:8000
setlocal
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
if not exist "python\python.exe" goto broken
if not exist ".env" if exist ".env.example" copy ".env.example" ".env" >nul
echo Dang khoi dong GreenScan tai http://localhost:8000 ...
echo Lan dau mo mat khoang 1 phut, nhung lan sau khoang 30 giay.
echo Giu cua so nay mo trong khi dung GreenScan. Dong cua so nay la tat GreenScan.
"python\python.exe" -m quantum_gw.cli app
if errorlevel 1 (
  echo.
  echo GreenScan da dung. Neu co loi o tren, chup man hinh cua so nay gui nguoi ho tro.
  pause
)
goto end
:broken
echo Thieu thu muc python\ - hay giai nen TOAN BO tep .zip roi nhap dup lai GreenScan.bat.
pause
:end
endlocal
"""

README = """GREENSCAN - BẢN CHẠY NGAY CHO WINDOWS
=====================================

1. Giải nén toàn bộ tệp .zip vào một thư mục bạn có quyền ghi, ví dụ Documents hoặc Desktop
   (không giải nén vào C:\\Program Files).
2. Mở thư mục GreenScan, nhấp đúp GreenScan.bat.
   Nếu Windows hiện "Windows protected your PC" (Windows đã bảo vệ máy tính của bạn):
   bấm "More info" (Thông tin thêm) rồi "Run anyway" (Vẫn chạy).
3. Trình duyệt tự mở http://localhost:8000 (lần đầu mất khoảng 1 phút, những lần sau khoảng
   30 giây). Nếu không, tự mở trình duyệt và gõ địa chỉ đó.
4. Giữ cửa sổ đen mở trong khi dùng. Đóng cửa sổ đó là tắt GreenScan.

Không cần mạng, không cần khoá API: tài liệu không rời khỏi máy (chế độ offline).
Dữ liệu phiên làm việc lưu trong thư mục .quantum bên cạnh GreenScan.bat.
Trang scan (ảnh chụp) cần thêm Tesseract OCR; xem tệp .env.example, mục OCR.
"""


def log(msg: str) -> None:
    print(f"[đóng gói] {msg}", flush=True)


def fetch(url: str, dest: Path) -> Path:
    if dest.exists() and dest.stat().st_size > 0:
        log(f"dùng bản đã tải: {dest.name}")
        return dest
    log(f"tải {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f)
    tmp.replace(dest)
    return dest


def dependencies() -> list[str]:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    return list(project["dependencies"])


def build_ui() -> None:
    if (ROOT / "frontend/dist/index.html").is_file():
        return
    npm = shutil.which("npm")
    if not npm:
        sys.exit("Chưa có frontend/dist và không tìm thấy npm: cài Node.js 20+ rồi chạy lại.")
    log("dựng giao diện web (npm ci, npm run build)")
    subprocess.run([npm, "ci"], cwd=ROOT / "frontend", check=True)
    subprocess.run([npm, "run", "build"], cwd=ROOT / "frontend", check=True)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # cửa sổ cmd tiếng Việt mặc định cp1258
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--python", default=DEFAULT_PYTHON, help="phiên bản Python nhúng, ví dụ 3.14.10")
    ap.add_argument("--out", default=str(ROOT / "build" / "portable"))
    ap.add_argument("--name", default="GreenScan-Windows-x64")
    args = ap.parse_args()

    if sys.platform != "win32":
        sys.exit("Chạy công cụ này trên Windows: thư viện cài vào gói là bản dựng cho Windows.")
    major, minor = (int(x) for x in args.python.split(".")[:2])
    if sys.version_info[:2] != (major, minor):
        sys.exit(f"Python đang chạy là {sys.version.split()[0]}; cần {major}.{minor} để thư viện khớp "
                 f"bản nhúng. Chạy: py -{major}.{minor} tools/build_windows_portable.py")

    out = Path(args.out)
    stage = out / "GreenScan"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    # 1. Python nhúng
    tag = f"{major}{minor}"
    embed = fetch(f"https://www.python.org/ftp/python/{args.python}/python-{args.python}-embed-amd64.zip",
                  out / "cache" / f"python-{args.python}-embed-amd64.zip")
    pydir = stage / "python"
    with zipfile.ZipFile(embed) as z:
        z.extractall(pydir)
    # ._pth: thêm site-packages và ..\src, bật import site
    (pydir / f"python{tag}._pth").write_text(
        f"python{tag}.zip\n.\nLib\\site-packages\n..\\src\nimport site\n", encoding="utf-8")

    # 2. Thư viện
    site = pydir / "Lib" / "site-packages"
    deps = dependencies()
    log(f"cài {len(deps)} thư viện vào gói")
    subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--no-compile",
                    "--target", str(site), *deps], check=True)
    shutil.rmtree(site / "bin", ignore_errors=True)  # lệnh chạy trỏ về Python của máy đóng gói

    # 3. Mã nguồn, cấu hình, dữ liệu, phiên mẫu (tệp git theo dõi), giao diện đã dựng
    build_ui()
    listed = subprocess.run(["git", "ls-files", "-z", "--", *GIT_PATHS], cwd=ROOT,
                            capture_output=True, check=True).stdout.decode("utf-8").split("\0")
    tracked = [r for r in listed if r and not r.startswith(SKIP_PREFIXES)]
    log(f"chép {len(tracked)} tệp mã nguồn và dữ liệu")
    for rel in tracked:
        dest = stage / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    shutil.copytree(ROOT / "frontend/dist", stage / "frontend/dist")
    (stage / "GreenScan.bat").write_text(LAUNCHER.replace("\n", "\r\n"), encoding="ascii")
    (stage / "HUONG_DAN.txt").write_text(README.replace("\n", "\r\n"), encoding="utf-8-sig")

    # 4. Kiểm nhanh: Python nhúng nạp được ứng dụng
    check = subprocess.run([str(pydir / "python.exe"), "-c",
                            "import quantum_gw.api, sklearn, fitz, pdfplumber; print('ok')"],
                           cwd=stage, capture_output=True, text=True)
    if check.returncode != 0 or "ok" not in check.stdout:
        sys.exit(f"Gói không nạp được ứng dụng:\n{check.stderr[-2000:]}")
    log("kiểm nạp ứng dụng: ok")

    # 5. Nén
    archive = out / f"{args.name}.zip"
    if archive.exists():
        archive.unlink()
    files = [p for p in stage.rglob("*") if p.is_file()]
    log(f"nén {len(files)} tệp")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in files:
            z.write(p, p.relative_to(out).as_posix())
    size = sum(p.stat().st_size for p in files) / 1e6
    log(f"xong: {archive} ({archive.stat().st_size / 1e6:.0f} MB nén, {size:.0f} MB giải nén)")


if __name__ == "__main__":
    main()
