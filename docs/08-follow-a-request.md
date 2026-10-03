# 08 · Follow a request through the code

Watch what happens, file by file, when you use the app. Open the files as you read.

---

## 1. The server starts

You run: `uvicorn api.main:app --app-dir backend --port 8080`

| Step | File | What happens |
|---|---|---|
| 1 | `api/main.py` | Python opens it. It imports `api/endpoints.py` |
| 2 | `api/endpoints.py` | Its imports bring in the agent and document code, settings and the logger. **No AI model and no database is created yet** |
| 3 | `config/settings.py` | Builds the `settings` object from `.env` |
| 4 | `logger/__init__.py` | Makes the `logs/` folder and the shared logger |
| 5 | `api/main.py` | Creates the app, adds CORS, registers the routes, serves the website if it was built |
| 6 | Uvicorn | Starts listening. You see `Application startup complete` |

Because nothing external is created at start-up, the server starts even with an empty `.env`. That is why `/api/health` always works.

## 2. You upload a PDF

| Step | File → function | What happens |
|---|---|---|
| 1 | `DocumentUploadTab.tsx` | You choose a PDF and click upload |
| 2 | `lib/api.ts` → `uploadDocument` | Sends it to `POST /api/rag/upload` |
| 3 | `api/endpoints.py` → `upload_documents` | Non-PDFs are marked "skipped" |
| 4 | same | Saves the file temporarily and copies it to your Cloud Storage bucket |
| 5 | `rag/data_ingestion.py` → `ingest_pdf` | Reads the pages, marks each with its source |
| 6 | `split_into_chunks` | Cuts the text into pieces (1000 characters, 100 overlap) |
| 7 | `rag/vector_store.py` → `get_vector_store` | **First use:** connects to Vector Search |
| 8 | `add_documents` | Turns each piece into 768 numbers and stores it |
| 9 | `endpoints.py` | Replies `{filename, status, pages, chunks}` |
| 10 | `logger` | Every step wrote one log line |

## 3. You ask a question

| Step | File → function | What happens |
|---|---|---|
| 1 | `RagQATab.tsx` → `askQuestion` | `POST /api/rag/ask` with your text and search type |
| 2 | `api/schemas.py` → `QueryRequest` | FastAPI checks the request |
| 3 | `endpoints.py` → `rag_query` | Calls `ask_question` |
| 4 | `rag/retrieval.py` → `build_retriever` | Picks the search type |
| 5 | `ask_question` | Builds the prompt and the two chains |
| 6 | `rag_chain.invoke` | Question → numbers → closest pieces → prompt → Gemini |
| 7 | `endpoints.py` | Replies `{answer}` |

## 4. You run an audit

| Step | File → function | What happens |
|---|---|---|
| 1 | `AuditTab.tsx` → `runAudit` | `POST /api/agent/audit` |
| 2 | `endpoints.py` → `run_audit` → `get_supervisor` | **First use:** `ProcurementSupervisor()` builds three agents |
| 3 | `agents.py` → `run_audit` | Runs the Risk agent, then Tax, then Control |
| 4 | Inside each agent | The AI reads its prompt, **picks a tool**, `tools.py` runs it, the AI reads the result, repeats, then writes its report |
| 5 | `agents.py` | Fills the CFO template with the three reports and asks the AI for the memo |
| 6 | `endpoints.py` | Replies with `risk_result`, `tax_result`, `control_result`, `cfo_memo` |

While this runs, the screen's progress steps move on timers (see [06](06-frontend-files.md)).

## 5. The server stops

`api/main.py` → `lifespan` → `flush_to_gcs()` uploads the log file to `gs://<your-bucket>/logs/…`. (The server's own disk disappears when it stops.)

## 6. Why this layout works

| Benefit | Because |
|---|---|
| The server starts and demos with no cloud | Nothing external is created at start-up |
| Tests need no accounts | Tests replace the two functions the routes call |
| Swap the AI or the database | Only `llm.py`, `embeddings.py` or `vector_store.py` change |
| Upload and bucket import act the same | Both call `ingest_pdf` |
| Prompts are easy to tune | They are plain text in `prompts.py` |
| Failures are visible | Every step logs; every route turns errors into a message |
