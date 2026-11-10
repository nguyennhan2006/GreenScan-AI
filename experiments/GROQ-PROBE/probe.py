"""GROQ-PROBE: which Groq chat models and request settings work for GreenScan's IR extraction.

Free-tier models and their accepted parameters change without notice (Qwen3-32B left Groq in 2026), so every
model listed live by GET /models is tried under a matrix of settings before any of them is used:
reasoning_effort (none / low / high), reasoning_format hidden, response_format json_object / json_schema,
and their useful combinations. A setting the API refuses (HTTP 400) is recorded once and skipped.

Probe texts: GS-Bench v1 B-b sentences with a gold IR (claims of every perturbation family + evidence sentences,
public reports only). Scored per call: HTTP ok, JSON readable, gold figure found (same quantity), and agreement on
metric / value_kind / status / period / scope / unit dimension; latency and token usage (reasoning included).
Calls are cached (out/calls.jsonl), so a re-run after a rate limit continues where it stopped.

usage (repository root): .venv/Scripts/python.exe -I experiments/GROQ-PROBE/probe.py [--texts 10] [--models a,b]
The key comes from GROQ_API_KEY in .env and is never printed.
"""
from __future__ import annotations

import argparse, hashlib, json, os, re, statistics, sys, time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments" / "AG-1"))
import httpx  # noqa: E402

import quantum_gw.settings  # noqa: E402,F401  (loads .env into os.environ)
from ag1_worker import PROMPT, parse, to_irs  # noqa: E402
from irlib import METRICS, SCOPES, VALUE_KINDS  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
BASE = "https://api.groq.com/openai/v1"
OUT = ROOT / "experiments" / "GROQ-PROBE" / "out"
NOT_CHAT = re.compile(r"whisper|orpheus|tts|guard|safety|playai|distil|embed|compound", re.I)
FIELDS = ("metric", "value_kind", "status", "period", "scope")
SCHEMA = {
    "type": "object",
    "properties": {"figures": {"type": "array", "items": {"type": "object", "properties": {
        "metric": {"type": "string", "enum": list(METRICS)}, "metric_text": {"type": "string"},
        "value_text": {"type": "string"}, "multiplier_text": {"type": "string"}, "unit_text": {"type": "string"},
        "value_kind": {"type": "string", "enum": list(VALUE_KINDS)},
        "change_direction": {"type": ["string", "null"]}, "baseline_year": {"type": ["integer", "null"]},
        "period": {"type": ["integer", "null"]}, "status": {"type": "string", "enum": ["actual", "target"]},
        "scope": {"type": ["string", "null"]}, "boundary": {"type": "string"}},
        "required": ["metric", "value_text", "unit_text", "value_kind", "period", "status"]}}},
    "required": ["figures"],
}
CONFIGS = {
    "default": {},
    "json_object": {"response_format": {"type": "json_object"}},
    "json_schema": {"response_format": {"type": "json_schema", "json_schema": {"name": "figures", "schema": SCHEMA}}},
    "effort_none": {"reasoning_effort": "none"},
    "effort_low": {"reasoning_effort": "low"},
    "effort_high": {"reasoning_effort": "high"},
    "format_hidden": {"reasoning_format": "hidden"},
    "effort_low+json_object": {"reasoning_effort": "low", "response_format": {"type": "json_object"}},
    "effort_none+json_object": {"reasoning_effort": "none", "response_format": {"type": "json_object"}},
}


def headers() -> dict:
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        sys.exit("GROQ_API_KEY trống trong .env")
    return {"Authorization": f"Bearer {key}"}


def probe_texts(n: int) -> list[dict]:
    """Up to n texts with a gold IR: one claim per perturbation family first, then evidence sentences."""
    cases = [json.loads(line) for line in (ROOT / "benchmark/gs_bench_v1/gs_bench_v1.jsonl").open(encoding="utf-8")]
    bb = sorted((c for c in cases if c["layer"] == "B-b"), key=lambda c: hashlib.sha1(c["id"].encode()).hexdigest())
    out, fams, seen = [], set(), set()
    for c in bb:
        if c["family"] not in fams and c["claim"] not in seen:
            fams.add(c["family"]); seen.add(c["claim"])
            out.append({"text": c["claim"], "gold": c["claim_ir"], "kind": f"claim {c['family'].split()[0]}"})
    for c in bb:
        if c["evidence"] not in seen:
            seen.add(c["evidence"])
            out.append({"text": c["evidence"], "gold": c["evidence_ir"], "kind": "evidence"})
    return out[:n]


