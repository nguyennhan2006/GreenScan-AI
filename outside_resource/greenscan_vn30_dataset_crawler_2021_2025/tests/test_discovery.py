from pathlib import Path
from crawler.discovery import links
def test_links():
    html=(Path(__file__).parent/'fixtures'/'sample.html').read_text(encoding='utf-8'); out=links('https://example.com/ir',html); urls={x.url for x in out}; assert 'https://example.com/files/VNM_Bao-cao-thuong-nien-2024.pdf' in urls; assert 'https://cdn.example.com/VNM_BCTC_2025.pdf' in urls
