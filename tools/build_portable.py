"""Đóng gói GreenScan thành một thư mục "giải nén là chạy" cho Windows 64-bit (portable-v1, 17/11/2026).

Người nhận không cần cài Python, thư viện hay bộ đọc ảnh quét: tất cả nằm trong gói.
Riêng mô hình ngôn ngữ chạy trên máy (Ollama + Qwen3-4B, tải khoảng 2,5 GB) không nằm trong gói;
tệp CAI_MO_HINH_TREN_MAY.bat tự cài khi người dùng bấm. Gói không chứa khoá API nào.

    .venv/Scripts/python.exe -I tools/build_portable.py \
        --source "<checkpoint>/GreenScan-AI" --store "<kho demo>" --out "<thư mục ra>" --zip

Bố cục gói:
    GreenScan/
      CHAY_GREENSCAN.bat            bấm đúp để chạy; trình duyệt tự mở
      CAI_MO_HINH_TREN_MAY.bat      tuỳ chọn: tự cài Ollama và tải mô hình
      DOC_TRUOC.txt                 hướng dẫn một trang
      python/                       Python nhúng + thư viện (đúng phiên bản máy dựng gói)
      app/                          mã nguồn, cấu hình, dữ liệu mẫu, giao diện đã dựng, bộ nhớ đệm mô hình
      ocr/                          Tesseract (chỉ tệp cần để đọc ảnh quét) + dữ liệu tiếng Việt, tiếng Anh
      du_lieu/                      kho phiên: các phiên mẫu đã chạy sẵn; phiên mới cũng lưu ở đây
"""
from __future__ import annotations

import argparse
import hashlib
import os
import platform
import re
import shutil
import subprocess
import sys
import tomllib
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PARTS = ["src", "configs", "data", "models/stance", "frontend/dist", "pyproject.toml", "README.md", ".env.example"]  # models/stance: sổ mô hình thách đấu (Hướng dẫn bước 8)
STORE_PARTS = ["runs", "documents", "reviews", "org_packs"]
SKIP_DIRS = {"__pycache__", ".pytest_cache", "node_modules"}
PRUNE_TESTS_IN = ("numpy", "scipy", "sklearn")       # thư mục tests/ của ba gói này không dùng khi chạy
# Thiết lập không bí mật lấy từ .env của máy dựng gói; mọi khoá API để trống.
ENV_KEYS = ["QUANTUM_CONFIG", "QUANTUM_PROFILE", "QUANTUM_OCR_ENABLED", "QUANTUM_OCR_LANGUAGES",
            "QUANTUM_LLM_CACHE_DIR", "QUANTUM_LLM_WORKERS", "EMBEDDING_PROVIDER", "EMBEDDING_CACHE_DIR",
            "RERANKER_PROVIDER", "RERANK_CANDIDATE_K", "RERANK_FINAL_K", "LLM_PROVIDER", "LLM_FALLBACK_ORDER",
            "LOCAL_LLM_PROVIDER", "LOCAL_LLM_MODEL", "LOCAL_LLM_TIMEOUT_SECONDS", "LOCAL_LLM_MAX_TOKENS", "GROQ_MODEL"]
SECRET_NAME = re.compile(r"API_?KEY|_KEY$|_TOKEN$|SECRET|PASSWORD")      # tên biến trông như bí mật (MAX_TOKENS thì không)
OLLAMA_MODEL = "qwen3:4b-instruct-2507-q4_K_M"

