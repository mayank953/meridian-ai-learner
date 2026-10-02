# Putting Meridian AI on Google Cloud

This page explains how to run the app on the internet and use document Q&A. It is written step by step. If a word is new, a short explanation follows it.

**Time:** about 30 minutes of work, plus 30–45 minutes of waiting the first time.
**Money:** read [Costs](#costs-read-this-first) before you start.

---

## The big picture

You will do four things:

1. Make a **Google Cloud project** (your own space in Google's cloud).
2. Make a **robot account** that GitHub can use to set things up for you.
3. Tell **GitHub** the robot's key and your Gemini key.
4. Press **Run workflow**. GitHub then creates everything and publishes the app.

You do **not** create the database, storage or server by hand. The file `.github/workflows/deploy.yml` does it using Google's command-line tool (`gcloud`).

---

## Costs (read this first)

| Service | How you are charged |
|---|---|
| **Vector Search** (the database for document Q&A) | **By the hour while it is running, even if nobody uses it.** This is the main cost. |
| Cloud Run (the web server) | Only when used. Light use is usually inside the free monthly allowance. |
| Cloud Storage, Cloud Build, Secret Manager | A few cents, or free allowances |
| Gemini API (the chat model) | Has a free tier. Free-tier content may be used by Google to improve its products, so use only the sample documents. |

**Things to know about Vector Search**

- The setup script does not choose a machine size or number of copies. Google's documentation says the number of copies defaults to **2**, so your hourly cost may be higher than a single small machine. A small machine is reported at roughly **$0.08 per hour (about $56 a month)** by third-party price guides. That is not an official figure; check https://cloud.google.com/vertex-ai/pricing.
- So: **do your cloud work in one sitting and switch the database off when you finish** (see [Switch everything off](#switch-everything-off)). Creating it again takes 30–45 minutes.

**The $300 free credit**

- New Google Cloud customers get **$300 of credit for 90 days** (about three months).
- You need a **credit or debit card**. Google places a temporary hold to check it. It is not a charge.
- You are **not charged automatically** when the trial ends. You are charged only if you choose to upgrade.
- The trial ends at whichever comes first: 90 days or $300 spent. After a 30-day grace period, trial resources are **deleted**.
- Only **new customers** qualify (you have never paid Google Cloud before).
- Trial accounts have limits. Google says some generative-AI services are restricted, and people report tight rate limits. The chat model here uses your Gemini key, so it is not affected. The **embedding** step (turning text into numbers) uses Google Cloud and could be limited. If you see errors like "project is not allowed" during upload, activate the full paid account in Billing: your remaining credit is still used first, and you are charged only for usage beyond it.
- Details: https://docs.cloud.google.com/free/docs/free-cloud-features

**Set a budget alert first** (step 4 below). It sends you an email as your spending grows. It does **not** stop the spending: you must switch things off yourself.

---

## Step by step

### Step 1 · Get a Gemini API key

1. Go to https://aistudio.google.com/apikey and sign in.
2. Click **Create API key** and copy it.
3. Treat it like a password: never post it or put it in Git.

### Step 2 · Create your Google Cloud account

Go to https://cloud.google.com/free and choose **Get started for free**. Add your card when asked.

### Step 3 · Create a project

A **project** holds all your cloud things and your bill.

1. Open https://console.cloud.google.com/.
2. Click the project name at the top → **New project**.
3. Pick a name. Write down the **Project ID** shown underneath (for example `meridian-ai-123456`). You will use the ID, not the name.

### Step 4 · Link billing and set a budget alert

1. Console menu → **Billing** → link your billing account to the project.
2. Console menu → **Billing → Budgets & alerts → Create budget**. Choose your project, set for example **$20**, and keep the email alerts on.

### Step 5 · Install and sign in to `gcloud`

Install Google's command-line tool: https://cloud.google.com/sdk/docs/install. Then:

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Step 6 · Create the robot account

A **service account** is an account for a program instead of a person. Run these (replace `YOUR_PROJECT_ID`):

```bash
export PROJECT_ID="YOUR_PROJECT_ID"        # Windows PowerShell: $env:PROJECT_ID="YOUR_PROJECT_ID"

gcloud iam service-accounts create github-deployer \
  --display-name="GitHub Actions Deployer" --project=$PROJECT_ID

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/resourcemanager.projectIamAdmin"

gcloud iam service-accounts keys create github-deployer-key.json \
  --iam-account=github-deployer@${PROJECT_ID}.iam.gserviceaccount.com
```

The last command makes a file, `github-deployer-key.json`. It is a **password for the robot**.

> **Keep it safe.**
> - Never commit it, email it, or paste it anywhere except the GitHub secret in step 8. Delete the file afterwards.
> - These permissions are broad on purpose, to keep the setup simple. A real company would give the robot only what it needs.
> - If it ever leaks: Console → IAM & Admin → Service accounts → `github-deployer` → Keys → delete it.

### Step 7 · Put the code on your own GitHub

The robot runs from **your** GitHub copy. On this repository's page click **Fork**. Then open the **Actions** tab of your fork and enable workflows if GitHub asks.

### Step 8 · Give GitHub three secrets

In your fork: **Settings → Secrets and variables → Actions → New repository secret**. Add:

| Name | Value |
|---|---|
| `GCP_PROJECT_ID` | Your Project ID |
| `GCP_CREDENTIALS_JSON` | The **whole contents** of `github-deployer-key.json` |
| `GOOGLE_API_KEY` | Your Gemini key |

### Step 9 · Run the workflow

**Actions → Deploy to GCP Cloud Run → Run workflow.** (It also starts by itself whenever you push to `main`.)

It does these jobs in order:

| Job | In plain words |
|---|---|
| Sign in | Logs in as the robot |
| Switch on services | Turns on the Google services the app needs |
| Storage | Creates a bucket (a cloud folder) for PDFs and logs |
| Vector database | Creates the index and endpoint, then starts the service. **This is the 30–45 minute wait** |
| Secrets | Stores your Gemini key in the cloud safe (Secret Manager) |
| Build | Packs the app into a Docker box |
| Deploy | Starts it on Cloud Run and makes it public |

Wait for the green tick. If a step fails, open it, read the last lines, and re-run: it is safe to run again.

> **Possible snag (not yet tested on a fresh project):** the build step names the image `gcr.io/…`. Google's old Container Registry is closed, and `gcr.io` names now need a matching Artifact Registry repository. If the build or push fails with "permission denied" or "repository does not exist", create a Docker repository in Artifact Registry (or change `IMAGE_NAME` at the top of `deploy.yml` to `us-central1-docker.pkg.dev/YOUR_PROJECT_ID/meridian/meridian-ai-cloud-run`, after creating that repository).

### Step 10 · Collect the values you need

```bash
gcloud ai indexes list --region=us-central1
gcloud ai index-endpoints list --region=us-central1
```

Note the ID of the index `financial-docs-production` and of the endpoint `financial-docs-endpoint`. The web address of your app is printed as `Service URL: https://…run.app` in the *Deploy to Cloud Run* step of the workflow log.

### Step 11 · Use it

- **On the internet:** open the Service URL. Upload the PDFs from `sample_docs/` and ask questions.
- **From your own computer** (using the cloud database): put these in your `.env`, sign in with `gcloud auth application-default login`, and start the app as in the README.

```
GCP_PROJECT_ID=YOUR_PROJECT_ID
GCP_REGION=us-central1
GCS_BUCKET_NAME=YOUR_PROJECT_ID-vector-staging
GCS_PREFIX=uploads/
VECTOR_SEARCH_INDEX_ID=<index id>
VECTOR_SEARCH_INDEX_ENDPOINT_ID=<endpoint id>
GOOGLE_API_KEY=<your Gemini key>
```

> **Careful:** the public address has **no login**. Anyone who finds it can use your Gemini quota and upload files. The service is capped at 3 copies to limit the damage. Do not upload private documents, and switch it off when you are done.

---

## Switch everything off

Do this when you finish. It stops the charges.

**Only the expensive part (the vector database):**

```bash
REGION=us-central1
gcloud ai index-endpoints undeploy-index ENDPOINT_ID --deployed-index-id=deployed_financial_docs --region=$REGION
gcloud ai index-endpoints delete ENDPOINT_ID --region=$REGION
gcloud ai indexes delete INDEX_ID --region=$REGION
```

**The web server:**

```bash
gcloud run services delete meridian-ai-cloud-run --region=us-central1
```

**Everything (safest):** deleting the project removes all of its resources. Google keeps it recoverable for 30 days.

```bash
gcloud projects delete YOUR_PROJECT_ID
```

Also: delete the robot's key (step 6), delete `github-deployer-key.json` from your computer, and remove the three GitHub secrets.

**Check:** next day, Billing → Reports should show the daily cost near zero.

---

## If something goes wrong

| What you see | Likely cause and fix |
|---|---|
| `403` / "permission denied" from Storage or Vertex AI | Wrong account or key. Run `gcloud auth list`; for the app use `gcloud auth application-default login` |
| "API has not been used… or it is disabled" | Wait a couple of minutes and retry; the workflow switches the services on |
| "Billing account not enabled" | Link billing to the project (step 4) |
| Workflow fails at sign-in | `GCP_CREDENTIALS_JSON` must be the entire file, including the `{ }` |
| App opens but answers fail | Open the Cloud Run **Logs**; check the Gemini key secret and the index IDs |
| "model not found" | Set `VERTEX_LLM_MODEL_NAME` to a current model: https://ai.google.dev/gemini-api/docs/models |
| First upload is slow or cold | Cloud Run wakes up from zero; the first request is slower |
