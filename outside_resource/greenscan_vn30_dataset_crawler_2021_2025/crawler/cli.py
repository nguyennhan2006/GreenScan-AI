import argparse,logging
from pathlib import Path
from rich.logging import RichHandler
from .config import load_companies
from .core import CompanyCrawler

def main():
    p=argparse.ArgumentParser(description='Crawl 30 Vietnamese companies, 2021-2025')
    p.add_argument('--config',type=Path,default=Path('configs/companies.yml')); p.add_argument('--company',action='append',help='Company id or ticker; repeatable'); p.add_argument('--source',choices=['all','official','cafef','hnx'],default='all'); p.add_argument('--data-root',type=Path,default=Path('data/raw')); p.add_argument('--dry-run',action='store_true'); p.add_argument('--log-level',default='INFO')
    # Per-run policy overrides. configs/companies.yml stays the canonical source
    # of URLs and identity; crawl budget is a property of the run, not the company.
    p.add_argument('--max-depth',type=int,help='Override policy.max_depth for every company')
    p.add_argument('--delay',type=float,help='Override policy.delay_seconds')
    p.add_argument('--requests-per-minute',type=int,help='Override policy.max_requests_per_minute')
    p.add_argument('--no-sitemaps',action='store_true',help='Skip sitemap discovery; crawl only the configured start URLs')
    p.add_argument('--max-sitemap-urls',type=int,help='Override policy.max_sitemap_urls')
    p.add_argument('--max-documents',type=int,help='Cap documents stored per company so one large site cannot consume the run')
    a=p.parse_args()
    logging.basicConfig(level=getattr(logging,a.log_level.upper()),format='%(message)s',handlers=[RichHandler(rich_tracebacks=True)])
    cs=load_companies(a.config)
    if a.company:
        wanted={x.lower() for x in a.company}
        cs=[c for c in cs if c.id in wanted or c.ticker.lower() in wanted]
    if not cs: raise SystemExit('No company matched')

    overrides={}
    if a.max_depth is not None: overrides['max_depth']=a.max_depth
    if a.delay is not None: overrides['delay_seconds']=a.delay
    if a.requests_per_minute is not None: overrides['max_requests_per_minute']=a.requests_per_minute
    if a.max_sitemap_urls is not None: overrides['max_sitemap_urls']=a.max_sitemap_urls
    if a.no_sitemaps: overrides['use_sitemaps']=False
    if overrides:
        logging.getLogger('crawler').info('Policy overrides: %s',overrides)
        cs=[c.model_copy(update={'policy':c.policy.model_copy(update=overrides)}) for c in cs]

    for c in cs:
        x=CompanyCrawler(c,a.data_root,a.dry_run,a.source,max_documents=a.max_documents)
        try: x.crawl()
        except Exception: logging.getLogger('crawler').exception('Company %s failed',c.id)
        finally: x.close()
if __name__=='__main__': main()
