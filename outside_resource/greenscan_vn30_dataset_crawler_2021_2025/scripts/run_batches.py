import argparse,subprocess,sys,time,yaml
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--config',type=Path,default=Path('configs/companies.yml')); p.add_argument('--batch-size',type=int,default=5); p.add_argument('--source',default='all',choices=['all','official','cafef','hnx']); p.add_argument('--data-root',default='data/raw'); p.add_argument('--dry-run',action='store_true'); a=p.parse_args()
cs=yaml.safe_load(a.config.read_text(encoding='utf-8'))['companies']
for i in range(0,len(cs),a.batch_size):
    batch=cs[i:i+a.batch_size]; print('Batch',i//a.batch_size+1,[x['ticker'] for x in batch])
    for c in batch:
        cmd=[sys.executable,'-m','crawler.cli','--config',str(a.config),'--company',c['id'],'--source',a.source,'--data-root',a.data_root]
        if a.dry_run: cmd.append('--dry-run')
        subprocess.run(cmd,check=False); time.sleep(2)
