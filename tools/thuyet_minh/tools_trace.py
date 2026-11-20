"""Trace the MCP tools, the harness (rules-only and with the free API) and the optional LLM assist stages
for one thesis case. Every prompt sent and every raw reply is recorded. Usage: tools_trace.py cfg.json out.json"""
import json, sys, time, copy, functools
sys.stdout.reconfigure(encoding="utf-8")
from quantum_gw import mcp_tools as T, agent_harness as H
from quantum_gw.providers.base import LLMResponse
from quantum_gw.domain.models import VerificationResult, Claim

cfg = json.load(open(sys.argv[1], encoding="utf-8"))
rid = cfg["run_id"]
out = {"case": cfg["case"], "run_id": rid, "scope": [], "tools": [], "harness": [], "assist": {}}

def timed(fn, *a, **k):
    t = time.perf_counter(); r = fn(*a, **k); return r, round(time.perf_counter() - t, 2)

# 1. scope guard
for q in cfg["scope_requests"]:
    r, s = timed(T.check_scope, q)
    out["scope"].append({"request": q, "result": r, "s": s})

# 2. MCP tools on the chosen claims
calls = []
for c in cfg["claims"]:
    calls += [("claim_attributes", {"claim": c}), ("find_evidence", {"claim": c, "run_id": rid, "k": 3}),
              ("verify_claim", {"claim": c, "run_id": rid}), ("explain_claim", {"claim": c, "run_id": rid})]
calls += [("get_claims", {"run_id": rid, "limit": 5}), ("review_queue", {"run_id": rid, "limit": 5}),
          ("review_assurance", {"text": cfg["assurance_text"]}), ("list_runs", {"limit": 3})]
for name, args in calls:
    try:
        r, s = timed(getattr(T, name), **args)
    except Exception as e:
        r, s = {"error": repr(e)}, 0
    out["tools"].append({"tool": name, "args": args, "result": r, "s": s})
    print("tool", name, s, flush=True)

# 3. harness: a recording wrapper around the free API
class Rec:
    def __init__(self):
        self.llm = H.FreeLLM(); self.log = []
    @property
    def available(self): return self.llm.available
    @property
    def model(self): return self.llm.model
    def __call__(self, messages, json_mode=False):
        import urllib.error
        t = time.perf_counter()
        for wait in (0, 20, 40, 60):
            time.sleep(wait or 2)
            try:
                txt = self.llm(messages, json_mode=json_mode); break
            except urllib.error.HTTPError as e:
                if e.code != 429 or wait == 60: raise
        self.log.append({"messages": messages, "json_mode": json_mode, "reply": txt, "s": round(time.perf_counter() - t, 2)})
        return txt

for q in cfg["harness_requests"]:
    for public in (False, True):
        rec = Rec()
        try:
            r, s = timed(H.run, q, run_id=rid, public=public, llm=rec)
        except Exception as e:
            r, s = {"error": repr(e)}, 0
        out["harness"].append({"request": q, "public": public, "result": r, "llm_log": rec.log, "s": s, "model": rec.model})
        print("harness", public, r.get("status"), r.get("plan_source"), r.get("answer_source"), s, flush=True)

# 4. assist stages (flags off in the product; run here to show the prompt and the guarded reply)
class RecProvider:
    name = "groq"
    def __init__(self): self.rec = Rec(); self.model = self.rec.model
    def generate(self, messages, response_schema=None, task_type=None):
        return LLMResponse(text=self.rec(messages), provider="groq", model=self.model)
class Gateway:
    def __init__(self, p): self.p = p
    def resolve(self, task_type=None): return self.p
    def generate(self, messages, response_schema=None, task_type=None): return self.p.generate(messages)

from quantum_gw.assist.client import StageModel
from quantum_gw.assist.stages import fill_attributes, explain_result
from quantum_gw.assist.prompts import stance_messages, version
from quantum_gw.verification.llm_judge import fenced
from quantum_gw.verification.ir_reader import IRReader
from quantum_gw.agents.verifier import missing_attributes

res = json.load(open(f".quantum/runs/{rid}/result.json", encoding="utf-8"))
vs = {v["claim"]["text"]: v for v in res["verifications"]}
for c in cfg["claims"]:
    v = vs.get(c)
    if not v: print("missing claim in run", c[:60]); continue
    entry = {}
    # S2
    p = RecProvider(); st = StageModel("attributes", "claim_normalization", gateway=Gateway(p))
    claim = Claim.model_validate(copy.deepcopy(v["claim"]))
    before = {a: getattr(claim, a) for a in ("period", "baseline", "scope")}
    stats = fill_attributes([claim], st)
    entry["S2_attributes"] = {"version": st.version, "before": before, "after": {a: getattr(claim, a) for a in before},
                              "assisted_fields": claim.assisted_fields, "stats": stats, "log": p.rec.log}
    # S4 IR reader on claim and top evidence
    p = RecProvider(); ir = IRReader(p)
    ev = v["evidence"][0]["text"] if v["evidence"] else ""
    try:
        lab = ir.label(c, ev)
    except Exception as e:
        lab = ("error", [repr(e)])
    entry["S4_ir_reader"] = {"label": lab, "log": p.rec.log}
    # S5 stance on the top pair (product variant: fenced)
    p = RecProvider(); tag = "5f3a9c1e2b7d"
    msgs = stance_messages(p.model, c, ev, fence=functools.partial(fenced, tag=tag))
    try:
        p.rec(msgs, json_mode=True)
    except Exception as e:
        p.rec.log.append({"messages": msgs, "reply": repr(e)})
    entry["S5_stance"] = {"version": version("stance_fenced", p.model), "rules_relation": v["evidence"][0].get("relation") if v["evidence"] else None,
                          "log": p.rec.log}
    # S6 explanation
    p = RecProvider(); st = StageModel("explain", "claim_explanation", gateway=Gateway(p))
    vr = VerificationResult.model_validate(copy.deepcopy(v))
    shown = explain_result(vr, st, missing_attributes(vr.claim))
    entry["S6_explain"] = {"version": st.version, "shown": shown, "assist": vr.assist, "missing": missing_attributes(vr.claim), "log": p.rec.log}
    out["assist"][c] = entry
    print("assist done", c[:50], flush=True)

json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("saved", sys.argv[2])
