import re
from datetime import datetime

from core.ai.provider import AIProvider
from core.models import ComparisonSummary, SemanticDiscrepancy, Severity

_SYSTEM_PROMPT = (
    "Eres un auditor de QA que clasifica discrepancias entre un documento esperado y uno actual. "
    "Para cada discrepancia responde EXCLUSIVAMENTE en este formato, sin texto adicional:\n"
    "SEVERIDAD: <CRITICO|AVISO|INFO>\n"
    "RAZON: <una frase breve>\n\n"
    "CRITICO: la discrepancia altera montos, cifras, fechas límite, identificadores legales, "
    "obligaciones o cláusulas — cambia el significado o validez del documento.\n"
    "AVISO: cambio de redacción, formato o dato secundario que conviene revisar pero no invalida el documento.\n"
    "INFO: diferencia cosmética o irrelevante (espacios, mayúsculas, orden trivial de palabras)."
)

_RESPONSE_PATTERN = re.compile(
    r"SEVERIDAD:\s*(CRITICO|AVISO|INFO).*?RAZON:\s*(.+)",
    re.IGNORECASE | re.DOTALL,
)

_FALLBACK_REASON = "No se pudo clasificar automáticamente; requiere revisión manual."


def _build_prompt(discrepancy: SemanticDiscrepancy) -> str:
    return (
        f"Tipo de cambio: {discrepancy.change_type.value}\n"
        f'Texto esperado: "{discrepancy.expected_text}"\n'
        f'Texto actual: "{discrepancy.actual_text}"\n'
        f"Cambios internos detectados: {[c.description for c in discrepancy.internal_changes]}"
    )


def _parse_severity_response(raw: str) -> tuple[Severity, str]:
    match = _RESPONSE_PATTERN.search(raw)
    if not match:
        return Severity.AVISO, _FALLBACK_REASON

    severidad_str = match.group(1).strip().upper()
    razon = match.group(2).strip().splitlines()[0].strip()

    try:
        return Severity(severidad_str), razon
    except ValueError:
        return Severity.AVISO, _FALLBACK_REASON


def assign_severity(discrepancy: SemanticDiscrepancy, ai_provider: AIProvider) -> tuple[Severity, str]:
    """
    Clasifica la severidad de una discrepancia vía IA. Nunca lanza excepción:
    si la IA falla o responde en un formato inesperado, degrada a AVISO con
    una razón explícita en vez de tumbar el pipeline de comparación.
    """
    try:
        raw = ai_provider.generate_text(
            _build_prompt(discrepancy),
            system_instruction=_SYSTEM_PROMPT,
            temperature=0.0,
        )
    except Exception:
        return Severity.AVISO, _FALLBACK_REASON

    return _parse_severity_response(raw)


def classify_discrepancies(
    discrepancies: list[SemanticDiscrepancy],
    ai_provider: AIProvider,
) -> list[SemanticDiscrepancy]:
    """Asigna severidad a cada discrepancia en el lugar y las devuelve."""
    for d in discrepancies:
        d.severity, d.severity_reasoning = assign_severity(d, ai_provider)
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
