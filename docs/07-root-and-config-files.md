# 07 · The root and config files

The files at the top of the repository. Each does one small job.

---

## `README.md` and `DEPLOY.md`
The front door, and the step-by-step guide for putting the app on Google Cloud.

## `.env.example`
A **template** for your private settings. Copy it to `.env` and fill it in.

```bash
cp .env.example .env
```

It lists every setting with a comment. `.env` itself is never saved in Git.

## `.gitignore`
Tells Git what **not** to save. Important entries: `.env`, `credentials/`, `node_modules/`, `dist/`, `__pycache__/`, `*.log`, `.venv`. This is what keeps secrets and clutter out of the repository.

## `requirements.txt`
Every Python package the app needs, with **exact versions** (for example `fastapi==0.135.1`). Exact versions matter because AI libraries change fast and break each other; pinning means everyone gets the same behaviour. Install with `pip install -r requirements.txt`. Groups inside it: web (FastAPI, Uvicorn, Pydantic), LangChain, Google Cloud, PDF reading.

## `requirements-dev.txt`
Says "everything in `requirements.txt`, plus `pytest` and `httpx`" (for tests). Kept separate so the live server does not carry test tools.

## `generate_json.py`
A 5-line script that writes `init_embeddings.json`: **one random vector** (768 numbers) with the id `init_0001`. The vector database must contain at least one item when it is created, so the deploy workflow runs this script and uploads the result. Afterwards the workflow removes that dummy item. You never need to run it yourself.

## `Dockerfile`
The recipe that packs the app into one Docker "box". Two stages:

1. **Build the website** with Node.js (`npm ci`, `npm run build`).
2. **Build the Python image**: install `requirements.txt`, copy `backend/`, copy the finished website from stage 1, then start `uvicorn` on port 8080.

Details in [13](13-docker-and-cloud-run.md).

## `.dockerignore`
What must **not** go into the box: `.env`, `credentials/`, `.git`, logs, `node_modules`. Secrets are never packed into an image anyone could pull.

## `.github/workflows/deploy.yml`
The **delivery robot**: when started (by you, or by a push to `main`), GitHub runs these steps on a temporary computer: sign in to Google Cloud → switch on services → create the bucket → create the vector database → store the Gemini key in Secret Manager → build the image → deploy to Cloud Run → make it public. This file **creates the cloud resources and deploys the app**. Terraform is **not** used in this project. Details in [14](14-provisioning-and-github-actions.md).

## `sample_docs/`
Four made-up PDFs about the fictional Aldermoor Industries:

| File | What it contains (answers a question in the app) |
|---|---|
| `aldermoor_annual_report_fy2024.pdf` | Company overview, revenue FY2024 EUR 2.84 billion |
| `aldermoor_procurement_policy.pdf` | Payment terms (Net-45), sanctions screening, approval limits |
| `eu_tariff_schedule_excerpt.pdf` | Import duty on PLC controllers (2.2 %), import VAT 19 % |
| `aldermoor_accounting_policy_ifrs.pdf` | Depreciation: filling-line equipment 10 years |

## `frontend/`, `backend/`
See [06](06-frontend-files.md) and [05](05-backend-files.md).

## `docs/`
This guide, plus `docs/examples/` with six small programs you can run without any cloud account.

---

## Which file do I edit when…?

| I want to… | Edit |
|---|---|
| Change the AI model | `VERTEX_LLM_MODEL_NAME` in `.env` |
| Make answers more or less random | `LLM_TEMPERATURE` in `.env` |
| Change chunk size | `CHUNK_SIZE` in `backend/rag/data_ingestion.py` |
| Change how many pieces are searched | `k` in `backend/rag/retrieval.py` |
| Change an agent's instructions | `backend/agent/prompts.py` |
| Add a tool | `backend/agent/tools.py`, then give it to an agent in `agents.py` |
| Add a web address | `backend/api/endpoints.py` (and a form in `schemas.py` if it takes data) |
| Change the page layout or tabs | `frontend/src/pages/Index.tsx` |
| Change what the screen calls | `frontend/src/lib/api.ts` |
| Add a Python package | `requirements.txt` |
| Change what gets deployed | `.github/workflows/deploy.yml` |
