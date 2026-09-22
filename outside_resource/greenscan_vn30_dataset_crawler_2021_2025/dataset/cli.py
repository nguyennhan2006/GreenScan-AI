import argparse,json
from pathlib import Path
import yaml
from .build import build
from .coverage import run
from .testcases import make

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    b=sub.add_parser('build'); b.add_argument('--database',type=Path,default=Path('data/raw/metadata.sqlite3')); b.add_argument('--output',type=Path,default=Path('data/normalized')); b.add_argument('--max-chars',type=int,default=1800); b.add_argument('--top-k',type=int,default=5)
    c=sub.add_parser('coverage'); c.add_argument('--database',type=Path,default=Path('data/raw/metadata.sqlite3')); c.add_argument('--signals',type=Path,default=Path('data/normalized/document_sustainability_signals.json')); c.add_argument('--output',type=Path,default=Path('outputs/coverage'))
    t=sub.add_parser('testcase-template'); t.add_argument('--config',type=Path,default=Path('configs/companies.yml')); t.add_argument('--output',type=Path,default=Path('examples/testcases.jsonl'))
    a=p.parse_args()
    if a.cmd=='build': print(json.dumps(build(a.database,a.output,a.max_chars,a.top_k),ensure_ascii=False,indent=2))
    elif a.cmd=='coverage': print(json.dumps(run(a.database,a.output,a.signals),ensure_ascii=False,indent=2))
    else:
        raw=yaml.safe_load(a.config.read_text(encoding='utf-8')); make([x['id'] for x in raw['companies']],a.output); print(a.output)
if __name__=='__main__': main()
