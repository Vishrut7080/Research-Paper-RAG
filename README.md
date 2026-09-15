# ResearchMate — RAG System for Research Papers

ResearchMate is a Retrieval-Augmented Generation (RAG) system that answers questions about a local corpus of research papers. You load a set of PDFs, ask a question in plain English, and the system retrieves the most relevant passages from those papers and generates a grounded answer with source citations.

When the corpus doesn't cover a question (low retrieval confidence), ResearchMate **falls back to web search** (Tavily) and augments the answer with web results — clearly labelled. Everything runs locally except the Groq LLM call and the optional web search.

---

## How It Works

```
research_papers/*.pdf  (or upload a PDF via the UI)
        │
        ▼
    1. Extract text        ── pypdf (PdfReader)
        │
        ▼
    2. Chunk the text      ── word-based chunks (configurable size + overlap)
        │
        ▼
3. Embed chunks        ── sentence-transformers (all-MiniLM-L6-v2, 384-dim)
        │
        ▼
     4. Persist + index      ── chunks & embeddings stored in SQLite (research.db),
        │                     loaded into a normalized in-memory matrix on startup
        ▼
   user query ──────────────► 5. Retrieve top-k  ── cosine similarity (query ⊗ chunk_matrix)
        │
        ▼
    6. Confidence check    ── if top score < threshold, add Tavily web results
        │
        ▼
    7. Generate answer     ── Groq LLM, given papers (+ web) context + system prompt
        │
        ▼
   answer + sources ([Paper: file] and/or [Web: title] with scores)
```

### The Pipeline (implemented in `rag.ipynb`)

| Step | Function | Details |
| :--- | :--- | :--- |
| Load | `load_corpus()` | Reads every `*.pdf` (or `.txt`) in `research_papers/` with `pypdf`, keeps `id`/`title`/`text` |
| Chunk | `chunk_text()` | Splits text by words, default `chunk_size=300`, `overlap=30` |
| Embed | `embed_texts()` | Encodes text with `all-MiniLM-L6-v2`, then L2-normalizes to enable cosine similarity via matrix multiply |
| Index | `chunk_records` + `chunk_matrix` | Each chunk is a dict (chunk_id, doc_id, doc_title, text); embeddings live in a NumPy matrix. In `backend/` the chunks + embeddings are **persisted in SQLite** (`chunks` table) and rebuilt into the matrix on server start — no `npy`/`json` cache files |
| Retrieve | `retrieve(query, k)` | Embeds the query, computes `chunk_matrix @ query_vec`, returns top-k chunks with scores |
| Web fallback | `search_web(query)` | If the best retrieval score < `WEB_SEARCH_THRESHOLD` (0.40), calls the Tavily API and appends `[Web: title]` results to the context |
| Generate | `ask(query, k)` | Calls Groq with a strict "answer only from context / say so if absent / cite sources / 2–3 line summary" system prompt |

The **same logic is ported to `backend/`** so the FastAPI server behaves identically to the notebook.

---

## Tech Stack

| Component | Technology |
| :--- | :--- |
| Language | Python 3.12 (`.python-version`) |
| Environment | uv + `.venv`, `uv.lock` for reproducibility |
| PDF parsing | `pypdf` (+ `fonttools` for CFF/Type1 fonts) |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dims) |
| Retrieval | NumPy cosine similarity (no external vector DB) |
| Generation | Groq (`groq`) — model & key from `.env` |
| Web search | Tavily (`requests`) — `TAVILY_API_KEY` in `.env` |
| Server | FastAPI + Uvicorn (`backend/`) |
| Storage | SQLite via SQLAlchemy (`backend/data/research.db`) |
| Frontend | React + Vite + Tailwind (`frontend/`) |
| Utilities | `scikit-learn`, `python-dotenv` |

> The `backend/` + `frontend/` full-stack is now implemented. Claude and ChromaDB remain future options — see `TODO.md`.

---

## Getting Started (Clean Clone)

