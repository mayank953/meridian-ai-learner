# Meridian AI

A small web app that does two jobs, using AI:

1. **Ask questions about your documents.** Upload PDFs (policies, contracts, reports), then ask in plain English. The app answers using only what is in your documents.
2. **Check a purchase before paying.** Paste a purchase request. Three AI "specialists" review it (risk, tax, accounting). A final "CFO" step writes one short memo with a decision.

It is built to **learn from**. The company in the examples, *Aldermoor Industries*, is **fictional**, and the sample documents contain made-up data.

> The "checks" in the audit are done by the AI from its general knowledge (only the exchange-rate check uses a live data source). This is a demo of how such a system is built, **not** a real compliance tool.

**Jump to:** [Technologies](#the-technologies-in-plain-words) · [How it fits together](#how-it-fits-together) · [Why many files?](#why-is-the-code-split-into-many-files) · [What is in this repo](#whats-in-this-repo) · [Run it on your computer](#run-it-on-your-computer) · [Why the cloud?](#why-would-you-need-the-cloud) · [Settings](#settings) · [Problems](#common-problems)

---

## The technologies, in plain words

Think of a **restaurant**. Each technology plays one part.

| Technology | What it is | Restaurant analogy |
|---|---|---|
| **React** (frontend) | The web page you click on | The dining room, menu and buttons |
| **FastAPI** (Python) | Receives requests from the page and sends back answers | The **waiter**: takes your order to the kitchen and brings the food back |
| **Pydantic** | Checks that requests are filled in correctly | The order form: "you forgot the table number" |
| **LangChain** | A toolkit for connecting AI steps together | The kitchen's recipe book and workflow |
| **Gemini** (Google's AI model) | Reads text and writes answers | The **chef** |
| **Embeddings** | Turn text into a list of numbers that capture its *meaning* | GPS coordinates for ideas: similar ideas get nearby coordinates |
| **Vertex AI Vector Search** | A database that finds the stored text closest in meaning to your question | A library catalogue organised by *meaning*, not by title |
| **RAG** (Retrieval-Augmented Generation) | Find the right pages first, then answer from them | An **open-book exam**: the chef checks the cookbook before answering |
| **Agents and tools** | AI that can decide to run small programs (tools) to get facts | A chef who can use a scale, a thermometer and a timer |
| **Cloud Storage** | Keeps files in Google Cloud | A filing cabinet |
| **Docker** | Packs the app and everything it needs into one box | A lunchbox: opens the same anywhere |
| **Cloud Run** | Runs that box on the internet, only when someone visits | A pop-up shop that opens only when customers arrive |
| **Secret Manager** | Stores passwords and keys safely | A safe |
| **GitHub Actions** | Builds and delivers the app automatically | A delivery robot |
| **Logging** (structlog) | The app writes down what it does | The kitchen's diary: when something goes wrong, you read it |

---

## How it fits together

```
 YOU (browser)
   │  click "Ask"
   ▼
 FRONTEND (React)                       the dining room
   │  sends a request
   ▼
 BACKEND (FastAPI)                      the waiter
   │
   ├── Document Q&A (RAG) ───────────┐
   │     1. cut PDFs into small pieces│   Vertex AI: turns pieces into numbers
   │     2. store them ───────────────┼─► Vector Search: finds pieces closest to your question
   │     3. find pieces for question ◄┘
   │     4. ask Gemini to answer from those pieces ─► Gemini
   │
   └── Purchase audit (agents)
         Risk agent    ─ tools ┐
         Tax agent     ─ tools ├─► each calls Gemini, then a "CFO" step writes the memo
         Control agent ─ tools ┘
```

**What happens when you ask a question**

1. You type a question in the page. The page sends it to the backend.
2. The backend turns your question into numbers (an embedding).
3. Vector Search returns the three stored pieces of your documents closest to it.
4. The backend gives Gemini those pieces and your question: *"Answer using only this."*
5. Gemini's answer travels back to your page.

**What happens when you run an audit**

1. You submit a purchase request.
2. The *risk*, *tax* and *control* agents each read it. Each one decides which tools to use (for example, "check the exchange rate") and writes a short report.
3. A final step reads the three reports and writes one memo with a decision: **approved**, **conditional hold**, or **rejected**.

---

## Why is the code split into many files?

You could put everything in one file. For a ten-line experiment that is fine. For a real app it becomes a problem. Think of a kitchen where everyone cooks on one table: you cannot find anything, people get in each other's way, and one spill ruins every dish.

The app is split so that **each folder and file has one job**, like stations in a kitchen:

| Problem with one big file | How splitting helps |
|---|---|
| Hard to find things ("where is the tax prompt?") | The name tells you where to look |
| Changing one thing can break another | A change stays inside its own file |
| Hard to test ("it needs the internet just to start") | Parts can be tested alone |
| Copy-pasted code drifts apart | One function is written once and reused |
| Many people editing the same file clash | People work in different files |
| Intimidating to read | Read one small file at a time |

**Rule of thumb:** *one file, one job.* The web layer does not know how AI works. The AI code does not know what a web address is.

---

## What's in this repo

```
backend/                      The Python server
├── api/                      The "waiter": web addresses and rules
│   ├── main.py                 Creates the app and plugs everything together
│   ├── endpoints.py            Every web address (e.g. POST /api/rag/ask)
│   └── schemas.py              The shape of requests and replies (the order forms)
├── rag/                      Document Q&A (the "library")
│   ├── llm.py                  Gets the Gemini chat model
│   ├── embeddings.py           Text → numbers
│   ├── vector_store.py         Connects to Vector Search
│   ├── data_ingestion.py       PDF → pieces → stored
│   └── retrieval.py            Question → find pieces → answer
├── agent/                    The purchase audit
│   ├── tools.py                The five tools agents can use
│   ├── prompts.py              The written instructions for each agent
│   └── agents.py               Creates the agents and runs them in order
├── config/settings.py        Reads settings (keys, names) from outside the code
├── logger/custom_logger.py   The app's diary (JSON log lines)
└── tests/                    Automatic checks that need no accounts

frontend/                     The web page (React + TypeScript)
└── src/lib/api.ts            The only file that talks to the backend

sample_docs/                  Four made-up PDFs to try the app with
.github/workflows/deploy.yml  Robot that sets up the cloud and deploys the app
Dockerfile                    Recipe to pack the app into one box
requirements.txt              Python packages (exact versions)
.env.example                  Template for your private settings
DEPLOY.md                     How to put the app on the internet
```

Each package depends only on the ones below it:

```
api  →  rag, agent  →  config, logger
```

---

## Run it on your computer

### What you need

| For | You need |
|---|---|
| Everything | **Python 3.12**, **Git**. For the web page also **Node.js 20+** |
| The audit feature | A free **Gemini API key** from https://aistudio.google.com/apikey |
| Document Q&A | A **Google Cloud** project (see [DEPLOY.md](DEPLOY.md)) |

### Quick start: the audit (about 10 minutes, no Google Cloud)

```bash
# 1. Get the code (or download the ZIP from GitHub and unzip it)
git clone https://github.com/mayank953/meridian-ai-learner.git
cd meridian-ai-learner

# 2. Make a private Python environment and install the packages
python3.12 -m venv .venv
source .venv/bin/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# 3. Create your settings file and add your Gemini key
cp .env.example .env                 # Windows: copy .env.example .env
#    open .env and set:  GOOGLE_API_KEY=your-key

# 4. Start the backend
uvicorn api.main:app --app-dir backend --reload --port 8080
```

Now open **http://localhost:8080/docs**. This page is made automatically by FastAPI and lets you try every address:

1. Open `GET /api/health` → **Try it out** → **Execute**. You should see `{"status": "ok"}`.
2. Open `POST /api/agent/audit` → **Try it out**. Paste a request such as:
   ```json
   {"request_text": "Purchase of 200 PLC controllers from Takumi Controls Europe B.V. (Netherlands). Total 480,000 EUR. Origin JP, destination DE. FX rate quoted: 1 EUR = 163.5 JPY."}
   ```
   Press **Execute** and wait: several AI calls are happening, so it can take up to a minute or more.
3. You get four texts: risk, tax and control reports, and the CFO memo. Wording changes each time (an AI writes it), but the layout stays the same.

> Run every command from the project's main folder. The app looks for `.env` in the folder where you start it.

### Add the web page (optional)

Open a **second terminal** and keep the backend running:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**.

### Try document Q&A

This needs the cloud setup in [DEPLOY.md](DEPLOY.md). Once your `.env` has the Google Cloud values:

1. Upload the PDFs in `sample_docs/` (Index Documents tab, or `POST /api/rag/upload`).
2. Ask: *"What is Aldermoor Industries total revenue in FY2024?"* → about **EUR 2.84 billion**.
   Also try: *payment terms for servo motor suppliers* (Net-45), *customs duty on PLC controllers from Japan* (2.2 %), *depreciation of filling line equipment* (10 years).
3. Ask something that is not in the documents. The answer should say it does not know.

### Check that everything is wired up

```bash
pytest backend/tests
```

Expected: `9 passed`. These tests need no accounts and no internet.

### Run it in Docker (optional)

```bash
docker build -t meridian-ai .
docker run -p 8080:8080 --env-file .env meridian-ai
```

Then open http://localhost:8080. (The box does not contain your `.env`, so you pass it in. For document Q&A you must also give it Google Cloud credentials; see [DEPLOY.md](DEPLOY.md).)

---

## Why would you need the cloud?

You do **not** need it for the audit. You do for these reasons:

| Reason | Explanation |
|---|---|
| **Document Q&A needs a vector database** | This app stores document meaning in **Google's Vertex AI Vector Search**, which exists only in Google Cloud. There is no local copy. |
| **Sharing** | On your laptop, only you can open `localhost`. In the cloud, anyone with the link can. |
| **Always on** | Your laptop sleeps and goes offline. A cloud service keeps running. |
| **Automatic delivery** | Each time you save changes, a robot can rebuild and publish the app. |
| **Scaling** | Many users at once? The cloud can start more copies. |

**It costs money.** The vector database is billed **by the hour while it is running, even if nobody uses it.** New Google Cloud customers get a **$300 credit for 90 days**. [DEPLOY.md](DEPLOY.md) explains the costs, how to set a budget alert, and how to switch everything off.

---

## Settings

Settings live in `.env` (copy `.env.example`). `.env` is never uploaded to Git.

| Setting | Meaning | Needed for |
|---|---|---|
| `GOOGLE_API_KEY` | Your Gemini key | Everything with AI |
| `GCP_PROJECT_ID` | Your Google Cloud project | Document Q&A |
| `GCP_REGION` | Where it runs, e.g. `us-central1` | Document Q&A |
| `GCS_BUCKET_NAME` | Cloud Storage bucket name | Document Q&A |
| `GCS_PREFIX` | Folder for uploads, `uploads/` | Document Q&A |
| `VECTOR_SEARCH_INDEX_ID` | ID of your vector index | Document Q&A |
| `VECTOR_SEARCH_INDEX_ENDPOINT_ID` | ID of its endpoint | Document Q&A |
| `GCP_SERVICE_ACCOUNT_PATH` | Path to your key file (optional) | Document Q&A on your computer |
| `VERTEX_LLM_MODEL_NAME` | Chat model, default `gemini-3.8-flash` | Optional |
| `VERTEX_EMBEDDING_MODEL_NAME` | Embedding model, default `text-embedding-005` | Optional |
| `LLM_TEMPERATURE` | `0` = most repeatable answers | Optional |

> AI model names are retired from time to time. If you see "model not found", look up a current name at https://ai.google.dev/gemini-api/docs/models and set `VERTEX_LLM_MODEL_NAME`.

---

## Common problems

| What you see | What to do |
|---|---|
| `ModuleNotFoundError: No module named 'api'` | Run from the main folder and keep `--app-dir backend` |
| Settings seem empty | Run from the main folder (where `.env` is) |
| `ModuleNotFoundError` for other packages | Activate the environment (`source .venv/bin/activate`) and run `pip install -r requirements.txt` |
| `index_id is required` | Set `VECTOR_SEARCH_INDEX_ID` and `VECTOR_SEARCH_INDEX_ENDPOINT_ID` |
| `403` from Google Cloud | Your login or key lacks permission, or the wrong account is used; see [DEPLOY.md](DEPLOY.md) |
| "model not found" | Change `VERTEX_LLM_MODEL_NAME` to a current model |
| Port already in use | Stop the other program, or use `--port 8081` |
| Browser says "blocked by CORS" | The backend is not running on port 8080 |

When something fails, read the last lines in the terminal. The app writes a diary of what it did as one JSON line per event; the error is usually there.

---

*Aldermoor Industries and all sample data are fictional.*
