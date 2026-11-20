"""GreenScan MCP server (stdio) for the minimum machine: 8–16 GB RAM, no GPU, offline profile.

    .venv/Scripts/python.exe -m quantum_gw.mcp_server          # or: greenscan-mcp
Claude Desktop / any MCP client: see deploy/mcp/claude_desktop_config.json and docs/04-data-ai/MCP_MAY_TOI_THIEU.md.

Tools are the product's own code (mcp_tools.py); `ask_greenscan` runs the bounded harness (agent_harness.py), which
may call the free API (Groq) only for public documents. Every free-text input passes the scope guard: out of scope ->
a warning and nothing else runs.
"""
from __future__ import annotations

import os

os.environ.setdefault("QUANTUM_PROFILE", "offline")

from mcp.server.mcpserver import MCPServer  # noqa: E402

from quantum_gw import agent_harness, mcp_tools as T  # noqa: E402

INSTRUCTIONS = """GreenScan kiểm tra tuyên bố MÔI TRƯỜNG trong báo cáo phát triển bền vững / thường niên của doanh nghiệp
Việt Nam, đối chiếu với bằng chứng trong tài liệu. Kết luận chỉ đến từ quy trình của hệ thống (analyze_documents),
các công cụ khác đọc lại kết luận, tìm bằng chứng, nêu thuộc tính. Gọi check_scope trước với yêu cầu tự do; nếu
stop = true thì báo warning cho người dùng và dừng. Hệ thống không kết luận gian lận, không tư vấn đầu tư, không viết
hay làm đẹp tuyên bố. Máy chạy là máy tối thiểu (CPU): tối đa 5 tệp, 80 MB mỗi lần phân tích.
Câu hỏi về khái niệm, cách tính, dấu hiệu tẩy xanh, claim chuẩn: dùng domain_lookup. Kết quả của domain_lookup là tri
thức nền, không bao giờ được trích như bằng chứng về doanh nghiệp."""

server = MCPServer("greenscan", instructions=INSTRUCTIONS, version="mcp-v1")


@server.tool(description="Kiểm tra yêu cầu có thuộc phạm vi GreenScan không; trả status ok / need_info / out_of_scope, việc cần làm và thông tin đã có.")
def check_scope(request: str) -> dict:
    return T.check_scope(request)


@server.tool(description="Hỏi GreenScan bằng câu tự nhiên: chặn phạm vi, lập kế hoạch, gọi công cụ, trả lời có kiểm. public=true mới dùng API miễn phí (chỉ tài liệu công khai).")
def ask_greenscan(request: str, run_id: str | None = None, public: bool = False) -> dict:
    return agent_harness.run(request, run_id=run_id, public=public)


@server.tool(description="Phân tích 1–5 tệp báo cáo (PDF/DOCX/TXT) bằng quy trình ngoại tuyến (luật + so số + truy xuất từ vựng); trả run_id và tóm tắt.")
def analyze_documents(paths: list[str], roles: list[str] | None = None, source_types: list[str] | None = None) -> dict:
    return T.analyze_documents(paths, roles, source_types)


@server.tool(description="Các phiên phân tích đã lưu (mới nhất trước).")
def list_runs(limit: int = 10) -> list[dict]:
    return T.list_runs(limit)


@server.tool(description="Tuyên bố và kết luận của một phiên; status lọc theo SUPPORTED / PARTIALLY_SUPPORTED / CONTRADICTED / INSUFFICIENT_EVIDENCE.")
def get_claims(run_id: str, status: str | None = None, limit: int = 20, offset: int = 0) -> dict:
    return T.get_claims(run_id, status, limit, offset)


@server.tool(description="Hàng soát mà quy trình đã xếp (độ trọng yếu, nghĩa vụ pháp lý, rủi ro), ưu tiên cao trước; câu nghi không phải tuyên bố bị để ngoài hàng.")
def review_queue(run_id: str, limit: int = 10) -> dict:
    return T.review_queue(run_id, limit)


@server.tool(description="Kết luận của hệ thống cho một tuyên bố trong phiên đã chạy; nếu phiên chưa xét câu đó thì chỉ trả thuộc tính và bằng chứng, không kết luận.")
def verify_claim(claim: str, run_id: str) -> dict:
    return T.verify_claim(claim, run_id)


@server.tool(description="Chỉ số, số liệu, kỳ, năm gốc, phạm vi mà một câu tuyên bố nêu, và những gì còn thiếu (luật của sản phẩm).")
def claim_attributes(claim: str) -> dict:
    return T.claim_attributes(claim)


@server.tool(description="Các đoạn bằng chứng cho một tuyên bố trong kho tài liệu của phiên (truy xuất từ vựng, k ≤ 10).")
def find_evidence(claim: str, run_id: str, k: int = 5) -> dict:
    return T.find_evidence(claim, run_id, k)


@server.tool(description="Đọc tờ đảm bảo độc lập: khớp mẫu câu kết luận ISSA 5000 / ISAE 3000 (mức đảm bảo, loại kết luận).")
def review_assurance(text: str) -> dict:
    return T.review_assurance(text)


@server.tool(description="Lý do của quy tắc cho kết luận đã có của một tuyên bố trong phiên.")
def explain_claim(claim: str, run_id: str) -> dict:
    return T.explain_claim(claim, run_id)


@server.tool(description="Tri thức nền (không phải bằng chứng): khái niệm, dấu hiệu rủi ro, cách tính, claim chuẩn, vụ việc, văn bản pháp lý. kind lọc concept / signal / formula / pattern / case / legal.")
def domain_lookup(query: str, kind: str | None = None, k: int = 3) -> dict:
    return T.domain_lookup(query, kind, k)


@server.tool(description="Tiền lệ: tuyên bố tương tự mà người soát đã chốt (kết luận của máy, của người, lý do). Không phải bằng chứng, không đổi kết luận.")
def precedents(claim: str, k: int = 3) -> dict:
    return T.precedents(claim, k)


@server.tool(description="Thử một bộ quy tắc nội bộ đã tải lên (org_id hoặc org_id@phiên_bản) trên một câu, không có bằng chứng. Quy tắc nội bộ không đổi kết luận.")
def org_pack_preview(pack: str, claim: str, sector: str = "") -> dict:
    return T.org_pack_preview(pack, claim, sector)


def main() -> None:
    os.chdir(T.ROOT)   # configs/ and .quantum/runs are relative to the repo, whatever folder the MCP client starts in
    server.run("stdio")


if __name__ == "__main__":
    main()