LAUNCHER = r"""@echo off
rem GreenScan - ban chay ngay. Bam dup tep nay; trinh duyet tu mo sau vai giay.
rem Dong cua so nay de dung chuong trinh. Du lieu phien nam trong thu muc du_lieu.
setlocal
title GreenScan
set "ROOT=%~dp0"
set "QUANTUM_RUNS_DIR=%ROOT%du_lieu\runs"
set "QUANTUM_DOCUMENTS_DIR=%ROOT%du_lieu\documents"
set "QUANTUM_REVIEWS_FILE=%ROOT%du_lieu\reviews\decisions.jsonl"
set "QUANTUM_ORG_PACK_STORE=%ROOT%du_lieu\org_packs"
set "QUANTUM_SEED_DIR="

rem Doc anh quet (OCR). Tesseract khong mo duoc thu muc co dau tieng Viet, nen neu no khong thay
rem du lieu tieng Viet trong goi thi chep du lieu (14 MB) sang %LOCALAPPDATA%\GreenScan\tessdata, mot lan.
if not exist "%ROOT%ocr\tesseract.exe" goto ocr_done
set "QUANTUM_TESSERACT_COMMAND=%ROOT%ocr\tesseract.exe"
set "TESSDATA_PREFIX=%ROOT%ocr\tessdata"
"%ROOT%ocr\tesseract.exe" --list-langs 2>nul | find "vie" >nul
if not errorlevel 1 goto ocr_done
set "TESSDATA_PREFIX=%LOCALAPPDATA%\GreenScan\tessdata"
if not exist "%TESSDATA_PREFIX%\vie.traineddata" xcopy /e /i /q /y "%ROOT%ocr\tessdata" "%TESSDATA_PREFIX%" >nul
:ocr_done

rem Mo hinh chay tren may (neu da cai): bat Ollama neu chua chay.
set "OLLAMA_EXE="
where ollama >nul 2>nul && set "OLLAMA_EXE=ollama"
if not defined OLLAMA_EXE if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
if not defined OLLAMA_EXE goto no_model
tasklist /fi "imagename eq ollama.exe" 2>nul | find /i "ollama.exe" >nul
if errorlevel 1 start "Ollama" /min "%OLLAMA_EXE%" serve
goto port
:no_model
echo [GreenScan] Chua co mo hinh chay tren may. Che do "chi luat va phep tinh" van chay day du.
echo             Muon bat mo hinh: dong cua so nay, bam dup CAI_MO_HINH_TREN_MAY.bat.
echo.

:port
set "PORT=8000"
netstat -ano | findstr /r /c:":8000 .*LISTENING" >nul 2>nul && set "PORT=8010"
set "BROWSER=--browser"
if defined GREENSCAN_NO_BROWSER set "BROWSER=--no-browser"
if defined GREENSCAN_PORT set "PORT=%GREENSCAN_PORT%"
cd /d "%ROOT%app"
echo [GreenScan] Dang khoi dong tai http://localhost:%PORT% ...
"%ROOT%python\python.exe" -X utf8 -m quantum_gw.cli app --port %PORT% %BROWSER%
echo.
echo [GreenScan] Chuong trinh da dung.
pause
"""

MODEL_SETUP = r"""@echo off
rem GreenScan - cai mo hinh ngon ngu chay tren may nay (tuy chon).
rem Tu cai Ollama (neu chua co) roi tai mo hinh __MODEL__ (khoang 2,5 GB). Can mang Internet.
rem May khong co card do hoa van chay duoc, nhung cham (vai chuc giay moi luot goi).
setlocal
title GreenScan - cai mo hinh
set "OLLAMA_DIR=%LOCALAPPDATA%\Programs\Ollama"
where ollama >nul 2>nul && goto have_ollama
if exist "%OLLAMA_DIR%\ollama.exe" goto add_path

echo [1/3] Cai Ollama bang winget...
winget install -e --id Ollama.Ollama --silent --accept-package-agreements --accept-source-agreements
if exist "%OLLAMA_DIR%\ollama.exe" goto add_path
echo       winget khong cai duoc. Tai bo cai tu ollama.com...
curl -L -o "%TEMP%\OllamaSetup.exe" https://ollama.com/download/OllamaSetup.exe
if errorlevel 1 goto failed
"%TEMP%\OllamaSetup.exe" /VERYSILENT /NORESTART
if not exist "%OLLAMA_DIR%\ollama.exe" goto failed

:add_path
set "PATH=%OLLAMA_DIR%;%PATH%"

:have_ollama
echo [2/3] Bat Ollama...
tasklist /fi "imagename eq ollama.exe" 2>nul | find /i "ollama.exe" >nul
if errorlevel 1 start "Ollama" /min ollama serve
timeout /t 6 /nobreak >nul

echo [3/3] Tai mo hinh __MODEL__ (bo qua neu da co)...
ollama pull __MODEL__
if errorlevel 1 goto failed
echo.
echo Xong. Mo GreenScan (CHAY_GREENSCAN.bat), o trang "Tai tai lieu" hoac "Cai dat"
echo chon "Mo hinh chay tren may nay", roi bam "Thu mo hinh".
pause
exit /b 0

:failed
echo.
echo Khong cai duoc tu dong. Tai Ollama tai https://ollama.com/download, cai xong chay lai tep nay.
pause
exit /b 1
"""

