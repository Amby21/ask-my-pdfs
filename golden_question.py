from rag import answer

GOLDEN = [
    (True,  "How do I reset my iPod?",[6,55]),
    (True,  "How do I turn on the backlight?",[6,10]),
    (True,  "How do I set the backlight timer?",[10]),
    (True,  "How do I lock the iPod screen with a combination?",[48,49]),
    (True,  "How do I reset the language?",[10,58]),
    (False, "How do I install Windows 11?",[]),
    (False, "Can I use this iPod with an Android phone?",[]),
    (False, "How do I download songs from Spotify onto the iPod?",[]),
    (False, "What is the weather in Chicago?",[]),
    (False, "What is a good recipe for pancakes?",[]),
]
MUST = {
    # p.6 and p.55: slide Hold to HOLD and back, then press Menu + Center ~6 s
    "How do I reset my iPod?": ["hold", "menu", "center"],

    # p.6: "Press any button or use the Click Wheel."
    "How do I turn on the backlight?": ["any button", "click wheel"],

    # p.10: "Choose Settings > Backlight Timer, and then choose the time you want."
    "How do I set the backlight timer?": ["settings"],

    # p.48-49: Extras > Screen Lock > Set Combination
    "How do I lock the iPod screen with a combination?": ["extras", "screen lock"],

    # p.58: Menu > Settings > Reset All Settings > Reset, then choose a language
    "How do I reset the language?": ["settings"],
}
if __name__ == "__main__":
    wrong = 0
    print("ok   in_guide  refused  question")
    for in_guide, question,expected in GOLDEN:
        reply = answer(question)                      # full RAG: search + model
        refused = reply.strip() == "NOT_FOUND"        # True if the model refused
        ok = (refused == (not in_guide))              # refusing is right only when NOT in the guide
        if not ok:
            wrong += 1
        print(f"{'yes' if ok else 'NO':4} {str(in_guide):9} {str(refused):8} {question}")

    print("\nwrong:", wrong, "of", len(GOLDEN))