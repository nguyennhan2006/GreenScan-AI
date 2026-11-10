"""Build the Kaggle notebook for agentic_ag2_product parity: the product reader (Ollama GGUF) on set G vs Kaggle 4B bf16.

The laptop had no free RAM on 01/11 (Ollama: needs 3.3 GiB, 2.6 GiB available), so the parity half of the registered
check runs on Kaggle with the same code path: Ollama + quantum_gw.verification.ir_reader + product_reader.py.
Reading time on T4 is NOT the laptop time; that half still needs the laptop.

    .venv/Scripts/python.exe -I experiments/AG-2/kaggle_q4/make_nb.py     -> experiments/AG-2/kaggle_q4/nb.ipynb
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FILES = [
    "src/quantum_gw/providers/base.py", "src/quantum_gw/providers/ollama.py",
    "src/quantum_gw/verification/ir_reader.py", "src/quantum_gw/verification/irlib.py",
    "experiments/AG-2/product_reader.py",
    "benchmark/gs_bench_v1/gs_heldout_v12.jsonl", "experiments/AG-1/out/g_v12/4b_cases.jsonl",
]
EMPTY = ["src/quantum_gw/__init__.py", "src/quantum_gw/providers/__init__.py", "src/quantum_gw/verification/__init__.py"]
MODELS = ["qwen3:4b-instruct-2507-q4_K_M", "qwen3:4b-instruct-2507-q8_0"]


def cell(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src}


STREAM = '''import subprocess, os
def sh(cmd, check=True):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=dict(os.environ, PYTHONUNBUFFERED="1"))
    for line in p.stdout:
        print(line, end="", flush=True)
    if p.wait() and check:
        raise SystemExit(f"command failed (rc {p.returncode}): {cmd}")
'''

bundle = {f: (ROOT / f).read_text(encoding="utf-8") for f in FILES}
bundle.update({f: "" for f in EMPTY})
cells = [
    cell('print("[cell] setup + ollama", flush=True)\n' + STREAM + '''sh("nvidia-smi --query-gpu=name,memory.total --format=csv || true", check=False)
sh("apt-get install -y -qq zstd > /dev/null 2>&1 || true", check=False)
sh("curl -fsSL https://ollama.com/install.sh | sh")
subprocess.Popen("ollama serve > /kaggle/working/ollama.log 2>&1", shell=True)
import time; time.sleep(8)
sh("ollama --version")
'''),
    cell('print("[cell] write bundle", flush=True)\nimport os\nB = ' + repr(bundle) + '''
for path, text in B.items():
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)
print(len(B), "files written", flush=True)
'''),
]
for m in MODELS:
    tag = m.rsplit("-", 1)[-1]
    cells.append(cell(f'print("[cell] {tag}: pull + read set G", flush=True)\n' + STREAM +
                      f'sh("ollama pull {m}")\n'
                      f'sh("python -u experiments/AG-2/product_reader.py benchmark/gs_bench_v1/gs_heldout_v12.jsonl out/{tag} '
                      f'--model {m} --ref experiments/AG-1/out/g_v12/4b_cases.jsonl")\n'))
cells.append(cell('print("[cell] done", flush=True)\nimport subprocess\nprint(subprocess.run("cat out/*/summary.json", shell=True, capture_output=True, text=True).stdout)\nprint("ALL CELLS OK", flush=True)\n'))
nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
      "nbformat": 4, "nbformat_minor": 5}
out = Path(__file__).with_name("nb.ipynb")
out.write_text(json.dumps(nb, ensure_ascii=False), encoding="utf-8")
print("wrote", out, out.stat().st_size, "bytes")
