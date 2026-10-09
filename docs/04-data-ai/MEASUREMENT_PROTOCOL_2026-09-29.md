# Quy trình đo — đăng ký trước ngày có gold

**Đăng ký:** 29/09/2026, trước khi có nhãn gold nào. **Ngưỡng quyết định:** [`configs/measurement_decisions.yaml`](../../configs/measurement_decisions.yaml), công cụ đọc thẳng từ file đó. Đổi ngưỡng sau khi thấy số là vô hiệu phép đo: muốn đổi thì thêm phiên bản mới và ghi lý do vào `DECISIONS_LOG`.

## 1. Đo cái gì, trả lời câu hỏi nào

| Phần | So sánh | Chỉ số | Trả lời |
| --- | --- | --- | --- |
| **Truy xuất** | lite · BGE-M3 · BGE-M3 + reranker, tìm trên **toàn bộ thư viện** của doanh nghiệp (chỉ trang công bố không muộn hơn tuyên bố, trừ chính trang tuyên bố) | Recall@1/5/10/30, MRR, nDCG@10, **verdict đúng khi chạy nối tiếp**, giây/tuyên bố | RQ4 (bật BGE-M3?), RQ5 (được nói reranker giúp?) |
| **Quan hệ từng cặp** | luật · mô hình, trên **mọi đoạn người đã gán nhãn** | Đúng/sai theo cặp, precision SUPPORTS/CONTRADICTS, theo từng cách quyết (numeric, cue, direction, similarity, llm), **mô hình vs luật trên cùng những cặp mô hình quyết** | Giữ mô hình? Tháo chốt chặn cho quan hệ nào? |
| **Kết luận** | luật · mô hình có chốt · mô hình tự quyết, với **bằng chứng người đã chọn** | Accuracy, macro-F1, **mâu thuẫn sai** (báo riêng), abstain | Verifier sai ở đâu khi truy xuất đã đúng |
| **Hàng đợi** | — | Tỷ lệ câu người gọi là tuyên bố (gold `is_claim` + 22 mục HPG) | Cần bộ lọc tuyên bố bằng LLM (việc D)? |
| **Thời gian** | làm tay · GreenScan (mỗi câu làm một lần) | Phút/tuyên bố, số đoạn đúng | RQ10 — con số bán được |
| **Cổng** | Quỳnh vs Thảo trên lô 1 | κ trên `is_claim`, `verdict`, từng thuộc tính, quan hệ bằng chứng | Nhãn có đáng tin để đo không |

Mọi con số có **n** và **khoảng tin cậy bootstrap 95 %**. Hai phương án đo trên cùng tuyên bố luôn so **theo cặp** (hiệu từng tuyên bố, rồi bootstrap), không so hai trung bình rời.

## 2. Luật quyết định (tóm tắt — bản đầy đủ trong YAML)

| Quyết định | Điều kiện |
| --- | --- |
| Không nói số nào với hội đồng | gold có verdict < 60 **hoặc** κ < 0,70 (D-2026-09-22-05, RQ7) |
| Bật BGE-M3 mặc định | ΔRecall@5 ≥ +10 điểm **và** thời gian ≤ 2× lite (RQ4) |
| Nói "reranker giúp" | Δ verdict đúng (nối tiếp) có cận dưới KTC > 0 (RQ5) |
| Giữ mô hình xét quan hệ | trên cặp mô hình quyết, mô hình đúng hơn luật, cận dưới KTC > 0 |
| Cho mô hình tự quyết SUPPORTED | precision ≥ 0,80, cận dưới ≥ 0,65, n ≥ 20 |
| Cho mô hình tự quyết CONTRADICTED | precision ≥ 0,90, cận dưới ≥ 0,75, n ≥ 10, **và** tỷ lệ mâu thuẫn sai không tăng |
| Làm bộ lọc tuyên bố (việc D) | tỷ lệ câu thật trong hàng đợi < 70 % |

## 3. Sai lệch đã biết — ghi trước để không bị bất ngờ

- **Thiên lệch pooling (truy xuất):** nhãn chỉ có cho các trang bộ truy xuất 08/2026 đề xuất. Bộ mới tìm được trang đúng khác sẽ không được tính → mức tăng đo được là **cận dưới**; mức giảm có thể một phần do thiên lệch này.
- **Tuyên bố lấy từ kho cũ (VN30), không phải DN phát thải cao** của kế hoạch v2. Kết quả nói về các báo cáo này, không suy rộng cho ngành thép/xi măng.
- **Bài đo thời gian so hai bộ tuyên bố khác nhau** (mỗi câu làm một lần để tránh hiệu ứng nhớ); n = 10 mỗi nhóm.
- **Mô hình qua API:** kết quả phụ thuộc phiên bản model FPT tại thời điểm gọi; bộ nhớ đệm ghi `prompt_version` + model, mọi lần đo lại trên cùng cặp dùng đúng câu trả lời cũ.

## 4. Đã chuẩn bị (29/09)

| Việc | Kết quả |
| --- | --- |
| Thư viện của 11 DN trong các lô gold | 15.409 trang, **14.708 vector** `Vietnamese_Embedding` đã lưu (`.quantum/emb_cache`, qua FPT, 77,7 trang/s) |
| Câu trả lời mô hình cho các cặp ứng viên | 259 cặp tới mô hình, **249/249** đã lưu (`.quantum/llm_cache`), 0 lỗi |
| BGE-M3 và reranker chạy local | cài được (`torch 2.14`, CPU). Đo tốc độ: **0,49 trang/s** và **0,28 cặp/s** → vector BGE-M3 cho thư viện ≈ 7,7 giờ; reranker local bị loại khỏi phép đo. Chỉ chạy `warm --local-bge` khi có một đêm để máy chạy |
| Chạy thử toàn bộ trên nhãn **giả** (lô 1) | thông suốt, 321 s; báo cáo tự bật cảnh báo "chỉ dùng nội bộ" khi gold < 60 hoặc κ < 0,70 |

Mô hình tìm kiếm dense đo qua FPT là `Vietnamese_Embedding` — theo model card là BAAI/bge-m3 tinh chỉnh cho tiếng Việt (1.024 chiều, 2.048 token); reranker là đúng `bge-reranker-v2-m3`. Đây là chỗ lệch có chủ đích so với kế hoạch "BGE-M3 local": trên máy không GPU, local không chạy nổi trong thời gian cho phép.

## 5. Ngày gold về — chạy đúng thứ tự này

```bash
# 0. (đã chạy trước) tính sẵn vector và câu trả lời mô hình cho các câu gold
python tools/measure_all.py warm

# 1. bỏ mọi file Quỳnh/Thảo gửi về vào một thư mục, rồi
python tools/labeling_pack.py import-all <thư_mục>
#    -> gold lô 2/3, bản riêng lô 1 của từng người, κ + bảng chỗ khác nhau, hàng đợi HPG, bài đo thời gian

# 2. sau buổi trọng tài lô 1 (Quỳnh gửi lại file đã thống nhất)
python tools/labeling_pack.py import <file_lo1_da_thong_nhat>.xlsx --final

# 3. đo mọi thứ, đối chiếu luật đã đăng ký
python tools/measure_all.py
#    -> benchmark/measurement_<ngày>.md / .json
```

Bộ test không bao giờ gọi mô hình thật (`tests/conftest.py`); `measure_all` gọi mô hình theo `.env` và dùng bộ nhớ đệm.
