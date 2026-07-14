from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import fitz


class TesseractOCR:
    def __init__(self, command: str = "tesseract", languages: str = "vie+eng"):
        self.command = command
        self.languages = languages

    @property
    def available(self) -> bool:
        return shutil.which(self.command) is not None

    def ocr_page(self, page: fitz.Page, dpi: int = 220) -> str:
        if not self.available:
            return ""
        pixmap = page.get_pixmap(dpi=dpi, alpha=False)
        with tempfile.TemporaryDirectory(prefix="quantum-ocr-") as tmp:
            image_path = Path(tmp) / "page.png"
            output_base = Path(tmp) / "out"
            pixmap.save(str(image_path))
            command = [
                self.command,
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
