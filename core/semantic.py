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


_BRACKET_PLACEHOLDER_PATTERN = re.compile(r"\[[^\[\]]*\]")
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
) -> tuple[list[InternalChange], str]:
    """
    Diff palabra por palabra dentro de un bloque, ya normalizado. Se
    distinguen tres categorías (ver ChangeKind): cambios reales
    ("Cambió"/"Eliminó"/"Añadió"), datos variables rellenados (marcador
    '[ ]' o '[Etiqueta]' -> dato real) y montos rellenados (marcador '____' -> monto real),
    ya que estas dos últimas representan el llenado esperado de una
    plantilla, no necesariamente un problema. Si `hide_variable_fills` es
    True, esas dos categorías se omiten por completo del desglose.

    `monetary_noise_tokens` permite reconocer montos donde el marcador de
    guiones bajos queda mezclado con texto de formato fijo específico del
    documento (p.ej. ["M.N.", "MN"] para pesos mexicanos) — sin asumir
    ninguno por defecto, ya que ese formato varía por tipo de documento.

    Además del desglose, devuelve el texto esperado "visible": si
    `hide_variable_fills` es True, los marcadores de plantilla se
    sustituyen ahí mismo por el dato realmente capturado en el documento
    actual. Así, quien resalte diferencias palabra por palabra a partir de
    este texto (tarjetas antes/después, overlay sobre el PDF) ya no
    encuentra una diferencia en esos tramos y no los marca como
    discrepancia — consistente con que el desglose tampoco los reporta.
    """
    esp_norm = _normalizar_texto_bloque(texto_esperado)
    act_norm = _normalizar_texto_bloque(texto_actual)

    palabras_esp = esp_norm.split()
    palabras_act = act_norm.split()
    palabras_esp_visibles = list(palabras_esp)
    offset = 0

    matcher = difflib.SequenceMatcher(None, palabras_esp, palabras_act, autojunk=False)
    desglose: list[InternalChange] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        sub_esperado = " ".join(palabras_esp[i1:i2])
        sub_actual = " ".join(palabras_act[j1:j2])

        if tag == "replace":
            es_variable = _es_relleno_de_marcador(sub_esperado, _BRACKET_PLACEHOLDER_PATTERN)
            es_monto = not es_variable and _es_relleno_de_marcador(
                sub_esperado, _MONTO_PLACEHOLDER_PATTERN, monetary_noise_tokens
            )

            if es_variable or es_monto:
                if hide_variable_fills:
                    reemplazo = palabras_act[j1:j2]
                    palabras_esp_visibles[i1 + offset : i2 + offset] = reemplazo
                    offset += len(reemplazo) - (i2 - i1)
                elif es_variable:
                    desglose.append(
                        InternalChange(ChangeKind.VARIABLE_FILL, f'Dato variable rellenado: "{sub_actual}"')
                    )
                else:
                    desglose.append(InternalChange(ChangeKind.MONTO_FILL, f'Monto rellenado: "{sub_actual}"'))
            else:
                desglose.append(
                    InternalChange(ChangeKind.REAL, f'Cambió: "{sub_esperado}" por "{sub_actual}"')
                )
        elif tag == "delete":
            desglose.append(InternalChange(ChangeKind.REAL, f'Eliminó: "{sub_esperado}"'))
        elif tag == "insert":
            desglose.append(InternalChange(ChangeKind.REAL, f'Añadió: "{sub_actual}"'))

    return desglose, " ".join(palabras_esp_visibles)


_LONGITUD_MINIMA_ETIQUETA = 5  # evita que placeholders cortos ("$", "[ ]", "1", "____") disparen el corte


def _es_etiqueta_util(linea: str) -> bool:
    """
    Filtra líneas demasiado cortas o genéricas (números sueltos, símbolos,
    marcadores de plantilla) para no usarlas como ancla de reordenamiento —
    solo interesan líneas con contenido textual propio (p.ej. una etiqueta
    o encabezado), no un placeholder o dato suelto que podría repetirse sin
    identificar realmente un bloque.
    """
    texto = re.sub(r"[^\w]", "", linea, flags=re.UNICODE)
    return len(texto) >= _LONGITUD_MINIMA_ETIQUETA and not texto.isdigit()


