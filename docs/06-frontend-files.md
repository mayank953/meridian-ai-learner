# 06 · The frontend, file by file

The frontend is the **screen**: what you see and click, running in your browser. It is built with **React** (a library for making screens out of reusable parts), **TypeScript** (JavaScript with checks), **Vite** (a tool that builds and serves it), **Tailwind CSS** (styling with short class names) and **shadcn/ui** (ready-made buttons and cards).

You do **not** need to know React to understand this project. What matters is how the screen **talks to the backend**.

---

## 1. The files that matter

### `frontend/src/lib/api.ts` — the one place that calls the backend

Every request to the backend is made here. One small helper and one function per address:

```ts
const BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? "http://localhost:8080" : "");

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}
```

Step by step:

1. `BASE_URL`: while you develop (`npm run dev`) requests go to `http://localhost:8080` (your backend). On the live site it is empty, so requests go to the same address that served the page.
2. `request()` sends the request. If the reply is an error, it reads the backend's `detail` message and shows **that**, so you see the real reason.
3. Then one function per backend address:

| Function | Calls |
|---|---|
| `uploadDocument(s)` | `POST /api/rag/upload` |
| `askQuestion` | `POST /api/rag/ask` |
| `triggerGcsIngestion` | `POST /api/rag/ingest-gcs` |
| `runAudit` | `POST /api/agent/audit` |
| `getSystemStatus` | `GET /api/status` |
| `healthCheck`, `listUploads` | `GET /api/health`, `GET /api/rag/uploads` |

**Try:** in your browser press **F12 → Network**, click a button in the app, and click the request to see what was sent and received.

### `frontend/src/pages/Index.tsx` — the page

The layout: a sidebar with four tabs and the area that shows the chosen tab. A variable remembers which tab is open (it starts on **Index Documents**).

| Tab (label) | Component |
|---|---|
| RAG Q&A | `RagQATab` |
| Procurement Audit | `AuditTab` |
| Index Documents | `DocumentUploadTab` |
| System Status | `SystemStatusTab` |

### The four screens (`frontend/src/components/`)

| File | What the screen does |
|---|---|
| `DocumentUploadTab.tsx` | Two ways to add documents. **Local:** choose or drag PDFs (only `.pdf` is accepted), upload them, and see each file's result (done, skipped, error). **Cloud Storage:** a button that indexes PDFs already in your bucket |
| `RagQATab.tsx` | A question box, a choice of search type (Normal, Contextual Compression, Multi-Query) and a history of answers. History lives in the page only, so it clears when you refresh |
| `AuditTab.tsx` | A text box (pre-filled with an example request), a **Run** button, four progress steps, and the three reports plus the memo. You can copy the memo |
| `SystemStatusTab.tsx` | Shows the backend's `/api/status` and refreshes every 5 seconds |

> **Good to know: the audit progress is a show, not real progress.** The backend returns *one* answer at the very end. To keep you company, `AuditTab.tsx` moves the four steps forward on **timers** (after 3, 6 and 9 seconds) no matter what the backend is doing. When the real answer arrives, all steps turn green. A real progress bar would need the backend to stream updates. That is a good improvement to try later.

---

## 2. Files that make the frontend work (rarely edited)

| File | Purpose |
|---|---|
| `index.html` | The single HTML page. React fills in `<div id="root">` |
| `src/main.tsx` | Starts React and places `App` on the page |
| `src/App.tsx` | Sets up shared helpers and page routing: `/` shows `Index`, anything else `NotFound` |
| `src/pages/NotFound.tsx` | The "page not found" screen |
| `src/components/NavLink.tsx` | A small link helper |
| `src/components/ui/` | About 49 generated building blocks (buttons, cards, tabs…) from shadcn/ui. **Don't edit by hand** |
| `src/hooks/` | Small reusable helpers (`use-toast`, `use-mobile`) |
| `src/lib/utils.ts` | `cn()`, which joins CSS class names |
| `src/index.css`, `src/App.css` | Global styles and colours |
| `src/vite-env.d.ts` | Type notes for Vite |

## 3. Tooling and settings files

| File | Purpose |
|---|---|
| `package.json` | The frontend's shopping list and its commands: `npm run dev`, `build`, `lint`, `test` |
| `package-lock.json` | The exact versions installed. Docker uses it |
| `bun.lock` | A second lock file from another tool (Bun). **Not used** by this project's build; npm is the supported tool |
| `vite.config.ts` | The development server runs on **port 3000**; sets the `@` shortcut for `src/` |
| `tsconfig*.json` | TypeScript rules |
| `tailwind.config.ts`, `postcss.config.js` | Styling system settings |
| `components.json` | Settings for the shadcn/ui generator |
| `eslint.config.js` | Code-style checks (`npm run lint`) |
| `vitest.config.ts`, `src/test/` | Frontend test setup. The only test is a placeholder |
| `playwright.config.ts`, `playwright-fixture.ts` | Browser-automation test setup. Not used here |

## 4. Run and build

```bash
cd frontend
npm install        # download packages (once)
npm run dev        # development server: http://localhost:3000
npm run build      # makes frontend/dist, the website that Docker packs into the box
```

## 5. How the screen and the backend meet

```
 click "Ask" in RagQATab.tsx
   → askQuestion() in lib/api.ts
     → POST http://localhost:8080/api/rag/ask   {"query": "...", "retriever_type": "similarity"}
       → backend/api/endpoints.py  rag_query()
     ← {"answer": "..."}
   → the answer appears in the history list
```

**Next:** [07 · Root and config files](07-root-and-config-files.md).
