"""Placeholders for chapters 5–7 and appendix A (LLM stages, MCP, harness, reviewer outputs, every prompt)."""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path


def register(g: dict) -> None:  # noqa: C901
    R, V, CID, TOOLS, RUNS, TRACED, REPO, DOC = (g[k] for k in ("R", "V", "CID", "TOOLS", "RUNS", "TRACED", "REPO", "DOC"))
    table, code, jdump, short, ph = (g[k] for k in ("table", "code", "jdump", "short", "ph"))
    from quantum_gw import agent_harness as H
    from quantum_gw.assist import prompts as P
    from quantum_gw.assist.guards import new_numbers
    from quantum_gw.verification import ir_reader, llm_judge

    def assist(k):
        case, prefix = TRACED[k]
        for text, e in TOOLS[case]["assist"].items():
            if text.startswith(prefix):
                return e
        raise KeyError(k)

    def msgs_block(messages, system_note=None, limit=None):
        out = []
        for m in messages:
            content = m["content"]
            if m["role"] == "system" and system_note:
                content = system_note
            if limit and len(content) > limit:
                content = content[:limit].rstrip() + f"\n… (cắt bớt, tổng {len(m['content'])} ký tự)"
            out.append(f"[{m['role']}]\n{content}")
        return code("\n\n".join(out))

    @ph
    def n_tasks():
        import yaml
        return str(len(yaml.safe_load((REPO / "configs/prompt_router/scope_v1.yaml").read_text(encoding="utf-8"))["tasks"]))

    @ph
    def n_htools():
        return str(len(H.TOOLS))

    @ph
    def n_fewshot():
        return str(len(H.FEW_SHOT))

    @ph
    def run_a():
        return f"`{RUNS['A']}`"

    @ph
    def run_b():
        return f"`{RUNS['B']}`"

    # ------------------------------------------------------------------ chapter 5: assist stages
    @ph
    def l5_overview():
        rows = []
        for k in V:
            e = assist(k)
            s5 = e["S5_stance"]["log"][0]["reply"] if e["S5_stance"]["log"] else ""
            m = re.search(r'"relation"\s*:\s*"(\w+)"', s5)
            rows.append([k, ", ".join(e["S2_attributes"]["assisted_fields"]) or "không điền", e["S4_ir_reader"]["label"][0],
                         e["S5_stance"]["rules_relation"], m.group(1) if m else s5[:40],
                         "hiển thị" if e["S6_explain"]["shown"] else "bị chặn", V[k]["status"]])
        return table(["Mã", "S2: trường được điền", "S4: nhãn IR", "Quan hệ của luật (đoạn 1)", "S5: quan hệ của LLM (đoạn 1)",
                      "S6: lời giải thích", "Kết luận sản phẩm (không đổi)"], rows)

    @ph
    def l5_s2():
        rows = []
        for k in V:
            a = assist(k)["S2_attributes"]
            reply = a["log"][0]["reply"] if a["log"] else "(không gọi: đủ cả ba trường)"
            rows.append([k, a["before"], a["after"], ", ".join(a["assisted_fields"]) or "—", a["stats"].get("non_verbatim_dropped"),
                         short(reply, 260)])
        return table(["Mã", "Trước (period, baseline, scope)", "Sau", "Trường được điền", "Bị loại vì không nguyên văn", "Trả lời thô của LLM"], rows)

    @ph
    def l5_s2_msgs_b1():
        a = assist("B1")["S2_attributes"]
        if not a["log"]:
            return "_Không có lời gọi._"
        return msgs_block(a["log"][0]["messages"], system_note="(prompt hệ thống attr-v1, toàn văn ở Phụ lục A.6)") + \
            "\n\nTrả lời thô:\n\n" + code(a["log"][0]["reply"], "json")

    @ph
    def l5_s4():
        out = []
        for k in ("A1", "B1"):
            s = assist(k)["S4_ir_reader"]
            out.append(f"**{k}** — nhãn IR: `{s['label'][0]}`; ghi chú: {short('; '.join(s['label'][1]), 400)}")
            for i, l in enumerate(s["log"], 1):
                what = "câu tuyên bố" if i == 1 else "đoạn bằng chứng số 1"
                prompt_user = l["messages"][-1]["content"]
                sentence = prompt_user.split("CÂU:")[-1].strip() if "CÂU:" in prompt_user else prompt_user[-300:]
                out.append(f"Lời gọi {i} ({what}); câu gửi đi: “{short(sentence, 300)}”. Trả lời thô:\n\n" + code(l["reply"][:1800], "json"))
        return "\n\n".join(out)

    @ph
    def l5_s5():
        rows = []
        for k in V:
            s = assist(k)["S5_stance"]
            reply = s["log"][0]["reply"] if s["log"] else ""
            rows.append([k, s["version"], V[k]["evidence"][0]["chunk_id"], s["rules_relation"], short(reply, 330)])
        return table(["Mã", "Phiên bản prompt", "Đoạn được hỏi", "Quan hệ do luật", "Trả lời thô của LLM"], rows)

    @ph
    def l5_s5_msgs_a2():
        s = assist("A2")["S5_stance"]
        return msgs_block(s["log"][0]["messages"], system_note="(prompt hệ thống stance-v3f = STANCE_LARGE + STANCE_FENCE, toàn văn ở Phụ lục A.4–A.5)") + \
            "\n\nTrả lời thô:\n\n" + code(s["log"][0]["reply"], "json")

    @ph
    def l5_s6():
        out = []
        for k in V:
            s = assist(k)["S6_explain"]
            v = V[k]
            if not s["log"]:
                out.append(f"**{k}**: không có lời gọi.")
                continue
            reply = s["log"][0]["reply"]
            try:
                parsed = json.loads(re.search(r"\{.*\}", reply, re.S).group(0))
            except Exception:  # noqa: BLE001
                parsed = {}
            text = f"{parsed.get('explanation', '')} {parsed.get('next_action', '')}"
            sources = [v["claim"]["text"], v["rationale"], *[f"{e['source_name']} {e.get('page')} {e['text']}" for e in v["evidence"]]]
            bad = new_numbers(text, *sources) if text.strip() else []
            if s["shown"]:
                verdict = "**hiển thị** cạnh lý do của luật"
            elif not parsed:
                verdict = ("**bị loại**: câu trả lời không phải JSON hợp lệ (`parse_json` trả rỗng), "
                           "hệ thống không lưu bộ nhớ đệm và giữ lý do của luật")
            else:
                verdict = f"**bị chặn**: có số không xuất hiện trong nguồn: {', '.join(sorted(bad))}"
            out.append(f"**{k}** (`{s['version']}`; thuộc tính còn thiếu đưa vào prompt: {', '.join(s['missing']) or 'không'}) — {verdict}.\n\n" +
                       code(reply, "json"))
        return "\n\n".join(out)

    @ph
    def l5_s6_msgs_b1():
        s = assist("B1")["S6_explain"]
        return msgs_block(s["log"][0]["messages"], system_note="(prompt hệ thống explain-v2, toàn văn ở Phụ lục A.8)", limit=3500)

    # ------------------------------------------------------------------ chapter 6: MCP and harness
    @ph
    def l6_tools():
        src = (REPO / "src/quantum_gw/mcp_server.py").read_text(encoding="utf-8")
        names = re.findall(r"@\w+\.tool\(.*\)\n\s*def (\w+)\(", src)
        desc = {
            "check_scope": ("request", "Chốt phạm vi bằng luật: trong phạm vi / thiếu thông tin / ngoài phạm vi, nhiệm vụ, slot"),
            "ask_greenscan": ("request, run_id, public=false", "Chạy harness: chốt phạm vi → lập kế hoạch → gọi công cụ → câu trả lời có kiểm"),
            "analyze_documents": ("paths (1–5), roles, source_types", "Chạy luồng phân tích 10 bước (hồ sơ offline); ≤5 tệp, ≤80 MB"),
            "list_runs": ("limit=10", "Các phiên đã lưu: mã, tài liệu, số tuyên bố, tóm tắt"),
            "get_claims": ("run_id, status, limit, offset", "Danh sách tuyên bố và kết luận, lọc theo status"),
            "review_queue": ("run_id, limit", "Hàng soát đã xếp ưu tiên"),
            "verify_claim": ("claim, run_id", "Kết luận đã có của một tuyên bố (khớp ≥ 0,85); không khớp thì chỉ trả thuộc tính và bằng chứng, không kết luận"),
            "claim_attributes": ("claim", "Thuộc tính câu nêu và còn thiếu (không cần phiên)"),
            "find_evidence": ("claim, run_id, k≤10", "Đoạn bằng chứng trong kho của phiên (dựng chỉ mục từ clean.jsonl)"),
            "review_assurance": ("text", "Khớp mẫu câu kết luận đảm bảo ISSA 5000 / ISAE 3000"),
            "explain_claim": ("claim, run_id", "Lý do của luật cho kết luận đã có"),
            "domain_lookup": ("query, kind, k≤3", "Tri thức nền (khái niệm, dấu hiệu tẩy xanh, cách tính, văn bản) từ `data/domain_kb/`; "
                              "không bao giờ là bằng chứng hay kết luận (D-2026-11-14-02, thêm 14/11)"),
        }
        rows = [[i, f"`{n}`", *desc.get(n, ("", ""))] for i, n in enumerate(names, 1)]
        return table(["#", "Công cụ", "Tham số", "Việc làm"], rows) + f"\n\nSố công cụ đăng ký trong `mcp_server.py`: **{len(names)}**."

    for case in ("A", "B"):
        def _scope(c=case):
            rows = []
            for s in TOOLS[c]["scope"]:
                r = s["result"]
                rows.append([s["request"], r["status"], r.get("category"), ", ".join(r.get("tasks") or []),
                             r.get("slots", {}).get("claim") and "có" or "—", r.get("warning")])
            return table(["Yêu cầu", "Trạng thái", "Nhóm ngoài phạm vi", "Nhiệm vụ", "Slot tuyên bố", "Cảnh báo trả về"], rows, {0: 110, 5: 200})
        _scope.__name__ = f"l6_scope_{case.lower()}"
        ph(_scope)

        def _calls(c=case):
            out = []
            for t in TOOLS[c]["tools"]:
                args = {k: (short(v, 80) if isinstance(v, str) else v) for k, v in t["args"].items()}
                out.append(f"**`{t['tool']}`** `{json.dumps(args, ensure_ascii=False)}` — {t['s']} s\n\n" + jdump(t["result"], 1600))
            return "\n\n".join(out)
        _calls.__name__ = f"l6_calls_{case.lower()}"
        ph(_calls)

    def harness_block(case, i):
        pair = [h for h in TOOLS[case]["harness"] if h["request"] == TOOLS[case]["harness"][2 * i]["request"]]
        rules, llm = pair[0], pair[1]
        out = [f"**Yêu cầu:** “{rules['request']}”  \n**Mã phiên:** `{TOOLS[case]['run_id']}`"]
        rr = rules["result"]
        if rr.get("status") in ("out_of_scope", "need_info"):
            lr = llm["result"]
            out.append(f"Cả hai chế độ (`public=false` và `public=true`) **dừng ở chốt phạm vi**: trạng thái `{rr.get('status')}`, "
                       f"nhóm `{rr.get('category')}`; số lời gọi LLM: {rr.get('llm_calls', 0)} và {lr.get('llm_calls', 0)}; "
                       f"không công cụ nào được chạy. Người dùng nhận:")
            out.append(code(rr.get("warning") or ""))
            return "\n\n".join(out)
        out.append(f"*(a) Chế độ chỉ luật (`public=false`, 0 lời gọi LLM, {rules['s']} s).* Trạng thái `{rr.get('status')}`; "
                   f"nhiệm vụ {rr.get('tasks')}; kế hoạch theo luật:")
        out.append(code(json.dumps([{k: s[k] for k in ('tool', 'args')} for s in rr.get("steps", [])], ensure_ascii=False, indent=1), "json")
                   if rr.get("steps") else f"_Không có kế hoạch: {rr.get('warning')}_")
        if rr.get("note"):
            out.append(f"Ghi chú harness trả kèm (phần yêu cầu chưa chạy được): “{rr['note']}”")
        out.append("Câu trả lời soạn sẵn theo luật (`rules_answer`):\n\n" + code(rr.get("answer") or rr.get("warning") or ""))
        lr = llm["result"]
        out.append(f"*(b) Có LLM (`public=true`, mô hình `{llm['model']}`, {lr.get('llm_calls', 0)} lời gọi, {llm['s']} s).* "
                   f"Nguồn kế hoạch: `{lr.get('plan_source')}`; nguồn câu trả lời: `{lr.get('answer_source')}`.")
        for j, call in enumerate(llm["llm_log"], 1):
            role = "lập kế hoạch" if call["json_mode"] else "viết câu trả lời"
            note = ("(prompt PLANNER đã điền danh sách công cụ, toàn văn ở Phụ lục A.1)" if call["json_mode"]
                    else "(prompt ANSWER, toàn văn ở Phụ lục A.3)")
            nfs = 2 * len(H.FEW_SHOT)
            shown = [m for m in call["messages"] if not (call["json_mode"] and m in call["messages"][1:1 + nfs])]
            fs = (f" {nfs} thông điệp few-shot ({len(H.FEW_SHOT)} cặp user/assistant ở Phụ lục A.2) nằm giữa system và user, không in lại."
                  if call["json_mode"] else "")
            out.append(f"Lời gọi {j} ({role}, {call['s']} s).{fs} Thông điệp gửi đi:")
            out.append(msgs_block(shown, system_note=note, limit=2200))
            out.append("Trả lời thô của LLM:\n\n" + code(call["reply"]))
        if lr.get("reasoning"):
            out.append(f"Trường `suy_luan` (hiện trong vết cho người soát): “{lr['reasoning']}”")
        if lr.get("steps"):
            trace = [{"tool": s["tool"], "args": s["args"], "ok": s["ok"],
                      "result": json.loads(short(json.dumps(s["result"], ensure_ascii=False), 100000))} for s in lr["steps"]]
            out.append("Vết thực thi công cụ (kết quả rút gọn):\n\n" + jdump(trace, 2400))
        out.append("**Câu trả lời cuối cùng người dùng nhận:**\n\n" + code(lr.get("answer") or lr.get("warning") or ""))
        return "\n\n".join(out)

    for case, n in (("A", 2), ("B", 3)):
        for i in range(n):
            def _h(c=case, k=i):
                return harness_block(c, k) if c in TOOLS and len(TOOLS[c]["harness"]) > 2 * k else "_Chưa có vết._"
            _h.__name__ = f"l6_harness_{case.lower()}{i + 1}"
            ph(_h)

    # ------------------------------------------------------------------ chapter 7: reviewer outputs
    @ph
    def l7_studio_a():
        from quantum_gw.domain.models import AnalysisResult
        from quantum_gw.studio.document import _missing_attributes
        from quantum_gw.studio.suggest import suggest, apply
        res = AnalysisResult.model_validate(R["A"]["result"])
        ver = {v.claim.claim_id: v for v in res.verifications}
        rows = []
        for c in res.claims:
            v = ver[c.claim_id]
            diag = {"claim_id": c.claim_id, "missing": _missing_attributes(c), "vague_terms": c.vague_terms_matched,
                    "status": v.status.value,
                    "evidence": [{"source_name": e.source_name, "page": e.page, "relation": e.relation, "text": e.text[:400]}
                                 for e in v.evidence[:4]]}
            for s in suggest(diag, c.text):
                if s is None:
                    continue
                rows.append([short(c.text, 70), s.kind, s.rule_code, apply(c.text, s) or "—", short(s.reason, 160)])
        return table(["Câu gốc", "Loại gợi ý", "Mã luật", "Câu sau khi áp gợi ý", "Lý do"], rows)

    @ph
    def l7_workpaper():
        from quantum_gw.domain.models import AnalysisResult
        from quantum_gw.workpaper import render_workpaper
        out_dir = DOC / "phu_luc"
        out_dir.mkdir(exist_ok=True)
        lines = []
        for c in ("A", "B"):
            html = render_workpaper(AnalysisResult.model_validate(R[c]["result"]), [], label=f"Ca {c}")
            p = out_dir / f"giay_lam_viec_ca_{c}.html"
            p.write_text(html, encoding="utf-8")
            heads = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.S)]
            lines.append(f"- **Ca {c}**: `{p.relative_to(DOC).as_posix()}` ({len(html) // 1024} KB). Các mục: " + "; ".join(heads))
        return "\n".join(lines)

    # ------------------------------------------------------------------ appendix A: every prompt
    def router_prompt():
        p = REPO / "training" / "router_data.py"
        spec = importlib.util.spec_from_file_location("router_data_tm", p)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            return mod.PLANNER_SYSTEM
        except Exception as e:  # noqa: BLE001
            src = p.read_text(encoding="utf-8")
            m = re.search(r"PLANNER_SYSTEM = \((.*?)\n\)", src, re.S)
            return (m.group(1) if m else f"(không đọc được: {e})")

    @ph
    def pa_planner():
        tools = "\n".join(f"- {n}({', '.join(a)}): {d}" for n, (_, a, d) in H.TOOLS.items())
        return code(H.PLANNER.format(tools=tools))

    @ph
    def pa_fewshot():
        return code("\n\n".join(f"[user]\n{q}\n\n[assistant]\n{json.dumps(a, ensure_ascii=False)}" for q, a in H.FEW_SHOT))

    @ph
    def pa_answer():
        return code(H.ANSWER)

    @ph
    def pa_stance_large():
        return code(P.STANCE_LARGE)

    @ph
    def pa_stance_small():
        return code(P.STANCE_SMALL)

    @ph
    def pa_stance_fence():
        return code(P.STANCE_FENCE.strip())

    @ph
    def pa_stance_v2():
        return code(llm_judge.SYSTEM_PROMPT)

    @ph
    def pa_attr_large():
        return code(P.ATTR_LARGE)

    @ph
    def pa_attr_small():
        return code(P.ATTR_SMALL)

    @ph
    def pa_explain_large():
        return code(P.EXPLAIN_LARGE)

    @ph
    def pa_explain_small():
        return code(P.EXPLAIN_SMALL)

    @ph
    def pa_ir():
        return code(ir_reader.PROMPT)

    @ph
    def pa_router():
        return code(router_prompt())

    @ph
    def pa_versions():
        rows = [[f"{st} / {fam}", v, "PROMPTS trong assist/prompts.py"] for (st, fam), (v, _) in P.PROMPTS.items()]
        rows += [["stance (mô hình chưa biết)", llm_judge.PROMPT_VERSION, "verification/llm_judge.py"],
                 ["harness: lập kế hoạch", "PLANNER + FEW_SHOT", "agent_harness.py"],
                 ["harness: trả lời", "ANSWER", "agent_harness.py"],
                 ["S4 đọc số liệu (IR)", "PROMPT", "verification/ir_reader.py"],
                 ["bộ định tuyến (huấn luyện)", "PLANNER_SYSTEM", "training/router_data.py"]]
        return table(["Bước / họ mô hình", "Phiên bản", "Nơi định nghĩa"], rows)

    @ph
    def pa_message_builders():
        import inspect
        src = "\n\n".join(inspect.getsource(f) for f in (P.stance_messages, P.attr_messages, P.explain_messages))
        return code(src, "python")
