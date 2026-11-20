# Chương 5. Bốn bước có mô hình ngôn ngữ hỗ trợ

Chương này trả lời câu hỏi: mô hình ngôn ngữ (LLM) được phép làm gì trong luồng phân tích, nó nhận đúng prompt nào, trả lời gì, và bộ kiểm bằng code làm gì với câu trả lời đó. Trong sản phẩm, **cả bốn bước đều tắt ở chế độ mặc định "chỉ luật"** (manifest của hai phiên có `prompt_version` rỗng). Chúng chạy khi người dùng bật công tắc mô hình sang "mô hình trên máy" hoặc "mô hình trên đám mây" (mục 2.3). Để thuyết minh, tác giả chạy riêng từng bước trên bốn tuyên bố được theo dõi, gửi tới Groq `openai/gpt-oss-120b` (temperature 0, reasoning_effort low) **đúng prompt và đúng hàm dựng thông điệp mà mã sản phẩm dùng**, rồi cho câu trả lời đi qua **đúng bộ kiểm** của sản phẩm (`tools/thuyet_minh/tools_trace.py`). Tài liệu của Ca A là hư cấu, của Ca B là công khai, nên việc gửi ra API không vi phạm quy định dữ liệu (D-2026-10-06-06).

## 5.1. Vị trí và quyền hạn

| Bước | Mã | Chạy sau | LLM được làm | LLM không được làm | Bộ kiểm |
|---|---|---|---|---|---|
| S2 Điền thuộc tính | `assist/stages.py: fill_attributes` | Bước 3 | Chép nguyên văn kỳ, năm gốc, phạm vi mà luật bỏ sót | Suy đoán, đổi đơn vị, điền trường đã có | `guards.verbatim`: chỉ nhận cụm có nguyên văn trong câu |
| S4 Đọc số liệu (IR) | `verification/ir_reader.py` | Bước 6 | Đọc câu thành bản ghi số liệu có cấu trúc | Tự so số, đổi kết luận | `irlib.ground`: số, bội số, năm phải có trong câu; so bằng số học |
| S5 Lập trường | `verification/llm_judge.py` | Bước 6, chỉ cho cặp luật không quyết được | Đánh SUPPORTS / PARTIAL / CONTEXT / CONTRADICTS | Tự thành kết luận; mâu thuẫn của LLM chỉ thành "ủng hộ một phần" + cờ chờ người | Khung dữ liệu ngẫu nhiên, trường `injection`, `llm_stance_decisive = false` |
| S6 Lời giải thích | `assist/stages.py: explain_result` | Sau bước 8 | Viết 2–4 câu giải thích cho người soát, kèm việc nên làm tiếp | Thêm số, đổi kết luận | `guards.new_numbers`: có số không nằm trong nguồn thì bỏ cả lời giải thích |

Thứ tự định tuyến khi bật (`configs/routing.yaml`): ưu tiên mô hình cục bộ `qwen3:4b-instruct-2507-q4_K_M` qua Ollama; dự phòng Groq `openai/gpt-oss-120b`. Hồ sơ `offline` chỉ cho phép nhà cung cấp cục bộ. Mỗi prompt có **chuỗi phiên bản** riêng theo họ mô hình (`small` cho Qwen3-4B/8B, `large` cho gpt-oss-120b, GLM): ví dụ `explain-v2@openai/gpt-oss-120b`. Chuỗi này đi vào khoá bộ nhớ đệm và manifest, nên câu trả lời của một prompt không bao giờ bị dùng cho prompt khác. Toàn văn mọi prompt nằm ở **Phụ lục A**.

## 5.2. Tổng hợp kết quả trên bốn tuyên bố

{{L5_OVERVIEW}}

Ba điều đáng chú ý:

1. Ở A2, S5 và luật cùng đánh đoạn đứng đầu là CONTRADICTS. Trước ngày 14/11 chỉ có S5 thấy mâu thuẫn này ("180 tỷ đồng chưa được phân bổ" trái với "sử dụng hoàn toàn"), còn luật bỏ lọt. Nay luật `absolute-share-v1` bắt được nó bằng phép tính 320/500 = 64%, không cần mô hình.
2. Ở A1 và B2, quan hệ S5 gán cho đoạn đứng đầu trùng với quan hệ của luật. Ở B1 thì khác: luật xếp đoạn đứng đầu (tiêu đề "Tái chế, tái sử dụng chất thải rắn") là PARTIAL theo độ tương đồng, còn S5 xếp là CONTEXT vì đoạn không nêu tỉ lệ nào. Cách đọc của S5 chặt hơn và đúng hơn ở đây. Kết luận cuối của B1 vẫn là "ủng hộ một phần" theo cả hai cách.
3. Lời giải thích S6 của A2 bị bộ kiểm loại, vì mô hình viết "trang 1" trong khi tài liệu văn bản không có số trang. Ba lời giải thích còn lại được hiển thị.

