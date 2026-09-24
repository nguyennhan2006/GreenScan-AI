# Sơ đồ pipeline 16:9 — mô hình thông tin và bản dựng

**Ngày:** 2026-09-24 · **Trạng thái:** camera-ready, đã dựng vector
**Tệp xuất:** [`diagrams/pipeline_16x9_vi.svg`](diagrams/pipeline_16x9_vi.svg) · [`.png`](diagrams/pipeline_16x9_vi.png) (3840×2160) · bản tiếng Anh [`_en.svg`](diagrams/pipeline_16x9_en.svg) · [`.png`](diagrams/pipeline_16x9_en.png)
**Dựng lại:** `python tools/make_pipeline_diagram.py` (cần `pip install -e ".[docs]"`)

> **Chữ là dữ liệu, hình học là code.** Sơ đồ được dựng vector chứ không sinh bằng AI: giá trị của nó nằm ở chỗ chữ đúng từng ký tự và các mũi tên đúng logic. Mô hình sinh ảnh viết lại nhãn, bỏ connector, tự đổi 30 thành 5 và không viết nổi dấu tiếng Việt. Ở đây mọi thay đổi đều nhìn được trong diff.

---

## 1. Cốt lõi phải truyền đạt

> **Không chấm "doanh nghiệp này có greenwashing không" ngay từ đầu.** Tách từng tuyên bố → tìm bằng chứng → kiểm tra xem hai con số có được phép so với nhau không → đối chiếu luật → chỉ sau đó mới kết luận.

> **Mô hình đọc. Luật quyết định. Người duyệt ca rủi ro cao.**

---

## 2. Bảy quyết định thiết kế (và vì sao)

### 2.1 Ba cửa vào, không phải một đống PDF

Không phải tài liệu nào cũng đi cùng một đường. Vẽ đúng ba luồng cho thấy đây là hệ kiểm chứng đa nguồn, không phải chatbot đọc một tệp:

| Nhóm | Vào ở bước | Vì sao quan trọng |
| --- | --- | --- |
| Báo cáo doanh nghiệp (PTBV, thường niên, tài chính, bản scan) | **ĐỌC TÀI LIỆU** | Nguồn tuyên bố |
| Bằng chứng độc lập (kiểm toán, cơ quan quản lý, quyết định xử phạt) | **TÌM BẰNG CHỨNG** | Một báo cáo không được tự xác nhận mình |
| Văn bản pháp luật + ngày hiệu lực | **ĐỐI CHIẾU PHÁP LUẬT** | Nghĩa vụ phụ thuộc thời điểm công bố |

### 2.2 Ranh giới pha được **vẽ ra**, không để ngầm hiểu

Một đường kẻ đứt ngang chia sơ đồ: phía trên là mô hình đọc, phía dưới là luật quyết định. Đây là thông điệp kiến trúc quan trọng nhất, nên nó phải là một nét vẽ chứ không phải một câu chú thích.

### 2.3 Badge trên từng thẻ, **không tô màu cả khối theo tầng**

Tô "thẻ 1–4 = AI, thẻ 5–8 = luật" thì dễ nhìn nhưng **sai**: bước đọc tài liệu có parser và thư viện chứ không chỉ mô hình; bước kiểm chứng có mô hình dự phòng cho tuyên bố không định lượng; bước cuối có con người. Người nghe kỹ thuật sẽ bắt được chỗ đơn giản hoá đó.

| Thẻ | Badge |
| --- | --- |
| Đọc tài liệu | `PARSER + MÔ HÌNH` |
| Lọc tuyên bố · Cấu trúc hoá · Tìm bằng chứng | `MÔ HÌNH` |
| Cổng khả năng so sánh · Đối chiếu pháp luật · Kết luận | `LUẬT` |
| Cổng kiểm soát | `LUẬT + NGƯỜI` |

### 2.4 Cổng khả năng so sánh là **nhân vật chính**

Nếu tám thẻ bằng nhau thì điểm mới lớn nhất bị chìm. Thẻ này to gấp đôi, viền đậm, có câu hỏi hiển thị rõ — *"Hai con số này có được phép so với nhau không?"* — hai con số đi vào, sáu điều kiện, hai ngả ra:

- **ĐƯỢC SO** → tính toán, dung sai theo độ chính xác đã công bố
- **KHÔNG SO ĐƯỢC** (viền đỏ) → không kết luận mâu thuẫn, chuyển người xem

Đây là hình ảnh đáng nhớ sau buổi thuyết trình, và nó minh hoạ đúng câu *"mô hình đọc, luật quyết định"*.

### 2.5 `30 → 5` thể hiện bằng hình, không bằng chữ

Trong thẻ *Tìm bằng chứng*: 30 ô mờ → phễu → 5 ô đậm. Cơ sở: thêm tài liệu truy xuất không đảm bảo tốt hơn, tài liệu nhiễu làm giảm chất lượng. Không cần viết giải thích.

### 2.6 Đầu ra **không phải "điểm greenwashing"**

Đây là chỗ dễ bị hỏi nhất. Sơ đồ ghi **kết luận từng tuyên bố** (5 mức) rồi mới tới **hồ sơ rủi ro** ba chiều. Nếu dashboard cần một số 0–100 thì gọi là *tóm tắt rủi ro*, tuyệt đối không gọi là *"72% greenwashing"* — hai khái niệm khác nhau hoàn toàn.

