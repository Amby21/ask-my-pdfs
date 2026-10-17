import json
import os
import json
import time

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI

from chunking import load_chunks

EMBED_MODEL = "text-embedding-3-small"

BATCH = 50

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default" 
)



client = AzureOpenAI(
    azure_endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"],
    azure_ad_token_provider = token_provider,
    api_version = "2024-10-21",
    )

chunks = load_chunks()
total_tokens = 0
started = time.time()

for i in range(0, len(chunks), BATCH):
    batch = chunks[i:i+BATCH]
    resp = client.embeddings.create(model=EMBED_MODEL, input=[c["text"] for c in batch])
    for chunk, item in zip(batch,resp.data):
        chunk["vector"] = item.embedding
        total_tokens += resp.usage.total_tokens
        print(f"embedded {min(i + BATCH, len(chunks))} of {len(chunks)}")

with open("chunks.json","w") as f:
    json.dump(chunks,f)

print("tokens used:", total_tokens, "| seconds:", round(time.time() - started, 1))  
