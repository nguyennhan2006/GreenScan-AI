#!/usr/bin/env python3
"""Everything the gold set can answer, in one run, judged by rules written before it existed.

    python tools/measure_all.py                      # every section the data allows
    python tools/measure_all.py --only stance,verdict
    python tools/measure_all.py warm                 # do the slow work now, before gold exists
    python tools/measure_all.py --sessions a.jsonl --out <dir>   # other gold / a dry run

Sections
    gates      κ from the two lô-1 copies, adjudicated rows, split hygiene
    retrieval  lite | bge-m3 | bge-m3+rerank searching each company's library:
               Recall@k, MRR, end-to-end verdict accuracy, seconds per claim
    stance     rules | model, on every passage a human labelled
    verdict    rules | model guarded | model decisive, on the evidence a human chose
    queue      share of queue rows a human called a claim (gold + HPG queue review)
    timing     minutes per claim, manual vs GreenScan (benchmark/timing_study.json)
    decisions  every rule in configs/measurement_decisions.yaml: value, threshold, decision

`warm` encodes the libraries of the companies in the gold lots with BGE-M3
(cached on disk, resumable) and asks the stance model about every candidate
pair of those claims (cached), so measurement day costs minutes, not hours.

Nothing here decides what a number means after the fact: the thresholds are
read from configs/measurement_decisions.yaml, registered 2026-09-29.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import evaluate_gold as ev  # noqa: E402
import labeling_pack as lp  # noqa: E402
import yaml  # noqa: E402

DECISIONS = ROOT / "configs" / "measurement_decisions.yaml"
SECTIONS = ["gates", "retrieval", "stance", "verdict", "queue", "timing"]
# (embedding provider, reranker provider). Measured 29/09 on the team laptop:
# local BGE-M3 0.49 pages/s, local bge-reranker 0.28 pairs/s -- the local
# reranker is left out (2.4 h per measurement), local BGE-M3 is measured only
# once `warm --local-bge` has computed its vectors.
RETRIEVAL_VARIANTS = {
    "lite": ("lite", "none"),
    "vn-embedding": ("fpt", "none"),
    "vn-embedding+rerank": ("fpt", "fpt"),
    "bge-m3-local": ("local", "none"),
}
UNWARMED_LIMIT = 200   # pages a local model may still have to encode during a measurement


def _settings(stance: str = "off", decisive: bool = False, embedding: str = "lite",
              reranker: str = "none"):
    from quantum_gw.settings import load_settings

    s = load_settings("configs/default.yaml")
    s.verification.llm_stance = stance
    s.verification.llm_stance_decisive = decisive
    s.embedding.provider = embedding
    s.reranker.provider = reranker
    s.runs_dir = str(ROOT / ".quantum" / "eval_runs")
    return s


# ------------------------------------------------------------------ sections


def gates(rows: list[dict], decided: list[dict]) -> dict:
    kappas = {}
    for a in sorted(lp.LABELER_COPIES.glob("*_quynh.jsonl")):
        b = a.with_name(a.name.replace("_quynh.jsonl", "_thao.jsonl"))
        if b.exists():
            result, disagreements = lp.kappa(a, b)
            kappas[a.stem.rsplit("_", 1)[0]] = {
                "claims": result["claims"],
                "fields": result["fields"],
                "disagreements": len(disagreements),
            }
    return {
        "rows_total": len(rows),
        "rows_adjudicated": len(decided),
        "with_verdict": sum(1 for r in decided if (r["labels"].get("verdict") or "") in ev.VERDICTS),
        "kappa": kappas,
        "splits": ev.split_report(rows),
    }


def retrieval(decided: list[dict]) -> dict:
    from quantum_gw.retrieval.embeddings import build_embedder
    from quantum_gw.retrieval.rerank import build_reranker

    out = {}
    library = ev._library({r["company_id"] for r in decided})
    texts = [p["text"] for pages in library.values() for p in pages]
    for name, (embedding, reranker) in RETRIEVAL_VARIANTS.items():
        s = _settings(embedding=embedding, reranker=reranker)
        try:
            embedder = build_embedder(s.embedding, strict=True)
            ranker = build_reranker(s.reranker, strict=True) if reranker != "none" else None
        except Exception as exc:  # noqa: BLE001
            out[name] = {"rows": 0, "unavailable": f"{type(exc).__name__}: {exc}"}
            continue
        if embedding == "local" and hasattr(embedder, "missing"):
            left = embedder.missing(texts)
            if left > UNWARMED_LIMIT:
                out[name] = {"rows": 0, "unavailable":
                             f"{left} trang chưa có vector — chạy `measure_all.py warm --local-bge` trước "
                             f"(≈ {left / 0.49 / 3600:.1f} giờ CPU)"}
                continue
        out[name] = ev.retrieval_over_library(decided, s, embedder=embedder, reranker=ranker)
        out[name]["embedder"] = f"{embedding}:{s.embedding.fpt_model if embedding == 'fpt' else s.embedding.model}"
    return out


def stance(decided: list[dict]) -> dict:
    return {
        "rules": ev.stance_metrics(decided, _settings("off")),
        "model": ev.stance_metrics(decided, _settings("on_ambiguous")),
    }


def verdict(decided: list[dict]) -> dict:
    return {
        "rules": ev.verification_metrics(decided, _settings("off")),
        "model_guarded": ev.verification_metrics(decided, _settings("on_ambiguous", False)),
        "model_decisive": ev.verification_metrics(decided, _settings("on_ambiguous", True)),
    }


def queue(decided: list[dict]) -> dict:
    result = {"gold": ev.claim_metrics(decided) if decided else {"rows": 0}}
    review = ev.OUT_DIR / "hpg_queue_review.json"
    if review.exists():
        data = json.loads(review.read_text(encoding="utf-8"))
        result["hpg_queue"] = {"top14": data["top14"], "all": data["all"], "why_not": data["why_not"]}
    return result


def timing() -> dict:
    path = ev.OUT_DIR / "timing_study.json"
    if not path.exists():
        return {"completed": 0}
    data = json.loads(path.read_text(encoding="utf-8"))
    groups = {}
    for group in ("manual", "greenscan"):
        items = [i for i in data["items"] if i["group"] == group and i["minutes"] is not None]
        minutes = [i["minutes"] for i in items]
        correct = [i["passages_correct"] for i in items if i["passages_correct"] is not None]
        groups[group] = {
            "n": len(items),
            "minutes": ev._mean_ci(minutes),
            "median_minutes": statistics.median(minutes) if minutes else None,
            "passages_correct": ev._mean_ci(correct) if correct else {"mean": None, "n": 0},
        }
    ratio = None
    if groups["manual"]["minutes"]["mean"] and groups["greenscan"]["minutes"]["mean"]:
        ratio = round(groups["manual"]["minutes"]["mean"] / groups["greenscan"]["minutes"]["mean"], 2)
    return {"completed": data["completed"], "groups": groups, "manual_over_greenscan": ratio,
            "note": "Hai nhóm là hai bộ tuyên bố khác nhau (mỗi câu làm một lần); n nhỏ."}


# ----------------------------------------------------------------- decisions


def _paired(a_rows: list[dict], b_rows: list[dict], key) -> dict:
    """Paired difference a - b on the claims both measured."""
    b_by_id = {r["claim_id"]: r for r in b_rows}
    both = [(key(r), key(b_by_id[r["claim_id"]])) for r in a_rows if r["claim_id"] in b_by_id]
    return ev._paired_diff([x for x, _ in both], [y for _, y in both])


def decide(results: dict, rules: dict) -> list[dict]:
    d = rules["decisions"]
    out = []

    def add(rule, value, threshold, decision, note=""):
        out.append({"rule": rule, "question": d[rule]["question"], "value": value,
                    "threshold": threshold, "decision": decision, "note": note})

    r = results.get("retrieval") or {}
    rule = d["dense_default"]
    base = r.get(rule["baseline"], {})
    for candidate in rule["candidates"]:
        m = r.get(candidate, {})
        if base.get("rows") and m.get("rows"):
            delta = _paired(m["per_row"], base["per_row"], lambda x: x["recall@5"])
            ratio = round(m["seconds_per_claim"] / max(base["seconds_per_claim"], 1e-6), 2)
            ok = (delta["mean"] is not None and delta["mean"] >= rule["min_delta"]
                  and ratio <= rule["max_time_ratio"])
            add("dense_default", f"{candidate}: ΔRecall@5 = {ev._fmt(delta)}; thời gian ×{ratio}",
                f"Δ ≥ {rule['min_delta']}, ×≤ {rule['max_time_ratio']}",
                "BẬT MẶC ĐỊNH" if ok else "CHƯA BẬT",
                "thời gian đo lúc truy vấn, vector đã tính sẵn")
        else:
            add("dense_default", f"{candidate}: —", "—", "KHÔNG ĐO ĐƯỢC",
                m.get("unavailable") or "chưa có gold truy xuất")
    with_rerank, without = (r.get(name, {}) for name in d["reranker_claim"]["compare"])
    if with_rerank.get("rows") and without.get("rows") and "verdict_accuracy" in without:
        delta = _paired(
            with_rerank["per_row"], without["per_row"],
            lambda x: 1.0 if x.get("verdict") == x.get("gold_verdict") else 0.0,
        )
        low = (delta.get("ci95") or [None])[0]
        ok = low is not None and low > d["reranker_claim"]["min_delta_ci_low"]
        add("reranker_claim", f"Δ verdict đúng = {ev._fmt(delta)}", "cận dưới KTC > 0",
            "ĐƯỢC NÓI" if ok else "CHƯA ĐƯỢC NÓI")
    else:
        add("reranker_claim", "—", "—", "KHÔNG ĐO ĐƯỢC",
            with_rerank.get("unavailable") or "chưa có gold")

    model = ((results.get("stance") or {}).get("model") or {})
    esc = model.get("model_vs_rules_on_escalated")
    if esc:
        diff = esc["difference"]
        low, high = (diff.get("ci95") or [None, None])
        decision = ("GIỮ BẬT" if low is not None and low > 0 else
                    "TẮT" if high is not None and high < 0 else "CHƯA RÕ — giữ chốt chặn, đo thêm")
        add("stance_model_keep_on", f"đúng hơn luật trên cùng cặp: {ev._fmt(diff)}",
            "cận dưới KTC > 0", decision)
    else:
        add("stance_model_keep_on", "—", "—", "KHÔNG ĐO ĐƯỢC", "chưa có cặp nào mô hình quyết")
    llm = (model.get("by_method") or {}).get("llm", {}).get("precision", {})
    for rule_name, stance_name in (("lift_guard_supports", "SUPPORTS"), ("lift_guard_contradicts", "CONTRADICTS")):
        rule = d[rule_name]
        p = llm.get(stance_name)
        if not p or not p.get("n"):
            add(rule_name, "—", "—", "GIỮ CHỐT CHẶN", f"mô hình chưa đưa ra {stance_name} nào trên gold")
            continue
        low = (p.get("ci95") or [0])[0]
        ok = p["mean"] >= rule["min_precision"] and low >= rule["min_ci_low"] and p["n"] >= rule["min_n"]
        note = ""
        if ok and stance_name == "CONTRADICTS":
            v = results.get("verdict") or {}
            fc_rules = (v.get("rules") or {}).get("false_contradiction", {}).get("rate")
            fc_dec = (v.get("model_decisive") or {}).get("false_contradiction", {}).get("rate")
            if fc_rules is not None and fc_dec is not None and fc_dec - fc_rules > rule[
                    "max_false_contradiction_rate_increase"]:
                ok, note = False, f"mâu thuẫn sai tăng {fc_rules:.2%} → {fc_dec:.2%}"
        add(rule_name, f"precision {ev._fmt(p)}",
            f"≥ {rule['min_precision']}, cận dưới ≥ {rule['min_ci_low']}, n ≥ {rule['min_n']}",
            "THÁO CHỐT" if ok else "GIỮ CHỐT CHẶN", note)

    q = results.get("queue") or {}
    shares = []
    if (q.get("gold") or {}).get("rows"):
        shares.append(("gold", q["gold"]["queue_precision"]["mean"]))
    if (q.get("hpg_queue") or {}).get("top14", {}).get("precision") is not None:
        shares.append(("HPG 14 mục đầu", q["hpg_queue"]["top14"]["precision"]))
    if shares:
        threshold = d["claim_filter_needed"]["build_if_below"]
        low = min(v for _, v in shares)
        add("claim_filter_needed", "; ".join(f"{n}: {v:.0%}" for n, v in shares), f"< {threshold:.0%}",
            "CẦN LÀM (việc D)" if low < threshold else "CHƯA CẦN")
    else:
        add("claim_filter_needed", "—", "—", "KHÔNG ĐO ĐƯỢC", "chưa có nhãn is_claim")
    return out


# -------------------------------------------------------------------- report


def render(results: dict, decisions: list[dict], rules: dict) -> list[str]:
    g = results["gates"]
    kappa_ok = all(
        (f["fields"].get("is_claim", {}).get("kappa") or 0) >= rules["gates"]["kappa_min"]
        and (f["fields"].get("verdict", {}).get("kappa") or 0) >= rules["gates"]["kappa_min"]
        for f in g["kappa"].values()
    ) if g["kappa"] else False
    enough = g["with_verdict"] >= rules["gates"]["gold_rows_for_accuracy_claims"]
    lines = [f"# Đo lường trên gold — {results['date']}", ""]
    if not (kappa_ok and enough):
        lines += [
            f"> **CHỈ DÙNG NỘI BỘ.** Gold có verdict: {g['with_verdict']} "
            f"(cần ≥ {rules['gates']['gold_rows_for_accuracy_claims']}); "
            f"κ đạt ≥ {rules['gates']['kappa_min']}: {'có' if kappa_ok else 'chưa'}. "
            "Không đưa số nào dưới đây lên slide (D-2026-09-22-05).", ""]
    lines += ["## Quyết định (luật đăng ký trước: `configs/measurement_decisions.yaml`)", "",
              "| Câu hỏi | Đo được | Ngưỡng | Quyết định | Ghi chú |", "| --- | --- | --- | --- | --- |"]
    for x in decisions:
        lines.append(f"| {x['question']} | {x['value']} | {x['threshold']} | **{x['decision']}** | {x['note']} |")

    lines += ["", "## Cổng", "",
              f"- Hàng: {g['rows_total']} · đã trọng tài: {g['rows_adjudicated']} · có verdict: {g['with_verdict']}",
              f"- Chia tập: `{g['splits']['by_split']}` · DN nhóm test lọt sang split khác: "
              f"{g['splits']['companies_in_more_than_one_split'] or 'không'}"]
    for stem, k in g["kappa"].items():
        fields = " · ".join(
            f"{name} {v['kappa']:.2f}" if v.get("kappa") is not None else f"{name} —"
            for name, v in k["fields"].items()
        )
        lines.append(f"- κ `{stem}` ({k['claims']} câu, {k['disagreements']} chỗ khác): {fields}")

    r = results.get("retrieval")
    if r:
        lines += ["", "## Truy xuất trên toàn bộ thư viện của doanh nghiệp", "",
                  "> Nhãn chỉ có cho các trang bộ truy xuất 08/2026 đề xuất: bộ mới tìm ra trang đúng "
                  "khác sẽ không được tính. Mức tăng đo ở đây là cận dưới.", "",
                  "| Phương án | n | Recall@1 | Recall@5 | Recall@10 | MRR | Verdict đúng | s/tuyên bố |",
                  "| --- | ---: | --- | --- | --- | --- | --- | ---: |"]
        for name, m in r.items():
            if not m.get("rows"):
                lines.append(f"| {name} | 0 | {m.get('unavailable', 'chưa có gold')} | | | | | |")
                continue
            lines.append(
                f"| {name} | {m['rows']} | {ev._fmt(m['recall_at']['@1'])} | {ev._fmt(m['recall_at']['@5'])} | "
                f"{ev._fmt(m['recall_at']['@10'])} | {ev._fmt(m['mrr'])} | "
                f"{ev._fmt(m.get('verdict_accuracy'))} | {m['seconds_per_claim']} |")

    s = results.get("stance")
    if s:
        lines += ["", "## Quan hệ từng cặp (người gán vs hệ thống)", "",
                  "| Phương án | Cặp | Đúng | Precision SUPPORTS | Precision CONTRADICTS | Mâu thuẫn sai |",
                  "| --- | ---: | --- | --- | --- | ---: |"]
        for name, m in s.items():
            if not m.get("rows"):
                lines.append(f"| {name} | 0 | | | | |")
                continue
            p = m["precision"]
            lines.append(f"| {name} | {m['rows']} | {ev._fmt(m['accuracy'])} | {ev._fmt(p.get('SUPPORTS'))} | "
                         f"{ev._fmt(p.get('CONTRADICTS'))} | {m['false_contradiction_pairs']} |")
        model = s.get("model") or {}
        if model.get("by_method"):
            lines += ["", "Theo cách quyết (phương án có mô hình):", "",
                      "| Cách | n | Đúng | Precision SUPPORTS | Precision CONTRADICTS |", "| --- | ---: | --- | --- | --- |"]
            for method, m in model["by_method"].items():
                lines.append(f"| {method} | {m['n']} | {ev._fmt(m['accuracy'])} | "
                             f"{ev._fmt(m['precision'].get('SUPPORTS'))} | {ev._fmt(m['precision'].get('CONTRADICTS'))} |")

    v = results.get("verdict")
    if v:
        lines += ["", "## Kết luận (bằng chứng người đã chọn)", "",
                  "| Phương án | n | Đúng | macro-F1 | Mâu thuẫn sai | Abstain phủ |", "| --- | ---: | --- | ---: | ---: | ---: |"]
        for name, m in v.items():
            if not m.get("rows"):
                lines.append(f"| {name} | 0 | | | | |")
                continue
            lines.append(f"| {name} | {m['rows']} | {ev._fmt(m['accuracy'])} | {m['macro_f1']} | "
                         f"{m['false_contradiction']['count']} ({m['false_contradiction']['rate']:.1%}) | "
                         f"{m['abstention']['coverage']:.0%} |")

    q = results.get("queue")
    if q:
        lines += ["", "## Hàng đợi", ""]
        if (q.get("gold") or {}).get("rows"):
            lines.append(f"- Gold: {ev._fmt(q['gold']['queue_precision'])} là tuyên bố thật · `{q['gold']['by_label']}`")
        if q.get("hpg_queue"):
            h = q["hpg_queue"]
            lines.append(f"- HPG 14 mục đầu: {h['top14']['yes']}/{h['top14']['answered']} · "
                         f"cả hàng đợi: {h['all']['yes']}/{h['all']['answered']} · lý do 'không': `{h['why_not']}`")

    t = results.get("timing")
    if t and t.get("completed"):
        gm, gg = t["groups"]["manual"], t["groups"]["greenscan"]
        lines += ["", "## Bài đo thời gian", "",
                  f"- Làm tay: {ev._fmt(gm['minutes'])} phút/tuyên bố · GreenScan: {ev._fmt(gg['minutes'])} · "
                  f"tỷ lệ ×{t['manual_over_greenscan']}",
                  f"- {t['note']}"]
    return lines


# ---------------------------------------------------------------------- warm


def warm(llm: bool, local_bge: bool) -> None:
    """Encode the gold companies' libraries and pre-ask the stance model, before gold exists."""
    from quantum_gw.retrieval.embeddings import build_embedder

    rows = []
    for path in sorted(ev.SESSIONS.glob("*.jsonl")):
        rows.extend(ev.load_rows([path], None))
    companies = {r["company_id"] for r in rows}
    library = ev._library(companies)
    pages = [p["text"] for c in sorted(library) for p in library[c]]
    providers = ["fpt"] + (["local"] if local_bge else [])
    for provider in providers:
        s = _settings(embedding=provider)
        embedder = build_embedder(s.embedding, strict=True)
        label = f"fpt:{s.embedding.fpt_model}" if provider == "fpt" else s.embedding.model
        left = embedder.missing(pages)
        print(f"{label}: {len(pages)} trang của {len(companies)} DN, còn {left} trang chưa có vector.")
        started = time.perf_counter()
        step = 512 if provider == "fpt" else 64
        for start in range(0, len(pages), step):
            embedder.encode(pages[start:start + step])
            done = min(start + step, len(pages))
            if embedder.misses:
                rate = embedder.misses / max(time.perf_counter() - started, 1e-6)
                print(f"  {done}/{len(pages)} · {rate:.1f} trang/s · còn ~"
                      f"{(left - embedder.misses) / max(rate, 1e-6) / 60:.0f} phút", flush=True)
        print(f"  mới tính: {embedder.misses} · đã có: {embedder.hits}")

    if llm:
        from quantum_gw.agents.claim_extractor import ClaimExtractionAgent
        from quantum_gw.agents.verifier import VerificationAgent

        s = _settings("on_ambiguous")
        extractor = ClaimExtractionAgent(s.claim_extraction, ev._NullAudit())
        verifier = VerificationAgent(s.verification, ev._NullAudit())
        work = [(ev._claim_for(r, extractor), [ev._evidence_for(r, c) for c in r["evidence_candidates"]])
                for r in rows]
        # One (claim, passage) per item, exactly as stance_metrics will ask it.
        stats = verifier.prefetch_llm([(claim, [item]) for claim, items in work for item in items])
        print(f"Mô hình xét quan hệ: {stats}")


