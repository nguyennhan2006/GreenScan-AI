"""AG-3 v0 (registration agentic_ag3_v0): raw flattened page vs rebuilt table rows, same IR reader, same irlib verdict.

Cases: size ladder N01-N06, N08 (HPG SR 2025 p.39). Reader: Groq openai/gpt-oss-120b (reasoning_effort low +
json_object, chosen by GROQ-PROBE), AG-1 prompt unchanged, figures held to the text by irlib.ground (to_irs).
  raw   the page text PyMuPDF gives (what every model judged before) is read as one text
  rows  every rebuilt row sentence of the page is read on its own; the evidence is the union of their figures
Calls are cached in out/cache.jsonl.

    .venv/Scripts/python.exe -I experiments/AG-3/eval_p39.py
"""
from __future__ import annotations

import hashlib, json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in ("src", "experiments/AG-1", "experiments/AG-3", "benchmark/size_ladder_2026-10-10"):
    sys.path.insert(0, str(ROOT / p))
os.chdir(ROOT)
import httpx  # noqa: E402
import pymupdf  # noqa: E402

import quantum_gw.settings  # noqa: E402,F401  (loads .env: GROQ_API_KEY)
import rows  # noqa: E402
from ag1_worker import PROMPT, parse, to_irs, verdict  # noqa: E402
from irlib import METRICS, SCOPES, VALUE_KINDS  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
OUT = ROOT / "experiments/AG-3/out"
BODY = {"model": "openai/gpt-oss-120b", "temperature": 0, "max_completion_tokens": 2048,
        "reasoning_effort": "low", "response_format": {"type": "json_object"}}
IDS = ("N01", "N02", "N03", "N04", "N05", "N06", "N08")


def read(text: str, cache: dict, fh) -> list:
    key = hashlib.sha1(text.encode()).hexdigest()[:16]
    if key not in cache:
        prompt = PROMPT.format(metrics=list(METRICS), kinds=list(VALUE_KINDS), scopes=list(SCOPES), sentence=text)
        for attempt in range(4):
            r = httpx.post("https://api.groq.com/openai/v1/chat/completions", timeout=120,
                           headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
                           json={**BODY, "messages": [{"role": "user", "content": prompt}]})
            if r.status_code == 429:
                time.sleep(float(r.headers.get("retry-after", "10")) + 1)
                continue
            r.raise_for_status()
            break
        reply = r.json()["choices"][0]["message"]["content"]
        cache[key] = {"key": key, "text": text, "raw": reply}
        fh.write(json.dumps(cache[key], ensure_ascii=False) + "\n"); fh.flush()
        time.sleep(2.2)
    obj = parse(cache[key]["raw"]) or {}
    return to_irs(obj.get("figures") if isinstance(obj.get("figures"), list) else [], text)


def main() -> None:
    from cases_noisy import CASES, P39
    OUT.mkdir(parents=True, exist_ok=True)
    cpath = OUT / "cache.jsonl"
    cache = {r["key"]: r for r in map(json.loads, cpath.open(encoding="utf-8"))} if cpath.exists() else {}
    page = pymupdf.open(ROOT / "data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf")[38]
    row_sentences = [r["sentence"] for r in rows.table_rows(page)]
    results = []
    with cpath.open("a", encoding="utf-8") as fh:
        ev_raw = read(P39, cache, fh)
        ev_rows = [ir for s in row_sentences for ir in read(s, cache, fh)]
        for cid, family, claim, evidence, ok in CASES:
            if cid not in IDS:
                continue
            c = read(claim, cache, fh)
            a, why_a = verdict(c, ev_raw, P39)
            b, why_b = verdict(c, ev_rows, "\n".join(row_sentences))
            results.append({"id": cid, "gold": sorted(ok), "raw": a, "rows": b, "why_rows": why_b[:2], "claim": claim})
    summ = {}
    for cond in ("raw", "rows"):
        summ[cond] = {"right": sum(r[cond] in r["gold"] for r in results), "n": len(results),
                      "false_S": sum(r[cond] == "S" and "S" not in r["gold"] for r in results),
                      "false_C": sum(r[cond] == "C" and "C" not in r["gold"] for r in results),
                      "decided": sum(r[cond] in "SC" for r in results)}
    (OUT / "result_p39.json").write_text(json.dumps({"rows": row_sentences, "cases": results, "summary": summ,
                                                      "evidence_figures": {"raw": len(ev_raw), "rows": len(ev_rows)}},
                                                     ensure_ascii=False, indent=1), encoding="utf-8")
    for r in results:
        print(f"{r['id']} gold {r['gold']} raw {r['raw']} rows {r['rows']} | {r['claim'][:80]}")
    print("SUMMARY", json.dumps(summ), "evidence figures raw", len(ev_raw), "rows", len(ev_rows))


if __name__ == "__main__":
    main()
