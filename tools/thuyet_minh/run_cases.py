"""Run GreenScan's 10-step pipeline on the two thesis cases, recording step timings. cwd must be the repo."""
import json, sys, time, tracemalloc
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
from quantum_gw.agents.orchestrator import OrchestratorAgent
from quantum_gw.domain.models import DocumentInput
from quantum_gw.domain.enums import DocumentRole, SourceType
from quantum_gw.settings import load_settings


def peak_mb():
    import ctypes, ctypes.wintypes as w
    class PMC(ctypes.Structure):
        _fields_ = [("cb", w.DWORD), ("PageFaultCount", w.DWORD)] + [(n, ctypes.c_size_t) for n in (
            "PeakWorkingSetSize", "WorkingSetSize", "QPPPU", "QPPU", "QPNPPU", "QNPPU", "PagefileUsage", "PeakPagefileUsage")]
    c = PMC(); c.cb = ctypes.sizeof(c)
    k = ctypes.windll.kernel32; k.GetCurrentProcess.restype = ctypes.c_void_p
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(PMC), w.DWORD]
    ctypes.windll.psapi.GetProcessMemoryInfo(k.GetCurrentProcess(), ctypes.byref(c), c.cb)
    return c.PeakWorkingSetSize / 1e6

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
CASES = {
    "A": [("data/sample/company_esg_2024.txt", "claim_source", "internal"),
          ("data/sample/financial_2024.txt", "evidence", "financial"),
          ("data/sample/legal_notice_2024.txt", "evidence", "legal")],
    "B": [("data/real_cases/sources/originals/HPG_Sustainability_Report_2025.pdf", "claim_source", "internal"),
          ("data/real_cases/sources/originals/HPG_Annual_Report_2024.pdf", "evidence", "financial")],
}
which = sys.argv[2:] or list(CASES)
s = load_settings()
for case in which:
    docs = [DocumentInput(path=p, role=DocumentRole(r), source_type=SourceType(t)) for p, r, t in CASES[case]]
    steps, t0 = [], time.perf_counter()
    last = [t0]
    def prog(name, i, n, detail):
        now = time.perf_counter()
        steps.append({"step": name, "index": i, "of": n, "detail": detail, "t": round(now - t0, 2)})
        print(f"[{case}] {i}/{n} {name} {detail}", flush=True) if not name.startswith(("retrieve", "check")) or detail.startswith("1/") else None
    res = OrchestratorAgent(s).run(docs, progress=prog)
    peak = peak_mb()
    total = round(time.perf_counter() - t0, 2)
    rid = Path(res.output_directory).name
    info = {"case": case, "run_id": rid, "seconds": total, "peak_working_set_mb": round(peak, 1), "steps": steps,
            "summary": res.summary.model_dump(mode="json"), "profile": "offline",
            "flags": {"stance_llm": bool(s.verification.llm_judge if hasattr(s.verification, 'llm_judge') else None),
                      "assist_explain": s.verification.assist_explain,
                      "assist_attributes": s.verification.assist_attributes,
                      "claim_model_dir": s.claim_extraction.claim_model_dir,
                      "version": s.version, "config_hash": s.stable_hash()}}
    (OUT / f"case_{case}.json").write_text(json.dumps(info, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(case, rid, total, "s", res.summary.model_dump(mode="json"), flush=True)