**Kết luận của sản phẩm không đổi** ở cả bốn trường hợp trong lượt ghi vết này. Lý do là S5 chỉ được gửi các cặp mà luật không quyết được (mục 5.5), và bốn tuyên bố này đều đã có quan hệ do luật quyết.

## 5.3. S2: Điền thuộc tính còn thiếu

**Cách chạy.** Với mỗi tuyên bố còn trống ít nhất một trong ba trường `period`, `baseline`, `scope`, hệ thống gửi câu tuyên bố cho mô hình với prompt `attr-v1` (họ large) hoặc `attr-s1` (họ small). Mô hình trả JSON 5 trường (`metric, value, period, baseline, scope`) kèm `is_claim`. Code chỉ giữ một trường khi (a) luật đang để trống trường đó và (b) chuỗi mô hình trả về **có nguyên văn trong câu** (so sau khi chuẩn hoá NFC, hạ chữ, gộp khoảng trắng). Trường được điền ghi vào `claim.assisted_fields` để người soát biết đó là do mô hình.

**Kết quả:**

{{L5_S2}}

Ở B1, mô hình chép được "nhóm thép" làm phạm vi; cụm này có nguyên văn trong câu nên được nhận. Ở A1, luật đã có kỳ và năm gốc nên mô hình không được điền đè. Ở B2, luật đã có phạm vi `group_consolidated`, còn kỳ để trống vì 2018 là năm của tên chuẩn ISO; mô hình cũng không điền kỳ, tức không lặp lại lỗi lấy năm 2018. Lưu ý thiết kế: S2 chỉ điền trường trống, không sửa trường luật đã điền, nên S2 không thể tự sửa được lỗi kiểu này nếu luật vẫn trích nhầm.

**Thông điệp thật gửi đi cho B1:**

{{L5_S2_MSGS_B1}}

## 5.4. S4: Đọc số liệu thành bản ghi có cấu trúc (IR)

**Cách chạy.** Chỉ áp cho câu có chữ số. Mô hình đọc từng câu (tuyên bố, và tối đa 3 câu có số của mỗi đoạn bằng chứng) thành danh sách số liệu với 13 trường: chỉ số (14 mã như `ghg_emissions`, `energy_consumption`, `water_use`…), chữ của giá trị, bội số, đơn vị, loại giá trị (`absolute / intensity / share / change / count`), hướng thay đổi, năm gốc, kỳ, trạng thái (`actual / target`), phạm vi, ranh giới. Code (`irlib.ground`) chỉ giữ số, bội số và năm thật sự có trong câu, rồi **tự so bằng số học**: hai số so được khi cùng chỉ số, cùng loại giá trị, cùng trạng thái, cùng kỳ, phạm vi, ranh giới; khớp khi chênh không quá tổng hai dung sai làm tròn. Nhãn ra là S (ủng hộ), C (bác bỏ) hoặc N (không quyết). Kết quả chỉ ghi vào `result.assist["ir"]` và một cảnh báo, không đổi quan hệ, kết luận hay cờ soát.

**Kết quả:**

{{L5_S4}}

Ở A1, mô hình đọc đúng chỉ số, hướng "giảm", năm gốc 2023, kỳ 2024 và hai số tuyệt đối 100.000 và 112.000 tCO2e của đoạn bằng chứng. Nhưng nó ghi loại giá trị của "30%" là `share` (tỷ trọng) thay vì `change` (mức thay đổi), và để trống đơn vị. Vì vậy code IR không so được hai bên (khác loại giá trị); nhãn là N. Đường IR cũng không tự tính lại mức thay đổi như luật ở bước 6, nên ở ca này luật mạnh hơn. Ở A2 và B2, câu tuyên bố không có số nên IR không có gì để đọc. Ở B1, IR đọc được "99%" nhưng không đoạn nào có số cùng loại.

## 5.5. S5: Đánh giá lập trường bằng mô hình

**Cách chạy.** Khi bật (`llm_stance = on_ambiguous`), S5 chỉ nhận những cặp mà bộ so số, bộ từ khoá và bộ xu hướng **đều không quyết được** và có độ trùng từ từ 0,12. Prompt `stance-v3f` gồm phần nguyên tắc (STANCE_LARGE) và phần an toàn (STANCE_FENCE): tuyên bố và đoạn được đặt giữa hai thẻ `<<<du_lieu_xxxxxxxxxxxx>>>` với mã ngẫu nhiên 12 ký tự hex sinh mới ở mỗi lời gọi, nên tài liệu không thể đóng thẻ sớm; mọi chuỗi dấu `<` `>` trong dữ liệu bị đổi thành `‹ ›`. Mô hình trả `relation`, `reason` và `injection`; `injection = true` thì quan hệ bị ép về CONTEXT. Ngay cả khi bật, `llm_stance_decisive = false`: mâu thuẫn do mô hình chỉ đưa tuyên bố về "ủng hộ một phần" kèm `requires_llm_review` (nhánh 2 của bảng quyết định, mục 4.6.4).

