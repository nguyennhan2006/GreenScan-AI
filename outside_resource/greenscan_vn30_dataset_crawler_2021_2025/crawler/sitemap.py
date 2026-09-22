from __future__ import annotations
from urllib.parse import urljoin
from lxml import etree
import httpx

def parse_xml(content:bytes)->tuple[list[str],list[str]]:
    try: root=etree.fromstring(content)
    except Exception: return [],[]
    locs=[str(x).strip() for x in root.xpath("//*[local-name()='loc']/text()")]
    if root.tag.lower().endswith("sitemapindex"): return [],locs
    return locs,[]

def discover(client:httpx.Client,seeds:list[str],maximum:int=5000)->list[str]:
    queue=list(dict.fromkeys(seeds)); seen=set(); urls=[]
    while queue and len(urls)<maximum:
        sm=queue.pop(0)
        if sm in seen: continue
        seen.add(sm)
        try:
            r=client.get(sm); r.raise_for_status(); page_urls,children=parse_xml(r.content)
            urls.extend(page_urls[:max(0,maximum-len(urls))]); queue.extend(children)
        except Exception: continue
    return list(dict.fromkeys(urls))
