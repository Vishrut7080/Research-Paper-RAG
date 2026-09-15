# STRUCTURE.md — What Each File Does

A file-by-file guide to the repository. Start with [README.md](README.md) for the big picture, then come here to understand what each file is responsible for.

---

*Video:* https://drive.google.com/file/d/1ZZD1ER29FbZ0U-ZU9osM8xffu_NxxSn1/view?usp=drive_link

---

## Repository Tree

```
Capstone Project/
├── README.md
├── STRUCTURE.md                    ← this file
├── TODO.md                         ← out-of-scope / future work
├── Logs.md
├── rag.ipynb
├── ResearchMate_Presentation.pptx  ← project slides
├── backend/                        ← FastAPI server + RAG modules + SQLite
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── init_db.py
│   ├── rag/                        ← ported notebook logic
│   │   ├── __init__.py
│   │   ├── pdf_processor.py
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   ├── generator.py
│   │   └── web_search.py
│   └── data/                       ← runtime DB / uploads (gitignored)
├── frontend/                       ← React + Vite + Tailwind web app
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx               ← React entry point
│       ├── App.jsx
│       ├── api.js
│       ├── index.css              ← Tailwind directives
│       └── components/
│           ├── Icons.jsx          ← inline SVG icons (PaperIcon, WebIcon)
│           └── ...
├── notebooks/
│   └── evaluation.ipynb           ← RAG vs plain-LLM evaluation
├── evaluation_results/            ← cached scores (JSON/CSV) + charts (PNG)
├── research_papers/
│   └── 8 PDFs                      ← the query corpus (gitignored)
├── pyproject.toml
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
- Project name: **ResearchMate**, status: **In Progress** — core RAG, web-search fallback, full-stack web dev, SQLite persistence, and evaluation are done; QA and deployment are pending
- Roadmap checklist: local system, web dev, and evaluation are done; deferred features, QA/testing, and deploy are pending
- Issues log: **chunking** (cut from 150 to 50 words while print-debugging, final default 300/30), **index caching**, **corpus seed filename check**, **system prompt formatting**

### `rag.ipynb`
**The heart of the project** — the entire working RAG implementation as a Jupyter notebook. Do most of your work here.

| Cell(s) | Section | What it defines / does |
| :--- | :--- | :--- |
| 1 | Setup | Imports: `numpy`, `os`, `json`, `requests`, `SentenceTransformer`, `PdfReader`, and `sklearn.feature_extraction.text.TfidfVectorizer` (imported but unused) |
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
| 21 | Demo | `answer, sources, web_results, web_search_used = ask('What is Machine Learning?')` — end-to-end example that also prints web results when used |

### `notebooks/evaluation.ipynb`
Quantitative comparison of the full RAG pipeline against a **plain zero-shot LLM baseline** (no retrieval). It reuses `backend.rag` + `backend.config` for retrieval, runs 15 queries (12 answerable from the corpus with an expected source, 3 out-of-corpus that trigger the Tavily fallback), and calls an **LLM-as-a-judge** to score both answers on a 1–5 rubric (correctness, groundedness, completeness, conciseness) with randomized A/B labels. Results are cached to `evaluation_results/evaluation_results.json` (set `REDO = True` to re-run) and summarized with `pandas` + `matplotlib` charts. Note: the saved results were produced against an earlier 9-PDF corpus that included an LLM survey and the RAG paper, so two questions now reference papers absent from `research_papers/`.

### `evaluation_results/`
Cached evaluation artefacts: `evaluation_results.json` + `.csv` (per-question scores, answers, latencies, token counts) and three PNG charts (`mean_scores_per_dimension.png`, `scores_per_question.png`, `latency_citations_overall.png`).

### `pyproject.toml`
Python project metadata and dependencies:
- `fastapi` + `uvicorn` — backend server (`backend/main.py`)
- `fonttools` — fixes pypdf CFF/Type1 font warnings and improves LaTeX math-symbol extraction
- `groq` — LLM API client for generation
- `matplotlib` — evaluation charts (`notebooks/evaluation.ipynb`)
- `numpy` — embedding matrix + cosine similarity
- `pandas` — evaluation result tables
- `pypdf` — PDF text extraction
- `python-dotenv` — reads `.env`
- `python-multipart` — file-upload parsing for `/upload`
- `requests` — Tavily web-search API calls
- `scikit-learn` — provides `TfidfVectorizer`; imported in `rag.ipynb` cell 1 but **not currently used** (the implemented baseline is a plain LLM, not TF-IDF)
- `sentence-transformers` — `all-MiniLM-L6-v2` embeddings
- `sqlalchemy` — SQLite ORM (chat history / document registry)

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
Eight PDFs at present. Each file name becomes the document `id` (extension stripped) and `title` (with extension):

1. `A Systematic Review of the Whale Optimization Algorithm - Theoretical Foundation, Improvements, and Hybridizations.pdf`
2. `A survey on multi-objective hyperparameter optimization algorithms for machine learning.pdf`
3. `Application of machine learning, deep learning and optimization.pdf`
4. `On Hyperparameter Optimization of Machine Learning Methods Using a Bayesian Optimization Algorithm to Predict Work Travel Mode Choice.pdf`
5. `Puma optimizer - a novel metaheuristic optimization algorithm and its application in machine learning.pdf`
6. `Review Of Feature Selection Methods Using Optimization Algorithm.pdf`
7. `Segmenting and classifying skin lesions using a.pdf`
8. `Nat Geo - Guide to Photography.pdf` — unrelated leftover; safe to remove (nothing references it)

Add more PDFs here to grow the corpus — `load_corpus()` picks them up automatically. **Note:** `*.pdf` is gitignored, so this folder is empty on a fresh clone until you add PDFs.

> A former `reference/` folder (Lab 6 instructions/guidelines PDFs) is no longer present in the repository.

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
Deps: `react`, `react-dom`, `axios`, `react-markdown`, `remark-gfm`. Dev deps: `vite`, `@vitejs/plugin-react`, `tailwindcss`, `@tailwindcss/typography`, `postcss`, `autoprefixer`.

### `frontend/package-lock.json`
npm lockfile pinning exact JS dependency versions (`npm install` uses it for reproducible installs).

### `frontend/vite.config.js`
Dev server on port 5173; proxies `/api/*` → `http://localhost:8000` (so `VITE_API_URL` is optional in dev).

### `frontend/tailwind.config.js` + `postcss.config.js`
Tailwind v3 setup with a `primary` blue palette and JSX content paths. The `@tailwindcss/typography` plugin is enabled so LLM Markdown answers render with `prose` styling.

### `frontend/src/main.jsx`
React entry point — mounts `<App />` into `#root` via `ReactDOM.createRoot` (wrapped in `StrictMode`).

### `frontend/src/api.js`
Axios client, base URL = `VITE_API_URL` or `/api`. Wraps `upload`, `query`, `history`, `documents`, plus `documentFileUrl(id)` for PDF downloads.

### `frontend/src/index.css`
Tailwind directives (`@tailwind base/components/utilities`).

### `frontend/src/App.jsx`
Layout: left sidebar (title + backend status, `DocumentUpload`, `DocumentsList`, `History`), right main area with `ChatInterface`. Polls `/health` on load.

### `frontend/src/components/DocumentUpload.jsx`
File picker (`.pdf`) → `POST /upload` → shows chunk count or error.

### `frontend/src/components/DocumentsList.jsx`
Sidebar list of all documents from `GET /documents` with a `corpus`/`upload` badge, chunk count + date, and a "Download" link to `/documents/{id}/file`; refresh button.

### `frontend/src/components/ChatInterface.jsx`
Message list, query input, submit → `POST /query`; loads prior history on mount; auto-scrolls; renders assistant answers as GFM Markdown (`react-markdown` + `remark-gfm`); renders `SourcePanel` under assistant messages.

### `frontend/src/components/SourcePanel.jsx`
Renders retrieved `[Paper]` chunks (title + score + preview) and `[Web]` results (title link + preview); shows an amber banner when web search was used.

### `frontend/src/components/Icons.jsx`
Inline SVG icon components (`PaperIcon`, `WebIcon`) used by `SourcePanel` to label sources.

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
5. **How was it evaluated?** → `notebooks/evaluation.ipynb` + `evaluation_results/`
6. **What's done, what's next?** → `Logs.md` (progress) and `TODO.md` (future work)
7. **Where does the data come from?** → `research_papers/` + uploaded PDFs in `backend/data/uploads`
8. **Where are the API keys?** → `.env` (gitignored; template in `.env.example`)
9. **What are the dependencies?** → `pyproject.toml` / `uv.lock` / `frontend/package.json`