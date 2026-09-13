from io import BytesIO

from pypdf import PdfReader

from backend.config import CHUNK_OVERLAP, CHUNK_SIZE


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file."""
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() for page in reader.pages)


def extract_text_from_pdf_bytes(data: bytes) -> str:
    """Extract all text from an in-memory PDF buffer."""
    reader = PdfReader(BytesIO(data))
    return "\n".join(page.extract_text() for page in reader.pages)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping word-based chunks (ported from rag.ipynb)."""
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start += chunk_size - overlap
    return chunks


def chunk_document(doc_id: str, doc_title: str, text: str) -> list[dict]:
    """Turn one document's raw text into chunk records."""
    return [
        {
            "chunk_id": f"{doc_id}_c{i}",
            "doc_id": doc_id,
            "doc_title": doc_title,
            "text": chunk,
            "source_type": "paper",
        }
        for i, chunk in enumerate(chunk_text(text))
    ]