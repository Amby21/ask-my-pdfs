import re
from rag import top_chunks, answer
from golden_question import GOLDEN


def cited_pages(reply):
    pages = set()
    for group in re.findall(r"\bpp?\.\s*([\d,\s–-]+)", reply):
        for number in re.findall(r"\d+", group):
            pages.add(int(number))
    return pages
if __name__ == "__main__":
    print(cited_pages("Hold the switch (p. 6) and see (pp. 48, 49)."))
    passed = 0
    total = 0
    fake_retrieved = {6, 49, 55, 58}
    print("self-test unseen:", cited_pages("Hold, then press Menu (p. 6) and see (p. 61).") - fake_retrieved)
    for in_guide, question, expected in GOLDEN:
        if not in_guide:
            continue
        total += 1
        retrieved = {chunk["page"] for score, chunk in top_chunks(question)}
        reply = answer(question)
        cited = cited_pages(reply)
        unseen = cited - retrieved
        ok = bool(cited) and not unseen
        if ok:
            passed += 1
        print(f"{'PASS' if ok else 'FAIL'} | cited {sorted(cited)} | retrieved {sorted(retrieved)} | unseen {sorted(unseen)} | {question}")

    print(f"\nCitations grounded: {passed}/{total}")
