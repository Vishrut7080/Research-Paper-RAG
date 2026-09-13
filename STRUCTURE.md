# STRUCTURE.md — What Each File Does

A file-by-file guide to the repository. Start with [README.md](README.md) for the big picture, then come here to understand what each file is responsible for.

---

## Repository Tree

```
Capstone Project/
├── README.md
├── STRUCTURE.md                    ← this file
├── TODO.md                         ← out-of-scope / future work
├── Logs.md
├── rag.ipynb
├── main.py
├── backend/                        ← FastAPI server + RAG modules + SQLite
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── init_db.py
│   ├── rag/                        ← ported notebook logic
│   └── data/                       ← runtime DB / uploads (gitignored)
├── frontend/                       ← React + Vite + Tailwind web app
│   └── src/
│       ├── App.jsx
│       ├── api.js
│       └── components/
├── research_papers/
│   └── 7 PDF research papers       ← the query corpus
├── reference/
│   ├── Lab6_Instructions.pdf
│   └── Lab6_Own_Project_Guidelines.pdf
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── .python-version
├── .env                            ← API keys (gitignored) — NEVER commit
├── .env.example                    ← template for .env
└── .gitignore
```

---

## Root Files

### `README.md`
Project overview: what ResearchMate does, the RAG pipeline, tech stack, how to run it, status, and a tour of the repo. **Start here.**

### `STRUCTURE.md`
This file. Detailed purpose of every file.

### `TODO.md`
Out-of-scope items captured during development (topic suggestions, export chat, dark mode, evaluation harness, deployment hardening). Each maps to a checklist from the plan; nothing here blocks the current core.

### `Logs.md`
Development progress log (author: Vishrut, created 9 Sep 2026).
- Project name: **MyRAG**, status: **In Progress**
- Roadmap checklist: local system is done; web dev, spec, features, QA, deploy are pending
- Issues log: **chunking** — chunk size had to be cut from 150 to 50 words to run locally and while print-debugging chunks

### `rag.ipynb`
**The heart of the project** — the entire working RAG implementation as a Jupyter notebook. Do most of your work here.

| Cell(s) | Section | What it defines / does |
| :--- | :--- | :--- |
| 1 | Setup | Imports: `numpy`, `os`, `json`, **`requests`**, `SentenceTransformer`, `PdfReader`, `TfidfVectorizer` |
| 2 | Model | Loads `embedder = SentenceTransformer('all-MiniLM-L6-v2')` |
| 5 | Load | `load_corpus(path='research_papers')` — extracts text from every `.pdf`/`.txt` into `{id, title, text}` |
| 6 | Load | Builds `corpus = load_corpus()` |
| 11 | Chunking | `chunk_text(text, chunk_size=300, overlap=30)` — word-based chunks with overlap |
| 13 | Chunking | Builds `chunk_records` = list of `{chunk_id, doc_id, doc_title, text}` and prints the chunk count |
| 14 | Embedding | `embed_texts(texts)` — encodes + L2-normalizes; guards against zero-norm |
| 15 | Embedding | Builds `chunk_matrix = embed_texts(all chunk texts)` — the searchable store |
| 16 | Retrieval | `retrieve(query, k=3)` — cosine similarity against `chunk_matrix`, returns top-k with `score` |
| 17 | Prompt | `SYSTEM_PROMPT` — "answer only from context, say so if absent, cite sources, 2–3 line summary" |
| 18 | LLM client | Loads `.env`, creates `Groq` client with `GROQ_API_KEY` / `GROQ_MODEL` |
| 19 | Web fallback | `WEB_SEARCH_THRESHOLD=0.40` + `search_web(query, max_results=5)` — Tavily API call, returns `[{title, url, content}]`, `[]` if no key |
| 20 | Generation | `ask(query, k=3)` — retrieves, runs web search if top score < threshold, calls Groq, returns `(answer, retrieved, web_results, web_search_used)` |
| 21 | Demo | `ask('What is Machine Learning?')` — end-to-end example that also prints web results when used |

### `main.py`
**Placeholder stub** — a `main()` that just prints "Hello from capstone-project!". Not part of the RAG flow; kept around for scaffolding. Replace or delete when a real entry point exists.

