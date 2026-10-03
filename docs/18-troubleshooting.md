# 18 · Troubleshooting

Find the part that is failing. Each entry: **what you see → why → what to do.** The real error text is usually in the **last lines of your terminal** and in the `detail` field of the reply.

**First checks for almost anything**

1. Are you in the **main folder** (the one with `backend/`, `frontend/`, `README.md`)?
2. Is your Python environment active (you see `(.venv)` in the prompt) and have you run `pip install -r requirements.txt`?
3. Does `.env` hold your Gemini key and, for cloud features, the project, bucket and index IDs? Compare with `.env.example`.

---

## Starting the backend

| You see | Why | Do this |
|---|---|---|
| `ModuleNotFoundError: No module named 'api'` | Started from the wrong folder | Run from the main folder: `uvicorn api.main:app --app-dir backend --reload --port 8080` |
| `ModuleNotFoundError` for another package | Environment not active, or packages not installed | `source .venv/bin/activate` then `pip install -r requirements.txt` |
| Settings look empty at `/api/status` | `.env` is read from the folder you start in | Start from the main folder |
| `Address already in use` | Port 8080 is taken | Stop the other program, or use `--port 8081` (and set `VITE_API_URL=http://localhost:8081` for the page) |
| `422 Unprocessable Entity` | The request body doesn't match the form | Compare with `/docs`; the reply names the missing field |

## The web page

| You see | Why | Do this |
|---|---|---|
| Browser says "blocked by CORS policy" | The backend isn't reachable | Start the backend on port 8080 |
| Page loads but every action fails | Backend not running or wrong address | Check `http://localhost:8080/api/health` |
| Blank page on the Docker address | The website wasn't built into the image | Rebuild the image |
| Audit progress steps move but nothing arrives | The steps run on timers. The real answer comes at the end | Wait; read the terminal for errors |

## The AI model

| You see | Why | Do this |
|---|---|---|
| `404 … model … not found` / "no longer available to new users" | The model was retired or isn't available to your key | Set `VERTEX_LLM_MODEL_NAME` to a current model: https://ai.google.dev/gemini-api/docs/models |
| `API key not valid` | Wrong or malformed key | Create a new key; no spaces or line breaks in `.env` |
| `ImportError: cannot import name 'create_agent'` | An old `langchain` is installed | `pip install -r requirements.txt` |
| `ModuleNotFoundError: langchain_classic` | Package missing | `pip install -r requirements.txt` |
| Tool results say `LLM_ERROR` or `SYSTEM WARNING … Manual review required` | A tool's own AI call failed (key, quota, model name) | Fix the key/model; check the logs |
| The answer repeats itself or loops | Model behaviour | Try `LLM_TEMPERATURE=1.0` or another model |
| Answers differ each time | Normal: an AI writes them | The layout and key words should stay the same |
| Exchange-rate check always uses the AI fallback | The live site `api.frankfurter.dev` isn't reachable from your network | Normal; the tool is built to fall back |

## Google Cloud and the vector database

| You see | Why | Do this |
|---|---|---|
| `index_id is required for api_version='v1'` | `VECTOR_SEARCH_INDEX_ID` / endpoint ID is empty | Fill them in `.env` ([DEPLOY.md](../DEPLOY.md), step 10) |
| `403 … does not have storage.objects.create access` (or any 403) | You are signed in as a different Google account or key | `gcloud auth list`; for the app: `gcloud auth application-default login`, or set `GCP_SERVICE_ACCOUNT_PATH` |
| "API has not been used… or it is disabled" | The service isn't switched on | Wait a couple of minutes and retry; the workflow switches them on |
| "Billing account … not enabled" | No billing linked | Link billing to the project |
| `DefaultCredentialsError` | No Google sign-in found for your code | `gcloud auth application-default login` |
| "Project is not allowed to use…" or repeated rate limits on a free-trial account | Trial accounts have restricted access/quotas for some Google AI services | In Billing, activate the full account (your credit is still used first) |
| Dimension mismatch when storing | The embedding model doesn't give 768 numbers | Use `text-embedding-005` (default) |
| Searches return nothing right after upload | New data takes a short while to become searchable | Wait about a minute |
| Duplicate answers | The same document was uploaded twice | Upload each once |
| Surprise bill | The vector database is billed by the hour | Delete it: [DEPLOY.md](../DEPLOY.md#switch-everything-off) |

## Docker and Cloud Run

| You see | Why | Do this |
|---|---|---|
| Container starts but settings are empty | The box has no `.env` by design | `docker run --env-file .env …` (see [13](13-docker-and-cloud-run.md)) |
| "container failed to start and listen on the port" | The app crashed or isn't using `$PORT` | Read the Cloud Run **Logs** |
| `npm ci` fails during the build | Lock file out of sync | `cd frontend && npm install`, commit `package-lock.json` |
| Address says 403 Forbidden | Public access wasn't applied | The last workflow step grants it; re-run |
| First request is slow | Scale-to-zero cold start | Normal |

## GitHub Actions

| You see | Why | Do this |
|---|---|---|
| Sign-in step fails ("credentials_json") | The secret isn't the whole key file | Copy the whole file, including `{ }` |
| App fails at runtime, key looks empty | `GOOGLE_API_KEY` secret missing | Add it under Settings → Secrets and variables → Actions |
| Build or push of `gcr.io/...` fails (permission or repository missing) | Google's old Container Registry is shut down; `gcr.io` names need an Artifact Registry repository. **Not yet tested on a fresh project** | See the note in [DEPLOY.md](../DEPLOY.md) |
| "Index creation in progress" never ends | First creation is slow | Re-run; it skips what exists |
| Run takes 40+ minutes | Normal the first time | Later runs take minutes |
| Every push to `main` redeploys | By design | Work on a branch; use **Run workflow** manually |
