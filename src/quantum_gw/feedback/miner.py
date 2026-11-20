"""Rule miner (feedback-loop-v1, tier 3): grouped overrides become measured, versioned proposals.

Nothing here edits a rule. The miner reads finalized decisions and writes a
proposal sheet ("phiếu đề xuất"): what to change, which decisions asked for it,
and — when asked to measure — what the change fixes and breaks on GS-Feedback
and GS-Bench. A person accepts a proposal by editing the reviewed file
(configs/stance_cues.yaml, the rule pack, an org pack) and bumping its version;
the path stays draft -> review -> tests -> new version (legal/rules.py).

Four kinds of proposal:

* cue    - a phrase that recurs in the passages reviewers pointed at when the
           machine read the passage the wrong way (stage `reading`): a refutation
           cue when people concluded CONTRADICTED, a support cue when they
           concluded SUPPORTED. Candidates already in the lexicon are skipped.
* rule   - overrides that blame a rule (RULE_NOT_APPLICABLE / RULE_WRONG),
           grouped by rule: an exception or a fix for the rule pack or org pack.
* query  - passages the system never retrieved (stage `retrieval`): the words
           the deciding passage uses that the claim does not, i.e. candidate
           synonyms for retrieval.
* org    - an organisation that keeps marking claims down for the same missing
           attribute (no baseline year, no scope...) gets a draft org-pack rule
           that would flag them, always as a draft (approved_by '').
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import time
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

import yaml

from quantum_gw.utils.text import normalize_text

from .hygiene import QAStore, clean_labels

WEAKER = {  # AI verdict -> reviewer verdicts that mean "the machine was too generous"
    "SUPPORTED": {"PARTIALLY_SUPPORTED", "UNSUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"},
    "PARTIALLY_SUPPORTED": {"UNSUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"},
}
# A candidate phrase must contain one of these words: phrases, not bare words, and
# only phrases that can carry a stance (the lexicon's own rule, configs/stance_cues.yaml).
REFUTE_SEEDS = ("chưa", "không", "thiếu", "chậm", "dở dang", "tạm dừng", "hủy", "huỷ", "ngừng", "vi phạm",
                "sai", "bị phạt", "giảm sút", "trễ", "not", "no", "yet", "delayed", "unallocated")
SUPPORT_SEEDS = ("đã", "hoàn thành", "đạt", "kiểm toán", "xác nhận", "chứng nhận", "vượt", "completed",
                 "verified", "assured", "achieved")
ATTRIBUTES_VI = {"baseline": "năm gốc", "period": "kỳ (năm)", "scope": "phạm vi", "unit": "đơn vị",
                 "value": "giá trị số"}
_WORDS = re.compile(r"[\wÀ-ỹ%]+", re.UNICODE)
# A phrase cut in the wrong place is not a cue: it may not open on a joining word
# nor end on a word that governs what follows ("chưa", "được", "và").
_BAD_START = frozenset("và của các những là thì mà hoặc với cho tại theo từ đến trong and of the to".split())
_BAD_END = frozenset("chưa không đã được bị sẽ đang và của các là có cho với để not no and of the to".split())
_SELF_SOURCES = {"internal", "financial", "environmental", None, ""}


def _words(text: str) -> list[str]:
    return _WORDS.findall(normalize_text(text or "").lower())


def _ngrams(words: list[str], low: int = 2, high: int = 4) -> set[str]:
    return {" ".join(words[i:i + n]) for n in range(low, high + 1) for i in range(len(words) - n + 1)}


def _decisive(g: dict) -> list[dict]:
    evidence = {e.get("chunk_id"): e for e in g.get("evidence_snapshot") or []}
    out = [evidence[c] for c in g.get("decisive_chunk_ids") or [] if c in evidence]
    if g.get("decisive_quote"):
        out.append({"text": g["decisive_quote"], "source_type": None, "chunk_id": None})
    return out


def _has_seed(gram: str, seeds: tuple[str, ...]) -> bool:
    padded = f" {gram} "
    return any(f" {seed} " in padded for seed in seeds)


def _well_cut(gram: str) -> bool:
    words = gram.split()
    return words[0] not in _BAD_START and words[-1] not in _BAD_END


def _overlaps(a: str, b: str) -> bool:
    """Two phrases from the same stretch of text: they share at least half the words of the shorter one."""
    wa, wb = a.split(), b.split()
    return len(set(wa) & set(wb)) * 2 >= min(len(wa), len(wb))


def cue_candidates(gold: list[dict], lexicon=None, top: int = 10) -> list[dict]:
    """Phrases from the passages people pointed at when the machine misread them."""
    from quantum_gw.verification.stance import StanceLexicon

    lexicon = lexicon or StanceLexicon()
    groups = {"refutes": defaultdict(list), "supports": defaultdict(list)}
    counter_text = {"refutes": [], "supports": []}
    for g in gold:
        label, ai = g.get("label"), g.get("ai_status")
        passages = _decisive(g)
        if not passages:
            continue
        texts = [p.get("text") or p.get("text_preview") or "" for p in passages]
        if g.get("error_stage") == "none":
            # A confirmed verdict: its passages are where a new cue must NOT fire the other way.
            if label == "SUPPORTED":
                counter_text["refutes"].extend(texts)
            elif label == "CONTRADICTED":
                counter_text["supports"].extend(texts)
            continue
        if g.get("error_stage") != "reading":
            continue
        if label == "CONTRADICTED" and ai != "CONTRADICTED":
            family, seeds = "refutes", REFUTE_SEEDS
        elif label == "SUPPORTED" and ai != "SUPPORTED":
            family, seeds = "supports", SUPPORT_SEEDS
        else:
            continue
        claim_grams = _ngrams(_words(g.get("claim_text") or ""), 1, 4)
        for passage, text in zip(passages, texts):
            for gram in _ngrams(_words(text)):
                if (gram in claim_grams or not _has_seed(gram, seeds) or not _well_cut(gram)
                        or lexicon.hits(family, gram)):
                    continue
                groups[family][gram].append({
                    "case_id": f"{g['run_id']}:{g['claim_id']}", "claim_text": g.get("claim_text"),
                    "ai_status": ai, "label": label, "self_source": passage.get("source_type") in _SELF_SOURCES,
                })
    out = []
    for family, grams in groups.items():
        counter = [" " + " ".join(_words(t)) + " " for t in counter_text[family]]
        ranked = []
        for gram, cases in grams.items():
            support = len({c["case_id"] for c in cases})
            against = sum(1 for t in counter if f" {gram} " in t)
            # A stance phrase usually opens on its stance word ("chưa được phân bổ", "không đạt"):
            # prefer those, then the longer of two equally supported phrases.
            seeds = REFUTE_SEEDS if family == "refutes" else SUPPORT_SEEDS
            opens = 0 if any(gram == s or gram.startswith(s + " ") for s in seeds) else 1
            ranked.append((support - against, (opens, -len(gram)), gram, cases, against))
        ranked.sort(key=lambda r: (-r[0], r[1]))
        # Keep the most specific phrase of a family of overlapping ones: "chưa được phân bổ" over "chưa được".
        kept: list[tuple] = []
        for item in ranked:
            if item[0] <= 0:
                continue
            if any(_overlaps(item[2], k[2]) and k[0] >= item[0] for k in kept):
                continue
            kept.append(item)
            if len(kept) >= top:
                break
        for score, _, gram, cases, against in kept:
            self_only = all(c["self_source"] for c in cases)
            out.append({
                "kind": "cue", "family": family, "term": gram, "support": score + against, "against": against,
                "cases": cases,
                "note": ("Mọi đoạn quyết định nằm trong tài liệu của chính doanh nghiệp: chốt chống vu oan "
                         "(verification.self_evidence_can_contradict = false) vẫn bỏ qua cụm này trên các đoạn đó, "
                         "nên thêm cụm từ một mình chưa sửa được các ca này.")
                if family == "refutes" and self_only else "",
            })
    return out


def rule_proposals(rule_feedback: list[dict]) -> list[dict]:
    """ReviewStore.rule_feedback groups, as exception or fix proposals for whoever owns the rule."""
    out = []
    for group in rule_feedback:
        ref = group["rule_ref"]
        out.append({
            "kind": "rule",
            "action": "exception" if group["override_reason"] == "RULE_NOT_APPLICABLE" else "fix",
            "rule_ref": ref,
            "target": "org_pack" if any((c.get("rule_context") or {}).get("org_packs") for c in group["cases"])
            and not ref.upper().startswith(("VN-", "LAW", "RP-")) else "rule_pack",
            "cases": [{k: c.get(k) for k in ("run_id", "claim_id", "claim_text", "ai_status", "label",
                                              "reviewer", "comment")} for c in group["cases"]],
        })
    return out


def query_proposals(gold: list[dict], top_words: int = 6) -> list[dict]:
    """Passages the system never retrieved, and the words they use that the claim does not."""
    out = []
    for g in gold:
        if g.get("error_stage") != "retrieval":
            continue
        claim_words = set(_words(g.get("claim_text") or ""))
        for passage in _decisive(g):
            words = [w for w in _words(passage.get("text") or passage.get("text_preview") or "")
                     if len(w) > 2 and not w.isdigit()]
            missing = [w for w, _ in Counter(w for w in words if w not in claim_words).most_common(top_words)]
            shared = sorted({w for w in words if w in claim_words})[:top_words]
            out.append({"kind": "query", "case_id": f"{g['run_id']}:{g['claim_id']}",
                        "claim_text": g.get("claim_text"), "shared_words": shared, "missing_words": missing})
    return out


def org_rule_drafts(gold: list[dict], min_cases: int = 2) -> list[dict]:
    """Draft org-pack rules from an organisation's repeated mark-downs for a missing attribute."""
    counts: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for g in gold:
        if g.get("label") not in WEAKER.get(g.get("ai_status") or "", set()):
            continue
        claim = g.get("claim") or {}
        if not claim:
            continue
        for attribute in ATTRIBUTES_VI:
            value = claim.get("values") if attribute == "value" else claim.get(
                "units" if attribute == "unit" else attribute)
            if not value:
                counts[(g.get("reviewer_org") or "", attribute)].append(g)
    out = []
    for (org, attribute), cases in sorted(counts.items(), key=lambda kv: -len(kv[1])):
        if len(cases) < min_cases:
            continue
        rule_id = f"PH_{attribute.upper()}_001"
        rule = {
            "rule_id": rule_id,
            "title": f"Tuyên bố phải nêu {ATTRIBUTES_VI[attribute]} (đề xuất từ {len(cases)} lần người soát hạ kết luận)",
            "source_document": "POL-01", "source_clauses": ["POL-01:§?"], "claim_types": [],
            "legal_issue": "org_policy", "applies_to_sectors": [], "effective_from": datetime.now(UTC).date().isoformat(),
            "effective_to": None, "severity": "warning", "on_fail": "flag_for_review",
            "machine_executable": "full", "reviewed_by": "",
            "conditions": [{"id": f"co_{attribute}", "description": f"Tuyên bố nêu {ATTRIBUTES_VI[attribute]}",
                            "source_clause": "POL-01:§?", "check": "claim_attribute_present", "attribute": attribute}],
        }
        out.append({
            "kind": "org", "org_id": org or "(triển khai này)", "attribute": attribute, "support": len(cases),
            "cases": [{"case_id": f"{c['run_id']}:{c['claim_id']}", "claim_text": c.get("claim_text"),
                       "ai_status": c.get("ai_status"), "label": c.get("label")} for c in cases[:10]],
            "rule_yaml": yaml.safe_dump([rule], allow_unicode=True, sort_keys=False),
            "note": "Bản nháp: điền điều khoản chính sách thật vào source_clauses và để người có thẩm quyền duyệt.",
        })
    return out


