#!/usr/bin/env python3
from pathlib import Path
import sys, yaml
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
data=yaml.safe_load((ROOT/'config/legal_case_targets.yaml').read_text(encoding='utf-8'))
targets=data['targets']
errors=[]
if len(targets)!=29: errors.append(f'expected 29 targets, got {len(targets)}')
ids=[t.get('id') for t in targets]
if len(ids)!=len(set(ids)): errors.append('duplicate target id')
required=['id','case_entity','reporting_entity','country','authority','case_id','level','outcome','qualifier','profile','case_url','report_urls','report_url_status']
authority_domains={'sec.gov','www.sec.gov','asic.gov.au','www.asic.gov.au','accc.gov.au','www.accc.gov.au','asa.org.uk','www.asa.org.uk'}
for t in targets:
    for k in required:
        if not t.get(k): errors.append(f"{t.get('id')}: missing {k}")
    if t.get('level') not in {'A','B','C'}: errors.append(f"{t.get('id')}: invalid level")
    u=t.get('case_url','')
    p=urlparse(u)
    if p.scheme!='https': errors.append(f"{t.get('id')}: case URL must be https")
    if p.netloc not in authority_domains: errors.append(f"{t.get('id')}: unexpected authority domain {p.netloc}")
    if not isinstance(t.get('report_urls'),list) or not t['report_urls']: errors.append(f"{t.get('id')}: no report seed")
    for ru in t.get('report_urls',[]):
        if urlparse(ru).scheme!='https': errors.append(f"{t.get('id')}: non-https report seed {ru}")
if errors:
    print('REGISTRY INVALID')
    for e in errors: print('-',e)
    sys.exit(1)
print(f'OK: {len(targets)} unique targets; mandatory fields and URL shape valid')
