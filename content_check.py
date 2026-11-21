from golden_question import MUST

def has_must(question,reply):
    reply_lower = reply.lower().split()
    req_words = MUST[question]
    reply_text = " ".join(reply_lower)
    return all(word in reply_text for word in req_words)
