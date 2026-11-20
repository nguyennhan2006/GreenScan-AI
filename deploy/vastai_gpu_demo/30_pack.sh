#!/usr/bin/env bash
# Gói kết quả để mang về laptop: bộ nhớ đệm câu trả lời của mô hình, các phiên đã chạy, log.
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$GS_ROOT"
STORE_REL="$(realpath --relative-to="$GS_ROOT" "$GS_STORE")"
tar czf gs_results.tar.gz .quantum/llm_cache "$STORE_REL/runs" logs
ls -la gs_results.tar.gz
wc -l .quantum/llm_cache/*.jsonl
