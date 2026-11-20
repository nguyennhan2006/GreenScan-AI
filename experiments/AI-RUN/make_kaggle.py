"""Run the newest GreenScan system WITH its AI stages on a Kaggle T4 and bring the runs back (user decision 11/11/2026).

The laptop (i7-1355U, ~2.6 GB free RAM) reads ~25 s per passage with Qwen3-4B Q4, so the AI path fails the runtime part of
gate ag2_dual_path_to_product there (llm_stages_v1.results.s4_runtime: ratio 2.81). The same code, the same model file
(Ollama qwen3:4b-instruct-2507-q4_K_M, the one routing.yaml names) and the same configs run here on a GPU instead.

What the notebook does, same machine for both arms:
  1. HPG BCPTBV 2025 (claim_source) + BCTN 2024 (evidence), rules only            -> runs/<id>  (baseline time)
  2. the same two PDFs with every stage whose llm_stages_v1 gate passed:
       QUANTUM_LLM_STANCE=on_ambiguous (S5), QUANTUM_VERIFY=dual (S4), QUANTUM_ASSIST_EXPLAIN=queue (S6)
     S2 attributes and S1 claim model stay OFF (their gates were falsified).                     -> runs/<id>
  3. quantum-agent evaluate-real (adjudicated case pack), rules vs AI                          -> eval_*.json
  4. summary.json: runtime ratio (tests amendment_2026-11-11_17h05.s4_prediction "gpu profile passes"), statuses /
     risk scores changed, how many passages the model read, explanations kept / dropped by the number guard.

    .venv/Scripts/python.exe -I experiments/AI-RUN/make_kaggle.py <staging_dir>
      -> <staging_dir>/dataset/greenscan_code.zip   (python tools/kaggle/kapi.py dscreate ... )
      -> experiments/AI-RUN/nb.ipynb               (python tools/kaggle/kapi.py push ... --datasets OWNER/SLUG)
"""
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = "qwen3:4b-instruct-2507-q4_K_M"
TREES = ["src/quantum_gw", "configs", "data/legal/clauses", "data/standards", "data/real_cases", "data/sample",
         "data/golden"]
FILES = ["pyproject.toml", "README.md", "LICENSE"]
SKIP_PARTS = {"__pycache__", ".pytest_cache", "node_modules", "static_build"}


