# Thay đổi gì

<!-- Một đoạn: thay đổi này làm gì, và vì sao bây giờ. -->

## Kiểm tra bất biến kiến trúc

Mười bất biến ở [`docs/00-project/ARCHITECTURE_INVARIANTS.md`](../docs/00-project/ARCHITECTURE_INVARIANTS.md).
Tick những bất biến mà thay đổi này **chạm tới** (không phải những cái nó tuân thủ):

- [ ] 1 — Kiểm chứng tuyên bố, không phán xét doanh nghiệp
- [ ] 2 — Tuyên bố nguyên tử, giữ nguyên gốc
- [ ] 3 — Truy xuất tìm ứng viên, không quyết định sự thật
- [ ] 4 — Chỉ so cái thật sự so được
- [ ] 5 — Số học là của code
- [ ] 6 — Mục tiêu ≠ thành tích; thiếu dữ liệu ≠ thất bại
- [ ] 7 — Pháp lý kiểm applicability, không chỉ relevance
- [ ] 8 — Abstain là kết quả hợp lệ
- [ ] 9 — Verdict ≠ risk ≠ priority
- [ ] 10 — Tái lập được, người kiểm tra được

## Bảy câu phải trả lời

**Failure mode nào được xử lý?**
<!-- Mô tả lỗi thật, tốt nhất là kèm số đo. "Cải thiện chất lượng" không phải câu trả lời. -->

**Phản ví dụ nào đã thêm vào test?**
<!-- Tên test. Một thay đổi hành vi mà không có test canh là một thay đổi sẽ bị lặp lại. -->

**Khi thiếu bằng chứng thì sao?**

**Khi đầu vào không so sánh được thì sao?**

**Thay đổi này có thể làm tăng mâu thuẫn sai không?**
<!-- Nếu có: đã đo trên HPG chưa? So với benchmark/baseline_2026-09-22.json. -->

**Có quyết định nào chuyển từ luật sang mô hình không?**
<!-- Nếu có: dừng lại. Xem bất biến 5. -->

**Kết quả còn tái lập được không?**
<!-- Manifest có đủ phiên bản không? Đầu ra còn trích dẫn được về đúng trang không? -->

## Số đo

```
pytest tests -q
quantum-agent evaluate
python data/real_cases/scripts/run_case.py --all
python tools/hpg_progress.py --label <nhãn>
```

<!-- Dán bảng so với baseline. Nếu một con số xấu đi, nói ra và giải thích, đừng bỏ qua. -->