Ba chiều rủi ro trên hình đúng bằng ba trường trong code: **độ mạnh bằng chứng · mức mâu thuẫn · mức trọng yếu**. Trường thứ ba hiện luôn là "chưa xác định" vì chưa có cơ sở đo — không bịa ra một cột "compliance risk" chưa tồn tại.

### 2.7 "Chưa đủ bằng chứng" có vị trí riêng

Không để nó làm chip thứ năm ngang hàng. Nó nằm trong ô màu hổ phách riêng, kèm dòng *thiếu: năm gốc · phạm vi · nguồn độc lập*. Thông điệp: **không biết cũng là một kết quả hợp lệ** — và đó là lý do hệ thống đáng tin hơn một mô hình buộc phải trả lời.

---

## 3. Vòng phản hồi: bốn bước, nét đứt

Không nối thẳng `Người → Mô hình` (dễ hiểu nhầm là người sửa thì mô hình học ngay):

```text
Quyết định người duyệt ⇢ Nhãn đã tuyển ⇢ Tập huấn luyện / đánh giá ⇢ Cập nhật mô hình định kỳ ⇢ quay lại bước CẤU TRÚC HOÁ
```

---

## 4. Tám bước hay chín bước hay mười bước?

Ba con số đang tồn tại trong ba tài liệu. Không phải mâu thuẫn, nhưng phải nói rõ kẻo bị hỏi vặn:

| Cách nhìn | Số bước | Dùng ở đâu | Nguồn |
| --- | --- | --- | --- |
| **Kiến trúc** | **8** | Slide, sơ đồ này | Đọc · Lọc · Cấu trúc · Bằng chứng · Kiểm chứng · Luật · Kết luận · Kiểm soát |
| **Thực thi** | **10** | Phụ lục kỹ thuật | `OrchestratorAgent.PLAN` trong code — thêm *validate_inputs* và *build_retrieval_index* |
| Hồ sơ Vòng 1 | 9 | Tài liệu đã nộp | Gộp khác một chút |

**Cách nói an toàn:** *"Kiến trúc 8 khối; khi chạy, trình điều phối thực thi 10 thao tác có đánh số và ghi trong manifest của mỗi lần chạy."* Hai sơ đồ nói ở hai mức trừu tượng khác nhau, không cần ép làm một.

---

## 5. Hệ thị giác

| Yếu tố | Giá trị |
| --- | --- |
| Nền | `#F7F7F4` off-white |
| Tầng luật | navy `#16283B` |
| Tầng mô hình | green `#1F7A52` |
| Abstain | amber `#B8792B` |
| Không so được | red `#A32C1E` |
| Đường kẻ | `#C3CDC7`, connector 1.8–2 px |
| Chữ | Segoe UI / Inter / IBM Plex Sans |
| Bo góc | 8–10 px · bóng: không · gradient: không |

Cảm giác cần đạt: **phần mềm kiểm toán / rủi ro doanh nghiệp**, không phải poster AI startup. Tránh: neon, bo mạch, robot, não phát sáng, 3D.

---

## 6. Kiểm tra trước khi dùng — bảy câu trong mười giây

Người chưa biết GreenScan nhìn hình phải trả lời được, **không đọc đoạn văn nào**:

| # | Câu hỏi | Nhìn vào đâu trên hình |
| --- | --- | --- |
| 1 | Đầu vào là gì? | Ba thẻ cửa vào bên trái |
| 2 | AI làm gì? | Bốn thẻ xanh lá hàng trên |
| 3 | Khác LLM thường ở đâu? | Đường kẻ ranh giới pha |
| 4 | Điểm kỹ thuật đặc biệt? | Cổng khả năng so sánh, 6 điều kiện |
| 5 | Thiếu bằng chứng thì sao? | Ô hổ phách "Chưa đủ bằng chứng" |
| 6 | Ai chịu trách nhiệm cuối? | Thẻ cổng kiểm soát + người duyệt |
| 7 | Đầu ra là gì? | Thẻ hồ sơ kiểm chứng màu navy |

Bản hiện tại trả lời được cả bảy.

---

## 7. AI sinh ảnh dùng vào việc gì

**Không dùng để vẽ sơ đồ này.** Chỉ dùng cho hình minh hoạ không chứa chữ, ví dụ slide mở đầu:

```text
A single conceptual illustration, flat vector, no text: a magnifying glass held over
one sentence inside a thick corporate sustainability report; through the lens the
sentence breaks into small labelled chips that float outward and connect by thin lines
to a page in a second document and to a small balance scale. Muted green and navy on
off-white, calm and precise, editorial infographic style, no words anywhere.
```

Nếu cần đổi bố cục sơ đồ: sửa `tools/make_pipeline_diagram.py` rồi chạy lại — **toàn bộ chữ nằm trong một từ điển `TEXT` ở đầu tệp**, đổi nhãn không cần động vào hình học.

---

## 8. Liên quan

[TARGET_PIPELINE_AND_TRAINING.md](../04-data-ai/TARGET_PIPELINE_AND_TRAINING.md) (mô hình nào cho việc nào, kế hoạch huấn luyện) · [DATA_LAYERS.md](../04-data-ai/DATA_LAYERS.md) · [RESEARCH_PROGRAM_2026-09-22.md](../00-project/RESEARCH_PROGRAM_2026-09-22.md) · [QA_BANK_100_2026-09-20.md](QA_BANK_100_2026-09-20.md)
