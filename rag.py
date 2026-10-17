import json,math,os,sys
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from azure.search.documents.models import VectorizedQuery
from azure.search.documents import SearchClient
import time

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-5-mini"
SEARCH_MODE = "hybrid"    # "local" | "vector" | "hybrid"

token_provider = get_bearer_token_provider(DefaultAzureCredential(),"https://cognitiveservices.azure.com/.default")

client = AzureOpenAI(azure_ad_token_provider=token_provider,
                     azure_endpoint=os.environ["CONTENTUNDERSTANDING_ENDPOINT"],
                     api_version = "2024-10-21",   
                    )
SEARCH_ENDPOINT = os.environ["SEARCH_ENDPOINT"]

search_client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name="ipod-guide-index",
                      credential=DefaultAzureCredential())

chunks = json.load(open("chunks.json"))

question = " ".join(sys.argv[1:])


def cosine(a,b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))

def top_chunks_local( question, k=5):
    q = client.embeddings.create(model=EMBED_MODEL, input = [question]).data[0].embedding
    scored = [(cosine(q,c["vector"]),c) for c in chunks]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:k]


def top_chunks_azure(question, k=5, hybrid=False):
    q = client.embeddings.create(model=EMBED_MODEL,input=[question]).data[0].embedding
    vq = VectorizedQuery(vector=q,k_nearest_neighbors=k, fields="vector")
    results = search_client.search(
        search_text=question if hybrid else None,
        vector_queries=[vq],
        top=k
    )
    return [(r["@search.score"], {"page": r["page"], "text": r["text"]}) for r in results]

def top_chunks(question, k=5):
    
    if SEARCH_MODE not in ("local", "vector", "hybrid"):
        raise ValueError(f"Unknown SEARCH_MODE: {SEARCH_MODE!r}")
    if SEARCH_MODE == "local":
        return top_chunks_local(question,k)
    return top_chunks_azure(question, k, hybrid=(SEARCH_MODE == "hybrid"))

def ask(question,k=5):

    t0 = time.perf_counter() # Intitiating time

    # 1. get the top 5 chunks with top_chunks(question, 5)
    results = top_chunks(question,k)

    t1 = time.perf_counter() # Recording Chunking time

    # 2. build one "context" string: for each chunk a line like "[page 6] <chunk text>"
    context = ""
    for score, chunk in results:
        context += f"[page {chunk['page']}] {chunk['text']} \n\n"

    system = "You are an assistant, answer ONLY from the context provided, cite pages like (p. 6), If the context does not contain the answer, reply with exactly the single word NOT_FOUND and nothing else. Do not explain."

    resp=client.chat.completions.create(
        model=CHAT_MODEL,
        messages = [{"role":"system",
                        "content": system},
                        {"role":"user",
                        "content": context+"\n"+question},
                    ],
    )
    t2 = time.perf_counter()
    usage = resp.usage
    return {
    "reply": resp.choices[0].message.content,
    "pages": sorted({chunk["page"] for score, chunk in results}),
    "prompt_tokens": usage.prompt_tokens,
    "completion_tokens": usage.completion_tokens,
    "reasoning_tokens": usage.completion_tokens_details.reasoning_tokens,
    "retrieval_s": round(t1 - t0, 2),
    "model_s": round(t2 - t1, 2),
    }   

def answer(question):
    
    return ask(question)["reply"]

if __name__ == "__main__":
    question = " ".join(sys.argv[1:])
    print("Question:", question)

    results = top_chunks(question)                       
    pages = sorted(chunk["page"] for score, chunk in results) # 2. pull out each chunk's page number
    print("Retrieved pages:", pages)                     # 3. show them before the answer
    print("Mode:", SEARCH_MODE)
    print("Scores:", [round(s, 3) for s, c in results])
    print(answer(question))