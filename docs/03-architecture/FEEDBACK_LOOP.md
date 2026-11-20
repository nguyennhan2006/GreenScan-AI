# Vòng học từ phản hồi của người soát (feedback-loop-v1)

Quyết định: D-2026-11-14-03. Mã: `src/quantum_gw/feedback/`, `storage/reviews.py`. Kiểm thử: `tests/test_feedback_loop.py`, `tests/test_org_pack_upload.py`.

## Nguyên tắc

Hệ thống **không học trực tuyến**: không có chuyện mỗi lần người soát sửa là mô hình tự đổi. Có ba lý do:

1. **Không đổi kết luận khi chưa đo** (D-2026-10-16-01). Kết luận chỉ đổi qua một phiên bản mới đã được đo trước và sau.
2. **Chống đầu độc.** Doanh nghiệp bị kiểm, hay một người soát cẩu thả, không được "dạy" hệ thống chấp nhận tuyên bố của mình.
3. **Truy vết được.** Cùng một hồ sơ, tuần này và tuần sau phải ra cùng kết luận, trừ khi có một phiên bản giải thích vì sao khác.

Vòng học vì vậy đi theo thứ tự: **phản hồi → đề xuất có phiên bản → đo → người duyệt → phát hành**. Không thành phần nào trong vòng đọc hay ghi kết luận, điểm rủi ro hay trạng thái phát hành. Hàng soát chỉ được **thêm** mục, không bao giờ bớt.

## Năm tầng

| Tầng | Làm gì | Ở đâu | Tác động lên một lượt chạy |
|---|---|---|---|
| 0. Nhãn chỉ chỗ | Người soát đánh dấu đoạn khiến họ kết luận, hoặc dán trích dẫn nếu máy không đưa ra đoạn đó. Máy tự suy ra giai đoạn sai: đoạn có trong danh sách mà vẫn kết luận sai là `reading` (đọc sai); đoạn không có là `retrieval` (tìm sai); lý do quy cho quy tắc là `rule` | `reviews.classify_stage`, `DecisionBar.jsx` | không |
| 1. GS-Feedback | Mỗi quyết định đã chốt thành một ca kiểm, chạy lại trên **đúng bằng chứng người soát đã thấy** (chụp tới 4.000 ký tự mỗi đoạn, kèm hồ sơ kho tài liệu của phiên). Bánh cóc `ratchet.json`: ca đã qua mà hỏng lại là hồi quy, lệnh trả mã lỗi | `feedback/bench.py`, `benchmark/gs_feedback/` | không |
| 2. Tiền lệ | Tuyên bố mới giống một tuyên bố đã chốt (cosine trên từ và cặp từ đã bỏ dấu) thì hiện thẻ tiền lệ cạnh kết luận. Nếu người soát từng ghi đè máy ở câu rất giống (độ giống ≥ 0,75) thì câu được thêm vào hàng soát. Khi bật S5, tiền lệ có nhãn chỉ chỗ được đưa vào prompt làm ví dụ mẫu | `feedback/precedents.py`, `feedback/memory.py` | thêm `precedents`, thêm `raised_by` và ghi `manifest.feedback` |
| 3. Máy đào luật | Gom các lần ghi đè thành **phiếu đề xuất**: cụm từ lập trường (lấy từ đoạn quyết định của các ca `reading`), ngoại lệ hoặc sửa quy tắc, từ đồng nghĩa cho truy xuất, quy tắc org pack nháp. `--measure` đo từng cụm từ trên GS-Feedback và GS-Bench bằng một bản sao tạm của `stance_cues.yaml` (`QUANTUM_STANCE_CUES`) | `feedback/miner.py` | không |
| 4. Mô hình thách đấu | Xuất cặp (tuyên bố, đoạn, quan hệ) từ nhãn chỉ chỗ đã lọc và 821 cặp Claude gán nhãn. Huấn luyện mô hình CPU `hashed-linear-v1`. Chấm cùng nhà vô địch (luật) trên tập giữ lại, tách theo công ty hoặc theo phiên. Mô hình đạt cổng thì lên `candidate` và chỉ thành `promoted` khi có người khác ký. Có thể chạy ngầm (`shadow.jsonl`); nếu đã thăng hạng thì có thể thay LLM cho các cặp mà luật đẩy lên | `feedback/dataset.py`, `stance_model.py`, `registry.py`, `local_judge.py` | ngầm: không; thay LLM: như LLM, có cùng chốt |

## Hai cơ chế giữ vòng học sạch

**Chọn ca nên hỏi** (`feedback/active.py`, mặc định tắt). Mỗi tuyên bố có một giá trị học từ 0 đến 1, kèm lý do:

| Thành phần | Trọng số |
|---|---|
| Bằng chứng trái chiều | 0,35 |
| Luật chưa quyết được | 0,25 |
| Mô hình thử nghiệm bất đồng với luật | 0,30 |
| Loại tuyên bố mới có dưới 5 nhãn | 0,20 |
| Chưa có tiền lệ | 0,10 |

`active_learning_slots` chỗ thêm trong hàng soát dành cho các tuyên bố có giá trị học cao nhất (≥ 0,3) chưa có trong hàng.

