"""AG-1 worker: one local LLM reads every claim and evidence text of GS-Bench v1 into IR figures; irlib decides.

    python -u ag1_worker.py --job '{"tag": "q3-4b-inst", "repo": "Qwen/Qwen3-4B-Instruct-2507", "tp": 1, "max_len": 4096}'

Runs inside a Kaggle notebook built by build_nb.py (files embedded next to it: llm.py from ZAIC Experiment/common,
irlib.py, gs_bench_v1.jsonl). Greedy, thinking off. The model only fills the IR; S / C / N comes from irlib.decide
(arithmetic by code, invariant 5). Output: out/<tag>_texts.jsonl (raw + parsed figures per unique text) and
out/<tag>_cases.jsonl (verdict per case), plus a one-line summary in the log.
Env: LIMIT=n (first n cases, smoke), MAX_TOKENS (default 768).
"""
import argparse, hashlib, json, os, re, time
from pathlib import Path

from irlib import IR, METRICS, SCOPES, VALUE_KINDS, decide

PROMPT = """Bạn trích số liệu môi trường từ MỘT câu trong báo cáo của doanh nghiệp Việt Nam.
Với MỖI con số mô tả một chỉ số môi trường (không lấy số năm, số điều luật, số thứ tự, số tiền), trả về một đối tượng:
- "metric": một mã trong {metrics}
- "metric_text": cụm từ gọi tên chỉ số, chép NGUYÊN VĂN từ câu
- "value_text": con số, chép NGUYÊN VĂN từ câu (giữ dấu chấm, phẩy), không kèm chữ
- "multiplier_text": "nghìn", "triệu", "tỷ" nếu câu viết chữ đó ngay sau số, ngược lại ""
- "unit_text": đơn vị nguyên văn (vd "tCO2e", "kWh", "m3", "tấn", "%", "tCO2e/tấn sản phẩm"); "" nếu không có
- "value_kind": một trong {kinds} (share = tỷ lệ phần trăm của một tổng; change = mức tăng/giảm so với kỳ trước hoặc năm gốc; intensity = trên một đơn vị sản phẩm/doanh thu)
- "change_direction": "decrease" | "increase" | null (chỉ khi value_kind = change)
- "baseline_year": năm gốc nếu là change và câu có nêu, ngược lại null
- "period": năm của số liệu nếu câu NÊU RÕ; null nếu câu không nêu
- "status": "actual" (đã thực hiện) | "target" (mục tiêu, kế hoạch, cam kết)
- "scope": một trong {scopes} nếu là phát thải khí nhà kính và câu nêu phạm vi, ngược lại null
- "boundary": "group" (tập đoàn, hợp nhất) | "parent" (công ty mẹ) | "facility" (nhà máy, cơ sở cụ thể) | "unspecified"
Câu không có số liệu môi trường thì trả về danh sách rỗng.

CÂU: {sentence}

Chỉ trả lời đúng một đối tượng JSON: {{"figures": [ ... ]}}"""


def parse(text):
    """First JSON object in the reply; None when there is none."""
    if not text:
        return None
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M)
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            if depth == 0:
                try:
                    obj = json.loads(text[start:i + 1])
                    return obj if isinstance(obj, dict) else None
                except json.JSONDecodeError:
                    break
        start = text.find("{", start + 1)
    return None


def to_irs(figures):
    out = []
    for f in figures or []:
        if isinstance(f, dict) and f.get("value_text") not in (None, ""):
            try:
                ir = IR.from_dict({**f, "value_text": str(f["value_text"])})
                ir.quantity()  # unreadable number -> dropped
                out.append(ir)
            except (TypeError, ValueError):
                pass
    return out


def verdict(claim_irs, ev_irs):
    if not claim_irs:
        return "N", ["không đọc được số liệu trong tuyên bố"]
    labels, why = [], []
    for c in claim_irs:
        label, steps = decide(c, ev_irs)
        labels.append(label)
        why.append(f"{c.value_text} {c.unit_text}: {label} " + "; ".join(s[1] for s in steps)[:300])
    if "C" in labels:
        return "C", why
    return ("S" if all(x == "S" for x in labels) else "N"), why


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--job")
    job = json.loads(ap.parse_args().job)
    tag = job["tag"]
    cases = [json.loads(line) for line in open("gs_bench_v1.jsonl", encoding="utf-8")]
    if os.environ.get("LIMIT"):
        cases = cases[: int(os.environ["LIMIT"])]
    texts = {}
    for c in cases:
        for t in (c["claim"], c["evidence"]):
            texts.setdefault(hashlib.sha1(t.encode()).hexdigest()[:16], t)
    for path in filter(None, os.environ.get("EXTRA_INPUT", "").split(",")):  # more sentences to read, no cases (second reader)
        for r in map(json.loads, open(path, encoding="utf-8")):
            texts.setdefault(hashlib.sha1(r["text"].encode()).hexdigest()[:16], r["text"])
    print(f"[{tag}] {len(cases)} cases, {len(texts)} unique texts, repo {job['repo']}", flush=True)
    from llm import LLM
    t0 = time.time()
    m = LLM(job["repo"], max_len=job.get("max_len", 4096), tp=job.get("tp", 1), **job.get("kw", {}))
    load_s = time.time() - t0
    keys = list(texts)
    prompts = [[{"role": "user", "content": PROMPT.format(metrics=list(METRICS), kinds=list(VALUE_KINDS), scopes=list(SCOPES),
                                                         sentence=texts[k])}] for k in keys]
    t1 = time.time()
    raw = []
    for i in range(0, len(prompts), 64):
        raw += m.gen(prompts[i:i + 64], max_tokens=int(os.environ.get("MAX_TOKENS", "768")))
        print(f"[{tag}] generated {len(raw)}/{len(prompts)}", flush=True)
    gen_s = time.time() - t1
    Path("out").mkdir(exist_ok=True)
    irs, bad = {}, 0
    with open(f"out/{tag}_texts.jsonl", "w", encoding="utf-8") as fh:
        for k, r in zip(keys, raw):
            obj = parse(r)
            bad += obj is None
            figs = (obj or {}).get("figures") if isinstance((obj or {}).get("figures"), list) else []
            irs[k] = to_irs(figs)
            fh.write(json.dumps({"key": k, "text": texts[k], "raw": r, "figures": [x.as_dict() for x in irs[k]]}, ensure_ascii=False) + "\n")
    right = 0
    with open(f"out/{tag}_cases.jsonl", "w", encoding="utf-8") as fh:
        for c in cases:
            kc, ke = (hashlib.sha1(t.encode()).hexdigest()[:16] for t in (c["claim"], c["evidence"]))
            label, why = verdict(irs[kc], irs[ke])
            right += label in c["labels"]
            fh.write(json.dumps({"id": c["id"], "label": label, "why": why}, ensure_ascii=False) + "\n")
    summary = {"tag": tag, "repo": job["repo"], "cases": len(cases), "right": right, "unparsed_texts": bad,
               "load_s": round(load_s), "gen_s": round(gen_s), "ntok_in": getattr(m, "ntok_in", None), "ntok_out": getattr(m, "ntok_out", None)}
    json.dump(summary, open(f"out/{tag}_summary.json", "w"), ensure_ascii=False)
    print(f"[{tag}] SUMMARY {json.dumps(summary, ensure_ascii=False)}", flush=True)


if __name__ == "__main__":
    main()
