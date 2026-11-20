# Hướng dẫn tạo thêm ca kiểm (11/11/2026)

Tài liệu này dành cho người trong đội cần thêm dữ liệu khi một bộ bị lệch. Mọi lệnh chạy từ thư mục gốc repo.
Số đo cân bằng hiện tại: [THE_DU_LIEU_2026-11-11.md](THE_DU_LIEU_2026-11-11.md).

## 1. Khi nào phải thêm ca

Chạy `python -X utf8 benchmark/data_card.py`. Một trường nhãn bị coi là **lệch** khi có một trong hai điều sau:
- tỷ lệ giữa lớp lớn nhất và lớp nhỏ nhất vượt 3;
- lớp nhỏ nhất có dưới 20 ca. Với 20 ca, khoảng Wilson 95 % của một tỷ lệ đã rộng khoảng ±20 điểm. Ít hơn thì không nói được gì về lớp đó.

Bộ nào lệch thì phải thêm ca **trước** khi đưa số của bộ đó ra ngoài. Không được thêm ca sau khi đã thấy kết quả chỉ để số đẹp lên. Thứ tự đúng là: thêm ca, đăng ký dự đoán trong `configs/measurement_decisions.yaml`, rồi mới chạy hệ thống.

## 2. Lớp A: sinh ca đột biến có đáp án (nhanh, không cần gán nhãn)

Mỗi ca bắt đầu từ một câu sạch, có đủ chỉ số, số, kỳ, năm gốc, phạm vi và nguồn. Sau đó cấy đúng một lỗi vào câu. Vì lỗi do mình cấy, ta biết chắc ba thứ: mã vấn đề, chỗ cần sửa, và một bản sửa mẫu. Doanh nghiệp, nhà máy và đơn vị bảo đảm đều là tên hư cấu.

```bash
# toàn bộ: 40 ca mỗi mã, 120 ca sạch, 60 ca hai lỗi
python -I -X utf8 benchmark/gs_issue/gen_cases.py
# thêm ca cho một vài mã, với hạt giống khác để câu không trùng
python -I -X utf8 benchmark/gs_issue/gen_cases.py --codes ABSOLUTE_CLAIM,OFFSET_NEUTRALITY --per-code 30 --seed 7 \
       --out benchmark/gs_issue/data/extra_absolute_offset.jsonl
```

**Làm câu đa dạng hơn** (nên làm khi một hệ thống đạt gần 100 % trên lớp A, vì khi đó lớp A đã quá dễ). Sửa các danh sách ở đầu `benchmark/gs_issue/gen_cases.py`:

| Danh sách | Dùng cho | Ghi chú |
|---|---|---|
| `SECTORS` | ngành, tên doanh nghiệp, cơ sở, sản phẩm | tên phải hư cấu; đừng dùng tên doanh nghiệp niêm yết |
| `METRICS` | chỉ số môi trường | `True` nếu là khí nhà kính (cần phạm vi 1/2/3) |
| `TEMPLATES` | trật tự câu | mỗi phần gắn một ô (`period`, `baseline`, `scope`, `figure`, `source`); ô nào bỏ được thì phải đứng riêng một phần |
| `VAGUE`, `ABSOLUTE` | cụm cấy cho lỗi mơ hồ / tuyệt đối hoá | không chứa từ của mã khác |
| `CERTS`, `ISSUERS`, `SMALL_GOOD`, `MANDATORY`, `PIONEER` | các mã cần bằng chứng hoặc ngữ cảnh | `MANDATORY` chỉ gồm nghĩa vụ có căn cứ pháp luật thật |

Nguồn trích (`SOURCES`) **không được chứa năm**. Nếu có năm, người đọc sẽ suy ra được kỳ báo cáo đã bị xoá, và ca MISSING_PERIOD hết còn đúng.

**Thêm một mã vấn đề mới:**
1. Thêm mã vào `CODES` và `KIND_OK` trong `benchmark/gs_issue/taxonomy.py`. Nếu mã chồng với mã cũ thì khai báo họ trong `FAMILY`.
2. Viết hàm sinh trong `gen_cases.py`. Có hai kiểu: bỏ một ô (thêm vào `DROP_CODE`), hoặc cấy một cụm hay thêm bằng chứng (thêm vào `EVIDENCE_CODES`). Hàm sinh trả cả ca lỗi lẫn ca sạch đối chứng.
3. Khai báo cách chấm bản sửa trong `oracle`:
   - `slot`: bản sửa phải có chỗ trống mới nhắc tới ô bị thiếu, theo từ khoá ở `SLOT_WORDS`;
   - `phrase`: cụm cấy phải biến mất, hoặc có chỗ trống hỏi thêm. Thêm `forbid`, `require` hoặc `alt` khi cần.