**Prerequisites:** Python 3.12, Node.js 18+, a [Groq API key](https://console.groq.com), and optionally a [Tavily API key](https://tavily.com) for web search fallback.

### 1. Clone + environment

```bash
git clone <repo-url> && cd "Capstone Project"
cp .env.example .env        # then fill in GROQ_API_KEY, GROQ_MODEL, and optionally TAVILY_API_KEY
uv sync                      # install Python deps (creates .venv)
```

> **API keys are required.** Without `GROQ_API_KEY`, the LLM generation step will fail. Without `TAVILY_API_KEY`, web search fallback is silently skipped (corpus-only mode).

### 2a. Notebook (research/prototyping)

```bash
uv run jupyter notebook rag.ipynb
```

Run cells top to bottom. The notebook builds the full RAG pipeline and ends with a demo query. If the Groq API returns a rate-limit error (HTTP 429), wait a minute and re-run the final cell — or use a smaller model by changing `GROQ_MODEL` in your `.env`.

### 2b. Full stack (server + web app)

**Terminal 1 — backend:**

```bash
uv run python backend/init_db.py        # create backend/data/research.db
uv run uvicorn backend.main:app --reload --port 8000
# first /health or /query seeds research_papers/ into the DB (chunks + embeddings)
# API docs: http://localhost:8000/docs
```

**Terminal 2 — frontend:**

```bash
cd frontend
npm install                             # install JS deps (node_modules is gitignored)
npm run dev                             # http://localhost:5173
```

Upload a PDF, ask a question, and answers appear with `[Paper]`/`[Web]` sources. Past queries show in the History sidebar.

### API endpoints

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `GET` | `/health` | Backend status + number of indexed chunks |
| `POST` | `/upload` | Upload a PDF: extract → chunk → embed → index |
| `POST` | `/query` | Ask a question (retrieval + optional web fallback + generation) |
| `GET` | `/history` | Last 50 chat entries |
| `GET` | `/documents` | All documents (`corpus`/`upload` source tag + chunk counts) |
| `GET` | `/documents/{id}/file` | Download the original PDF file |

---

## What Didn't Work

These are the approaches we tried and abandoned, or problems we hit during development:

| Attempt | What happened | Why we moved on |
| :--- | :--- | :--- |
| **Chunk size = 150 words** | Too large for print-debugging in the notebook; output was overwhelming and hard to inspect visually | Reduced to 50 during debug; final default is 300 (tune per use case) |
| **JSON + NumPy cache** (`chunks.json` + `matrix.npy`) | Corrupted when the backend crashed mid-write; no atomicity guarantee; stale index after adding PDFs | Replaced with SQLite-backed index — single source of truth, rebuilt from DB on every server start |
| **ChromaDB** | Considered as a vector store, but added a dependency that duplicated what NumPy + SQLite already did | Kept the lightweight in-memory cosine-similarity approach |
| **Claude API** | Initially planned as the LLM, but Groq was faster and had a generous free tier | Switched to Groq; Claude remains a future option in `TODO.md` |
| **Case-sensitive filename matching** | `fname.endswith("pdf")` misses `*.PDF` on case-sensitive file systems; unresolved minor bug | Logged in `Logs.md`; the current corpus is all lowercase so it works, but this is a real gap for user uploads |

## Limitations

- **Limited evaluation.** The notebook has **no formal baseline yet** — a TF-IDF vs. dense-vector **recall@3** comparison on hand-labeled queries is planned as part of the evaluation harness in `TODO.md`. Currently only qualitative spot-checking of retrieved chunks and generated answers has been done. There is also no scoring of *answer quality* (faithfulness/groundedness). A fuller evaluation harness is listed in `TODO.md`.
- **API key dependency.** The system requires a valid `GROQ_API_KEY` to generate answers. Without it, retrieval works but generation fails. Free-tier rate limits (e.g., 429 errors) can block the notebook's final cell.
- **No document-level deduplication.** If the same PDF is uploaded twice (via the UI or corpus seed), it gets indexed twice with different chunk IDs.
- **Single-process backend.** The FastAPI server runs a single worker; concurrent requests may be slow because embedding is CPU-bound.
- **Fixed embedding model.** `all-MiniLM-L6-v2` is fast but not the most accurate. Switching requires re-embedding the entire corpus.
- **PDF text extraction is imperfect.** `pypdf` cannot handle scanned PDFs, complex tables, or figures — only text-based PDFs.
- **No persistent vector index.** Embeddings are rebuilt from SQLite on every server startup. For large corpora this would be slow; currently acceptable at 435 chunks.

## Status

- **Working**: Local retrieval + generation with sources and similarity scores; web-search fallback; FastAPI backend; React UI; chat history in SQLite
- **In progress** (see `TODO.md`): fuller evaluation harness, topic suggestions, export, dark mode, deployment.

---

## Self-Evaluation Against the Project Rubric

**Q1 — Does it run end-to-end from a clean clone, not just on your machine?**
Yes, with caveats. `uv sync` + `npm install` reproduce the environment, and the 24 MB corpus is committed, so a fresh clone has all data. The full-stack path (`uv run uvicorn ...` + `npm run dev`) works without anything from this machine. Two non-reproducible bits are documented upfront: the notebook's last cell needs a live Groq API key (and free-tier 429 rate limits currently surface as a raw traceback in the saved output — a nicer error is planned), and the `backend/data/research.db` is gitignored so the first `/health` call re-seeds and re-embeds the corpus (takes a few minutes).

**Q2 — Is there an actual baseline in the notebook, not just a final number?**
Not yet. The notebook currently demonstrates the pipeline end-to-end with a single demo query but contains no baseline comparison. A **TF-IDF vs. `all-MiniLM-L6-v2`** retrieval baseline (recall@k on hand-labeled queries) is planned — see the evaluation harness in `TODO.md`.

**Q3 — Did you report what didn't work, not only what did?**
Yes. See the **What Didn't Work** table above (chunk-size debugging, the JSON+npy cache corruption, dropped ChromaDB/Claude plans, the case-sensitive filename bug) plus the **Limitations** list (no answer-quality scoring yet, no dedup, single-process backend, imperfect PDF extraction).

**Q4 — Is the generated answer itself evaluated, or just retrieval?**
Neither, formally. There is no numeric evaluation in the notebook yet — retrieval and generation have only been spot-checked qualitatively. A retrieval baseline (recall@k) and answer-grounding evaluation are planned, listed in `TODO.md`.

---

## Repository Tour

```
Capstone Project/
├── README.md              ← you are here (project overview)
├── STRUCTURE.md           ← what every file does, in detail
├── TODO.md                ← out-of-scope / future work
├── Logs.md                ← progress log & lessons learned
├── rag.ipynb              ← the RAG implementation (web search included)
├── backend/               ← FastAPI server + RAG modules + SQLite (SQLAlchemy)
├── frontend/              ← React + Vite + Tailwind web app
├── research_papers/       ← PDF corpus (data you query over)
├── reference/             ← Lab6 instructions & guidelines PDFs
├── pyproject.toml         ← project metadata + dependencies (uv-managed)
├── uv.lock                ← locked dependency versions
├── .python-version        ← Python 3.12
├── .env                   ← API keys (GITIGNORED, do not commit)
└── .gitignore             ← ignores .venv, PDFs, .env, DBs, node_modules
```

See [STRUCTURE.md](STRUCTURE.md) for a full file-by-file breakdown.

---

## Disclaimer

`.env` contains your `GROQ_API_KEY` (and optionally `TAVILY_API_KEY`) and is intentionally gitignored. Never commit it. Runtime data (`backend/data/`) and `node_modules/` are also gitignored — a fresh clone needs `uv sync` (Python) + `npm install` (frontend). API keys are **required** for the LLM and web-search steps.