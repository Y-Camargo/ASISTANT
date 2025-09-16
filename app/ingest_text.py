# file: app/ingest.py
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import List

from app.config import CFG
from app.db import get_client, get_collection
from app.chunking import chunk_text
from app.embeddings import embed_text

def _hash_id(source: str, idx: int, content: str) -> str:
    h = sha256()
    h.update(source.encode()); h.update(f"#{idx}".encode()); h.update(content.encode())
    return h.hexdigest()

@dataclass
class IngestResult:
    source: str
    chunks: int
    total_after: int

def ingest_text(source_name: str, text: str) -> IngestResult:
    if not source_name or len(source_name) < 3:
        raise ValueError("source_name inválido (min 3).")
    if not text or len(text.strip()) < 50:
        raise ValueError("Texto demasiado corto (min 50 chars).")

    client = get_client(CFG.db_path)
    col = get_collection(client, CFG.collection)

    chunks: List[str] = chunk_text(text.strip(), max_chars=CFG.max_chars, overlap_chars=CFG.overlap_chars)
    if not chunks:
        raise ValueError("No se generaron fragmentos (revisa el texto).")

    # limpiar previos de este source
    try:
        col.delete(where={"source": source_name})
    except Exception:
        pass

    ids = [_hash_id(source_name, i, c) for i, c in enumerate(chunks)]
    metas = [{"source": source_name, "chunk": i} for i, _ in enumerate(chunks)]
    embs = [embed_text(c, CFG.embed_model) for c in chunks]

    if not (len(ids) == len(chunks) == len(embs) == len(metas)):
        raise RuntimeError("Desalineación ids/docs/embeddings/metadatas.")

    col.upsert(ids=ids, documents=chunks, metadatas=metas, embeddings=embs)

    try:
        total = col.count()
    except Exception:
        total = len(col.get().get("ids", []))

    return IngestResult(source=source_name, chunks=len(chunks), total_after=total)

