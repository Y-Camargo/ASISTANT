from __future__ import annotations
import argparse
from app.config import CFG
from app.embeddings import ensure_ollama_ready
from app.indexer import build_index
from app.logging import log

def main() -> None:
    parser = argparse.ArgumentParser(description="Construye índice ChromaDB desde PDFs usando Ollama.")
    parser.add_argument("--docs", default=str(CFG.docs_path))
    parser.add_argument("--db", default=str(CFG.db_path))
    parser.add_argument("--collection", default=CFG.collection)
    parser.add_argument("--max-chars", type=int, default=CFG.max_chars)
    parser.add_argument("--overlap", type=int, default=CFG.overlap_chars)
    args = parser.parse_args()

    dim, chat_ok = ensure_ollama_ready(CFG.embed_model, CFG.chat_model)
    log(f"Ollama OK. dim={dim}. chat_model_ready={bool(chat_ok)}")

    stats = build_index(
        docs_path=CFG.docs_path if args.docs == str(CFG.docs_path) else None or __import__("pathlib").Path(args.docs),
        db_path=CFG.db_path if args.db == str(CFG.db_path) else None or __import__("pathlib").Path(args.db),
        collection=args.collection,
        max_chars=args.max_chars,
        overlap_chars=args.overlap,
    )
    log(f"Listo ✅ PDFs={stats.files}, chunks nuevos={stats.chunks}, total en colección={stats.total_after}")

if __name__ == "__main__":
    main()
