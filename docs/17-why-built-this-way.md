# 17 · Why it is built this way

The reasons behind the choices. Some are shortcuts made to keep a learning project simple; those are marked **(shortcut)**. A production system would do them differently.

---

## Structure

| Choice | Why | Cost |
|---|---|---|
| Split into `api`, `rag`, `agent`, `config`, `logger` | One job per part; changes stay local; easy to find things | More files to open |
| Routes are short | A route translates web → function → web. Logic inside routes can't be reused or tested without a server | One extra function call |
| `ingest_pdf()` used by upload **and** bucket import | One behaviour, fixed once | – |
| Frontend and backend in separate folders | Different languages and tools | Two terminals while developing |
| Prompts in their own file | They change more often than code | A little indirection |
| Tests with fake settings | Anyone can run them with no accounts | They test wiring, not answer quality |

## Python and settings

| Choice | Why |
|---|---|
| Pinned versions | AI libraries change fast; pinning gives everyone the same behaviour |
| `requirements-dev.txt` separate | The live server shouldn't carry test tools |
| Settings from environment variables / `.env` | Code stays the same everywhere; secrets stay out of Git |
| One `settings` object | One truth, checked and typed |
| Models and connections created on first use (`lru_cache`) | The app starts, and `/api/health` and the tests work, before any cloud is set up |
| `temperature = 0` | The same question gives (nearly) the same answer: easier to debug |
| Model name is a setting | Models are retired; changing one shouldn't need a code change |

## Document Q&A

| Choice | Why | Trade-off |
|---|---|---|
| 1000-character chunks, 100 overlap | Full idea per piece, precise match, ideas on the edge survive | Too small loses context; too big blurs |
| 768 numbers | The database was created for 768 | Changing the model needs a new database |
| Same embedding model for storing and searching | Numbers from different models can't be compared | – |
| 3 results | Enough context, short prompt | Complex questions may need more (use Contextual) |
| "Answer only from the context, else say you don't know" | Fewer made-up answers | May refuse when the answer is partly there |
| Copy of each PDF in Cloud Storage | The database holds pieces, not originals | Small storage cost |

## Agents

| Choice | Why | Trade-off |
|---|---|---|
| Three specialists, not one agent | Each has a short, focused prompt and only the tools it needs: more reliable | More AI calls: slower, costlier |
| Plain-Python supervisor + one summary call | Control flow you can read and debug | Less flexible than a self-organising graph |
| Agents run one after another | Easy to read and to follow in logs | Could run in parallel for speed |
| Fixed output layouts and keywords | The CFO rules depend on them | A change must be made in two places |
| `create_agent` | The standard builder; runs on LangGraph for you | For loops/branches/approvals you'd use LangGraph directly |
| Tools ask the AI instead of real data **(shortcut)** | No extra accounts needed | A real system must call real services and keep a human reviewer |
| Each tool catches its own errors | One failed lookup shouldn't kill the audit | Errors can hide inside text; read the logs |
| FX check uses a live site first | Facts that exist as data should come from data | Needs internet |

## Web server

| Choice | Why |
|---|---|
| `/api/...` prefix | Keeps API addresses apart from website pages |
| Pydantic forms | Automatic checking, docs and clear errors |
| Errors returned as a message | The screen can show it; learners can debug |
| CORS allows all sites **(shortcut)** | Page (port 3000) and backend (port 8080) are different "origins" while developing |
| Upload's slow part in a helper thread | Server stays responsive |
| `/api/status` doesn't call the cloud | It must work exactly when the cloud is misconfigured |
| The server also serves the website | One box, one address, no CORS issues live |
| Upload history in memory **(shortcut)** | Simple; a database would keep it |

## Logging

| Choice | Why |
|---|---|
| JSON lines | Machines can search and filter them |
| Terminal **and** file | Live view plus a record |
| `severity` field | Google's log viewer uses it |
| One shared logger | One format everywhere |
| Upload logs at shutdown | The container's disk disappears |

## Packaging and cloud

| Choice | Why | Trade-off |
|---|---|---|
| Docker | Same everywhere; Cloud Run runs containers | Something to learn |
| Two-stage Dockerfile | Final box has no build tools | Slightly longer file |
| Copy `requirements.txt` first | Docker reuses slow steps | – |
| `.dockerignore` hides `.env` | Secrets must never be packed in an image | – |
| Cloud Run | No server to manage; scales to zero | Cold starts |
| `--max-instances 3` | Limits cost and abuse | Heavy traffic is limited |
| `--allow-unauthenticated` **(shortcut)** | Anyone can open the demo | Add sign-in for real data |
| Key in Secret Manager | Out of code, images and plain settings | One more service |
| Access to *that one* secret only | Least privilege | – |
| Vector Search endpoint | Managed, fast, fits LangChain | **Hourly cost while deployed** |
| Key file for the robot **(shortcut)** | Simplest to set up | Keys can leak; production uses keyless sign-in |
| `editor` + `projectIamAdmin` **(shortcut)** | One robot can do everything | Far more access than needed |
| Scripts in GitHub Actions, not Terraform | No extra tool; one file does it all | See [14](14-provisioning-and-github-actions.md) |

## What a production version would add

1. Real data sources for sanctions, credit and tax.
2. Sign-in and tighter permissions.
3. A database for history.
4. Automatic tests in the GitHub workflow.
5. Measuring answer quality.
6. A real progress display (streaming) for the audit.
7. Keyless sign-in from GitHub to Google Cloud.

## Other options for each layer

| Layer | Used here | Alternatives |
|---|---|---|
| Cloud | Google Cloud | AWS, Azure |
| Web framework | FastAPI | Flask, Django, Express |
| AI model | Gemini | Claude, GPT, open-source models |
| Vector database | Vertex AI Vector Search | Vector Search 2.0, Postgres + pgvector, Pinecone, Chroma |
| Agents | LangChain `create_agent` | LangGraph, Google ADK, CrewAI, AutoGen |
| Hosting | Cloud Run | App Engine, Kubernetes, a virtual machine |
| Cloud setup | `gcloud` in GitHub Actions | Terraform |

## A way to read any file

Ask: **What is its one job? Who calls it? What does it call? What does it read from settings? What does it log? What breaks if I delete it?**