**Lọc nhãn** (`feedback/hygiene.py`):
- **Bên bị kiểm không dạy bên kiểm.** Nhãn có vai trò `reviewed_company` được lưu trong vết kiểm toán nhưng không bao giờ huấn luyện hay chấm mô hình.
- **Bất đồng không phải nhãn.**
  - Mỗi tháng lấy mẫu 10% nhãn đã chốt. Mẫu là tất định theo hạt giống `YYYY-MM`.
  - Người thứ hai soát mù và phải khác người đầu.
  - Ca bất đồng bị giữ lại cho tới khi có trọng tài, sau đó nhãn của trọng tài thay nhãn cũ.
  - Độ đồng thuận được báo bằng kappa Cohen.
- **Nhãn của tổ chức ở lại với tổ chức.** Một triển khai cấu hình `org_id = X` chỉ thấy nhãn lõi và nhãn của X. Nhãn của X lên bộ nhớ lõi chỉ khi đội GreenScan thăng hạng nó (`core_promotion`). Nhãn không gắn tổ chức thuộc về chính triển khai đó.

Tệp QA (`qa.jsonl`, nằm cạnh `decisions.jsonl`) chỉ ghi thêm, như kho quyết định.

## Cổng thăng hạng mô hình (`registry.gate`)

Một mô hình chỉ thăng hạng được khi đủ cả năm điều kiện:
1. Có ít nhất 30 cặp giữ lại được chấm.
2. Macro-F1 không thấp hơn nhà vô địch.
3. Số `CONTRADICTS` sai (lỗi vu oan) không nhiều hơn nhà vô địch.
4. Số `SUPPORTS` sai trên cặp vàng `CONTEXT` hoặc `CONTRADICTS` (lỗi bỏ lọt) không nhiều hơn nhà vô địch.
5. Có người duyệt, và người đó khác người huấn luyện.

Mã băm trọng số được ghi khi đăng ký. Tệp trọng số bị tráo sau đó thì mô hình bị từ chối. Trọng số lưu dạng `.npz` và nạp với `allow_pickle=False`, nên nạp một mô hình không thể chạy mã.

## Cấu hình (`settings.feedback`, mặc định không ghi vào bản dump nên mã băm cấu hình không đổi)

| Trường | Mặc định | Biến môi trường |
|---|---|---|
| `precedents` | `true` | `QUANTUM_FEEDBACK_PRECEDENTS` |
| `precedent_min_similarity` / `precedent_raise_similarity` | 0,55 / 0,75 | — |
| `precedent_raise_queue` | `true` | — |
| `org_id` | `""` | `QUANTUM_FEEDBACK_ORG` |
| `active_learning_slots` | 0 (tắt) | `QUANTUM_ACTIVE_LEARNING_SLOTS` |
| `stance_examples` | 0 (tắt) | `QUANTUM_STANCE_EXAMPLES` |
| `shadow_model` | `""` | `QUANTUM_SHADOW_MODEL` |
| `local_stance_model` | `""` (chỉ nhận mô hình đã thăng hạng) | `QUANTUM_LOCAL_STANCE_MODEL` |

Khi kho quyết định rỗng, kết quả giống hệt lúc chưa có tính năng: không có khoá `precedents`, không có `manifest.feedback`. Khi có dùng kho, manifest ghi đường dẫn, số bản ghi và sha256 của kho, nên một lượt chạy có thể được đọc lại đúng như lúc chạy.

## Lệnh

```
quantum-agent feedback-bench [--update-ratchet]       # GS-Feedback + bánh cóc
quantum-agent feedback-mine [--measure --bench-limit 453]
quantum-agent feedback-qa sample|agreement
quantum-agent feedback-dataset --out .quantum/feedback/stance_pairs.jsonl
quantum-agent feedback-train --trained-by "Tên"       # đăng ký candidate kèm kết quả cổng
quantum-agent feedback-promote <model_id> --approved-by "Người khác"
```

API: `GET /v1/feedback/summary`, `GET /v1/feedback/precedents?text=…`, `GET /v1/feedback/second-review-sample`, `POST /v1/feedback/qa`, `GET /v1/feedback/proposals`. `POST /v1/reviews` nhận thêm `decisive_chunk_ids`, `decisive_quote`, `reviewer_role`, `reviewer_org`. MCP: `precedents`. Giao diện: trang **Học từ phản hồi**, mục **Tiền lệ của người soát** trong trang tuyên bố, nút **Chỉ đoạn quyết định** trong thanh quyết định.

## Giới hạn

- **Tiền lệ so theo từ**, không theo nghĩa. Hai câu cùng ý viết khác chữ sẽ không khớp. Ngược lại, câu cùng chữ khác chủ thể vẫn khớp; thẻ tiền lệ ghi "từ chung" để người soát tự đánh giá.
- **Mô hình CPU nhỏ, không có nhãn `CONTRADICTS`** trong 821 cặp Claude, nên không học được quan hệ bác bỏ. Quan hệ này chỉ đến từ nhãn chỉ chỗ của người soát.
- **GS-Feedback cần phiên gốc còn trong kho** để lấy hồ sơ kho tài liệu. Nếu không còn, ca chỉ ra được `INSUFFICIENT_EVIDENCE` khi vắng bằng chứng.
- **Máy đào chỉ đề xuất.** Ví dụ trên ca A2: cụm "chưa được phân bổ" được đề xuất, nhưng đo cho thấy chỉ thêm cụm từ thì chưa sửa được ca này, vì đoạn bằng chứng nằm trong tài liệu của chính doanh nghiệp. Sửa được nó cần đổi chính sách chốt chống vu oan, và đó là quyết định của con người.