4. Cập nhật lời nhắc trong `benchmark/gs_issue/kaggle/issue_worker.py`. Lời nhắc lấy danh sách mã từ `taxonomy.CODES`, nên thường chỉ cần dựng lại notebook.

**Tự kiểm trước khi dùng.** Lệnh dưới đây phải in `0` và `0`:
```bash
cd benchmark/gs_issue && python -X utf8 -c "
import json; from taxonomy import oracle
r=[json.loads(l) for l in open('data/layer_a.jsonl',encoding='utf-8')]
print(sum(1 for x in r if x['codes'] and not oracle(x,x['claim'],x['reference_fix'])['resolves']),   # bản sửa mẫu phải qua
      sum(1 for x in r if x['codes'] and oracle(x,x['claim'],x['claim'])['resolves']))"              # câu không sửa phải trượt
```
Sau đó đọc tận mắt 20 ca rút ngẫu nhiên. Câu nào đọc lên thấy gượng thì sửa mẫu câu, đừng giữ lại.

## 3. Lớp B: gom thêm câu thật

Câu thật cho số đáng tin hơn lớp A, nhưng phải có người gán nhãn. Có năm bước.

1. **Thêm báo cáo vào kho câu.** Phân tích báo cáo mới trên GreenScan, rồi xuất câu vào `benchmark/gs_eval_v2/inputs/pool_a.jsonl` theo cách `benchmark/gs_eval_v2/refresh_system_outputs.py` đang làm. Ưu tiên ngành và doanh nghiệp còn ít: HPG đang chiếm 40 % kho.
2. **Chọn câu theo họ vấn đề:** `python -I -X utf8 benchmark/gs_issue/build_real_pool.py`. Lệnh này bỏ câu đã có trong D-EDIT và đặt trần cho mỗi doanh nghiệp. Từ khoá chỉ dùng để chọn mẫu, không dùng làm nhãn.
3. **Hai máy đọc độc lập trên Kaggle** (Qwen3-14B-AWQ và Qwen3-32B-AWQ). Notebook nào cũng phải dưới 1 MB, nên mỗi phần không quá khoảng 500 câu:
   ```bash
   python -I -X utf8 tools/kaggle/build_nb.py benchmark/gs_issue/kaggle/nb_32b_b1.ipynb \
     --files experiments/AG-1/llm.py experiments/AG-1/multirun.py benchmark/gs_issue/kaggle/issue_worker.py \
             benchmark/gs_issue/taxonomy.py benchmark/gs_issue/kaggle/jobs_32b.json benchmark/gs_issue/kaggle/inputs/gsi_layer_b1.jsonl \
     --pip "vllm==0.32.0" --run "INPUTS=gsi_layer_b1.jsonl python -u multirun.py jobs_32b.json issue_worker.py"
   python -I -X utf8 tools/kaggle/kapi.py push benchmark/gs_issue/kaggle/nb_32b_b1.ipynb --account <tài khoản> --slug <slug mới> --gpu --internet
   ```
   Chọn tài khoản bằng `python C:/Users/ASUS/.kaggle/kquota.py --best`. Khi đẩy, ghi mốc vào `docs/RUNS.md`: mốc có log đầu và mốc dự kiến xong. Làm xong thì tải đầu ra về `benchmark/gs_issue/out/` (`kapi.py output <user>/<slug> --dest ...`).
4. **Nhãn bạc và chọn cân bằng.** `python -X utf8 benchmark/gs_issue/score_issue.py` ghi `data/layer_b_silver.jsonl`: chỉ giữ mã mà cả hai máy đều gán, hoặc câu mà cả hai đều cho là sạch. Tiếp theo, `python -X utf8 benchmark/gs_issue/select_real.py` chọn tập cân bằng. Mã nào in "THIẾU" thì quay lại bước 1 với báo cáo mới, hoặc bù tạm bằng lớp A và ghi rõ là đã bù.
5. **Người duyệt** (mục 4). Chưa qua người duyệt thì mọi số trên lớp B phải ghi là "nhãn bạc".

