#!/usr/bin/env bash
# Cài môi trường trên máy vast.ai (A100 80 GB, image PyTorch/CUDA 12.x hoặc vllm/vllm-openai). Chạy một lần.
#   bash 00_setup.sh            # cài thư viện + tải trước mô hình vào ~/.cache/huggingface
set -euo pipefail
cd "$(dirname "$0")"
echo "[cell] setup gpu"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
python -c "import sys; print(sys.version)"
echo "[cell] setup pip"
pip install -q -r requirements.txt
pip list 2>/dev/null | grep -i -E '^(vllm|torch|transformers|peft) '
echo "[cell] setup models"
# Tải trước để lượt train/serve không chờ mạng. HF_TOKEN không cần (mô hình công khai).
for m in ${GS_MODELS:-"Qwen/Qwen3-14B Qwen/Qwen3-4B-Instruct-2507 Qwen/Qwen3-32B-AWQ openai/gpt-oss-120b intfloat/multilingual-e5-small intfloat/multilingual-e5-base MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 Alibaba-NLP/gte-multilingual-reranker-base"}; do
  echo "[setup] download $m"
  huggingface-cli download "$m" --quiet > /dev/null || echo "[setup] !! could not download $m"
done
df -h ~ | tail -1
echo "[setup] OK"
