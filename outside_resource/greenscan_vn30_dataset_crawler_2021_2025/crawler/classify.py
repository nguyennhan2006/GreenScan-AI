from __future__ import annotations
import re
from .utils import lower, extract_years

TERMS={
 "annual_report":["báo cáo thường niên","bctn","annual report"],
 "integrated_report":["báo cáo tích hợp","integrated report"],
 "sustainability_report":["báo cáo phát triển bền vững","bcptbv","ptbv","sustainability report","esg report"],
 "financial_statement":["báo cáo tài chính","bctc","financial statement","financial statements"],
 "governance_report":["báo cáo tình hình quản trị","báo cáo quản trị","corporate governance report","governance report"],
 "agm_document":["đại hội đồng cổ đông","đhđcđ","annual general meeting","agm"],
 "environmental_document":["giấy phép môi trường","đánh giá tác động môi trường","đtm","quan trắc môi trường","environmental permit","environmental impact"],
 "assurance_report":["assurance report","limited assurance","xác nhận độc lập","đảm bảo độc lập"],
 "regulatory_record":["xử phạt","thanh tra","vi phạm môi trường","quyết định xử phạt","inspection","violation"]
}

def classify(text:str)->str:
    v=lower(text); scores={k:sum(term in v for term in terms) for k,terms in TERMS.items()}; best=max(scores,key=scores.get)
    return best if scores[best] else "other"

def attributes(text:str)->dict:
    v=lower(text)
    period="annual" if any(x in v for x in ["cả năm","năm 20","annual","cn/20"]) else "semiannual" if any(x in v for x in ["bán niên","6 tháng","semi-annual","half-year"]) else "quarterly" if any(x in v for x in ["quý 1","quý 2","quý 3","quý 4","q1","q2","q3","q4"]) else "unknown"
    audit="audited" if any(x in v for x in ["đã kiểm toán","kiểm toán","audited"]) else "reviewed" if any(x in v for x in ["soát xét","reviewed"]) else "unknown"
    scope="consolidated" if any(x in v for x in ["hợp nhất","consolidated"]) else "separate" if any(x in v for x in ["riêng","công ty mẹ","separate","parent company"]) else "unknown"
    lang="vi" if any(ch in text for ch in "ăâđêôơưĂÂĐÊÔƠƯ") else "en" if re.search(r"\b(the|and|report|financial)\b",v) else "unknown"
    return {"period_type":period,"audit_status":audit,"scope":scope,"language":lang}

def relevant(text:str,ticker:str,company:str,years:list[int])->bool:
    v=lower(text)
    doc=any(term in v for terms in TERMS.values() for term in terms)
    year=any(str(y) in v for y in years)
    identity=lower(ticker) in v or any(part in v for part in lower(company).split() if len(part)>5)
    return doc and (year or identity)

def preferred_year(text:str, years:list[int]):
    found=extract_years(text); valid=[x for x in found if x in years]; return (valid[-1] if valid else None,found)
