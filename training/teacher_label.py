"""Teacher labels from a cloud model, for distillation into small local models.

Two tasks:
  claim   sentences (training/data/claim_sentences.jsonl) → one of
          QUANTIFIED_CLAIM · QUALITATIVE_CLAIM · VAGUE · NOT_CLAIM, 20 per call;
  align   claim/evidence pairs from a saved run (masked) → which evidence slot
          measures the same quantity as each claim slot (the partial-offline
          protocol of benchmark/size_ladder_2026-10-10/run_masked.py).

Rules this script enforces:
  * Only public documents (the corpus is public reports; a run's documents must
    be declared public with --public) — never internal drafts or working papers.
  * Numbers are masked before sending unless --raw is given; entity names in
    --entities are masked too.
  * Every answer is cached by (task, prompt version, model, masked input), so a
    re-run costs nothing; --max-calls caps spend; the cost estimate is printed.
  * Teacher labels are NOT gold: they train a student, and the student is judged
    on human-labelled data and the constructed cases only.

usage:
  python training/teacher_label.py claim --n 1000 [--model gemma-4-31B-it] [--max-calls 60]
  python training/teacher_label.py align --run .quantum/runs/<id> --public --entities "Tập đoàn Hòa Phát" "Dung Quất"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from quantum_gw.providers.router import ModelGateway  # noqa: E402
from training.masking import entity_patterns, mask  # noqa: E402

PROMPT_VERSION = {"claim": "teacher-claim-v1", "align": "teacher-align-v1"}
# US$ per 1M tokens (input, output) on FPT AI Marketplace, 10/2026 — for the estimate only.
PRICES = {"gemma-4-31B-it": (0.15, 0.45), "gemma-4-26B-A4B-it": (0.14, 0.40), "GLM-5.2": (1.40, 4.40)}

CLAIM_PROMPT = """Bạn gán nhãn câu trong báo cáo của doanh nghiệp niêm yết Việt Nam. Số liệu có thể đã được thay bằng mã <E1>, <E2>… (vẫn coi là có số). Với MỖI câu, chọn đúng một nhãn:
- QUANTIFIED_CLAIM: doanh nghiệp tự nói về kết quả, hiện trạng hoặc mục tiêu MÔI TRƯỜNG của mình, có số liệu kiểm chứng được (phát thải, năng lượng, nước, chất thải, tái chế, năng lượng tái tạo, tài chính xanh…).
- QUALITATIVE_CLAIM: doanh nghiệp tự nói về hành động hoặc kết quả môi trường CỤ THỂ của mình nhưng không có số liệu.
- VAGUE: khẩu hiệu, cam kết chung chung, ngôn từ quảng bá về môi trường/bền vững không kiểm chứng được.
- NOT_CLAIM: không phải tuyên bố môi trường của doanh nghiệp: giải thích kỹ thuật, bối cảnh ngành/quốc gia, tiêu đề, mục lục, câu bị cắt, nội dung xã hội, tài chính, quản trị không liên quan môi trường.

CÁC CÂU:
{items}

Trả lời đúng một mảng JSON, mỗi phần tử {{"id": "<id>", "label": "<nhãn>"}}, đủ {n} phần tử, không giải thích."""

ALIGN_PROMPT = (ROOT / "benchmark/size_ladder_2026-10-10/run_masked.py").read_text(encoding="utf-8")
ALIGN_PROMPT = ALIGN_PROMPT[ALIGN_PROMPT.index('PROMPT = """') + 12: ALIGN_PROMPT.index('"""', ALIGN_PROMPT.index('PROMPT = """') + 12)]

CACHE = ROOT / "training/data/teacher_cache.jsonl"


def _load_cache() -> dict[str, dict]:
    if not CACHE.exists():
        return {}
    out = {}
    for line in CACHE.open(encoding="utf-8"):
        rec = json.loads(line)
        out[rec["key"]] = rec
    return out


