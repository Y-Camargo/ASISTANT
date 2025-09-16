from __future__ import annotations
import argparse
from app.config import CFG
from app.profiles import load_profile
from app.retriever import retrieve
from app.prompts import build_system, build_user_prompt
from app.llm import chat

def main() -> None:
    p = argparse.ArgumentParser(description="CLI de chat sobre el índice.")
    p.add_argument("message", help="Pregunta del usuario")
    p.add_argument("--user", default="ana", help="ID del perfil (archivo en perfiles/)")
    p.add_argument("--k", type=int, default=CFG.top_k)
    p.add_argument("--th", type=float, default=CFG.distance_threshold)
    p.add_argument("--temp", type=float, default=0.3)
    args = p.parse_args()

    profile = load_profile(args.user)
    ctx, srcs, used = retrieve(args.message, k=args.k, threshold=args.th)
    sys_p = build_system(profile)
    user_p = build_user_prompt(args.message, ctx)
    if used == 0:
        user_p += "\n\nNota: No se encontró contexto relevante."
    resp = chat(CFG.chat_model, sys_p, user_p, args.temp)
    print("\n--- Respuesta ---\n")
    print(resp)
    if srcs:
        print("\n--- Fuentes ---")
        for s in srcs:
            print(" •", s)

if __name__ == "__main__":
    main()
