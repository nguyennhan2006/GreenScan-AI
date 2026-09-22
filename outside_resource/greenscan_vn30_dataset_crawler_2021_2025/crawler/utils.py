from __future__ import annotations
import re, unicodedata
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

YEAR_RE=re.compile(r"(?<!\d)(20(?:1\d|2\d|3\d))(?!\d)")

def normalize(text: str) -> str:
    return re.sub(r"\s+"," ",unicodedata.normalize("NFKC", text or "")).strip()

def lower(text: str) -> str:
    return normalize(text).casefold()

def extract_years(*values: str) -> list[int]:
    out=set()
    for value in values:
        out.update(int(x) for x in YEAR_RE.findall(value or ""))
    return sorted(out)

def canonical_url(url: str) -> str:
    p=urlparse(url)
    q=[(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True) if k.casefold() not in {"utm_source","utm_medium","utm_campaign","utm_content","utm_term"}]
    return urlunparse((p.scheme.lower(),p.netloc.lower(),p.path,"",urlencode(q),""))

def host_allowed(url: str, domains: list[str]) -> bool:
    host=(urlparse(url).hostname or "").lower()
    return any(host==d or host.endswith("."+d) for d in domains)

def filename(url: str) -> str:
    return Path(urlparse(url).path).name or "document"

# Page assets never carry report content, but they sit inside report markup, so
# relevant() scores them highly on the surrounding text and they get queued.
# On the Vinamilk annual-report microsites that burned most of the crawl budget
# on jquery.js, aos.js and favicon.ico. Filter by extension, not by text.
ASSET_EXTENSIONS = {
    ".js", ".mjs", ".css", ".map",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".bmp", ".avif",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp4", ".webm", ".mp3", ".wav", ".zip", ".rar", ".gz",
}


def is_page_asset(url: str) -> bool:
    return Path(urlparse(url).path).suffix.lower() in ASSET_EXTENSIONS
