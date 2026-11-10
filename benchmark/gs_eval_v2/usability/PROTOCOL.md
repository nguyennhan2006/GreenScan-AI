# Giao thức thử nghiệm độ dễ dùng GreenScan với người thật (D-UX)

*Soạn 04/11/2026 · labeler `claude-opus-5-5` · guide_version `gs-eval-v2.0` · review_status `pending_human_review` (Nhân duyệt). Theo `LABELING_GUIDE.md` §5.*

Tệp đi kèm: `tasks.yaml` (16 nhiệm vụ, câu hỏi SEQ / niềm tin / kiểm hiểu), `SUS_vi.md`, `heuristics.yaml` (18 nguyên tắc, thang mức độ 0–4), `ux_lint_spec.md` (kiểm tự động), `persona_walkthrough.md` (mô phỏng bằng agent, chạy **trước** để chọn điểm cần hỏi, không thay buổi thử này).

## 1. Câu hỏi đánh giá

| Mã | Câu hỏi | Đo bằng |
|---|---|---|
| UX-1 | Kiểm toán viên có tự làm xong các việc cốt lõi không: đọc hàng đợi, hiểu vì sao một tuyên bố bị gắn cờ, ghi quyết định, xử lý gợi ý sửa, xuất giấy làm việc? | Tỷ lệ hoàn thành T03, T04, T07, T09, T11 |
| UX-2 | Người dùng có hiểu đúng kết luận, nhất là không đọc “chưa đủ bằng chứng” thành “doanh nghiệp sai / vi phạm”? | Kiểm hiểu KH1–KH4, KH6; lỗi nghiêm trọng ở T04, T06 |
| UX-3 | Niềm tin có được hiệu chỉnh: hiểu, kiểm lại được, nhưng không ghi kết luận yếu vào giấy làm việc mà không kiểm? | NT1–NT4 sau T04, T09 |
| UX-4 | Cảm nhận tổng thể về độ dễ dùng ở mức nào? | SUS, SEQ |
| UX-5 | Người phụ trách tuân thủ có đưa được quy tắc nội bộ vào, biết nó áp dụng chưa và tác động ra sao? | T13, T14 trên bản mẫu (kiểm khái niệm, báo cáo riêng) |

Bài đo **thời gian tiết kiệm so với làm tay** (RQ10, `AUDITOR_WORKFLOW_POSITIONING.md` §6) là giao thức riêng, không nói to suy nghĩ. Có thể dùng chung người tham gia nhưng không gộp số.

## 2. Người tham gia

| Persona (`tasks.yaml`) | Tiêu chí chọn | Vòng A (trước 10/11) | Vòng B (sau chung kết) |
|---|---|---|---|
| KTV | ≥ 1 năm kiểm toán, đảm bảo hoặc kiểm soát nội bộ. Nếu không tuyển được: sinh viên năm 3–4 kiểm toán đã học chuẩn mực kiểm toán, ghi rõ là **đại diện gần (proxy)** | 3–5 | 5–8 |
| PT | Phân tích đầu tư, ESG hoặc tư vấn bền vững | 0–1 | 3 |
| TD | Cán bộ tín dụng, thẩm định tại ngân hàng | 0–1 | 3 |
| TT | Cán bộ tuân thủ, pháp chế, hoặc phụ trách phương pháp ở công ty kiểm toán | 0–1 (chỉ T13–T14) | 3 |

- Loại trừ: thành viên đội GreenScan; người đã xem demo chi tiết (được dùng cho buổi thí điểm).
- Năm người thường đủ để thấy phần lớn vấn đề lớn của một giao diện (Nielsen & Landauer 1993) [KIẾN THỨC NỀN], nhưng **không đủ** để có số SUS hay tỷ lệ hoàn thành chắc chắn; mọi số của vòng A ghi “sơ bộ, n = …”.
- Đồng ý tham gia: phiếu ghi mục đích, việc ghi màn hình và tiếng, ẩn danh bằng mã P01…, quyền dừng bất cứ lúc nào, thời hạn giữ dữ liệu (§11).

## 3. Chuẩn bị

**Vai trò:** một người điều phối (không phải người viết giao diện, để tránh bênh vực thiết kế) và một người ghi chép.

