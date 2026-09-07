import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from core.ai.provider import AIProvider
from core.models import ComparisonSummary, SemanticDiscrepancy, Severity

# Tope de discrepancias por llamada: lotes más grandes arriesgan que la
# respuesta JSON del modelo se trunque antes de cubrir todos los índices.
# Los lotes se procesan en paralelo, así que documentos con muchas
# discrepancias siguen resolviéndose en el tiempo de un solo lote.
_BATCH_SIZE = 40

_SYSTEM_PROMPT = (
    "Eres un auditor de QA que clasifica una lista de discrepancias entre un documento esperado y uno "
    "actual. Cada discrepancia viene identificada por su índice numérico.\n\n"
    "CRITICO: la discrepancia altera montos, cifras, fechas límite, identificadores legales, "
    "obligaciones o cláusulas — cambia el significado o validez del documento.\n"
    "AVISO: cambio de redacción, formato o dato secundario que conviene revisar pero no invalida el documento.\n"
    "INFO: diferencia cosmética o irrelevante (espacios, mayúsculas, orden trivial de palabras).\n\n"
    "Responde EXCLUSIVAMENTE con un array JSON, un objeto por discrepancia, en el mismo orden y con la "
    "misma cantidad de elementos que la lista recibida, sin texto adicional ni bloques de código "
    "markdown. Formato de cada objeto:\n"
    '{"indice": <int>, "severidad": "<CRITICO|AVISO|INFO>", "razon": "<una frase breve>"}'
)

_FALLBACK_REASON = "No se pudo clasificar automáticamente; requiere revisión manual."
_JSON_ARRAY_PATTERN = re.compile(r"\[.*\]", re.DOTALL)


def _build_batch_prompt(discrepancies: list[SemanticDiscrepancy]) -> str:
    bloques = []
    for i, d in enumerate(discrepancies):
        bloques.append(
            f"[{i}]\n"
            f"Tipo de cambio: {d.change_type.value}\n"
            f'Texto esperado: "{d.expected_text}"\n'
            f'Texto actual: "{d.actual_text}"\n'
            f"Cambios internos detectados: {[c.description for c in d.internal_changes]}"
        )
    return "\n\n".join(bloques)


def _parse_batch_response(raw: str, count: int) -> dict[int, tuple[Severity, str]]:
    match = _JSON_ARRAY_PATTERN.search(raw)
    if not match:
        return {}

    try:
        data = json.loads(match.group(0))
    except (json.JSONDecodeError, ValueError):
        return {}

    if not isinstance(data, list):
        return {}

    resultados: dict[int, tuple[Severity, str]] = {}
    for item in data:
        if not isinstance(item, dict):
            continue
        try:
            idx = int(item.get("indice"))
        except (TypeError, ValueError):
            continue
        if not (0 <= idx < count):
            continue
        try:
            severidad = Severity(str(item.get("severidad", "")).strip().upper())
        except ValueError:
            continue
        razon = str(item.get("razon", "")).strip() or _FALLBACK_REASON
        resultados[idx] = (severidad, razon)

    return resultados


def _classify_batch(
    discrepancies: list[SemanticDiscrepancy],
    ai_provider: AIProvider,
) -> dict[int, tuple[Severity, str]]:
    """Clasifica un lote (índices relativos al lote) en una única llamada a la IA."""
    try:
        raw = ai_provider.generate_text(
            _build_batch_prompt(discrepancies),
            system_instruction=_SYSTEM_PROMPT,
            temperature=0.0,
        )
        return _parse_batch_response(raw, len(discrepancies))
    except Exception:
        return {}


def classify_discrepancies(
    discrepancies: list[SemanticDiscrepancy],
    ai_provider: AIProvider,
) -> list[SemanticDiscrepancy]:
    """
    Asigna severidad a todas las discrepancias agrupándolas en lotes de
    `_BATCH_SIZE` y resolviendo un lote por llamada a la IA (en vez de una
    llamada por discrepancia), con los lotes en paralelo para minimizar la
    latencia total.

    Nunca lanza excepción: si la IA falla, responde en un formato inesperado,
    o solo cubre parcialmente un lote, las discrepancias sin clasificar
    degradan individualmente a AVISO en vez de tumbar el pipeline de
    comparación.
    """
    if not discrepancies:
        return discrepancies

    lotes = [discrepancies[i : i + _BATCH_SIZE] for i in range(0, len(discrepancies), _BATCH_SIZE)]

    with ThreadPoolExecutor(max_workers=max(1, len(lotes))) as executor:
        resultados_por_lote = list(executor.map(lambda lote: _classify_batch(lote, ai_provider), lotes))

    for lote, clasificaciones in zip(lotes, resultados_por_lote):
        for i, d in enumerate(lote):
            d.severity, d.severity_reasoning = clasificaciones.get(i, (Severity.AVISO, _FALLBACK_REASON))

    return discrepancies


def build_summary(discrepancies: list[SemanticDiscrepancy]) -> ComparisonSummary:
    critical = sum(1 for d in discrepancies if d.severity == Severity.CRITICO)
    warning = sum(1 for d in discrepancies if d.severity == Severity.AVISO)
    info = sum(1 for d in discrepancies if d.severity == Severity.INFO)

    return ComparisonSummary(
        status="FAILED" if critical > 0 else "PASSED",
        total_discrepancies=len(discrepancies),
        critical=critical,
        warning=warning,
        info=info,
        generated_at=datetime.now(),
    )
