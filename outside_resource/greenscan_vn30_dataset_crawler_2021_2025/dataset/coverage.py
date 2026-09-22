from __future__ import annotations
import csv,json,sqlite3
from pathlib import Path
YEARS=range(2021,2026)
def load_signals(path): return json.loads(path.read_text(encoding='utf-8')) if path and path.exists() else {}
def run(db:Path,out:Path,signals_path:Path|None=None):
    con=sqlite3.connect(db); con.row_factory=sqlite3.Row; docs=[dict(x) for x in con.execute("SELECT * FROM documents WHERE status IN('downloaded','duplicate')")]; signals=load_signals(signals_path); rows=[]
    companies=sorted({(d['company_id'],d['ticker']) for d in docs})
    for cid,ticker in companies:
        for year in YEARS:
            ds=[d for d in docs if d['company_id']==cid and d['publication_year']==year]
            annual=any(d['document_type'] in {'annual_report','integrated_report'} for d in ds)
            financial=any(d['document_type']=='financial_statement' and d['period_type']=='annual' and d['audit_status'] in {'audited','unknown'} for d in ds)
            governance=any(d['document_type']=='governance_report' and d['period_type'] in {'annual','unknown'} for d in ds)
            sustainability=any(d['document_type'] in {'sustainability_report','integrated_report'} for d in ds) or any(d['document_type']=='annual_report' and signals.get(d['document_id'],0)>=8 for d in ds)
            mirror=any(d['source_authority'] in {'official_exchange','aggregator'} for d in ds)
            core=sum([annual,financial,governance,sustainability]); rows.append({'company_id':cid,'ticker':ticker,'year':year,'annual_or_integrated':int(annual),'audited_annual_financial':int(financial),'full_year_governance':int(governance),'sustainability_separate_or_embedded':int(sustainability),'exchange_or_aggregator_copy':int(mirror),'core_score_pct':round(core/4*100,1),'complete_core':int(core==4),'missing':';'.join(name for name,value in [('annual',annual),('financial',financial),('governance',governance),('sustainability',sustainability)] if not value)})
    out.mkdir(parents=True,exist_ok=True)
    with (out/'coverage_company_year.csv').open('w',newline='',encoding='utf-8-sig') as f: w=csv.DictWriter(f,fieldnames=rows[0].keys() if rows else ['company_id']); w.writeheader(); w.writerows(rows)
    summary=[]
    for cid,ticker in companies:
        rs=[r for r in rows if r['company_id']==cid]; summary.append({'company_id':cid,'ticker':ticker,'complete_years':sum(r['complete_core'] for r in rs),'years_target':5,'average_core_score_pct':round(sum(r['core_score_pct'] for r in rs)/5,1),'all_2021_2025_complete':int(all(r['complete_core'] for r in rs))})
    with (out/'coverage_company_summary.csv').open('w',newline='',encoding='utf-8-sig') as f: w=csv.DictWriter(f,fieldnames=summary[0].keys() if summary else ['company_id']); w.writeheader(); w.writerows(summary)
    return {'company_year_rows':len(rows),'complete_company_years':sum(r['complete_core'] for r in rows),'fully_complete_companies':sum(x['all_2021_2025_complete'] for x in summary)}
