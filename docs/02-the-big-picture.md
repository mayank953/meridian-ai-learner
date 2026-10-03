# 02 · The big picture

How the whole app fits together, in simple terms. No code yet.

---

## 1. The restaurant

Imagine a restaurant. This is the picture to keep in your head for the whole project.

| In the restaurant | In Meridian AI | Code |
|---|---|---|
| **Dining room**: menu, tables, you | The web page: tabs and buttons | `frontend/` |
| **Waiter**: takes your order to the kitchen and brings the food back | The web server (API) | `backend/api/` |
| **Order form**: the waiter checks it is filled in | Request checking (Pydantic) | `backend/api/schemas.py` |
| **Chef**: cooks the meal | The AI model (Gemini) | `backend/rag/llm.py` |
| **Cookbook shelf** the chef checks before cooking | Your documents, found by meaning (RAG) | `backend/rag/` |
| **Kitchen helpers**: a scale, a thermometer, a timer | Agent tools | `backend/agent/tools.py` |
| **Head chef's instructions to each station** | Prompts | `backend/agent/prompts.py` |
| **Manager's notebook** with the restaurant's settings | Settings (`.env`) | `backend/config/` |
| **Kitchen diary**: what was cooked, what went wrong | Logs | `backend/logger/` |
| **Safe** for the keys | Secret Manager | Google Cloud |
| **Delivery robot** that opens a new branch | GitHub Actions | `.github/workflows/` |

## 2. The picture

```
 YOU
  │ click a button
  ▼
┌──────────────────────┐
│ FRONTEND (React)     │   what you see, runs in your browser
└──────────┬───────────┘
           │ sends a request (JSON over HTTP)
           ▼
┌──────────────────────┐
│ BACKEND (FastAPI)    │   the waiter: checks the request, calls the right helper
└───┬──────────────┬───┘
    │              │
    ▼              ▼
┌──────────┐   ┌──────────────────────────────┐
│ RAG      │   │ AGENTS                       │
│ (answers │   │ Risk · Tax · Control         │
│  from    │   │   each uses tools            │
│  your    │   │ then a CFO step writes memo  │
│  docs)   │   └──────────────┬───────────────┘
└────┬─────┘                  │
     │                        │
     ▼                        ▼
 Vector Search ─ stores        Gemini ─ the AI model
 meaning of your docs          (writes the answers)
 Embeddings ─ text → numbers
```

## 3. The two journeys

### Journey 1 · Ask a question about documents

**Getting the documents in (once):**

1. You upload a PDF.
2. The backend reads the text and **cuts it into small pieces** (about a paragraph each).
3. Each piece is turned into **numbers that capture its meaning** (an *embedding*).
4. The pieces and their numbers are stored in the **vector database**.

**Asking (every time):**

1. You type a question.
2. The question is turned into numbers the same way.
3. The database returns the **three pieces closest in meaning**.
4. The backend tells Gemini: *"Here are some pieces of our documents. Answer the question using only these."*
5. Gemini writes the answer.

This is **RAG** (Retrieval-Augmented Generation). *Analogy: an open-book exam.* The chef looks up the right cookbook pages first and then answers.

### Journey 2 · Audit a purchase

1. You paste a purchase request.
2. **Three agents** read it, one after another:
   - **Risk agent** (tools: sanctions check, credit score)
   - **Tax agent** (tools: tax calculator, exchange-rate check)
   - **Control agent** (tool: expense classifier)
3. Each agent decides which of its tools to use, reads the results, and writes a short report in a fixed layout.
4. A **CFO step** reads the three reports and writes one memo. Simple written rules decide the outcome: `RED ALERT` → **REJECTED**; `FX ALERT` or `HOLD FOR TREASURY AUDIT` → **CONDITIONAL HOLD**; all clear → **APPROVED TO PAY**.

An **agent** is an AI that can *choose to use tools* to get facts before answering. *Analogy: a chef who can pick up a thermometer.*

## 4. Layers: who is allowed to talk to whom

```
 Layer 1  Screen          frontend/
 Layer 2  Web server      backend/api/
 Layer 3  Helpers         backend/rag/        backend/agent/
 Layer 4  Basics          backend/config/     backend/logger/
```

Rule: **a layer only uses the layers below it.** The web server may call the helpers, but the helpers know nothing about web addresses. Settings and logging are at the bottom, so everyone can use them and they depend on nothing.

## 5. Where it runs

| Place | What runs there |
|---|---|
| **Your computer** (development) | Backend on port 8080, web page on port 3000. Good for learning and for the audit |
| **Google Cloud** (live) | One Docker "box" on **Cloud Run** holding both the backend and the web page; **Vector Search** (the document database); a **Cloud Storage** bucket; **Secret Manager** for the key |
| **Google's AI** | **Gemini** answers questions (called with your API key). **Embeddings** use Google Cloud |

## 6. The pieces, once more, in a table

| Piece | Job | Analogy |
|---|---|---|
| React | The screen | Dining room |
| FastAPI | Connects screen to logic | Waiter |
| Pydantic | Checks requests | Order form |
| LangChain | Connects AI steps | Recipe book |
| Gemini | Writes answers | Chef |
| Embeddings | Text → meaning-numbers | GPS for ideas |
| Vector Search | Finds closest meaning | Library catalogue by meaning |
| RAG | Look up, then answer | Open-book exam |
| Agents + tools | AI that can use instruments | Chef with a thermometer |
| Docker | Packs the app | Lunchbox |
| Cloud Run | Runs it on the internet | Pop-up shop |
| Cloud Storage | Keeps files | Filing cabinet |
| Secret Manager | Keeps keys | Safe |
| GitHub Actions | Delivers it | Delivery robot |
| Logging | Writes what happened | Diary |

**Next:** [03 · Basics for newcomers](03-basics-for-newcomers.md).
