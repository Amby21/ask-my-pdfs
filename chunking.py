from pypdf import PdfReader

def chunk_page(text, page, size=1000, overlap=150):
    text = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):                     # not the last chunk: back up to a space
            cut = text.rfind(" ", start, end)
            if cut > start:
                end = cut
        chunks.append({"page": page, "text": text[start:end]})
        if end >= len(text):
            break
        start = end - overlap
        space = text.find(" ", start)           # move forward to the start of a word
        if 0 <= space < end:
            start = space + 1
    print(chunks )
    return chunks

def load_chunks(path="sample.pdf"):
    reader = PdfReader(path)
    all_chunks = []
    for i, page in enumerate(reader.pages, start=1):
        all_chunks += chunk_page(page.extract_text() or "", i)
    return all_chunks

if __name__ == "__main__":
    chunks = load_chunks()
    lens = [len(c["text"]) for c in chunks]
    print("chunks:", len(chunks), "| shortest:", min(lens), "| longest:", max(lens))







# def chunk_page(text, page, size=1000, overlap=150):

#     text = " ".join(text.split())
#     chunks = []
#     start = 0
#     while start < len(text):
#         end = min(start + size, len(text))
#         if end < len(text):                     # not the last chunk: back up to a space
#             cut = text.rfind(" ", start, end)
#             if cut > start:
#                 end = cut
#         chunks.append({"page": page, "text": text[start:end]})
#         if end >= len(text):
#             break
#         start = end - overlap
#         space = text.find(" ", start)           # move forward to the start of a word
#         if 0 <= space < end:
#             start = space + 1
#     return chunks













# def load_chunks(path = "sample.pdf"):
#     reader = PdfReader(path)
#     all_chunks = []
#     print(reader.pages)
#     for i, page in enumerate(reader.pages,start=1):
#         all_chunks += chunk_page(page.extract_text() or "", i)
#     return all_chunks





# if __name__ == "__main__":
#     chunks = load_chunks()
