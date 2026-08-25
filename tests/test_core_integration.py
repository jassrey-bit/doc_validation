import os

import pytest

from core import GeminiProvider, compare_documents
from reports.console_reporter import ConsoleReporter
from reports.html_reporter import HtmlReporter

pytestmark = pytest.mark.integration

ACTUAL = "documents/actual.pdf"
EXPECTED = "documents/expected.docx"


@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="Requiere GEMINI_API_KEY configurada")
def test_compare_actual_vs_expected_full_pipeline():
    provider = GeminiProvider()

    result = compare_documents(ACTUAL, EXPECTED, ai_provider=provider)

    ConsoleReporter().print_report(result)
    HtmlReporter().generate_report(result)

    assert result.structural.score >= 0
    assert result.summary.status in ("PASSED", "FAILED")
    assert result.summary.total_discrepancies == len(result.semantic.discrepancies)

    for d in result.semantic.discrepancies:
        assert d.severity is not None

    # El análisis visual depende de servicios externos (LibreOffice, Gemini);
    # si no está disponible en este entorno, debe degradar con un motivo claro,
    # nunca tumbar el resto de la comparación.
    if result.visual is not None and not result.visual.available:
        assert result.visual.error
