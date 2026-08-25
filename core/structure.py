import re
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document

from core.ai.provider import AIProvider
from core.exceptions import ExtractionError
from core.models import DiscoveryMethod

_MAX_TITLE_LEN = 100
_MIN_TITLE_LEN = 6
_CENTER_TOLERANCE_PX = 15.0


def _es_ruido(texto: str) -> bool:
    t = texto.strip()
    if len(t) < _MIN_TITLE_LEN or len(t) > _MAX_TITLE_LEN:
        return True
    if "$" in t or "/" in t:
        return True
    if t.isdigit():
        return True
    return False


def _discover_from_toc(pdf_path: str | Path) -> list[str]:
    """Nivel 1: marcadores/TOC nativos del PDF (más preciso cuando existe)."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise ExtractionError(f"No se pudo abrir el PDF para leer TOC '{pdf_path}': {e}") from e

    try:
        toc = doc.get_toc()
        titulos = [item[1].strip() for item in toc if item[0] == 1 and item[1].strip()]
        return list(dict.fromkeys(titulos))  # sin duplicados, conserva orden
    finally:
        doc.close()


def _discover_pdf_heuristic(pdf_path: str | Path) -> list[str]:
    """Nivel 2 (PDF): negrita + centrado matemático vía bounding box."""
    secciones: list[str] = []

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise ExtractionError(f"No se pudo abrir el PDF para heurística visual '{pdf_path}': {e}") from e

    try:
        for page in doc:
            ancho_pagina = page.rect.width
            centro_pagina = ancho_pagina / 2
            blocks = page.get_text("dict")["blocks"]

            for b in blocks:
                if "lines" not in b:
                    continue
                for l in b["lines"]:
                    for s in l["spans"]:
                        texto = s["text"].strip()
                        if _es_ruido(texto):
                            continue

                        fuente = s["font"].lower()
                        es_negrita = "bold" in fuente or "black" in fuente

                        x0, x1 = s["bbox"][0], s["bbox"][2]
                        centro_texto = (x0 + x1) / 2
                        es_centrado = abs(centro_texto - centro_pagina) < _CENTER_TOLERANCE_PX

                        if es_negrita and es_centrado and texto not in secciones:
                            secciones.append(texto)
    finally:
        doc.close()

    return secciones


def _discover_docx_heuristic(docx_path: str | Path) -> list[str]:
    """Nivel 2 (DOCX): heading style, negrita o centrado."""
    secciones: list[str] = []

    try:
        doc = Document(docx_path)
    except Exception as e:
        raise ExtractionError(f"No se pudo abrir el DOCX para heurística visual '{docx_path}': {e}") from e

    for paragraph in doc.paragraphs:
        texto = paragraph.text.strip()
        if _es_ruido(texto):
            continue

        is_bold = any(run.bold for run in paragraph.runs if run.text.strip())
        is_heading_style = bool(paragraph.style and "heading" in paragraph.style.name.lower())
        is_centered = paragraph.alignment == 1  # WD_ALIGN_PARAGRAPH.CENTER

        if (is_bold or is_heading_style or is_centered) and texto not in secciones:
            secciones.append(texto)

    return secciones


def _discover_from_heuristic(file_path: str | Path) -> list[str]:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return _discover_pdf_heuristic(file_path)
    elif ext == ".docx":
        return _discover_docx_heuristic(file_path)
    raise ExtractionError(f"Formato de archivo no soportado: '{ext}'")


def discover_sections(
    file_path: str | Path,
    ai_provider: AIProvider | None = None,
) -> tuple[list[str], DiscoveryMethod]:
    """
    Cascada de auto-descubrimiento estructural sobre un documento de referencia:
    1) TOC/marcadores nativos (solo PDF), 2) heurística visual, 3) IA (fallback).

    No hay catálogo ni configuración por tipo de documento: la estructura
    esperada siempre se deriva del propio archivo que se está analizando.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        secciones = _discover_from_toc(file_path)
        if secciones:
            return secciones, DiscoveryMethod.TOC

    secciones = _discover_from_heuristic(file_path)
    if secciones:
        return secciones, DiscoveryMethod.HEURISTIC

    if ai_provider is not None:
        from core.structure_ai import discover_from_ai  # import diferido, ver paso 7

        secciones = discover_from_ai(file_path, ai_provider)
        if secciones:
            return secciones, DiscoveryMethod.AI

    return [], DiscoveryMethod.NONE


def score_structure(expected_sections: list[str], actual_text: str) -> tuple[list[str], list[str], float]:
    """Busca cada sección esperada en el texto actual y calcula el % de completitud."""
    encontradas: list[str] = []
    faltantes: list[str] = []

    for seccion in expected_sections:
        if re.search(re.escape(seccion), actual_text, re.IGNORECASE):
            encontradas.append(seccion)
        else:
            faltantes.append(seccion)

    total = len(expected_sections)
    score = (len(encontradas) / total) * 100 if total > 0 else 0.0
    return encontradas, faltantes, round(score, 2)
