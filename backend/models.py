import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, LargeBinary, String, Text, create_engine
from sqlalchemy.orm import declarative_base

from backend.config import DB_PATH

Base = declarative_base()


def new_id() -> str:
    return uuid.uuid4().hex


class Chat(Base):
    __tablename__ = "chats"

    id = Column(String, primary_key=True, default=new_id)
    query = Column(String, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(JSON, default=list)
    web_results = Column(JSON, default=list)
    web_search_used = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=new_id)
    filename = Column(String, unique=True, nullable=False)
    source = Column(String, default="upload")  # 'corpus' (seeded) | 'upload' (user)
    local_path = Column(String, default="")
    num_chunks = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class Chunk(Base):
    """One indexed chunk of a document, with its embedding (float32 bytes)."""

    __tablename__ = "chunks"

    id = Column(String, primary_key=True, default=new_id)
    chunk_id = Column(String, unique=True, nullable=False)
    doc_id = Column(String, nullable=False)
    doc_title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    source_type = Column(String, default="paper")
    position = Column(Integer, default=0)
    embedding = Column(LargeBinary, nullable=False)


engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})