def bundle(dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / "greenscan_code.zip"
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for tree in TREES:
            for p in sorted((ROOT / tree).rglob("*")):
                if p.is_file() and not SKIP_PARTS & set(p.parts) and p.suffix not in {".pyc", ".pyo"}:
                    z.write(p, p.relative_to(ROOT).as_posix()); n += 1
        for f in FILES:
            if (ROOT / f).is_file():
                z.write(ROOT / f, f); n += 1
        # the legal gate reads data/legal/raw/<id>/fulltext.txt when a source has no clauses file; the scans stay home
        for p in sorted((ROOT / "data/legal/raw").glob("*/fulltext.txt")):
            z.write(p, p.relative_to(ROOT).as_posix()); n += 1
    print(f"bundle: {n} files, {out.stat().st_size / 1e6:.1f} MB -> {out}")
    return out


def cell(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src}


SH = '''import subprocess, os, time, json
def sh(cmd, check=True, env=None):
    p = subprocess.Popen(cmd, shell=True, executable="/bin/bash", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
                         env=dict(os.environ, PYTHONUNBUFFERED="1", **(env or {})))
    for line in p.stdout:
        print(line, end="", flush=True)
    if p.wait() and check:
        raise SystemExit(f"command failed (rc {p.returncode}): {cmd}")
    return p.returncode
'''

COMMON = {  # both arms: no .env on Kaggle, so everything is explicit
    "QUANTUM_CONFIG": "configs/default.yaml", "QUANTUM_RUNS_DIR": "/kaggle/working/runs", "QUANTUM_LOG_LEVEL": "INFO",
    "EMBEDDING_PROVIDER": "lite", "RERANKER_PROVIDER": "none", "QUANTUM_OCR_ENABLED": "true",
    "QUANTUM_OCR_LANGUAGES": "vie+eng", "QUANTUM_TESSERACT_COMMAND": "tesseract",
}
RULES = {**COMMON, "QUANTUM_LLM_STANCE": "off", "QUANTUM_VERIFY": "rules", "QUANTUM_ASSIST_EXPLAIN": "off",
         "QUANTUM_ASSIST_ATTRIBUTES": "0", "LOCAL_LLM_BASE_URL": ""}
AI = {**COMMON, "QUANTUM_LLM_STANCE": "on_ambiguous", "QUANTUM_VERIFY": "dual", "QUANTUM_ASSIST_EXPLAIN": "queue",
      "QUANTUM_ASSIST_ATTRIBUTES": "0", "LLM_PROVIDER": "local", "LLM_FALLBACK_ORDER": "local",
      "LOCAL_LLM_PROVIDER": "ollama", "LOCAL_LLM_BASE_URL": "http://127.0.0.1:11434", "LOCAL_LLM_MODEL": MODEL,
      "LOCAL_LLM_TIMEOUT_SECONDS": "180", "QUANTUM_LLM_WORKERS": "4", "QUANTUM_LLM_CACHE_DIR": "/kaggle/working/llm_cache"}
HPG = ("data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf "
       "data/real_cases/sources/originals/HPG_Annual_Report_2024.pdf --roles claim_source,evidence "
       "--source-types internal,internal")

SUMMARY = r'''
import glob, collections
def load(run_id):
    return json.load(open(f"/kaggle/working/runs/{run_id}/result.json", encoding="utf-8"))
def run_id_of(log):
    for line in open(log, encoding="utf-8"):
        if line.startswith("Evidence pack:"):
            return line.split("/runs/")[1].split("/")[0]
def facts(r):
    rel = collections.Counter(e.get("relation_method") or "-" for v in r["verifications"] for e in v["evidence"])
    ir = [x for v in r["verifications"] for x in (v.get("assist") or {}).get("ir", [])]
    expl = [v for v in r["verifications"] if (v.get("assist") or {}).get("explanation")]
    return {"summary": r["summary"], "relation_method": dict(rel), "ir_passages_read": len(ir),
            "ir_vs_rules": dict(collections.Counter(f'{x["rules"]}->{x["ir"]}' for x in ir)),
            "explanations_kept": len(expl), "queue": sum(1 for p in r["priorities"] if p["in_queue"])}
T = json.load(open("/kaggle/working/times.json"))
base, ai = run_id_of("/kaggle/working/hpg_rules.log"), run_id_of("/kaggle/working/hpg_ai.log")
rb, ra = load(base), load(ai)
st = {v["claim"]["claim_id"]: v["status"] for v in rb["verifications"]}
rs = {x["claim_id"]: x["risk_score"] for x in rb["risks"]}
S = {"model": "''' + MODEL + '''", "gpu": T.get("gpu"), "runs": {"rules": base, "ai": ai},
     "seconds": {"rules": T["hpg_rules"], "ai": T["hpg_ai"]}, "ratio_ai_over_rules": round(T["hpg_ai"] / T["hpg_rules"], 2),
     "statuses_changed": [(v["claim"]["claim_id"], st.get(v["claim"]["claim_id"]), v["status"]) for v in ra["verifications"]
                          if st.get(v["claim"]["claim_id"]) != v["status"]],
     "risk_scores_changed": sum(1 for x in ra["risks"] if abs(rs.get(x["claim_id"], -1) - x["risk_score"]) > 1e-9),
     "rules": facts(rb), "ai": facts(ra), "llm_cache_files": len(glob.glob("/kaggle/working/llm_cache/**/*", recursive=True)),
     "evaluate_real_seconds": {k: T.get(k) for k in ("eval_rules", "eval_ai")}}
json.dump(S, open("/kaggle/working/summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: S[k] for k in ("runs", "seconds", "ratio_ai_over_rules", "risk_scores_changed")}, ensure_ascii=False), flush=True)
print("statuses changed:", len(S["statuses_changed"]), S["statuses_changed"][:10], flush=True)
print("rules:", json.dumps(S["rules"], ensure_ascii=False), flush=True)
print("ai:   ", json.dumps(S["ai"], ensure_ascii=False), flush=True)
'''


def notebook() -> dict:
    env = lambda d: repr(d)
    timed = lambda key, cmd, e, log: (
        f'E = {env(e)}\nt0 = time.time()\nrc = sh("cd /kaggle/working/gs && {cmd} | tee {log}; exit ${{PIPESTATUS[0]}}", '
        f'check=False, env=E)\n'
        f'T = json.load(open("/kaggle/working/times.json")); T["{key}"] = round(time.time() - t0, 1); T["{key}_rc"] = rc\n'
        f'json.dump(T, open("/kaggle/working/times.json", "w"))\nprint("[time] {key}", T["{key}"], "s, rc", rc, flush=True)\n')
    cells = [
        cell('print("[cell] setup: gpu, tesseract, ollama", flush=True)\n' + SH + '''
sh("nvidia-smi --query-gpu=name,memory.total --format=csv || true", check=False)
gpu = subprocess.run("nvidia-smi --query-gpu=name --format=csv,noheader", shell=True, capture_output=True, text=True).stdout.strip()
json.dump({"gpu": gpu}, open("/kaggle/working/times.json", "w"))
sh("apt-get update -qq > /dev/null 2>&1; apt-get install -y -qq zstd tesseract-ocr tesseract-ocr-vie > /dev/null 2>&1 || true", check=False)
sh("tesseract --version 2>&1 | head -1", check=False)
sh("curl -fsSL https://ollama.com/install.sh | sh > /kaggle/working/ollama_install.log 2>&1; tail -2 /kaggle/working/ollama_install.log")
subprocess.Popen("OLLAMA_NUM_PARALLEL=4 ollama serve > /kaggle/working/ollama.log 2>&1", shell=True)
time.sleep(8)
sh("ollama --version")
'''),
        cell('print("[cell] unpack GreenScan + pip install", flush=True)\n' + SH + '''
z = subprocess.run("find /kaggle/input -name greenscan_code.zip | head -1", shell=True, capture_output=True, text=True).stdout.strip()
print("bundle:", z, flush=True)
if z:
    sh(f"mkdir -p /kaggle/working/gs && cd /kaggle/working/gs && unzip -q -o '{z}' && ls")
else:  # Kaggle extracted the zip: copy the folder that holds pyproject.toml
    d = subprocess.run("find /kaggle/input -name pyproject.toml | head -1", shell=True, capture_output=True, text=True).stdout.strip()
    print("extracted bundle:", d, flush=True)
    assert d, "neither greenscan_code.zip nor an extracted copy under /kaggle/input"
    sh(f"cp -r '{os.path.dirname(d)}' /kaggle/working/gs && ls /kaggle/working/gs")
sh("cd /kaggle/working/gs && pip install -q -e . 2>&1 | tail -3")
sh("cd /kaggle/working/gs && quantum-agent --help | head -20")
'''),
        cell(f'print("[cell] pull {MODEL} + warm-up", flush=True)\n' + SH + f'''
sh("ollama pull {MODEL} 2>&1 | tail -2")
t0 = time.time()
import urllib.request
body = json.dumps({{"model": "{MODEL}", "stream": False, "messages": [{{"role": "user", "content": "Trả lời một từ: xanh hay đỏ?"}}]}}).encode()
print(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:11434/api/chat", body), timeout=600).read()[:400], flush=True)
print("[warm-up]", round(time.time() - t0, 1), "s", flush=True)
sh("ollama ps", check=False)
'''),
        cell('print("[cell] HPG rules only (baseline)", flush=True)\n' + SH +
             timed("hpg_rules", f"quantum-agent analyze {HPG} 2>&1", RULES, "/kaggle/working/hpg_rules.log")),
        cell('print("[cell] HPG with AI stages (S5 stance, S4 dual reader, S6 explanations)", flush=True)\n' + SH + '''
import threading
stop = threading.Event()
def beat():  # progress while the pipeline runs: how many answers the model has cached so far
    while not stop.wait(60):
        n = subprocess.run("find /kaggle/working/llm_cache -type f 2>/dev/null | wc -l", shell=True, capture_output=True, text=True).stdout.strip()
        print("[progress] llm cache files:", n, flush=True)
threading.Thread(target=beat, daemon=True).start()
''' + timed("hpg_ai", f"quantum-agent analyze {HPG} 2>&1", AI, "/kaggle/working/hpg_ai.log") + 'stop.set()\nsh("tail -5 /kaggle/working/ollama.log", check=False)\n'),
        cell('print("[cell] evaluate-real: rules vs AI", flush=True)\n' + SH +
             timed("eval_rules", "quantum-agent evaluate-real 2>&1 > /kaggle/working/eval_rules.json", RULES, "/kaggle/working/eval_rules.log") +
             timed("eval_ai", "quantum-agent evaluate-real 2>&1 > /kaggle/working/eval_ai.json", AI, "/kaggle/working/eval_ai.log")),
        cell('print("[cell] summary + pack", flush=True)\n' + SH + SUMMARY + '''
sh("cd /kaggle/working && tar czf runs.tgz runs llm_cache && ls -la /kaggle/working | head -30")
print("ALL CELLS OK", flush=True)
'''),
    ]
    return {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4, "nbformat_minor": 5}


if __name__ == "__main__":
    stage = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "out/ai_run_stage"
    bundle(stage / "dataset")
    out = Path(__file__).with_name("nb.ipynb")
    out.write_text(json.dumps(notebook(), ensure_ascii=False, indent=1), encoding="utf-8")
    print("notebook:", out, out.stat().st_size, "bytes")
