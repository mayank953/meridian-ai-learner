# 05 · The backend, file by file

Open each file next to this page. For every file you get: **what it is for**, **what is inside**, **how it connects** to the others, and something to **try**.

Files are in the order you would read them, from the bottom layer up: settings and logging first, then document Q&A, then agents, then the web layer.

> A note on `__init__.py`: every package folder has one. It tells Python "this folder is a package". Most are empty.

---

## Layer 4 · The basics

### `backend/config/settings.py` — the manager's notebook

**Job:** read every setting (keys, names, IDs) from *outside* the code and hand it to the rest of the app.

**Inside:** one class, `Settings`, and one ready object, `settings`.

```python
class Settings(BaseSettings):
    llm_model_name: str = Field("gemini-3.8-flash", validation_alias="VERTEX_LLM_MODEL_NAME")
    llm_temperature: float = Field(0.0, validation_alias="LLM_TEMPERATURE")
    GOOGLE_API_KEY: str = Field("", validation_alias="GOOGLE_API_KEY")
    ...
settings = Settings()
```

Step by step:

1. Each line is **one setting**: a Python name, a type, a default, and the **environment variable name** to read (`validation_alias`).
2. When the file loads, Python looks for the value in this order: a real environment variable → the `.env` file → the default.
3. Types are checked. `LLM_TEMPERATURE=0.5` becomes the number `0.5`. `LLM_TEMPERATURE=abc` stops the program with a clear error.
4. At the bottom, if `GCP_SERVICE_ACCOUNT_PATH` points to a real file, the code sets the standard variable `GOOGLE_APPLICATION_CREDENTIALS` so Google's libraries find your key.

**Connects:** everything imports it: `from config.settings import settings`. It imports nothing from the project.

**Try:** run `python docs/examples/06_settings_demo.py`, then `GCP_REGION=europe-west1 python docs/examples/06_settings_demo.py`.

### `backend/logger/custom_logger.py` — the diary

**Job:** write down what the app does, as one line per event, to the screen and to a file.

**Inside:** a function `add_severity` and a class `CustomLogger`.

