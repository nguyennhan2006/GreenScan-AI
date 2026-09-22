from __future__ import annotations
from pathlib import Path
import fitz
from .classify import classify,attributes,preferred_year

def inspect_pdf(path:Path,title:str,years:list[int])->dict:
    doc=fitz.open(path); chars=[]; sample=[]
    indices=list(range(min(4,len(doc))))
    if len(doc)>4: indices.append(len(doc)-1)
    for i,p in enumerate(doc):
        text=p.get_text('text').strip(); chars.append(len(text))
        if i in indices: sample.append(text)
    combined=title+'\n'+'\n'.join(sample); year,found=preferred_year(combined,years); attrs=attributes(combined)
    return {'page_count':len(doc),'native_text_chars':sum(chars),'scan_like_ratio':round(sum(x<80 for x in chars)/max(len(chars),1),4),'publication_year':year,'discovered_years_json':__import__('json').dumps(found),'document_type':classify(combined),**attrs}
