from __future__ import annotations

def chunk_text(
    text: str,
    max_chars: int = 2800,
    overlap_chars: int = 400,
    min_tail_merge: int = 300,
) -> list[str]:
    if not text:
        return []
    if max_chars <= 0 or not (0 <= overlap_chars < max_chars):
        raise ValueError("Parámetros de chunking inválidos.")
    chunks: list[str] = []
    step = max_chars - overlap_chars
    for i in range(0, len(text), step):
        chunks.append(text[i : i + max_chars].strip())
    if len(chunks) >= 2 and len(chunks[-1]) < min_tail_merge:
        chunks[-2] = (chunks[-2] + " " + chunks[-1]).strip()
        chunks.pop()
    return [c for c in chunks if c]