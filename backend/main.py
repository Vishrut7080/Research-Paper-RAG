from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker

from backend.config import RETRIEVAL_K, TOP_WEB_RESULTS, UPLOADS_DIR, WEB_SEARCH_THRESHOLD
from backend.models import Chat, Document, engine
from backend.rag.generator import generate_answer
from backend.rag.retriever import add_uploaded_pdf, build_index, retrieve
from backend.rag.web_search import search_web

app = FastAPI(title="ResearchMate", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


class QueryRequest(BaseModel):
    query_text: str


@app.get("/health")
def health():
    index = build_index()
    return {"status": "ok", "chunks": len(index["records"])}


@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    filename = Path(file.filename).name
    if not filename.lower().endswith("pdf"):
        return {"status": "error", "message": "Only PDF files are supported."}

    data = file.file.read()
    if not data:
        return {"status": "error", "message": "Uploaded file is empty.", "chunks": 0}

    save_path = UPLOADS_DIR / filename
    save_path.write_bytes(data)
    chunks = add_uploaded_pdf(filename, data, local_path=str(save_path))

    if chunks == 0:
        return {"status": "error", "message": "No text could be extracted from this PDF.", "chunks": 0}

    return {"status": "success", "filename": filename, "chunks": chunks}


@app.post("/query")
def query(payload: QueryRequest):
    query_text = payload.query_text
    retrieved = retrieve(query_text, k=RETRIEVAL_K)
    top_score = retrieved[0]["score"] if retrieved else 0.0
    web_search_used = top_score < WEB_SEARCH_THRESHOLD

    context = "\n\n".join(
        f"[{r['doc_title']}]\n{r['text']}" for r in retrieved
    ) or "No relevant papers found in the corpus."

    web_results = []
    if web_search_used:
        web_results = search_web(query_text)
        if web_results:
            web_context = "\n\n".join(
                f"[Web: {r['title']}]\n{r['url']}\n{r['content'][:500]}" for r in web_results
            )
            context = (
                context
                + "\n\n--- WEB RESULTS (use only if the papers above lack the answer) ---\n\n"
                + web_context
            )

    answer = generate_answer(query_text, context)

    sources = [
        {
            "doc_title": r["doc_title"],
            "chunk_id": r["chunk_id"],
            "score": r["score"],
            "text": r["text"][:200],
        }
        for r in retrieved
    ]

    db = SessionLocal()
    try:
        chat = Chat(
            query=query_text,
            answer=answer,
            sources=sources,
            web_results=web_results,
            web_search_used=web_search_used,
        )
        db.add(chat)
        db.commit()
    finally:
        db.close()

    return {
        "query": query_text,
        "answer": answer,
        "sources": sources,
        "web_results": web_results,
        "web_search_used": web_search_used,
    }


@app.get("/history")
def history():
    db = SessionLocal()
    try:
        chats = (
            db.query(Chat).order_by(Chat.timestamp.desc()).limit(50).all()
        )
        return [
            {
                "id": c.id,
                "query": c.query,
                "answer": c.answer,
                "sources": c.sources,
                "web_results": c.web_results,
                "web_search_used": c.web_search_used,
                "timestamp": c.timestamp.isoformat() if c.timestamp else None,
            }
            for c in chats
        ]
    finally:
        db.close()


@app.get("/documents")
def documents():
    db = SessionLocal()
    try:
        docs = db.query(Document).order_by(Document.uploaded_at.desc()).all()
        return [
            {
                "id": d.id,
                "filename": d.filename,
                "source": d.source,
                "local_path": d.local_path,
                "num_chunks": d.num_chunks,
                "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
            }
            for d in docs
        ]
    finally:
        db.close()


@app.get("/documents/{doc_id}/file")
def document_file(doc_id: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
    finally:
        db.close()
    if doc is None or not doc.local_path:
        raise HTTPException(status_code=404, detail="Document file not found.")
    path = Path(doc.local_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing on disk.")
    return FileResponse(path, filename=doc.filename, media_type="application/pdf")