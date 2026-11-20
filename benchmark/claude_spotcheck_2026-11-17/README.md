# Claude đọc lại ba bộ tài liệu (17/11/2026)

Nhãn của mô hình `claude-fable-5-2`, đọc một lượt, **chưa có người rà**. Không dùng làm nhãn chuẩn khi chưa rà.

- `labels.jsonl`: 67 câu hệ thống lấy ra (5 Minh Họa, 35 Techcombank, 27 Hòa Phát), mỗi dòng có kết quả của hệ thống và loại do Claude gán (`claude_category`: REAL, VAGUE, CONTEXT, METHOD, LAYOUT, SOCIAL) kèm ghi chú.
- `missed.jsonl`: 14 câu quan trọng có trong tài liệu mà hệ thống không lấy.
- Bản kết quả: `docs/04-data-ai/KIEM_CHUNG_BANG_CLAUDE_2026-11-17.md`.
- Phiên của hệ thống: Hòa Phát `4431e073ee1241dd` (kho demo); Minh Họa và Techcombank chạy lại bằng chế độ chỉ luật trên mã ngày 17/11 (bản chốt `vong2_2026-11-17c`).
- Mẫu Hòa Phát: 7 mục hàng đợi, 5 mẫu ngẫu nhiên của hệ thống, 15 câu rút ngẫu nhiên ngoài hai nhóm đó (`random.seed(20261117)` trên danh sách mã đã sắp xếp).
