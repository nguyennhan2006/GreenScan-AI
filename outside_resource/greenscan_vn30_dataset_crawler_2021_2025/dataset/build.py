from __future__ import annotations
import csv,json,sqlite3
from pathlib import Path
from .extract import extract
from .chunk import sentences,chunks,id_for
from .candidates import claim_candidates,evidence_candidates,sustainability_signal
from .pairing import top_pairs
from .split import temporal

# U+2028/U+2029/U+0085 are legal inside a JSON string but str.splitlines() treats
# them as line breaks, so a consumer reading this file the obvious way loses one
# record per occurrence. PDF text extraction does emit them. Escape on write so
# every line of a .jsonl file really is one record.
_LINE_BREAKS=str.maketrans({'\u2028':'\\u2028','\u2029':'\\u2029','\u0085':'\\u0085'})

def jsonl(path,records):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8') as f:
        for r in records: f.write(json.dumps(r,ensure_ascii=False).translate(_LINE_BREAKS)+'\n')
def read_db(path):
    con=sqlite3.connect(path); con.row_factory=sqlite3.Row; return [dict(x) for x in con.execute("SELECT * FROM documents ORDER BY company_id,publication_year,document_type")]
def build(db:Path,out:Path,max_chars=1800,top_k=5):
    docs=read_db(db); units=[]; chs=[]; claims=[]; evidence=[]; doc_signals={}
    for d in docs:
        if d['status'] not in {'downloaded','duplicate'} or not d.get('object_path') or not Path(d['object_path']).exists(): continue
        total_signal=0
        for u in extract(Path(d['object_path'])):
            text=u.get('text',''); total_signal+=sustainability_signal(text)
            unit_id=f"{d['document_id']}:unit:{u['unit_index']}"; units.append({'unit_id':unit_id,'document_id':d['document_id'],'company_id':d['company_id'],'publication_year':d['publication_year'],'document_type':d['document_type'],'unit_type':u['unit_type'],'unit_index':u['unit_index'],'text':text})
            for ct in chunks(sentences(text),max_chars):
                cid=id_for(d['document_id'],u['unit_index'],ct); base={'chunk_id':cid,'document_id':d['document_id'],'company_id':d['company_id'],'ticker':d['ticker'],'source_kind':d['source_kind'],'source_authority':d['source_authority'],'publication_year':d['publication_year'],'document_type':d['document_type'],'unit_type':u['unit_type'],'unit_index':u['unit_index'],'text':ct,'split':temporal(d['publication_year'])}; chs.append(base)
                for i,x in enumerate(claim_candidates(ct),1): claims.append({**base,**x,'candidate_id':f'{cid}:claim:{i}','candidate_type':'claim'})
                for i,x in enumerate(evidence_candidates(ct),1): evidence.append({**base,**x,'candidate_id':f'{cid}:evidence:{i}','candidate_type':'evidence'})
        doc_signals[d['document_id']]=total_signal
    pairs=top_pairs(claims,evidence,top_k)
    out.mkdir(parents=True,exist_ok=True); jsonl(out/'documents.jsonl',docs); jsonl(out/'units.jsonl',units); jsonl(out/'chunks.jsonl',chs); jsonl(out/'claim_candidates.jsonl',claims); jsonl(out/'evidence_candidates.jsonl',evidence); jsonl(out/'annotation_pairs.jsonl',pairs)
    (out/'document_sustainability_signals.json').write_text(json.dumps(doc_signals,indent=2),encoding='utf-8')
    hashes={}; leakage=[]
    for d in docs:
        if d.get('sha256'):
            split=temporal(d.get('publication_year')); hashes.setdefault(d['sha256'],set()).add(split)
    for h,s in hashes.items():
        if len(s)>1: leakage.append({'sha256':h,'splits':sorted(s)})
    (out/'leakage_report.json').write_text(json.dumps({'cross_split_duplicate_hashes':leakage},indent=2),encoding='utf-8')
    return {'documents':len(docs),'units':len(units),'chunks':len(chs),'claims':len(claims),'evidence':len(evidence),'pairs':len(pairs),'cross_split_duplicate_hashes':len(leakage)}
