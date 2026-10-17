from rag import ask
from golden_question import GOLDEN

# warm-up: absorbs the cold start (Entra token, first connection); result is discarded
ask("How do I reset my iPod?")

rows = []

print("prompt  compl  reason  retr_s  model_s  refused  question")
for in_guide, question, expected in GOLDEN:
    r = ask(question)
    refused = r["reply"].strip() == "NOT_FOUND"
    row = {
        "question": question,
        "refused": refused,
        "pages": r["pages"],
        "prompt": r["prompt_tokens"],
        "completion": r["completion_tokens"],
        "reasoning": r["reasoning_tokens"],
        "retrieval_s": r["retrieval_s"],
        "model_s": r["model_s"],
    }
    rows.append(row)
    print(f"{row['prompt']:>6} {row['completion']:>6} {row['reasoning']:>7} {row['retrieval_s']:>7} {row['model_s']:>8}  {str(refused):7}  {question}")


def avg(group, key):
    return sum(x[key] for x in group) / len(group)


def summary(label, group):
    print(f"{label:9} n={len(group):<2} prompt {avg(group, 'prompt'):6.0f} | completion {avg(group, 'completion'):5.0f} | reasoning {avg(group, 'reasoning'):5.0f} | retrieval {avg(group, 'retrieval_s'):.2f}s | model {avg(group, 'model_s'):.2f}s")


print()
summary("all", rows)
summary("answered", [x for x in rows if not x["refused"]])
summary("refused", [x for x in rows if x["refused"]])
print("slowest retrieval:", max(x["retrieval_s"] for x in rows), "s | slowest model:", max(x["model_s"] for x in rows), "s")