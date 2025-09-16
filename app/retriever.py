from __future__ import annotations
from typing import List, Tuple
from .config import CFG
from .embeddings import embed_text
from .db import get_client, get_collection

def retrieve(
    query: str,
    k: int = max(8, CFG.top_k),                 # ↑ recall por defecto
    threshold: float = max(0.95, CFG.distance_threshold),  # ↑ umbral (cosine distance: menor = mejor)
    fallback_if_empty: bool = True,             # si nada pasa el umbral, usa el mejor vecino
) -> Tuple[str, List[str], int]:
    client = get_client(CFG.db_path); col = get_collection(client, CFG.collection)
    try:
        total = col.count()
    except Exception:
        total = len(col.get().get("ids", []))
    if total == 0:
        return "", [], 0

    k = min(k, total)
    q_emb = embed_text(query, CFG.embed_model)
    res = col.query(query_embeddings=[q_emb], n_results=k, include=["documents", "metadatas", "distances"])
    docs0 = res.get("documents", [[]])[0] or []
    metas0 = res.get("metadatas", [[]])[0] or []
    dists0 = res.get("distances", [[]])[0] or []

    ctx_parts, sources, used = [], [], 0
    for doc, meta, dist in zip(docs0, metas0, dists0):
        if dist is not None and dist <= threshold:
            tag = f"[{meta.get('source', 'unk')}#{meta.get('chunk', '?')}]"
            ctx_parts.append(f"{tag} {doc}")
            sources.append(tag)
            used += 1

    # Fallback: usa el mejor vecino aunque supere el umbral
    if used == 0 and fallback_if_empty and docs0:
        best_idx = min(range(len(docs0)), key=lambda i: (dists0[i] if dists0[i] is not None else 1e9))
        best_doc = docs0[best_idx]
        best_meta = metas0[best_idx]
        tag = f"[{best_meta.get('source','unk')}#{best_meta.get('chunk','?')}]"
        ctx_parts.append(f"{tag} {best_doc}")
        sources.append(tag + " (low_conf)")
        used = 1

    return ("\n\n".join(ctx_parts), sources, used)
