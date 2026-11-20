"""Two-axis reading of a verdict and the kind of ground it rests on (assessment-v1, 15/11/2026).

Expert review, 14/11: "154 ủng hộ một phần" on Hòa Phát reads as a flat result. The same information
reads clearly on two axes:

  consistency          khớp / không khớp / không so được   -- what the passages say about the claim
  source_independence  độc lập / tài liệu tài chính của doanh nghiệp / tự công bố
                                                          -- who wrote the best passage that agrees
  basis                phép tính / cụm từ / mô hình / chỉ tương đồng -- how the deciding stance was reached

Derived only from fields the verifier already sets (relation, relation_method, source_type, doc_id);
it changes no verdict. "financial" is the company's own annual report or financial statements: it is
not labelled "đã kiểm toán" because the system cannot tell which part an auditor signed.
"""

from __future__ import annotations

INDEPENDENT = {"legal", "external", "standard"}
COMPANY_FINANCIAL = {"financial"}

CONSISTENCY_VI = {"match": "khớp", "conflict": "không khớp", "not_comparable": "không so được"}
INDEPENDENCE_VI = {"independent": "nguồn độc lập", "company_financial": "tài liệu tài chính của doanh nghiệp",
                   "self": "chỉ tài liệu tự công bố", "none": "chưa có đoạn xác nhận"}
BASIS_VI = {"arithmetic": "phép tính", "phrase": "cụm từ", "model": "mô hình ngôn ngữ (chỉ gợi ý)",
            "similarity": "chỉ tương đồng nội dung", "none": "không có"}

_PHRASE_METHODS = {"qualitative", "cue", "authority", "absolute", "direction", "rules"}


def _basis(method: str | None) -> str:
    if method in ("numeric", "internal"):
        return "arithmetic"
    if method == "llm":
        return "model"
    if method in (None, "", "similarity"):
        return "similarity"
    return "phrase" if method in _PHRASE_METHODS or method else "similarity"


def assess(claim, evidence, status: str) -> dict:
    """{'consistency', 'source_independence', 'basis'} plus their Vietnamese labels."""
    contradicting = [e for e in evidence if e.relation == "CONTRADICTS" and e.relation_method != "llm"]
    supporting = [e for e in evidence if e.relation in ("SUPPORTS", "PARTIAL")]
    agreeing = [e for e in evidence if e.relation == "SUPPORTS"]
    if contradicting:
        consistency, deciding = "conflict", contradicting[0]
    elif agreeing:
        consistency, deciding = "match", agreeing[0]
    else:
        consistency = "not_comparable"
        deciding = next((e for e in supporting if e.relation_method == "numeric"), supporting[0] if supporting else None)

    def klass(item) -> str:
        if claim.source_doc_id and item.doc_id == claim.source_doc_id:
            return "self"
        source = getattr(item.source_type, "value", item.source_type)
        if source in INDEPENDENT:
            return "independent"
        if source in COMPANY_FINANCIAL:
            return "company_financial"
        return "self"

    order = ["independent", "company_financial", "self"]
    pool = agreeing or supporting
    independence = min((klass(e) for e in pool), key=order.index) if pool else "none"
    basis = _basis(deciding.relation_method) if deciding is not None else "none"
    return {
        "policy": "assessment-v1",
        "consistency": consistency, "consistency_vi": CONSISTENCY_VI[consistency],
        "source_independence": independence, "source_independence_vi": INDEPENDENCE_VI[independence],
        "basis": basis, "basis_vi": BASIS_VI[basis],
        "summary_vi": f"{CONSISTENCY_VI[consistency].capitalize()} với tài liệu; {INDEPENDENCE_VI[independence]}; "
                      f"căn cứ: {BASIS_VI[basis]}.",
    }
