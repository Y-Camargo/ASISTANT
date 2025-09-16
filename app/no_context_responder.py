# file: no_context_responder.py
from __future__ import annotations

from dataclasses import dataclass

@dataclass
class Profile:
    learning_style: str = "visual"      # visual | pragmatica | narrativa
    level: str = "intermedio"
    max_words: int = 180

def _cta(topic: str) -> str:
    return (
        "Para incorporarlo al asistente, por favor agrega un material fuente (PDF o guía interna) que cubra:\n"
        f"• Definición y alcance de {topic}\n"
        "• Responsabilidades antes / durante / después\n"
        "• Límites de responsabilidad y escalamiento\n"
        "• Listas de verificación y métricas (KPIs)\n"
        "Ubícalo en ./materiales y reindexa."
    )

def _general_guidance(topic: str, style: str) -> str:
    # Por qué: ofrecer ayuda opcional, marcada como no validada por el material
    if style == "pragmatica":
        return (
            "Guía general (no validada por el material):\n"
            "Checklist durante la sesión:\n"
            "1) Apertura: objetivos, reglas y agenda.\n"
            "2) Gestión del tiempo y participación (preguntas, turnos, dinámicas breves).\n"
            "3) Claridad: resumir puntos clave y verificar comprensión.\n"
            "4) Seguridad/ética: cuidar datos y respeto.\n"
            "5) Cierre: acuerdos, siguientes pasos y evaluación rápida."
        )
    if style == "narrativa":
        return (
            "Guía general (no validada por el material):\n"
            "Escenario breve: Ana facilita una sesión. Arranca alineando objetivos y tiempos, alterna explicación y práctica, "
            "observa señales de confusión y ajusta el ritmo, promueve participación equitativa, resume cada bloque y cierra con "
            "compromisos y encuesta rápida."
        )
    # visual (default)
    return (
        "Guía general (no validada por el material):\n"
        "Durante la sesión — mapa rápido:\n"
        "• Apertura: propósito, agenda, reglas.\n"
        "• Desarrollo: explicar→practicar→feedback (ciclos cortos).\n"
        "• Inclusión: turnos, preguntas, ejemplos.\n"
        "• Seguimiento: resumen, tareas, evaluación."
    )

def no_context_reply(topic: str, profile: Profile, strict: bool = True) -> str:
    base = (
        f"No encuentro información sobre “{topic}” en los materiales indexados [source#none]. "
        "Para responder con precisión necesito esa fuente."
    )
    cta = _cta(topic)
    parts = [base, cta]
    if not strict:
        parts.append(_general_guidance(topic, profile.learning_style))
    msg = "\n\n".join(parts)

    # Límite de palabras suave
    words = msg.split()
    if len(words) > profile.max_words:
        msg = " ".join(words[: profile.max_words]) + "…"
    return msg

# ---- Ejemplos de uso ----
if __name__ == "__main__":
    topic = "las responsabilidades del facilitador durante una sesión"
    print("# Estricto (recomendado por defecto)")
    print(no_context_reply(topic, Profile("visual", "intermedio", 120), strict=True))
    print("\n# Con guía general opcional")
    print(no_context_reply(topic, Profile("pragmatica", "intermedio", 180), strict=False))
