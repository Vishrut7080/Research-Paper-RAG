import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "research.db"
CORPUS_DIR = Path(os.getenv("RESEARCH_CORPUS", BASE_DIR.parent / "research_papers"))

CHUNK_SIZE = 300
CHUNK_OVERLAP = 30
RETRIEVAL_K = 5
WEB_SEARCH_THRESHOLD = 0.40
TOP_WEB_RESULTS = 5
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
EMBEDDING_BATCH_SIZE = 32
MAX_TOKENS = 500
SYSTEM_PROMPT = (
    "Answer using ONLY the provided context below (research papers and, if present, web results). "
    "If the context doesn't contain the answer, just SAY SO. "
    "Cite each fact with its source: [Paper: filename] or [Web: title]. "
    "Also summarize the answer in 2-3 lines."
)

for _d in (DATA_DIR, UPLOADS_DIR):
    _d.mkdir(parents=True, exist_ok=True)