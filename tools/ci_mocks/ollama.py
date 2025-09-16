from __future__ import annotations
from typing import Any, Dict, List
import re
try:
    from sentence_transformers import SentenceTransformer
except Exception:  # fallback mínimo
    SentenceTransformer = None

_model = None
def _get_model():
    global _model
    if _model is None:
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers no instalado")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embeddings(model: str, prompt: str) -> Dict[str, Any]:
    vec = _get_model().encode([prompt])[0]
    return {"embedding": vec.tolist()}

def chat(model: str, messages: List[Dict[str, str]], options: Dict[str, Any] | None = None) -> Dict[str, Any]:
    # Extrae contexto del mensaje de usuario
    user = next((m for m in messages if m.get("role") == "user"), {"content": ""})
    content = user.get("content", "")
    # Captura bloque de contexto entre "Contexto recuperado:" y "Instrucciones"
    ctx_match = re.search(r"Contexto recuperado:\s*(.+?)\n\nInstrucciones", content, flags=re.S)
    ctx = (ctx_match.group(1) if ctx_match else "").strip()
    # Tags tipo [source#chunk]
    tags = re.findall(r"\[([^\]]+?)#(\d+)\]", ctx)
    unique_tags = []
    for src, ch in tags:
        tag = f"[{src}#{ch}]"
        if tag not in unique_tags:
            unique_tags.append(tag)
        
    # Construye respuesta corta: primeras frases del contexto
    # Quita los tags del texto para mayor legibilidad
    clean_ctx = re.sub(r"\[[^\]]+?\#\d+\]\s*", "", ctx)
    clean_ctx = re.sub(r"\s+", " ", clean_ctx).strip()
    if not clean_ctx:
        ans = "No se encontró contexto relevante; por favor agrega materiales y reintenta."
    else:
        snippet = " ".join(clean_ctx.split()[:90])
        ans = f"{snippet}"
        if unique_tags:
            ans += " " + " ".join(unique_tags[:3])
    return {"message": {"content": ans}}