# 04 · Project tour

Every folder, why it exists, and why the code is split into many files.

---

## 1. The whole repository

```
meridian-ai-learner/
│
├── backend/                  PYTHON: the server (the "kitchen")
├── frontend/                 TYPESCRIPT/REACT: the screens (the "dining room")
│
├── sample_docs/              4 made-up PDFs to try the app
├── docs/                     This guide
│
├── Dockerfile                Recipe to pack the app into one box
├── .dockerignore             What must NOT go into the box
├── .github/workflows/        The delivery robot (GitHub Actions)
│
├── requirements.txt          Python packages (exact versions)
├── requirements-dev.txt      + tools for testing
├── .env.example              Template for your private settings
├── .gitignore                What Git must not save
├── generate_json.py          Makes one starter vector for the database
│
├── README.md                 The front door
└── DEPLOY.md                 How to put it on Google Cloud
```

## 2. Why isn't it just one file?

You *could* put everything in one file. For ten lines that's fine. For a real app it causes trouble. Picture a kitchen where everyone cooks on a single table.

| Problem with one big file | How splitting solves it |
|---|---|
| **Hard to find things.** "Where is the tax prompt?" | The name tells you: `agent/prompts.py` |
| **One change breaks something else.** | A change stays inside its own file |
| **Hard to test.** The file needs the internet just to start. | Parts can be tested alone |
| **Copy-pasted code drifts apart.** | One function, written once, used everywhere |
| **Several people editing one file clash.** | Different people, different files |
| **Scary to read.** | Read one small file at a time |

The rule: **one file, one job.** The waiter doesn't cook; the chef doesn't take orders.

### Where it started

An earlier stage of this project kept the agent logic and the document logic in two large files, `agent.py` and `rag.py`. They were later split into packages (`agent/`, `rag/`, `api/`, `config/`, `logger/`). The ideas are the same; each piece is now easy to find and change. A later cleanup also removed copy-pasted code: uploading a PDF and importing PDFs from the bucket now share **one** function, `ingest_pdf()`.

## 3. The backend folders (the kitchen stations)

| Folder | Question it answers | Analogy |
|---|---|---|
| `backend/api/` | How does the outside world talk to the server? | The **waiter** |
| `backend/rag/` | How do we find the right passages in documents and answer from them? | The **cookbook shelf and chef** |
| `backend/agent/` | How do the AI specialists check a purchase? | The **audit team** |
| `backend/config/` | Where do settings come from? | The **manager's notebook** |
| `backend/logger/` | How does the app write down what it does? | The **diary** |
| `backend/tests/` | How do we know it still works? | The **taste test** |

### Who may use whom

```
api  →  rag, agent  →  config, logger
```

Arrows point one way. `rag` never imports `api`. `config` imports nothing from the project. This keeps the code easy to test and prevents "A needs B needs A" tangles.

## 4. The frontend folder

| Path | What it is |
|---|---|
| `frontend/src/lib/api.ts` | **The only file that calls the backend** |
| `frontend/src/pages/Index.tsx` | The page: sidebar and four tabs |
| `frontend/src/components/*Tab.tsx` | The four screens |
| `frontend/src/components/ui/` | Ready-made buttons, cards, inputs (generated; don't edit) |
| `frontend/package.json` | The frontend's shopping list and commands |

The frontend lives in its own folder because it has its own language, tools (`npm`) and build output.

## 5. Why the backend and frontend are separate

| Reason | Explanation |
|---|---|
| Different languages and tools | Python + `pip` vs TypeScript + `npm` |
| Independent change | Redesign the screen without touching the AI logic |
| Same backend, many screens | A phone app or another program could use the same API |

## 6. Folders that appear on your computer but are *not* saved in Git

| Folder | Made by | Why not saved |
|---|---|---|
| `.venv/` | `python -m venv` | Your private Python; can be recreated |
| `frontend/node_modules/` | `npm install` | Downloaded packages; can be recreated |
| `frontend/dist/` | `npm run build` | Built website; Docker rebuilds it |
| `logs/`, `backend/logs/` | the logger | Your local diary |
| `__pycache__/`, `.pytest_cache/` | Python tools | Caches |
| `.env`, `credentials/` | you | **Secrets** |

## 7. Which parts need which accounts?

| Part | Gemini key | Google Cloud |
|---|:---:|:---:|
| `/api/health`, `/api/status` | – | – |
| Tests (`pytest backend/tests`) | – | – |
| Audit (`/api/agent/audit`) | ✔ | – |
| Document Q&A (`/api/rag/...`) | ✔ | ✔ |

## 8. Read the files next

- Backend, file by file → [05](05-backend-files.md)
- Frontend, file by file → [06](06-frontend-files.md)
- Root and config files → [07](07-root-and-config-files.md)
