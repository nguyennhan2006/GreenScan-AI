"""Kiểm nhanh các điểm yếu dễ thấy nhất của GreenScan, mỗi điểm một con số.

Mỗi phép kiểm đọc thứ đã có sẵn (mã nguồn, lượt chạy Hòa Phát mới nhất, kết quả
GS-Eval v2, tệp nhãn), không chạy lại mô hình, xong trong vài giây. Ý tưởng: một
giám khảo thấy lỗi trong phút đầu (số kiểu Anh, nhãn lệch giữa hai màn hình, câu
rác đứng đầu hàng đợi, "Được ủng hộ" mà nguồn là chính doanh nghiệp), nên những
lỗi đó phải được đo trước khi nộp, mỗi lần sửa mã.

Chạy (thư mục gốc dự án):
    .venv/Scripts/python.exe tools/check_weaknesses.py              # lượt HPG mới nhất
    .venv/Scripts/python.exe tools/check_weaknesses.py --run <id>   # một lượt cụ thể
    .venv/Scripts/python.exe tools/check_weaknesses.py --strict     # mã thoát 1 nếu còn lỗi hiển thị (nhóm A)
Ghi benchmark/weakness_check_<ngày>.json. Danh sách điểm yếu và người phụ trách:
docs/10-chung-ket-2026-11/DIEM_YEU_2026-11-11.md.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
RUNS = ROOT / ".quantum" / "runs"
HPG_SR_SHA = "6ec039f79b65354c2cc5464ba4d29a26ef8085d859a1f65af9b274c0edf530ad"
VN = timezone(timedelta(hours=7))

# Machine-written text a reader sees. Passages quoted from documents are not scanned:
# a company may write 22,540,603 in its own report.
VISIBLE_PATTERNS = {
    "số kiểu Anh (dấu phẩy ngăn nghìn)": re.compile(r"(?<![\w.,])\d{1,3}(?:,\d{3})+(?![\d,])"),
    "số thập phân kiểu Anh": re.compile(r"(?<![\w.,])\d+\.\d{1,2}(?![\d.])"),
    "số dạng khoa học": re.compile(r"\d(?:\.\d+)?e[+-]\d{2}"),
    "chữ 'vs'": re.compile(r"\bvs\b"),
    "chữ 'None'": re.compile(r"\bNone\b"),
    "giờ UTC": re.compile(r"\bUTC\b"),
    "đơn vị viết thô (tco2e)": re.compile(r"\btco2e?\b"),
    "mã kết luận tiếng Anh": re.compile(r"\b(?:PARTIALLY_SUPPORTED|INSUFFICIENT_EVIDENCE|UNSUPPORTED|CONTRADICTED|SUPPORTED)\b"),
}


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(group, key, name, value, target, ok, how, detail=None):
    return {"nhom": group, "ma": key, "ten": name, "gia_tri": value, "muc_tieu": target,
            "dat": ok, "cach_xem_1_phut": how, "chi_tiet": detail}


# ---------- the run to read ----------

def newest_hpg_run(explicit: str | None) -> tuple[str, dict] | tuple[None, None]:
    if explicit:
        return explicit, json.loads((RUNS / explicit / "result.json").read_text(encoding="utf-8"))
    best = None
    for rdir in RUNS.iterdir():
        manifest, result = rdir / "manifest.json", rdir / "result.json"
        if not manifest.exists() or not result.exists() or result.stat().st_size < 500_000:
            continue
        text = manifest.read_text(encoding="utf-8")
        low = text.lower()
        if HPG_SR_SHA not in text and not ("hoa" in low and "phat" in low) and "hòa phát" not in low:
            continue
        stamp = json.loads(text).get("created_at", "")
        if best is None or stamp > best[0]:
            best = (stamp, rdir.name)
    if best is None:
        return None, None
    return best[1], json.loads((RUNS / best[1] / "result.json").read_text(encoding="utf-8"))


def visible_strings(run: dict):
    for v in run.get("verifications", []):
        yield "lý do kết luận", v.get("rationale") or ""
        for w in v.get("warnings") or []:
            yield "cảnh báo", w
        for e in v.get("evidence") or []:
            yield "lý do quan hệ bằng chứng", e.get("relation_reason") or ""
    for p in run.get("priorities", []):
        for r in p.get("reasons") or []:
            yield "lý do hàng đợi", r
    for f in run.get("figure_checks", []):
        yield "phép tính trên số liệu", f.get("calculation") or ""
        yield "ghi chú phép tính", f.get("note") or ""
    for g in run.get("quality_gates", []):
        details = g.get("details")
        for d in details if isinstance(details, list) else [details or ""]:
            yield "cổng chất lượng", d if isinstance(d, str) else json.dumps(d, ensure_ascii=False)


# ---------- A. visible errors ----------

def group_a(run_id, run) -> list[dict]:
    out = []
    ui = _load_module(ROOT / "tools" / "check_ui_language.py", "check_ui_language")
    # Same count as tests/test_ui_language.py: words already reviewed and kept are listed in
    # tools/ui_language_allow.txt (standards, symbols); only a word not on that list is an error.
    allow = {line.strip() for line in (ROOT / "tools" / "ui_language_allow.txt").read_text(encoding="utf-8").splitlines()
             if line.strip() and not line.startswith("#")}
    hits = ui.scan()
    new = sorted({f"{rel}	{tok}" for rel, _line, tok, _kind, _s in hits} - allow)
    out.append(check("A", "A1", "Từ tiếng Anh / mã nội bộ mới trong chữ giao diện", len(new), 0, not new,
                     "python tools/check_ui_language.py",
                     {"chua_duyet": new[:8], "da_duyet_giu_lai": len(hits) - len(new)}))

    if run is not None:
        found: Counter = Counter()
        examples: list[str] = []
        for where, text in visible_strings(run):
            for name, pattern in VISIBLE_PATTERNS.items():
                m = pattern.search(text)
                if m:
                    found[name] += 1
                    if len(examples) < 8:
                        examples.append(f"{where} · {name}: …{text[max(0, m.start() - 40):m.end() + 30]}…")
        total = sum(found.values())
        out.append(check("A", "A2", f"Số, giờ, mã kiểu Anh trong chữ máy viết (lượt {run_id})", total, 0, total == 0,
                         "Mở một tuyên bố có số liệu, đọc dòng lý do và khung “Thủ tục trên số liệu công bố”",
                         {"theo_loai": dict(found), "vi_du": examples}))
    static = [str(p.relative_to(ROOT)) for p in (ROOT / "src" / "quantum_gw").rglob("*.py")
              if "UTC\")" in p.read_text(encoding="utf-8") and "strftime" in p.read_text(encoding="utf-8")]
    out.append(check("A", "A3", "Mã còn in giờ UTC cho người đọc", len(static), 0, not static,
                     "Giấy làm việc: dòng “In lúc …” phải ghi giờ Việt Nam", static))

    from quantum_gw.labels_vi import VERDICT
    from quantum_gw.studio.document import STATUS_LABELS as STUDIO
    badges = (ROOT / "frontend" / "src" / "components" / "badges.jsx").read_text(encoding="utf-8")
    block = badges[badges.index("STATUS_LABELS"):]
    block = block[:block.index("}")]
    front = dict(re.findall(r"(\w+): '([^']+)'", block))
    same = front == dict(VERDICT) == dict(STUDIO)
    out.append(check("A", "A4", "Tên kết luận giống nhau ở hàng đợi, trang tuyên bố, Studio, giấy làm việc",
                     "giống" if same else "lệch", "giống", same,
                     "Mở cùng một tuyên bố ở hàng đợi và ở Studio: tên kết luận phải trùng",
                     None if same else {"giao_dien": front, "may_chu": VERDICT, "studio": dict(STUDIO)}))

    from quantum_gw.agents.verifier import missing_attributes
    from quantum_gw.domain.models import Claim
    claims_js = (ROOT / "frontend" / "src" / "lib" / "claims.js").read_text(encoding="utf-8")
    attrs = claims_js[claims_js.index("export const ATTRIBUTES = ["):]
    attrs = attrs[:attrs.index("\n]\n")]
    front_keys = re.findall(r"key: '(\w+)'", attrs)
    empty = Claim(claim_id="x", text="giảm", claim_type="x", source_chunk_id="x", source_name="x", direction="decrease")
    back_keys = missing_attributes(empty)
    same = front_keys == back_keys
    out.append(check("A", "A5", "Năm thuộc tính: một định nghĩa cho thẻ thuộc tính, nhãn hàng đợi và máy chủ",
                     "giống" if same else "lệch", "giống", same,
                     "Mục số 1 hàng đợi HPG: nhãn “thiếu 3/5 thuộc tính” phải khớp thẻ “Thuộc tính bắt buộc”",
                     None if same else {"giao_dien": front_keys, "may_chu": back_keys}))
    return out


# ---------- B. trust in verdicts ----------

def group_b(run_id, run) -> list[dict]:
    from quantum_gw.agents.verifier import INDEPENDENT_SOURCE_TYPES
    from quantum_gw.settings import load_settings

    out = []
    settings = load_settings(str(ROOT / "configs" / "default.yaml"))
    guard = settings.verification.support_requires_independent_source
    if run is not None:
        statuses = Counter(v["status"] for v in run["verifications"])
        n = sum(statuses.values()) or 1
        own_echo = []
        for v in run["verifications"]:
            if v["status"] != "SUPPORTED":
                continue
            own = v["claim"].get("source_doc_id")
            backing = [e for e in v.get("evidence") or [] if e.get("relation") == "SUPPORTS"
                       and not (own and e.get("doc_id") == own)]
            if backing and not any(e.get("source_type") in INDEPENDENT_SOURCE_TYPES for e in backing):
                own_echo.append(v["claim"]["text"][:100])
        out.append(check("B", "B1", "“Được ủng hộ” chỉ dựa trên tài liệu của chính doanh nghiệp (lượt HPG)",
                         len(own_echo), 0, not own_echo,
                         "Mở một tuyên bố “Được ủng hộ”, thẻ Bằng chứng, dòng “nguồn”",
                         {"co_nguon_doc_lap_dang_bat": guard, "vi_du": own_echo[:3]}))
        decisive = statuses.get("SUPPORTED", 0) + statuses.get("CONTRADICTED", 0)
        out.append(check("B", "B2", "Phân bố kết luận trên HPG (chỉ để biết, không chấm doanh nghiệp)",
                         {"ung_ho_mot_phan": f"{statuses.get('PARTIALLY_SUPPORTED', 0)}/{n}",
                          "dut_khoat": f"{decisive}/{n}", "theo_loai": dict(statuses)},
                         "giải thích được trong hướng dẫn (mục Câu hỏi hay gặp)", None,
                         "Trang Hướng dẫn → “Vì sao gần như mọi câu đều là Ủng hộ một phần?”"))

    eval_path = ROOT / "benchmark" / "gs_eval_v2" / "results" / "eval_results.json"
    replay_path = ROOT / "benchmark" / "gs_eval_v2" / "results" / "replay_support_guard.json"
    if eval_path.exists():
        dec = json.loads(eval_path.read_text(encoding="utf-8"))["explain"]["decisive"]
        on = json.loads(replay_path.read_text(encoding="utf-8"))["explain_labelled"]["on"] if replay_path.exists() else None
        out.append(check("B", "B3", "GS-Eval v2: “Được ủng hộ” sai trên 146 câu có nhãn",
                         {"hien_tai": dec["false_supported"], "khi_bat_co": on["false_supported"] if on else None},
                         0, dec["false_supported"] == 0,
                         "benchmark/gs_eval_v2/results/EVAL_REPORT.md, mục kết luận dứt khoát",
                         {"do_chinh_xac_ket_luan_dut_khoat": {"hien_tai": dec["precision_vs_reference"],
                                                             "khi_bat_co": on["precision_vs_reference"] if on else None},
                          "luu_y": "nhãn tham chiếu do Claude gán (bạc), chưa phải nhãn người"}))
    return out


# ---------- C. queue ----------

def group_c(run_id, run) -> list[dict]:
    from quantum_gw.agents.claim_quality import starts_with_glued_heading

    out = []
    if run is not None:
        claims = {c["claim_id"]: c for c in run.get("claims", [])}
        queue = sorted((p for p in run.get("priorities", []) if p.get("in_queue")), key=lambda p: p["rank"])
        bad = []
        for p in queue:
            c = claims.get(p.get("claim_id")) or {}
            text = (p.get("text") or c.get("text") or "").strip()
            # The product's own flag, plus the glued-heading rule for runs made before v1.1.
            if c.get("quality_flag") or starts_with_glued_heading(text):
                bad.append(f"#{p['rank']}: {text[:90]}")
        first = (queue[0].get("text") or "")[:120] if queue else None
        out.append(check("C", "C1", f"Câu không phải tuyên bố trong {len(queue)} mục đầu hàng đợi HPG", len(bad), 0,
                         not bad, "Mở hàng đợi HPG, đọc mục số 1", {"muc_1": first, "nghi_ngo": bad}))
    usefulness = sorted(ROOT.glob("benchmark/**/queue_usefulness*"))
    out.append(check("C", "C2", "Hàng đợi đã được chuyên gia kiểm (Precision@9, mục bị bỏ sót)",
                     "có" if usefulness else "chưa đo", "có số đo", bool(usefulness),
                     "docs/10-chung-ket-2026-11: đăng ký queue_usefulness_v1",
                     [str(p.relative_to(ROOT)) for p in usefulness[:3]]))
    return out


# ---------- D. human labels ----------

def _xlsx_filled(path: Path) -> tuple[int, int]:
    from openpyxl import load_workbook
    book = load_workbook(path, read_only=True, data_only=True)
    ws = book["Gán nhãn"] if "Gán nhãn" in book.sheetnames else book.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return 0, 0
    head = [str(h or "").strip().lower() for h in rows[0]]
    label, sentence = head.index("nhan"), head.index("cau")
    body = [r for r in rows[1:] if r and len(r) > sentence and r[sentence]]
    return sum(1 for r in body if r[label] not in (None, "")), len(body)


def group_d() -> list[dict]:
    out = []
    labelled = total = 0
    for f in sorted((ROOT / "data" / "gold" / "sessions").glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            total += 1
            lab = json.loads(line).get("labels") or {}
            who = str(lab.get("labeler") or "").lower()
            if who and "claude" not in who and (lab.get("verdict") or lab.get("is_claim") is not None):
                labelled += 1
    out.append(check("D", "D1", "Cặp tuyên bố–bằng chứng có nhãn người", f"{labelled}/{total}",
                     "≥ 60 (mức tối thiểu để nói về độ chính xác)", labelled >= 60,
                     "data/gold/sessions/*.jsonl, trường labels.labeler", None))
    packs = ROOT / "training" / "data" / "gold_t1" / "packs"
    people = {}
    for who in ("nhan", "quynh", "thao"):
        best = None
        for f in sorted(packs.glob(f"T1_{who}_lo1*.xlsx")):
            try:
                filled, rows = _xlsx_filled(f)
            except Exception as exc:  # noqa: BLE001
                people[who] = f"không đọc được {f.name}: {type(exc).__name__}"
                continue
            if best is None or filled > best[0]:
                best = (filled, rows)
        if best is None and (packs / f"T1_{who}_lo1.csv").exists():
            with (packs / f"T1_{who}_lo1.csv").open(encoding="utf-8-sig") as fh:
                body = [r for r in csv.DictReader(fh) if r.get("cau")]
            best = (sum(1 for r in body if (r.get("nhan") or "").strip()), len(body))
        if best is not None:
            people[who] = f"{best[0]}/{best[1]}"
    done = all(isinstance(v, str) and "/" in v and v.split("/")[0] == v.split("/")[1] and v != "0/0"
               for v in people.values()) and len(people) == 3
    out.append(check("D", "D2", "Gói gán nhãn T1 (79 câu, ba người gán độc lập)", people,
                     "đủ 3 gói, kappa ≥ 0,70", done, "training/data/gold_t1/packs/T1_<tên>_lo1.xlsx, cột “nhan”", None))
    return out


# ---------- E/F. AI role and retrieval ----------

def group_e() -> list[dict]:
    from quantum_gw.settings import load_settings
    settings = load_settings(str(ROOT / "configs" / "default.yaml"))
    stance = settings.verification.llm_stance
    verify = os.getenv("QUANTUM_VERIFY") or "(chưa đặt)"
    ablation = sorted(p for p in ROOT.glob("benchmark/**/*ablation*") if p.is_file())
    out = [check("E", "E1", "AI trong luồng mặc định", {"llm_stance": stance, "QUANTUM_VERIFY": verify},
                 "nói rõ AI làm gì và đo được AI giúp gì", None,
                 "Cài đặt → Mô hình ngôn ngữ; trang Hướng dẫn → “Tài liệu có bị gửi ra ngoài không?”", None),
           check("E", "E2", "Số đo bật / tắt AI trên cùng bộ (ablation)", "có" if ablation else "chưa có",
                 "có số đo", bool(ablation), "benchmark/**/*ablation*", [str(p.relative_to(ROOT)) for p in ablation[:3]])]
    found = []
    for p in list(ROOT.glob("benchmark/**/*.json")) + list(ROOT.glob("experiments/**/*.json")):
        if p.name.startswith("weakness_check_"):
            continue  # this tool's own report names the metric
        try:
            if p.stat().st_size < 5_000_000 and re.search(r"recall_at_5|recall@5|\"mrr\"", p.read_text(encoding="utf-8"), re.I):
                found.append(str(p.relative_to(ROOT)))
        except (OSError, UnicodeDecodeError):
            continue
    out.append(check("F", "F1", "Truy xuất bằng chứng: Recall@5, MRR", "có" if found else "chưa đo", "có số đo",
                     bool(found), "tools/measure_all.py (cần nhãn người ở D1)", found[:3]))
    return out


# ---------- G. the written report ----------

REPORT_GLOBS = ["docs/10-chung-ket-2026-11/*.md", "docs/09-luan-van/LUAN_VAN_GREENSCAN/*.md",
                "docs/07-presentation/paper/*.md"]
PLACEHOLDER = re.compile(r"\[(?:URL|url|link|cần điền|điền|TODO)\]|\bTODO\b|\bTBD\b|\?\?\?")


def group_g() -> list[dict]:
    holes, stale = [], []
    for pattern in REPORT_GLOBS:
        for p in sorted(ROOT.glob(pattern)):
            if p.name.startswith("DIEM_YEU_"):
                continue  # the weakness list quotes the patterns it asks to remove
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                rel = f"{p.relative_to(ROOT)}:{i}"
                if PLACEHOLDER.search(line):
                    holes.append(f"{rel}: {line.strip()[:90]}")
                # 172 = 156 claims + 16 disclosed figures (HPG). Correct, but beside "156 tuyên bố"
                # it reads as a contradiction unless the line says what 172 counts.
                if re.search(r"\b9/172\b|\b172 (?:tuyên bố|mục|câu)", line) and not ("156" in line and "16" in line):
                    stale.append(f"{rel}: {line.strip()[:90]}")
    return [
        check("G", "G1", "Chỗ trống chưa điền trong báo cáo ([URL], TODO, ???)", len(holes), 0, not holes,
              "Tìm “[URL]” trong bản báo cáo", holes[:8]),
        check("G", "G2", "“9/172” không ghi rõ 172 = 156 tuyên bố + 16 số liệu công bố (người đọc thấy lệch với “156”)",
              len(stale), 0, not stale, "Tìm “172” trong bản báo cáo", stale[:8]),
    ]


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    explicit = argv[argv.index("--run") + 1] if "--run" in argv else None
    run_id, run = newest_hpg_run(explicit)
    results = group_a(run_id, run) + group_b(run_id, run) + group_c(run_id, run) + group_d() + group_e() + group_g()
    created = None
    if run is not None:
        created = (run.get("manifest") or {}).get("created_at")
    now = datetime.now(VN)
    report = {"ngay": now.strftime("%d/%m/%Y %H:%M"), "luot_hpg": run_id, "luot_hpg_tao_luc": created,
              "ket_qua": results,
              "tom_tat": {"dat": sum(r["dat"] is True for r in results), "chua_dat": sum(r["dat"] is False for r in results),
                          "chi_de_biet": sum(r["dat"] is None for r in results)}}
    path = ROOT / "benchmark" / f"weakness_check_{now:%Y-%m-%d}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    mark = {True: "ĐẠT ", False: "CHƯA", None: "BIẾT"}
    print(f"Lượt HPG: {run_id} (tạo {created})")
    for r in results:
        value = r["gia_tri"] if not isinstance(r["gia_tri"], dict) else json.dumps(r["gia_tri"], ensure_ascii=False)
        print(f"[{mark[r['dat']]}] {r['ma']} {r['ten']}: {value}")
    s = report["tom_tat"]
    print(f"Đạt {s['dat']} · chưa đạt {s['chua_dat']} · chỉ để biết {s['chi_de_biet']} → {path.relative_to(ROOT)}")
    visible_bad = any(r["nhom"] == "A" and r["dat"] is False for r in results)
    return 1 if ("--strict" in argv and visible_bad) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