**Máy:** app một cổng `python -m quantum_gw.cli app --port 8011`; trình duyệt cửa sổ 1672×941 trở lên (cỡ ảnh chụp); phần mềm ghi màn hình; Word để mở DOCX (T12).

**Dữ liệu:**
1. Phiên demo `cd5a82e326bf4117` (Hòa Phát, 156 tuyên bố, 9 mục trong hàng đợi). Đáp án trong `tasks.yaml` theo phiên này.
2. Phiên phụ **P-MT** có một ca Mâu thuẫn (phiên demo có 0 mâu thuẫn), **P-CHOT** có mục #3 đã chốt. Cách làm: `tasks.yaml` → `moi_truong.phien_phu_can_chuan_bi`.
3. Bản mẫu cho T13–T14 (HTML tĩnh hoặc giấy) theo đường đi “ĐỀ XUẤT” và thông báo lỗi mẫu trong `tasks.yaml`; hai tệp `pack.yaml` (nháp, đã duyệt) và một tệp lỗi.

**Khôi phục trạng thái sạch cho từng người** (quyết định và nhật ký Studio là append-only):
1. Trước buổi đầu: đóng app, nén nguyên thư mục `.quantum/` thành bản sạch.
2. Sau mỗi người: đóng app, khôi phục bản sạch, mở lại; chốt sẵn mục #3 (P-CHOT); vào Cài đặt bấm “Quên tên” để người sau nhập mã của mình.
3. Kiểm nhanh: hàng đợi “Đã chốt 0/9” (trước khi chốt P-CHOT), Studio “Nhật ký thay đổi (0)”.
4. [CHƯA XÁC MINH] khôi phục `.quantum/` là đủ để xoá mọi trạng thái (tên người soát xét lưu ở trình duyệt; có thể còn bộ nhớ đệm khác). Làm thử một lần ở buổi thí điểm.

**Thí điểm:** chạy trọn buổi với một người trước vòng A; sửa kịch bản, thời gian mục tiêu, đáp án; ghi thay đổi vào `tasks.yaml` (giữ `review_status: pending_human_review` cho tới khi Nhân duyệt).

## 4. Trình tự một buổi (60–75 phút)

| Phút | Bước | Ghi chú |
|---|---|---|
| 0–5 | Chào, phiếu đồng ý, lời giới thiệu chuẩn (Phụ lục A) | Không giới thiệu tính năng, không demo |
| 5–8 | Phiếu nền (Phụ lục B) | |
| 8–10 | Khởi động nói to suy nghĩ (§5) | Bài tập ngoài GreenScan |
| 10–35 | Khối 1: T02 → T03 → T04 → T05 → T06; Khối 2: T07 → T08 | Khối 1 trước vì T07 dùng hiểu biết từ T04 |
| 35–50 | Khối 3: T09 → T10 → T12; Khối 4: T11 → T16; Khối 5: T15 | T11 sau T07 để có quyết định trong giấy làm việc |
| 50–53 | **SUS** (`SUS_vi.md`) | Trước khối khái niệm |
| 53–63 | Khối 6 (chỉ TT, TD hoặc KTV trưởng nhóm): T13 → T14 trên bản mẫu | Báo cáo riêng, không gộp SUS |
| 63–70 | Phỏng vấn cuối buổi (§10) | |
| tuỳ | T01 (tạo phiên mới, máy chạy khoảng 2 phút) | Chỉ khi còn thời gian; cuối buổi |

- Sau mỗi nhiệm vụ: SEQ; sau T04 và T09 thêm NT1–NT4; kiểm hiểu KH1–KH4 sau khối 1, KH6 sau T09, KH5 sau T13 (văn bản câu hỏi ở `tasks.yaml` → `cau_hoi`).
- Thứ tự cố định vì nhiệm vụ phụ thuộc nhau; ghi rõ là giới hạn (hiệu ứng học). Trong một khối, nếu có ≥ 6 người, đảo thứ tự T05/T06 và T15/T16 xen kẽ giữa người chẵn và lẻ.

## 5. Nói to suy nghĩ

