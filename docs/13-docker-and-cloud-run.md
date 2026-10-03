# 13 · Docker and Cloud Run

How the app is packed into a box and run on the internet.

---

## 1. The problem Docker solves

"It works on my computer!" The app needs Python 3.12, the right packages, a built website... Your friend's computer has different versions. **Docker** packs the app *and* everything it needs into one sealed box, so it runs the same everywhere.

| Word | Meaning | Analogy |
|---|---|---|
| **Image** | The packed box (read-only) | A lunchbox, packed and sealed |
| **Container** | A running copy of an image | The lunchbox, opened and eaten |
| **Dockerfile** | The recipe for packing | The packing list |
| **Registry** | A warehouse for images | A storage shed |

## 2. The Dockerfile in two stages

**Stage 1: build the website (Node.js).**
```dockerfile
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY frontend/ ./
RUN npm run build
```
Install the website's packages, then build the finished website into `frontend/dist`.

**Stage 2: the app (Python).**
```dockerfile
FROM python:3.12-slim AS backend-builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
EXPOSE 8080
CMD uvicorn api.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8080}
```

| Line | Meaning |
|---|---|
| `COPY requirements.txt` + `pip install` **before** copying the code | Docker remembers finished steps. Installing packages is slow and rarely changes, so it goes first and is reused |
| `COPY --from=frontend-builder …` | Takes only the finished website from stage 1. Node.js itself stays out of the final image, which keeps it small |
| `--host 0.0.0.0` | Listen on all network connections inside the box |
| `--port ${PORT:-8080}` | Cloud Run says which port via `PORT`; the default is 8080 |

The backend finds `frontend/dist` and serves it, so **one box = the whole app**.

## 3. What is *not* in the box

`.dockerignore` keeps out `.env`, `credentials/`, `.git`, logs and `node_modules`. Secrets are given to the container when it runs; they are never packed inside.

Run it yourself:

```bash
docker build -t meridian-ai .
docker run -p 8080:8080 --env-file .env meridian-ai
```

For document Q&A the container also needs Google Cloud sign-in:

```bash
docker run -p 8080:8080 --env-file .env \
  -e GOOGLE_APPLICATION_CREDENTIALS=/creds/service-account.json \
  -v "$(pwd)/credentials:/creds:ro" meridian-ai
```

## 4. Cloud Run: a pop-up shop

**Cloud Run** runs your box on Google's computers. It starts a copy when someone visits and scales back to **zero** when nobody does, so you pay only for use.

The workflow deploys with:

```bash
gcloud run deploy meridian-ai-cloud-run \
  --image <image> --region us-central1 --platform managed \
  --allow-unauthenticated --port 8080 --max-instances 3 \
  --set-env-vars="ENVIRONMENT=production,GCP_PROJECT_ID=...,..." \
  --update-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest"
```

| Option | Meaning |
|---|---|
| `--allow-unauthenticated` | Anyone with the address can open the app |
| `--max-instances 3` | Never more than 3 copies, which limits cost if someone floods the address |
| `--set-env-vars` | Plain settings (project, region, bucket, model names, index IDs) |
| `--update-secrets` | Gives the app `GOOGLE_API_KEY` from Secret Manager |

## 5. Things to know about Cloud Run

| Behaviour | Why it matters |
|---|---|
| **Scale to zero** | After a quiet period the first visit is slower (a *cold start*) |
| **Temporary disk** | Files written inside the container disappear when it stops. That is why uploads also go to Cloud Storage and logs are uploaded at shutdown |
| **Identity** | The app uses the project's default service account to reach Vertex AI, Storage and Secret Manager |
| **Public address** | No sign-in. Anyone who finds it can upload files and use your Gemini quota |

> **Public address warning.** Delete the service when you finish ([DEPLOY.md](../DEPLOY.md)) and don't upload private documents.

## 6. Where the image is stored
The workflow names the image `gcr.io/<project>/…`. Google's old Container Registry is shut down; `gcr.io` names now need a matching Artifact Registry repository. If the build or push fails with "permission denied" or "repository does not exist", see the note in [DEPLOY.md](../DEPLOY.md).

## 7. Try it
1. Build and run the box locally and open `http://localhost:8080`.
2. Look at `.dockerignore`. What would happen if `.env` were not listed?
3. Change the `--max-instances` value in `deploy.yml` and explain what it changes.
