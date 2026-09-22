from __future__ import annotations
from dataclasses import dataclass
from time import monotonic
from urllib.parse import urlparse
import urllib.robotparser, httpx
@dataclass
class Entry: parser: urllib.robotparser.RobotFileParser|None; status:str; at:float; text:str=""
class Robots:
    def __init__(self,client,user_agent,on_missing,on_error): self.client=client; self.ua=user_agent; self.on_missing=on_missing; self.on_error=on_error; self.cache={}
    def origin(self,url):
        p=urlparse(url); return f"{p.scheme}://{p.netloc}"
    def load(self,url):
        origin=self.origin(url)
        if origin in self.cache: return self.cache[origin]
        try:
            r=self.client.get(origin+"/robots.txt")
            # RFC 9309 s2.3.1: 4xx is "unavailable" -> no restrictions apply.
            # Only 5xx and transport failures are "unreachable", where a crawler
            # should assume a complete disallow. Treating every non-404 as an
            # error denied 177 public PDFs on S3/CloudFront hosts, which answer
            # 403 for a robots.txt object that simply does not exist.
            if 400<=r.status_code<500: e=Entry(None,"missing",monotonic(),"")
            else:
                r.raise_for_status(); p=urllib.robotparser.RobotFileParser(); p.set_url(origin+"/robots.txt"); p.parse(r.text.splitlines()); e=Entry(p,"loaded",monotonic(),r.text)
        except Exception: e=Entry(None,"error",monotonic(),"")
        self.cache[origin]=e; return e
    def allowed(self,url):
        e=self.load(url)
        if e.status=="loaded" and e.parser: return e.parser.can_fetch(self.ua,url),"robots_rule"
        if e.status=="missing": return self.on_missing=="allow","robots_missing"
        return self.on_error=="allow","robots_error"
    def sitemap_urls(self,url):
        e=self.load(url); out=[]
        for line in e.text.splitlines():
            if line.lower().startswith("sitemap:"): out.append(line.split(":",1)[1].strip())
        return out
