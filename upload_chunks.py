import json
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
import os

SEARCH_ENDPOINT = os.environ["SEARCH_ENDPOINT"]
INDEX = "ipod-guide-index"

client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name=INDEX, credential=DefaultAzureCredential())

chunks = json.load(open("chunks.json"))

docs = []

for i,chunk in enumerate(chunks,start=1):
    docs.append({"id": f"chunk_{i}",
     "page": chunk["page"],
     "text": chunk["text"],
     "vector": chunk["vector"]})
    
print("documents to upload:", len(docs))
result = client.upload_documents(documents=docs)
print("succeeded:", sum(r.succeeded for r in result))
print("in index :", client.get_document_count())