README = """GREENSCAN - BẢN CHẠY NGAY (Windows 10/11, 64-bit)
Dựng ngày __DATE__ từ bản mã nguồn "__SOURCE__".

1. CHẠY
   Bấm đúp CHAY_GREENSCAN.bat. Trình duyệt tự mở trang http://localhost:8000
   (nếu cổng 8000 đang bận thì là 8010). Không cần cài gì thêm.
   Lần chạy đầu sau khi giải nén mất khoảng 1 phút; các lần sau khoảng 10 giây.
   Nếu trình duyệt báo chưa kết nối được, đợi vài giây rồi bấm tải lại trang.
   Lần đầu Windows có thể hỏi "Windows protected your PC": chọn More info > Run anyway.
   Muốn dừng: đóng cửa sổ đen.

2. LÀM GÌ TRƯỚC
   Nhập tên người soát xét. Ở đầu mỗi trang có dòng "Việc tiếp theo" nói rõ nên làm gì.
   Thử nhanh: trang "Tải tài liệu" > bấm bộ mẫu "Công ty Minh Họa" > "Bắt đầu phân tích".
   Xem phiên đã chạy sẵn: mục "Lịch sử phân tích" (có báo cáo thật của Hòa Phát, 264 trang).

3. CÓ SẴN TRONG GÓI
   - Toàn bộ quy trình bằng luật và phép tính: đọc PDF/DOCX/HTML/TXT, đọc trang quét (OCR tiếng Việt, tiếng Anh),
     tách tuyên bố, tìm bằng chứng, so số liệu, xếp hàng đợi, ghi quyết định, in giấy làm việc.
   - __RUNS__ phiên mẫu đã chạy, quy tắc nội bộ mẫu của một ngân hàng giả lập, thư viện pháp lý.
   - Câu trả lời đã lưu của mô hình cho bộ mẫu Công ty Minh Họa (bật mô hình là phát lại được ngay).

4. BẬT MÔ HÌNH NGÔN NGỮ CHẠY TRÊN MÁY (tuỳ chọn)
   Bấm đúp CAI_MO_HINH_TREN_MAY.bat một lần: máy tự cài Ollama và tải mô hình __MODEL__
   (khoảng 2,5 GB, cần mạng). Sau đó trong GreenScan chọn "Mô hình chạy trên máy này".
   Máy không có card đồ hoạ vẫn chạy được nhưng chậm: bộ mẫu 5 tuyên bố mất hơn 15 phút ở lần đầu.

5. BẬT MÔ HÌNH TRÊN ĐÁM MÂY (tuỳ chọn, chỉ dùng cho tài liệu đã công bố)
   Mở tệp app\\.env bằng Notepad, điền khoá vào dòng GROQ_API_KEY=, lưu, rồi chạy lại.
   Gói này không kèm khoá nào.

6. DỮ LIỆU CỦA BẠN
   Tài liệu tải lên, phiên phân tích và quyết định nằm trong thư mục du_lieu. Không có gì được gửi ra ngoài,
   trừ khi bạn tự bật mô hình trên đám mây. Xoá thư mục GreenScan là gỡ sạch (Ollama, nếu đã cài, gỡ riêng).
   Nếu thư mục giải nén có dấu tiếng Việt, lần chạy đầu sẽ chép 14 MB dữ liệu đọc ảnh quét sang
   %LOCALAPPDATA%\\GreenScan\\tessdata (chương trình đọc ảnh quét không mở được thư mục có dấu). Gỡ thì xoá thêm thư mục đó.

7. GIỚI HẠN
   Kết quả là tín hiệu để người soát xét khoanh vùng, không phải kết luận pháp lý về doanh nghiệp.
   Chỉ chạy trên Windows 64-bit. Máy khác hệ điều hành: xem README.md trong thư mục app.
"""


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def copy_tree(src: Path, dst: Path) -> int:
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return 1
    count = 0
    for path in src.rglob("*"):
        if path.is_file() and not (SKIP_DIRS & set(path.parts)) and path.suffix != ".pyc":
            target = dst / path.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            count += 1
    return count


