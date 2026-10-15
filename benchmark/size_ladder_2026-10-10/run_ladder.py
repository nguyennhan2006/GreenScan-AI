"""Run the constructed-truth cases through GreenScan (offline) and a ladder of LLMs.

usage: run_ladder.py <out.json> [model ...]     (models default: the FPT ladder)
Run from the repository root so configs/ resolve.
"""
import json, os, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(__file__))
CASES = __import__(os.environ.get("LADDER_CASES", "cases")).CASES

os.environ["QUANTUM_LLM_STANCE"] = "off"            # GreenScan arm is the offline product
os.environ["QUANTUM_RUNS_DIR"] = tempfile.mkdtemp(prefix="gs-ladder-runs-")
os.environ["QUANTUM_DOCUMENTS_DIR"] = tempfile.mkdtemp(prefix="gs-ladder-docs-")

from quantum_gw.agents.orchestrator import OrchestratorAgent  # noqa: E402
from quantum_gw.domain.enums import DocumentRole, SourceType, VerificationStatus as V  # noqa: E402
from quantum_gw.domain.models import DocumentInput  # noqa: E402
from quantum_gw.providers.router import ModelGateway  # noqa: E402
from quantum_gw.settings import load_settings  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
out_path = sys.argv[1]
MODELS = sys.argv[2:] or ["gemma-4-26B-A4B-it", "gemma-4-31B-it", "Llama-3.3-70B-Instruct", "GLM-5.2"]

PROMPT = """Bạn là kiểm toán viên kiểm tra một tuyên bố môi trường trong báo cáo của doanh nghiệp.
Chỉ dựa vào ĐOẠN BẰNG CHỨNG dưới đây, hãy xếp tuyên bố vào đúng một nhãn:

- SUPPORTED: bằng chứng nói về cùng chỉ số, cùng kỳ, cùng phạm vi phát thải và ranh giới tổ chức, cùng loại giá trị (thực hiện hay mục tiêu; tuyệt đối, cường độ, tỷ trọng hay mức thay đổi), và giá trị khớp với tuyên bố trong sai số làm tròn của con số được công bố. Có thể cần tự tính (cộng các thành phần, tính % thay đổi).
- CONTRADICTED: bằng chứng nói về cùng chỉ số, cùng kỳ, cùng phạm vi, cùng ranh giới, cùng loại giá trị nhưng giá trị khác ngoài sai số làm tròn, hoặc chiều thay đổi ngược lại.
- NOT_ENOUGH_INFO: bằng chứng không cho phép xác nhận hay bác bỏ: khác chỉ số, khác kỳ, khác phạm vi hoặc ranh giới, mục tiêu so với thực hiện, cường độ so với tuyệt đối, hoặc không liên quan.

TUYÊN BỐ: {claim}

ĐOẠN BẰNG CHỨNG: {evidence}

Trả lời đúng một đối tượng JSON: {{"label": "SUPPORTED" | "CONTRADICTED" | "NOT_ENOUGH_INFO", "ly_do": "<một câu>"}}"""

MAP = {"SUPPORTED": "S", "CONTRADICTED": "C", "NOT_ENOUGH_INFO": "N"}


def greenscan(case):
    cid, family, claim, evidence, ok = case
    settings = load_settings()
    docs = [
        DocumentInput(name="claim.txt", text=claim, role=DocumentRole.CLAIM_SOURCE, source_type=SourceType.INTERNAL),
        DocumentInput(name="evidence.txt", text=evidence, role=DocumentRole.EVIDENCE, source_type=SourceType.EXTERNAL),
    ]
    r = OrchestratorAgent(settings).run(docs)
    statuses = [v.status for v in r.verifications]
    if not statuses:
        label = "N"  # no claim extracted -> the system concludes nothing
    elif V.CONTRADICTED in statuses:
        label = "C"
    elif all(s == V.SUPPORTED for s in statuses):
        label = "S"
    else:
        label = "N"
    reason = " | ".join(f"{v.status.value}: {v.rationale}"[:220] for v in r.verifications) or "không trích được tuyên bố"
    return {"label": label, "raw": [s.value for s in statuses], "reason": reason}


def llm(provider, case):
    cid, family, claim, evidence, ok = case
    t = time.time()
    for attempt in range(3):
        try:
            resp = provider.generate([{"role": "user", "content": PROMPT.format(claim=claim, evidence=evidence)}],
                                     response_schema={"type": "object"})
            parsed = resp.parsed or {}
            raw = str(parsed.get("label", "")).strip().upper()
            return {"label": MAP.get(raw, "?"), "raw": raw or resp.text[:200], "reason": str(parsed.get("ly_do", ""))[:300],
                    "seconds": round(time.time() - t, 1), "usage": resp.usage}
        except Exception as exc:  # noqa: BLE001
            err = repr(exc)[:200]
            time.sleep(3 * (attempt + 1))
    return {"label": "?", "raw": "ERROR", "reason": err, "seconds": round(time.time() - t, 1)}


results = {"cases": [{"id": c[0], "family": c[1], "claim": c[2], "evidence": c[3], "ok": sorted(c[4])} for c in CASES],
           "systems": {}}
t0 = time.time()
results["systems"]["GreenScan (luật, ngoại tuyến)"] = {c[0]: greenscan(c) for c in CASES}
print(f"GreenScan done in {time.time()-t0:.1f}s", flush=True)

gateway = ModelGateway()
fpt = gateway._provider("fpt")
for model in MODELS:
    provider = fpt.bind_model(model)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=6) as pool:
        answers = list(pool.map(lambda c: llm(provider, c), CASES))
    results["systems"][model] = {c[0]: a for c, a in zip(CASES, answers)}
    print(f"{model} done in {time.time()-t0:.1f}s; errors={sum(a['raw']=='ERROR' for a in answers)}", flush=True)
    json.dump(results, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

json.dump(results, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- summary ---
ok = {c[0]: c[4] for c in CASES}
print(f"\n{'system':34s} correct  falseC  falseS  unparsed")
for name, ans in results["systems"].items():
    correct = sum(a["label"] in ok[k] for k, a in ans.items())
    false_c = sum(a["label"] == "C" and "C" not in ok[k] for k, a in ans.items())
    false_s = sum(a["label"] == "S" and "S" not in ok[k] for k, a in ans.items())
    unparsed = sum(a["label"] == "?" for a in ans.values())
    print(f"{name:34s} {correct:2d}/{len(ok)}   {false_c:4d}    {false_s:4d}    {unparsed:4d}")
