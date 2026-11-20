#!/usr/bin/env bash
# Chạy trên máy GPU thuê, trong tmux:  bash vast/10_run.sh
# Bốn bước, bước nào hỏng thì dừng:
#   1. Hòa Phát chỉ luật  -> phải trùng kết quả của laptop (171 tuyên bố, cùng kết luận)   ~3-5 phút
#   2. Thử mô hình ba lượt -> số giây mỗi lượt gọi                                          < 1 phút
#   3. Ca mẫu A có mô hình  (23 lượt gọi; laptop CPU: 940 giây)                              vài phút
#   4. Hòa Phát có mô hình                                                                   chưa đo
# Chỉ chạy vài bước: STEPS="parity test" bash vast/10_run.sh
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$GS_ROOT"
STEPS="${STEPS:-parity test caseA caseB}"
PY=".venv/bin/python -u"
RUN="$PY tools/thuyet_minh/run_demo_models.py $GS_STORE"

# Mỗi phút in một dòng [tick]: số dòng bộ nhớ đệm tăng = mô hình đang trả lời; đứng yên nhiều phút = treo.
tick() {
  while sleep 60; do
    echo "[tick] $(date +%H:%M:%S) cache $(cat .quantum/llm_cache/*.jsonl 2>/dev/null | wc -l) dòng; gpu $(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | sed -n 1p)"
  done
}
tick & TICK=$!
trap 'kill $TICK 2>/dev/null || true' EXIT

for step in $STEPS; do
  case "$step" in
    parity)
      echo "[cell] parity: Hòa Phát chỉ luật"
      $RUN rules B 2>&1 | tee logs/rules_B.log | grep -E "^\[run\]|^\[progress\]" | cut -c1-200
      RUN_ID="$(grep -o "run_id [0-9a-f]*" logs/rules_B.log | tail -1 | cut -d" " -f2)"
      $PY vast/check_parity.py "$GS_STORE" vast/expected_B.json "$RUN_ID"
      ;;
    test)
      echo "[cell] test: thử mô hình"
      bash vast/01_ollama.sh > logs/ollama_check.log 2>&1 || { tail -15 logs/ollama_check.log; exit 1; }
      $PY vast/model_test.py 2>&1 | tee logs/model_test.log
      ;;
    caseA)
      echo "[cell] caseA: Ca mẫu A có mô hình"
      $RUN local A 2>&1 | tee logs/local_A.log | grep -E "^\[run\]|^\[audit\]|^\[progress\]" | cut -c1-240
      ;;
    caseB)
      echo "[cell] caseB: Hòa Phát có mô hình"
      $RUN local B 2>&1 | tee logs/local_B.log | grep -E "^\[run\]|^\[audit\]|^\[progress\]" | cut -c1-240
      ;;
    *) echo "[run] không có bước '$step'"; exit 2 ;;
  esac
done
echo "[cell] pack"
bash vast/30_pack.sh
echo "[run] XONG. Tải gs_results.tar.gz về laptop rồi xoá máy (Destroy)."
