# Logs Markdown File
## RAG system for Research Papers

This file is to maintain a track of progress, objectives, tech stack and completion percentage of the whole project.

---

## 1. Quick Overview
- **Project Name:** ResearchMate
- **Date Created:** 9 September 2026
- **Status:** In Progress — core RAG, web-search fallback, full-stack web dev, SQLite persistence, and evaluation are done; QA and deployment are pending
- **Author:** Vishrut

---

## 2. Key Objectives & Checklist
- [x] Initial setup and project scaffolding for RAG
- [x] Local RAG system (retrieval + generation, no web search)
- [x] Web-search fallback (Tavily) when retrieval confidence is low
- [x] Initial setup and project scaffolding for Web Dev
- [x] Define system architecture and technical requirements
- [x] Implement core features
- [x] Evaluation harness (`notebooks/evaluation.ipynb`) — RAG vs plain-LLM baseline with LLM-as-a-judge scoring
- [ ] Implement deferred features (topic suggestions, export chat, dark mode; see `TODO.md`)
- [ ] Conduct user testing and quality assurance
- [ ] Deploy to production

---

## 3. Architecture & Components

| Component | Responsibility | Tech Stack | Status |
| :--- | :--- | :--- | :--- |
| **RAG Pipeline** | Prototype retrieval + generation (notebook) | Python, `sentence-transformers`, `groq`, Tavily | Done (`rag.ipynb`) |
| **Backend API** | Server + ported RAG modules + persistence | Python / FastAPI / Uvicorn | Working |
| **Database** | Chunks, embeddings, chat history, document registry | SQLite / SQLAlchemy | Working |
| **Embeddings** | `all-MiniLM-L6-v2`, 384-dim | `sentence-transformers` | Done |
| **Retrieval** | Cosine similarity over in-memory NumPy matrix | NumPy | Done |
| **Generation** | Grounded answer from context + sources | Groq (`groq`) | Working |
| **Web Search** | Fallback when retrieval confidence is low | Tavily (`requests`) | Working |
| **Frontend** | User interface & client logic (sidebar + chat) | React / Vite / Tailwind | Working |
| **Evaluation** | RAG vs plain-LLM comparison + LLM-as-a-judge scores | `pandas` / `matplotlib` (`notebooks/evaluation.ipynb`) | Done (results on an earlier corpus) |

---

## 4. Issues faced and their status
| **Issue** | **Resolved?** | **How?** | **Reason behind issue** |
| :--- | :--- | :--- | :--- |
| **Chunking** | Yes | Reduced chunk size from 150 to 50 words to run locally while print-debugging chunks; final default tuned to 300/30 in `backend/config.py` | The chunk size was too large for the local system and print statements were used to inspect chunks |
| **Index caching** | Yes | Replaced the old `chunks.json` + `matrix.npy` cache with a SQLite-backed index (`chunks` table) rebuilt into the in-memory matrix on startup | File cache drifted out of sync and added extra runtime state |
| **Corpus seed filename check** | No (minor) | Known limitation — `fname.endswith("pdf")` in `backend/rag/retriever.py` is case-sensitive | Non-`.pdf` or mixed-case extensions are skipped during the one-time seed |
| **System prompt formatting** | No (minor) | Known cosmetic issue — a couple of sentences in `SYSTEM_PROMPT` (`backend/config.py`) are concatenated without separating spaces/periods | Lines were added to the prompt at the end of the string |
| **Evaluation corpus drift** | No (minor) | The saved `evaluation_results/` were produced on an earlier 9-PDF corpus; two questions expect the LLM survey and RAG papers, which are not in the current `research_papers/` folder, so their `expected_hit` is `false` | The corpus changed after the evaluation was run; results were not regenerated |

---

## 5. Code Snippet Example

```python
answer, sources, web_results, web_search_used = ask("What is Machine Learning?")
print(answer)
for s in sources:
    print(f"[{s['score']:.3f}] {s['doc_title']}")
if web_search_used:
    for r in web_results:
        print(f"- {r['title']}\n  {r['url']}")
```