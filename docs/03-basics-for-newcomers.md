# 03 · Basics for newcomers

New to building software projects? This page explains the words used in the rest of the guide. Skim it, and come back whenever a word is unfamiliar.

---

## 1. A project is a folder of many kinds of files

| Kind | Examples here | Rule |
|---|---|---|
| **Code**: instructions the computer runs | `backend/rag/retrieval.py` | Read it, change it carefully |
| **Settings**: values that change behaviour | `.env`, `requirements.txt` | Change values, not logic |
| **Secrets**: keys and passwords | your Gemini key inside `.env` | **Never put in Git** |
| **Data**: input files | `sample_docs/*.pdf` | Replace with your own |
| **Documents**: explanations for people | `README.md`, this guide | Keep up to date |
| **Automation**: scripts run by a robot | `.github/workflows/deploy.yml` | Trigger it, let it run |
| **Generated**: made by tools | `frontend/dist/`, `node_modules/`, `__pycache__/` | **Never edit; not saved in Git** |

## 2. Git and GitHub

- A **repository** ("repo") is your project folder plus the full history of changes.
- **Git** records that history. A **commit** is one saved set of changes with a note. A **branch** is a separate line of work.
- **GitHub** is a website that stores repos so people can share them.
- **`.gitignore`** lists files Git must **not** save: secrets, generated files. That is how a password avoids ending up on the internet by accident.
- **Fork** = your own copy of someone else's repo on GitHub.

## 3. Frontend and backend

```
 your browser                     a computer running your Python
┌─────────────┐   request ──►    ┌──────────────────┐
│  FRONTEND   │                   │  BACKEND         │
│ what you see│   ◄── response    │ the real work    │
└─────────────┘                   └──────────────────┘
```

- **Frontend**: the screen, running in your browser. Here: React (TypeScript).
- **Backend**: the engine, running on a server. Here: Python with FastAPI.
- They talk through an **API**: a menu of web addresses the backend offers, each doing one job. Data travels as **JSON**, which looks like a Python dictionary: `{"query": "hello"}`.

## 4. Python words

| Word | Meaning | Here |
|---|---|---|
| **Module** | One `.py` file | `retrieval.py` |
| **Package** | A folder of modules (has an `__init__.py` file) | `backend/rag/` |
| **Import** | Use code from another file | `from rag.llm import get_llm` |
| **Dependency** | Someone else's code that yours uses | `fastapi`, `langchain` |
| **`requirements.txt`** | The shopping list of dependencies | project root |
| **Pinned version** | An exact version, e.g. `fastapi==0.135.1`, so everyone gets the same behaviour | `requirements.txt` |
| **Virtual environment** | A private box of Python and packages for one project | `.venv/` |

Normal routine:

```bash
python3.12 -m venv .venv            # make the private box (once)
source .venv/bin/activate           # step inside it (every new terminal)
pip install -r requirements.txt     # install the shopping list
```

Forgot to step inside? You will see `ModuleNotFoundError`.

## 5. Settings stay outside the code

Some values change from computer to computer (project name, model name) and some are secret (API key). Typing them inside code is a bad idea: you would edit code to change them, and secrets would be saved in Git.

Instead the program reads **environment variables**: named values that live outside the code.

- On your computer, a file called **`.env`** holds them:
  ```
  GOOGLE_API_KEY=abc123
  GCP_REGION=us-central1
  ```
- **`.env.example`** is a *template* showing the names without real values. It **is** saved in Git. You copy it to `.env` and fill it in.
- On the live server there is no `.env`; the hosting platform provides the values.

## 6. One file, one job

A project is split into small parts where **each has one job**, so you can find things by name and change one part without breaking others. Think of kitchen stations: one for salads, one for grill, one for desserts. See [04](04-project-tour.md).

## 7. Words about the cloud

| Word | Plain meaning |
|---|---|
| **Cloud provider** | A company (here Google) that rents you computers, storage and services over the internet |
| **Project (Google Cloud)** | Your named space that holds your resources and your bill |
| **Provisioning** | Creating the cloud things your app needs (storage, database, server) |
| **Deployment** | Putting a new version of your app on those things |
| **Docker image / container** | A sealed box containing your app plus everything it needs. The *container* is a running copy |
| **CI/CD** | A robot that builds and delivers your app automatically whenever you push changes |
| **API key** | A password-like string that lets your program use a service |
| **Service account** | An account for a *program* instead of a person |
| **Log** | A diary the program writes while running |

## 8. Words about AI

| Word | Plain meaning |
|---|---|
| **LLM** (large language model) | An AI that reads and writes text, e.g. Gemini |
| **Prompt** | The instructions you give the AI |
| **Token** | A small chunk of text (roughly a short word); AI pricing counts tokens |
| **Embedding** | A list of numbers that captures the *meaning* of a text. Similar meaning → similar numbers |
| **Vector database** | A database that finds the stored items with the most similar numbers |
| **RAG** | "Look up the relevant pieces first, then answer from them" |
| **Hallucination** | When an AI states something confidently that is not true |
| **Tool** | A small program an AI may choose to run to get a fact |
| **Agent** | An AI that decides which tools to use, step by step |
| **Temperature** | How random the AI's wording is. 0 = most repeatable |

More in the [glossary](19-glossary.md).

**Next:** [04 · Project tour](04-project-tour.md).
