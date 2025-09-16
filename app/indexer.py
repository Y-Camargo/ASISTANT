from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable, Tuple, List
from .config import CFG
from .logging import log
from .pdf import find_pdfs, load_pdf_text
from .chunking import chunk_text
from .embeddings import embed_text
from .db import get_client, get_collection

@dataclass
class IndexStats:
    files: int
    chunks: int
    total_after: int

def _hash_id(source: str, idx: int, content: str) -> str:
    h = sha256()
    h.update(source.encode()); h.update(f"#{idx}".encode()); h.update(content.encode())
    return h.hexdigest()

def _embed_batch(texts: List[str], batch_size: int = 16, model: str = CFG.embed_model) -> List[List[float]]:
    embs: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        log(f"Embeddings {i}-{i+len(batch)-1}…")
        for t in batch:
            embs.append(embed_text(t, model))
    return embs

def build_index(
    docs_path: Path = CFG.docs_path,
    db_path: Path = CFG.db_path,
    collection: str = CFG.collection,
    max_chars: int = CFG.max_chars,
    overlap_chars: int = CFG.overlap_chars,
) -> IndexStats:
    if not docs_path.is_dir():
        raise FileNotFoundError(f"No existe la carpeta de materiales: {docs_path}")
    pdfs = find_pdfs(docs_path)
    if not pdfs:
        raise FileNotFoundError("No se encontraron PDFs para indexar.")
    client = get_client(db_path); col = get_collection(client, collection)
    total_chunks = 0
    for pdf in pdfs:
        log(f"Extrayendo: {pdf.name}")
        text = load_pdf_text(pdf)
        if not text:
            log(f"Saltando (sin texto): {pdf.name}")
            continue
        chunks = chunk_text(text, max_chars=max_chars, overlap_chars=overlap_chars)
        log(f"{pdf.name}: {len(chunks)} fragmentos")
        try:
            col.delete(where={"source": pdf.name})
        except Exception:
            pass
        ids = [_hash_id(pdf.name, i, c) for i, c in enumerate(chunks)]
        metas = [{"source": pdf.name, "chunk": i} for i, _ in enumerate(chunks)]
        embs = _embed_batch(chunks, batch_size=16, model=CFG.embed_model)
        if not (len(ids) == len(chunks) == len(embs) == len(metas)):
            raise RuntimeError("Desalineación ids/docs/embeddings/metadatas.")
        col.upsert(ids=ids, documents=chunks, metadatas=metas, embeddings=embs)
        total_chunks += len(chunks)
    try:
        count = col.count()
    except Exception:
        count = len(col.get().get("ids", []))
    return IndexStats(files=len(pdfs), chunks=total_chunks, total_after=count)
