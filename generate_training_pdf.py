# file: generate_training_pdf.py
# Requisitos: pip install reportlab
from __future__ import annotations

import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfdoc

OUT_DIR = Path("./materiales")
OUT_FILE = OUT_DIR / "manual_capacitacion.pdf"

# Por qué: asegurar extracción y búsqueda; metadatos ayudan a lectores/ATS.
DOC_INFO = {
    "title": "Manual de Capacitación - Operaciones y Atención al Cliente",
    "author": "Capacitación Interna",
    "subject": "Objetivos, procesos, políticas, KPIs y seguridad",
    "keywords": "capacitación, procesos, políticas, KPIs, seguridad, glosario",
}


def _styles():
    ss = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleXL",
        parent=ss["Title"],
        fontSize=28,
        leading=32,
        spaceAfter=24,
        alignment=1,
    )
    h1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=18, leading=22, spaceBefore=12, spaceAfter=8)
    h2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=14, leading=18, spaceBefore=10, spaceAfter=6)
    body = ParagraphStyle("Body", parent=ss["BodyText"], fontSize=11, leading=16, spaceAfter=8)
    small = ParagraphStyle("Small", parent=body, fontSize=9, leading=13)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=14, bulletIndent=6)
    return {"title": title, "h1": h1, "h2": h2, "body": body, "small": small, "bullet": bullet}


def _page_number(canvas, doc):
    # Por qué: ayuda a navegación y chunking estable.
    canvas.saveState()
    page_num = f"{doc.page}"
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(A4[0] - 2 * cm, 1.5 * cm, f"Página {page_num}")
    canvas.restoreState()


