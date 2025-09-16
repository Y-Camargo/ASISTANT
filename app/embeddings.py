from __future__ import annotations
from typing import List, Tuple
import ollama
import requests

def ensure_ollama_ready(embed_model: str, chat_model: str) -> Tuple[int, bool]:
    try:
        requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
    except Exception as e:
        raise RuntimeError(f"No pude conectar con Ollama: {e}. Ejecuta `ollama serve`.") from e
    try:
        e = ollama.embeddings(model=embed_model, prompt="ok")
        emb = e.get("embedding", [])
        if not isinstance(emb, list) or not emb:
            raise RuntimeError("Respuesta de embeddings inválida.")
        dim = len(emb)
    except Exception as ex:
        raise RuntimeError(f"Embeddings falló con '{embed_model}': {ex}. ¿`ollama pull {embed_model}`?") from ex
    chat_ok = False
    try:
        r = ollama.chat(model=chat_model, messages=[{"role": "user", "content": "ok"}], options={"temperature": 0.0})
        chat_ok = bool((r or {}).get("message", {}).get("content"))
    except Exception:
        chat_ok = False
    return dim, chat_ok

def embed_text(text: str, model: str) -> List[float]:
    try:
        return ollama.embeddings(model=model, prompt=text)["embedding"]
    except Exception as ex:
        raise RuntimeError(f"Error creando embedding con '{model}': {ex}") from ex
