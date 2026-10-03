# 16 · Exercises

Learn by doing. Each exercise says what to do and what you should see. Do them in order within a topic. Hints are at the end of each group.

> Exercises marked **(cloud)** need the Google Cloud setup from [DEPLOY.md](../DEPLOY.md). All others work with just a Gemini key or with nothing at all.

---

## A · Find your way around (no setup)

1. Which file decides the chunk size? Which decides the number of search results? Which holds the tax agent's instructions?
2. Which single file does the web page use to call the backend?
3. List the seven web addresses of the backend and what each does.
4. Draw the folder tree from memory, with one word per folder.
5. Why does `rag/` never import from `api/`?

*Hints:* `rag/data_ingestion.py`, `rag/retrieval.py`, `agent/prompts.py`; `frontend/src/lib/api.ts`; see [05](05-backend-files.md); [04](04-project-tour.md).

## B · Run the small examples (no accounts)

1. Run `docs/examples/03_chunking_demo.py`. Change `CHUNK_SIZE` to 100 and then 400. How does the number of pieces change?
2. Run `05_similarity_demo.py`. Add a fourth document and a question so the closest match changes.
3. Run `02_logging_demo.py`. Add a `log.warning(...)` of your own.
4. Run `04_tool_demo.py`. Change the docstring and watch the description change.
5. Run `06_settings_demo.py` with `LLM_TEMPERATURE=0.7 python 06_settings_demo.py`.

## C · The tests (no accounts)

1. Run `pytest backend/tests`. Expect `9 passed`.
2. Open `test_api.py`. Find the test that checks the question route. Find where it swaps `ask_question` for a stand-in.
3. Break something on purpose: change `"status": "ok"` in `endpoints.py` to `"status": "fine"`. Run the tests. Which fails? Fix it.
4. Write a test that `GET /api/rag/uploads` returns `{"uploads": []}`. (Other tests may already have added entries, so clear `endpoints._upload_history` at the start of your test.)

## D · FastAPI (no accounts)

1. Start the backend. In `/docs` call `POST /api/rag/ask` with `{}`. Read the 422 message.
2. Add a route `GET /api/ping` returning the current time. See it appear in `/docs`.
3. Run `docs/examples/01_fastapi_hello.py`. Trigger a 422 and a 400.
4. In the example, add a route with `async def` that calls `time.sleep(10)`. While it runs, open another route. Change `async def` to `def` and repeat. What differs?

*Hint for 2:* in `endpoints.py`, copy the `health` route and return `{"time": datetime.now(timezone.utc).isoformat()}`.

## E · Settings and logging (a Gemini key helps)

1. Start the backend and open `/api/status`. Change `GCP_REGION` in `.env`, restart, and look again.
2. Find the newest file in `logs/`. What is in it after a `/api/health` call?
3. Add a log line to `rag/retrieval.py` recording the length of the answer.
4. Leave `VECTOR_SEARCH_INDEX_ID` empty and call `POST /api/rag/ask`. Find the `"level": "error"` line in the log.
5. Use `grep '"severity": "ERROR"' logs/*.log` to list only errors.

## F · The audit (Gemini key)

1. Run an audit with the example request from the README. Read all four texts.
2. Run it again. What changed and what stayed the same?
3. Use `1 EUR = 190 JPY`. Which report shows `FX ALERT`? What is the CFO decision?
4. Add a sixth tool, `check_delivery_risk(country: str)`, to `tools.py` and give it to the Control agent in `agents.py`. Does the agent use it? (Mention delivery risk in your request.)
5. Change the `75` in the risk prompt to `90`. Run the same request. What changes?
6. Remove the "OUTPUT FORMAT" section from one prompt. What happens to the report and the memo?

## G · Document Q&A **(cloud)**

1. Upload the four PDFs in `sample_docs/`. Note the `pages` and `chunks` reported for each.
2. Ask the four example questions in [01](01-the-case.md). Check the answers.
3. Ask something not covered. You should get "I don't know".
4. Ask the same question with Normal, Multi-Query and Contextual Compression. Compare speed and answer.
5. Change `CHUNK_SIZE` to 300, upload a PDF again, ask again. Did the answer change?

## H · Packaging and delivery

1. Build the Docker box: `docker build -t meridian-ai .` Run it and open `http://localhost:8080`.
2. Read `.dockerignore`. Explain what could go wrong without `.env` listed.
3. Read `.github/workflows/deploy.yml`. Find the three "check, then create" blocks.
4. Find where the Gemini key travels from a GitHub secret to the running app. Name each place.
5. **(cloud)** Run the workflow. Then delete the vector database and check Billing the next day.

## I · Think like a designer

1. The audit tools ask the AI instead of real databases. List two risks and what you would connect instead.
2. The audit progress bar is driven by timers. How would you build a *real* progress display?
3. The deployed app has no login. Name two ways to protect it.
4. Why does the CFO step use fixed keywords instead of asking the AI to "decide"?
5. What would you change to make the audit run its three agents in parallel? What would you lose?

*Hints:* see [06](06-frontend-files.md) (timers), [17](17-why-built-this-way.md).

## Check yourself

You understand the project when you can, without notes:

- explain the restaurant picture and name which folder is which part;
- follow a question from the button to the answer, naming each file;
- say why the code is split and which file you'd edit for a given change;
- explain why a vector database that is "just sitting there" still costs money.
