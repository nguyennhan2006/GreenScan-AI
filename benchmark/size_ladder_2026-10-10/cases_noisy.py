"""Real noisy pages as evidence, claims with truth read off the page by hand.

Evidence is the raw text PyMuPDF extracts from three public HPG pages — flattened
tables, glued columns, several figures per paragraph. Same label scheme as
cases.py (S / C / N; several labels where an auditor could accept either).
"""
from pathlib import Path

import pymupdf

_ROOT = Path.cwd() / "data/real_cases/sources/originals"


def _page(name: str, page: int) -> str:
    return pymupdf.open(_ROOT / name)[page - 1].get_text()


P39 = _page("HPG_Sustainability_Report_2025.pdf", 39)   # GHG table flattened
P09 = _page("HPG_Sustainability_Report_2025.pdf", 9)    # two-column highlights, glued
P86 = _page("HPG_Annual_Report_2024.pdf", 86)           # many figures, two boundaries

CASES = [
    # p.39 — the column alignment of a flattened table
    ("N01", "bảng dàn phẳng", "Năm 2025, tổng phát thải khí nhà kính phạm vi 1 và 2 toàn Tập đoàn là 23,47 triệu tCO2e.", P39, {"S"}),
    ("N02", "bảng dàn phẳng", "Năm 2025, phát thải khí nhà kính phạm vi 1 toàn Tập đoàn là 23.369.500 tCO2e.", P39, {"C"}),
    ("N03", "bảng dàn phẳng", "Năm 2025, mảng thép phát thải 23.369.500 tCO2e, chiếm 99,55% tổng phát thải khí nhà kính của Tập đoàn.", P39, {"S"}),
    ("N04", "bảng dàn phẳng", "Năm 2025, mảng nông nghiệp chiếm 0,39% tổng phát thải khí nhà kính của Tập đoàn.", P39, {"S"}),
    ("N05", "bảng dàn phẳng", "Năm 2025, mảng nông nghiệp phát thải 933.876 tCO2e.", P39, {"C"}),
    ("N06", "bảng dàn phẳng", "Năm 2025, phát thải khí nhà kính phạm vi 3 toàn Tập đoàn là 23,47 triệu tCO2e.", P39, {"N"}),
    ("N08", "bảng dàn phẳng", "Năm 2025, phát thải khí nhà kính phạm vi 2 toàn Tập đoàn là 0,93 triệu tCO2e.", P39, {"S"}),
    # p.9 — glued two-column highlight page
    ("N09", "chữ dính cột", "Năm 2025, Tập đoàn hoàn thành 90% kế hoạch kiểm kê khí nhà kính.", P09, {"N", "C"}),
    ("N10", "chữ dính cột", "Khu liên hợp Gang thép Hòa Phát Dung Quất tự chủ 90% nhu cầu điện.", P09, {"S"}),
    ("N11", "chữ dính cột", "Khu liên hợp Gang thép Hòa Phát Dung Quất tái sử dụng 90% nước.", P09, {"C"}),
    ("N12", "chữ dính cột", "Năm 2025, tỷ lệ tái chế, tái sử dụng chất thải rắn của nhóm thép và nông nghiệp đạt trên 99%.", P09, {"S"}),
    ("N13", "chữ dính cột", "Năm 2025, tỷ lệ phụ nữ ở các cấp quản lý trong toàn Tập đoàn đạt 22%.", P09, {"C"}),
    # p.86 — several figures, two organisational boundaries
    ("N14", "nhiều số, nhiều ranh giới", "Năm 2024, các nhà máy điện nhiệt dư tại hai khu liên hợp Hải Dương và Dung Quất phát 3,18 tỷ kWh điện, tăng 29% so với năm trước.", P86, {"S"}),
    ("N15", "nhiều số, nhiều ranh giới", "Năm 2024, nhà máy điện nhiệt dư tại Dung Quất phát 3,18 tỷ kWh điện.", P86, {"C"}),
    ("N16", "nhiều số, nhiều ranh giới", "Năm 2024, lượng điện phát của các nhà máy điện nhiệt dư thuộc hai khu liên hợp tăng 39% so với cùng kỳ.", P86, {"C"}),
    ("N17", "nhiều số, nhiều ranh giới", "Năm 2024, Hòa Phát tự chủ 100% lượng điện cho sản xuất thép.", P86, {"N", "C"}),
    ("N18", "nhiều số, nhiều ranh giới", "Công nghệ tuabin thu hồi năng lượng quạt gió lò cao (BPRT) giúp tiết kiệm đến 50% lượng điện tiêu thụ so với phương pháp truyền thống.", P86, {"S"}),
    ("N19", "nhiều số, nhiều ranh giới", "Năm 2024, giải pháp thu hồi nhiệt dư giúp Hòa Phát giảm 50% phát thải CO2.", P86, {"N"}),
    ("N20", "nhiều số, nhiều ranh giới", "Ngày 05/02/2025, nhà máy nhiệt điện tại Dung Quất đạt sản lượng điện lũy kế 10 tỷ kWh.", P86, {"S"}),
]