### `pyproject.toml`
Python project metadata and dependencies:
- `fastapi` + `uvicorn` — backend server (`backend/main.py`)
- `fonttools` — fixes pypdf CFF/Type1 font warnings and improves LaTeX math-symbol extraction
- `groq` — LLM API client for generation
- `numpy` — embedding matrix + cosine similarity
- `pypdf` — PDF text extraction
- `python-dotenv` — reads `.env`
- `python-multipart` — file-upload parsing for `/upload`
- `requests` — Tavily web-search API calls
- `scikit-learn` — TF-IDF utility (available, currently unused in the pipeline)
- `sentence-transformers` — `all-MiniLM-L6-v2` embeddings
- `sqlalchemy` — SQLite ORM (chat history / document registry)

### `requirements.txt`
The same dependency list in pip format, for `pip install -r requirements.txt` users.

### `uv.lock`
Lockfile pinning exact dependency versions for reproducible installs (`uv sync`).

### `.python-version`
Pins the project to Python `3.12`.

### `.env`
Credential/environment variables used by the notebook and backend:
- `GROQ_API_KEY` — Groq API key
- `GROQ_MODEL` — Groq chat model id
- `TAVILY_API_KEY` — optional; enables the web-search fallback
- `RESEARCH_CORPUS` — optional; overrides the corpus folder
**Gitignored — never commit this file.**

### `.env.example`
Template for `.env` with each variable documented. Safe to commit.

### `.gitignore`
Ignores Python caches/builds, the virtual env (`.venv`), `*.pdf`, `.env`, `node_modules/`, `frontend/dist`, `backend/data/`, `*.db` and `*.npy`.

---

## Directories

### `research_papers/` — the query corpus
Seven PDFs covering optimization and machine-learning methods. Each file name becomes the document `id` (extension stripped) and `title` (with extension):

1. `A Systematic Review of the Whale Optimization Algorithm - Theoretical Foundation, Improvements, and Hybridizations.pdf`
2. `A survey on multi-objective hyperparameter optimization algorithms for machine learning.pdf`
3. `Application of machine learning, deep learning and optimization.pdf`
4. `On Hyperparameter Optimization of Machine Learning Methods Using a Bayesian Optimization Algorithm to Predict Work Travel Mode Choice.pdf`
5. `Puma optimizer - a novel metaheuristic optimization algorithm and its application in machine learning.pdf`
6. `Review Of Feature Selection Methods Using Optimization Algorithm.pdf`
7. `Segmenting and classifying skin lesions using a.pdf`

Add more PDFs here to grow the corpus — `load_corpus()` picks them up automatically.

### `reference/`
Course material, for reference only (not read by any code):
- `Lab6_Instructions.pdf` — Lab 6 task instructions
- `Lab6_Own_Project_Guidelines.pdf` — project guidelines

---

## Backend (`backend/`) — FastAPI server + RAG modules

Port of the notebook logic into importable modules, plus a server, a database, and web search.

### `backend/main.py`
FastAPI app with CORS. Endpoints:
- `GET /health` — status + indexed chunk count (triggers the one-time corpus seed on first call)
- `POST /upload` — saves a PDF to `data/uploads/<sanitized-filename>`, extracts/chunks/embeds, inserts `Chunk` + `Document` rows (source=`upload`), refreshes the in-memory index, returns `{status, filename, chunks}`
- `POST /query` — accepts `{query_text}`, retrieves top-k, triggers Tavily web search if the top score < `WEB_SEARCH_THRESHOLD`, calls Groq, saves a `Chat` row, returns `{query, answer, sources, web_results, web_search_used}`
- `GET /history` — last 50 chats, newest first
- `GET /documents` — all documents with `source` (`corpus`/`upload`), `local_path`, and chunk counts
- `GET /documents/{id}/file` — streams the original PDF from disk (`FileResponse`)

### `backend/config.py`
Constants (chunk size/overlap = 300/30, `RETRIEVAL_K=5`, `WEB_SEARCH_THRESHOLD=0.40`, embedding model, `EMBEDDING_DIM=384`, max tokens, system prompt) and paths (`data/`, `uploads/`, `research.db`, corpus dir). Creates the `data/` dirs on import.

### `backend/models.py`
SQLAlchemy schema + engine:
- `Chat` — query, answer, `sources` JSON, `web_results` JSON, `web_search_used`, timestamp
- `Document` — filename, `source` (`corpus`/`upload`), `local_path`, num_chunks, uploaded_at
- `Chunk` — `chunk_id` (unique), doc_id, doc_title, text, `source_type`, position, embedding (`LargeBinary`, 1536 bytes for 384 floats)