def embedded_python(out: Path, cache: Path) -> None:
    version = platform.python_version()
    name = f"python-{version}-embed-amd64.zip"
    archive = cache / name
    if not archive.is_file():
        cache.mkdir(parents=True, exist_ok=True)
        url = f"https://www.python.org/ftp/python/{version}/{name}"
        print("[portable] tải", url, flush=True)
        urllib.request.urlretrieve(url, archive)
    target = out / "python"
    with zipfile.ZipFile(archive) as z:
        z.extractall(target)
    pth = next(target.glob("python*._pth"))
    # Đường dẫn tương đối so với thư mục python/: thư viện đi kèm, rồi mã nguồn GreenScan.
    pth.write_text(f"{pth.stem}.zip\n.\nLib\\site-packages\n..\\app\\src\nimport site\n", encoding="ascii")
    print("[portable] python nhúng", version, flush=True)


def site_packages(out: Path, source: Path) -> None:
    target = out / "python" / "Lib" / "site-packages"
    target.mkdir(parents=True, exist_ok=True)
    deps = tomllib.loads((source / "pyproject.toml").read_text(encoding="utf-8"))["project"]["dependencies"]
    frozen = subprocess.run([sys.executable, "-I", "-m", "pip", "list", "--format=freeze"], capture_output=True, text=True, check=True).stdout
    constraints = out / "_constraints.txt"
    constraints.write_text("\n".join(line for line in frozen.splitlines()
                                     if "==" in line and not line.lower().startswith(("quantum", "greenscan", "pip=="))) + "\n",
                           encoding="utf-8")
    run([sys.executable, "-I", "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--no-compile",
         "--target", str(target), "-c", str(constraints), *deps])
    constraints.unlink()
    shutil.rmtree(target / "bin", ignore_errors=True)
    pruned = 0
    for package in PRUNE_TESTS_IN:
        for tests in list((target / package).rglob("tests")):
            if tests.is_dir():
                pruned += sum(f.stat().st_size for f in tests.rglob("*") if f.is_file())
                shutil.rmtree(tests)
    print(f"[portable] thư viện: {sum(1 for _ in target.iterdir())} mục; bỏ {pruned / 2**20:.0f} MB thư mục tests", flush=True)


def app_env(out: Path) -> None:
    values = {}
    source = ROOT / ".env"
    if source.is_file():
        for line in source.read_text(encoding="utf-8").splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() in ENV_KEYS:
                values[key.strip()] = value.strip()
    values.setdefault("QUANTUM_PROFILE", "offline")
    lines = ["# GreenScan bản chạy ngay: thiết lập không bí mật. Không có khoá nào trong tệp này.",
             *[f"{k}={v}" for k, v in values.items()],
             "", "# Mô hình trên đám mây (tuỳ chọn, chỉ dùng cho tài liệu đã công bố): điền khoá rồi chạy lại.",
             "GROQ_API_KEY="]
    text = "\n".join(lines) + "\n"
    for line in text.splitlines():        # an toàn: không dòng nào mang giá trị cho một biến có vẻ là bí mật
        key, sep, value = line.partition("=")
        assert not (sep and value.strip() and SECRET_NAME.search(key.strip().upper())), key
    (out / "app" / ".env").write_text(text, encoding="utf-8")


