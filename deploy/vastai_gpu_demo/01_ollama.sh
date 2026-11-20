#!/usr/bin/env bash
# Bật Ollama (nếu chưa chạy), tải mô hình, nạp vào GPU. Chạy lại được bất cứ lúc nào (ví dụ sau khi máy khởi động lại).
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$GS_ROOT"

echo "[cell] ollama start"
if ! curl -s -m 3 "http://$OLLAMA_HOST/api/version" > /dev/null; then
  nohup ollama serve > logs/ollama.log 2>&1 &
  for _ in $(seq 1 30); do
    curl -s -m 3 "http://$OLLAMA_HOST/api/version" > /dev/null && break
    sleep 2
  done
fi
curl -s -m 3 "http://$OLLAMA_HOST/api/version" || { echo "[ollama] !! không khởi động được"; tail -20 logs/ollama.log; exit 1; }
echo

echo "[cell] ollama pull $GS_MODEL"
# Không nối ống vào grep/head ở đây: với `set -o pipefail`, lệnh đọc đóng sớm sẽ làm cả script dừng oan.
HAVE="$(ollama list)"
case "$HAVE" in
  *"$GS_MODEL"*) ;;
  *) ollama pull "$GS_MODEL" > logs/ollama_pull.log 2>&1 || { tail -c 600 logs/ollama_pull.log; exit 1; } ;;
esac
ollama list

echo "[cell] ollama warm"
# Một lượt gọi ngắn để nạp mô hình; sau đó `ollama ps` phải ghi "100% GPU".
WARM="$(curl -s -m 300 "http://$OLLAMA_HOST/api/chat" \
  -d "{\"model\":\"$GS_MODEL\",\"stream\":false,\"messages\":[{\"role\":\"user\",\"content\":\"Trả lời một chữ: xanh\"}]}")"
echo "${WARM:0:300}"
LOADED="$(ollama ps)"
echo "$LOADED"
case "$LOADED" in
  *"100% GPU"*) ;;
  *) echo "[ollama] !! mô hình KHÔNG nằm trọn trên GPU. Dừng ở đây: chạy bằng CPU thì thuê máy này vô ích."
     exit 1 ;;
esac
echo "[ollama] OK"
