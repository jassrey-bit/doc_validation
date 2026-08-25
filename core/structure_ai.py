import json
import re
from pathlib import Path

from core.ai.provider import AIProvider
from core.extraction import extract_text_with_page_mapping

_SYSTEM_PROMPT = (
    "Eres un extractor de metadatos de alta precisión para documentos legales y financieros. "
    "Tu única tarea es identificar los títulos de secciones, capítulos o apartados principales "
    "presentes en el texto, extraídos EXACTAMENTE como aparecen escritos. "
    "Ignora párrafos de contenido común y datos variables entre corchetes ([ ]). "
    "Responde EXCLUSIVAMENTE con un array JSON de strings, sin texto adicional ni bloques de "
    'código markdown. Ejemplo: ["TÍTULO UNO", "TÍTULO DOS"]'
)

_MAX_CHARS = 7000
_JSON_ARRAY_PATTERN = re.compile(r"\[.*\]", re.DOTALL)


def discover_from_ai(file_path: str | Path, ai_provider: AIProvider) -> list[str]:
    """
    Último recurso de la cascada de auto-descubrimiento estructural: cuando
    el documento no tiene TOC nativo ni marcas visuales claras (negrita +
    centrado / heading), se le pide a la IA que identifique los títulos.
    """
    texto, _ = extract_text_with_page_mapping(file_path)
    if not texto.strip():
        return []

    try:
        raw = ai_provider.generate_text(
            texto[:_MAX_CHARS],
            system_instruction=_SYSTEM_PROMPT,
            temperature=0.0,
        )
    except Exception:
        return []

    match = _JSON_ARRAY_PATTERN.search(raw)
    if not match:
        return []

    try:
        data = json.loads(match.group(0))
    except (json.JSONDecodeError, ValueError):
        return []

    if not isinstance(data, list):
        return []

    return [str(item).strip() for item in data if str(item).strip()]
