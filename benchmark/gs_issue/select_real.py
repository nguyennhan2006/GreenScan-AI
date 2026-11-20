"""Chọn tập câu thật CÂN BẰNG từ nhãn bạc của lớp B (data/layer_b_silver.jsonl, do score_issue.py ghi).

    python -X utf8 benchmark/gs_issue/select_real.py [--per-code 40] [--clean 80] [--per-company-share 0.35]

Mỗi mã lấy tối đa --per-code câu có mã đó (ưu tiên câu một mã), cộng --clean câu sạch; không doanh nghiệp nào quá
--per-company-share của tập. Mã nào chưa đủ --min câu thì in "THIẾU" và gợi ý lệnh sinh thêm (lớp A) hoặc cách gom
thêm câu thật (docs/04-data-ai/HUONG_DAN_TAO_THEM_CASE.md, mục 3).
Ra: data/layer_b_balanced.jsonl (review_status: pending_human_review) + bảng đếm.
"""
import argparse
import json
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-code", type=int, default=40)
    ap.add_argument("--clean", type=int, default=80)
    ap.add_argument("--min", type=int, default=20)
    ap.add_argument("--per-company-share", type=float, default=0.35)
    ap.add_argument("--seed", type=int, default=20261111)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    rows = [json.loads(line) for line in open(HERE / "data/layer_b_silver.jsonl", encoding="utf-8")]
    rng.shuffle(rows)
    rows.sort(key=lambda r: len(r["codes"]) or 99)  # single-code sentences first, clean last
    counts = Counter(c for r in rows for c in r["codes"])
    cap_total = a.per_code * len(counts) + a.clean
    per_co_cap = max(10, int(a.per_company_share * cap_total))
    take, got, per_co = {}, Counter(), Counter()
    for code in sorted(counts, key=lambda c: counts[c]):  # rarest first
        for r in rows:
            if got[code] >= a.per_code:
                break
            if code in r["codes"] and r["id"] not in take and per_co[r["company"]] < per_co_cap:
                take[r["id"]] = r
                per_co[r["company"]] += 1
                for c in r["codes"]:
                    got[c] += 1
    n_clean = 0
    for r in rows:
        if n_clean >= a.clean:
            break
        if not r["codes"] and r["id"] not in take and per_co[r["company"]] < per_co_cap:
            take[r["id"]] = r
            per_co[r["company"]] += 1
            n_clean += 1
    with open(HERE / "data/layer_b_balanced.jsonl", "w", encoding="utf-8") as fh:
        for r in take.values():
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)} silver -> {len(take)} chosen ({n_clean} clean); per company {dict(per_co.most_common())}")
    for code, n in sorted(got.items(), key=lambda x: x[1]):
        flag = "THIẾU" if n < a.min else "đủ"
        print(f"  {code:26s} {n:4d}  {flag}  (có trong nhãn bạc: {counts[code]})")
        if n < a.min:
            print(f"      -> lớp A: python -I -X utf8 benchmark/gs_issue/gen_cases.py --codes {code} --per-code {a.per_code} "
                  f"--seed 7 --out benchmark/gs_issue/data/extra_{code.lower()}.jsonl ; câu thật: HUONG_DAN_TAO_THEM_CASE.md mục 3")


if __name__ == "__main__":
    main()
