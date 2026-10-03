# 01 · The case: what problem are we solving?

Before looking at any code, it helps to know **why this app exists**. Good software starts with a real problem. This page tells that story.

> Aldermoor Industries, its people and its documents are **made up** for this project.

---

## 1. The story

**Aldermoor Industries** is a (pretend) company in Hamburg, Germany. It builds machines that fill and pack bottles and boxes. To build them it buys parts from suppliers around the world: motors, controllers, sensors, steel.

Every purchase must be checked **before** the company pays. The checks come from different departments:

| Department | Question it must answer |
|---|---|
| **Compliance / Risk** | Is this supplier allowed? (Is it on a sanctions list?) Can it be trusted to deliver and survive financially? |
| **Tax / Treasury** | How much tax and import duty will we pay? Is the exchange rate in the supplier's quote sensible? |
| **Finance / Control** | Is this a lasting asset or a running cost? Who has the authority to approve this amount? |
| **The CFO** (finance boss) | Taking all of that together: do we pay, hold, or reject? |

## 2. What goes wrong today

| Problem | Example |
|---|---|
| **It is slow.** Each department checks in turn, and the request waits in someone's inbox | A 480,000 EUR order waits days for three sign-offs |
| **The rules are hidden in documents.** Payment terms, approval limits and tax rules live in long PDFs | "What are our payment terms for servo-motor suppliers?" means finding the right page in the right PDF |
| **People apply the rules differently** | Two buyers get two different answers to the same question |
| **There is no clear written record** of how a decision was reached | An auditor asks "why did you approve this?" and nobody remembers |

## 3. The idea

Build one app with **two helpers**:

1. **A document helper.** Upload the company's policy PDFs once. Anyone can then ask a question in plain English and get an answer taken from those documents.
2. **An audit helper.** Paste a purchase request. Three AI "specialists", one for each department above, check it and write a short report. A final "CFO" step reads all three and writes **one memo with a decision**.

The people still make the final call. The app **prepares** the answer quickly and consistently, and writes it down.

## 4. Who uses it, and how

| Person | What they do in the app |
|---|---|
| **Buyer** | Pastes a purchase request into the **Procurement Audit** tab and reads the memo |
| **Policy owner / admin** | Uploads policy PDFs in the **Index Documents** tab |
| **Anyone** | Asks "what does our policy say about …?" in the **RAG Q&A** tab |
| **Developer / IT** | Watches the **System Status** tab and the logs |

### A day in the life

1. **Morning.** The admin uploads four PDFs: the annual report, the procurement policy, a customs tariff excerpt and the accounting policy. The app reads them and remembers their *meaning*.
2. **10:00.** A buyer wonders about payment terms and asks: *"What are the standard payment terms for servo motor suppliers?"* Answer in seconds: **Net-45** (for suppliers with a credit score of 75 or higher).
3. **11:00.** The same buyer pastes a purchase request for 200 PLC controllers (480,000 EUR) from a supplier in the Netherlands, made in Japan. The app runs the audit and returns three short reports and a memo.
4. **11:05.** The memo says the supplier is unknown, so risk is high, and recommends conditions before payment. The buyer sends it up for sign-off, with a clear written trail.

## 5. Four scenarios you can try

These all work with the sample documents in `sample_docs/`.

### Scenario A · A policy question (document helper)

- **Ask:** *What is Aldermoor Industries total revenue in FY2024?*
- **Expect:** about **EUR 2.84 billion**.
- **Also try:** payment terms for servo motor suppliers (**Net-45**), customs duty on PLC controllers from Japan (**2.2 %**), depreciation of filling-line equipment (**10 years, straight line**).
- **Why it matters:** the answer comes from *your* documents, not from the AI's memory.

### Scenario B · A question that is not in the documents

- **Ask:** *Who won the 2018 World Cup?*
- **Expect:** the app says it **does not know**.
- **Why it matters:** the helper is told to answer *only* from the documents. Saying "I don't know" is better than inventing an answer.

### Scenario C · A normal audit

- **Submit:** 200 PLC controllers, 480,000 EUR, supplier *Takumi Controls Europe B.V.*, from Japan to Germany, FX rate `1 EUR = 163.5 JPY`.
- **Expect (wording varies each time):**
  - **Risk:** the supplier is fictional and unknown, so the credit check gives a low score and the report is cautious.
  - **Tax:** import VAT of about 19 % plus customs duty, and the total landed cost.
  - **Control:** a capital purchase (an asset), and the amount is over EUR 250,000, so it needs a Department Head's sign-off. Above EUR 1,000,000 it would need the CFO and the Management Board.
  - **CFO memo:** a decision with reasons and next actions.

### Scenario D · A suspicious exchange rate

- **Submit the same request** but with `1 EUR = 190 JPY`.
- **Expect:** the tax report flags **FX ALERT** because the quoted rate is more than 5 % away from the market rate. The CFO rules then force the decision **CONDITIONAL HOLD**.
- **Why it matters:** this shows that the final decision follows **written rules**, not mood. A report containing `RED ALERT` forces **REJECTED**; `FX ALERT` or `HOLD FOR TREASURY AUDIT` forces **CONDITIONAL HOLD**; only clean reports give **APPROVED TO PAY**.

## 6. What the app does *not* do (be honest about limits)

| Limit | Why it matters |
|---|---|
| The audit "checks" come from the AI's **general knowledge**, not from real sanctions, credit or tax databases. Only the exchange-rate check uses live data | A real company must connect real data sources |
| AI answers can be wrong, and the wording changes between runs | A person must review important decisions |
| There is no sign-in | Anyone with the web address can use it. Never put private documents in a public demo |
| Upload history is kept in memory and disappears on restart | A real system would use a database |
| Only text-based PDFs work. Scanned images have no text to read | Scanned documents need text recognition (OCR) first |

## 7. From the need to the technology

Every part of the app exists to serve a need in the story:

| The need | The part that serves it | Plain-English reason |
|---|---|---|
| "Let people use it from a browser" | **React** web page | A screen with tabs and buttons |
| "Connect the screen to the logic" | **FastAPI** | The waiter between the dining room and the kitchen |
| "Answer from our documents" | **RAG**: chunks, embeddings, **Vector Search** | Find the right pages by *meaning*, then answer from them |
| "Write the answers in good English" | **Gemini** | The chef that writes the answer |
| "Check a purchase from several angles" | **Agents** with **tools** and **prompts** | Specialists with job descriptions and instruments |
| "Make the decision follow rules" | The CFO prompt and the keywords | Written decision rules |
| "Keep the key and passwords safe" | **Secret Manager**, `.env` | A safe, and a private notes file |
| "Let other people use it" | **Docker**, **Cloud Run** | Pack it in a box and run it on the internet |
| "Update it without manual work" | **GitHub Actions** | A delivery robot |
| "Find out what went wrong" | **Logging** | The app's diary |

## 8. Where this shows up in the code

| Part of the case | Folder |
|---|---|
| The document helper | `backend/rag/` |
| The audit helper | `backend/agent/` |
| The screens | `frontend/` |
| The waiter between them | `backend/api/` |
| The sample documents | `sample_docs/` |

**Next:** [02 · The big picture](02-the-big-picture.md).
