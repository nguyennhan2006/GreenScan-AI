"""Run the current system (offline profile, CPU) on extra companies for GS-Eval v2 pool A."""
import json, subprocess, time, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
plan = json.loads((ROOT / "benchmark/gs_eval_v2/inputs/extra_runs_plan.json").read_text(encoding="utf-8"))
log = ROOT / "benchmark/gs_eval_v2/inputs/extra_runs_cq1.log"
log.write_text("", encoding="utf-8")
exe = str(ROOT / ".venv/Scripts/quantum-agent.exe")
for p in plan:
    args = [exe, "analyze", p["sr"]] + ([p["ar"]] if p.get("ar") else [])
    args += ["--roles", "claim_source,evidence" if p.get("ar") else "claim_source",
             "--source-types", "internal,internal" if p.get("ar") else "internal"]
    t0 = time.time()
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    (ROOT / f"benchmark/gs_eval_v2/inputs/run_{p["ticker"]}_cq1.out").write_text(out, encoding="utf-8")
    rid = re.findall(r"\b[0-9a-f]{16}\b", out)
    with log.open("a", encoding="utf-8") as f:
        f.write(f"{p['ticker']} rc={r.returncode} secs={time.time()-t0:.0f} run={rid[:1]}\n")
with log.open("a", encoding="utf-8") as f:
    f.write("DONE\n")
