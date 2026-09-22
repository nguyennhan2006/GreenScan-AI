from crawler.filetypes import infer_extension
def test_pdf_magic(): assert infer_extension('https://x/download?id=1','text/html',b'%PDF-1.7')=='.pdf'
