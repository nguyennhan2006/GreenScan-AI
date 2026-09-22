from dataset.candidates import claim_candidates,evidence_candidates,sustainability_signal
def test_candidates():
    text='Công ty cam kết giảm phát thải 30% đến năm 2030. Phát thải Scope 1 năm 2024 là 12.500 tCO2e.'
    assert claim_candidates(text); assert evidence_candidates(text); assert sustainability_signal(text)>0
