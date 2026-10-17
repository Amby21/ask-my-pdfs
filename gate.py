import sys
from rag import ask
from golden_question import GOLDEN
from citation_check import cited_pages

MIN_RECALL = 1.0          # the recall@5 bar; lower it only on purpose

refusal_wrong = 0
answerable = 0
hits = 0
grounded = 0

for in_guide, question, expected in GOLDEN:
    r = ask(question)
    retrieved = set(r["pages"])
    reply = r["reply"]
    refused = reply.strip() == "NOT_FOUND"

    if refused == in_guide:           # refused when it should answer, or answered when it should refuse
        refusal_wrong += 1

    if in_guide:
        answerable += 1
        if retrieved & set(expected):
            hits += 1
        cited = cited_pages(reply)
        if cited and not (cited - retrieved):
            grounded += 1

recall = hits / answerable
print(f"Refusal wrong:      {refusal_wrong} of {len(GOLDEN)}")
print(f"Recall@5:           {hits}/{answerable} = {recall:.0%}")
print(f"Citations grounded: {grounded}/{answerable}")

passed = refusal_wrong == 0 and recall >= MIN_RECALL and grounded == answerable
print("GATE:", "PASS" if passed else "FAIL")
sys.exit(0 if passed else 1)