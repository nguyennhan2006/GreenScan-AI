"""page-regions-v1 and figure-tension-v1 (17/11/2026): page layout, table figures, table arithmetic, absolute claims."""
from types import SimpleNamespace

import fitz

from quantum_gw.agents.figures import keep_material, table_checks
from quantum_gw.agents.prioritizer import _figure_tension
from quantum_gw.domain.models import DisclosedFigure
from quantum_gw.parsers import layout


def _page_with_columns_and_grid():
    doc = fitz.open()
    page = doc.new_page(width=800, height=600)
    left = ["Left column line one is about water.", "Left column line two goes on.", "Left column line three ends."]
    right = ["Right column line one is about steel.", "Right column line two goes on.", "Right column line three."]
    # Each column written as its own run of text, as a layout program writes a two-column page.
    for x, column in ((40, left), (440, right)):
        for i, line in enumerate(column):
            page.insert_text((x, 60 + 16 * i), line, fontsize=10, fontname="helv")
    page.insert_text((440, 300), "(Nghin tan)", fontsize=10, fontname="helv")
    rows = [("Tong chat thai ran phat sinh", "7,085"), ("Chat thai khong nguy hai", "6,838"), ("Chat thai nguy hai", "247")]
    for i, (label, value) in enumerate(rows):
        page.insert_text((440, 330 + 20 * i), label, fontsize=10, fontname="helv")
        page.insert_text((720, 330 + 20 * i), value, fontsize=10, fontname="helv")
    return doc, page


def test_columns_are_read_one_after_the_other_and_the_grid_is_a_table():
    doc, page = _page_with_columns_and_grid()
    laid = layout.analyze(layout.lines_from_page(page), page.rect.width, page)
    text = laid.text
    assert text.index("Left column line three") < text.index("Right column line one")
    assert len(laid.tables) == 1
    table = laid.tables[0]
    assert table.kind == "grid" and table.style == "en"
    values = [c.value for r in table.rows for c in r.cells]
    assert values == [7_085_000, 6_838_000, 247_000]
    assert "Tong chat thai" not in text  # table rows are not prose


def test_number_style_is_decided_per_table():
    assert layout.separators(["7,085", "6,838", "247"]) == "en"
    assert layout.separators(["22.540.603", "933.876"]) == "vi"
    assert layout.separators(["38,52"]) == "vi"
    assert layout.parse_number("7,085", "en") == (7085.0, False)
    assert layout.parse_number("22.540.603", "vi") == (22540603.0, False)
    assert layout.unit_of("Số dư (tỷ VND)") == ("VND", 1e9)
    assert layout.unit_of("CHỈ TIÊU (NGHÌN TẤN)") == ("tấn", 1e3)


def _fig(fid, label, value, unit, chunk="t1", page=8, total=False, raw=None):
    return DisclosedFigure(figure_id=fid, label=label, value=value, unit=unit, is_total=total, source_doc_id="d",
                           source_chunk_id=chunk, source_name="r.pdf", source_page=page,
                           raw_line=raw or f"{label} | {value}", metric=None)


def test_page_sum_and_ratio_on_an_allocation_report():
    figures = [
        _fig("issued", "TCBL · Số tiền bán (tỷ VND)", 450e9, "VND", chunk="t2"),
        _fig("issued_total", "Tổng · Số tiền bán (tỷ VND)", 450e9, "VND", chunk="t2", total=True),
        _fig("alloc", "Số tiền được phân bổ", 399e9, "VND", raw="Số tiền được phân bổ | 89% | 399"),
        _fig("alloc_pct", "Số tiền được phân bổ · Tỷ lệ", 89, "%", raw="Số tiền được phân bổ | 89% | 399"),
        _fig("left", "Số tiền còn lại chưa phân bổ", 51e9, "VND"),
    ]
    checks = table_checks(figures)
    kinds = {(c.kind, c.status) for c in checks}
    assert ("page_sum", "CONSISTENT") in kinds and ("ratio", "CONSISTENT") in kinds
    ratio = next(c for c in checks if c.kind == "ratio")
    assert "88,67 %" in ratio.calculation and "89 %" in ratio.calculation


