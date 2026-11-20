#!/usr/bin/env bash
# Máy chủ vLLM (API tương thích OpenAI) cho phương án 2: laptop chạy GreenScan, gọi máy này để đọc cặp và viết lời giải thích.
#   GS_API_KEY=<chuỗi bí mật> bash 30_serve.sh              # mặc định gpt-oss-120b (vừa 1 × A100 80 GB)
#   GS_SERVE_MODEL=Qwen/Qwen3-32B-AWQ bash 30_serve.sh      # dự phòng nhẹ hơn (GPU 24-48 GB)
#   GS_SERVE_MODEL=Qwen/Qwen3-14B GS_LORA=1 bash 30_serve.sh  # 14B + adapter stance/explain vừa huấn luyện
# Mở cổng 8001 trong mục "Open ports" của vast.ai (hoặc dùng SSH tunnel: ssh -L 8001:localhost:8001 ...).
set -euo pipefail
cd "$(dirname "$0")"
: "${GS_API_KEY:?đặt GS_API_KEY (chuỗi ngẫu nhiên dài) trước khi mở máy chủ ra mạng}"
MODEL="${GS_SERVE_MODEL:-openai/gpt-oss-120b}"
NAME="${GS_SERVED_NAME:-$MODEL}"     # tên laptop gửi trong LOCAL_LLM_MODEL; giữ "gpt-oss"/"32b" để sản phẩm chọn prompt họ lớn
ARGS=(--host 0.0.0.0 --port "${GS_PORT:-8001}" --api-key "$GS_API_KEY" --served-model-name "$NAME"
      --max-model-len "${GS_MAX_LEN:-16384}" --gpu-memory-utilization 0.92)
if [ "${GS_LORA:-0}" = "1" ]; then
  ARGS+=(--enable-lora --max-lora-rank 64 --lora-modules "stance=out/stance-14b/adapter" "explain=out/explain-14b/adapter")
fi
echo "[serve] $MODEL as '$NAME' on :${GS_PORT:-8001} (lora=${GS_LORA:-0})"
exec vllm serve "$MODEL" "${ARGS[@]}"
