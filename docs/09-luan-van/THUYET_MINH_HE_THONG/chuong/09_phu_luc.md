# Phụ lục A. Toàn văn mọi prompt

Các khối dưới đây được **nhập trực tiếp từ mã nguồn** khi dựng tài liệu (`tools/thuyet_minh/build_tm_llm.py` import các hằng số), nên trùng từng ký tự với văn bản mà hệ thống gửi đi. Phần trong `{…}` là chỗ code điền dữ liệu.

## A.0. Danh mục và phiên bản

{{PA_VERSIONS}}

## A.1. Harness: bộ lập kế hoạch (PLANNER, đã điền danh sách công cụ)

{{PA_PLANNER}}

## A.2. Harness: các ví dụ few-shot (FEW_SHOT)

{{PA_FEWSHOT}}

## A.3. Harness: bộ viết câu trả lời (ANSWER)

{{PA_ANSWER}}

## A.4. S5 lập trường, họ mô hình lớn (STANCE_LARGE, dùng trong stance-v3 / stance-v3f)

{{PA_STANCE_LARGE}}

## A.5. S5 phần an toàn thêm vào bản sản phẩm (STANCE_FENCE, tạo stance-v3f / stance-s1f)

{{PA_STANCE_FENCE}}

## A.6. S2 điền thuộc tính, họ mô hình lớn (ATTR_LARGE, attr-v1)

{{PA_ATTR_LARGE}}

## A.7. S2 điền thuộc tính, họ mô hình nhỏ (ATTR_SMALL, attr-s1)

{{PA_ATTR_SMALL}}

## A.8. S6 lời giải thích, họ mô hình lớn (EXPLAIN_LARGE, explain-v2)

{{PA_EXPLAIN_LARGE}}

## A.9. S6 lời giải thích, họ mô hình nhỏ (EXPLAIN_SMALL, explain-s2)

{{PA_EXPLAIN_SMALL}}

## A.10. S5 lập trường, họ mô hình nhỏ (STANCE_SMALL, stance-s1 / stance-s1f)

{{PA_STANCE_SMALL}}

## A.11. S5 lập trường, bản chung khi chưa biết mô hình (SYSTEM_PROMPT, stance-v2)

{{PA_STANCE_V2}}

## A.12. S4 đọc số liệu thành IR (PROMPT của ir_reader)

{{PA_IR}}

## A.13. Bộ định tuyến phạm vi (PLANNER_SYSTEM, dùng để huấn luyện Qwen3-0.6B, chưa dùng trong sản phẩm)

{{PA_ROUTER}}

## A.14. Hàm dựng thông điệp (cách prompt được ghép với dữ liệu)

{{PA_MESSAGE_BUILDERS}}

# Phụ lục B. Cách tái lập

Chạy từ thư mục gốc kho mã `docs/greenscan-ai/GreenScan-AI`, PowerShell hoặc Git Bash:

```bash
# 1. Chạy luồng phân tích cho hai ca, ghi thời gian từng bước (thư mục ra tuỳ chọn)
.venv/Scripts/python.exe -I tools/thuyet_minh/run_cases.py <thu_muc_vet>/clean A
.venv/Scripts/python.exe -I tools/thuyet_minh/run_cases.py <thu_muc_vet>/clean B

# 2. Ghi vết công cụ MCP, harness và bốn bước LLM (cần GROQ_API_KEY trong .env;
#    sửa run_id trong cfg_A.json / cfg_B.json theo mã phiên vừa chạy)
.venv/Scripts/python.exe -I tools/thuyet_minh/tools_trace.py <thu_muc_vet>/cfg_A.json <thu_muc_vet>/tools_A.json
.venv/Scripts/python.exe -I tools/thuyet_minh/tools_trace.py <thu_muc_vet>/cfg_B.json <thu_muc_vet>/tools_B.json

# 3. Dựng tài liệu (Markdown → hình → Word)
bash tools/thuyet_minh/make_docx.sh <thu_muc_vet>
```

Kết quả của luồng phân tích (kết luận, điểm, hàng soát) là tất định: chạy lại cho cùng phân bố kết luận và mức rủi ro (mã phiên `run_id` thì mới mỗi lần). Câu trả lời của LLM có thể khác chút ít giữa các lần dù temperature bằng 0; vết trong tài liệu là vết của lượt chạy ngày 14/11/2026, lưu trong `docs/09-luan-van/THUYET_MINH_HE_THONG/vet/`.{{COPY_TRACES}}

# Phụ lục C. Bản ghi đầy đủ của một tuyên bố (Ca A, A1)

Toàn bộ đối tượng kiểm chứng của A1 trong `result.json` (gồm tuyên bố, 5 đoạn bằng chứng với quan hệ từng đoạn, phép tính và lý do):

{{PC_VERIF_A1}}
