"""The review queue as a CSV table (việc 35): one row per item, queue first, for Excel.

The first row is the mandatory notice (DISCLAIMER_VI, việc 34): a table copied out of
GreenScan must not travel without it. Encoded UTF-8 with BOM so Excel shows Vietnamese.
Scores are whole numbers, so no decimal separator can be misread across locales.
"""

from __future__ import annotations

import csv
import io

from quantum_gw.agents.claim_quality import reason_vi
from quantum_gw.domain.models import AnalysisResult
from quantum_gw.labels_vi import DISCLAIMER_VI, VERDICT

HEADER = ["Thứ tự", "Trong hàng đợi", "Loại mục", "Câu gốc / số liệu", "Tệp", "Trang", "Kết luận của máy",
          "Điểm ưu tiên", "Lý do xếp thứ tự", "Đánh dấu không phải tuyên bố"]


def render_queue_csv(result: AnalysisResult) -> bytes:
    claims = {c.claim_id: c for c in result.claims}
    figures = {f.figure_id: f for f in result.disclosed_figures}
    status = {v.claim.claim_id: v.status.value for v in result.verifications}
    rows = sorted(result.priorities, key=lambda p: (not p.get("in_queue"), p.get("rank") or 10**6))

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow([DISCLAIMER_VI])
    writer.writerow(HEADER)
    for p in rows:
        claim = claims.get(p.get("claim_id") or "")
        figure = figures.get(p.get("item_id") or "")
        source = claim or figure
        flag = getattr(claim, "quality_flag", None)
        writer.writerow([
            p.get("rank", ""),
            "có" if p.get("in_queue") else "không",
            "số liệu công bố" if p.get("item_type") == "figure" else "tuyên bố",
            " ".join((p.get("text") or "").split()),
            getattr(source, "source_name", "") or "",
            getattr(source, "source_page", "") or "",
            VERDICT.get(status.get(p.get("claim_id") or "", ""), "") if claim else "",
            round(p.get("priority_score") or 0),
            " | ".join(p.get("reasons") or []),
            reason_vi(flag) if flag else "",
        ])
    return out.getvalue().encode("utf-8-sig")