## 4. Người duyệt nhãn (Quỳnh gán, Thảo đọc lại)

- Mở `data/layer_b_balanced.jsonl` (hoặc bản Excel xuất từ tệp này) và đọc từng câu. Ở bước này **không** xem máy đã sửa câu thế nào.
- Với mỗi câu, giữ hoặc sửa `codes` theo bảng mã ở `benchmark/gs_eval_v2/LABELING_GUIDE.md` mục 2. Sau đó đổi `review_status` thành `human_reviewed` (giữ nguyên nhãn) hoặc `human_corrected` (có sửa), và thêm `reviewer`.
- Thảo đọc lại độc lập 25 % số câu, chọn ngẫu nhiên. Tính κ theo từng mã. Mã có κ dưới 0,70 (cổng `kappa_min`) thì hai người thống nhất lại định nghĩa trước khi gán tiếp.
- Duyệt xong thì chạy lại `score_issue.py`. Số trên phần đã duyệt mới được gọi là nhãn người.

## 5. Viết ca bằng tay

Dùng khi cần một tình huống mà bộ sinh không làm được, ví dụ một câu đọc từ vụ việc có thật. Ghi vào một tệp `benchmark/gs_issue/data/manual_*.jsonl`, mỗi dòng một ca:

```json
{"id": "M-absolute-001", "split": "A-single", "codes": ["ABSOLUTE_CLAIM"],
 "claim": "Bao bì của dòng sản phẩm X không gây bất kỳ tác hại nào cho môi trường.",
 "evidence": "", "sector": "bán lẻ", "company": "(hư cấu hoặc tên thật nếu là câu công khai có nguồn)",
 "template": "manual", "fix_kinds_ok": ["soften"],
 "reference_fix": "Bao bì của dòng sản phẩm X [bổ sung: chỉ số tác động môi trường và phương pháp đo].",
 "oracle": {"type": "phrase", "phrase": "không gây bất kỳ tác hại nào cho môi trường", "slot": "figure"},
 "span": "không gây bất kỳ tác hại nào cho môi trường", "needs_edit": true, "source_note": "ai viết, lấy từ đâu"}
```

Kiểm từng ca: bản sửa mẫu phải qua `oracle`, còn câu gốc chưa sửa phải trượt (lệnh ở mục 2). Một câu chỉ cấy **một** lỗi, trừ khi đặt `split` là `A-multi`. Mỗi ca cần thêm một câu sạch đối chứng gần giống nó, để đo được cả tỷ lệ báo nhầm.

## 6. Bù cho D-EXPLAIN và D-SCORE

`python -X utf8 benchmark/gs_issue/build_supplements.py` sinh hai tệp:
- `data/supp_explain.jsonl`: 50 ca "mâu thuẫn" và 35 ca "khớp" lấy từ GS-Bench v1. Mỗi doanh nghiệp tối đa 12 ca cho mỗi nhãn. Mỗi ca có `key_numbers` để kiểm tự động xem lời giải thích có nêu đúng số không.
- `data/supp_score_pairs.jsonl`: 80 cặp song sinh, mỗi cặp gồm một câu sạch và bản đột biến của nó. Dùng để kiểm điểm ưu tiên có tăng khi câu có lỗi hay không.

Chạy hệ thống trên hai tệp bằng `.venv/Scripts/python.exe -I -X utf8 benchmark/gs_issue/run_pipeline_supp.py`, rồi chấm bằng `python -X utf8 benchmark/gs_issue/score_supp.py`. Muốn so với mã đã commit thì giải nén mã ra một thư mục (`git archive HEAD src configs | tar -x -C <thư mục>`) và chạy với biến `GS_SRC=<thư mục>/src GS_TAG=head`.

## 7. Danh sách kiểm trước khi đưa số ra ngoài

- [ ] `data_card.py`: không còn bộ nào bị cờ "lệch" mà chưa ghi chú.
- [ ] Tự kiểm oracle in `0 0`. Đã đọc tận mắt 20 ca.
- [ ] Lớp A không có tên doanh nghiệp thật. Lớp B không trùng D-EDIT.
- [ ] Dự đoán đã đăng ký trong `configs/measurement_decisions.yaml` **trước** khi chạy hệ thống.
- [ ] Mỗi con số đều ghi rõ loại nhãn: đáp án có sẵn (lớp A), nhãn Claude, nhãn bạc hay nhãn người.