def tesseract(out: Path, install: Path, extra_tessdata: Path | None) -> None:
    if not (install / "tesseract.exe").is_file():
        print("[portable] !! không thấy Tesseract ở", install, "- gói sẽ không đọc được trang quét", flush=True)
        return
    target = out / "ocr"
    (target / "tessdata").mkdir(parents=True, exist_ok=True)
    shutil.copy2(install / "tesseract.exe", target)
    for dll in install.glob("*.dll"):
        shutil.copy2(dll, target)
    for data in list((install / "tessdata").glob("*.traineddata")) + (list(extra_tessdata.glob("*.traineddata")) if extra_tessdata else []):
        shutil.copy2(data, target / "tessdata")
    for extra in ("tessdata/configs", "tessdata/tessconfigs"):
        if (install / extra).is_dir():
            shutil.copytree(install / extra, target / extra, dirs_exist_ok=True)
    for doc in ("doc/LICENSE", "doc/AUTHORS"):
        if (install / doc).is_file():
            shutil.copy2(install / doc, target / ("TESSERACT_" + Path(doc).name + ".txt"))

    # Ảnh thử có chữ, rồi bỏ từng DLL mà tesseract không cần để đọc ảnh đó.
    import fitz  # PyMuPDF, có trong môi trường dựng gói
    doc = fitz.open()
    page = doc.new_page(width=420, height=120)
    page.insert_text((20, 70), "GreenScan 2026 OCR", fontsize=28)
    probe = out / "_probe.png"
    page.get_pixmap(dpi=150).save(probe)
    # PATH tối thiểu: nếu để PATH của máy dựng gói, Windows tìm được DLL cùng tên ở thư mục khác (ví dụ của Git)
    # và bước lược bớt sẽ bỏ nhầm tệp mà máy người nhận không có (lỗi 0xC0000135, bắt được khi thử gói 17/11).
    windir = os.environ.get("SystemRoot", "C:/Windows")
    env = {"SystemRoot": windir, "windir": windir, "PATH": f"{windir}/System32;{windir}",
           "TEMP": os.environ.get("TEMP", ""), "TMP": os.environ.get("TMP", ""), "TESSDATA_PREFIX": str(target / "tessdata")}

    def reads() -> bool:
        try:
            r = subprocess.run([str(target / "tesseract.exe"), str(probe), "stdout", "-l", "vie+eng"],
                               capture_output=True, timeout=60, env=env, cwd=target)
        except (OSError, subprocess.TimeoutExpired):
            return False
        if r.returncode != 0 or b"GreenScan" not in r.stdout:
            return False
        langs = subprocess.run([str(target / "tesseract.exe"), "--list-langs"], capture_output=True, timeout=60, env=env, cwd=target)
        return langs.returncode == 0 and b"vie" in langs.stdout          # cách ứng dụng nhận biết có OCR

    assert reads(), "tesseract trong gói không đọc được ảnh thử"
    kept, dropped = 0, 0
    for dll in sorted(target.glob("*.dll")):
        parked = dll.with_suffix(".dll_off")
        dll.rename(parked)
        if reads():
            parked.unlink()
            dropped += 1
        else:
            parked.rename(dll)
            kept += 1
    probe.unlink()
    assert (target / "tessdata" / "vie.traineddata").is_file(), "thiếu dữ liệu tiếng Việt cho OCR"
    size = sum(f.stat().st_size for f in target.rglob("*") if f.is_file()) / 2**20
    print(f"[portable] OCR: giữ {kept} DLL, bỏ {dropped}; {size:.0f} MB", flush=True)


EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
SCRUB_SUFFIXES = {".json", ".jsonl", ".md", ".txt", ".csv", ".yaml", ".yml"}


def scrub(out: Path, store: Path) -> dict:
    """Người nhận không cần biết thư mục trên máy dựng gói hay địa chỉ liên hệ dùng lúc tải dữ liệu.

    - Trong kho phiên mẫu: đường dẫn tuyệt đối tới kho gốc được thay bằng "du_lieu".
    - Trong nhật ký tải báo cáo (download_manifest.json): địa chỉ e-mail trong chuỗi user_agent được ẩn.
    """
    store_text = str(store.resolve())
    variants = set()
    for drive in (store_text[0].lower(), store_text[0].upper()):
        base = drive + store_text[1:]
        variants |= {base, base.replace("\\", "/"), base.replace("\\", "\\\\")}
    counts = {"paths": 0, "emails": 0}
    targets = [f for f in (out / "du_lieu").rglob("*") if f.is_file() and f.suffix in SCRUB_SUFFIXES]
    targets += list((out / "app" / "data").rglob("download_manifest.json"))
    for f in targets:
        if f.stat().st_size > 60 * 2**20:
            continue
        text = f.read_text(encoding="utf-8", errors="surrogateescape")
        new = text
        for v in sorted(variants, key=len, reverse=True):
            if v in new:
                counts["paths"] += new.count(v)
                new = new.replace(v, "du_lieu")
        if f.name == "download_manifest.json":
            new, n = EMAIL.subn("(da an dia chi lien he)", new)
            counts["emails"] += n
        if new != text:
            f.write_text(new, encoding="utf-8", errors="surrogateescape")
    return counts


