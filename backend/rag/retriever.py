import os

import numpy as np
from sqlalchemy.orm import sessionmaker

from backend.config import CORPUS_DIR, EMBEDDING_DIM, RETRIEVAL_K
from backend.models import Chunk, Document, engine
from backend.rag.embeddings import get_embeddings
from backend.rag.pdf_processor import (
    chunk_document,
    extract_text_from_pdf,
    extract_text_from_pdf_bytes,
)

_session = sessionmaker(bind=engine, autoflush=False)

_index: dict | None = None
"""In-memory index: {"records": [...], "matrix": np.ndarray}. Rebuilt from the DB."""


def _embed(records: list[dict]) -> np.ndarray:
    return (
        get_embeddings([r["text"] for r in records])
        if records
        else np.zeros((0, EMBEDDING_DIM))
    )


def _rows_to_index(rows) -> dict:
    records = []
    vecs = []
    for row in rows:
        records.append(
            {
                "chunk_id": row.chunk_id,
                "doc_id": row.doc_id,
                "doc_title": row.doc_title,
                "text": row.text,
                "source_type": row.source_type,
            }
        )
        vecs.append(np.frombuffer(row.embedding, dtype=np.float32))
    matrix = np.vstack(vecs) if vecs else np.zeros((0, EMBEDDING_DIM))
    return {"records": records, "matrix": matrix}


def _load_from_db() -> dict:
    """Read every chunk + embedding from SQLite and rebuild the in-memory index."""
    db = _session()
    try:
        rows = db.query(Chunk).order_by(Chunk.doc_id, Chunk.position).all()
    finally:
        db.close()
    return _rows_to_index(rows)


def _seed_corpus():
    """Ingest research_papers/*.pdf into the DB once (Document.source = 'corpus')."""
    db = _session()
    try:
        if db.query(Chunk).count() > 0:
            return

        for fname in sorted(os.listdir(CORPUS_DIR)):
            if not fname.endswith("pdf"):
                continue
            doc_id = os.path.splitext(fname)[0]
            path = CORPUS_DIR / fname
            text = extract_text_from_pdf(str(path))
            records = chunk_document(doc_id, fname, text)
            for rec in records:
                rec["source_type"] = "paper"
            if not records:
                continue

            emb = _embed(records)
            doc = Document(
                filename=fname,
                source="corpus",
                local_path=str(path),
                num_chunks=len(records),
            )
            db.add(doc)
            for i, (rec, vec) in enumerate(zip(records, emb)):
                db.add(
                    Chunk(
                        chunk_id=rec["chunk_id"],
                        doc_id=rec["doc_id"],
                        doc_title=rec["doc_title"],
                        text=rec["text"],
                        source_type="paper",
                        position=i,
                        embedding=vec.astype(np.float32).tobytes(),
                    )
                )
        db.commit()
    finally:
        db.close()


def build_index(force: bool = False) -> dict:
    """Build the in-memory index from the DB (seeding research_papers/ on first run)."""
    global _index
    if _index is not None and not force:
        return _index
    _seed_corpus()
    _index = _load_from_db()
    return _index


def add_uploaded_pdf(filename: str, pdf_bytes: bytes, local_path: str = "") -> int:
    """Persist an uploaded PDF's chunks + embeddings to the DB, then refresh the index."""
    global _index
    doc_id = os.path.splitext(filename)[0]
    text = extract_text_from_pdf_bytes(pdf_bytes)
    records = chunk_document(doc_id, filename, text)
    for rec in records:
        rec["source_type"] = "upload"
    if not records:
        return 0

    emb = _embed(records)

    db = _session()
    try:
        # Re-uploading the same filename replaces the old version.
        db.query(Chunk).filter(Chunk.doc_id == doc_id).delete()
        doc = db.query(Document).filter(Document.filename == filename).first()
        if doc is None:
            doc = Document(
                filename=filename,
                source="upload",
                local_path=local_path,
                num_chunks=len(records),
            )
            db.add(doc)
        else:
            doc.source = "upload"
            doc.local_path = local_path
            doc.num_chunks = len(records)

        for i, (rec, vec) in enumerate(zip(records, emb)):
            db.add(
                Chunk(
                    chunk_id=rec["chunk_id"],
                    doc_id=rec["doc_id"],
                    doc_title=rec["doc_title"],
                    text=rec["text"],
                    source_type="upload",
                    position=i,
                    embedding=vec.astype(np.float32).tobytes(),
                )
            )
        db.commit()
    finally:
        db.close()

    # Refresh the in-memory index from the DB so it stays consistent.
    _index = _load_from_db()
    return len(records)


def retrieve(query: str, k: int = RETRIEVAL_K, index: dict | None = None) -> list[dict]:
    """Cosine-similarity retrieval: embed query, dot with matrix, return top-k (like rag.ipynb cell 16)."""
    index = index or build_index()
    records, matrix = index["records"], index["matrix"]
    if not records:
        return []
    q_vec = get_embeddings([query])[0]
    sims = matrix @ q_vec
    top_idx = np.argsort(-sims)[:k]
    return [
        {**records[i], "score": float(sims[i])}
        for i in top_idx
        if float(sims[i]) > 0
    ]