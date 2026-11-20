#!/usr/bin/env bash
# Thiết lập chung cho các script trong thư mục này. Không chạy trực tiếp: `source vast/env.sh`.
export GS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export GS_STORE="${GS_STORE:-$GS_ROOT/gs_store}"            # kho phiên trên máy thuê
export GS_MODEL="${GS_MODEL:-qwen3:4b-instruct-2507-q4_K_M}" # PHẢI trùng tên trên laptop: tên này nằm trong khoá bộ nhớ đệm
export GS_OLLAMA_VERSION="${GS_OLLAMA_VERSION:-0.13.5}"      # bản Ollama đang dùng trên laptop (16/11)
export OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11434}"         # chỉ nghe trong máy; laptop nối qua SSH tunnel
export OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-4}"       # 4 lượt gọi cùng lúc; .env đặt QUANTUM_LLM_WORKERS=4
export OLLAMA_CONTEXT_LENGTH="${OLLAMA_CONTEXT_LENGTH:-8192}"
export OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:-24h}"         # giữ mô hình trong GPU, không nạp lại giữa các lượt
export PATH="$HOME/.local/bin:$PATH"
export PYTHONUTF8=1 PYTHONUNBUFFERED=1
mkdir -p "$GS_ROOT/logs"
