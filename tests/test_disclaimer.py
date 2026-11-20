"""Việc 34–35: the mandatory notice heads every output, word for word, and the queue
exports to a CSV table that opens in Excel."""
import csv
import io
import re
import zipfile
from pathlib import Path

import pytest

from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.domain.models import DocumentInput
from quantum_gw.labels_vi import DISCLAIMER_VI
from quantum_gw.queue_csv import HEADER, render_queue_csv
from quantum_gw.settings import load_settings
from quantum_gw.workpaper import render_workpaper

ROOT = Path(__file__).resolve().parent.parent
CLAIMS = ("Năm 2024, Tập đoàn giảm 12% phát thải khí nhà kính phạm vi 1 so với năm 2020. "
          "Tổng lượng nước tiêu thụ năm 2024 là 1.250.000 m3.")
EVIDENCE = "Năm 2024, phát thải khí nhà kính phạm vi 1 của Tập đoàn giảm 12% so với năm 2020."


@pytest.fixture(scope="module")
def result(tmp_path_factory):
    settings = load_settings("configs/default.yaml")
    settings.runs_dir = str(tmp_path_factory.mktemp("disclaimer_runs"))
    docs = [DocumentInput(name="bao_cao.txt", text=CLAIMS, role="claim_source", source_type="internal"),
            DocumentInput(name="doi_chieu.txt", text=EVIDENCE, role="evidence", source_type="external")]
    return OrchestratorAgent(settings).run(docs)


def test_frontend_shows_the_same_words():
    js = (ROOT / "frontend" / "src" / "lib" / "labels.js").read_text(encoding="utf-8")
    front = re.search(r"export const DISCLAIMER = '([^']+)'", js).group(1)
    assert front == DISCLAIMER_VI
    assert "{DISCLAIMER}" in (ROOT / "frontend" / "src" / "components" / "Shell.jsx").read_text(encoding="utf-8")


def test_working_paper_and_evidence_pack_open_with_the_notice(result):
    html = render_workpaper(result)
    assert DISCLAIMER_VI in html and html.index(DISCLAIMER_VI) < html.index("Đơn vị được xem xét")
    pack = (Path(result.output_directory) / "evidence_pack.md").read_text(encoding="utf-8")
    assert DISCLAIMER_VI in pack.split("\n- Run ID")[0]


def test_studio_reports_open_with_the_notice():
    from quantum_gw.studio import report
    ctx = {"doc_name": "bao_cao.pdf", "run_id": "r1", "exported_at": "2026-11-11T07:00:00+00:00", "user": "Nhân",
           "layout_note": "—", "items": [], "kept": [], "open": {"error": 0, "warning": 0, "info": 0},
           "source_sha256": "a" * 64, "base_sha256": "b" * 64, "final_sha256": "c" * 64}
    assert DISCLAIMER_VI in report.render_html(ctx)
    xml = zipfile.ZipFile(io.BytesIO(report.render_docx(ctx))).read("word/document.xml").decode("utf-8")
    assert DISCLAIMER_VI in xml


def test_queue_csv_opens_with_the_notice_then_the_table(result):
    data = render_queue_csv(result)
    assert data[:3] == bytes([0xEF, 0xBB, 0xBF])  # BOM: Excel reads the file as UTF-8
    rows = list(csv.reader(io.StringIO(data.decode("utf-8-sig"))))
    assert rows[0] == [DISCLAIMER_VI] and rows[1] == HEADER
    body = rows[2:]
    assert len(body) == len(result.priorities) and body
    assert {r[1] for r in body} <= {"có", "không"}
    queued = [r for r in body if r[1] == "có"]
    assert body[:len(queued)] == queued  # queue first