**Kết quả** (để so sánh, tác giả hỏi mô hình cả những cặp mà luật đã quyết; trong sản phẩm, các cặp đó không được gửi):

{{L5_S5}}

**Thông điệp thật gửi đi cho A2** (thấy rõ khung dữ liệu ngẫu nhiên):

{{L5_S5_MSGS_A2}}

Trường hợp A2 cho thấy hai đường đi tới cùng một điều. Mô hình đọc được ý nghĩa của "chưa được phân bổ" và nhận ra nó trái với "hoàn toàn". Từ 14/11, luật cũng thấy điều đó, nhưng bằng một phép chia ghi được trong lý do (320/500 = 64%), nên kết luận "mâu thuẫn" tái lập được mà không cần mô hình. Trước khi có luật này, nếu bật S5, sản phẩm cũng chỉ chuyển A2 sang "ủng hộ một phần" kèm cờ chờ người, không kết luận "mâu thuẫn"; người soát quyết định cuối cùng. Lý do không cho mô hình quyết: trên bộ đo GS-Eval v2 và các lượt đo trước, mô hình lập trường chưa qua cổng đăng ký trước về số "vu oan" (kết luận mâu thuẫn sai) (D-2026-10-16-01).

## 5.6. S6: Lời giải thích cho người soát

**Cách chạy.** Với các tuyên bố trong hàng soát (chế độ `queue`) hoặc mọi tuyên bố (chế độ `all`), hệ thống gửi cho mô hình: câu tuyên bố, kết luận của luật, lý do của luật, tối đa 3 đoạn bằng chứng (tên tài liệu, trang, quan hệ, nội dung), và danh sách thuộc tính còn thiếu bằng tiếng Việt. Prompt `explain-v2` yêu cầu một JSON gồm `explanation` và `next_action`. Code thay tên tệp dạng mã băm bằng chữ "tài liệu", rồi chạy `new_numbers`: lấy mọi con số trong lời giải thích, so với mọi con số có trong câu tuyên bố, lý do và các đoạn (kể cả tên tài liệu và số trang); **có một số lạ là bỏ cả lời giải thích**, người soát chỉ thấy lý do của luật.

**Thông điệp thật gửi đi cho B1:**

{{L5_S6_MSGS_B1}}

**Trả lời và quyết định của bộ kiểm:**

{{L5_S6}}

Bộ kiểm chặn khá chặt. Ở A2, lời giải thích đúng nội dung: 320/500 tỷ đồng, 64%, 180 tỷ chưa phân bổ, trái với "hoàn toàn". Nhưng mô hình viết "tài liệu tài chính (trang 1)", trong khi tài liệu văn bản này không có số trang. Số 1 không có trong nguồn nên cả đoạn bị bỏ, và người soát chỉ thấy lý do của luật. Lượt ghi vết ngày 14/11 có một trường hợp cùng kiểu: lời giải thích của A1 bị bỏ vì mô hình viết thêm "Scope 3". Đây là đánh đổi có chủ đích: thà mất một lời giải thích còn hơn hiển thị một con số không truy được nguồn. Lượt chạy ngày 13/11 còn cho thấy một đường loại khác: lời giải thích của một tuyên bố bị bỏ vì mô hình trả JSON hỏng. `StageModel.ask` không lưu câu trả lời hỏng vào bộ nhớ đệm nên lượt sau hỏi lại.

## 5.7. Vì sao kết luận không đổi

Bốn bước trên đều được thiết kế để **không chạm** vào trường `status` của kết quả kiểm chứng:

- S2 chỉ thêm thuộc tính, và chỉ thêm nguyên văn.
- S4 ghi vào `assist["ir"]`, không vào `relation`.
- S5 nếu bật chỉ có thể đưa một tuyên bố về "ủng hộ một phần" kèm cờ chờ người; không thể tạo `CONTRADICTED` hay `SUPPORTED`.
- S6 ghi vào `assist["explanation"]`, hiển thị cạnh lý do của luật, có nhãn là do mô hình viết.

Nhờ đó, kết luận của hệ thống luôn tái lập được bằng luật và phép tính, còn LLM chỉ giúp người soát đọc nhanh hơn và chỉ ra chỗ luật có thể đã bỏ sót.
