from __future__ import annotations
import hashlib,json,sqlite3
from datetime import datetime,timezone
from pathlib import Path
SCHEMA="""
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS documents(
 id INTEGER PRIMARY KEY AUTOINCREMENT, document_id TEXT UNIQUE, company_id TEXT, ticker TEXT, exchange TEXT,
 source_kind TEXT, source_authority TEXT, source_page_url TEXT, url TEXT UNIQUE, final_url TEXT, title TEXT,
 publication_year INTEGER, discovered_years_json TEXT, document_type TEXT, period_type TEXT, audit_status TEXT,
 scope TEXT, language TEXT, extension TEXT, content_type TEXT, content_length INTEGER, sha256 TEXT, object_path TEXT,
 page_count INTEGER, native_text_chars INTEGER, scan_like_ratio REAL, status TEXT, discovered_at TEXT, downloaded_at TEXT,
 error_code TEXT, error_message TEXT, metadata_json TEXT);
CREATE INDEX IF NOT EXISTS idx_docs_company_year ON documents(company_id,publication_year);
CREATE INDEX IF NOT EXISTS idx_docs_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_docs_hash ON documents(sha256);
"""
class Storage:
    def __init__(self,root:Path):
        self.root=root; self.objects=root/'objects'/'sha256'; self.manifests=root/'manifests'; self.objects.mkdir(parents=True,exist_ok=True); self.manifests.mkdir(parents=True,exist_ok=True)
        self.conn=sqlite3.connect(root/'metadata.sqlite3'); self.conn.row_factory=sqlite3.Row; self.conn.executescript(SCHEMA); self.conn.commit()
    @staticmethod
    def now(): return datetime.now(timezone.utc).isoformat()
    def upsert(self,r):
        p=dict(r); p['discovered_years_json']=json.dumps(p.pop('discovered_years',[])); p['metadata_json']=json.dumps(p.pop('metadata',{}),ensure_ascii=False); p.setdefault('status','discovered'); p.setdefault('discovered_at',self.now())
        cols=['document_id','company_id','ticker','exchange','source_kind','source_authority','source_page_url','url','title','publication_year','discovered_years_json','document_type','period_type','audit_status','scope','language','status','discovered_at','metadata_json']
        vals={x:p.get(x) for x in cols}
        self.conn.execute(f"INSERT INTO documents({','.join(cols)}) VALUES({','.join(':'+x for x in cols)}) ON CONFLICT(url) DO UPDATE SET title=excluded.title,source_page_url=excluded.source_page_url,publication_year=COALESCE(excluded.publication_year,documents.publication_year),document_type=CASE WHEN documents.document_type='other' THEN excluded.document_type ELSE documents.document_type END,metadata_json=excluded.metadata_json",vals); self.conn.commit()
    def has(self,url): return bool(self.conn.execute("SELECT 1 FROM documents WHERE url=? AND status IN('downloaded','duplicate')",(url,)).fetchone())
    def store(self,content,ext):
        h=hashlib.sha256(content).hexdigest(); p=self.objects/h[:2]/f"{h}{ext}"; existed=p.exists(); p.parent.mkdir(parents=True,exist_ok=True)
        if not existed: p.write_bytes(content)
        return h,p,existed
    def update(self,url,status,**kwargs):
        allowed={'final_url','publication_year','discovered_years_json','document_type','period_type','audit_status','scope','language','extension','content_type','content_length','sha256','object_path','page_count','native_text_chars','scan_like_ratio','downloaded_at','error_code','error_message'}
        u={'status':status,**{k:v for k,v in kwargs.items() if k in allowed},'urlkey':url}; sets=','.join(f"{k}=:{k}" for k in u if k!='urlkey'); self.conn.execute(f"UPDATE documents SET {sets} WHERE url=:urlkey",u); self.conn.commit()
    def manifest(self,run,event):
        with (self.manifests/f"{run}.jsonl").open('a',encoding='utf-8') as f: f.write(json.dumps(event,ensure_ascii=False)+'\n')