- Kiểu đồng thời (concurrent think-aloud): người tham gia nói điều mình đang nhìn, đang tìm, đang nghĩ.
- Khởi động 2 phút: đếm số cửa sổ trong nhà mình trong khi nói to cách đếm, hoặc tìm một mục trong một trang web bất kỳ.
- Người điều phối chỉ nói câu trung tính: “Anh/chị đang nghĩ gì?” (sau khoảng 15 giây im lặng), “Anh/chị đang tìm gì?”, “Cứ làm như khi ở một mình.” Không trả lời câu hỏi về giao diện trong lúc làm; ghi lại câu hỏi đó.
- Trợ giúp: chỉ khi người tham gia bế tắc quá `thoi_gian_toi_da_giay` hoặc xin giúp hai lần. Mỗi lần trợ giúp ghi `assists += 1`; điểm nhiệm vụ tối đa 0,5.
- Nói to làm chậm thao tác; thời gian trong giao thức này chỉ dùng **so tương đối** giữa nhiệm vụ và giữa các phiên bản giao diện, không dùng làm số “tiết kiệm thời gian”.

## 6. Đo gì

| Chỉ số | Định nghĩa | Cách ghi |
|---|---|---|
| Hoàn thành | 1 / 0,5 / 0 theo `cham` của từng nhiệm vụ và `cham_chung` | Người ghi chép đánh dấu từng tiêu chí `c1…` |
| Thời gian | Từ lúc đọc xong kịch bản tới lúc người tham gia nói “xong” hoặc đạt tiêu chí | Đồng hồ + mốc trong video |
| Lỗi thao tác (slip) | Bấm nhầm rồi tự sửa | Đếm, ghi chỗ |
| Lỗi hiểu (mistake) | Hiểu sai nghĩa nhãn, số, kết luận | Ghi nguyên văn câu nói |
| Lỗi nghiêm trọng | Ghi hoặc nói kết luận sai có thể vào giấy làm việc: coi chưa đủ bằng chứng là vi phạm, coi quy tắc nội bộ đổi được kết luận, xuất giấy mà tưởng đã soát hết | Nhiệm vụ = 0 |
| Lệch đường | Đi khác `duong_di_mong_doi` nhưng vẫn tới đích | Ghi đường thực tế (để sửa giao diện hoặc sửa đường mong đợi) |
| SEQ | 1–7, sau mỗi nhiệm vụ | Phiếu |
| Niềm tin NT1–NT4 | 1–7, sau T04, T09 (và T13 trên bản mẫu) | Phiếu |
| Kiểm hiểu KH1–KH6 | Đúng / Sai | Phiếu |
| SUS | 0–100 | `SUS_vi.md` |
| Vấn đề khả dụng | Mỗi vấn đề: mô tả, nhiệm vụ, nguyên tắc (`heuristics.yaml`), mức 0–4, tần suất k/n, trích lời | Sau buổi, hai người chấm độc lập |

## 7. Ngưỡng đặt trước (đề xuất, Nhân duyệt trước buổi thí điểm)

| Chỉ tiêu | Ngưỡng vòng A |
|---|---|
| Hoàn thành không trợ giúp, từng nhiệm vụ cốt lõi T03, T04, T07, T09, T11 | ≥ 4/5 người (≥ 80 %) |
| Lỗi nghiêm trọng ở T04, T06 | 0 |
| Kiểm hiểu KH1–KH4, KH6 | ≥ 4/5 câu đúng ở ≥ 80 % người |
| Hiệu chỉnh niềm tin ở T04 (ca bằng chứng yếu: ủng hộ một phần, không nguồn độc lập) | trung vị NT2 ≥ 5 **và** trung vị NT3 ≤ 4 |
| SUS trung bình | ≥ 68 (xem diễn giải ở `SUS_vi.md` §5) |
| SEQ trung bình nhiệm vụ cốt lõi | ≥ 5 (mức tham chiếu khoảng 5,5 theo Sauro [CHƯA XÁC MINH]) |
| Thời gian | ≥ 60 % lượt đạt nằm trong `thoi_gian_muc_tieu_giay` (chỉ để hiệu chỉnh) |

Không đạt ngưỡng thì không “làm tròn”; ghi vào phần hạn chế của luận văn kèm vấn đề gây ra.

## 8. Ghi dữ liệu

Một dòng JSON cho mỗi lượt nhiệm vụ, ghi vào `usability/results/round_<A|B>.jsonl` (thư mục tạo khi bắt đầu vòng thử; chưa có ngày 04/11):

