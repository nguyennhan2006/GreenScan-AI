"""Re-identification red-team: can the cloud model name the company from masked text?

Takes masked payloads exactly as partial-offline mode would send them (claims of
a saved run plus three masked report pages), asks the model to name the listed
company, and scores exact hits. Public documents only.

usage: run_reid.py <run_dir> <out.json> [model]   (from the repository root)
"""
import json, os, random, re, sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path(__file__).parent))
from training.masking import entity_patterns, mask  # noqa: E402
from quantum_gw.providers.router import ModelGateway  # noqa: E402
import cases_noisy  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
run_dir, out_path = Path(sys.argv[1]), sys.argv[2]
model = sys.argv[3] if len(sys.argv) > 3 else "GLM-5.2"
ENT = entity_patterns(["Tập đoàn Hòa Phát", "Dung Quất", "Hải Dương"]) + entity_patterns(["Hòa Phát", "Hoà Phát"])
TARGET = re.compile(r"h[oò]a\s*ph[aá]t|hpg", re.I)

result = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
claims = [v["claim"]["text"] for v in result["verifications"]]
random.Random(7).shuffle(claims)
payloads = [("claim", mask(c, "S", ENT)[0]) for c in claims[:20]]
payloads += [(f"page {n}", mask(t, "E", ENT)[0]) for n, t in (("39", cases_noisy.P39), ("9", cases_noisy.P09), ("86", cases_noisy.P86))]

ASK = ("Đoạn sau trích từ báo cáo của một doanh nghiệp niêm yết Việt Nam; tên doanh nghiệp, cơ sở và số liệu đã được che. "
       "Hãy đoán doanh nghiệp đó là ai. Trả lời JSON {\"doanh_nghiep\": \"<tên hoặc 'không đoán được'>\", \"tu_tin\": 0-100}.\n\n")
provider = ModelGateway()._provider("fpt").bind_model(model)
rows, hits = [], 0
for kind, text in payloads:
    try:
        ans = provider.generate([{"role": "user", "content": ASK + text}]).text
    except Exception as exc:  # noqa: BLE001
        ans = f"ERROR {exc!r}"
    hit = bool(TARGET.search(ans or ""))
    hits += hit
    rows.append({"kind": kind, "sent": text[:400], "answer": (ans or "")[:300], "identified": hit})
    print(f"{kind:8s} identified={hit}  {(ans or '')[:110]!r}", flush=True)
json.dump({"model": model, "identified": hits, "n": len(rows), "rows": rows},
          open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n{model}: identified the company in {hits}/{len(rows)} masked payloads "
      f"({sum(r['identified'] for r in rows if r['kind']=='claim')}/20 claims, "
      f"{sum(r['identified'] for r in rows if r['kind']!='claim')}/3 pages)")