def make_pdf(path: Path) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    styles = _styles()
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.0 * cm,
        title=DOC_INFO["title"],
        author=DOC_INFO["author"],
        subject=DOC_INFO["subject"],
        keywords=DOC_INFO["keywords"],
    )

    story = []

    # Portada
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph("Manual de Capacitación", styles["title"]))
    story.append(Paragraph("Operaciones y Atención al Cliente", styles["h2"]))
    story.append(Spacer(1, 1.2 * cm))
    story.append(
        Paragraph(
            "Este documento define objetivos, alcance, procedimientos, políticas, métricas (KPIs) y lineamientos de seguridad para el equipo.",
            styles["body"],
        )
    )
    story.append(Spacer(1, 10))
    story.append(Paragraph("Versión 1.0 — Español (es-ES)", styles["small"]))
    story.append(PageBreak())

    # 1. Objetivo general
    story.append(Paragraph("1. Objetivo general", styles["h1"]))
    story.append(
        Paragraph(
            "Alinear a todo el personal en prácticas homogéneas de servicio y operación, reduciendo variabilidad, mejorando la experiencia del cliente y "
            "asegurando el cumplimiento normativo en cada interacción.",
            styles["body"],
        )
    )

    # 2. Objetivos específicos
    story.append(Paragraph("2. Objetivos específicos", styles["h1"]))
    objetivos = [
        "Estandarizar el proceso de alta, atención, seguimiento y cierre.",
        "Disminuir retrabajos y tiempos de ciclo en un 20% trimestral.",
        "Incrementar la satisfacción (CSAT) por encima de 4.5/5.",
        "Fortalecer la cultura de seguridad y protección de datos.",
    ]
    story.append(
        ListFlowable(
            [ListItem(Paragraph(o, styles["body"])) for o in objetivos],
            bulletType="bullet",
            start="•",
            leftPadding=14,
        )
    )

    # 3. Alcance y público
    story.append(Paragraph("3. Alcance y público objetivo", styles["h1"]))
    story.append(
        Paragraph(
            "Este manual aplica a personal nuevo y vigente de Operaciones y Atención al Cliente, con foco en actividades de front-office, back-office, "
            "y roles de supervisión. No cubre configuración de sistemas ni administración de infraestructura.",
            styles["body"],
        )
    )

    # 4. Procedimiento de alta de cliente
    story.append(Paragraph("4. Procedimiento de alta de cliente", styles["h1"]))
    pasos = [
        ("Recepción de solicitud", "Registrar requerimiento con datos mínimos y consentimiento informado."),
        ("Validación de identidad", "Verificar documentación y coincidencia de datos personales."),
        ("Evaluación y aprobación", "Revisar criterios de elegibilidad y riesgos, documentar decisión."),
        ("Creación en sistema", "Generar registro maestro y asignar identificadores."),
        ("Bienvenida y activación", "Enviar correo de bienvenida y guías de primeros pasos."),
    ]
    for i, (titulo, detalle) in enumerate(pasos, start=1):
        story.append(Paragraph(f"4.{i}. {titulo}", styles["h2"]))
        story.append(Paragraph(detalle, styles["body"]))

    # 5. Políticas (Do / Don't)
    story.append(Paragraph("5. Políticas de atención (Do / Don't)", styles["h1"]))
    story.append(Paragraph("Do (obligatorio):", styles["h2"]))
    do_list = [
        "Confirmar identidad antes de revelar información sensible.",
        "Usar lenguaje claro, empático y profesional.",
        "Registrar cada interacción en el sistema dentro de las 24 horas.",
    ]
    story.append(ListFlowable([ListItem(Paragraph(x, styles["body"])) for x in do_list], bulletType="bullet", start="•"))
    story.append(Paragraph("Don't (prohibido):", styles["h2"]))
    dont_list = [
        "Compartir credenciales, códigos o datos personales por canales no autorizados.",
        "Modificar registros sin evidencia documental.",
        "Prometer tiempos o resultados que no puedas cumplir.",
    ]
    story.append(
        ListFlowable([ListItem(Paragraph(x, styles["body"])) for x in dont_list], bulletType="bullet", start="•")
    )

    # 6. KPIs y metas
    story.append(Paragraph("6. Métricas y KPIs", styles["h1"]))
    story.append(
        Paragraph(
            "Se realiza seguimiento semanal y mensual. Los KPIs se calculan con definiciones claras y fuentes controladas.",
            styles["body"],
        )
    )
    kpis = [
        "<b>CSAT</b>: promedio de satisfacción del cliente post-atención (meta ≥ 4.5/5).",
        "<b>NPS</b>: recomendación neta; complemento cualitativo del CSAT.",
        "<b>FCR</b>: resolución al primer contacto (meta ≥ 75%).",
        "<b>AHT</b>: tiempo medio de atención; optimizar sin afectar calidad.",
        "<b>SLA</b>: cumplimiento de acuerdos de nivel de servicio.",
    ]
    story.append(
        ListFlowable(
            [ListItem(Paragraph(k, styles["body"])) for k in kpis],
            bulletType="bullet",
            start="•",
            leftPadding=14,
        )
    )

    # 7. Seguridad e higiene
    story.append(Paragraph("7. Seguridad e higiene", styles["h1"]))
    story.append(
        Paragraph(
            "Cumple las normas de seguridad ocupacional. Reporta incidentes en menos de 24 horas. Mantén áreas despejadas, "
            "usa EPP cuando aplique y protege datos conforme a la política de privacidad.",
            styles["body"],
        )
    )
    story.append(
        ListFlowable(
            [
                ListItem(Paragraph("Bloquea tu equipo al ausentarte del puesto.", styles["body"])),
                ListItem(Paragraph("No imprimas datos personales salvo autorización expresa.", styles["body"])),
                ListItem(Paragraph("Sigue las rutas de evacuación y participa en simulacros.", styles["body"])),
            ],
            bulletType="bullet",
            start="•",
        )
    )

    # 8. Roles y responsabilidades
    story.append(Paragraph("8. Roles y responsabilidades", styles["h1"]))
    story.append(
        Paragraph(
            "<b>Agente</b>: ejecutar procesos, registrar evidencias y escalar riesgos. "
            "<b>Supervisor</b>: monitoreo, coaching y aprobación de excepciones. "
            "<b>Calidad</b>: auditoría y mejora continua.",
            styles["body"],
        )
    )

    # 9. Anexos y glosario
    story.append(Paragraph("9. Anexos y glosario", styles["h1"]))
    story.append(
        Paragraph(
            "<b>Glosario:</b> KPI (indicador clave de desempeño), CSAT (satisfacción del cliente), FCR (resolución al primer contacto), SLA (acuerdo de nivel de servicio).",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "Para materiales complementarios (plantillas, guías rápidas y checklist), consulta el repositorio interno.",
            styles["body"],
        )
    )

    # Relleno controlado para asegurar varias páginas (chunking cómodo)
    filler = (
        "Nota operativa: valida que las entradas de datos estén completas y legibles. "
        "Los campos obligatorios deben tener formato consistente; usa validaciones automáticas. "
        "Documenta decisiones y excepciones con evidencia adjunta. "
        "Revisa periódicamente las métricas y detecta desviaciones para acciones correctivas."
    )
    for _ in range(8):
        story.append(Paragraph(filler, styles["body"]))

    # Construcción
    def _on_first(canvas, doc):
        _page_number(canvas, doc)
        info = pdfdoc.PDFInfo()
        info.title = DOC_INFO["title"]
        info.author = DOC_INFO["author"]
        info.subject = DOC_INFO["subject"]
        info.keywords = DOC_INFO["keywords"]
        canvas._doc.info = info  # por qué: fijar metadatos básicos

    doc.build(story, onFirstPage=_on_first, onLaterPages=_page_number)
    print(f"PDF generado en: {path.resolve()}")


if __name__ == "__main__":
    make_pdf(OUT_FILE)