# ---------------------------------------------------------------- measuring a cue


def patched_cue_file(term: str, family: str, base: str | Path = "configs/stance_cues.yaml") -> Path:
    """A temporary copy of the cue file with `term` added; the reviewed file is not touched."""
    base = Path(base)
    if not base.exists():
        base = Path(__file__).resolve().parents[3] / "configs" / "stance_cues.yaml"
    raw = yaml.safe_load(base.read_text(encoding="utf-8")) or {}
    raw.setdefault(family, {}).setdefault("vi", [])
    raw[family]["vi"] = list(raw[family]["vi"]) + [term]
    raw["version"] = f"{raw.get('version', 'unversioned')}+proposal"
    handle, name = tempfile.mkstemp(prefix="cues-proposal-", suffix=".yaml")
    os.close(handle)
    Path(name).write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return Path(name)


def measure_cue(term: str, family: str, cases: list[dict], bench_limit: int = 0, settings=None) -> dict:
    """What adding `term` does on GS-Feedback and (bench_limit > 0) on the first GS-Bench cases."""
    from quantum_gw.verification.stance import StanceLexicon

    from .bench import run_cases

    patched = patched_cue_file(term, family)
    try:
        before = {r["case_id"]: r for r in run_cases(cases, settings)}
        after = {r["case_id"]: r for r in run_cases(cases, settings, lexicon=StanceLexicon(patched))}
        fixed = sorted(k for k in after if after[k]["passed"] and not before[k]["passed"])
        broken = sorted(k for k in after if before[k]["passed"] and not after[k]["passed"])
        report = {"term": term, "family": family,
                  "gs_feedback": {"cases": len(after), "fixed": fixed, "broken": broken,
                                  "passed_before": sum(r["passed"] for r in before.values()),
                                  "passed_after": sum(r["passed"] for r in after.values())}}
        if bench_limit:
            report["gs_bench"] = _bench_delta(patched, bench_limit, settings)
        return report
    finally:
        patched.unlink(missing_ok=True)


