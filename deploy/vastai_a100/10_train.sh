#!/usr/bin/env bash
# Huấn luyện toàn bộ trên A100 (khoảng 3-4 giờ). Log từng bước ra logs/<bước>.log và màn hình.
#   bash 10_train.sh                 # mọi bước
#   STEPS="stance_llm explain" bash 10_train.sh   # chỉ vài bước
# Bước: t1 stance_enc reranker teacher explain stance_llm
set -euo pipefail
cd "$(dirname "$0")/gs_train"
export GS_DATA="$(cd ../data && pwd)" GS_OUT="$(cd .. && pwd)/out" PYTHONUNBUFFERED=1
mkdir -p ../logs "$GS_OUT"
TEACHER="${TEACHER:-openai/gpt-oss-120b}"   # thầy lời giải thích; dự phòng: Qwen/Qwen3-32B-AWQ
STEPS="${STEPS:-t1 stance_enc reranker teacher explain stance_llm}"
run() { local name="$1"; shift; echo "[cell] train $name"; "$@" 2>&1 | tee "../logs/$name.log"; }

for s in $STEPS; do case "$s" in
  t1)         run t1 python -u train_t1.py ;;
  stance_enc) run stance_enc python -u train_stance_enc.py ;;
  reranker)   run reranker python -u train_reranker.py ;;
  teacher)    run teacher python -u gen_teacher.py --model "$TEACHER" --input explain_train.jsonl --field msgs_large \
                --out "$GS_OUT/teacher/explain_teacher.jsonl" --max-len 8192 ;;
  explain)    # học trò 4B (cho bản ngoại tuyến) và 14B (cho bản tự host), cùng dữ liệu thầy
              run explain_4b python -u train_llm_sft.py --base Qwen/Qwen3-4B-Instruct-2507 \
                --train "$GS_OUT/teacher/explain_teacher.jsonl" --name explain-4b --dtype bf16 --merge --merge-dir /tmp/explain-4b-merged
              run explain_14b python -u train_llm_sft.py --base Qwen/Qwen3-14B \
                --train "$GS_OUT/teacher/explain_teacher.jsonl" --name explain-14b --dtype bf16 ;;
  stance_llm) run stance_llm python -u train_llm_sft.py --base Qwen/Qwen3-14B --train stance_sft.jsonl \
                --name stance-14b --dtype bf16 --epochs 3 --lr 1e-4 ;;
  *) echo "unknown step $s"; exit 2 ;;
esac; done
echo "[train] ALL DONE -> $GS_OUT"
