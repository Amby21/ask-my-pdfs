from rag import top_chunks, SEARCH_MODE
from golden_question import GOLDEN

print(SEARCH_MODE)
hits = 0
total = 0

for in_guide,question, expected in GOLDEN:
    if in_guide:
        total += 1
        pages = {chunk["page"] for score, chunk in top_chunks(question)}
        found =  pages & set(expected)
        if found:
            hits += 1
        print(f"{'HIT ' if found else 'MISS'} | expected {sorted(expected)} | got {sorted(pages)} | {question}")

print(f"Recall@5: {hits}/{total} = {hits / total:.2%}")

        
