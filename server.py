from __future__ import annotations
import os
from typing import Any, Dict, List
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from app.config import CFG
from app.embeddings import ensure_ollama_ready
from app.profiles import load_profile
from app.retriever import retrieve
from app.prompts import build_system, build_user_prompt
from app.llm import chat
from app.db import get_client, get_collection
from app.ingest_text import ingest_text  # ← este módulo/función existe en app/ingest_text.py

app = FastAPI(title="Asistente de Aprendizaje")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

class IngestIn(BaseModel):
    source_name: str = Field(..., min_length=3)
    text: str = Field(..., min_length=50)

class ChatIn(BaseModel):
    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    top_k: int = Field(CFG.top_k, ge=1, le=20)
    distance_threshold: float = Field(CFG.distance_threshold, ge=0.0, le=2.0)
    temperature: float = Field(0.3, ge=0.0, le=1.0)

class ChatOut(BaseModel):
    answer: str
    sources: List[str] = []
    used_chunks: int = 0
    meta: Dict[str, Any] = {}

@app.on_event("startup")
def _startup() -> None:
    print(f"[server] loaded: {__file__}", flush=True)
    ensure_ollama_ready(CFG.embed_model, CFG.chat_model)

@app.get("/health")
def health() -> Dict[str, Any]:
    dim, chat_ok = ensure_ollama_ready(CFG.embed_model, CFG.chat_model)
    client = get_client(CFG.db_path); col = get_collection(client, CFG.collection)
    try: cnt = col.count()
    except Exception: cnt = len(col.get().get("ids", []))
    return {"status": "ok", "embedding_dim": dim, "chat_model_ready": bool(chat_ok), "chroma_count": cnt}

@app.get("/sources")
def sources() -> Dict[str, Any]:
    """Lista fuentes y cantidad de chunks por cada una."""
    client = get_client(CFG.db_path)
    col = get_collection(client, CFG.collection)
    data = col.get(include=["metadatas"])
    metas = (data or {}).get("metadatas", [])
    counts: Dict[str, int] = {}
    for m in metas:
        src = m.get("source", "unk")
        counts[src] = counts.get(src, 0) + 1
    return {
        "sources": [{"source": s, "chunks": n} for s, n in sorted(counts.items(), key=lambda x: -x[1])],
        "total": sum(counts.values()),
    }

@app.post("/ingest_text")
def ingest_text_ep(payload: IngestIn):
    try:
        res = ingest_text(payload.source_name, payload.text)
        return {"ok": True, "source": res.source, "chunks": res.chunks, "total_after": res.total_after}
    except ValidationError as ve:
        return JSONResponse(status_code=422, content={"error": "payload inválido", "detail": ve.errors()})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Ingest falló: {type(e).__name__}: {e}"})

@app.post("/chat", response_model=ChatOut)
def chat_ep(payload: ChatIn):
    try:
        profile = load_profile(payload.user_id)
        context, sources_tags, used = retrieve(payload.message, k=payload.top_k, threshold=payload.distance_threshold)
        sys_prompt = build_system(profile)
        user_prompt = build_user_prompt(payload.message, context)
        if used == 0:
            user_prompt += "\n\nNota: No se encontró contexto relevante."
        answer = chat(CFG.chat_model, sys_prompt, user_prompt, payload.temperature) or "Modelo no disponible."
        return ChatOut(answer=answer, sources=sources_tags, used_chunks=used, meta={"model": CFG.chat_model})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Fallo en /chat: {type(e).__name__}: {e}"})

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)