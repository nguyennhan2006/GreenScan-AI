"""Chốt một checkpoint mã nguồn để nộp bài, tách khỏi bản đang sửa.

Sao đúng bộ tệp mà tools/package_submission.py sẽ đưa vào zip nộp bài sang
<out>/<name>/GreenScan-AI/, rồi ghi:
  - MANIFEST.txt: sha256 từng tệp;
  - CHECKPOINT.md: git HEAD, số thay đổi chưa commit, kết quả kiểm thử (nếu truyền vào), cách dùng;
  - AQ2026-R2-<ma_doi>-Ma_nguon.zip: dựng từ chính bản sao, nên nộp tệp này là nộp đúng checkpoint.

Sau khi chốt, repo được sửa thoải mái; bài nộp lấy từ checkpoint, không lấy từ repo.

    .venv/Scripts/python.exe -I tools/make_checkpoint.py --ma-doi AQ2026-119 \
        --name vong2_2026-11-14 --tests "530 passed"
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import re
import zipfile
from datetime import datetime
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import package_submission as ps  # noqa: E402  (same selection rules as the zip)

ROOT = ps.ROOT


EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")


PLACEHOLDER = "<thu_muc_du_an>"


def _spellings(base: str) -> set[str]:
    out = set()
    for drive in {base[0].lower(), base[0].upper()}:
        b = drive + base[1:]
        forms = {b, b.replace("\\", "/"), b.replace("\\", "\\\\"), "/" + drive.lower() + b[2:].replace("\\", "/")}
        for v in forms:
            out |= {v, v.encode("ascii", "backslashreplace").decode("ascii").replace("\\x", "\\u00")}
    return out


def local_prefixes() -> list[tuple[str, str]]:
    """Folders of the build machine, in every spelling a text file may use (Windows, forward slash,
    JSON-escaped, Git Bash), each with the placeholder that replaces it in the submitted copy.

    Docs, logs and configs written on the build machine name absolute paths; the submitted copy shows a
    neutral placeholder instead. Worked out from ROOT at run time, so no path is written in this file.
    """
    project = str(ROOT.parents[2].resolve())       # the folder holding docs/greenscan-ai/GreenScan-AI
    home = str(ROOT.parents[3].resolve())          # the folder above it, named in a few notes
    pairs = [(v, PLACEHOLDER) for v in _spellings(project)]
    if len(home) > 3:                              # never a bare drive root
        pairs += [(v, "<thu_muc_may>") for v in _spellings(home)]
    return sorted(set(pairs), key=lambda p: len(p[0]), reverse=True)


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True).stdout.decode(
            "utf-8", "replace").strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ma-doi", required=True)
    ap.add_argument("--name", default=f"vong2_{datetime.now():%Y-%m-%d}")
    ap.add_argument("--out", default=str(ROOT.parents[2] / "checkpoint_nop_bai"))
    ap.add_argument("--tests", default="", help="Kết quả kiểm thử đã chạy trên đúng trạng thái này")
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    files, dropped = ps.select(ps.candidate_files())
    hits = ps.scan_secrets(files)
    if hits:
        print("DỪNG: có chuỗi giống khoá bí mật:")
        for h in hits[:40]:
            print("  " + h)
        raise SystemExit(2)
    if not (ROOT / "frontend/dist/index.html").is_file():
        raise SystemExit("DỪNG: chưa có frontend/dist — chạy `npm run build` trong frontend/ trước.")

    dest = Path(args.out) / args.name
    if dest.exists():
        raise SystemExit(f"DỪNG: {dest} đã có. Checkpoint không bị ghi đè; chọn --name khác.")
    code = dest / ps.TOP
    code.mkdir(parents=True)

    manifest = []
    total = 0
    emails = 0
    paths = 0
    prefixes = local_prefixes()
    for f in files:
        src, dst = ROOT / f, code / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if Path(f).suffix.lower() in ps.TEXT_SUFFIXES:
            raw = dst.read_bytes()
            try:
                enc, text = "utf-8", raw.decode("utf-8")
            except UnicodeDecodeError:
                enc, text = "cp1252", raw.decode("cp1252", errors="surrogateescape")   # a few Windows console logs
            if any(v in text for v, _ in prefixes):
                for v, holder in prefixes:
                    paths += text.count(v)
                    text = text.replace(v, holder)
                dst.write_bytes(text.encode(enc, errors="surrogateescape"))
        if f.endswith("download_manifest.json"):
            # The download log names the team member's e-mail in its user_agent string: hidden in the
            # submitted copy, as tools/build_portable.py does (the repo keeps the original record).
            text, n = EMAIL.subn("(da an dia chi lien he)", dst.read_text(encoding="utf-8"))
            dst.write_text(text, encoding="utf-8")
            emails += n
        data = dst.read_bytes()
        total += len(data)
        manifest.append(f"{hashlib.sha256(data).hexdigest()}  {f}")
    (dest / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    zip_path = dest / f"AQ2026-R2-{args.ma_doi}-Ma_nguon.zip"
    header = [f"# {zip_path.name}", f"# Checkpoint {args.name}, tạo lúc {datetime.now().isoformat(timespec='seconds')}"
              " bằng tools/make_checkpoint.py", f"# {len(files)} tệp; sha256 từng tệp bên dưới", ""]
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in files:
            z.writestr(f"{ps.TOP}/{f}", (code / f).read_bytes())
        z.writestr(f"{ps.TOP}/MANIFEST_NOP_BAI.txt", "\n".join(header + manifest) + "\n")
    zip_sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()

    head = git("log", "-1", "--format=%H %ci %s")
    dirty = [line for line in git("status", "--porcelain").splitlines() if line.strip()]
    big = sorted((f, why) for f, why in dropped if why.startswith("large"))
    lines = [
        f"# Checkpoint nộp bài `{args.name}`",
        "",
        f"- Tạo lúc: {datetime.now().isoformat(timespec='seconds')}",
        f"- Nguồn: `{ROOT}`",
        f"- Git HEAD: `{head or 'không đọc được'}`; thay đổi chưa commit lúc chốt: {len(dirty)} (đã chụp vào bản sao).",
        f"- Số tệp: {len(files)} ({total / 1e6:.1f} MB trước nén); bỏ {len(dropped)} tệp theo quy tắc của"
        " `tools/package_submission.py`.",
        f"- Kiểm thử trên đúng trạng thái này: {args.tests or 'chưa ghi'}",
        f"- Zip nộp bài: `{zip_path.name}`, sha256 `{zip_sha}`",
    ]
    if args.note:
        lines.append(f"- Ghi chú: {args.note}")
    lines += [
        "",
        "## Cách dùng",
        "",
        "- **Không sửa thư mục này.** Mọi thay đổi làm ở repo; checkpoint chỉ để nộp và để đối chiếu.",
        "- Nộp mã nguồn: dùng đúng tệp zip ở trên (đổi tên nếu BTC yêu cầu, không dựng lại).",
        "- Kiểm lại một tệp: so sha256 với `MANIFEST.txt`.",
        "- Chạy lại sản phẩm từ checkpoint: giải nén zip ra thư mục mới rồi làm theo `README.md` / Hướng dẫn.",
        "- Muốn chốt bản mới: chạy lại `tools/make_checkpoint.py` với `--name` khác; bản cũ giữ nguyên.",
    ]
    if big:
        lines += ["", "## Tệp lớn bị bỏ (giống zip nộp bài)", ""] + [f"- `{f}` ({why})" for f, why in big]
    (dest / "CHECKPOINT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Đã ẩn {emails} địa chỉ e-mail trong download_manifest.json")
    print(f"Đã thay {paths} đường dẫn thư mục trên máy dựng bằng {PLACEHOLDER} / <thu_muc_may>")
    print(f"Đã chốt {dest}: {len(files)} tệp, zip {zip_path.stat().st_size / 1e6:.1f} MB, sha256 {zip_sha}")


if __name__ == "__main__":
    main()
