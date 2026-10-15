"""Same cases, same prompt, local qwen3:8b through Ollama (CPU laptop).

usage: run_local.py <out.json> [model]
"""
import ast, json, os, re, sys, time
from pathlib import Path

import httpx

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
CASES = __import__(os.environ.get("LADDER_CASES", "cases")).CASES

# single source of truth for the prompt: read it out of run_ladder.py
tree = ast.parse((HERE / "run_ladder.py").read_text(encoding="utf-8"))
PROMPT = next(node.value.value for node in tree.body
              if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "PROMPT")
MAP = {"SUPPORTED": "S", "CONTRADICTED": "C", "NOT_ENOUGH_INFO": "N"}

sys.stdout.reconfigure(encoding="utf-8")
out_path = sys.argv[1]
model = sys.argv[2] if len(sys.argv) > 2 else "qwen3:8b"
answers = {}
for cid, family, claim, evidence, ok in CASES:
    t = time.time()
    try:
        r = httpx.post("http://127.0.0.1:11434/api/chat", timeout=900, json={
            "model": model, "stream": False, "think": os.environ.get("LADDER_THINK", "0") == "1", "options": {"temperature": 0, "num_ctx": 4096},
            "messages": [{"role": "user", "content": PROMPT.format(claim=claim, evidence=evidence)}]})
        text = r.json()["message"]["content"]
        body = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
        m = re.search(r"\{.*\}", body, flags=re.S)
        parsed = json.loads(m.group(0)) if m else {}
        raw = str(parsed.get("label", "")).strip().upper()
        answers[cid] = {"label": MAP.get(raw, "?"), "raw": raw or body[:200], "reason": str(parsed.get("ly_do", ""))[:300],
                        "seconds": round(time.time() - t, 1)}
    except Exception as exc:  # noqa: BLE001
        answers[cid] = {"label": "?", "raw": "ERROR", "reason": repr(exc)[:200], "seconds": round(time.time() - t, 1)}
    print(f"{cid} {answers[cid]['label']} {answers[cid]['seconds']}s", flush=True)
    json.dump({model: answers}, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
ok = {c[0]: c[4] for c in CASES}
correct = sum(a["label"] in ok[k] for k, a in answers.items())
print(f"{model}: {correct}/{len(ok)} correct; mean {sum(a['seconds'] for a in answers.values())/len(answers):.1f}s/call")
