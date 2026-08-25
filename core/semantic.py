import difflib
import re

from core.extraction import LineMap
from core.models import ChangeType, SemanticDiscrepancy, SemanticResult

_TAG_TO_CHANGE_TYPE = {
    "replace": ChangeType.MODIFIED,
    "delete": ChangeType.MISSING,
    "insert": ChangeType.ADDED,
}


def _normalizar_texto_bloque(texto: str) -> str:
    """Normaliza comillas curvas y espacios para comparar de forma consistente."""
    if not texto:
        return ""
    texto = texto.replace("“", '"').replace("”", '"')
    texto = texto.replace("[LINEA_OMITIDA]", "")
    return " ".join(texto.split())


def _extraer_esqueleto_fijo(texto: str, ignore_phrases: list[str]) -> list[str]:
    """
    Devuelve las palabras estáticas (no dinámicas) de un bloque, ordenadas,
    para poder detectar cuando dos bloques solo difieren en datos variables
    (montos, fechas, IDs) que comparten la misma plantilla.
    """
    if not texto:
        return []

    t = texto.lower()
    t = t.replace("[linea_omitida]", "")
    for frase in ignore_phrases:
        t = t.replace(frase.lower(), "")

    t = re.sub(r"\[\s*\]", " ", t)
    t = t.replace("[", " ").replace("]", " ")

    palabras_estaticas = []
    for p in t.split():
        p_limpia = re.sub(r"^[^\w\s]|[^\w\s]$", "", p)
        if not p_limpia:
            continue
        if p_limpia.isdigit():
            continue
        if p_limpia == "$" or p_limpia.startswith("_"):
            continue
        if re.match(r"^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]+$", p_limpia):
            continue  # IDs alfanuméricos tipo hash/código
        palabras_estaticas.append(p_limpia)

    palabras_estaticas.sort()
    return palabras_estaticas


def _desmenuzar_cambios_bloque(texto_esperado: str, texto_actual: str) -> list[str]:
    """Diff palabra por palabra dentro de un bloque, ya normalizado."""
    esp_norm = _normalizar_texto_bloque(texto_esperado)
    act_norm = _normalizar_texto_bloque(texto_actual)

    palabras_esp = esp_norm.split()
    palabras_act = act_norm.split()

    matcher = difflib.SequenceMatcher(None, palabras_esp, palabras_act, autojunk=False)
    desglose = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        sub_esperado = " ".join(palabras_esp[i1:i2])
        sub_actual = " ".join(palabras_act[j1:j2])

        if tag == "replace":
            desglose.append(f'Cambió: "{sub_esperado}" por "{sub_actual}"')
        elif tag == "delete":
            desglose.append(f'Eliminó: "{sub_esperado}"')
        elif tag == "insert":
            desglose.append(f'Añadió: "{sub_actual}"')

    return desglose


def diff_documents(
    actual_lines_map: LineMap,
    expected_lines_map: LineMap,
    ignore_phrases: list[str] | None = None,
) -> SemanticResult:
    """
    Diff determinista por bloques entre dos documentos ya extraídos
    (ver core.extraction.extract_text_with_page_mapping).
    """
    phrases = ignore_phrases or []

    txt_esperado = [item[0] for item in expected_lines_map]
    txt_actual = [item[0] for item in actual_lines_map]

    matcher = difflib.SequenceMatcher(None, txt_esperado, txt_actual, autojunk=False)
    discrepancias: list[SemanticDiscrepancy] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        bloque_esperado = " ".join(txt_esperado[i1:i2]).strip()
        bloque_actual = " ".join(txt_actual[j1:j2]).strip()

        if not bloque_esperado and not bloque_actual:
            continue

        if _extraer_esqueleto_fijo(bloque_esperado, phrases) == _extraer_esqueleto_fijo(bloque_actual, phrases):
            continue  # misma plantilla, solo cambiaron datos dinámicos

        cambios_internos = _desmenuzar_cambios_bloque(bloque_esperado, bloque_actual)
        if not cambios_internos:
            continue  # tras normalizar, no había diferencia real

        idx_linea = j1 if j1 < len(actual_lines_map) else len(actual_lines_map) - 1
        ubicacion = actual_lines_map[idx_linea][1] if actual_lines_map else 1

        discrepancias.append(
            SemanticDiscrepancy(
                location=ubicacion,
                change_type=_TAG_TO_CHANGE_TYPE[tag],
                expected_text=bloque_esperado,
                actual_text=bloque_actual,
                internal_changes=cambios_internos,
            )
        )

    return SemanticResult(
        matches=len(discrepancias) == 0,
        details=f"Se detectaron {len(discrepancias)} bloques con discrepancias.",
        discrepancies=discrepancias,
    )