```json
{"participant_id": "P01", "persona": "KTV", "proxy": false, "round": "A", "date": "2026-11-06",
 "task_id": "T04", "order": 4, "time_s": 163, "outcome": 1, "criteria_met": ["c1", "c2", "c3", "c4"],
 "assists": 0, "errors": [{"type": "mistake", "critical": false, "note": "đọc 92 % là độ tin cậy"}],
 "path_actual": "Hàng đợi → Mở → tab Bằng chứng → Studio", "seq": 6,
 "trust": {"NT1": 6, "NT2": 6, "NT3": 3, "NT4": 5}, "comprehension": {"KH1": "Sai", "KH3": "Đúng"},
 "quotes": ["…"], "heuristics_hit": ["H02", "A02"], "moderator": "…", "note_taker": "…",
 "app_build": "ngày build hoặc mã phiên", "review_status": "pending_human_review"}
```

SUS ghi riêng một dòng mỗi người theo mẫu ở `SUS_vi.md` §7. Vấn đề khả dụng ghi theo mẫu ở `persona_walkthrough.md` §6, trường `nguon: nguoi_that`.

## 9. Phân tích

- **Tỷ lệ hoàn thành:** x/n kèm khoảng tin cậy 95 % Wald hiệu chỉnh (Agresti–Coull; Sauro & Lewis 2005 cho mẫu nhỏ) [KIẾN THỨC NỀN]: p̃ = (x + 1,92) / (n + 3,84); p̃ ± 1,96 × √(p̃(1 − p̃) / (n + 3,84)). Ví dụ 4/5: p̃ = 0,670, khoảng 0,36–0,98 — cho thấy n = 5 chỉ đủ phát hiện vấn đề, không đủ để khẳng định tỷ lệ.
- **Thời gian:** chỉ lượt đạt; trung bình nhân (exp của trung bình ln t) và trung vị; khoảng tin cậy tính trên ln t.
- **SEQ, NT:** trung bình và trung vị theo nhiệm vụ; NT3 cao ở ca bằng chứng yếu là dấu hiệu tin quá mức (Lee & See 2004) [KIẾN THỨC NỀN].
- **Vấn đề:** gộp trùng; mức độ = trung bình của hai người chấm; xếp ưu tiên theo mức độ × tần suất; gắn mã nguyên tắc; đối chiếu với phát hiện mô phỏng (`persona_walkthrough.md`) để biết mô phỏng trúng, trượt bao nhiêu (báo số trúng / tổng).
- **Theo persona:** chỉ tách khi mỗi nhóm có ≥ 3 người.

## 10. Phỏng vấn cuối buổi

1. Điều gì khiến anh/chị tin, hoặc không tin, kết quả của GreenScan?
2. Nếu dùng thật, anh/chị vẫn sẽ kiểm lại bằng tay phần nào?
3. Có chỗ nào anh/chị sợ ghi sai vào giấy làm việc không?
4. So với cách làm hiện nay (đọc, Ctrl+F, gõ giấy làm việc), phần nào nhanh hơn, phần nào chậm hơn?
5. (TT, TD) Anh/chị muốn đưa loại quy tắc hay tài liệu nội bộ nào vào? Cần thấy gì để yên tâm rằng hệ thống làm đúng theo quy tắc đó?

## 11. Đạo đức và dữ liệu cá nhân

- Chỉ dùng tài liệu công khai (báo cáo đã công bố của Hòa Phát) và tài liệu giả lập; không đưa tài liệu nội bộ thật của người tham gia vào máy thử.
- Video, tiếng: chỉ ghi khi đồng ý; lưu ở ổ của đội; xoá sau 30 ngày kể từ khi phân tích xong (đề xuất). Bảng kết quả chỉ chứa mã P01…; danh sách tên ↔ mã giữ riêng.
- Dự án đã lưu ý Luật BVDLCN 91/2025 (theo `KE_HOACH_PHAN_BIEN_HE_THONG_VA_EDITOR_2026-10-14.md` §3); việc ghi hình người tham gia cần phiếu đồng ý bằng văn bản [CHƯA XÁC MINH yêu cầu cụ thể của luật với nghiên cứu sinh viên].

## 12. Giới hạn và đe doạ hiệu lực

