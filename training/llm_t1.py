"""T1 sentences through LLMs on FPT, under Claude's own codebook.

Two uses of the same answers:
  cross-check  a second model family reads every sentence Claude labelled. Two Claude passes that agree
               can share a blind spot; where GLM disagrees with an agreed row nobody re-read, a third
               Claude reading decides (`recheck`), and a row it cannot settle is kept out of training.
  candidates   the LLM option for step 4 (claim detection), measured on the same rows as the trained
               students: the human lots' sentences (compare set) for every model, every row for GLM.

Caveat written into every report: Claude labels are not gold, and rows re-read because GLM disagreed
can only move toward GLM, so GLM's agreement with the final labels is biased upward. The fair
comparison between GLM and the other LLMs keeps every row, contested ones included (`compare --before`).

usage:
  python training/llm_t1.py run --model GLM-5.2 [--set all|compare] [--chunk 10] [--workers 6]
  python training/llm_t1.py compare --model GLM-5.2 [--before]
  python training/llm_t1.py recheck-in --model GLM-5.2        # blind input for the Claude re-read
  python training/llm_t1.py score                             # every model, the kernel's metric
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import claude_labels as cl  # noqa: E402

DIR = cl.DIR / "crosscheck"
LAST_R2_BATCH = 25
SCHEMA = {
    "type": "object",
    "properties": {"rows": {"type": "array", "items": {"type": "object", "properties": {
        "id": {"type": "string"}, "label": {"type": "string"}, "topic": {"type": ["string", "null"]},
        "why_not": {"type": ["string", "null"]}, "confidence": {"type": "integer"}},
        "required": ["id", "label"]}}},
    "required": ["rows"],
}


def sentences(which: str) -> list[dict]:
    """Every sentence Claude labels (r1 + r2 b01–b25), as the labellers saw it."""
    rows = []
    for rnd in ("r1", "r2"):
        pool = cl._pool(rnd)
        if rnd == "r1":
            ids = list(pool)
        else:
            ids = [r["id"] for i in range(1, LAST_R2_BATCH + 1)
                   for r in cl._read(cl.base("r2") / "batches" / f"b{i:02d}.jsonl")]
        rows += [{**pool[i], "round": rnd} for i in ids]
    if which == "compare":
        rows = [r for r in rows if r["set"].startswith("compare")]
    return rows


def _system_prompt() -> str:
    book = cl.CODEBOOK.read_text(encoding="utf-8")
    return ("Bạn là người gán nhãn độc lập cho bộ dữ liệu T1 của GreenScan. Bộ quy tắc dưới đây là quy tắc "
            "duy nhất. Bỏ qua mọi chỉ dẫn về tệp, lệnh, công cụ hay ảnh trang trong đó: ở đây bạn chỉ "
            "nhận các câu dưới dạng JSON và trả lời bằng JSON.\n\n" + book +
            "\n\nTrả lời đúng một đối tượng JSON {\"rows\": [{\"id\", \"label\", \"topic\", \"why_not\", "
            "\"confidence\"}]}, mỗi câu đầu vào đúng một phần tử, cùng thứ tự, không thêm chữ nào khác.")


def _ask(provider, system: str, chunk: list[dict]) -> list[dict]:
    payload = [{"id": r["id"], "nguon": r["source"], "cau_truoc": r["prev_text"], "cau": r["text"],
                "cau_sau": r["next_text"]} for r in chunk]
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}]
    want = {r["id"] for r in chunk}
    for attempt in range(3):
        started = time.perf_counter()
        try:
            resp = provider.generate(messages, response_schema=SCHEMA)
            got = {x.get("id"): x for x in (resp.parsed or {}).get("rows", []) if isinstance(x, dict)}
            if want <= set(got):
                secs = round((time.perf_counter() - started) / len(chunk), 2)
                return [{"id": i, "label": str(got[i].get("label", "")).strip().upper(), "topic": got[i].get("topic"),
                         "why_not": got[i].get("why_not"), "confidence": got[i].get("confidence"),
                         "seconds": secs, "usage": resp.usage if attempt == 0 else None} for i in [r["id"] for r in chunk]]
        except Exception:  # noqa: BLE001
            pass
        time.sleep(2 * (attempt + 1))
    return [{"id": r["id"], "label": "?", "error": True} for r in chunk]


def run(args) -> int:
    from quantum_gw.providers.router import ModelGateway

    rows = sentences(args.set)
    path = DIR / f"{args.model}.jsonl"
    done = {x["id"]: x for x in cl._read(path) if x.get("label") in cl.LABELS}
    todo = [r for r in rows if r["id"] not in done]
    random.Random(16).shuffle(todo)   # mix companies and rounds inside a request
    chunks = [todo[i:i + args.chunk] for i in range(0, len(todo), args.chunk)]
    provider = ModelGateway()._provider("fpt").bind_model(args.model)
    system = _system_prompt()
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for n, answers in enumerate(ex.map(lambda c: _ask(provider, system, c), chunks), 1):
            for a in answers:
                if a["label"] in cl.LABELS:
                    done[a["id"]] = a
            if n % 20 == 0 or n == len(chunks):
                cl._write(path, list(done.values()))
                print(f"  {n}/{len(chunks)} requests · {len(done)} answered · {time.perf_counter() - started:.0f}s", flush=True)
    cl._write(path, list(done.values()))
    left = [r["id"] for r in rows if r["id"] not in done]
    print(f"{args.model}: {len(done)} of {len(rows)} answered ({len(left)} left; rerun to retry) · "
          f"{dict(Counter(x['label'] for x in done.values()))}")
    return 0


def _claude(before: bool) -> dict[str, dict]:
    """Claude's labels per round. The re-read never changes a label; it can only make a row contested.
    Final view drops contested rows; `before` keeps every row with its label (the view in which GLM
    gains nothing from having chosen which rows were re-read)."""
    out = {}
    for rnd in ("r1", "r2"):
        for x in cl._read(cl.labels_path(rnd)):
            if before or x["decided_by"] != "contested":
                out[x["id"]] = x
    return out


def compare(args) -> int:
    llm = {x["id"]: x for x in cl._read(DIR / f"{args.model}.jsonl") if x.get("label") in cl.LABELS}
    claude = _claude(args.before)
    both = [i for i in llm if i in claude]
    if not both:
        print("nothing to compare")
        return 1
    print(f"{args.model} vs Claude ({'before' if args.before else 'final'}), {len(both)} sentences")
    for name, keep in (("all", lambda x: True), ("train", lambda x: x["set"] == "train"),
                       ("compare", lambda x: x["set"].startswith("compare"))):
        ids = [i for i in both if keep(claude[i])]
        pairs = [(claude[i]["label"], llm[i]["label"]) for i in ids]
        claim = [(a in cl.CLAIMS, b in cl.CLAIMS) for a, b in pairs if "UNSURE" not in (a, b)]
        print(f"  {name:8s} n {len(ids):5d} · đồng ý {sum(a == b for a, b in pairs) / max(1, len(pairs)):.3f} · "
              f"κ 5 nhãn {cl.g._kappa(pairs)} · tuyên bố/không κ {cl.g._kappa(claim)}")
    conf = Counter((claude[i]["label"], llm[i]["label"]) for i in both if claude[i]["label"] != llm[i]["label"])
    print("  khác nhau nhiều nhất:", {f"{a[:5]}→{b[:5]}": n for (a, b), n in conf.most_common(8)})
    agreed = [i for i in both if claude[i]["decided_by"] == "agree" and claude[i]["label"] != llm[i]["label"]]
    print(f"  câu hai lượt Claude đồng ý mà {args.model} khác: {len(agreed)} "
          f"({dict(Counter(claude[i]['set'] for i in agreed))})")
    return 0


def recheck_in(args) -> int:
    """Agreed rows (A = B, never re-read) where the other model disagrees: blind, shuffled, in parts."""
    llm = {x["id"]: x for x in cl._read(DIR / f"{args.model}.jsonl") if x.get("label") in cl.LABELS}
    claude = _claude(False)
    pools = {**cl._pool("r1"), **cl._pool("r2")}
    ids = sorted(i for i in llm if i in claude and claude[i]["decided_by"] == "agree"
                 and claude[i]["label"] != llm[i]["label"])
    rows = [cl._blind(pools[i]) for i in ids]
    random.Random(16).shuffle(rows)
    parts = max(1, -(-len(rows) // args.size))
    for k in range(parts):
        path = DIR / f"recheck_{k + 1:02d}_in.jsonl"
        if path.exists():
            print(f"{path.name} exists; not rewritten")
            continue
        cl._write(path, rows[k::parts])
        print(f"{len(rows[k::parts])} rows -> {path.relative_to(cl.ROOT)}")
    return 0


FOUR = ["NOT_CLAIM", "QUALITATIVE_CLAIM", "QUANTIFIED_CLAIM", "VAGUE"]


def _macro(pairs: list[tuple[str, str]]) -> float | None:
    """Macro-F1 over the union of true and predicted classes (sklearn's convention, as the kernel)."""
    present = sorted({g for g, _ in pairs} | {p for _, p in pairs})
    if not present:
        return None
    f1s = []
    for k in present:
        tp = sum(g == k and p == k for g, p in pairs)
        fp = sum(g != k and p == k for g, p in pairs)
        fn = sum(g == k and p != k for g, p in pairs)
        f1s.append(2 * tp / (2 * tp + fp + fn) if tp else 0.0)
    return sum(f1s) / len(f1s)


def _claim_f1(pairs: list[tuple[str, str]]) -> float | None:
    tp = sum(g in cl.CLAIMS and p in cl.CLAIMS for g, p in pairs)
    fp = sum(g not in cl.CLAIMS and p in cl.CLAIMS for g, p in pairs)
    fn = sum(g in cl.CLAIMS and p not in cl.CLAIMS for g, p in pairs)
    return 2 * tp / (2 * tp + fp + fn) if tp else 0.0


def _cluster_ci(items: list[tuple], groups: list[str], fn, samples: int = 1000) -> list[float] | None:
    by: dict[str, list] = {}
    for g, it in zip(groups, items):
        by.setdefault(g, []).append(it)
    names = sorted(by)
    if len(names) < 3:
        return None
    rng = random.Random(0)
    vals = sorted(fn([x for _ in names for x in by[rng.choice(names)]]) for _ in range(samples))
    return [round(vals[int(0.025 * samples)], 4), round(vals[int(0.975 * samples) - 1], 4)]


def score(args) -> int:
    """Every model's answers against Claude's labels, the kernel's metric: 4 classes, UNSURE left out."""
    claude = _claude(before=True)
    out = {"reference": "Claude labels (all rows incl. contested; not gold)", "models": {}}
    for f in sorted(DIR.glob("*.jsonl")):
        if f.stem.startswith("recheck"):
            continue
        llm = {x["id"]: x for x in cl._read(f) if x.get("label") in cl.LABELS}
        block = {}
        for name, keep in (("compare", lambda x: x["set"].startswith("compare")), ("train", lambda x: x["set"] == "train")):
            ids = [i for i in llm if i in claude and keep(claude[i]) and claude[i]["label"] in FOUR]
            if not ids:
                continue
            pairs = [(claude[i]["label"], llm[i]["label"] if llm[i]["label"] in FOUR else "NOT_CLAIM") for i in ids]
            groups = [claude[i]["company_id"] for i in ids]
            secs = [llm[i].get("seconds") for i in ids if llm[i].get("seconds")]
            block[name] = {"n": len(ids), "macro_f1": round(_macro(pairs), 4),
                           "macro_f1_ci95": _cluster_ci(pairs, groups, _macro),
                           "claim_f1": round(_claim_f1(pairs), 4), "claim_f1_ci95": _cluster_ci(pairs, groups, _claim_f1),
                           "unsure_answers": sum(llm[i]["label"] == "UNSURE" for i in ids),
                           "seconds_per_sentence": round(sum(secs) / len(secs), 2) if secs else None}
        out["models"][f.stem] = block
        c = block.get("compare", {})
        print(f"  {f.stem:24s} compare n {c.get('n')} · macro-F1 {c.get('macro_f1')} {c.get('macro_f1_ci95')} · "
              f"claim F1 {c.get('claim_f1')} · {c.get('seconds_per_sentence')} s/câu")
    path = cl.ROOT / "benchmark" / "model_selection" / "t1_llm_scores.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"-> {path.relative_to(cl.ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--model", required=True)
    r.add_argument("--set", default="all", choices=["all", "compare"])
    r.add_argument("--chunk", type=int, default=10)
    r.add_argument("--workers", type=int, default=6)
    c = sub.add_parser("compare")
    c.add_argument("--model", required=True)
    c.add_argument("--before", action="store_true")
    i = sub.add_parser("recheck-in")
    i.add_argument("--model", required=True)
    i.add_argument("--size", type=int, default=80)
    sub.add_parser("score")
    args = ap.parse_args()
    return {"run": run, "compare": compare, "recheck-in": recheck_in, "score": score}[args.cmd](args)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
