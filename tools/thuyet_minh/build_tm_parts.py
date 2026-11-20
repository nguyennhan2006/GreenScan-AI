"""Placeholders for chapters 4–9 and the appendices of the system description (see build_tm.py)."""
from __future__ import annotations

import json
from collections import Counter


def register(g: dict) -> None:  # noqa: C901 - one place for every generated block
    R, V, CID, TIME, TOOLS, RUNS, TRACED = (g[k] for k in ("R", "V", "CID", "TIME", "TOOLS", "RUNS", "TRACED"))
    table, code, jdump, short, vn, cell, events, ph, by_claim = (
        g[k] for k in ("table", "code", "jdump", "short", "vn", "cell", "events", "ph", "by_claim"))

    def keys_of(case):
        return [k for k in V if TRACED[k][0] == case]

    # ------------------------------------------------------------------ figure facts (Hình 2.1)
    @ph
    def pipeline_facts():
        def facts(c):
            r = R[c]["result"]
            s = r["summary"]
            ev = sum(len(v["evidence"]) for v in r["verifications"])
            rej = sum(1 for x in R[c]["extract"] if x.get("rejected_reason"))
            q = sum(1 for p in r["priorities"] if p["in_queue"])
            gates = Counter(gg["status"] for gg in r["quality_gates"])
            parts = [f"{k.replace('INSUFFICIENT_EVIDENCE', 'INSUFFICIENT')} {v}" for k, v in sorted(s["status_counts"].items(), key=lambda x: -x[1])]
            lines, cur = [], ""
            for part in parts:
                if cur and len(cur) + len(part) + 3 > 32:
                    lines.append(cur); cur = part
                else:
                    cur = f"{cur} · {part}" if cur else part
            st = chr(10).join(lines + [cur])
            return {
                1: f"{s['total_documents']} tệp\nmã phiên {r['run_id'][:8]}…",
                2: f"{s['total_chunks']} đoạn văn\n{sum(1 for u in R[c]['clean'] if u.get('used_ocr'))} đoạn đọc bằng OCR",
                3: f"{s['total_claims']} tuyên bố\n{rej} câu bị loại có lý do" if rej else f"{s['total_claims']} tuyên bố",
                4: f"chỉ mục BM25 + lite\ntrên {s['total_chunks']} đoạn",
                5: f"{ev} cặp tuyên bố–đoạn\n(5 đoạn / tuyên bố)",
                6: st,
                7: f"{len(r['legal_checks'])} lượt đối chiếu\npháp lý",
                8: f"{len(r['risks'])} điểm rủi ro; {len(r['disclosed_figures'])} số liệu\nhàng soát {q}/{len(r['priorities'])} mục",
                9: f"{gates.get('PASS', 0)} PASS, {gates.get('PENDING_HUMAN_REVIEW', 0)} chờ người\n→ {s['release_status']}",
                10: f"result.json, evidence_pack.md\n{len(R[c]['audit'])} sự kiện audit",
            }
        a, b = facts("A"), facts("B")
        titles = ["Kiểm đầu vào", "Đọc + OCR", "Trích tuyên bố", "Dựng chỉ mục", "Truy xuất bằng chứng",
                  "Kiểm chứng", "Đối chiếu pháp lý", "Rủi ro + hàng soát", "Cổng chất lượng", "Ghi gói bằng chứng"]
        names = ["validate_inputs", "parse_and_ocr_documents", "extract_green_claims", "build_hybrid_retrieval_index",
                 "retrieve_evidence_per_claim", "verify_claim_evidence_pairs", "check_applicable_law",
                 "score_greenwashing_risk", "apply_quality_gates", "write_evidence_pack"]
        return {"steps": [{"n": i + 1, "name": names[i], "title": titles[i], "a": a[i + 1], "b": b[i + 1]} for i in range(10)],
                "footer": f"Ca A: {vn(TIME['A']['seconds'], 2)} s · Ca B: {vn(TIME['B']['seconds'], 1)} s trên i7-1355U, 16 GB RAM, không GPU · "
                          "hồ sơ offline: không mô hình nơ-ron nào trong luồng ra kết luận"}

    # ------------------------------------------------------------------ step 1
    @ph
    def s1_manifest_a():
        return jdump(R["A"]["manifest"])

    @ph
    def s1_events():
        rows = []
        for c in "AB":
            ev = Counter(e["event"] for e in R[c]["audit"])
            rows.append([f"Ca {c}", len(R[c]["audit"]), ", ".join(f"{k} ×{v}" for k, v in ev.most_common())])
        return table(["Ca", "Số sự kiện", "Các loại sự kiện"], rows)

    # ------------------------------------------------------------------ step 2
    @ph
    def s2_docs():
        rows = []
        for c in "AB":
            for p in events(c, "document_parsed"):
                rows.append([f"Ca {c}", p["name"], p["role"], p["source_type"], p["chunks"]])
        return table(["Ca", "Tệp", "Vai trò", "Loại nguồn", "Số đoạn"], rows)

    @ph
    def s2_chunks_a():
        rows = [[f"`{u['unit_id']}`", u["source_name"], u["block_index"], u["char_count"], ", ".join(u["normalizations"]),
                 u["text"]] for u in R["A"]["clean"]]
        return table(["unit_id (chunk_id)", "Tệp", "Khối", "Ký tự", "Chuẩn hoá", "Nội dung"], rows, {5: 170})

    @ph
    def s2_clean_record_a():
        return jdump(R["A"]["clean"][4])

    @ph
    def s2_corpus():
        rows = []
        for c in "AB":
            k = R[c]["result"]["corpus"]
            rows.append([f"Ca {c}", k["documents"], k["chunks"], k["by_role"], k["by_source_type"], ", ".join(k["years"]),
                         k["has_comparison"], k["has_independent"], k["coverage"], k["sufficient_for_absence"]])
        return table(["Ca", "Tài liệu", "Đoạn", "Theo vai trò", "Theo loại nguồn", "Năm xuất hiện", "Có tài liệu đối chiếu",
                      "Có nguồn độc lập", "Độ phủ", "Đủ để kết luận 'không có'"], rows)

    @ph
    def s2_reading_b():
        rd = R["B"]["result"].get("reading") or []
        if not rd:
            return "_Phiên không ghi trang nào phải đọc bằng OCR._"
        by_doc = Counter(x["source_name"] for x in rd)
        low = [x for x in rd if x["ocr_confidence"] is not None and x["ocr_confidence"] < 60]
        rows = [[x["source_name"][:34], x["page"], x["ocr_confidence"], x["ocr_low_share"], len(x["ocr_doubtful_numbers"]),
                 " ".join(x["ocr_doubtful_numbers"][:6])] for x in sorted(rd, key=lambda x: x["ocr_confidence"] or 0)[:8]]
        conf = [x["ocr_confidence"] for x in rd if x["ocr_confidence"] is not None]
        head = (f"Ca B có **{len(rd)} trang đọc bằng OCR** ({', '.join(f'{k}: {v}' for k, v in by_doc.items())}); độ tin cậy OCR "
                f"trung bình {vn(sum(conf) / len(conf))}, {len(low)} trang dưới 60. Tám trang có độ tin cậy thấp nhất:\n\n")
        return head + table(["Tệp", "Trang", "Độ tin cậy OCR", "Tỉ lệ từ tin cậy thấp", "Số 'con số đáng ngờ'", "Ví dụ"], rows)

    @ph
    def s2_gates_reading():
        rows = []
        for c in "AB":
            for gg in R[c]["result"]["quality_gates"]:
                if gg["gate_id"] in ("G8", "G9"):
                    rows.append([f"Ca {c}", gg["gate_id"], gg["name"], gg["status"], gg["details"]])
        return table(["Ca", "Cổng", "Tên", "Trạng thái", "Chi tiết"], rows, {4: 260})

    # ------------------------------------------------------------------ step 3
    def claim_row(c):
        return [f"`{c['claim_id']}`", c["text"], c["claim_type"], c["metric"], c["direction"], c["values"], c["units"],
                c["period"], c["baseline"], c["scope"], "có" if c["is_future_commitment"] else "", ", ".join(c["vague_terms_matched"]),
                round(c["confidence"], 2)]

    CLAIM_HEAD = ["claim_id", "Câu tuyên bố", "Loại", "Chỉ số", "Hướng", "Giá trị", "Đơn vị", "Kỳ", "Năm gốc", "Phạm vi",
                  "Cam kết tương lai", "Từ mơ hồ", "Độ tin"]

    @ph
    def s3_claims_a():
        return table(CLAIM_HEAD, [claim_row(c) for c in R["A"]["result"]["claims"]], {1: 120})

    @ph
    def s3_rejected_a():
        rows = [[x["text"], x["rejected_reason"]] for x in R["A"]["extract"] if x.get("rejected_reason")]
        return table(["Câu bị loại", "Lý do"], rows) if rows else "_Không có câu nào bị loại có ghi lý do._"

    @ph
    def s3_stats_b():
        p = events("B", "claims_extracted")[0]
        rows1 = [[k, v] for k, v in sorted(p["by_type"].items(), key=lambda x: -x[1])]
        rows2 = [[k, v] for k, v in sorted(p.get("rejected", {}).items(), key=lambda x: -x[1])]
        return ("**Tuyên bố giữ lại theo loại (Ca B):**\n\n" + table(["Loại tuyên bố", "Số câu"], rows1) +
                f"\n\nNgôn ngữ: {p['by_language']}.\n\n**Câu bị loại theo lý do (Ca B):**\n\n" + table(["Lý do loại", "Số câu"], rows2))

    @ph
    def s3_claims_traced():
        return table(CLAIM_HEAD, [claim_row(V[k]["claim"]) for k in V], {1: 110})

    @ph
    def s3_extract_record_a1():
        x = next(e for e in R["A"]["extract"] if e.get("extract_id") == CID["A1"] or e.get("text") == V["A1"]["claim"]["text"])
        return jdump(x)

    @ph
    def s3_vague_examples_b():
        rows = []
        for c in R["B"]["result"]["claims"]:
            if c["vague_terms_matched"] and len(rows) < 6:
                rows.append([c.get("source_page"), c["text"], ", ".join(c["vague_terms_matched"])])
        return table(["Trang", "Câu", "Từ mơ hồ khớp"], rows, {1: 160})

    # ------------------------------------------------------------------ step 4–5
    def ev_rows(k):
        rows = []
        for i, e in enumerate(V[k]["evidence"], 1):
            rows.append([i, f"`{e['chunk_id']}`", e["source_name"].replace("HPG_", "").replace(".pdf", ""), e.get("page") or "—",
                         e["score"], e["lexical_score"], e["semantic_score"], "có" if e["below_threshold"] else "không",
                         "có" if e["suspicious_instruction"] else "không", e["text"]])
        return rows

    EV_HEAD = ["#", "chunk_id", "Tài liệu", "Trang", "Điểm gộp", "Điểm từ vựng", "Điểm ngữ nghĩa (lite)", "Dưới ngưỡng",
               "Nghi chèn lệnh", "Đoạn (rút gọn)"]

    for key in ("A1", "A2", "B1", "B2"):
        def _mk(k=key):
            return table(EV_HEAD, ev_rows(k), {9: 150})
        _mk.__name__ = f"s5_ev_{key.lower()}"
        ph(_mk)

    @ph
    def s5_scores_b():
        sc = [s for p in events("B", "evidence_retrieved") for s in p["scores"]]
        top = [p["scores"][0] for p in events("B", "evidence_retrieved") if p["scores"]]
        sa = [s for p in events("A", "evidence_retrieved") for s in p["scores"]]
        return table(["Ca", "Số cặp", "Điểm gộp nhỏ nhất", "Trung vị", "Lớn nhất"], [
            ["A", len(sa), min(sa), sorted(sa)[len(sa) // 2], max(sa)],
            ["B", len(sc), min(sc), sorted(sc)[len(sc) // 2], max(sc)]]) + \
            f"\n\nỞ Ca B, điểm của đoạn đứng đầu nằm trong khoảng {vn(min(top), 3)}–{vn(max(top), 3)}."

    # ------------------------------------------------------------------ step 6
    def rel_rows(k):
        return [[i, f"`{e['chunk_id']}`", e.get("relation"), e.get("relation_method"), e.get("relation_reason")]
                for i, e in enumerate(V[k]["evidence"], 1)]

    for key in ("A1", "A2", "B1", "B2"):
        def _mk(k=key):
            v = V[k]
            return (table(["#", "chunk_id", "Quan hệ", "Phương pháp", "Lý do do code sinh ra"], rel_rows(k), {4: 200}) +
                    f"\n\n**Kết luận:** `{v['status']}`.\n\n**Lý do (rationale) hệ thống ghi:** {v['rationale']}")
        _mk.__name__ = f"s6_rel_{key.lower()}"
        ph(_mk)

    for key in ("A1", "B1"):
        def _mk(k=key):
            return jdump(V[k].get("computed_values"), 3500)
        _mk.__name__ = f"s6_computed_{key.lower()}"
        ph(_mk)

    @ph
    def s6_status_all():
        rows = []
        for c in "AB":
            s = R[c]["result"]["summary"]["status_counts"]
            rows.append([f"Ca {c}"] + [s.get(x, 0) for x in ("SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED", "CONTRADICTED",
                                                             "INSUFFICIENT_EVIDENCE")] + [sum(s.values())])
        return table(["Ca", "SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE", "Tổng"], rows)

    @ph
    def s6_status_a():
        return table(["claim_id", "Tuyên bố", "Kết luận", "Lý do"],
                     [[f"`{v['claim']['claim_id']}`", v["claim"]["text"], v["status"], v["rationale"]]
                      for v in R["A"]["result"]["verifications"]], {1: 90, 3: 260})

    @ph
    def s6_methods_b():
        m = Counter((e.get("relation"), e.get("relation_method")) for v in R["B"]["result"]["verifications"] for e in v["evidence"])
        return table(["Quan hệ", "Phương pháp", "Số cặp"], [[a, b, n] for (a, b), n in m.most_common()])

    @ph
    def s6_rationale_b():
        m = Counter(v["rationale"].split(".")[0] for v in R["B"]["result"]["verifications"])
        return table(["Câu mở đầu của lý do", "Số tuyên bố"], [[k, n] for k, n in m.most_common(8)], {0: 200})

    # ------------------------------------------------------------------ step 7
    def legal_rows(keys):
        rows = []
        for k in keys:
            c = TRACED[k][0]
            lc = by_claim(c, "legal_checks").get(CID[k])
            if not lc:
                rows.append([k, "—", "—", "—", "—", "—"])
                continue
            src = "; ".join(f"{s['id']} ({s['effective_from']})" for s in lc["applicable_sources"])
            rows.append([k, lc["issue"], src, lc["legal_finding"], lc["legal_risk"], lc.get("notes")])
        return rows

    @ph
    def s7_legal_traced():
        return table(["Mã", "Chủ đề pháp lý", "Văn bản áp dụng (hiệu lực từ)", "Kết luận pháp lý", "Rủi ro pháp lý", "Ghi chú"],
                     legal_rows(list(V)), {5: 220})

    @ph
    def s7_legal_record_a1():
        return jdump(by_claim("A", "legal_checks")[CID["A1"]], 4000)

    @ph
    def s7_issues_b():
        lc = R["B"]["result"]["legal_checks"]
        m = Counter(x["issue"] for x in lc)
        f = Counter(x["legal_finding"] for x in lc)
        ra = Counter(r for x in lc for r in x["rules_applied"])
        return (table(["Chủ đề pháp lý", "Số tuyên bố"], [[k, n] for k, n in m.most_common()]) +
                f"\n\nKết luận pháp lý ở Ca B: {dict(f)}. Quy tắc được áp dụng: {dict(ra) or 'không có'}.")

    @ph
    def s7_sources():
        seen = {}
        for c in "AB":
            for x in R[c]["result"]["legal_checks"]:
                for s in x["applicable_sources"]:
                    seen.setdefault(s["id"], s)
        return table(["Mã văn bản", "Tên", "Hiệu lực từ", "Vai trò", "Nguồn"],
                     [[s["id"], s["title"], s["effective_from"], s.get("role"), s.get("source_url")] for s in seen.values()], {1: 120, 4: 70})

    # ------------------------------------------------------------------ step 8
    def comp_table(k):
        c = TRACED[k][0]
        r = by_claim(c, "risks")[CID[k]]
        rows = [[x["name"], x["score"], x["max_score"], x["status"], x["reason"]] for x in r["components"]]
        rows.append(["**Tổng**", r["risk_score"], sum(x["max_score"] for x in r["components"]), "", ""])
        tail = (f"\n\n**Mức:** `{r['severity']}`; độ mạnh bằng chứng `{r['evidence_strength']}`; độ mạnh mâu thuẫn "
                f"`{r['contradiction_strength']}`; trọng yếu `{r['materiality']}`; cần người soát: "
                f"{'có' if r['requires_human_review'] else 'không'}; rubric `{r['rubric_version']}`.")
        if r.get("severity_cap_reason"):
            tail += f" Điều chỉnh mức: {r['severity_cap_reason']}"
        return table(["Thành phần", "Điểm", "Tối đa", "Trạng thái", "Lý do"], rows, {4: 160}) + tail

    for key in ("A1", "A2", "B1", "B2"):
        def _mk(k=key):
            return comp_table(k)
        _mk.__name__ = f"s8_risk_{key.lower()}"
        ph(_mk)

    @ph
    def s8_risk_a_all():
        rk = by_claim("A", "risks")
        rows = []
        for v in R["A"]["result"]["verifications"]:
            r = rk[v["claim"]["claim_id"]]
            comp = {x["name"]: x["score"] for x in r["components"]}
            rows.append([short(v["claim"]["text"], 60), v["status"]] + [comp.get(n) for n in (
                "specificity", "quantitative_evidence", "baseline", "period", "scope_boundary", "evidence_support",
                "independent_assurance", "contradiction", "vague_or_exaggerated_language")] + [r["risk_score"], r["severity"]])
        return table(["Tuyên bố", "Kết luận", "spec", "quant", "base", "period", "scope", "evid", "indep", "contra", "vague",
                      "Điểm", "Mức"], rows)

    @ph
    def s8_severity():
        rows = []
        for c in "AB":
            s = R[c]["result"]["summary"]["severity_counts"]
            sc = [r["risk_score"] for r in R[c]["result"]["risks"]]
            rows.append([f"Ca {c}", s.get("LOW", 0), s.get("MEDIUM", 0), s.get("HIGH", 0), s.get("CRITICAL", 0), min(sc), max(sc)])
        return table(["Ca", "LOW", "MEDIUM", "HIGH", "CRITICAL", "Điểm thấp nhất", "Điểm cao nhất"], rows)

    @ph
    def s8_figures_a():
        return table(["figure_id", "Nhãn", "Giá trị", "Đơn vị", "Kỳ", "Phạm vi", "Là tổng", "Dòng gốc"],
                     [[f"`{f['figure_id']}`", f["label"], f["value"], f["unit"], f["period"], f["scopes"], f["is_total"], f["raw_line"]]
                      for f in R["A"]["result"]["disclosed_figures"]], {7: 120})

    @ph
    def s8_figures_b():
        figs = R["B"]["result"]["disclosed_figures"]
        rows = [[f.get("source_page"), f["label"], vn(f["value"], 0) if f["value"] >= 100 else f["value"], f["unit"], f["period"],
                 f["scopes"], "có" if f["is_total"] else ""] for f in figs]
        chk = R["B"]["result"]["figure_checks"]
        tail = "\n\n**Kiểm tra cộng dọc / đối chiếu chéo (Ca B):**\n\n" + table(
            ["Loại", "Trạng thái", "Phép tính", "Chênh lệch", "Dung sai", "Ghi chú"],
            [[x["kind"], x["status"], x.get("calculation"), x.get("difference"), x.get("tolerance"), x.get("note")] for x in chk])
        return table(["Trang", "Nhãn", "Giá trị", "Đơn vị", "Kỳ", "Phạm vi", "Là tổng"], rows, {1: 70}) + tail

    def queue_rows(c, n=None, only_queue=False):
        rows = []
        items = sorted(R[c]["result"]["priorities"], key=lambda p: p["rank"])
        for p in items:
            if only_queue and not p["in_queue"]:
                continue
            comp = {x["name"]: x["score"] for x in p["components"]}
            rows.append([p["rank"], p["item_type"], p["text"], p["priority_score"], comp.get("materiality"), comp.get("obligation"),
                         comp.get("evidence_gap"), comp.get("anomaly"), "có" if p["in_queue"] else "không"])
            if n and len(rows) >= n:
                break
        return rows

    Q_HEAD = ["Hạng", "Loại", "Mục", "Điểm ưu tiên", "Trọng yếu /40", "Nghĩa vụ /25", "Khoảng trống bằng chứng /25",
              "Bất thường /10", "Vào hàng soát"]

    @ph
    def s8_queue_a():
        return table(Q_HEAD, queue_rows("A"), {2: 90}) + "\n\n**Ghi chú phạm vi (scope_note) hệ thống tự viết:** " + R["A"]["result"]["scope_note"]

    @ph
    def s8_queue_b():
        return table(Q_HEAD, queue_rows("B", only_queue=True), {2: 120}) + \
            "\n\n**Ghi chú phạm vi (scope_note) hệ thống tự viết:** " + R["B"]["result"]["scope_note"]

    @ph
    def s8_queue_reasons_a1():
        p = next(x for x in R["A"]["result"]["priorities"] if x.get("claim_id") == CID["A1"])
        return "\n".join(f"- {r}" for r in p["reasons"]) + "\n\n" + table(
            ["Thành phần", "Điểm", "Tối đa", "Trạng thái", "Lý do"],
            [[x["name"], x["score"], x["max_score"], x["status"], x["reason"]] for x in p["components"]], {4: 200})

    @ph
    def s8_traced_rank():
        rows = []
        for k in V:
            c = TRACED[k][0]
            p = next(x for x in R[c]["result"]["priorities"] if x.get("claim_id") == CID[k])
            rows.append([k, p["rank"], len(R[c]["result"]["priorities"]), p["priority_score"], "có" if p["in_queue"] else "không"])
        return table(["Mã", "Hạng", "Trên tổng số mục", "Điểm ưu tiên", "Vào hàng soát"], rows)

    # ------------------------------------------------------------------ step 9
    @ph
    def s9_gates():
        ga = {gg["gate_id"]: gg for gg in R["A"]["result"]["quality_gates"]}
        gb = {gg["gate_id"]: gg for gg in R["B"]["result"]["quality_gates"]}
        rows = [[gid, ga[gid]["name"], ga[gid]["status"], gb[gid]["status"], gb[gid]["details"]] for gid in ga]
        return table(["Cổng", "Tên", "Ca A", "Ca B", "Chi tiết (Ca B)"], rows, {4: 230}) + \
            f"\n\n**Trạng thái phát hành:** Ca A `{R['A']['result']['summary']['release_status']}`, Ca B `{R['B']['result']['summary']['release_status']}`."

    # ------------------------------------------------------------------ step 10
    @ph
    def s10_files():
        rows = []
        for c in "AB":
            d = R[c]["dir"]
            for p in sorted(d.rglob("*")):
                if p.is_file():
                    rows.append([f"Ca {c}", p.relative_to(d).as_posix(), vn(p.stat().st_size / 1024, 1) + " KB"])
        return table(["Ca", "Tệp trong `.quantum/runs/<run_id>/`", "Dung lượng"], rows)

    @ph
    def s10_pack_a1():
        pack = R["A"]["pack"]
        start = pack.find("### 2. ")
        end = pack.find("### 3. ")
        return code(pack[start:end].strip(), "markdown")

    @ph
    def s10_pack_head_a():
        pack = R["A"]["pack"]
        return code(pack[: pack.find("## Claim assessments")].strip(), "markdown")

    @ph
    def s10_layers():
        rows = []
        for c in "AB":
            p = events(c, "data_layers_written")[0]
            rows.append([f"Ca {c}", p.get("raw"), p.get("clean"), p.get("extract")])
        return table(["Ca", "raw (tài liệu)", "clean (đoạn)", "extract (tuyên bố + câu bị loại)"], rows)

    @ph
    def s10_audit_a():
        lines = []
        for e in R["A"]["audit"]:
            lines.append(json.dumps({"t": e["timestamp"][11:23], "event": e["event"],
                                     "payload": json.loads(short(json.dumps(e["payload"], ensure_ascii=False), 9999))},
                                    ensure_ascii=False)[:230])
        return code("\n".join(lines), "json")

    # ------------------------------------------------------------------ chapter 8 timings
    @ph
    def t_steps():
        rows = []
        for c in "AB":
            st = TIME[c]["steps"]
            first = {}
            for s in st:
                first.setdefault(s["step"], s["t"])
            names = list(first)
            for i, n in enumerate(names):
                t1 = first[names[i + 1]] if i + 1 < len(names) else TIME[c]["seconds"]
                rows.append([f"Ca {c}", i + 1, n, vn(t1 - first[n], 2)])
        return table(["Ca", "#", "Bước", "Thời gian (s)"], rows)

    @ph
    def t_summary():
        return table(["Ca", "Tổng thời gian (s)", "Đỉnh bộ nhớ tiến trình (MB)", "Số tuyên bố", "Số đoạn"],
                     [[f"Ca {c}", vn(TIME[c]["seconds"], 2), vn(TIME[c]["peak_working_set_mb"], 0),
                       R[c]["result"]["summary"]["total_claims"], R[c]["result"]["summary"]["total_chunks"]] for c in "AB"])

    @ph
    def t_tools():
        rows = []
        for c in "AB":
            if c not in TOOLS:
                continue
            for t in TOOLS[c]["tools"]:
                rows.append([f"Ca {c}", t["tool"], short(json.dumps({k: v for k, v in t["args"].items() if k != "run_id"},
                                                                  ensure_ascii=False), 70), t["s"]])
            for h in TOOLS[c]["harness"]:
                rows.append([f"Ca {c}", f"ask_greenscan (public={h['public']})", short(h["request"], 70), h["s"]])
        return table(["Ca", "Công cụ", "Tham số", "Thời gian (s)"], rows)

    @ph
    def t_a_seconds():
        return vn(TIME["A"]["seconds"], 2)

    @ph
    def t_b_seconds():
        return vn(TIME["B"]["seconds"], 1)

    @ph
    def pc_verif_a1():
        return jdump(V["A1"])

    @ph
    def t_parse_b():
        first = {}
        for st in TIME["B"]["steps"]:
            first.setdefault(st["step"], st["t"])
        sec = first["extract_green_claims"] - first["parse_and_ocr_documents"]
        return f"{vn(sec, 1)} s trên tổng {vn(TIME['B']['seconds'], 1)} s"

    @ph
    def fix_b2():
        v = V["B2"]
        return (f"kết luận của B2 nay là `{v['status']}` (trước: `SUPPORTED`), kỳ báo cáo `{v['claim']['period'] or 'trống'}`; "
                f"lý do hệ thống ghi: “{v['rationale']}”")

    @ph
    def fix_pytest():
        p = g["TRACE"] / "pytest_summary.txt"
        return p.read_text(encoding="utf-8").strip() if p.exists() else "(chưa chạy)"

    @ph
    def copy_traces():
        import shutil
        dst = g["DOC"] / "vet"
        dst.mkdir(exist_ok=True)
        for p in [*g["TRACE"].glob("tools_*.json"), *g["TRACE"].glob("cfg_*.json"), *(g["TRACE"] / "clean").glob("case_*.json")]:
            shutil.copy2(p, dst / p.name)
        return ""

    from build_tm_llm import register as reg_llm
    reg_llm(g)
