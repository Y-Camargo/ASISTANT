from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Config:
    db_path: Path = Path(os.getenv("DB_PATH", "./chroma_db"))
    docs_path: Path = Path(os.getenv("DOCS_PATH", "./materiales"))
    profiles_path: Path = Path(os.getenv("PROFILES_PATH", "./perfiles"))
    collection: str = os.getenv("COLLECTION", "capacitacion")
    chat_model: str = os.getenv("CHAT_MODEL", "phi3")
    embed_model: str = os.getenv("EMBED_MODEL", "nomic-embed-text")
    max_words: int = int(os.getenv("MAX_WORDS", "180"))
    top_k: int = int(os.getenv("TOP_K", "4"))
    distance_threshold: float = float(os.getenv("DIST_THRESHOLD", "0.4"))
    max_chars: int = int(os.getenv("MAX_CHARS", "2800"))
    overlap_chars: int = int(os.getenv("OVERLAP_CHARS", "400"))

CFG = Config()