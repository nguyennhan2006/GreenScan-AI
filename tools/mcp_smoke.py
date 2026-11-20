"""Start the GreenScan MCP server over stdio like a client would, list its tools, call three of them.

    .venv/Scripts/python.exe -X utf8 tools/mcp_smoke.py
"""
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


async def main() -> int:
    params = StdioServerParameters(command=sys.executable, args=["-X", "utf8", "-m", "quantum_gw.mcp_server"],
                                   env={"QUANTUM_PROFILE": "offline", "PYTHONPATH": str(ROOT / "src"),
                                        "PYTHONIOENCODING": "utf-8", "SYSTEMROOT": "C:\Windows"})
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = [t.name for t in (await s.list_tools()).tools]
            print("tools:", tools)
            for name, args in (("check_scope", {"request": "Hòa Phát có gian lận số liệu không?"}),
                               ("claim_attributes", {"claim": "Năm 2024 giảm 12% nước tiêu thụ so với 2020."}),
                               ("ask_greenscan", {"request": 'Tuyên bố "Năm 2024 giảm 12% nước tiêu thụ so với 2020" còn thiếu gì?'})):
                res = await s.call_tool(name, args)
                text = res.content[0].text if res.content else str(res)
                print(f"{name}: {text[:220]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
