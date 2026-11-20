#!/usr/bin/env bash
# Build the system description: Markdown (from run files) -> figure -> pandoc -> styled .docx
# Usage (repo root): bash tools/thuyet_minh/make_docx.sh <trace_dir>
set -euo pipefail
TRACE="$1"
DOC="docs/09-luan-van/THUYET_MINH_HE_THONG"
PANDOC="$(command -v pandoc || echo D:/anaconda3/Library/bin/pandoc.exe)"
PYPLOT="${PYPLOT:-C:/Python314/python.exe}"
.venv/Scripts/python.exe -I tools/thuyet_minh/build_tm.py "$TRACE"
"$PYPLOT" -X utf8 tools/thuyet_minh/fig_tm.py "$DOC/hinh/pipeline_facts.json" "$DOC/hinh/pipeline_hai_ca.png"
"$PANDOC" "$DOC/THUYET_MINH_HE_THONG.md" -o "$DOC/_pandoc.docx" --toc --toc-depth=3 \
  --reference-doc tools/thuyet_minh/ref.docx --resource-path "$DOC" -f markdown-implicit_figures+implicit_figures
"$PYPLOT" -X utf8 tools/thuyet_minh/post_docx.py "$DOC/_pandoc.docx" "$DOC/THUYET_MINH_HE_THONG.docx"
rm -f "$DOC/_pandoc.docx"
