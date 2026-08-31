import shutil
import tempfile

from core.ai.provider import AIProvider
from core.exceptions import AIProviderError, VisualUnavailableError
from core.extraction import extract_text_with_page_mapping
from core.models import ComparisonResult, StructuralResult, VisualVerdict
from core.semantic import diff_documents
from core.severity import build_summary, classify_discrepancies
from core.structure import discover_sections, score_structure
from core.visual import convert_document_to_images

_VISUAL_SYSTEM_PROMPT = (
    "Eres un Ingeniero de QA Automation Senior y Auditor de Calidad Visual de Documentos.\n"
    "Se te proporcionan las imágenes de dos documentos:\n"
    "- Documento ESPERADO (Template/Expected): la referencia base correcta.\n"
    "- Documento ACTUAL (Generated/Actual): el documento generado bajo prueba.\n\n"
    "TU OBJETIVO DE QA:\n"
    "1. Inicia tu respuesta estrictamente con [STATUS: PASSED] o [STATUS: FAILED].\n"
    "2. Compara visualmente el documento ACTUAL contra el ESPERADO.\n"
    "3. Detecta diferencias de formato visual: desalineaciones de tablas, cambios de tipografía/"
    "negritas, márgenes alterados, imágenes/logos movidos o faltantes, y saltos de página.\n"
    "4. Entrega un resumen ejecutivo: Estado, Severidad (Crítica/Alta/Media) y Hallazgos Visuales Clave."
)


def _run_visual_analysis(actual_path: str, expected_path: str, ai_provider: AIProvider | None) -> VisualVerdict:
    if ai_provider is None:
        return VisualVerdict(available=False, error="Análisis visual deshabilitado: no se proporcionó un proveedor de IA.")

    tmp_dir = tempfile.mkdtemp(prefix="doc_validation_")
    try:
        actual_images = convert_document_to_images(actual_path, tmp_dir)
        expected_images = convert_document_to_images(expected_path, tmp_dir)

        prompt = (
            "Compara las imágenes adjuntas de ambos documentos y genera el dictamen de QA "
            "según las instrucciones del sistema."
        )
        raw = ai_provider.generate_multimodal(
            prompt,
            expected_images + actual_images,
            system_instruction=_VISUAL_SYSTEM_PROMPT,
        )

        normalized = raw.upper().replace(" ", "")
        if "[STATUS:FAILED]" in normalized:
            status = "FAILED"
        elif "[STATUS:PASSED]" in normalized:
            status = "PASSED"
        else:
            status = None
        return VisualVerdict(available=True, status=status, findings=raw)

    except (VisualUnavailableError, AIProviderError) as e:
        return VisualVerdict(available=False, error=str(e))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def compare_documents(
    actual_path: str,
    expected_path: str,
    *,
    ai_provider: AIProvider | None = None,
    enable_visual: bool = True,
    ignore_line_patterns: list[str] | None = None,
    ignore_skeleton_phrases: list[str] | None = None,
    hide_variable_fills: bool = False,
    monetary_noise_tokens: list[str] | None = None,
) -> ComparisonResult:
    """
    Compara dos documentos (PDF y/o DOCX, cualquier combinación) y devuelve un
    resultado unificado: estructura, diferencias semánticas con severidad, y
    (si hay proveedor de IA y `enable_visual=True`) un veredicto visual.

    La estructura esperada se autodescubre del propio `expected_path` en cada
    corrida — no depende de ningún catálogo por tipo de documento.

    `hide_variable_fills` oculta del desglose los cambios que solo llenan un
    marcador de plantilla ('[ ]' o '____') con un dato real — útil para un
    reporte más limpio cuando esos rellenos no son de interés para la
    revisión.

    `monetary_noise_tokens` reconoce montos rellenados aunque el blanco de
    guiones bajos quede mezclado con texto de formato fijo específico del
    documento (p.ej. ["M.N.", "MN"] para pesos mexicanos) — no asume ningún
    formato de moneda por defecto.
    """
    actual_text, actual_lines_map = extract_text_with_page_mapping(actual_path, ignore_line_patterns)
    expected_text, expected_lines_map = extract_text_with_page_mapping(expected_path, ignore_line_patterns)

    expected_sections, discovery_method = discover_sections(expected_path, ai_provider=ai_provider)
    found_sections, missing_sections, score = score_structure(expected_sections, actual_text)
    structural = StructuralResult(
        expected_sections=expected_sections,
        found_sections=found_sections,
        missing_sections=missing_sections,
        score=score,
        discovery_method=discovery_method,
    )

    semantic_result = diff_documents(
        actual_lines_map, expected_lines_map, ignore_skeleton_phrases, hide_variable_fills, monetary_noise_tokens
    )

    if semantic_result.discrepancies and ai_provider is not None:
        classify_discrepancies(semantic_result.discrepancies, ai_provider)

    summary = build_summary(semantic_result.discrepancies)

    visual = _run_visual_analysis(actual_path, expected_path, ai_provider) if enable_visual else None

    return ComparisonResult(
        actual_path=str(actual_path),
        expected_path=str(expected_path),
        structural=structural,
        semantic=semantic_result,
        visual=visual,
        summary=summary,
    )
