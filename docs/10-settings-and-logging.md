# 10 · Settings and logging

Two small packages, used by almost every file.

---

# Part A · Settings

## The problem
The app needs values that differ between computers (project name, model name) and some that are secret (API key). Typing them into the code means editing code to change them, and saving secrets in Git.

## The solution: environment variables
An **environment variable** is a named value that lives outside your code. Your program asks for it by name.

```bash
export GCP_REGION=europe-west1     # set one for this terminal
echo $GCP_REGION                    # read it back
```

For convenience on your own computer, put them in a **`.env`** file. The app reads it at start-up.

## Where a value comes from (highest wins)

| Priority | Source | Used for |
|---|---|---|
| 1 | A real environment variable | Docker, Cloud Run, one-off tests |
| 2 | The `.env` file in the folder you run from | Your computer |
| 3 | The default in `settings.py` | Fallback |

Try: `python docs/examples/06_settings_demo.py`, then `GCP_REGION=europe-west1 python docs/examples/06_settings_demo.py`.

## `backend/config/settings.py`

```python
class Settings(BaseSettings):
    llm_model_name: str = Field("gemini-3.8-flash", validation_alias="VERTEX_LLM_MODEL_NAME")
    ...
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
```

- Each line is a setting: Python name, type, default, and the **variable name** to read.
- Types are enforced; `"0.5"` becomes the number 0.5.
- `env_file=".env"` is relative to the **folder you run from**. That is why you must run commands from the main folder.
- Every other file does `from config.settings import settings`. Nobody else reads `.env`.

## All the settings

| In `.env` | Default | Used for |
|---|---|---|
| `GOOGLE_API_KEY` | – | The Gemini chat model |
| `GCP_PROJECT_ID` | – | Your Google Cloud project |
| `GCP_REGION` | – | Where it runs |
| `GCS_BUCKET_NAME` | – | Your storage bucket |
| `GCS_PREFIX` | – | Folder for uploads (`uploads/`) |
| `GCP_SERVICE_ACCOUNT_PATH` | – | Path to a key file (optional) |
| `VECTOR_SEARCH_INDEX_ID` | – | Your vector index |
| `VECTOR_SEARCH_INDEX_ENDPOINT_ID` | – | Its endpoint |
| `VERTEX_LLM_MODEL_NAME` | `gemini-3.8-flash` | Chat model |
| `VERTEX_EMBEDDING_MODEL_NAME` | `text-embedding-005` | Embedding model (768 numbers) |
| `LLM_TEMPERATURE` | `0.0` | 0 = most repeatable |
| `ENVIRONMENT` | – | Information only |

## Where each place keeps its settings

| Place | How |
|---|---|
| Your computer | `.env` (never saved in Git) |
| Docker on your computer | `docker run --env-file .env` |
| Cloud Run | Settings in `deploy.yml`; the API key comes from Secret Manager |
| GitHub Actions | Repository **secrets** |
| Tests | `conftest.py` sets fake values |

## Rules
1. Never commit `.env` or a key file.
2. Add every new setting to `Settings` **and** `.env.example`.
3. Read settings only through `settings`.

---

# Part B · Logging

## Why log?
A running server can't be watched. **Logging** is the program writing a **diary**. When something breaks, the diary tells you why. `print()` isn't enough: no importance level, no time, no structure.

## Log levels

| Level | Meaning | Example here |
|---|---|---|
| DEBUG | Details for developers | – |
| INFO | Normal progress | "Loaded PDF", "Phase complete" |
| WARNING | Odd, but handled | "No chunks extracted, skipping" |
| ERROR | Something failed | "Upload failed" |
| CRITICAL | Can't continue | – |

## Plain vs structured logs

Plain: `2026-10-03 03:40 INFO Loaded PDF blob=policy.pdf pages=12`

Structured (what this app writes):
```json
{"blob": "policy.pdf", "pages": 12, "timestamp": "2026-10-02T22:10:45Z", "level": "info", "severity": "INFO", "event": "Loaded PDF from GCS"}
```

A person reads the first more easily, but a **program** can search the second: "show all errors", "count uploads per hour". Run `python docs/examples/02_logging_demo.py` to see both.

You write a message and then named facts:
```python
log.info("Loaded PDF from GCS", blob=blob.name, pages=len(docs))
```

## How the logger is built (`logger/custom_logger.py`)

1. Makes a `logs/` folder and a file named after the start time.
2. Sets **two destinations**: the terminal and that file.
3. Each line passes through a chain: **timestamp** → **level** → **severity** → **message renamed `event`** → **one JSON line**.
4. `logger/__init__.py` creates **one shared logger**; every file imports it as `log`.

## Why a `severity` field?
Cloud Run sends everything your app prints to **Cloud Logging**. Cloud Logging looks for a field named `severity` to decide whether a line is info, warning or error. The `add_severity` step copies the level into that field. The original `level` stays, so nothing breaks.

## Why upload logs when the server stops?
A container's disk is temporary. When Cloud Run stops the server, `logs/` vanishes. `flush_to_gcs()` copies the file to `gs://<bucket>/logs/` first. With no bucket (local runs, tests) it prints a note and skips.

## What is logged where

| Event | File | Level |
|---|---|---|
| Frontend not built | `api/main.py` | warning |
| Failures in audit / questions / upload | `api/endpoints.py` | error |
| Files saved, chunks created | `api/endpoints.py`, `rag/data_ingestion.py` | info |
| Question received / answered | `rag/retrieval.py` | info |
| Each audit phase, with its result | `agent/agents.py` | info |

> Logs contain questions and answers. Treat log files as sensitive and don't use private documents in the demo.

## Reading logs

| Where | How |
|---|---|
| Terminal | Lines appear as the server runs |
| File | `logs/<time>.log`; find errors with `grep '"severity": "ERROR"' logs/*.log` |
| Cloud Run | Console → your service → **Logs**; filter `severity>=ERROR` |
| Bucket | `gs://<bucket>/logs/` after the server stopped |

## Add your own line
```python
from logger import GLOBAL_LOGGER as log
log.info("Vendor screened", vendor=vendor_name, result="CLEARED")
log.error("Credit lookup failed", vendor=vendor_name, error=str(e))
```
One event per line, a short fixed message, facts as named values. **Never** log keys, passwords or whole documents.

## Try it
1. Start the backend, call `/api/health`, open the newest file in `logs/`.
2. Run an audit and watch the phase lines.
3. Leave `VECTOR_SEARCH_INDEX_ID` empty, ask a question, and find the `"level": "error"` line.
