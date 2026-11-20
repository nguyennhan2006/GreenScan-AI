#!/usr/bin/env bash
# Cài môi trường trên máy GPU thuê. Chạy một lần, khoảng 5-8 phút (phần lớn là tải mô hình 2,5 GB).
#   bash vast/00_setup.sh
#   GS_SKIP_OLLAMA=1 bash vast/00_setup.sh     # chỉ cài Python (thử trên máy không có GPU)
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$GS_ROOT"

echo "[cell] setup gpu"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || echo "[setup] !! không thấy GPU"

echo "[cell] setup apt"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq --no-install-recommends ca-certificates curl tmux zstd pciutils \
  tesseract-ocr tesseract-ocr-eng tesseract-ocr-vie > /dev/null
tesseract --version 2>&1 | sed -n 1p

echo "[cell] setup python"
command -v uv > /dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh > /dev/null
uv --version
# Python 3.14 và đúng các phiên bản thư viện của laptop (vast/constraints.txt): cùng bộ đọc PDF thì cùng tuyên bố.
[ -d .venv ] || uv venv --quiet --python 3.14 .venv
uv pip install --quiet --python .venv/bin/python -c vast/constraints.txt .
[ -f .env ] || cp vast/dot_env .env
.venv/bin/python -c "import sys, pdfplumber, fitz, sklearn; print('[setup] python', sys.version.split()[0], 'pdfplumber', pdfplumber.__version__, 'pymupdf', fitz.__doc__.split()[1], 'sklearn', sklearn.__version__)"

if [ "${GS_SKIP_OLLAMA:-0}" != "1" ]; then
  echo "[cell] setup ollama"
  if ! command -v ollama > /dev/null; then
    curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION="$GS_OLLAMA_VERSION" sh > logs/ollama_install.log 2>&1 \
      || { tail -20 logs/ollama_install.log; exit 1; }
  fi
  bash vast/01_ollama.sh
fi
df -h "$GS_ROOT" | tail -1
echo "[setup] OK"
