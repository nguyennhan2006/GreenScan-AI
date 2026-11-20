# Công tắc mô hình ngôn ngữ và bộ lọc bảng giả (16/11/2026)

Quyết định D-2026-11-16-01. Mọi số đều [ĐÃ THỰC NGHIỆM] trên laptop i7-1355U, 16 GB, không GPU, ngày 16/11/2026.

## 1. Vì sao làm

Hai điểm yếu lộ ra khi chuẩn bị demo bán kết:

1. **Không bật được mô hình lúc demo.** Các công đoạn dùng mô hình ngôn ngữ đã có từ trước (đọc cặp khó, điền thuộc tính, đọc số liệu, viết lời giải thích), nhưng chỉ bật bằng biến môi trường rồi khởi động lại. Giám khảo không nhìn thấy mô hình nào chạy.
2. **Mục đứng đầu hàng đợi Hòa Phát là chữ ghép sai:** “Hoàn thành kiểm kê khí nhà kính theo tiêu 90%”. Con số 90% thuộc ô bên cạnh (“Tự chủ 90% nhu cầu điện”).

## 2. Công tắc mô hình (`model-mode-v1`)

Mã: `src/quantum_gw/model_mode.py`, `POST /v1/runtime/model-mode`, `POST /v1/runtime/model-test`, thành phần giao diện `frontend/src/components/ModelModeSwitch.jsx` (trang Cài đặt và trang Tải tài liệu).

| Chế độ | Mô hình | Tài liệu rời máy? | Dùng khi |
|---|---|---|---|
| Chỉ luật và phép tính | không | Không | Mặc định |
| Mô hình chạy trên máy này | `qwen3:4b-instruct-2507-q4_K_M` qua Ollama (hoặc máy chủ mô hình cục bộ ghi trong `.env`) | Không | Tài liệu nội bộ, tài liệu mật |
| Mô hình trên đám mây | `openai/gpt-oss-120b` qua Groq (hoặc FPT nếu có khoá) | Có, đoạn trích của cặp khó | Chỉ tài liệu đã công bố |

Công tắc ghi các biến mà mỗi lượt chạy vốn đã đọc (`QUANTUM_LLM_STANCE`, `QUANTUM_VERIFY`, `QUANTUM_ASSIST_EXPLAIN`, `QUANTUM_ASSIST_ATTRIBUTES`, hồ sơ và nhà cung cấp), nên không cần khởi động lại. Chế độ “trên máy” đặt hồ sơ `offline`: bộ định tuyến chỉ thử nhà cung cấp cục bộ, kể cả khi máy có khoá đám mây (có kiểm thử).

**Điều không đổi:** `llm_stance_decisive = False`. Mô hình không tự ra “ủng hộ” hay “mâu thuẫn”. Nó đọc thêm, viết lời giải thích; chỗ nó đọc khác luật thì tuyên bố được gắn cờ cho người xác nhận. Mức trung gian có thể đổi: ở Ca mẫu A, câu “doanh nghiệp xanh hàng đầu” là “không có căn cứ” khi chỉ dùng luật và “ủng hộ một phần, cần người xác nhận” khi có mô hình.

Mỗi phiên ghi `model_stages` vào manifest (chế độ và mô hình của từng công đoạn). Hàng đợi hiện một dòng dưới tên phiên: “Phiên này chỉ dùng luật và phép tính” hoặc “Phiên này có mô hình cùng đọc: …”.

### Số đo

| Việc | Trên máy (Qwen3-4B, CPU) | Đám mây (gpt-oss-120b) |
|---|---|---|
| Nút “Thử mô hình” (một cặp ngắn) | 32,1 giây | 1,1 giây |
| Ca mẫu A (3 tệp, 5 tuyên bố), lần đầu | 940 giây, 23 lượt gọi | 130 giây |
| Ca mẫu A, chạy lại từ bộ nhớ đệm | 1,0 giây | — |
| Hòa Phát (171 tuyên bố) | không chạy (ước tính nhiều giờ) | chưa xong: gói miễn phí giới hạn tốc độ, dừng ở 34/171 tuyên bố sau hơn một giờ |

Lần gọi lỗi: trên máy 1/8 cặp lập trường quá hạn 180 giây (hạn của chế độ trên máy nay là 600 giây); đám mây 3/8 cặp và 1/3 lời giải thích lỗi ở lượt đầu. Cặp lỗi giữ kết quả của luật.

**Cách dùng khi demo:** phiên Ca mẫu A có mô hình đã chạy sẵn, nên bấm phân tích lại sẽ phát lại từ bộ nhớ đệm trong 1 giây. Muốn cho thấy mô hình đang chạy thật thì bấm “Thử mô hình”.

### Sửa kèm theo

- Lời giải thích từng ghi “mở trang None” với tệp không có số trang, và lọt chữ “values”. Đã sửa ở `assist/prompts.py`.
- Thẻ chế độ đám mây hiện tên mô hình thật thay cho tên nhà cung cấp.

## 3. Bộ lọc bảng giả (`table-shape-v1`)

Nguyên nhân: pdfplumber trả về mọi khung chữ nhật có kẻ viền như một “bảng”. Trên báo cáo có thiết kế, phần lớn là thanh bên, băng tiêu đề, hoặc cả một trang infographic trong một ô, đọc từng dòng xuyên qua các cột.

Luật (`parsers/documents.py::is_data_table`): giữ một bảng khi có ít nhất hai dòng có từ hai ô có chữ, và không ô nào dài quá 12 dòng. Tắt bằng `QUANTUM_TABLE_SHAPE_FILTER=off`.

| Hòa Phát (BCPTBV 2025 + BCTN 2024) | Trước | Sau |
|---|---|---|
| “Bảng” pdfplumber trả về, BCPTBV / BCTN | 122 / 150 | giữ 1 / 2 |
| Tuyên bố | 179 | 171 |
| Tuyên bố bị bớt / thêm | — | 8 / 0 |
| Hàng đợi | 10 trên 195 | 7 trên 186 |
| Mục đầu hàng đợi | “…theo tiêu 90%” (ghép sai) | Câu trang 7 “tự chủ điện năng rất cao” |
| Phép cộng lại bảng khí nhà kính trang 39 | khớp | khớp |

Cả 8 câu bị bớt đều là chữ ghép sai (đọc tay). Nội dung thật của các khung ấy vẫn có trong phần chữ đọc theo khối.

Chưa đo lại: GS-Claims (độ chính xác bộ trích 0,71 là số trước bộ lọc) và `evaluate-real`. GS-Bench, GS-Mutation và phép phát lại GS-Eval v2 dùng cặp đã lưu nên không đổi.

## 4. Kiểm thử

`tests/test_model_mode.py` (9 ca): ba chế độ, chế độ trên máy không rơi sang khoá đám mây, mô hình không tự quyết, API đổi chế độ, bảng giả so với bảng thật. Tổng 768 kiểm thử qua.

## 5. Còn lại

- Mô hình 4B trên CPU quá chậm cho một báo cáo dài; cần GPU hoặc mô hình nhỏ hơn đã đo chất lượng.
- Tiêu đề dính vào câu vẫn lọt vào hàng đợi (mục #3 của Hòa Phát).
- Chế độ không được lưu qua lần khởi động lại: mở lên là chế độ ghi trong `.env`.
