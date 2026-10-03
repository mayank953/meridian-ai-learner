# 11 · Document Q&A (RAG) explained

**RAG** = *Retrieval-Augmented Generation*. In plain words: **look up the right pages first, then answer from them.** Like an open-book exam.

---

## 1. Why not just ask the AI?

An AI model only knows what it saw during training. It has never read **your** documents. If you ask about your company's payment terms, it may guess, and sound confident while being wrong (a *hallucination*).

RAG fixes this:

```
Without RAG:  question ───────────────────────────► AI ─► guess
With RAG:     question ─► find the right pages ─┐
                                                ├─► AI ─► answer based on those pages
                          your documents ───────┘
```

## 2. Two stages

```
STAGE 1: getting documents in (once per document)
   PDF → pages → small pieces → numbers (embeddings) → stored in the vector database

STAGE 2: asking (every question)
   question → numbers → find closest stored pieces → prompt (pieces + question) → Gemini → answer
```

## 3. The words

| Word | Plain meaning | Analogy |
|---|---|---|
| **Chunk** | A small piece of a document (about 1000 characters) | An index card |
| **Overlap** | Neighbouring chunks share 100 characters | Each card repeats the end of the last one, so an idea on the edge isn't cut |
| **Embedding** | A list of 768 numbers that captures the *meaning* of a text | GPS coordinates for an idea |
| **Vector database** | Finds the stored items whose numbers are closest to yours | A library catalogue organised by meaning |
| **Index** | The stored data inside Vertex AI Vector Search | The catalogue itself |
| **Endpoint** | The running service that searches the index. **Billed by the hour** | The reading room, open while you pay for it |
| **Retriever** | The LangChain part that returns the best chunks | The librarian |

## 4. Why numbers?

Computers can't compare *meaning*, but they can compare numbers. Texts with similar meaning get similar numbers. Here is the idea with three numbers instead of 768:

```
"Servo motors are paid on Net-45 terms"        → [0.9, 0.1, 0.0]
"Filling line equipment is depreciated 10 yrs" → [0.1, 0.9, 0.1]
Question "When do we pay servo motor suppliers?" → [0.8, 0.2, 0.1]   ← closest to the first one
```

Run `python docs/examples/05_similarity_demo.py` to see the maths.

## 5. The files

| File | Job |
|---|---|
| `rag/llm.py` | The Gemini chat model |
| `rag/embeddings.py` | Text → 768 numbers |
| `rag/vector_store.py` | The database connection |
| `rag/data_ingestion.py` | Stage 1: documents in |
| `rag/retrieval.py` | Stage 2: answers out |

### Stage 1 in code (`data_ingestion.py`)

```python
def ingest_pdf(local_path, source):
    pages = PyPDFLoader(local_path).load()           # 1. read the PDF
    for page in pages:
        page.metadata["source"] = source              # 2. remember where it came from
    chunks = split_into_chunks(pages)                 # 3. cut into pieces
    if chunks:
        get_vector_store().add_documents(chunks)      # 4. make numbers and store them
    return {"pages": len(pages), "chunks": len(chunks)}
```

PDFs that are only pictures of text have no text to read; the upload route reports them as skipped.

### Stage 2 in code (`retrieval.py`)

```python
question_answer_chain = create_stuff_documents_chain(get_llm(), prompt)
rag_chain = create_retrieval_chain(build_retriever(retriever_type), question_answer_chain)
return rag_chain.invoke({"input": query})["answer"]
```

Two chains: the first *stuffs* the found chunks into the prompt and calls Gemini; the second runs the search first, then the first chain.

The prompt tells the AI:

```
Use the following pieces of retrieved context to answer the question.
If you don't know the answer based on the context, say that you don't know.
```

That is why a question not covered by your documents gets "I don't know".

## 6. Three ways to search

| Choice in the screen | `retriever_type` | What it does | Trade-off |
|---|---|---|---|
| Normal | `similarity` | The 3 closest chunks | Fastest |
| Multi-Query | `multiquery` | The AI rewrites your question several ways, merges results | Finds more, slower |
| Contextual Compression | `contextual` | Gets 10 chunks, then the AI trims each to the useful sentences | Cleanest, slowest |

## 7. Choices to understand

| Choice | Why |
|---|---|
| **Chunks of 1000 characters** | Big enough for a full idea, small enough for a precise match. Too small loses context; too big blurs the match |
| **Overlap of 100** | Ideas that straddle a boundary survive |
| **768 numbers** | The database was created for 768. The model must match |
| **Same model for storing and searching** | Numbers from different models can't be compared |
| **3 chunks (`k=3`)** | Enough context without a long, costly prompt |
| **Streaming updates** | New uploads become searchable in a short time |
| **A copy of each PDF in Cloud Storage** | The database holds chunks, not originals; a copy lets you re-index later |

## 8. Packages: new and classic

`create_retrieval_chain` and the retrievers come from **`langchain_classic`**; the agents use the newer **`langchain`**. Both are in `requirements.txt`. Online examples mix old and new names, so check which package an import comes from.

## 9. Try it

1. `python docs/examples/03_chunking_demo.py`: change `CHUNK_SIZE` and `CHUNK_OVERLAP`, run again.
2. Change `CHUNK_SIZE` in `data_ingestion.py` to 300, upload a PDF again, ask the same question.
3. Ask the same question with each of the three search types. Compare speed and answer.
4. Ask something that isn't in the documents.
