import json, sys
sys.stdout.reconfigure(encoding="utf-8")
r = json.load(open(sys.argv[1], encoding="utf-8"))
ids = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] else None
W = int(sys.argv[3]) if len(sys.argv) > 3 else 160
risk = {x["claim_id"]: x for x in r["risks"]}
leg = {x["claim_id"]: x for x in r["legal_checks"]}
pri = {x["claim_id"]: x for x in r["priorities"] if x.get("claim_id")}
for v in r["verifications"]:
    c = v["claim"]
    if ids and c["claim_id"] not in ids: continue
    print("=" * 8, c["claim_id"], c["claim_type"], "conf", round(c["confidence"], 2), "| vague", c["vague_terms_matched"])
    print("  TEXT:", c["text"][:W])
    print("  ATTR:", {k: c[k] for k in ("metric", "direction", "values", "units", "period", "baseline", "scope", "is_future_commitment", "quality_flag")})
    extra = {k: v[k] for k in v if k not in ("claim", "evidence", "rationale", "status")}
    print("  STATUS:", v["status"], "| extra:", json.dumps(extra, ensure_ascii=False)[:W])
    print("  RATIONALE:", v["rationale"][:W * 3])
    for e in v["evidence"]:
        print(f"   - {e['chunk_id']} {e['source_name']} s={e['score']:.3f} lex={e['lexical_score']:.3f} sem={e['semantic_score']:.3f} bt={e['below_threshold']} rel={e.get('relation')}/{e.get('relation_method')} :: {e.get('relation_reason','')[:W]} || {e['text'][:90]}")
    k = risk.get(c["claim_id"])
    if k:
        print("  RISK:", k["risk_score"], k["severity"], k["evidence_strength"], k["contradiction_strength"], k["materiality"], "cap:", (k["severity_cap_reason"] or "")[:W])
        for comp in k["components"]:
            print(f"     {comp['name']}: {comp['score']}/{comp['max_score']} [{comp['status']}] {(comp["reason"] or "")[:W]}")
    l = leg.get(c["claim_id"])
    if l:
        print("  LEGAL:", l["issue"], "|", l["legal_finding"][:W], "|", l["legal_risk"], "| rules", l["rules_applied"], l["rules_relevant"][:3], "| src", [s["id"] for s in l["applicable_sources"]][:6])
    p = pri.get(c["claim_id"])
    if p:
        print("  PRIO:", p["rank"], p["priority_score"], p["in_queue"], "|", "; ".join(p["reasons"])[:W])
        print("     ", ", ".join(f"{x['name']}={x['score']}/{x['max_score']}" for x in p["components"]))
