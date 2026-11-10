"""GS-Bench v1, step 1: IR of every figure in real environmental sentences, read by two cloud models.

Sentences: Vietnamese sentences of training/data/claim_sentences.jsonl (public annual / sustainability
reports) that carry a figure, an environmental lexicon hit and a unit; at most CAP per company.
Two models of different families (gemma-4-31B-it, GLM-5.2 on FPT; Vietnam region) read each sentence
independently. Public documents only; nothing is masked because the figures are the object of study
(user decision 31/10: cloud allowed for public reports, US$5 cap). Calls are cached and their token
usage is logged, so a re-run costs nothing.

usage (repository root): .venv/Scripts/python.exe benchmark/gs_bench_v1/extract_ir.py [--limit N]
"""
from __future__ import annotations

import argparse, hashlib, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from irlib import BOUNDARIES, METRICS, SCOPES, STATUSES, VALUE_KINDS  # noqa: E402

from quantum_gw.providers.router import ModelGateway  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
SOURCE = Path("training/data/claim_sentences.jsonl")
CACHE = HERE / "cache_ir.jsonl"
MODELS = ("gemma-4-31B-it", "GLM-5.2")
PRICE = {"gemma-4-31B-it": (0.15, 0.45), "GLM-5.2": (1.40, 4.40)}  # US$ per million tokens in / out (routing.yaml)
CAP = 40
VI = re.compile("[ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", re.I)
UNIT = re.compile(r"(tCO2|CO2e|kWh|MWh|GWh|TOE|m3|m³|tấn|kg|%|lít|MW)", re.I)

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
- "period": năm của số liệu nếu câu NÊU RÕ; null nếu câu không nêu (không đoán từ ngữ cảnh)
- "status": "actual" (đã thực hiện) | "target" (mục tiêu, kế hoạch, cam kết)
- "scope": một trong {scopes} nếu là phát thải khí nhà kính và câu nêu phạm vi, ngược lại null
- "boundary": "group" (tập đoàn, hợp nhất) | "parent" (công ty mẹ) | "facility" (nhà máy, cơ sở, chi nhánh cụ thể) | "unspecified"
- "subject_text": chủ thể nguyên văn (vd "Công ty", "Nhà máy Dung Quất"); "" nếu không có
Câu không có số liệu môi trường thì trả về danh sách rỗng.

CÂU: {sentence}

Trả lời đúng một đối tượng JSON: {{"figures": [ ... ]}}"""


def candidates() -> list[dict]:
    rows = [json.loads(line) for line in SOURCE.open(encoding="utf-8")]
    keep = [r for r in rows if r["has_figure"] and r["lexicon_hit"] and VI.search(r["text"]) and UNIT.search(r["text"])
            and 40 <= len(r["text"]) <= 350]
    keep.sort(key=lambda r: hashlib.sha1(r["id"].encode()).hexdigest())  # fixed, content-independent order
    per, out = {}, []
    for r in keep:
        if per.get(r["company_id"], 0) < CAP:
            per[r["company_id"]] = per.get(r["company_id"], 0) + 1
            out.append(r)
    return out


def load_cache() -> dict:
    if not CACHE.exists():
        return {}
    return {(c["id"], c["model"]): c for c in map(json.loads, CACHE.open(encoding="utf-8"))}


def call(provider, model: str, row: dict) -> dict:
    prompt = PROMPT.format(metrics=list(METRICS), kinds=list(VALUE_KINDS), scopes=list(SCOPES), sentence=row["text"])
    err = ""
    for attempt in range(3):
        try:
            t = time.time()
            resp = provider.generate([{"role": "user", "content": prompt}], response_schema={"type": "object"})
            figures = (resp.parsed or {}).get("figures")
            if not isinstance(figures, list):
                raise ValueError(f"no figures list: {resp.text[:120]!r}")
            return {"id": row["id"], "model": model, "figures": figures, "usage": resp.usage, "seconds": round(time.time() - t, 1)}
        except Exception as exc:  # noqa: BLE001
            err = repr(exc)[:200]
            time.sleep(4 * (attempt + 1))
    return {"id": row["id"], "model": model, "figures": None, "error": err}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    rows = candidates()[: args.limit or None]
    cache = load_cache()
    fpt = ModelGateway()._provider("fpt")
    todo = [(m, r) for m in MODELS for r in rows if (r["id"], m) not in cache or cache[(r["id"], m)].get("figures") is None]
    print(f"[ir] {len(rows)} sentences, {len(todo)} calls to make", flush=True)
    with ThreadPoolExecutor(4) as pool, CACHE.open("a", encoding="utf-8") as fh:
        for i, rec in enumerate(pool.map(lambda mr: call(fpt.bind_model(mr[0]), mr[0], mr[1]), todo), 1):
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            if i % 25 == 0:
                print(f"[ir] {i}/{len(todo)}", flush=True)
    cache = load_cache()
    cost, tokens = 0.0, {}
    for (_, model), rec in cache.items():
        u = rec.get("usage") or {}
        pin, pout = u.get("prompt_tokens", 0), u.get("completion_tokens", 0)
        tokens[model] = [a + b for a, b in zip(tokens.get(model, [0, 0]), (pin, pout))]
        cost += (pin * PRICE[model][0] + pout * PRICE[model][1]) / 1e6
    failed = sum(1 for rec in cache.values() if rec.get("figures") is None)
    print(f"[ir] cached {len(cache)} calls, failed {failed}, tokens {tokens}, cost US${cost:.3f}", flush=True)


if __name__ == "__main__":
    os.environ.setdefault("QUANTUM_PROFILE", "cloud")
    main()
