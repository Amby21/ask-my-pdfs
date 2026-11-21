import sys
from rag import ask
from golden_question import GOLDEN
from citation_check import cited_pages
from content_check import has_must

PRICES = {
    "gpt-5-mini": (0.25, 2.00),
    "gpt-6-luna": (0.10, 0.50),
}

def cost_usd(model, tokens_in, tokens_out):
    price_in, price_out = PRICES[model]
    return (tokens_in * price_in + tokens_out * price_out) / 1_000_000

def flag(value):
    """True -> yes, False -> No, None-> '-" (Not applicable)"""
    if value is None:
        return "-"
    return "yes" if value else "NO"

def run_exam(model):
    rows = []
    for in_guide, question , expected in GOLDEN:
        r = ask(question,model=model)

        if not r["served_model"].startswith(model):
            raise RuntimeError(
                f"asked for {model} but {r['served_model']} answered"
            )

        reply = r["reply"]
        refused = reply.strip() == "NOT_FOUND"
        refusal_ok = refused == (not in_guide)
        content_ok = None   # only meaningful for answerable questions
        grounded = None
        if in_guide:
            content_ok = has_must(question, reply)
            cited = cited_pages(reply)
            grounded = bool(cited) and not (cited - set(r["pages"]))

        rows.append({
            "question": question,
            "in_guide": in_guide,
            "refusal_ok": refusal_ok,
            "content_ok": content_ok,
            "grounded": grounded,
            "prompt_tokens": r["prompt_tokens"],
            "completion_tokens": r["completion_tokens"],
            "model_s": r["model_s"],
            "served_model": r["served_model"],
            "cost": cost_usd(model, r["prompt_tokens"], r["completion_tokens"]),
        })
    return rows

if __name__ == "__main__":
    model = sys.argv[1]
    rows = run_exam(model)

    print(f"model: {model}  (served by {rows[0]['served_model']})")
    print("refus content ground  in   out  secs  question")
    for row in rows:
        print(
            f"{flag(row['refusal_ok']):6} {flag(row['content_ok']):7} "
            f"{flag(row['grounded']):6} {row['prompt_tokens']:4} "
            f"{row['completion_tokens']:4} {row['model_s']:5.1f}  {row['question']}"
        )

    answerable = [x for x in rows if x["in_guide"]]
    n = len(rows)
    print()
    print(f"Refusal correct:   {sum(x['refusal_ok'] for x in rows)}/{n}")
    print(f"Content ok:        {sum(bool(x['content_ok']) for x in answerable)}/{len(answerable)}")
    print(f"Citations grounded:{sum(bool(x['grounded']) for x in answerable)}/{len(answerable)}")
    print(f"Avg tokens in/out: {sum(x['prompt_tokens'] for x in rows)/n:.0f} / "
          f"{sum(x['completion_tokens'] for x in rows)/n:.0f}")
    print(f"Avg model seconds: {sum(x['model_s'] for x in rows)/n:.1f}")
    avg_cost = sum(x["cost"] for x in rows) / n
    print(f"Avg cost/question: ${avg_cost:.6f}   (per 1,000 questions: ${avg_cost*1000:.2f})")
