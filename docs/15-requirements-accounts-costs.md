# 15 · What you need: skills, accounts, software, costs

---

## 1. Skills

| You should know | How well |
|---|---|
| Python | Functions, classes, packages, virtual environments |
| **LangChain basics** | Prompts, chat models, chains, what a tool is |
| Command line | Run commands, set environment variables |
| Git | Clone a repository |

You do **not** need cloud, FastAPI, Docker or CI/CD experience. This guide explains them.

## 2. Accounts

| Account | Needed for | Cost | Path |
|---|---|---|---|
| **Google account** | All Google things | Free | all |
| **Gemini API key** (https://aistudio.google.com/apikey) | The AI model | Free tier; see below | all |
| **Google Cloud account** | Vector database, storage, hosting | **$300 free credit** for new customers | cloud |
| **GitHub account** | Robot that sets up and deploys | Free | cloud |

A **card is required** for Google Cloud, even for the free trial. Google places a temporary hold to check it; it is not a charge.

### Gemini API key
- Has a **free tier** for `gemini-3.8-flash`, with rate limits.
- Free-tier content may be **used by Google to improve its products**. Use only the sample documents.
- Paid tier prices (per 1 million tokens): input $0.75 and output $3.75 until 31 Dec 2026; $1.50 and $7.50 from 1 Jan 2027. Paid content is not used for improvement.
- Models are retired from time to time. Check https://ai.google.dev/gemini-api/docs/models.

### The $300 Google Cloud credit
| Question | Answer |
|---|---|
| How much? | **$300** |
| For how long? | **90 days** (about three months) |
| Who? | **New customers only** |
| Card? | Yes (hold, not charge) |
| Automatic charge after? | **No**; only if you upgrade |
| When it ends | At 90 days **or** $300 used, whichever first. After a 30-day grace period, trial resources are **deleted** |
| Limits | Some generative-AI services are restricted; people report tight limits on trial accounts. The chat model uses your Gemini key, so it is unaffected. The **embedding** step runs on Google Cloud and could be limited. If you see "project is not allowed…", upgrade to the full account (credit is still used first) |

Source: https://docs.cloud.google.com/free/docs/free-cloud-features

## 3. Software

| Tool | Version | Used for |
|---|---|---|
| Python | 3.12 | Backend |
| Node.js + npm | 20+ | Frontend |
| Git | any recent | Getting the code |
| Google Cloud CLI (`gcloud`) | recent | Cloud setup (cloud path) |
| Docker Desktop | recent | Optional |
| A code editor (e.g. VS Code) | – | Reading and editing |

**Windows:** the commands use macOS/Linux style. **WSL 2** is the smoothest way to follow along.

Computer: 8 GB memory, 3 GB free disk, internet.

## 4. What costs money

| Service | Billed | Expect |
|---|---|---|
| **Vector Search** | **By the hour while deployed, even with no users** | **The main cost** |
| Cloud Run | Only when used | Usually inside the free monthly allowance |
| Cloud Storage, Cloud Build, Secret Manager | Tiny | Cents or free allowances |
| Gemini API | Free tier or per token | Free for light use |

**Vector Search warning.** The setup script does not choose a machine size or number of copies. Google's documentation says the number of copies defaults to **2**. A small machine is reported at about $0.08 an hour (roughly $56 a month) by third-party guides; that is not an official figure (https://cloud.google.com/vertex-ai/pricing). **Do your cloud work in one sitting and delete the database when you finish.** A **budget alert** only emails you; it does not stop spending.

Steps and the clean-up commands are in [DEPLOY.md](../DEPLOY.md).

## 5. Time

| Task | Time |
|---|---|
| Audit on your computer | about 10–30 minutes |
| Google Cloud setup | about 30–45 minutes |
| First cloud deployment | **30–45 minutes of waiting** |
| Reading this guide | 2–3 hours |

## 6. Checklist
- [ ] Google account
- [ ] Gemini API key
- [ ] Python 3.12, Node.js 20+, Git
- [ ] (Cloud) Card, budget alert, `gcloud`, GitHub account