def write_bat(path: Path, text: str) -> None:
    assert text.isascii(), path.name          # tệp lệnh chỉ dùng ASCII để không phụ thuộc bảng mã của máy
    path.write_bytes(text.replace("\r\n", "\n").replace("\n", "\r\n").encode("ascii"))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")     # chạy với -I thì PYTHONIOENCODING bị bỏ qua
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="Thư mục mã nguồn đã chốt (checkpoint .../GreenScan-AI)")
    ap.add_argument("--store", required=True, help="Kho phiên mẫu (runs, documents, reviews, org_packs)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--llm-cache", default=str(ROOT / ".quantum" / "llm_cache"))
    ap.add_argument("--tesseract", default=r"C:\Program Files\Tesseract-OCR")
    ap.add_argument("--tessdata", default=str(Path(os.environ.get("LOCALAPPDATA", "")) / "GreenScan" / "tessdata"))
    ap.add_argument("--zip", action="store_true")
    args = ap.parse_args()
    source, store, base = Path(args.source), Path(args.store), Path(args.out)
    out = base / "GreenScan"
    assert (source / "src" / "quantum_gw").is_dir(), source
    assert (source / "frontend" / "dist" / "index.html").is_file(), "bản mã nguồn chưa có giao diện đã dựng"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    embedded_python(out, base / "_cache")
    site_packages(out, source)
    files = sum(copy_tree(source / part, out / "app" / part) for part in APP_PARTS if (source / part).exists())
    app_env(out)
    cache = Path(args.llm_cache)
    if cache.is_dir():
        files += copy_tree(cache, out / "app" / ".quantum" / "llm_cache")
    for part in STORE_PARTS:
        if (store / part).exists():
            files += copy_tree(store / part, out / "du_lieu" / part)
    runs = sum(1 for d in (out / "du_lieu" / "runs").iterdir() if (d / "result.json").is_file())
    tessdata = Path(args.tessdata)
    tesseract(out, Path(args.tesseract), tessdata if tessdata.is_dir() else None)
    print("[portable] đã ẩn:", scrub(out, store), flush=True)

    write_bat(out / "CHAY_GREENSCAN.bat", LAUNCHER)
    write_bat(out / "CAI_MO_HINH_TREN_MAY.bat", MODEL_SETUP.replace("__MODEL__", OLLAMA_MODEL))
    stamp = datetime.now().strftime("%d/%m/%Y")
    (out / "DOC_TRUOC.txt").write_text(
        README.replace("__DATE__", stamp).replace("__SOURCE__", source.parent.name).replace("__RUNS__", str(runs))
        .replace("__MODEL__", OLLAMA_MODEL), encoding="utf-8-sig")

    all_files = [f for f in out.rglob("*") if f.is_file()]
    size = sum(f.stat().st_size for f in all_files) / 2**20
    for f in all_files:                    # không tệp .env nào khác ngoài tệp vừa ghi, không tệp khoá
        assert f.name != ".env" or f.parent == out / "app", f
    print(f"[portable] {out}: {len(all_files)} tệp, {size:.0f} MB, {runs} phiên mẫu", flush=True)

    if args.zip:
        archive = base / f"GreenScan_chay_ngay_{datetime.now():%Y-%m-%d}.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for f in sorted(all_files):
                z.write(f, f.relative_to(base).as_posix())
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        print(f"[portable] {archive}: {archive.stat().st_size / 2**20:.1f} MB, sha256 {digest}", flush=True)


if __name__ == "__main__":
    main()