def _key(task: str, model: str, payload: str) -> str:
    return hashlib.sha256(json.dumps([PROMPT_VERSION[task], model, payload], ensure_ascii=False).encode()).hexdigest()


def _ask(provider, content: str):
    for attempt in range(3):
        try:
            return provider.generate([{"role": "user", "content": content}])
        except Exception:  # noqa: BLE001
            time.sleep(3 * (attempt + 1))
    return None


def _parse_json(text: str):
    import re
    m = re.search(r"\[.*\]|\{.*\}", text or "", flags=re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except ValueError:
        return None


def claim_task(args, provider, cache, out_fh) -> tuple[int, dict]:
    rows = [json.loads(l) for l in open(args.data, encoding="utf-8")]
    rng = random.Random(args.seed)
    strata = {
        "rule_positive": [r for r in rows if r["rule_label"] == 1],
        "env_refused_or_missed": [r for r in rows if r["rule_label"] == 0 and r["lexicon_hit"] == 1],
        "other_with_figure": [r for r in rows if r["rule_label"] == 0 and r["lexicon_hit"] == 0 and r["has_figure"] == 1],
        "other": [r for r in rows if r["rule_label"] == 0 and r["lexicon_hit"] == 0 and r["has_figure"] == 0],
    }
    share = {"rule_positive": 0.3, "env_refused_or_missed": 0.4, "other_with_figure": 0.2, "other": 0.1}
    sample = []
    for name, pool in strata.items():
        rng.shuffle(pool)
        for r in pool[: int(args.n * share[name])]:
            sample.append({**r, "stratum": name})
    batches = [sample[i:i + args.batch] for i in range(0, len(sample), args.batch)]
    calls, usage = 0, {"prompt_tokens": 0, "completion_tokens": 0}

    def work(batch):
        items, masked_text = [], {}
        for r in batch:
            text = r["text"] if args.raw else mask(r["text"], "E", entity_patterns(args.entities))[0]
            masked_text[r["id"]] = text
            items.append(f'{{"id": "{r["id"]}", "câu": {json.dumps(text, ensure_ascii=False)}}}')
        payload = "\n".join(items)
        key = _key("claim", args.model, payload)
        if key in cache:
            return batch, masked_text, cache[key], False
        resp = _ask(provider, CLAIM_PROMPT.format(items=payload, n=len(batch)))
        if resp is None:
            return batch, masked_text, None, True
        rec = {"key": key, "task": "claim", "model": args.model, "prompt_version": PROMPT_VERSION["claim"],
               "answer": _parse_json(resp.text), "usage": resp.usage}
        return batch, masked_text, rec, True

    # Cached batches cost nothing; at most --max-calls uncached batches are sent.
    todo, uncached = [], 0
    for b in batches:
        payload = "\n".join(
            f'{{"id": "{r["id"]}", "câu": {json.dumps(r["text"] if args.raw else mask(r["text"], "E", entity_patterns(args.entities))[0], ensure_ascii=False)}}}'
            for r in b)
        if _key("claim", args.model, payload) not in cache:
            if uncached >= args.max_calls:
                continue
            uncached += 1
        todo.append(b)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for batch, masked_text, rec, live in pool.map(work, todo):
            if live:
                calls += 1
                if rec is None:
                    continue
                cache[rec["key"]] = rec
                with CACHE.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                for k in usage:
                    usage[k] += int((rec.get("usage") or {}).get(k, 0) or 0)
            labels = {str(x.get("id")): x.get("label") for x in (rec or {}).get("answer") or [] if isinstance(x, dict)}
            for r in batch:
                label = labels.get(r["id"])
                if label in {"QUANTIFIED_CLAIM", "QUALITATIVE_CLAIM", "VAGUE", "NOT_CLAIM"}:
                    out_fh.write(json.dumps({**r, "sent_text": masked_text[r["id"]], "teacher_label": label,
                                             "teacher_model": args.model,
                                             "prompt_version": PROMPT_VERSION["claim"]}, ensure_ascii=False) + "\n")
    return calls, usage


def align_task(args, provider, cache, out_fh) -> tuple[int, dict]:
    if not args.public:
        raise SystemExit("align: pass --public to confirm every document of this run is published (class A).")
    result = json.loads((Path(args.run) / "result.json").read_text(encoding="utf-8"))
    entities = entity_patterns(args.entities)
    pairs = []
    for v in result["verifications"]:
        claim = v["claim"]["text"]
        mclaim, cslots = mask(claim, "S", entities)
        if not cslots:
            continue
        for e in v["evidence"][: args.per_claim]:
            ev = (e.get("chunk") or e).get("text") or ""
            mev, eslots = mask(ev, "E", entities)
            if eslots:
                pairs.append((v["claim"]["claim_id"], claim, mclaim, cslots, ev, mev, eslots))
    calls, usage = 0, {"prompt_tokens": 0, "completion_tokens": 0}

    def work(p):
        cid, claim, mclaim, cslots, ev, mev, eslots = p
        content = ALIGN_PROMPT.format(claim=mclaim, evidence=mev)
        key = _key("align", args.model, content)
        if key in cache:
            return p, cache[key], False
        resp = _ask(provider, content)
        if resp is None:
            return p, None, True
        return p, {"key": key, "task": "align", "model": args.model, "prompt_version": PROMPT_VERSION["align"],
                   "answer": _parse_json(resp.text), "usage": resp.usage}, True

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for p, rec, live in pool.map(work, pairs[: args.max_calls] if args.max_calls else pairs):
            if live:
                calls += 1
                if rec is None:
                    continue
                cache[rec["key"]] = rec
                with CACHE.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                for k in usage:
                    usage[k] += int((rec.get("usage") or {}).get(k, 0) or 0)
            cid, claim, mclaim, cslots, ev, mev, eslots = p
            ans = (rec or {}).get("answer") or {}
            out_fh.write(json.dumps({"claim_id": cid, "sent_claim": mclaim, "sent_evidence": mev,
                                     "claim_slots": cslots, "evidence_slots": eslots,
                                     "mappings": ans.get("mappings") if isinstance(ans, dict) else None,
                                     "teacher_model": args.model, "prompt_version": PROMPT_VERSION["align"],
                                     "run": str(args.run)}, ensure_ascii=False) + "\n")
    return calls, usage


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("task", choices=["claim", "align"])
    ap.add_argument("--model", default="gemma-4-31B-it")
    ap.add_argument("--data", default=str(ROOT / "training/data/claim_sentences.jsonl"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--n", type=int, default=1000, help="claim: sentences to label")
    ap.add_argument("--batch", type=int, default=20, help="claim: sentences per call")
    ap.add_argument("--run", help="align: a saved run directory")
    ap.add_argument("--per-claim", type=int, default=3, help="align: evidence passages per claim")
    ap.add_argument("--public", action="store_true", help="align: the run's documents are published")
    ap.add_argument("--entities", nargs="*", default=[], help="names to mask: entity first, then sites")
    ap.add_argument("--raw", action="store_true", help="claim: send unmasked sentences (public corpus only)")
    ap.add_argument("--max-calls", type=int, default=60)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    out = Path(args.out or ROOT / f"training/data/teacher_{args.task}_{args.model}.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    provider = ModelGateway()._provider("fpt").bind_model(args.model)
    cache = _load_cache()
    t0 = time.time()
    with out.open("w", encoding="utf-8") as fh:
        calls, usage = (claim_task if args.task == "claim" else align_task)(args, provider, cache, fh)
    p_in, p_out = PRICES.get(args.model, (0.0, 0.0))
    cost = usage["prompt_tokens"] / 1e6 * p_in + usage["completion_tokens"] / 1e6 * p_out
    lines = sum(1 for _ in out.open(encoding="utf-8"))
    print(f"{args.task}: {lines} labelled rows → {out}")
    print(f"live calls {calls} (cap {args.max_calls}), tokens in/out {usage['prompt_tokens']}/{usage['completion_tokens']}, "
          f"≈ US${cost:.3f}, {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