- **Người đại diện gần:** sinh viên không có xét đoán nghề nghiệp như kiểm toán viên; kết quả về hiểu kết luận có thể lạc quan hoặc bi quan hơn thực tế.
- **Một bộ dữ liệu:** phiên demo chỉ có Hòa Phát, kết quả phẳng (153/156 “ủng hộ một phần”, 0 mâu thuẫn) vì toàn bộ bằng chứng là tài liệu nội bộ. Giao diện cho ca mâu thuẫn chỉ thử được qua phiên phụ P-MT.
- **Ảnh chụp và bản build:** đường đi mong đợi viết theo ảnh 15/10 và mã đọc 04/11; giao diện có thể đã đổi. Buổi thí điểm phải đối chiếu lại.
- **Người điều phối, hiệu ứng học, nói to suy nghĩ** làm lệch thời gian và hành vi; ghi rõ trong báo cáo.
- **T13–T14 trên bản mẫu:** đo cách hiểu khái niệm, không đo độ dễ dùng của tính năng (chưa có).

## 13. Lịch đề xuất (Nhân quyết)

| Ngày | Việc |
|---|---|
| 04–05/11 | Nhân duyệt bộ D-UX; chuẩn bị máy, bản sạch `.quantum/`, P-MT, P-CHOT, bản mẫu T13–T14; chạy `persona_walkthrough.md` để chọn câu hỏi thăm dò |
| 05/11 | Thí điểm 1 người; sửa `tasks.yaml` |
| 06–08/11 | Vòng A, 3–5 người |
| 09/11 | Tổng hợp; số nào đưa vào phần hỏi đáp thì ghi kèm n |
| sau 10/11 | Vòng B theo persona; T13–T14 trên giao diện thật khi có bộ nạp org pack |

Không tuyển kịp người trước 10/11 thì báo trung thực: bộ kiểm đã thiết kế, kiểm tự động (`ux_lint_spec.md`) đã chạy sơ bộ trên phiên demo, thử với người thật chưa làm.

## 14. Một câu trả lời mẫu khi giám khảo hỏi “đã thử với người dùng chưa?”

Chỉ dùng số đã đo. Nếu đã chạy vòng A: “Vòng đầu n = …: nhiệm vụ cốt lõi đạt …/…, SUS trung bình … (n nhỏ, sơ bộ); vấn đề lớn nhất là …, đã sửa / đang sửa.” Nếu chưa: “Chúng tôi đã dựng bộ kiểm 16 nhiệm vụ theo vai trò, SUS tiếng Việt, 18 nguyên tắc chấm chuyên gia và 15 kiểm tự động trên đầu ra; kiểm tự động trên phiên demo phát hiện … (số trong `ux_lint_spec.md` §3). Thử với kiểm toán viên thật là bước kế tiếp.”

---

## Phụ lục A. Lời giới thiệu chuẩn (đọc nguyên văn)

> Cảm ơn anh/chị đã tham gia. GreenScan là công cụ hỗ trợ rà soát các tuyên bố môi trường trong báo cáo doanh nghiệp: nó đọc báo cáo, tìm các câu tuyên bố, tìm đoạn đối chiếu và xếp thứ tự nên soát. Quyết định cuối cùng là của người soát xét.
> Hôm nay chúng tôi thử phần mềm, không thử anh/chị. Chỗ nào anh/chị thấy khó là thông tin quý cho chúng tôi. Tôi sẽ đọc từng tình huống; anh/chị làm như khi đang làm việc thật, và nói to điều mình đang nghĩ. Trong lúc làm, tôi sẽ không trả lời câu hỏi về cách dùng; cuối buổi tôi sẽ giải thích mọi thứ.

## Phụ lục B. Phiếu nền

1. Vai trò hiện tại; số năm kinh nghiệm kiểm toán / đảm bảo / phân tích / tín dụng / tuân thủ.
2. Đã từng rà soát báo cáo phát triển bền vững chưa? (chưa / 1–2 lần / thường xuyên)
3. Mức quen với: GRI, ISSA 5000 hoặc ISAE 3000, kiểm kê khí nhà kính (Scope 1/2/3) — mỗi mục 1–5.
4. Tần suất dùng công cụ AI trong công việc (không / hàng tháng / hàng tuần / hàng ngày).
5. Mức tin chung vào kết quả do AI tạo ra (1–7).
