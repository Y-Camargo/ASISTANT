from __future__ import annotations
from typing import Dict, Any
import ollama

def chat(model: str, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    # Por qué: centralizamos llamada para poder interceptar/streaming luego.
    r: Dict[str, Any] = ollama.chat(
        model=model,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        options={"temperature": temperature},
    )
    return (r or {}).get("message", {}).get("content", "").strip()

