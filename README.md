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

## Getting Started

### 1. Environment + API keys

```bash
cp .env.example .env   # then fill in GROQ_API_KEY, GROQ_MODEL, TAVILY_API_KEY
uv sync
```

### 2a. Notebook (research/prototyping)

Open `rag.ipynb`, run cells top to bottom, then:

```python
answer, sources, web_results, web_search_used = ask("What is Machine Learning?")
print(answer)
for s in sources:
    print(f"[{s['score']:.3f}] {s['doc_title']}")
if web_search_used:
    for r in web_results:
        print(f"- {r['title']}\n  {r['url']}")
```

### 2b. Full stack (server + web app)

Terminal 1 — backend:

```bash
uv run python backend/init_db.py        # create backend/data/research.db
uv run uvicorn backend.main:app --reload --port 8000
# first /health or /query seeds research_papers/ into the DB (chunks + embeddings)
# API docs: http://localhost:8000/docs
```

Terminal 2 — frontend:

```bash
cd frontend
npm install
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

## Status & Known Issues

- **Status**: In progress (`Logs.md`, 9 Sep 2026)
- **Working**: Local retrieval + generation with sources and similarity scores; web-search fallback; FastAPI backend; React UI; chat history in SQLite
- **Learned**: Chunk size of 150 was too large for the local notebook run and print-debugging; reduced to 50 during development. The current default in `chunk_text` is 300 — tune per hardware.
- **Not yet done** (see `TODO.md`): topic suggestions, export, dark mode, evaluation harness, deployment.

---

## Repository Tour

```
Capstone Project/
├── README.md              ← you are here (project overview)
├── STRUCTURE.md           ← what every file does, in detail
├── TODO.md                ← out-of-scope / future work
├── Logs.md                ← progress log & lessons learned
├── rag.ipynb              ← the RAG implementation (web search included)
├── main.py                ← placeholder stub (not part of the RAG flow)
├── backend/               ← FastAPI server + RAG modules + SQLite (SQLAlchemy)
├── frontend/              ← React + Vite + Tailwind web app
├── research_papers/       ← PDF corpus (data you query over)
├── reference/             ← Lab6 instructions & guidelines PDFs
├── pyproject.toml         ← project metadata + dependencies
├── requirements.txt       ← pip-formatted dependency list
├── uv.lock                ← locked dependency versions
├── .python-version        ← Python 3.12
├── .env                   ← API keys (GITIGNORED, do not commit)
└── .gitignore             ← ignores .venv, PDFs, .env, DBs, node_modules
```

See [STRUCTURE.md](STRUCTURE.md) for a full file-by-file breakdown.

---

## Disclaimer

`.env` contains your `GROQ_API_KEY` (and optionally `TAVILY_API_KEY`) and is intentionally gitignored. Never commit it. Runtime data (`backend/data/`) and `node_modules/` are also gitignored — a fresh clone needs `uv sync` + `npm install`.