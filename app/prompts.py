from __future__ import annotations

def build_system(profile: dict) -> str:
    style = profile.get("learning_style", "visual")
    level = profile.get("level", "intermedio")
    maxw = int(profile.get("constraints", {}).get("max_words", 180))
    tone = {
        "visual": "usa listas, esquemas y analogías visuales",
        "pragmatica": "da pasos accionables, ejemplos breves y checklists",
        "narrativa": "usa ejemplos con pequeñas historias y escenarios",
    }.get(style, "da explicaciones claras y ejemplos")
    return (
        "Eres un asistente de aprendizaje para capacitaciones internas.\n"
        f"Lenguaje: español. Nivel del público: {level}. Estilo: {style} ({tone}).\n"
        f"Responde en menos de {maxw} palabras y cita como [source#chunk] solo si **existe** en el contexto.\n"
        "Si no hay contexto relevante, dilo explícitamente y **no inventes** etiquetas de cita."
    )

def build_user_prompt(message: str, context: str) -> str:
    return (
        f"Pregunta del colaborador: {message}\n\n"
        f"Contexto recuperado (cítalo como [source#chunk] solo si aparece abajo):\n{context}\n\n"
        "Instrucciones: responde SOLO con información respaldada por el contexto cuando sea posible. "
        "Si el contexto está vacío o es irrelevante, indícalo claramente y no inventes citas."
    )
