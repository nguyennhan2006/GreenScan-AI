"""Constructed-truth cases: claim, evidence, acceptable labels, failure family.

Labels: S = evidence confirms the claim, C = evidence about the same metric,
period, scope, boundary and value type conflicts with it, N = evidence does not
allow confirming or refuting (different metric/period/scope/boundary/value
type, target vs actual, or unrelated). The truth follows from the semantics of
GHG / disclosure reporting, not from GreenScan's rules; where an auditor could
reasonably accept two labels, both are listed.
"""

GHG_TABLE = (
    "Bảng 5.2 — Phát thải khí nhà kính năm 2025: Phạm vi 1: 22.540.603 tCO2e; "
    "Phạm vi 2: 933.876 tCO2e; Tổng phạm vi 1 và 2: 23.474.480 tCO2e."
)

CASES = [
    # F1 match after rounding
    ("F01", "khớp sau làm tròn", "Năm 2025, tổng phát thải khí nhà kính phạm vi 1 và 2 của Công ty là khoảng 23,5 triệu tCO2e.", GHG_TABLE, {"S"}),
    ("F02", "khớp sau làm tròn", "Phát thải khí nhà kính phạm vi 2 của Công ty năm 2025 là 933.876 tCO2e.", GHG_TABLE, {"S"}),
    # F2 one number differs
    ("F03", "lệch một con số", "Năm 2025, tổng phát thải khí nhà kính phạm vi 1 và 2 của Công ty là 21,4 triệu tCO2e.", GHG_TABLE, {"C"}),
    ("F04", "lệch một con số", "Phát thải khí nhà kính phạm vi 2 của Công ty năm 2025 là 833.876 tCO2e.", GHG_TABLE, {"C"}),
    ("F05", "lệch một con số", "Năm 2024, nhà máy điện nhiệt dư đáp ứng 90% nhu cầu điện của khu liên hợp.", "Năm 2024, nhà máy điện nhiệt dư đáp ứng 80% nhu cầu điện của khu liên hợp.", {"C"}),
    # F3 recompute a percentage change
    ("F06", "tính lại % thay đổi", "Năm 2025, phát thải khí nhà kính phạm vi 1 của Công ty giảm 20% so với năm 2020.", "Phát thải khí nhà kính phạm vi 1 của Công ty: năm 2020 là 1.000.000 tCO2e; năm 2025 là 800.000 tCO2e.", {"S"}),
    ("F07", "tính lại % thay đổi", "Năm 2025, phát thải khí nhà kính phạm vi 1 của Công ty giảm 20% so với năm 2020.", "Phát thải khí nhà kính phạm vi 1 của Công ty: năm 2020 là 1.000.000 tCO2e; năm 2025 là 850.000 tCO2e.", {"C"}),
    ("F08", "tính lại % thay đổi", "Năm 2025, phát thải khí nhà kính phạm vi 1 của Công ty giảm 20% so với năm 2020.", "Phát thải khí nhà kính phạm vi 1 của Công ty: năm 2020 là 1.000.000 tCO2e; năm 2025 là 1.050.000 tCO2e.", {"C"}),
    # F4 different basis (share / change / intensity / absolute)
    ("F09", "khác cơ sở đo", "Hoạt động sản xuất gang thép chiếm hơn 99% tổng phát thải khí nhà kính của Tập đoàn.", "Năm 2025, sản lượng thép thô của Tập đoàn tăng 24% so với năm 2024.", {"N"}),
    ("F10", "khác cơ sở đo", "Cường độ phát thải khí nhà kính năm 2025 của Công ty là 1,9 tCO2e/tấn thép.", GHG_TABLE, {"N"}),
    ("F11", "khác cơ sở đo", "Tổng phát thải khí nhà kính của Công ty năm 2025 giảm 5% so với năm 2024.", "Cường độ phát thải khí nhà kính (tCO2e/tấn thép) của Công ty năm 2025 giảm 5% so với năm 2024.", {"N"}),
    # F5 scope mismatch
    ("F12", "khác phạm vi phát thải", "Năm 2025, phát thải khí nhà kính phạm vi 1 của Công ty giảm 30% so với năm 2020.", "Năm 2025, phát thải khí nhà kính phạm vi 1, 2 và 3 của Công ty giảm 8% so với năm 2020.", {"N"}),
    ("F13", "khác phạm vi phát thải", "Phát thải khí nhà kính phạm vi 1 và 2 của Công ty năm 2025 là 23,5 triệu tCO2e.", "Phát thải khí nhà kính phạm vi 1 của Công ty năm 2025 là 22.540.603 tCO2e.", {"N"}),
    # F6 period mismatch
    ("F14", "khác kỳ", "Năm 2025, phát thải khí nhà kính phạm vi 1 của Công ty là 22,5 triệu tCO2e.", "Năm 2024, phát thải khí nhà kính phạm vi 1 của Công ty là 22,5 triệu tCO2e.", {"N"}),
    ("F15", "khác kỳ", "Năm 2025, lượng nước sử dụng của Công ty giảm 12% so với năm 2024.", "Năm 2023, lượng nước sử dụng của Công ty giảm 12% so với năm 2022.", {"N"}),
    # F7 target vs actual
    ("F16", "mục tiêu hay thực hiện", "Công ty đã giảm 30% phát thải khí nhà kính phạm vi 1 và 2 so với năm 2020.", "Mục tiêu đến năm 2030: giảm 30% phát thải khí nhà kính phạm vi 1 và 2 so với năm 2020.", {"N"}),
    ("F17", "mục tiêu hay thực hiện", "Công ty đặt mục tiêu giảm 30% phát thải khí nhà kính phạm vi 1 và 2 vào năm 2030 so với năm 2020.", "Mục tiêu đến năm 2030: giảm 30% phát thải khí nhà kính phạm vi 1 và 2 so với năm 2020.", {"S"}),
    ("F18", "mục tiêu hay thực hiện", "Năm 2025, tỷ lệ phế liệu tái chế đưa vào sản xuất của Công ty đạt 30%.", "Năm 2025, tỷ lệ phế liệu tái chế đưa vào sản xuất của Công ty đạt 18%, thấp hơn mục tiêu 30%.", {"C"}),
    # F8 organisational boundary
    ("F19", "khác ranh giới tổ chức", "Phát thải khí nhà kính phạm vi 1 và 2 hợp nhất của Tập đoàn năm 2025 là 23,5 triệu tCO2e.", "Phát thải khí nhà kính phạm vi 1 và 2 của Khu liên hợp Dung Quất năm 2025 là 12.300.000 tCO2e.", {"N"}),
    ("F20", "khác ranh giới tổ chức", "Phát thải khí nhà kính phạm vi 1 và 2 của công ty mẹ năm 2025 là 1,2 triệu tCO2e.", "Phát thải khí nhà kính phạm vi 1 và 2 hợp nhất toàn Tập đoàn năm 2025 là 23,47 triệu tCO2e.", {"N"}),
    # F9 unit / multiplier
    ("F21", "khác đơn vị / hệ số", "Năm 2025, Công ty tiêu thụ 5,6 triệu MWh điện.", "Năm 2025, Công ty tiêu thụ 5,6 triệu tấn than.", {"N"}),
    ("F22", "khác đơn vị / hệ số", "Năm 2025, Công ty sử dụng 15 triệu m3 nước.", "Lượng nước sử dụng của Công ty năm 2025: 15.000 m3.", {"C"}),
    ("F23", "khác đơn vị / hệ số", "Năm 2025, Công ty sử dụng 15 triệu m3 nước.", "Lượng nước sử dụng của Công ty năm 2025: 15.000.000 m3.", {"S"}),
    # F10 precision of the published figure
    ("F24", "dung sai theo độ chính xác", "Tỷ lệ năng lượng tái tạo trong tổng năng lượng tiêu thụ của Công ty năm 2025 đạt 12%.", "Tỷ lệ năng lượng tái tạo trong tổng năng lượng tiêu thụ của Công ty năm 2025: 12,4%.", {"S"}),
    ("F25", "dung sai theo độ chính xác", "Tỷ lệ năng lượng tái tạo trong tổng năng lượng tiêu thụ của Công ty năm 2025 đạt 12,0%.", "Tỷ lệ năng lượng tái tạo trong tổng năng lượng tiêu thụ của Công ty năm 2025: 12,4%.", {"C"}),
    # F11 cross-foot (requires adding the components)
    ("F26", "cộng lại bảng", "Tổng phát thải khí nhà kính phạm vi 1 và 2 của Công ty năm 2025 là 23.474.480 tCO2e.", "Phát thải khí nhà kính năm 2025 của Công ty — Phạm vi 1: 22.540.603 tCO2e; Phạm vi 2: 933.876 tCO2e.", {"S"}),
    ("F27", "cộng lại bảng", "Tổng phát thải khí nhà kính phạm vi 1 và 2 của Công ty năm 2025 là 24.474.480 tCO2e.", "Phát thải khí nhà kính năm 2025 của Công ty — Phạm vi 1: 22.540.603 tCO2e; Phạm vi 2: 933.876 tCO2e.", {"C"}),
    # F12 negation / cue traps — anything but C is acceptable
    ("F28", "bẫy từ phủ định", "Năm 2024, Tập đoàn giảm phát thải khí nhà kính tại các nhà máy thép.", "Năm 2024, nhà máy thép áp dụng công nghệ thiêu kết mới giúp giảm phát thải khí nhà kính.", {"S", "N"}),
    ("F29", "bẫy từ phủ định", "Năm 2024, Tập đoàn giảm phát thải khí nhà kính tại các nhà máy thép.", "Năm 2024 không có sự cố môi trường nào tại các nhà máy thép; phát thải khí nhà kính giảm so với năm trước.", {"S", "N"}),
    # F13 nothing relevant / insufficient
    ("F30", "không có bằng chứng liên quan", "Năm 2025, 100% nước thải của Công ty được xử lý đạt quy chuẩn trước khi xả ra môi trường.", "Năm 2025, Công ty tổ chức 12 khoá đào tạo an toàn lao động cho 3.000 lượt người lao động.", {"N"}),
    ("F31", "không có bằng chứng liên quan", "Công ty đã đạt trung hòa carbon trong năm 2025.", "Năm 2025, Công ty trồng 50.000 cây xanh tại các khu công nghiệp.", {"N"}),
    # same number, different metric (the false SUPPORTED seen on a real report)
    ("F32", "cùng số, khác chỉ số", "Năm 2025, Công ty tự chủ 90% nhu cầu điện cho sản xuất thép.", "Năm 2025, Công ty hoàn thành 90% kế hoạch kiểm kê khí nhà kính.", {"N"}),
]
