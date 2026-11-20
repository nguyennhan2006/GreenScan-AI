#!/usr/bin/env bash
# Chấm mọi mô hình LLM trên bộ đã đăng ký (S5 chấm quan hệ, S6 lời giải thích), rồi vẽ biểu đồ.
#   bash 20_eval.sh
set -euo pipefail
cd "$(dirname "$0")/gs_train"
export GS_DATA="$(cd ../data && pwd)" GS_OUT="$(cd .. && pwd)/out" PYTHONUNBUFFERED=1
mkdir -p ../logs
run() { local name="$1"; shift; echo "[cell] eval $name"; "$@" 2>&1 | tee "../logs/eval_$name.log"; }

run s5_gptoss   python -u eval_stance_llm.py --base openai/gpt-oss-120b --field msgs_large --tag gpt-oss-120b || true
run s5_14b      python -u eval_stance_llm.py --base Qwen/Qwen3-14B --adapter "$GS_OUT/stance-14b/adapter" --field msgs_large --tag q3-14b
run s6_gptoss   python -u eval_explain.py --base openai/gpt-oss-120b --field msgs_large --tag gpt-oss-120b || true
run s6_4b       python -u eval_explain.py --base Qwen/Qwen3-4B-Instruct-2507 --adapter "$GS_OUT/explain-4b/adapter" --field msgs_small --tag student-4b-a100
run s6_14b      python -u eval_explain.py --base Qwen/Qwen3-14B --adapter "$GS_OUT/explain-14b/adapter" --field msgs_small --tag student-14b
run gguf        bash export_gguf.sh /tmp/explain-4b-merged "$GS_OUT/explain-4b-gguf" greenscan-explain-4b || true
run plots       python -u plots.py --results "$GS_OUT" --out "$GS_OUT/hinh"
echo "[eval] DONE -> $GS_OUT (tải về: bash ../../../tools/vastai_pull.sh hoặc scp -r)"
