"""Build the source-code archive for the AI-Quantum Challenge 2026 Round 2 submission.

    AQ2026-R2-<Madoi>-Ma_nguon.zip   (Thông báo Vòng 2, mục II.3: one archive, not a repository link)

What goes in: every file git tracks or would track (.gitignore respected), plus the built web UI
(frontend/dist, so the jury needs no Node.js) and the seeded demo runs (deploy/seed).
What stays out: secrets (.env and anything that looks like a key -- the build STOPS if one is found),
caches and installed packages, the 4 GB crawl corpus, third-party reference PDFs, experiment outputs,
and large binaries outside the sample data the prototype needs.

Usage (repository root):
  .venv/Scripts/python.exe -I tools/package_submission.py --ma-doi AQ2026-119 [--out "D:/…/nop_vong2"] [--dry-run]
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import re
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOP = "GreenScan-AI"
MAX_FILE_MB = 3.0

ALWAYS_INCLUDE_DIRS = ["frontend/dist", "deploy/seed"]
# Gitignored because the repository does not redistribute third-party originals, but the jury's
# check (Hướng dẫn, mục 5: re-run the Hòa Phát analysis) needs these two public reports.
ALWAYS_INCLUDE_FILES = ["data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf",
                        "data/real_cases/sources/originals/HPG_Annual_Report_2024.pdf"]
EXCLUDE = [
    ".env", ".env.*", "*/.env", "*/.env.*",
    ".git/*", ".venv/*", ".quantum/*", "*/node_modules/*", "*__pycache__*", "*.pyc", ".pytest_cache/*",
    "data/crawl/*", "data/legal_cases/*",
    "data/legal/raw/*.pdf", "data/legal/raw/*.doc", "data/legal/raw/*.docx", "data/legal/raw/*.htm", "data/legal/raw/*.html",
    "docs/reference/*", "outside_resource/*",
    "experiments/*/out/*", "experiments/*/kaggle_*/*", "training/runs/*",
    "*.mp4", "*.mov", "*.zip", "*.7z", "*.pptx", "*.log",
]
KEEP_EXCEPTION = [".env.example"]
# Large files allowed because the prototype or its check needs them.
LARGE_OK = ["data/real_cases/sources/originals/*", "deploy/seed/*", "frontend/dist/*",
            "benchmark/gs_eval_v2/inputs/pool_a.jsonl"]

SECRET_PATTERNS = [
    ("Groq key", re.compile(r"gsk_[A-Za-z0-9]{20,}")),
    ("OpenAI/OpenRouter key", re.compile(r"(?<![A-Za-z0-9])sk-(?:or-|proj-)?[A-Za-z0-9_-]{24,}")),
    ("Anthropic key", re.compile(r"(?<![A-Za-z0-9])sk-ant-[A-Za-z0-9_-]{20,}")),
    ("Google key", re.compile(r"AIza[0-9A-Za-z_-]{30,}")),
    ("Hugging Face token", re.compile(r"hf_[A-Za-z0-9]{30,}")),
    ("Kaggle key", re.compile(r"\"key\"\s*:\s*\"[0-9a-f]{32}\"")),
    ("Assigned secret", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|access[_-]?token|auth[_-]?token|password)\b\s*[:=]\s*['\"]?(?!your|xxx|<|\$\{|changeme|example)[A-Za-z0-9_\-]{20,}")),
]
TEXT_SUFFIXES = {".py", ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".js", ".jsx",
                 ".ts", ".html", ".css", ".sh", ".bat", ".ps1", ".env", ".example", ".csv", ".ipynb", ".tex"}


def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, p) or fnmatch.fnmatch("/" + path, "*/" + p) for p in patterns)


def candidate_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT, capture_output=True, check=True,
    ).stdout.decode("utf-8", "replace").split("\0")
    files = {f for f in out if f}
    for d in ALWAYS_INCLUDE_DIRS:
        base = ROOT / d
        if base.is_dir():
            files.update(p.relative_to(ROOT).as_posix() for p in base.rglob("*") if p.is_file())
    files.update(f for f in ALWAYS_INCLUDE_FILES if (ROOT / f).is_file())
    return sorted(f for f in files if (ROOT / f).is_file())


def select(files: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    keep, dropped = [], []
    for f in files:
        name = f.rsplit("/", 1)[-1]
        if name not in KEEP_EXCEPTION and matches(f, EXCLUDE):
            dropped.append((f, "excluded"))
            continue
        size_mb = (ROOT / f).stat().st_size / 1e6
        if size_mb > MAX_FILE_MB and not matches(f, LARGE_OK):
            dropped.append((f, f"large {size_mb:.1f} MB"))
            continue
        keep.append(f)
    return keep, dropped


def scan_secrets(files: list[str]) -> list[str]:
    hits = []
    for f in files:
        p = ROOT / f
        if p.suffix.lower() not in TEXT_SUFFIXES and not p.name.startswith(".env"):
            continue
        if p.stat().st_size > 5e6:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for label, pattern in SECRET_PATTERNS:
            for m in pattern.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                hits.append(f"{f}:{line}: {label}: {m.group(0)[:12]}…")
    return hits


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ma-doi", required=True, help="Mã đội, ví dụ AQ2026-119")
    ap.add_argument("--out", default=str(ROOT.parents[2] / "nop_vong2"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files, dropped = select(candidate_files())
    hits = scan_secrets(files)
    total = sum((ROOT / f).stat().st_size for f in files)
    print(f"Chọn {len(files)} tệp ({total / 1e6:.1f} MB trước nén); bỏ {len(dropped)} tệp.")
    big_drops = sorted(((f, why) for f, why in dropped if why.startswith("large")), key=lambda x: x[0])
    for f, why in big_drops[:15]:
        print(f"  bỏ ({why}): {f}")
    if hits:
        print("\nDỪNG: có chuỗi giống khoá bí mật trong tệp sẽ nộp. Xoá khoá hoặc loại tệp rồi chạy lại:")
        for h in hits[:40]:
            print("  " + h)
        raise SystemExit(2)
    if not (ROOT / "frontend/dist/index.html").is_file():
        raise SystemExit("DỪNG: chưa có frontend/dist — chạy `npm run build` trong frontend/ trước.")
    if args.dry_run:
        print("Chạy thử: không ghi tệp zip.")
        return

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"AQ2026-R2-{args.ma_doi}-Ma_nguon.zip"
    manifest = [f"# {target.name}", f"# Tạo lúc {datetime.now().isoformat(timespec='seconds')} bằng tools/package_submission.py",
                f"# {len(files)} tệp; sha256 từng tệp bên dưới", ""]
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in files:
            data = (ROOT / f).read_bytes()
            manifest.append(f"{hashlib.sha256(data).hexdigest()}  {f}")
            z.writestr(f"{TOP}/{f}", data)
        z.writestr(f"{TOP}/MANIFEST_NOP_BAI.txt", "\n".join(manifest) + "\n")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    print(f"\nĐã ghi {target} ({target.stat().st_size / 1e6:.1f} MB), sha256 {digest}")


if __name__ == "__main__":
    main()
