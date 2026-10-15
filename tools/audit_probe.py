"""Re-run the deliberate break attempts and the run statistics behind AUDIT_HE_THONG_2026-10.md.

Usage:  .venv\\Scripts\\python tools\\audit_probe.py [run_id]

Without a run id it takes the newest saved run that has a priority queue. It
writes nothing: inputs for the break attempts go to a temporary folder.
"""

from __future__ import annotations

import sys
import tempfile
from collections import Counter
from pathlib import Path

import fitz

from quantum_gw import intake
from quantum_gw.domain.models import DocumentInput
from quantum_gw.parsers.documents import DocumentParser
from quantum_gw.settings import load_settings
from quantum_gw.storage.runs import RunStore
from quantum_gw.studio.export import docx_from_lines


def _break_inputs(settings) -> None:
    parser = DocumentParser(settings.intake)
    tmp = Path(tempfile.mkdtemp())
    line = "Năm 2024 Tập đoàn giảm 30% phát thải khí nhà kính so với năm 2020."
    (tmp / "a.docx").write_bytes(docx_from_lines([line], [line], [None], [], "", tracked=False))
    (tmp / "a.html").write_text(f"<p>{line}</p>", encoding="utf-8")
    page = fitz.open().new_page()
    page.insert_text((72, 72), "Giam 30% phat thai CO2 nam 2024", fontsize=18)
    scan = fitz.open()
    image_page = scan.new_page(width=page.rect.width, height=page.rect.height)
    image_page.insert_image(image_page.rect, pixmap=page.get_pixmap(dpi=150))
    scan.save(tmp / "scan.pdf")
    for name in ("a.docx", "a.html", "scan.pdf"):
        try:
            chunks = parser.parse(DocumentInput(path=str(tmp / name)))
            print(f"  {name:9s} → {len(chunks)} đoạn")
        except Exception as exc:  # noqa: BLE001 - the failure is the finding
            print(f"  {name:9s} → {type(exc).__name__}: {exc}")
    preview = intake.preview_file(tmp / "scan.pdf", "scan.pdf", settings.intake)
    print(f"  OCR có sẵn: {preview['ocr_available']} · cảnh báo xem trước: {preview['warnings']}")


def _run_stats(result) -> None:
    v = result.verifications
    evidence = [e for x in v for e in x.evidence]
    claims = result.claims
    legal = getattr(result, "legal_checks", None) or []
    print(f"  tuyên bố: {len(claims)} · verdict: {dict(Counter(x.status.value for x in v))}")
    print(f"  bằng chứng: {len(evidence)} · nguồn: {dict(Counter(e.source_type.value for e in evidence))}"
          f" · quan hệ: {dict(Counter(getattr(e, 'relation', None) for e in evidence))}")
    print(f"  pháp lý: {dict(Counter(lc.get('legal_finding') for lc in legal))} · có quy tắc áp dụng: "
          f"{sum(bool(lc.get('rules_applied')) for lc in legal)}")
    print(f"  mơ hồ {sum(c.is_vague for c in claims)} · có số {sum(bool(c.values) for c in claims)} · thiếu kỳ "
          f"{sum(c.period is None for c in claims)} · thiếu năm gốc {sum(c.baseline is None for c in claims)}")
    print(f"  số liệu công bố {len(result.disclosed_figures)} · phép kiểm {dict(Counter(f.status for f in result.figure_checks))}")
    print(f"  hàng đợi {sum(bool(p.get('in_queue')) for p in result.priorities)} · chưa tính: "
          f"{dict(Counter(n for p in result.priorities for n in p.get('not_computed', [])))}")
    print(f"  severity {dict(Counter(str(r.severity.value) for r in result.risks))}")


def main() -> None:
    settings = load_settings()
    store = RunStore(settings.runs_dir)
    run_id = sys.argv[1] if len(sys.argv) > 1 else None
    if run_id is None:
        for row in store.list(limit=200):
            candidate = store.load(row["run_id"])
            if candidate.priorities:
                run_id = row["run_id"]
                break
    print("1. Thử phá đầu vào")
    _break_inputs(settings)
    if run_id:
        print(f"2. Thống kê phiên {run_id} ({store.label_of(run_id)})")
        _run_stats(store.load(run_id))
    else:
        print("2. Không có phiên nào có hàng đợi ưu tiên.")


if __name__ == "__main__":
    main()
