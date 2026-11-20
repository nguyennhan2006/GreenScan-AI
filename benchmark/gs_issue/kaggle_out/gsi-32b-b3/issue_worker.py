"""GS-Issue worker: one local LLM finds the issues of each claim and proposes edits (same prompt for every model).

    INPUTS=layer_a.jsonl,d_edit.jsonl python -u issue_worker.py --job '{"tag": "q3-4b", "repo": "Qwen/Qwen3-4B-Instruct-2507", "tp": 1}'

Runs inside a Kaggle notebook built by tools/kaggle/build_nb.py with llm.py and multirun.py of experiments/AG-1.
Greedy, thinking off. Input rows: {id, claim, evidence}. Output: out/<tag>__<input stem>.jsonl, one row per input row:
{id, raw, parsed (or null)}; out/<tag>_summary.json. Env: LIMIT=n (first n rows of each input, smoke), MAX_TOKENS (900).
The prompt is the D-EDIT labelling guide (benchmark/gs_eval_v2/LABELING_GUIDE.md section 2), shortened; the taxonomy
is benchmark/gs_issue/taxonomy.py (embedded next to this file).
"""
import argparse
import json
import os
import re
import time
from pathlib import Path

from taxonomy import CODES, KINDS

SYSTEM = "Bạn là kiểm toán viên soát xét tuyên bố môi trường trong báo cáo của doanh nghiệp Việt Nam. Bạn chỉ trả lời bằng JSON."
PROMPT = """Đọc TUYÊN BỐ (và BẰNG CHỨNG nếu có). Tìm các vấn đề khiến tuyên bố có thể gây hiểu nhầm, rồi đề xuất sửa.

Mã vấn đề (chỉ dùng các mã này):
{codes}

Bốn loại sửa được phép:
{kinds}

Quy tắc:
- Chỉ nêu vấn đề có thật trong câu; câu đã đủ chỉ số, số, kỳ, năm gốc, phạm vi, nguồn và không nói quá thì "issues": [].
- Câu không phải tuyên bố môi trường (tiêu đề, mục lục, câu tài chính, định nghĩa) thì "is_green_claim": false và không sửa.
- BẰNG CHỨNG chỉ để hiểu bối cảnh (ví dụ: tổng phát thải thật ra tăng, số của công ty mẹ khác số hợp nhất, mục tiêu chưa đạt).
- Không thêm bất kỳ con số nào không có trong tuyên bố. Thông tin chưa biết thì viết chỗ trống "[bổ sung: ...]".
- Không đổi nghĩa, không biến mục tiêu thành thành tích, không xoá thông tin đúng.
- "span" và "target_span" chép NGUYÊN VĂN một đoạn của tuyên bố.

TUYÊN BỐ: {claim}
BẰNG CHỨNG: {evidence}

Trả lời đúng một đối tượng JSON:
{{"is_green_claim": true, "issues": [{{"code": "...", "span": "..."}}], "edits": [{{"kind": "...", "rule_code": "...", "target_span": "...", "replacement": "..."}}], "rewritten_claim": "tuyên bố sau khi áp mọi sửa"}}"""


def parse(text):
    if not text:
        return None
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M)
    start = text.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                esc = (ch == "\\" and not esc)
                if ch == '"' and not esc:
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            depth += {"{": 1, "}": -1}.get(ch, 0)
            if depth == 0:
                try:
                    obj = json.loads(text[start:i + 1])
                    return obj if isinstance(obj, dict) else None
                except json.JSONDecodeError:
                    break
        start = text.find("{", start + 1)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job")
    job = json.loads(ap.parse_args().job)
    tag = job["tag"]
    inputs = [p for p in os.environ.get("INPUTS", "").split(",") if p]
    rows = []
    for path in inputs:
        part = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
        if os.environ.get("LIMIT"):
            part = part[: int(os.environ["LIMIT"])]
        rows += [(Path(path).stem, r) for r in part]
    print(f"[{tag}] {len(rows)} rows from {inputs}, repo {job['repo']}", flush=True)
    from llm import LLM
    t0 = time.time()
    m = LLM(job["repo"], max_len=job.get("max_len", 4096), tp=job.get("tp", 1), **job.get("kw", {}))
    load_s = time.time() - t0
    codes = "\n".join(f"- {k}: {v}" for k, v in CODES.items())
    kinds = "\n".join(f"- {k}: {v}" for k, v in KINDS.items())
    prompts = [[{"role": "system", "content": SYSTEM},
                {"role": "user", "content": PROMPT.format(codes=codes, kinds=kinds, claim=r["claim"],
                                                          evidence=(r.get("evidence") or "(không có)")[:900])}] for _, r in rows]
    t1 = time.time()
    raw = []
    for i in range(0, len(prompts), 64):
        raw += m.gen(prompts[i:i + 64], max_tokens=int(os.environ.get("MAX_TOKENS", "900")))
        print(f"[{tag}] generated {len(raw)}/{len(prompts)} ({time.time() - t1:.0f}s)", flush=True)
    gen_s = time.time() - t1
    Path("out").mkdir(exist_ok=True)
    bad, files = 0, {}
    for (stem, r), text in zip(rows, raw):
        obj = parse(text)
        bad += obj is None
        files.setdefault(stem, []).append({"id": r["id"], "raw": text, "parsed": obj})
    for stem, out in files.items():
        with open(f"out/{tag}__{stem}.jsonl", "w", encoding="utf-8") as fh:
            for o in out:
                fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    summary = {"tag": tag, "repo": job["repo"], "rows": len(rows), "unparsed": bad, "load_s": round(load_s), "gen_s": round(gen_s),
               "ntok_in": getattr(m, "ntok_in", None), "ntok_out": getattr(m, "ntok_out", None), "overflow": getattr(m, "overflow", None)}
    json.dump(summary, open(f"out/{tag}_summary.json", "w"), ensure_ascii=False)
    print(f"[{tag}] SUMMARY {json.dumps(summary, ensure_ascii=False)}", flush=True)


if __name__ == "__main__":
    main()