def _bench_delta(patched: Path, limit: int, settings=None) -> dict:
    from quantum_gw.agents.orchestrator import OrchestratorAgent
    from quantum_gw.domain.enums import DocumentRole, SourceType
    from quantum_gw.domain.models import DocumentInput
    from quantum_gw.settings import load_settings

    bench = Path("benchmark/gs_bench_v1/gs_bench_v1.jsonl")
    cases = [json.loads(line) for line in bench.read_text(encoding="utf-8").splitlines() if line.strip()][:limit]
    settings = settings or load_settings()
    started = time.perf_counter()

    def label_all(env_value: str | None) -> dict[str, str]:
        old = os.environ.get("QUANTUM_STANCE_CUES")
        if env_value:
            os.environ["QUANTUM_STANCE_CUES"] = env_value
        else:
            os.environ.pop("QUANTUM_STANCE_CUES", None)
        try:
            out = {}
            with tempfile.TemporaryDirectory(prefix="miner-bench-") as runs:
                local = settings.model_copy(deep=True)
                local.runs_dir = runs
                local.verification.llm_stance = "off"
                for case in cases:
                    docs = [DocumentInput(name="claim.txt", text=case["claim"], role=DocumentRole.CLAIM_SOURCE,
                                          source_type=SourceType.INTERNAL),
                            DocumentInput(name="evidence.txt", text=case["evidence"], role=DocumentRole.EVIDENCE,
                                          source_type=SourceType.EXTERNAL)]
                    statuses = [v.status.value for v in OrchestratorAgent(local).run(docs).verifications]
                    out[case["id"]] = ("N" if not statuses else "C" if "CONTRADICTED" in statuses
                                       else "S" if all(s == "SUPPORTED" for s in statuses) else "N")
            return out
        finally:
            if old is None:
                os.environ.pop("QUANTUM_STANCE_CUES", None)
            else:
                os.environ["QUANTUM_STANCE_CUES"] = old

    before, after = label_all(None), label_all(str(patched))
    gold = {c["id"]: set(c.get("labels") or []) for c in cases}
    changed = [k for k in before if before[k] != after[k]]
    return {
        "cases": len(cases), "changed": len(changed),
        "right_before": sum(1 for k in before if before[k] in gold[k]),
        "right_after": sum(1 for k in after if after[k] in gold[k]),
        # The error the team counts first: a new CONTRADICTED where no gold label says C.
        "new_false_contradicted": sum(1 for k in changed if after[k] == "C" and "C" not in gold[k]),
        "examples": [{"id": k, "before": before[k], "after": after[k], "gold": sorted(gold[k])} for k in changed[:10]],
        "seconds": round(time.perf_counter() - started, 1),
    }


