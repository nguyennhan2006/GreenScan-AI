# GROQ-PROBE · Model và cấu hình Groq nào dùng được cho việc đọc IR (31/10/2026)

**Vấn đề.**
- Khoá FPT bị 401, nên người dùng tạo khoá Groq miễn phí.
- Groq đổi danh sách model không báo trước: Qwen3-32B đã bị gỡ.
- Mỗi model nhận một bộ tham số khác nhau.
- Người dùng yêu cầu thử nhiều cấu hình trước khi dùng.

**Cách làm** (`probe.py`):
- Lấy danh sách model qua `GET /models`.
- Mỗi model chat thử 9 cấu hình:
  - mặc định;
  - `json_object`;
  - `json_schema`;
  - `reasoning_effort` none / low / high;
  - `reasoning_format` hidden;
  - hai tổ hợp low/none + `json_object`.
- Đầu vào là 12 câu GS-Bench B-b có IR gold: 9 tuyên bố, mỗi họ nhiễu một câu, và 3 câu bằng chứng; đều lấy từ báo cáo công khai.
- Chấm mỗi lời gọi:
  - HTTP OK;
  - JSON đọc được;
  - tìm đúng số liệu gold;
  - khớp các trường chỉ số / loại giá trị / thực hiện–mục tiêu / kỳ / phạm vi.
- Ghi thêm độ trễ và số token ra.
- Đầu ra: `out/calls.jsonl`, `out/summary.json`, `out/models.json`.

**Kết quả** [ĐÃ THỰC NGHIỆM, n = 12 câu cho mỗi ô, nên chỉ đủ để sàng lọc]:

| Model | Cấu hình tốt nhất | Tìm đúng | Trường khớp | Trung vị độ trễ | Token ra |
|---|---|---|---|---|---|
| `openai/gpt-oss-120b` | `reasoning_effort: low` + `json_object` | 12/12 | 1,00 | 1,0 s | 190 |
| `openai/gpt-oss-120b` | `json_object` | 12/12 | 1,00 | 1,9 s | 584 |
| `qwen/qwen3.8-27b` | `reasoning_effort: low` | 12/12 | 1,00 | 2,2 s | 586 |
| `openai/gpt-oss-20b` | mặc định / `format_hidden` | 11/12 | 0,92 | 1,4–1,6 s | 650–690 |

**Thông số API:**
- gpt-oss **không nhận** `reasoning_effort: none` (HTTP 400; chỉ nhận low, medium, high).
- `effort_high` làm hỏng JSON: gpt-oss-20b chỉ 8/12, 120b còn 10/12.
- qwen3.8-27b nhận mọi tham số, nhưng chạm hạn mức miễn phí giữa chừng: 4 cấu hình chỉ có 1–7 lời gọi.
- `allam-2-7b` (model tiếng Ả Rập) không đọc được số liệu: loại.

**Chọn cho thí nghiệm** (chỉ dùng cho báo cáo công khai):
```
GROQ_MODEL=openai/gpt-oss-120b
GROQ_EXTRA_BODY={"reasoning_effort": "low", "response_format": {"type": "json_object"}}
```

**Giới hạn.**
- 12 câu là quá ít để xếp hạng các model; con số chỉ dùng để chọn cấu hình chạy được.
- Khi có lượt lớn hơn, chấm lại trên toàn GS-Bench như AG-1.
- Gói miễn phí có thể lưu dữ liệu, nên không đưa tài liệu người dùng qua Groq.
