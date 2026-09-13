import numpy as np
from sentence_transformers import SentenceTransformer

from backend.config import EMBEDDING_BATCH_SIZE, EMBEDDING_MODEL

_MODEL: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Lazily load (and cache) the embedding model, like rag.ipynb cell 2."""
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(EMBEDDING_MODEL)
    return _MODEL


def get_embeddings(texts: list[str]) -> np.ndarray:
    """Encode texts and L2-normalize, so dot-product == cosine similarity."""
    model = get_model()
    vecs = model.encode(texts, convert_to_numpy=True, batch_size=EMBEDDING_BATCH_SIZE)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1e-8
    return vecs / norms