### `backend/init_db.py`
Creates `backend/data/research.db` (`Base.metadata.create_all`). Run: `uv run python backend/init_db.py`.

### `backend/rag/pdf_processor.py`
- `extract_text_from_pdf(path)` / `extract_text_from_pdf_bytes(data)` — pypdf text extraction
- `chunk_text(text, chunk_size, overlap)` — ported from notebook cell 11
- `chunk_document(doc_id, doc_title, text)` — chunks one doc into records with a `source_type` field

### `backend/rag/embeddings.py`
- Lazy singleton `SentenceTransformer('all-MiniLM-L6-v2')`
- `get_embeddings(texts)` — encode + L2-normalize (same as notebook `embed_texts`)

### `backend/rag/retriever.py`
SQLite-backed index (replaces the old `chunks.json` + `matrix.npy` cache):
- `build_index()` — seeds `research_papers/` into the DB once (if empty), then loads all chunks + embeddings from SQLite into the in-memory matrix
- `add_uploaded_pdf(filename, pdf_bytes, local_path)` — chunks/embeds an upload, upserts its `Chunk` + `Document` rows, refreshes the index, returns chunk count
- `retrieve(query, k)` — cosine similarity against the DB-loaded matrix, returns top-k with scores

### `backend/rag/generator.py`
`generate_answer(query, context)` — Groq call with the strict system prompt. Reads `GROQ_API_KEY`/`GROQ_MODEL` from `.env`.

### `backend/rag/web_search.py`
`search_web(query, max_results=5)` — Tavily API call; `[]` if `TAVILY_API_KEY` missing or the request fails.

### `backend/data/` (gitignored)
Runtime state: `research.db` (chunks, embeddings, documents, chat history — the source of truth for the index) and `uploads/` (user PDFs).

---

## Frontend (`frontend/`) — React + Vite + Tailwind

### `frontend/package.json`
Deps: `react`, `react-dom`, `axios`. Dev deps: `vite`, `@vitejs/plugin-react`, `tailwindcss`, `postcss`, `autoprefixer`.

### `frontend/vite.config.js`
Dev server on port 5173; proxies `/api/*` → `http://localhost:8000` (so `VITE_API_URL` is optional in dev).

### `frontend/tailwind.config.js` + `postcss.config.js`
Tailwind v3 setup with a `primary` blue palette and JSX content paths.

### `frontend/src/api.js`
Axios client, base URL = `VITE_API_URL` or `/api`. Wraps `upload`, `query`, `history`, `documents`, plus `documentFileUrl(id)` for PDF downloads.

### `frontend/src/App.jsx`
Layout: left sidebar (title + backend status, `DocumentUpload`, `DocumentsList`, `History`), right main area with `ChatInterface`. Polls `/health` on load.

### `frontend/src/components/DocumentUpload.jsx`
File picker (`.pdf`) → `POST /upload` → shows chunk count or error.

### `frontend/src/components/DocumentsList.jsx`
Sidebar list of all documents from `GET /documents` with a `corpus`/`upload` badge, chunk count + date, and a "Download" link to `/documents/{id}/file`; refresh button.

### `frontend/src/components/ChatInterface.jsx`
Message list, query input, submit → `POST /query`; loads prior history on mount; auto-scrolls; renders `SourcePanel` under assistant messages.

### `frontend/src/components/SourcePanel.jsx`
Renders retrieved `[Paper]` chunks (title + score + preview) and `[Web]` results (title link + preview); shows an amber banner when web search was used.

### `frontend/src/components/History.jsx`
Sidebar list of past queries from `GET /history` with timestamp + "web" tag; local filter box; refresh button.

### `frontend/.env.example`
`VITE_API_URL=http://localhost:8000` — only needed if not using the Vite `/api` proxy.

---

## How to Navigate

1. **What is this project?** → `README.md`
2. **Where is the (notebook) code?** → `rag.ipynb` (cells mapped above)
3. **Where is the server code?** → `backend/` (FastAPI) + `backend/rag/` (ported RAG)
4. **Where is the web UI?** → `frontend/`
5. **What's done, what's next?** → `Logs.md` (progress) and `TODO.md` (future work)
6. **Where does the data come from?** → `research_papers/` + uploaded PDFs in `backend/data/uploads`
7. **Where are the API keys?** → `.env` (gitignored; template in `.env.example`)
8. **What are the dependencies?** → `pyproject.toml` / `uv.lock` / `frontend/package.json`