# P08 · Rủi ro và hàng đợi ưu tiên

*Nhãn:* **[ĐÃ THỰC NGHIỆM]** số đo của đội · **[KIẾN THỨC NỀN]** thiết kế đã cài, chưa đo · **[NGOÀI]** trích theo file nguồn · **[GIẢ THUYẾT]** dự đoán đăng ký trước. Đường dẫn tính từ thư mục gốc repo.

## 1. Vấn đề giải quyết

Cho người soát biết nên mở tuyên bố nào trước (hàng đợi), và mức độ cần chú ý theo rubric (rủi ro). Đây là hai việc khác với verdict đúng hay sai **[KIẾN THỨC NỀN]** (`docs/00-project/ARCHITECTURE_INVARIANTS.md`, bất biến 9).

## 2. Lỗi hoặc rủi ro đã đo được

- Trước rà soát 06/10, hàng đợi có 22/213 mục; trong đó 10/22 là câu giải thích công nghệ, câu nối ý hoặc chữ dính cột. Sau rà soát, 9/172 mục và cả 9 là câu doanh nghiệp tự nói về mình **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`).
- Một văn bản pháp lý bị trích sai: NĐ 83/2026 (chỉ sửa phần ô-dôn) đi kèm 55 tuyên bố phát thải. Sau sửa còn 0 **[ĐÃ THỰC NGHIỆM]** (cùng file).
- Một lượt HPG: 65 HIGH và 1 CRITICAL trên doanh nghiệp đối chứng, được đọc như cáo buộc **[ĐÃ THỰC NGHIỆM]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-22-03).

## 3. Thiết kế hiện tại, file code, cấu hình

- Điểm rủi ro cấp tuyên bố theo thang: 0–20 LOW, 21–40 MODERATE, 41–60 HIGH, 61–80 VERY_HIGH, 81–100 CRITICAL **[KIẾN THỨC NỀN]** (`docs/04-data-ai/RISK_SCORING_SPEC.md`, mục 4).
- Điểm cấp doanh nghiệp đề xuất: 35 % tỷ lệ tuyên bố mâu thuẫn, 20 % tuyên bố tài chính xanh rủi ro cao, 15 % tuyên bố pháp lý, 15 % thiếu minh bạch, 10 % mật độ tuyên bố mơ hồ, 5 % yếu kém bảo đảm **[KIẾN THỨC NỀN]** (cùng file, mục 7.2).
- Hàng đợi `priority-v1.1`: trọng yếu 40, nghĩa vụ 25, khoảng trống bằng chứng 25, bất thường 10 (chưa tính) **[KIẾN THỨC NỀN]** (`docs/03-architecture/HE_THONG_HIEN_TAI_2026-10-10.md`, mục 2, bước 8).

## 4. Vì sao chọn, phương án đã bỏ

- Tách verdict, risk và priority. Không dùng điểm 72/100 thay cho đúng hay sai, không suy ngược verdict từ vị trí hàng đợi **[KIẾN THỨC NỀN]** (`docs/00-project/ARCHITECTURE_INVARIANTS.md`, bất biến 9).
- Bỏ "mức độ trung thực ESG" và các ngưỡng ngành tùy ý; điểm rủi ro 0–100 là rubric sàng lọc có trần thành phần, không phải xác suất greenwashing **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-18-05).
- Bỏ phán xét cấp doanh nghiệp: không có trường kết luận cấp công ty **[KIẾN THỨC NỀN]** (`docs/00-project/ARCHITECTURE_INVARIANTS.md`, bất biến 1).

## 5. Số đo có n

- Hàng đợi: 213 → 172 mục; số liệu công bố đọc được 57 → 16 **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`).
- Mức HIGH và CRITICAL trên doanh nghiệp đối chứng: 8 HIGH và 2 CRITICAL khi bật mô hình không chốt chặn; 0 khi tắt mô hình và khi bật có chốt chặn **[ĐÃ THỰC NGHIỆM]** (`benchmark/llm_stance_ab_2026-09-28.md`).
- Trên 156 tuyên bố, kết quả kiểm chứng và mức rủi ro không đổi sau rà soát hàng đợi (chỉ thay thứ tự) **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`).

## 6. Giới hạn và yếu tố gây nhiễu

- Thứ tự hàng đợi chưa được ai kiểm. Đo độ chính xác thứ tự cần nhãn của Quỳnh **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`, mục "Còn lại").
- Trọng số 40/25/25/10 chưa calibrate; công thức doanh nghiệp là "đề xuất" cho MVP **[KIẾN THỨC NỀN]** (`docs/04-data-ai/RISK_SCORING_SPEC.md`, mục 7.2).
- Trần MEDIUM cho đến khi calibration trên gold (B6) **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-22-03).

## 7. Lỗi đã gặp và cách gỡ

- Gộp dấu "cộng" và "công"; nhãn vượt ranh giới câu; đơn vị cột bên cạnh. Đã sửa **[ĐÃ THỰC NGHIỆM]** (`benchmark/queue_quality_2026-10-06.md`, nguyên nhân 1–3).
- Câu không nêu chủ thể bị ưu tiên sai: nay nhân trọng yếu ×0,75; chữ dính cột ×0,5. Chỉ đổi thứ tự **[ĐÃ THỰC NGHIỆM]** (cùng file, nguyên nhân 5).

## 8. Trạng thái năng lực

- Priority-v1.1: **IMPLEMENTED–NOT VALIDATED**.
- Risk: **IMPLEMENTED–NOT VALIDATED**; là rubric sàng lọc, chưa đo trên gold **[KIẾN THỨC NỀN]** (`docs/04-data-ai/RISK_SCORING_SPEC.md`).

## 9. Hướng phát triển và thí nghiệm kế tiếp

- Đo độ chính xác thứ tự hàng đợi bằng nhãn của Quỳnh **[KIẾN THỨC NỀN]** (`benchmark/queue_quality_2026-10-06.md`).
- Calibrate severity trên gold (B6); cho phép CRITICAL chỉ khi kèm vi phạm pháp lý hoặc số học có `policy_id` **[KIẾN THỨC NỀN]** (`docs/00-project/DECISIONS_LOG.md`, D-2026-09-22-03).
- Câu hỏi mở: thứ tự hiện tại có đúng không. Chưa có dự đoán được đăng ký cho hàng đợi **[GIẢ THUYẾT]** (`benchmark/queue_quality_2026-10-06.md`, mục "Còn lại").

## 10. Hình nên vẽ và file dữ liệu

- Bảng trước và sau rà soát hàng đợi; cột mức rủi ro theo mức.
- Dữ liệu: `benchmark/queue_quality_2026-10-06.md`; `docs/04-data-ai/RISK_SCORING_SPEC.md` mục 4 và 7.
