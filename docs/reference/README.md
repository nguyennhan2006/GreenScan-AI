# docs/reference — tài liệu tham chiếu lịch sử

| File | Trạng thái | Ghi chú |
| --- | --- | --- |
| `AI-QUANTUM_AGENT_CRITERIA_v1.docx` | **SUPERSEDED — không dùng cho slide, brief, UI** (DECISIONS_LOG D-2026-09-18-05) | Chứa công thức "mức độ trung thực ESG", nhãn "Rất trung thực", ngưỡng ngành tùy ý (≥20% năng lượng tái tạo = 0 điểm trừ; "chi phí môi trường tiềm ẩn = 10% dịch vụ mua ngoài"). Các công thức này chấm điểm doanh nghiệp, xung đột trực tiếp nguyên tắc P4 (đơn vị phân tích là claim; hệ thống không kết luận doanh nghiệp). Thay thế bởi `configs/scoring_v1.yaml` (`risk-rubric-v2`) và `docs/01-domain-audit/MANUAL_SCORING_RUBRIC.md`. Giữ lại chỉ để truy vết lịch sử. |
| `../GreenScan_AI_Research_Source_Pack_2026-08-13/` | Tham khảo | Bộ nguồn nghiên cứu (paper RAG, TREX, …) dùng cho phần trả lời phản biện; xem `docs/07-presentation/QA_DRILL.md`. |
| `GreenScan_AI_Ho_so_Vong1_BAN_HOAN_CHINH_v2.docx` — Hồ sơ Vòng 1 | Tham khảo, đã nộp (chuyển từ gốc repo 2026-09-22) | Mọi số trong đó là **cam kết/mục tiêu**, không phải kết quả đã đo; slide phải tách Achieved / Target / Hypothesis (DECISIONS_LOG D-2026-09-18-08). |

Trước presentation freeze (17/10), kiểm tra: `grep -rn "trung thực\|điểm trừ\|honesty" docs/07-presentation frontend/src configs` phải không có kết quả liên quan tới chấm điểm doanh nghiệp.
