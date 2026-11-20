#!/usr/bin/env bash
# Merged HF model -> GGUF Q4_K_M + Ollama Modelfile, for the offline laptop (Ollama).
#   bash export_gguf.sh /tmp/explain-4b-merged out/explain-4b-gguf greenscan-explain-4b
set -euo pipefail
MERGED="$1"; OUT="$2"; NAME="${3:-greenscan-model}"
echo "[cell] gguf build llama.cpp"
mkdir -p "$OUT"
[ -d /tmp/llama.cpp ] || git clone --depth 1 https://github.com/ggml-org/llama.cpp /tmp/llama.cpp
pip install -q /tmp/llama.cpp/gguf-py sentencepiece protobuf
cmake -S /tmp/llama.cpp -B /tmp/llama.cpp/build -DGGML_CUDA=OFF -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF > /tmp/cmake.log
cmake --build /tmp/llama.cpp/build --target llama-quantize -j "$(nproc)" > /tmp/build.log
echo "[cell] gguf convert f16"
python -u /tmp/llama.cpp/convert_hf_to_gguf.py "$MERGED" --outfile /tmp/model-f16.gguf --outtype f16
echo "[cell] gguf quantize Q4_K_M"
/tmp/llama.cpp/build/bin/llama-quantize /tmp/model-f16.gguf "$OUT/$NAME-q4_k_m.gguf" Q4_K_M
rm -f /tmp/model-f16.gguf
cat > "$OUT/Modelfile" <<EOF
FROM ./$NAME-q4_k_m.gguf
PARAMETER temperature 0
PARAMETER num_ctx 4096
EOF
ls -la "$OUT"
echo "[gguf] done: ollama create $NAME -f $OUT/Modelfile"