def _reasignar_contenido_desplazado(
    opcodes: list[tuple[str, int, int, int, int]],
    txt_esperado: list[str],
    txt_actual: list[str],
) -> list[tuple[str, list[str], list[str]]]:
    """
    Cuando dos secciones estructuralmente similares intercambian su orden
    entre el documento esperado y el actual (p.ej. dos bloques de firma que
    se intercambiaron de posición), el diff por posición de difflib puede
    terminar mezclando contenido del bloque siguiente dentro del bloque
    anterior: como el documento actual presenta antes lo que en la
    plantilla viene después, el rango "actual" de un bloque termina
    incluyendo la etiqueta y el contenido que en realidad pertenecen al
    bloque que sigue.

    Esta función detecta esos casos buscando, dentro del rango actual de
    cada bloque no-'equal', una línea que coincide con alguna línea del
    bloque esperado INMEDIATAMENTE siguiente — y ahí recorta, moviendo esa
    cola al bloque siguiente. Es intencionalmente conservadora: solo mira
    un bloque hacia adelante y requiere una coincidencia textual exacta.

    Devuelve bloques ya materializados (tag, líneas_esperadas,
    líneas_actuales) en vez de únicamente los rangos de índices de difflib,
    porque una vez reasignado el contenido ya no corresponde a un solo
    rango contiguo del documento actual.
    """
    bloques = [
        (tag, list(txt_esperado[i1:i2]), list(txt_actual[j1:j2]))
        for tag, i1, i2, j1, j2 in opcodes
        if tag != "equal"
    ]

    for idx in range(len(bloques) - 1):
        tag, exp_lineas, act_lineas = bloques[idx]
        if not act_lineas:
            continue

        _, exp_siguiente, _ = bloques[idx + 1]
        etiquetas_siguientes = {l for l in exp_siguiente if _es_etiqueta_util(l)}
        if not etiquetas_siguientes:
            continue

        punto_corte = next(
            (i for i, linea in enumerate(act_lineas) if linea in etiquetas_siguientes),
            None,
        )
        if punto_corte is None:
            continue

        cola = act_lineas[punto_corte:]
        bloques[idx] = (tag, exp_lineas, act_lineas[:punto_corte])
        tag_sig, exp_sig, act_sig = bloques[idx + 1]
        bloques[idx + 1] = (tag_sig, exp_sig, cola + act_sig)

    return bloques


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
    marcador de plantilla ('[ ]', '[Etiqueta]' o '____') se muestran etiquetados como tal
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
    opcodes = matcher.get_opcodes()
    bloques = _reasignar_contenido_desplazado(opcodes, txt_esperado, txt_actual)
    indices_j1 = [j1 for tag, _, _, j1, _ in opcodes if tag != "equal"]

    discrepancias: list[SemanticDiscrepancy] = []

    for (tag, exp_lineas, act_lineas), j1 in zip(bloques, indices_j1):
        bloque_esperado = " ".join(exp_lineas).strip()
        bloque_actual = " ".join(act_lineas).strip()

        if not bloque_esperado and not bloque_actual:
            continue

        if _extraer_esqueleto_fijo(bloque_esperado, phrases) == _extraer_esqueleto_fijo(bloque_actual, phrases):
            continue  # misma plantilla, solo cambiaron datos dinámicos

        cambios_internos, bloque_esperado_visible = _desmenuzar_cambios_bloque(
            bloque_esperado, bloque_actual, hide_variable_fills, monetary_noise_tokens
        )
        if not cambios_internos:
            continue  # tras normalizar, no había diferencia real

        idx_linea = j1 if j1 < len(actual_lines_map) else len(actual_lines_map) - 1
        ubicacion = actual_lines_map[idx_linea][1] if actual_lines_map else 1

        # el recorte de _reasignar_contenido_desplazado puede dejar un lado
        # vacío aunque el opcode original fuera 'replace' — el tipo de
        # cambio debe reflejar eso (faltante/añadido) y no quedar como
        # "modified" con un lado en blanco.
        if bloque_actual and not bloque_esperado:
            tipo_cambio = ChangeType.ADDED
        elif bloque_esperado and not bloque_actual:
            tipo_cambio = ChangeType.MISSING
        else:
            tipo_cambio = _TAG_TO_CHANGE_TYPE[tag]

        discrepancias.append(
            SemanticDiscrepancy(
                location=ubicacion,
                change_type=tipo_cambio,
                expected_text=bloque_esperado_visible if hide_variable_fills else bloque_esperado,
                actual_text=bloque_actual,
                internal_changes=cambios_internos,
            )
        )

    return SemanticResult(
        matches=len(discrepancias) == 0,
        details=f"Se detectaron {len(discrepancias)} bloques con discrepancias.",
        discrepancies=discrepancias,
    )
