from __future__ import annotations
import re
from dataclasses import dataclass
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .utils import canonical_url
@dataclass
class Link: url:str; title:str; context:str; source_page_url:str
URL_RE=re.compile(r"https?://[^\s\"'<>\\]+",re.I)
FILE_RE=re.compile(r"(?:https?:)?//[^\s\"'<>\\]+\.(?:pdf|docx?|xlsx?|csv)(?:\?[^\s\"'<>\\]*)?",re.I)
def links(page_url:str,html:str)->list[Link]:
    soup=BeautifulSoup(html,"lxml"); out={}
    attrs=["href","data-href","data-url","data-download","data-file","src"]
    for node in soup.find_all(True):
        title=" ".join(node.stripped_strings)[:500]
        context=" ".join(node.parent.stripped_strings)[:1200] if node.parent else title
        for attr in attrs:
            value=(node.get(attr) or "").strip()
            if value and not value.startswith(("javascript:","mailto:","#")):
                u=canonical_url(urljoin(page_url,value)); out[u]=Link(u,title or u,context,page_url)
        onclick=node.get("onclick") or ""
        for raw in URL_RE.findall(onclick):
            u=canonical_url(urljoin(page_url,raw)); out[u]=Link(u,title or u,context,page_url)
    for raw in FILE_RE.findall(html):
        u=canonical_url(urljoin(page_url,raw)); out[u]=Link(u,u,"raw_html_file_url",page_url)
    return list(out.values())
