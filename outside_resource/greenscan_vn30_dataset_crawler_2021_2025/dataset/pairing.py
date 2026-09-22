import math,re
from collections import Counter
from rapidfuzz.fuzz import token_set_ratio
TOK=re.compile(r'\w+',re.UNICODE)
def toks(x): return [y.casefold() for y in TOK.findall(x or '') if len(y)>1]
def score(a,b):
    x,y=Counter(toks(a['text'])),Counter(toks(b['text'])); overlap=sum((x&y).values()); cos=overlap/math.sqrt(max(sum(x.values()),1)*max(sum(y.values()),1)); s=.65*cos+.35*token_set_ratio(a['text'],b['text'])/100
    if a['company_id']==b['company_id']: s+=.18
    if a.get('publication_year') and b.get('publication_year'):
        d=b['publication_year']-a['publication_year']; s+=.12 if 0<=d<=2 else .04 if 0<=d<=4 else 0
    if a['source_kind']!=b['source_kind']: s+=.08
    return round(s,6)
def top_pairs(claims,evidence,k=5):
    out=[]
    for c in claims:
        pool=[e for e in evidence if e['company_id']==c['company_id'] and e['candidate_id']!=c['candidate_id']]
        for rank,(s,e) in enumerate(sorted(((score(c,e),e) for e in pool),key=lambda x:x[0],reverse=True)[:k],1):
            out.append({'pair_id':f"{c['candidate_id']}::{e['candidate_id']}",'company_id':c['company_id'],'claim_id':c['candidate_id'],'evidence_id':e['candidate_id'],'claim_year':c.get('publication_year'),'evidence_year':e.get('publication_year'),'rank':rank,'retrieval_score':s,'label':'','label_options':['supported','partially_supported','contradicted','insufficient_evidence','not_relevant'],'review_notes':''})
    return out
