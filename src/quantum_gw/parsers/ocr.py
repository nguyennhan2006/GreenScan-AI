from __future__ import annotations

import shutil
import subprocess
import tempfile
from functools import cache
from pathlib import Path

import fitz

# The Windows installer (UB Mannheim) does not add tesseract to PATH.
WINDOWS_TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")


def resolve_command(command: str) -> str | None:
    """`command` found on PATH or as a path, else the default Windows install; None when absent."""
    found = shutil.which(command)
    if found is None and command == "tesseract" and WINDOWS_TESSERACT.exists():
        found = str(WINDOWS_TESSERACT)
    return found


@cache
def installed_languages(command: str) -> frozenset[str]:
    """Languages tesseract can load (TESSDATA_PREFIX is honoured); empty when it cannot run."""
    try:
        completed = subprocess.run(
            [command, "--list-langs"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return frozenset()
    # The first line is a header: List of available languages in "...tessdata/" (N):
    return frozenset(line.strip() for line in completed.stdout.splitlines()[1:] if line.strip())


class TesseractOCR:
    def __init__(self, command: str = "tesseract", languages: str = "vie+eng"):
        self.command = command
        self.languages = languages

    @property
    def available(self) -> bool:
        # A missing vie.traineddata makes every call fail, which used to look like a blank page.
        resolved = resolve_command(self.command)
        return resolved is not None and set(self.languages.split("+")) <= installed_languages(resolved)

    def ocr_page(self, page: fitz.Page, dpi: int = 220) -> str:
        if not self.available:
            return ""
        pixmap = page.get_pixmap(dpi=dpi, alpha=False)
        with tempfile.TemporaryDirectory(prefix="quantum-ocr-") as tmp:
            image_path = Path(tmp) / "page.png"
            output_base = Path(tmp) / "out"
            pixmap.save(str(image_path))
            command = [
                resolve_command(self.command),
                str(image_path),
                str(output_base),
                "-l",
                self.languages,
                "--psm",
                "6",
            ]
            completed = subprocess.run(command, capture_output=True, text=True, timeout=120)
            if completed.returncode != 0:
                return ""
            output_path = output_base.with_suffix(".txt")
            return output_path.read_text(encoding="utf-8", errors="ignore") if output_path.exists() else ""
