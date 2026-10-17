Ask My PDFs

Question answering over a PDF, built on Azure. Every answer cites the pages it came from, and a question the document can't answer gets a clear NOT_FOUND instead of a guess.

Status: proof of concept. A one-command gate checks refusals, retrieval and citations on every change, and it passes on the sample document. The test set is small (10 questions), so the results show the method works, not that it is production-ready. See Evaluation and Limitations.

How it works
PDF ──► extract text per page ──► chunk (1,000 chars, 150 overlap) ──► embed ──► Azure AI Search index
                                                                                         │
question ──► embed ──► search (local | vector | hybrid) ──► top 5 chunks ◄───────────────┘
                                                                │
                                              gpt-5-mini answers ONLY from those chunks,
                                              cites pages like (p. 6), or replies NOT_FOUND
Step	What happens	Tool
Extract	Read the text of every page	pypdf
Chunk	Cut pages into 1,000-character pieces, 150 overlap, tagged with page number	chunking.py
Embed	Turn each chunk into a 1,536-number vector	Azure OpenAI text-embedding-3-small
Index	Store id, page, text and vector	Azure AI Search (HNSW vector index)
Retrieve	Fetch the 5 most relevant chunks	Azure AI Search, or a local cosine loop
Answer	Answer only from the retrieved chunks, with page citations	Azure OpenAI gpt-5-mini

Authentication uses Microsoft Entra (az login and DefaultAzureCredential). No API keys are stored in the code.

Search modes

SEARCH_MODE in rag.py is a single switch. Both retrieval and answer() follow it, and the evaluation scripts don't change between modes.

Mode	What runs
local	Cosine similarity in Python over chunks.json (the baseline)
vector	Azure AI Search, by meaning only
hybrid	Azure AI Search, meaning plus keywords, merged with rank fusion

An unknown value raises an error rather than silently falling back.

Scores are on different scales per mode, so compare the pages returned, not the numbers:

local: cosine similarity (for example 0.628)
vector: Azure converts cosine to 1 / (2 - cosine) (0.628 shows as 0.729)
hybrid: reciprocal rank fusion, about 0.033 at best
Repository layout
rag.py               search switch, ask() (reply + pages + tokens + timings), answer()
chunking.py          page text -> chunks with page numbers
embed_chunks.py      embeds chunks, writes chunks.json
create_index.py      defines the Azure AI Search index
upload_chunks.py     uploads chunks (with vectors) to the index
golden_question.py   the 10 test questions and the expected pages
recall_at_5.py       is a correct page in the top 5? (per question)
citation_check.py    does every cited page appear in the retrieved pages?
gate.py              runs all checks once; exits 0 (pass) or 1 (fail)
usage_report.py      tokens and timings per question, with averages
tools/find_page.py   finds which PDF pages contain a word (for building the answer key)
Setup

You need an Azure subscription with:

an Azure OpenAI / Foundry resource with two deployments: text-embedding-3-small and gpt-5-mini
an Azure AI Search service (the Free tier is enough for one PDF)

Roles for the identity you use with az login:

permission to call the model deployments (for example Cognitive Services OpenAI User)
Search Service Contributor (create the index) and Search Index Data Contributor (upload and query)
bash
az login
pip install -r requirements.txt

The scripts read two environment variables. Set them in your terminal before running (see .env.example):

bash
export CONTENTUNDERSTANDING_ENDPOINT="https://<your-resource>.cognitiveservices.azure.com/"   # the Azure OpenAI resource
export SEARCH_ENDPOINT="https://<your-search-service>.search.windows.net"

On Windows PowerShell use $env:NAME = "value" instead of export.

Run it

Bring your own PDF. The sample used in development (Apple's iPod Features Guide) is not included.

bash
# 1. Put your PDF in the project folder as sample.pdf
python embed_chunks.py        # extract, chunk, embed -> chunks.json
python create_index.py        # create the Azure AI Search index
python upload_chunks.py       # upload chunks + vectors

# 2. Ask a question
python rag.py "How do I reset my iPod?"

rag.py prints the mode, the retrieved pages, the scores, and then the answer.

Evaluation

All checks run through one command:

bash
python gate.py

It asks each of the 10 test questions once and checks three rules. The gate exits with code 1 if any rule fails, so it can block a change in a CI pipeline.

Rule	What it checks
Refusals	The model answers when the document has the answer, and replies NOT_FOUND when it doesn't (10 questions)
Recall@5	At least one expected page is among the 5 retrieved pages (5 answerable questions)
Citations	Every page the answer cites was among the pages the model was shown

Current result: 0 of 10 refusals wrong, recall@5 5/5, citations grounded 5/5, gate PASS.

The expected pages come from reading the PDF, not from the search. tools/find_page.py finds candidate pages for a word, and each candidate page was read before it went into the answer key.

What testing showed
A similarity-score threshold can't decide when to refuse. The lowest score among answerable questions was 0.524 and the highest among unanswerable ones was 0.521. A near-topic question (Spotify) scores like a real one.
A fixed refusal token makes refusals checkable. Instructing the model to reply with exactly NOT_FOUND turned a free-text refusal into a one-line test.
Retrieve five, not one. In testing, the page with the answer once ranked fifth. Related chunks score close together, so the model reads five and chooses.
Building the answer key meant reading the pages. The word "combination" appears on the volume-limit pages (26 to 28) more often than on the screen-lock pages (48, 49), and "Setting the Language" (p. 10) is a different task from resetting it (p. 58). Counting keyword hits would have produced a wrong key. The back-of-book index pages also match keywords and answer nothing.
Measuring found a bug. Logging tokens showed each question sending about 4,300 input tokens, because the context was built in a nested loop that included every chunk five times. After the fix it is about 920 to 1,200. The tests passed before and after, which is why the bug was invisible without the measurement.
Reasoning dominates the output. Over the 10 questions, about 88% of output tokens were the model's hidden reasoning, and the model call was about 94% of the time per question.
All three search modes tie on this test. Local, vector and hybrid returned the same pages for every question. The questions reuse the guide's own wording, so keyword and meaning matching agree. This test cannot separate the modes.
Cost and speed (10-question run)
	Average per question
Input tokens	about 1,050
Output tokens	about 280 (about 410 when answering, about 140 when refusing)
Model time	about 2.8 s (about 3.6 s when answering, about 1.9 s when refusing)

Measured with one warm-up call first, one request at a time. This is not a load test.

Limitations
The test set is small: 10 questions, 5 of them answerable. It shows the method works, not how accurate the system is in general.
The modes are not separated yet. Questions that avoid the guide's wording, or that depend on an exact term, are needed.
The citation check proves the cited pages were retrieved. It does not prove that the cited page supports the sentence.
Index pages and very short chunks are indexed, and they take result slots.
pypdf flattens tables. Document Intelligence's layout model would read them better.
One document, one search per question. It is a retrieval workflow, not an agent: code decides each step, and there is no tool loop or memory.