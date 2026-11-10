"""Re-run the CURRENT system (offline) on the documents behind legacy runs, so GS-Eval v2 scores today's code."""
import subprocess, time, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
exe = str(ROOT / ".venv/Scripts/quantum-agent.exe")
blob = ROOT / ".quantum/documents/blobs"
SR = str(blob / "6e/6ec039f79b65354c2cc5464ba4d29a26ef8085d859a1f65af9b274c0edf530ad.pdf")
AR = str(blob / "4f/4f203765a2c39a14aa8c78838d3b21db5b03f663b2c4490b801d17427830446d.pdf")
KLM = str(blob / "69/69f340054d183a25046ad1814625bde5bf0fc9819b6bcfe10a4be3ed9c6a1d44.pdf")
jobs = [
    ("HPG_SR", ["analyze", SR, "--roles", "claim_source", "--source-types", "internal"]),
    ("HPG_SR_ARev", ["analyze", SR, AR, "--roles", "claim_source,evidence", "--source-types", "internal,internal"]),
    ("HPG_AR_SR", ["analyze", AR, SR, "--roles", "claim_source,claim_source", "--source-types", "internal,internal"]),
    ("KLM_packet", ["analyze", KLM, "--roles", "claim_source", "--source-types", "internal"]),
]
log = ROOT / "benchmark/gs_eval_v2/inputs/refresh_runs_cq1.log"
log.write_text("", encoding="utf-8")
for name, args in jobs:
    t0 = time.time()
    r = subprocess.run([exe] + args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    (ROOT / f"benchmark/gs_eval_v2/inputs/refresh_{name}_cq1.out").write_text(out, encoding="utf-8")
    with log.open("a", encoding="utf-8") as f:
        f.write(f"{name} rc={r.returncode} secs={time.time()-t0:.0f} runs={sorted(set(re.findall(r'[0-9a-f]{16}', out)))[:6]}\n")
with log.open("a", encoding="utf-8") as f:
    f.write("DONE\n")