# ---------------------------------------------------------------------- main


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", nargs="?", default="measure", choices=["measure", "warm"])
    ap.add_argument("--sessions", nargs="*")
    ap.add_argument("--only", default=",".join(SECTIONS))
    ap.add_argument("--out", default=str(ev.OUT_DIR))
    ap.add_argument("--no-llm", action="store_true", help="warm: vectors only")
    ap.add_argument("--local-bge", action="store_true",
                    help="warm: also encode with local BGE-M3 (≈ 8 h on the team laptop CPU)")
    args = ap.parse_args()

    if args.cmd == "warm":
        warm(llm=not args.no_llm, local_bge=args.local_bge)
        return

    paths = [Path(p) for p in args.sessions] if args.sessions else sorted(ev.SESSIONS.glob("*.jsonl"))
    rows = ev.load_rows(paths, None)
    decided = ev.adjudicated(rows)
    only = set(args.only.split(","))
    rules = yaml.safe_load(DECISIONS.read_text(encoding="utf-8"))

    results: dict = {"date": dt.date.today().isoformat(), "sessions": [p.name for p in paths],
                     "rules_version": rules["version"]}
    results["gates"] = gates(rows, decided)
    for name, fn in (("retrieval", retrieval), ("stance", stance), ("verdict", verdict), ("queue", queue)):
        if name in only:
            started = time.perf_counter()
            results[name] = fn(decided) if decided or name == "queue" else {}
            print(f"[{name}] {time.perf_counter() - started:.0f}s", flush=True)
    if "timing" in only:
        results["timing"] = timing()
    decisions = decide(results, rules)
    results["decisions"] = decisions

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"measurement_{results['date']}"
    (out / f"{stem}.json").write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str),
                                      encoding="utf-8")
    lines = render(results, decisions, rules)
    (out / f"{stem}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwritten: {out / stem}.md · .json")


if __name__ == "__main__":
    main()
