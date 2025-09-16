from __future__ import annotations
import glob
from pathlib import Path
from typing import List
from pypdf import PdfReader
from .logging import log

def find_pdfs(path: Path) -> List[Path]:
    pdfs = set(glob.glob(str(path / "*.pdf"))) | set(glob.glob(str(path / "*.PDF")))
    return sorted(Path(p) for p in pdfs)

def load_pdf_text(fp: Path) -> str:
    try:
        reader = PdfReader(str(fp))
        texts = []
        for i, page in enumerate(reader.pages):
            try:
                txt = page.extract_text() or ""
            except Exception as e:
                log(f"Advertencia: no pude extraer texto de la página {i} en {fp.name}: {e}")
                txt = ""
            texts.append(txt)
        return " ".join(" ".join(t.split()) for t in texts).strip()
    except Exception as e:
        log(f"Error leyendo {fp.name}: {e}")
        return ""