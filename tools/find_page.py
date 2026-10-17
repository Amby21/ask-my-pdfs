import sys
from pypdf import PdfReader

word = sys.argv[1].lower()
reader = PdfReader("sample.pdf")

for page_number, page in enumerate(reader.pages, start=1):
    text = page.extract_text() or ""
    lower = text.lower()
    pos = lower.find(word)
    if pos != -1:
        start = max(0, pos - 80)
        snippet = text[start:pos + 120].replace("\n", " ")
        print(f"p. {page_number} | {lower.count(word)} hits | ...{snippet}...")