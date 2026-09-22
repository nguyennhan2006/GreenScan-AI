import json
from pathlib import Path
TYPES=['claim_specificity','numeric_consistency','target_progress_over_time','scope_1_2_3_boundary','financial_environmental_consistency','cross_source_conflict','insufficient_evidence','independent_assurance','citation_provenance']
def make(company_ids,out:Path):
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8') as f:
        for cid in company_ids:
            for t in TYPES:
                f.write(json.dumps({'test_id':f'{cid}:{t}:001','company_id':cid,'test_type':t,'query_or_claim':'','expected_label':'','expected_evidence_ids':[],'forbidden_evidence_ids':[],'year_cutoff':2025,'review_status':'unlabeled','notes':''},ensure_ascii=False)+'\n')
