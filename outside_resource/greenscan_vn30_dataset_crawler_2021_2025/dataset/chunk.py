import hashlib,re
def sentences(text): return [x.strip() for x in re.split(r'(?<=[.!?])\s+|\n+',text or '') if len(x.strip())>=20]
def chunks(items,max_chars=1800,overlap=1):
    out=[]; cur=[]; n=0
    for x in items:
        if cur and n+len(x)>max_chars: out.append(' '.join(cur)); cur=cur[-overlap:] if overlap else []; n=sum(len(y)+1 for y in cur)
        cur.append(x); n+=len(x)+1
    if cur: out.append(' '.join(cur))
    return out
def id_for(doc,unit,text): return f"{doc}:u{unit}:{hashlib.sha1(text.encode(errors='replace')).hexdigest()[:12]}"
