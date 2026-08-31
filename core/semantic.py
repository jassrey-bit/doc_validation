import difflib
import re

from core.extraction import LineMap
from core.models import ChangeKind, ChangeType, InternalChange, SemanticDiscrepancy, SemanticResult

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


_BRACKET_PLACEHOLDER_PATTERN = re.compile(r"\[\s*\]")
_MONTO_PLACEHOLDER_PATTERN = re.compile(r"_+")


def _es_relleno_de_marcador(
    sub_esperado: str,
    patron_marcador: re.Pattern,
    ruido_conocido: list[str] | None = None,
) -> bool:
    """
    True si el lado esperado de un cambio es únicamente el marcador dado
    (corchetes o guiones bajos) más puntuación/símbolos, números sueltos y/o
    tokens de ruido conocidos (p.ej. abreviaturas de moneda como 'M.N.') —
    es decir: un campo de plantilla que se espera que se llene con datos
    reales al generar el documento actual.

    Los números se tratan siempre como dato dinámico (igual que en la
    comparación de "misma plantilla" a nivel de bloque), ya que un monto
    puede quedar mezclado con el marcador en el mismo token. `ruido_conocido`
    permite indicar tokens de formato específicos del documento (sin
    asumir ninguno por defecto) que también deben ignorarse al decidir si
    lo que sobra es texto real. Si después de limpiar todo eso queda
    alguna letra, ya no se considera un relleno puro.
    """
    if not patron_marcador.search(sub_esperado):
        return False
    sin_marcador = patron_marcador.sub("", sub_esperado)
    sin_marcador_ni_digitos = re.sub(r"\d+", "", sin_marcador)
    for token in ruido_conocido or []:
        sin_marcador_ni_digitos = re.sub(re.escape(token), "", sin_marcador_ni_digitos, flags=re.IGNORECASE)
    return re.search(r"[a-zA-Z]", sin_marcador_ni_digitos) is None


def _desmenuzar_cambios_bloque(
    texto_esperado: str,
    texto_actual: str,
    hide_variable_fills: bool = False,
    monetary_noise_tokens: list[str] | None = None,
) -> list[InternalChange]:
    """
    Diff palabra por palabra dentro de un bloque, ya normalizado. Se
    distinguen tres categorías (ver ChangeKind): cambios reales
    ("Cambió"/"Eliminó"/"Añadió"), datos variables rellenados (marcador
    '[ ]' -> dato real) y montos rellenados (marcador '____' -> monto real),
    ya que estas dos últimas representan el llenado esperado de una
    plantilla, no necesariamente un problema. Si `hide_variable_fills` es
    True, esas dos categorías se omiten por completo del desglose.

    `monetary_noise_tokens` permite reconocer montos donde el marcador de
    guiones bajos queda mezclado con texto de formato fijo específico del
    documento (p.ej. ["M.N.", "MN"] para pesos mexicanos) — sin asumir
    ninguno por defecto, ya que ese formato varía por tipo de documento.
    """
    esp_norm = _normalizar_texto_bloque(texto_esperado)
    act_norm = _normalizar_texto_bloque(texto_actual)

    palabras_esp = esp_norm.split()
    palabras_act = act_norm.split()

    matcher = difflib.SequenceMatcher(None, palabras_esp, palabras_act, autojunk=False)
    desglose: list[InternalChange] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        sub_esperado = " ".join(palabras_esp[i1:i2])
        sub_actual = " ".join(palabras_act[j1:j2])

        if tag == "replace":
            if _es_relleno_de_marcador(sub_esperado, _BRACKET_PLACEHOLDER_PATTERN):
                if not hide_variable_fills:
                    desglose.append(
                        InternalChange(ChangeKind.VARIABLE_FILL, f'Dato variable rellenado: "{sub_actual}"')
                    )
            elif _es_relleno_de_marcador(sub_esperado, _MONTO_PLACEHOLDER_PATTERN, monetary_noise_tokens):
                if not hide_variable_fills:
                    desglose.append(InternalChange(ChangeKind.MONTO_FILL, f'Monto rellenado: "{sub_actual}"'))
            else:
                desglose.append(
                    InternalChange(ChangeKind.REAL, f'Cambió: "{sub_esperado}" por "{sub_actual}"')
                )
        elif tag == "delete":
            desglose.append(InternalChange(ChangeKind.REAL, f'Eliminó: "{sub_esperado}"'))
        elif tag == "insert":
            desglose.append(InternalChange(ChangeKind.REAL, f'Añadió: "{sub_actual}"'))

    return desglose


def diff_documents(
    actual_lines_map: LineMap,
    expected_lines_map: LineMap,
    ignore_phrases: list[str] | None = None,
    hide_variable_fills: bool = False,
    monetary_noise_tokens: list[str] | None = None,
) -> SemanticResult:
    """
    Diff determinista por bloques entre dos documentos ya extraídos
    (ver core.extraction.extract_text_with_page_mapping).

    `hide_variable_fills` controla si los cambios que solo llenan un
    marcador de plantilla ('[ ]' o '____') se muestran etiquetados como tal
    (default) u se ocultan por completo del desglose interno.

    `monetary_noise_tokens` es una lista opcional de tokens de formato de
    moneda propios del documento (p.ej. ["M.N.", "MN"]) que se ignoran al
    decidir si un blanco de guiones bajos es un monto rellenado — no hay
    ningún token asumido por defecto.
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

        cambios_internos = _desmenuzar_cambios_bloque(
            bloque_esperado, bloque_actual, hide_variable_fills, monetary_noise_tokens
        )
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
