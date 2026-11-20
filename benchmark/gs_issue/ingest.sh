#!/usr/bin/env bash
# Gom kết quả 12 notebook GS-Issue (11/11/2026), chấm, chọn tập thật cân bằng, vẽ lại biểu đồ.
#   bash benchmark/gs_issue/ingest.sh            (chạy từ gốc repo)
set -u
K="tranthuytien2511/gsi-small-ae nngocnh/gsi-small-b1 phanvnhtrng/gsi-small-b2 letranchauanh/gsi-small-b3
thanhhuyen11/gsi-14b-ae quynhnhu82/gsi-14b-b1 phantrnanna/gsi-14b-b2 nguyenlethaonhi123/gsi-14b-b3
phannguyngiahuy11a5/gsi-32b-ae nguyntrquangtrung/gsi-32b-b1 nguynthanhnhnn/gsi-32b-b2 khanhnguyenm841/gsi-32b-b3"
mkdir -p benchmark/gs_issue/kaggle_out benchmark/gs_issue/out
for k in $K; do
  st=$(python -I -X utf8 tools/kaggle/kapi.py status "$k" 2>&1 | grep -o 'KernelWorkerStatus.[A-Z]*')
  echo "$k $st"
  if [ "$st" = "KernelWorkerStatus.COMPLETE" ]; then
    d="benchmark/gs_issue/kaggle_out/${k#*/}"
    [ -d "$d" ] || .venv/Scripts/python.exe -I -X utf8 tools/kaggle/kapi.py output "$k" --dest "$d" 2>&1 | tail -1
    find "$d" -name '*__gsi_*.jsonl' -exec cp {} benchmark/gs_issue/out/ \;
    find "$d" -name '*_summary.json' -exec sh -c 'echo "   $(cat "$1")"' _ {} \;
  fi
done
ls benchmark/gs_issue/out/
.venv/Scripts/python.exe -X utf8 benchmark/gs_issue/score_issue.py > /dev/null && echo "scored -> benchmark/gs_issue/results/SCORE_ISSUE.md"
[ -f benchmark/gs_issue/data/layer_b_silver.jsonl ] && python -X utf8 benchmark/gs_issue/select_real.py
.venv/Scripts/python.exe -X utf8 benchmark/data_card.py > /dev/null
.venv/Scripts/python.exe -X utf8 benchmark/gs_issue/make_figs.py
