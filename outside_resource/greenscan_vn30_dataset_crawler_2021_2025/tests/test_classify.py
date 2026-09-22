from crawler.classify import classify,attributes,relevant,preferred_year
def test_types():
    assert classify('Báo cáo phát triển bền vững 2024')=='sustainability_report'
    assert classify('BCTC hợp nhất năm 2025 đã kiểm toán')=='financial_statement'
    a=attributes('BCTC hợp nhất năm 2025 đã kiểm toán'); assert a['period_type']=='annual' and a['audit_status']=='audited' and a['scope']=='consolidated'
def test_relevant_year():
    assert relevant('VNM Báo cáo thường niên 2024','VNM','Công ty Cổ phần Sữa Việt Nam',[2021,2022,2023,2024,2025])
    assert preferred_year('report 2023 updated 2025',[2021,2022,2023,2024,2025])[0]==2025
