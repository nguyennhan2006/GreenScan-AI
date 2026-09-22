import re
from .chunk import sentences
CLAIMS=['cam kết','mục tiêu','đến năm','net zero','trung hòa carbon','giảm phát thải','năng lượng tái tạo','phát triển bền vững','thân thiện môi trường','kinh tế tuần hoàn','tiết kiệm năng lượng','giảm nước','tái chế','will reduce','target','by 2030','net-zero','carbon neutral','renewable energy','sustainable']
EVIDENCE=['tco2e','co2e','scope 1','scope 2','scope 3','phát thải','năng lượng','điện','nước','chất thải','tái chế','capex','chi phí môi trường','iso 14001','fsc','asc','bap','leed','kiểm toán','assurance','verified','mwh','gj','m3','tấn']
NUM=re.compile(r'(?<!\w)\d[\d.,\s]*(?:%|tco2e|co2e|mwh|gwh|gj|m3|tấn|triệu|tỷ|million|billion)?',re.I)
def claim_candidates(text):
    out=[]
    for i,s in enumerate(sentences(text),1):
        if any(x in s.casefold() for x in CLAIMS): out.append({'sentence_index':i,'text':s,'has_number':bool(NUM.search(s))})
    return out
def evidence_candidates(text):
    out=[]
    for i,s in enumerate(sentences(text),1):
        if NUM.search(s) and any(x in s.casefold() for x in EVIDENCE): out.append({'sentence_index':i,'text':s,'numbers':NUM.findall(s)})
    return out
def sustainability_signal(text): return sum(x in text.casefold() for x in set(CLAIMS+EVIDENCE))