def test_a_percentage_that_is_not_a_share_is_not_a_finding():
    raw = "Thép | 6.809,6 | 99%"
    figures = [
        _fig("steel", "Thép · (NGHÌN TẤN)", 6_809_600, "tấn", raw=raw),
        _fig("steel_pct", "Thép · TÁI SỬ DỤNG", 99, "%", raw=raw),
        _fig("agri", "Nông nghiệp · (NGHÌN TẤN)", 114_500, "tấn"),
        _fig("total", "Cộng · (NGHÌN TẤN)", 6_924_100, "tấn", total=True),
    ]
    checks = table_checks(figures)
    assert not [c for c in checks if c.status == "INCONSISTENT"]
    assert any(c.kind == "table_sum" and c.status == "CONSISTENT" for c in checks)


def test_unnamed_table_cells_stay_out_unless_a_check_used_them():
    noise = _fig("noise", "Công ty con · Vốn điều lệ", 5e11, "VND")
    used = _fig("used", "Số tiền còn lại", 51e9, "VND")
    check = SimpleNamespace(figure_ids=["used"])
    assert [f.figure_id for f in keep_material([noise, used], [check])] == ["used"]


def _claim(text, metric="water", future=False):
    return SimpleNamespace(text=text, metric=metric, is_future_commitment=future, source_doc_id="d")


def test_an_absolute_claim_meets_a_nonzero_figure_of_its_subject():
    water = _fig("w", "Nước thải hoàn trả lại môi trường sau khi qua hệ thống xử lý", 4.994e9, "lít")
    water.metric = "water"
    hit = _figure_tension(_claim("Các khu liên hợp hoàn toàn không có nước thải công nghiệp xả ra môi trường."), [water])
    assert hit is water
    assert _figure_tension(_claim("Tập đoàn hướng tới phát thải ròng bằng 0 vào năm 2050.", "emissions", True), [water]) is None
    assert _figure_tension(_claim("Nước thải được xử lý đạt QCVN 40:2011."), [water]) is None


def test_the_tension_reason_names_the_row_and_prints_the_number_as_the_page_does():
    import tempfile
    from pathlib import Path

    from quantum_gw.agents.prioritizer import PrioritizationAgent
    from quantum_gw.storage.audit import AuditLogger

    agent = PrioritizationAgent("configs/priority_v1.yaml", AuditLogger(Path(tempfile.mkdtemp()) / "a.jsonl"))
    water = _fig("w", "Nước thải hoàn trả lại môi trường sau khi qua hệ thống xử lý · (Triệu lít)", 4.994e9, "lít",
                 page=48)
    water.metric = "water"
    part = agent._claim_anomaly(_claim("Các khu liên hợp hoàn toàn không có nước thải công nghiệp xả ra môi trường."),
                                [water])
    assert part.score == part.max_score
    assert "“Nước thải hoàn trả lại môi trường sau khi qua hệ thống xử lý” trang 48" in part.reason
    assert "4.994 triệu" in part.reason and "Triệu lít)" not in part.reason
    assert "cần người xem" in part.reason


def test_a_table_sum_is_written_in_the_scale_the_page_prints():
    rows = [_fig("a", "Nước thải hoàn trả · (Triệu lít)", 4.994e9, "lít", page=48),
            _fig("b", "Nước tiêu thụ · (Triệu lít)", 41.334e9, "lít", page=48),
            _fig("t", "Nước khai thác · (Triệu lít)", 46.328e9, "lít", page=48, total=True)]
    for f in rows:
        f.metric = "water"
    checks = table_checks(rows, [])
    assert any(c.calculation == "4.994 + 41.334 = 46.328; công bố 46.328 triệu lít" for c in checks), \
        [c.calculation for c in checks]


def test_a_share_column_adds_up_to_its_total_row():
    rows = [_fig("s1", "Thép · TỶ TRỌNG", 99.55, "%"), _fig("s2", "Nông nghiệp · TỶ TRỌNG", 0.39, "%"),
            _fig("s3", "Bất động sản · TỶ TRỌNG", 0.06, "%"), _fig("st", "Cộng · TỶ TRỌNG", 100.0, "%", total=True)]
    checks = table_checks(rows, [])
    share = [c for c in checks if c.kind == "table_sum"]
    assert share and share[0].status == "CONSISTENT" and "st" in share[0].figure_ids
    assert share[0].calculation.startswith("99,55 + 0,39 + 0,06 = 100,00 %")
