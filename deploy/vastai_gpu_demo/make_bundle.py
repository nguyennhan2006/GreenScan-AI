"""Build the upload for a rented GPU machine (vast.ai): the submitted source + the scripts in this folder.

Run on the laptop, from anywhere:
    C:/Python314/python.exe deploy/vastai_gpu_demo/make_bundle.py

Writes <AI quantum>/vast_bundle/greenscan_vast.tar.gz with one top folder `greenscan/`:
    src, configs, data, tools/thuyet_minh, pyproject.toml, README.md   from the submission checkpoint
    vast/*.sh, vast/*.py                                               the scripts of this folder
    vast/constraints.txt     the laptop's package versions (same parser versions -> same claims)
    vast/dot_env             the laptop's non-secret settings (no key, no Windows path)
    vast/expected_B.json     claims and verdicts of the laptop's rules-only Hòa Phát run (parity check)
"""
from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WRAPPER = REPO.parents[2]                      # .../AI quantum
CHECKPOINT = WRAPPER / "checkpoint_nop_bai" / "vong2_2026-11-16" / "GreenScan-AI"
REFERENCE_RUN = WRAPPER / "demo_store_ban_ket" / "runs" / "efcd9717caef4d7b" / "result.json"
OUT = WRAPPER / "vast_bundle" / "greenscan_vast.tar.gz"

PARTS = ["src", "configs", "data", "tools/thuyet_minh", "pyproject.toml", "README.md"]
SKIP_DIRS = {"__pycache__", ".pytest_cache", "node_modules"}
TEXT_SUFFIXES = {".sh", ".py", ".txt", ".json", ".md", ".env"}
# Settings copied from the laptop's .env. Nothing secret, nothing that is a Windows path.
ENV_KEYS = ["QUANTUM_CONFIG", "QUANTUM_PROFILE", "QUANTUM_OCR_ENABLED", "QUANTUM_OCR_LANGUAGES",
            "QUANTUM_LLM_CACHE_DIR", "EMBEDDING_PROVIDER", "EMBEDDING_CACHE_DIR", "RERANKER_PROVIDER",
            "RERANK_CANDIDATE_K", "RERANK_FINAL_K", "LLM_PROVIDER", "LLM_FALLBACK_ORDER",
            "LOCAL_LLM_PROVIDER", "LOCAL_LLM_MODEL", "LOCAL_LLM_TIMEOUT_SECONDS", "LOCAL_LLM_MAX_TOKENS"]
ENV_OVERRIDES = {"QUANTUM_LLM_WORKERS": "4"}   # matches OLLAMA_NUM_PARALLEL in vast/env.sh


def claim_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def expected() -> bytes:
    result = json.loads(REFERENCE_RUN.read_text(encoding="utf-8"))
    rows = sorted([claim_digest(v["claim"]["text"]), v["status"]] for v in result["verifications"])
    summary = result["summary"]
    body = {"run_id": result["run_id"], "total_claims": summary["total_claims"],
            "status_counts": summary["status_counts"], "severity_counts": summary["severity_counts"],
            "total_chunks": summary["total_chunks"], "claims": rows}
    return json.dumps(body, ensure_ascii=False, indent=1).encode("utf-8")


def constraints() -> bytes:
    python = REPO / ".venv" / "Scripts" / "python.exe"
    frozen = subprocess.run([str(python), "-I", "-m", "pip", "list", "--format=freeze"],
                            capture_output=True, text=True, check=True).stdout
    keep = [line for line in frozen.splitlines()
            if "==" in line and not line.lower().startswith(("quantum", "greenscan", "pywin32", "pywinpty", "pip=="))]
    return ("\n".join(keep) + "\n").encode("utf-8")


def dot_env() -> bytes:
    values = {}
    for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition("=")
        if sep and key.strip() in ENV_KEYS:
            values[key.strip()] = value.strip()
    values.update(ENV_OVERRIDES)
    return ("# GreenScan trên máy GPU thuê: cùng thiết lập như laptop, không có khoá nào.\n"
            + "".join(f"{k}={v}\n" for k, v in values.items())).encode("utf-8")


def add_bytes(tar: tarfile.TarFile, name: str, data: bytes, mode: int = 0o644) -> None:
    info = tarfile.TarInfo(name)
    info.size, info.mode = len(data), mode
    tar.addfile(info, io.BytesIO(data))


def add_tree(tar: tarfile.TarFile, source: Path, name: str) -> int:
    if source.is_file():
        tar.add(source, arcname=name)
        return 1
    count = 0
    for path in sorted(source.rglob("*")):
        if path.is_file() and not (SKIP_DIRS & set(path.parts)) and path.suffix != ".pyc":
            tar.add(path, arcname=f"{name}/{path.relative_to(source).as_posix()}")
            count += 1
    return count


def main() -> None:
    for needed in (CHECKPOINT, REFERENCE_RUN):
        if not needed.exists():
            sys.exit(f"missing: {needed}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    files = 0
    with tarfile.open(OUT, "w:gz", compresslevel=6) as tar:
        for part in PARTS:
            files += add_tree(tar, CHECKPOINT / part, f"greenscan/{part}")
        for script in sorted(HERE.iterdir()):
            if script.suffix in {".sh", ".py"} and script.name not in {"make_bundle.py", "import_results.py"}:
                data = script.read_bytes().replace(b"\r\n", b"\n")      # edited on Windows
                add_bytes(tar, f"greenscan/vast/{script.name}", data, 0o755)
                files += 1
        add_bytes(tar, "greenscan/vast/constraints.txt", constraints())
        add_bytes(tar, "greenscan/vast/dot_env", dot_env())
        add_bytes(tar, "greenscan/vast/expected_B.json", expected())
        files += 3
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print(f"{OUT}\n{files} files, {OUT.stat().st_size / 2**20:.1f} MB, sha256 {digest}")


if __name__ == "__main__":
    main()
