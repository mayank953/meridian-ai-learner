# 14 · Creating the cloud resources and deploying (GitHub Actions)

> **Short answer: this project creates its cloud resources with GitHub Actions running `gcloud` commands (`.github/workflows/deploy.yml`). It does *not* use Terraform.**

---

## 1. Two words

- **Provisioning** = creating the things your app needs in the cloud (storage, database, server).
- **Deployment** = putting your app's newest code onto those things.

This project's workflow does **both** in one go.

## 2. What gets created

| Resource | What it is for |
|---|---|
| Switched-on Google services (APIs) | A service must be enabled in a project before use |
| Cloud Storage **bucket** | PDFs, logs, staging data for the database |
| Vertex AI Vector Search **index**, **endpoint**, **deployed index** | The document database and its running search service (billed by the hour) |
| Secret Manager **secret** | Holds your Gemini key |
| Docker **image** | The packed app |
| Cloud Run **service** | Runs the app, with a public address |

## 3. How to create cloud things

| Way | What you do | Good | Not so good |
|---|---|---|---|
| **Click in the console** | Use Google's website | Easy to learn | Slow; hard to repeat; no record |
| **Commands in a script** *(this project)* | A list of `gcloud` commands, run by GitHub Actions | Repeatable; the file is the record; no extra tool | You must write "only if missing" checks yourself |
| **Terraform** *(not used here)* | You describe the end result; the tool makes it so | Previews changes; remembers what exists; cleans up | One more tool to learn; a state file to protect |

*Imperative* (this project) means you write the **steps**. *Declarative* (Terraform) means you write the **end result**.

## 4. The "check, then create" pattern

The workflow can be run again and again because each step first checks whether the thing exists. Example:

```bash
if ! gcloud storage buckets describe gs://PROJECT-vector-staging >/dev/null 2>&1; then
  gcloud storage buckets create gs://PROJECT-vector-staging --location=us-central1 \
    --uniform-bucket-level-access --public-access-prevention
else
  echo "Vector bucket already exists."
fi
```

`describe` succeeds if the bucket exists; `!` flips that; so `create` only runs the first time. The same trick is used for the index, endpoint, deployed index and secret.

## 5. When it runs

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
```

- Automatically on every push to the `main` branch.
- By hand: **Actions → Deploy to GCP Cloud Run → Run workflow**.

Pushes to other branches do **not** deploy. Experiment on a branch.

## 6. The steps

| # | Step | In plain words |
|---|---|---|
| 1 | Checkout | Download the code onto the robot's computer |
| 2 | Authenticate | Sign in to Google Cloud with the robot's key (`GCP_CREDENTIALS_JSON`) |
| 3 | Set up Cloud SDK | Install `gcloud` |
| 4 | Enable APIs | Switch on the Google services needed; wait 90 seconds |
| 5 | Buckets | Create the bucket if missing |
| 6 | Starter file | Run `generate_json.py` and copy the one dummy vector to the bucket |
| 7 | Vector Search | Create the index, the endpoint, deploy the index, remove the dummy item. **30–45 minutes the first time** |
| 8 | Secrets | Store your Gemini key in Secret Manager; allow the app to read that one secret |
| 9 | Build | `gcloud builds submit` builds and stores the image |
| 10 | Deploy | `gcloud run deploy` with settings, the secret and `--max-instances 3` |
| 11 | Public access | Let anyone open the address; print the access rules |

The Gemini key is passed to the step through an environment variable, so its value doesn't appear in the command text.

## 7. Reading a run

1. Open **Actions** and click the run.
2. Click the job and expand a step.
3. A red cross marks the failed step. Read the last lines.
4. Press **Re-run failed jobs**. It's safe thanks to the "check, then create" pattern.

## 8. The three GitHub secrets

| Secret | What it is |
|---|---|
| `GCP_PROJECT_ID` | Your Google Cloud project ID |
| `GCP_CREDENTIALS_JSON` | The robot's key file (whole contents) |
| `GOOGLE_API_KEY` | Your Gemini key |

GitHub encrypts secrets and hides them in logs. Never print them or write them in code.

## 9. Security notes

| Topic | Note |
|---|---|
| The key file | A long-lived "password for the robot". A safer modern method is *Workload Identity Federation*, where GitHub proves who it is with no stored key |
| Broad permissions | The robot has `editor` and `projectIamAdmin`: easy for learning, too much for production |
| Public address | No sign-in; capped at 3 copies |

## 10. About Terraform

Many teams use **Terraform** instead of scripts to create cloud resources. It is **not** part of this project. If you want to learn it later, you would write the same list (bucket, index, endpoint, secret, Cloud Run service) as declarations, run `terraform plan` to preview, and `terraform apply` to create. Don't run both approaches on the same project: they would try to create the same names.

## 11. Try it
1. Find the three "check, then create" blocks in the Vector Search step.
2. Find where the Gemini key reaches Cloud Run, and explain why it isn't written in the file.
3. Change `--max-instances 3` to `2` and describe what changes.
