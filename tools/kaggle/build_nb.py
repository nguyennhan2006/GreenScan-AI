"""Build a Kaggle notebook that embeds code files and runs commands (each streamed line by line).

    python kaggle/build_nb.py OUT.ipynb --files a.py b.py --pip "vllm" --run "python -u run.py --x 1" [--run ...]

Cells: setup (GPU info; `pip install` of --pip (env PIP_SPEC overrides), then --pip-post (env PIP_POST overrides), only when a GPU is present, versions printed), one cell writing every --files
file into the working directory (same base name), one cell per --run command, then a last cell printing ALL CELLS OK.
Every cell starts with print("[cell] ...", flush=True) (~/.claude/CLAUDE.md section 5).
"""
import argparse
import json
from pathlib import Path


def cell(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src}


STREAM = '''import subprocess, sys, os
def sh(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=dict(os.environ, PYTHONUNBUFFERED="1"))
    for line in p.stdout:
        print(line, end="", flush=True)
    if p.wait():
        raise SystemExit(f"command failed (rc {p.returncode}): {cmd}")
'''


def build(files, pip, runs, post=""):
    setup = f'print("[cell] setup", flush=True)\n{STREAM}' + '''sh("nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv || true")
import torch
print("torch", torch.__version__, "cuda", torch.cuda.is_available(), torch.cuda.device_count(), flush=True)
PIP = os.environ.get("PIP_SPEC", %r)   # --env PIP_SPEC=... / PIP_POST=... override the built-in install
if PIP and torch.cuda.is_available():
    sh(f"pip install -q {PIP}")
    if os.environ.get("PIP_POST", %r):
        sh(os.environ.get("PIP_POST", %r))
sh("pip list 2>/dev/null | grep -i -E '^(vllm|torch|transformers|qwen-asr|pandas|openpyxl) ' || true")
''' % (pip, post, post)
    write = 'print("[cell] write code files", flush=True)\nFILES = {\n'
    write += "".join(f"    {Path(f).name!r}: {Path(f).read_text(encoding='utf-8')!r},\n" for f in files)
    write += "}\nfor name, text in FILES.items():\n    open(name, 'w', encoding='utf-8').write(text)\n    print('wrote', name, len(text), flush=True)\n"
    cells = [cell(setup), cell(write)]
    cells += [cell(f'print({f"[cell] run {i + 1}: {r[:60]}"!r}, flush=True)\n{STREAM}sh({r!r})\n') for i, r in enumerate(runs)]
    cells.append(cell('print("[cell] done", flush=True)\nprint("ALL CELLS OK", flush=True)'))
    return {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                         "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--pip", default="")
    ap.add_argument("--pip-post", default="", help="command run after --pip, e.g. 'pip uninstall -y torchaudio'")
    ap.add_argument("--run", action="append", default=[])
    a = ap.parse_args()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    if ("vllm" in a.pip or "peft" in a.pip) and not a.pip_post:  # Kaggle's torchaudio / torchao break vLLM's torch and peft's import (29/10: 5 dead notebooks)
        a.pip_post = "pip uninstall -y torchaudio torchao"
    Path(a.out).write_text(json.dumps(build(a.files, a.pip, a.run, a.pip_post), ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", a.out)