1. `CustomLogger.__init__` makes a `logs/` folder and picks a file name from the current time. It also registers `flush_to_gcs` to run when the program exits.
2. `get_logger()` sets up **two destinations** (the terminal and the file) and a chain of steps every log line passes through: add a timestamp → add the level → add `severity` → name the message `event` → turn it into one JSON line.
3. `add_severity` copies the level into a field named `severity`, because Google's log viewer uses that name to colour and filter lines.
4. `flush_to_gcs()` uploads the log file to your bucket when the server stops (the server's own disk disappears when it shuts down). If no bucket is set, it just prints a note.

A log line looks like this:

```json
{"pages": 12, "timestamp": "2026-10-02T22:10:45Z", "level": "info", "severity": "INFO", "event": "Loaded PDF from GCS"}
```

**Connects:** `logger/__init__.py` creates the one shared logger, `GLOBAL_LOGGER`. Every other file starts with `from logger import GLOBAL_LOGGER as log`. More in [10](10-settings-and-logging.md).

**Try:** start the backend, call `/api/health`, then open the newest file in `logs/`.

---

## Layer 3a · Document Q&A (`backend/rag/`)

### `rag/llm.py` — the chef

**Job:** give the rest of the app the Gemini chat model.

```python
@lru_cache(maxsize=1)
def get_llm():
    return ChatGoogleGenerativeAI(model=settings.llm_model_name,
                                  google_api_key=settings.GOOGLE_API_KEY,
                                  temperature=settings.llm_temperature)
```

1. `ChatGoogleGenerativeAI` is LangChain's wrapper for Gemini. It needs the model name, your **API key**, and a temperature.
2. `@lru_cache` means: *do it once, remember the answer.* The model is created the first time someone asks, then reused. Nothing is created when the app starts, so the app starts even without a key.
3. `extract_text()` handles a Gemini quirk: sometimes a reply arrives as a list of pieces instead of plain text. It joins the text pieces.

**Connects:** used by `retrieval.py`, `tools.py` and `agents.py`.

### `rag/embeddings.py` — GPS for ideas

**Job:** turn text into a list of **768 numbers** that capture its meaning.

```python
@lru_cache(maxsize=1)
def get_embeddings():
    return VertexAIEmbeddings(model_name=settings.embedding_model_name)
```

- Uses **Google Cloud** sign-in (not the API key).
- The database was built to hold exactly 768 numbers per item, and the **same model must be used for storing and for searching**. Change the model and you must make a new database.

**Try:** see the idea with tiny numbers: `python docs/examples/05_similarity_demo.py`.

### `rag/vector_store.py` — the library catalogue

**Job:** connect to the Vertex AI Vector Search database.

```python
@lru_cache(maxsize=1)
def get_vector_store():
    aiplatform.init(project=settings.GCP_PROJECT, location=settings.GCP_REGION)
    return VectorSearchVectorStore.from_components(
        project_id=..., region=..., embedding=get_embeddings(),
        index_id=settings.vector_search_index_id,
        endpoint_id=settings.vector_search_index_endpoint_id,
        gcs_bucket_name=settings.GCS_BUCKET_NAME,
        stream_update=True)
```

1. Tells Google's library which project and region to use.
2. Connects to your **index** (the stored data) and **endpoint** (the running search service) using their IDs.
3. `stream_update=True`: new documents become searchable quickly.
4. If the index ID is empty you get: `index_id is required for api_version='v1'`.

### `rag/data_ingestion.py` — putting documents in

**Job:** get PDFs *into* the database.

Three functions:

| Function | What it does |
|---|---|
| `split_into_chunks(pages)` | Cuts pages into pieces of about 1000 characters; neighbouring pieces overlap by 100 characters so a sentence at the edge isn't lost |
| `ingest_pdf(local_path, source)` | Loads one PDF → marks each page with where it came from → splits → stores the pieces (embeddings are made automatically) → returns `{"pages": n, "chunks": n}` |
| `ingest_data_from_gcs()` | Finds every PDF in your bucket folder and calls `ingest_pdf` for each |

**Why it matters:** both the upload button and the "import from bucket" button use `ingest_pdf`, so fixing a bug once fixes both.

**Try:** `python docs/examples/03_chunking_demo.py`; change `CHUNK_SIZE` and run again.

### `rag/retrieval.py` — getting answers out

**Job:** answer a question from the stored documents.

- `SYSTEM_PROMPT`: the instruction to the AI: *use the context below; if the answer isn't there, say you don't know; be concise.*
- `build_retriever(type)`: chooses *how* to search:

| Type | How it searches | Trade-off |
|---|---|---|
| `similarity` (Normal) | the 3 closest pieces | fastest |
| `multiquery` | the AI rewrites your question several ways and merges the results | finds more, slower |
| `contextual` | fetches 10 pieces, then the AI trims each to its useful part | cleanest, slowest |

- `ask_question(query, type)` builds two chains and runs them:

```python
question_answer_chain = create_stuff_documents_chain(get_llm(), prompt)   # put pieces into the prompt, call Gemini
rag_chain = create_retrieval_chain(build_retriever(retriever_type), question_answer_chain)  # search first, then the above
response = rag_chain.invoke({"input": query})
return response["answer"]
```

**Note:** `create_retrieval_chain` comes from the package `langchain_classic`, while agents use the newer `langchain`. Both are installed. Online examples mix them.

---

## Layer 3b · The audit agents (`backend/agent/`)

### `agent/tools.py` — the instruments

**Job:** five small functions an agent may call. Each is marked `@tool` and has a **docstring** (the one-line description), which is what the AI reads to decide when to use it.

| Tool | Used by | What it does | Where the facts come from |
|---|---|---|---|
| `check_sanctions_list(vendor_name)` | Risk | Says `CLEARED` or `RED ALERT` | The AI's general knowledge |
| `get_vendor_credit_score(vendor_name)` | Risk | Score 0–100 and risk level (unknown vendors get 45) | The AI's general knowledge |
| `calculate_cross_border_tax(amount, origin, destination)` | Tax | VAT, import duty, total cost | The AI's general knowledge |
| `validate_fx_hedge(currency_pair, rate_used)` | Tax | Compares the quoted rate with the market rate; more than 5 % apart = `FX ALERT` | **A live exchange-rate website**; the AI only if that fails |
| `categorize_expense(amount, item_description)` | Control | Capital asset (CapEx) or running cost (OpEx), plus approval flags | The AI's general knowledge |

Helper `_ask_llm(prompt)` calls the AI and catches errors. If a tool's AI call fails, the tool returns a message like `SYSTEM WARNING … Manual review required` instead of crashing the whole audit.

**Try:** `python docs/examples/04_tool_demo.py` shows what an agent actually "sees" of a tool.

### `agent/prompts.py` — the job descriptions

**Job:** the written instructions for each agent, kept as plain text.

Four texts: `RISK_AGENT_PROMPT`, `TAX_AGENT_PROMPT`, `CONTROL_AGENT_PROMPT`, `SYNTHESIS_PROMPT_TEMPLATE` (the CFO). Each agent prompt has the same **four parts**:

1. **Role**: who you are.
2. **Responsibilities**: what you are accountable for.
3. **Decision framework**: which tool first, what the thresholds are.
4. **Output format**: the exact layout of your answer.

A fixed layout lets the next step rely on it. The CFO prompt looks for exact words:

| Word in a report | Result |
|---|---|
| `RED ALERT` | **REJECTED** |
| `FX ALERT` or `HOLD FOR TREASURY AUDIT` | **CONDITIONAL HOLD** |
| everything `APPROVED` / `SUCCESS` | **APPROVED TO PAY** |

If you rename one of these words, rename it everywhere.

### `agent/agents.py` — the team and the CFO

**Job:** build the three agents and run them in order.

```python
def create_specialized_agent(tools, system_prompt):
    return create_agent(model=get_llm(), tools=tools, system_prompt=system_prompt)
```

An **agent** = the AI + some tools + a job description. `create_agent` (from LangChain) builds one. (It runs on a library called LangGraph underneath; this project does not write any LangGraph code.)

`ProcurementSupervisor`:

1. `__init__`: builds the three agents, each with its own tools and prompt.
2. `_invoke_agent(agent, request)`: sends the request, waits, returns the agent's final text.
3. `run_audit(request)`: runs **Risk → Tax → Control**, one after another, then fills the CFO template with the three reports and asks the AI for the final memo. Returns four texts.

Each phase writes a log line, so you can follow an audit in the terminal.

**Try:** from the `backend/` folder: `GOOGLE_API_KEY=your-key python -m agent.agents` runs a built-in sample audit.

---

## Layer 2 · The web server (`backend/api/`)

### `api/schemas.py` — the order forms

```python
class QueryRequest(BaseModel):
    query: str
    retriever_type: str = "similarity"
class QueryResponse(BaseModel):
    answer: str
```

Four classes: `AuditRequest`, `AuditResponse`, `QueryRequest`, `QueryResponse`. FastAPI checks every incoming request against them. A missing field gives an automatic **422** error naming the field. They also create the documentation page at `/docs`.

### `api/endpoints.py` — the menu of web addresses

| Address | Function | What it does |
|---|---|---|
| `GET /api/health` | `health` | Returns `{"status": "ok"}` |
| `GET /api/status` | `system_status` | Shows settings and uptime (does not call Google) |
| `POST /api/agent/audit` | `run_audit` | Runs the audit |
| `POST /api/rag/ask` | `rag_query` | Answers a question |
| `POST /api/rag/upload` | `upload_documents` | Saves PDFs to the bucket and indexes them |
| `GET /api/rag/uploads` | `list_uploads` | Shows uploads since the server started |
| `POST /api/rag/ingest-gcs` | `trigger_gcs_ingestion` | Indexes every PDF already in the bucket |

Every route is **short**: check input → call one function → return the result (or an HTTP 500 with the real error message). Two details:

- `get_supervisor()` builds the audit team on the first audit request (and then remembers it).
- `upload_documents` is the only `async` route. The slow part (reading and embedding the PDF) runs in a helper thread so the server stays responsive.

### `api/main.py` — putting it together

1. Creates the `FastAPI` app (title and version come from settings).
2. Adds **CORS** so a browser page on another port may call the API (it allows every website — fine for learning, restrict it in production).
3. Registers the four groups of routes.
4. A `lifespan` function uploads the log file to the bucket when the server stops.
5. If the folder `frontend/dist` exists (inside Docker), it also **serves the website**: real files if they exist, otherwise `index.html`. Unknown `/api/...` addresses return 404, and files outside `dist` can't be read.

---

## Tests · `backend/tests/`

| File | What it does |
|---|---|
| `conftest.py` | Runs first: sets fake settings so no accounts are needed |
| `test_api.py` | Nine checks: health, status, unknown address, question route, audit route, non-PDF rejected, chunking, sample PDFs load, log severity |

The tests replace the AI and the cloud with simple stand-ins, so they are fast, free and repeatable. Run: `pytest backend/tests` (expect `9 passed`).

**Next:** [06 · The frontend, file by file](06-frontend-files.md).
