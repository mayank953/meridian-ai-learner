# 09 · FastAPI explained

FastAPI is the **waiter** of the app. This page explains it from scratch. Runnable companion: `docs/examples/01_fastapi_hello.py`.

---

## 1. What is an API?

Two programs talk by sending text messages over the internet using rules called **HTTP**.

A **request** has:

| Part | Example | Meaning |
|---|---|---|
| Method | `POST` | What to do: `GET` = read, `POST` = send data to process |
| Address (path) | `/api/rag/ask` | What you are talking to |
| Body | `{"query": "hello"}` | The data (as **JSON**) |

A **response** has a **status code** and usually a body:

| Code | Meaning | Where you see it here |
|---|---|---|
| 200 | OK | Normal success |
| 400 | Bad request | Upload with no files |
| 404 | Not found | A wrong `/api/...` address |
| 422 | Your data has the wrong shape | A missing field; FastAPI replies automatically |
| 500 | The server failed | An error inside a route; the message is in `detail` |

## 2. What FastAPI does for you

You write normal Python functions. FastAPI:

1. matches the address and method to the right function (**routing**);
2. checks the incoming data against your **type hints** (**validation**);
3. calls your function;
4. turns the result into JSON;
5. builds a clickable documentation page at **`/docs`**.

```python
@rag_router.post("/ask", response_model=QueryResponse)
def rag_query(payload: QueryRequest):
    return QueryResponse(answer=ask_question(payload.query, payload.retriever_type))
```

The hint `payload: QueryRequest` tells FastAPI: *the body must have a `query` text and an optional `retriever_type`.*

## 3. Three names that confuse people

- **FastAPI**: the framework; your routes and rules.
- **Uvicorn**: the program that listens on the network and passes requests to FastAPI.
- **`api.main:app`**: "in the module `api.main`, use the variable `app`." That is what you give Uvicorn.

Useful options: `--reload` (restart when you save a file), `--port 8080`, `--app-dir backend` (look for packages inside `backend/`).

## 4. Pydantic: the order-form checker

```python
class QueryRequest(BaseModel):
    query: str
    retriever_type: str = "similarity"      # has a default, so it is optional
```

- `{"query": "hi"}` → accepted.
- `{}` → rejected: *Field required*.

Open `/docs`, try `POST /api/rag/ask` with `{}`, and read the 422 message.

## 5. Routers: groups of routes

```python
rag_router = APIRouter(prefix="/api/rag", tags=["RAG"])
@rag_router.post("/ask")          # full address: /api/rag/ask
```

`prefix` is added to every route in the group; `tags` group them on `/docs`. `main.py` plugs the groups in with `app.include_router(...)`.

## 6. `def` or `async def`?

A server handles many users at once.

| Style | What happens |
|---|---|
| **`def`** | FastAPI runs it in a helper thread. While one request waits for Gemini, others are served |
| **`async def`** | Runs on the main loop. You use `await` for waiting. **Slow code that isn't awaited freezes everyone** |

`upload_documents` is `async def` because it must `await` the file. But embedding a PDF is slow, so it is handed to a helper thread:

```python
summary = await run_in_threadpool(ingest_pdf, local_path, f"upload://{upload.filename}")
```

**Rule of thumb:** use plain `def` unless you need `await`; never run slow code directly inside `async def`.

## 7. Errors

An uncaught error becomes a bare "500". The routes here catch errors, log them, and reply with a message:

```python
raise HTTPException(status_code=500, detail=str(e))
```

The web page reads `detail` and shows it, so you see the real reason.

## 8. CORS in one minute

A browser blocks a page on `localhost:3000` from calling an API on `localhost:8080` unless the API agrees. The API's agreement is called **CORS**. This project allows every website (`allow_origins=["*"]`), which is convenient for learning but should be restricted in production. In Docker/Cloud Run the page and API share one address, so CORS is not even needed.

## 9. `lifespan`: code at start and stop

```python
@asynccontextmanager
async def lifespan(app):
    yield                              # the server runs here
    _LOGGER_INSTANCE.flush_to_gcs()    # runs once when the server stops
```

## 10. One server, two jobs

If `frontend/dist` exists, the same server also serves the website. The API routes are registered first, so `/api/...` reaches the API. A final "catch-all" route returns a real file if it exists, otherwise `index.html`.

## 11. `lru_cache`: do it once

```python
@lru_cache(maxsize=1)
def get_supervisor():
    return ProcurementSupervisor()
```

"Run the first time, remember the answer." Used for the AI model, the embeddings, the database connection and the audit team, so nothing expensive happens at start-up.

## 12. Testing without a server

```python
client = TestClient(app)
assert client.get("/api/health").json() == {"status": "ok"}
```

To test a route that would call Gemini, swap the function for a stand-in:

```python
monkeypatch.setattr(endpoints, "ask_question", lambda query, retriever_type: "stub answer")
```

See `backend/tests/test_api.py`.

## 13. Common mistakes

| Mistake | You see | Fix |
|---|---|---|
| Running from the wrong folder | `No module named 'api'` | Run from the main folder with `--app-dir backend` |
| Slow code inside `async def` | Whole server freezes | Use `def` or `run_in_threadpool` |
| Catch-all route registered first | Every `/api/...` returns the web page | Register API routes first |
| `.env` not found | Settings empty | Run from the folder that holds `.env` |

## 14. Try it

1. Run the example: `uvicorn 01_fastapi_hello:app --reload --port 8001` (from `docs/examples/`) and open `http://localhost:8001/docs`.
2. Trigger a 422 and a 400.
3. Add a `DELETE /orders/{id}` route.