def score(reply: str | None, gold: dict) -> dict:
    obj = parse(reply)
    if obj is None or not isinstance(obj.get("figures"), list):
        return {"json_ok": False, "found": False, "fields": 0.0}
    from irlib import IR
    g = IR.from_dict(gold)
    gv, gt, gdim = g.quantity()
    best = 0.0
    found = False
    for ir in to_irs(obj["figures"]):
        v, t, dim = ir.quantity()
        if abs(v - gv) <= t + gt and dim == gdim:
            found = True
            best = max(best, sum(getattr(ir, f) == getattr(g, f) for f in FIELDS) / len(FIELDS))
    return {"json_ok": True, "found": found, "fields": best}


def call(client: httpx.Client, model: str, config: dict, text: str) -> dict:
    prompt = PROMPT.format(metrics=list(METRICS), kinds=list(VALUE_KINDS), scopes=list(SCOPES), sentence=text)
    body = {"model": model, "temperature": 0, "max_completion_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}], **config}
    for attempt in range(4):
        t = time.time()
        r = client.post(f"{BASE}/chat/completions", headers=headers(), json=body)
        secs = round(time.time() - t, 2)
        if r.status_code == 429:
            wait = float(r.headers.get("retry-after", "20"))
            if wait > 120:  # daily cap: stop this model
                return {"status": 429, "error": f"rate limit, retry-after {wait:.0f}s", "seconds": secs}
            time.sleep(wait + 1)
            continue
        if r.status_code != 200:
            return {"status": r.status_code, "error": r.text[:300], "seconds": secs}
        j = r.json()
        msg = j["choices"][0]["message"]
        content = re.sub(r"<think>.*?</think>", "", msg.get("content") or "", flags=re.S).strip()
        return {"status": 200, "reply": content, "has_reasoning_field": bool(msg.get("reasoning")),
                "usage": j.get("usage", {}), "seconds": secs}
    return {"status": 429, "error": "rate limit after retries"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--texts", type=int, default=10)
    ap.add_argument("--models", default="")
    ap.add_argument("--gap", type=float, default=2.2, help="seconds between calls (free tier ~30 RPM)")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cache_path = OUT / "calls.jsonl"
    cache = {r["key"]: r for r in map(json.loads, cache_path.open(encoding="utf-8"))} if cache_path.exists() else {}
    with httpx.Client(timeout=120) as client:
        listed = client.get(f"{BASE}/models", headers=headers()).json().get("data", [])
        (OUT / "models.json").write_text(json.dumps(listed, ensure_ascii=False, indent=1), encoding="utf-8")
        models = a.models.split(",") if a.models else sorted(m["id"] for m in listed if not NOT_CHAT.search(m["id"]) and m.get("active", True))
        print(f"[probe] models: {models}", flush=True)
        texts = probe_texts(a.texts)
        with cache_path.open("a", encoding="utf-8") as fh:
            for model in models:
                capped = False
                for name, config in CONFIGS.items():
                    refused = False
                    for t in texts:
                        key = hashlib.sha1(f"{model}|{name}|{t['text']}".encode()).hexdigest()[:20]
                        if key in cache:
                            refused = refused or cache[key]["status"] == 400
                            continue
                        if refused or capped:
                            break
                        rec = call(client, model, config, t["text"])
                        rec.update({"key": key, "model": model, "config": name, "kind": t["kind"]})
                        if rec["status"] == 200:
                            rec.update(score(rec["reply"], t["gold"]))
                        cache[key] = rec
                        fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()
                        refused = rec["status"] == 400
                        capped = rec["status"] == 429
                        time.sleep(a.gap)
                    print(f"[probe] {model} · {name}: done", flush=True)
    summarize(cache)


def summarize(cache: dict) -> None:
    rows = {}
    for r in cache.values():
        rows.setdefault((r["model"], r["config"]), []).append(r)
    table = []
    for (model, name), rs in sorted(rows.items()):
        ok = [r for r in rs if r["status"] == 200]
        err = next((r.get("error", "") for r in rs if r["status"] != 200), "")
        table.append({
            "model": model, "config": name, "calls": len(rs), "http_ok": len(ok),
            "json_ok": sum(r.get("json_ok", False) for r in ok), "found": sum(r.get("found", False) for r in ok),
            "field_acc": round(statistics.mean(r.get("fields", 0) for r in ok), 3) if ok else None,
            "p50_s": round(statistics.median(r["seconds"] for r in ok), 2) if ok else None,
            "tokens_out_mean": round(statistics.mean(r["usage"].get("completion_tokens", 0) for r in ok)) if ok else None,
            "error": err[:120],
        })
    (OUT / "summary.json").write_text(json.dumps(table, ensure_ascii=False, indent=1), encoding="utf-8")
    for t in table:
        print(f"{t['model']:<32} {t['config']:<24} ok {t['http_ok']}/{t['calls']} json {t['json_ok']} found {t['found']} "
              f"fields {t['field_acc']} p50 {t['p50_s']}s out {t['tokens_out_mean']} {t['error'][:60]}", flush=True)


if __name__ == "__main__":
    main()