# ---------------------------------------------------------------- the sheet


def mine(store=None, qa: QAStore | None = None, scope: str = "core") -> dict:
    from quantum_gw.storage.reviews import ReviewStore

    store = store or ReviewStore()
    gold = store.gold_records()
    qa_rows = (qa or QAStore(reviews=store)).all()
    clean = clean_labels(gold, qa_rows, scope)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "labels": {"gold": len(gold), "clean": len(clean)},
        "cues": cue_candidates(clean),
        "rules": rule_proposals(store.rule_feedback()),
        "queries": query_proposals(clean),
        "org_rules": org_rule_drafts(gold),
    }


def render_sheet(proposals: dict) -> str:
    """The proposal sheet as Markdown, in Vietnamese, for the person who decides."""
    lines = ["# Phiếu đề xuất từ phản hồi của người soát", "",
             f"Tạo lúc {proposals['generated_at']}. Nhãn chuẩn: {proposals['labels']['gold']}, "
             f"dùng được sau khi lọc: {proposals['labels']['clean']}.", "",
             "Không đề xuất nào tự có hiệu lực. Chấp nhận một đề xuất = sửa tệp đã duyệt, tăng phiên bản, "
             "chạy GS-Feedback, GS-Bench, GS-Eval v2 và evaluate-real (D-2026-10-16-01).", ""]
    lines += ["## 1. Cụm từ lập trường (configs/stance_cues.yaml)", ""]
    if not proposals["cues"]:
        lines.append("Chưa có: cần các quyết định ghi đè ở giai đoạn “đọc sai” kèm đoạn quyết định.")
    for c in proposals["cues"]:
        fam = "bác bỏ (refutes)" if c["family"] == "refutes" else "ủng hộ (supports)"
        lines.append(f"- **“{c['term']}”** → nhóm {fam}; {c['support']} ca ủng hộ, {c['against']} ca phản chứng.")
        for case in c["cases"][:3]:
            lines.append(f"  - {case['case_id']}: máy {case['ai_status']} → người soát {case['label']}: "
                         f"“{(case['claim_text'] or '')[:120]}”")
        if c.get("measured"):
            m = c["measured"]
            fb = m["gs_feedback"]
            lines.append(f"  - Đo trên GS-Feedback ({fb['cases']} ca): sửa {len(fb['fixed'])}, làm hỏng {len(fb['broken'])}.")
            if "gs_bench" in m:
                b = m["gs_bench"]
                lines.append(f"  - Đo trên {b['cases']} ca GS-Bench đầu: {b['changed']} ca đổi nhãn, đúng {b['right_before']} → "
                             f"{b['right_after']}, CONTRADICTED sai mới: {b['new_false_contradicted']}.")
        if c.get("note"):
            lines.append(f"  - Lưu ý: {c['note']}")
    lines += ["", "## 2. Quy tắc (rule pack / org pack)", ""]
    if not proposals["rules"]:
        lines.append("Chưa có quyết định ghi đè nào quy cho quy tắc.")
    for r in proposals["rules"]:
        action = "thêm ngoại lệ" if r["action"] == "exception" else "sửa quy tắc"
        lines.append(f"- **{r['rule_ref']}** ({'org pack' if r['target'] == 'org_pack' else 'rule pack'}): {action}, "
                     f"{len(r['cases'])} ca.")
        for case in r["cases"][:3]:
            lines.append(f"  - {case['claim_id']}: {case['ai_status']} → {case['label']}; “{case.get('comment') or ''}”")
    lines += ["", "## 3. Truy xuất: đoạn quyết định mà hệ thống không tìm thấy", ""]
    if not proposals["queries"]:
        lines.append("Chưa có ca nào ở giai đoạn “truy xuất”.")
    for q in proposals["queries"]:
        lines.append(f"- {q['case_id']}: từ chung với tuyên bố: {', '.join(q['shared_words']) or '—'}; "
                     f"từ đoạn quyết định dùng mà tuyên bố không có: {', '.join(q['missing_words']) or '—'}.")
    lines += ["", "## 4. Quy tắc nội bộ nháp (org pack)", ""]
    if not proposals["org_rules"]:
        lines.append("Chưa tổ chức nào hạ kết luận lặp lại vì cùng một thuộc tính thiếu.")
    for o in proposals["org_rules"]:
        lines.append(f"- **{o['org_id']}**: {o['support']} lần hạ kết luận khi tuyên bố thiếu {ATTRIBUTES_VI[o['attribute']]}. "
                     f"{o['note']}")
        lines.append("")
        lines.append("```yaml")
        lines.append(o["rule_yaml"].rstrip())
        lines.append("```")
    return "\n".join(lines) + "\n"


def write_sheet(proposals: dict, out_dir: str | Path = ".quantum/feedback/proposals") -> tuple[Path, Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    md = out_dir / f"phieu_de_xuat_{stamp}.md"
    js = out_dir / f"phieu_de_xuat_{stamp}.json"
    md.write_text(render_sheet(proposals), encoding="utf-8")
    js.write_text(json.dumps(proposals, ensure_ascii=False, indent=2), encoding="utf-8")
    return md, js
