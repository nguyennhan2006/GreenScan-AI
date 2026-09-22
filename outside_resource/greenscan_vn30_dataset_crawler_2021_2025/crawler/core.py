from __future__ import annotations
from collections import deque
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse
import logging,uuid,httpx
from tenacity import retry,retry_if_exception,stop_after_attempt,wait_exponential
from .models import CompanyConfig
from .rate_limit import RateLimiter
from .robots import Robots
from .utils import canonical_url,host_allowed,filename,lower,is_page_asset
from .filetypes import infer_extension
from .classify import classify,attributes,relevant,preferred_year
from .discovery import links
from .sitemap import discover as discover_sitemaps
from .storage import Storage
from .inspect import inspect_pdf
log=logging.getLogger(__name__)
TRUSTED_ATTACHMENTS=['cafef1.mediacdn.vn','static2.vietstock.vn','staticfile.hsx.vn','owa.hnx.vn','hnx.vn','www.hnx.vn']
def retryable(exc):
    if isinstance(exc,httpx.TransportError): return True
    return isinstance(exc,httpx.HTTPStatusError) and exc.response.status_code in {408,425,429,500,502,503,504}
class CompanyCrawler:
    def __init__(self,c:CompanyConfig,data:Path,dry=False,source_filter='all',max_documents=None):
        self.c=c; self.data=data; self.dry=dry; self.source_filter=source_filter; p=c.policy
        # Without a cap one large IR site takes the whole run. Coteccons alone
        # pulled 150 documents while 24 other companies had not been reached.
        self.max_documents=max_documents; self.stored=0
        self.client=httpx.Client(headers={'User-Agent':p.user_agent,'Accept':'text/html,application/pdf,application/octet-stream,*/*;q=0.8'},follow_redirects=True,timeout=httpx.Timeout(40,connect=15),verify=p.verify_ssl)
        self.robots=Robots(self.client,p.user_agent,p.robots_on_missing,p.robots_on_error); self.limit=RateLimiter(p.max_requests_per_minute,p.delay_seconds); self.storage=Storage(data); self.visited=set(); self.run=f"{c.id}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    def close(self): self.client.close()
    @retry(retry=retry_if_exception(retryable),stop=stop_after_attempt(3),wait=wait_exponential(multiplier=1,min=1,max=12),reraise=True)
    def fetch(self,url): self.limit.wait(); r=self.client.get(url); r.raise_for_status(); return r
    def source_profiles(self):
        profiles=[]
        if self.source_filter in {'all','official'}: profiles.append(('official','official_company',[str(x) for x in self.c.official_start_urls],self.c.official_domains+self.c.attachment_domains))
        if self.source_filter in {'all','cafef'}: profiles.append(('cafef','aggregator',[str(x) for x in self.c.cafef_urls],['cafef.vn']+TRUSTED_ATTACHMENTS))
        if self.c.hnx_urls and self.source_filter in {'all','hnx'}: profiles.append(('hnx','official_exchange',[str(x) for x in self.c.hnx_urls],['hnx.vn','www.hnx.vn','owa.hnx.vn']))
        return profiles
    def attachment_hint(self,url,title):
        v=lower(url+' '+title); path=urlparse(url).path.lower()
        return path.endswith(('.pdf','.doc','.docx','.xls','.xlsx','.csv')) or any(x in v for x in ['download','attachment','file=','.ashx','tải về','tai-lieu','document'])
    def allowed_host(self,url,domains,attachment=False):
        return host_allowed(url,domains) or (attachment and host_allowed(url,TRUSTED_ATTACHMENTS))
    def record(self,source_kind,authority,url,title,source_page,context=''):
        text=f"{title} {url} {context}"; year,found=preferred_year(text,self.c.years); attrs=attributes(text)
        return {'document_id':str(uuid.uuid5(uuid.NAMESPACE_URL,f"{self.c.id}:{url}")),'company_id':self.c.id,'ticker':self.c.ticker,'exchange':self.c.exchange,'source_kind':source_kind,'source_authority':authority,'source_page_url':source_page,'url':url,'title':title or filename(url),'publication_year':year,'discovered_years':found,'document_type':classify(text),**attrs,'metadata':{'context':context[:2000]}}
    def save_response(self,rec,r,allow_html=False):
        ext=infer_extension(str(r.url),r.headers.get('content-type',''),r.content)
        if ext=='.html' and not allow_html: return
        if ext not in {'.pdf','.doc','.docx','.xls','.xlsx','.csv','.html'}: return
        h,p,existed=self.storage.store(r.content,ext); status='duplicate' if existed else 'downloaded'; fields={'final_url':str(r.url),'extension':ext,'content_type':r.headers.get('content-type'),'content_length':len(r.content),'sha256':h,'object_path':str(p),'downloaded_at':self.storage.now()}
        if ext=='.pdf':
            try: fields.update(inspect_pdf(p,rec['title'],self.c.years))
            except Exception as e: fields['error_message']=f'inspection:{e}'
        self.storage.update(rec['url'],status,**fields); self.storage.manifest(self.run,{'event':status,'company':self.c.id,'url':rec['url'],'final_url':str(r.url),'path':str(p),'sha256':h}); self.stored+=1
    def budget_spent(self): return self.max_documents is not None and self.stored>=self.max_documents
    def download(self,rec,domains):
        self.storage.upsert(rec); self.storage.manifest(self.run,{'event':'discovered',**rec})
        if self.dry or self.storage.has(rec['url']) or self.budget_spent(): return
        ok,reason=self.robots.allowed(rec['url'])
        if not ok: self.storage.update(rec['url'],'robots_denied',error_code=reason); return
        try:
            r=self.fetch(rec['url']); self.save_response(rec,r,allow_html=False)
        except httpx.HTTPStatusError as e:
            code=e.response.status_code; status='not_found' if code==404 else 'forbidden' if code in {401,403} else 'http_error'; self.storage.update(rec['url'],status,error_code=f'http_{code}',error_message=str(e)[:500])
        except Exception as e: self.storage.update(rec['url'],'temporary_error',error_code=type(e).__name__,error_message=str(e)[:500])
    def crawl_profile(self,source_kind,authority,seeds,domains):
        queue=deque((canonical_url(x),0) for x in seeds)
        if self.c.policy.use_sitemaps and source_kind=='official':
            sm=[]
            for seed in seeds:
                origin=f"{urlparse(seed).scheme}://{urlparse(seed).netloc}"; sm += self.robots.sitemap_urls(seed)+[origin+'/sitemap.xml',origin+'/sitemap_index.xml']
            for u in discover_sitemaps(self.client,sm,self.c.policy.max_sitemap_urls):
                if not is_page_asset(u) and host_allowed(u,domains) and relevant(u,self.c.ticker,self.c.company,self.c.years): queue.append((canonical_url(u),1))
        while queue:
            if self.budget_spent():
                log.info('%s reached max_documents=%d, moving on',self.c.id,self.max_documents); break
            url,depth=queue.popleft()
            key=(source_kind,url)
            if key in self.visited or depth>self.c.policy.max_depth: continue
            self.visited.add(key)
            if not self.allowed_host(url,domains,attachment=True): continue
            ok,_=self.robots.allowed(url)
            if not ok: continue
            try: r=self.fetch(url)
            except Exception: continue
            ext=infer_extension(str(r.url),r.headers.get('content-type',''),r.content)
            if ext and ext!='.html':
                rec=self.record(source_kind,authority,url,filename(url),url); self.storage.upsert(rec)
                if not self.dry: self.save_response(rec,r); continue
            html=r.text
            page_relevant=relevant(f"{url} {html[:30000]}",self.c.ticker,self.c.company,self.c.years)
            if page_relevant and self.c.policy.save_relevant_html:
                rec=self.record(source_kind,authority,url,url,url,html[:2000]); self.storage.upsert(rec)
                if not self.dry: self.save_response(rec,r,allow_html=True)
            for link in links(str(r.url),html):
                if is_page_asset(link.url): continue
                text=f"{link.title} {link.context} {link.url}"
                rel=relevant(text,self.c.ticker,self.c.company,self.c.years)
                if self.attachment_hint(link.url,link.title) and rel and self.allowed_host(link.url,domains,attachment=True):
                    self.download(self.record(source_kind,authority,link.url,link.title,link.source_page_url,link.context),domains)
                elif depth<self.c.policy.max_depth and rel and self.allowed_host(link.url,domains): queue.append((link.url,depth+1))
    def crawl(self):
        for profile in self.source_profiles(): log.info('Source %s / %s',self.c.id,profile[0]); self.crawl_profile(*profile)
