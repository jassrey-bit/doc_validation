from extractors.pdf_extractor import PdfExtractor
from structured.comparators.pdf_comparator import PdfComparator
from structured.parsers.contract_parser import ContractParser
from reports.console_reporter import ConsoleReporter
from structured.normalizers.data_normalizer import DataNormalizer
from reports.html_reporter import HtmlReporter
from structured.ai.structured_ai_analyzer import (
    StructuredAIAnalyzer
)
from structured.reporting.report_builder import (
    ReportBuilder
)

def test_compare_pdfs():

    extractor = PdfExtractor()
    parser = ContractParser()
    comparator = PdfComparator()
    reporter = ConsoleReporter()
    normalizer = DataNormalizer()
    html_reporter = HtmlReporter()
    ai_analyzer = StructuredAIAnalyzer()
    reporter_builder = ReportBuilder()

    expected_text = extractor.extract_text(
        "documents/expected.pdf"
    )

    actual_text = extractor.extract_text(
        "documents/actual.pdf"
    )

    expected_data = parser.parse(expected_text)
    actual_data = parser.parse(actual_text)

    expected_data = normalizer.normalize(expected_data)
    actual_data = normalizer.normalize(actual_data)

    differences = comparator.compare(
        expected_data,
        actual_data
    )

    summary = reporter_builder.build_summary(
        differences
    )

    reporter.print_report(
        differences
    )

    analysis = ai_analyzer.analyze(
        differences
    )

    html_reporter.generate_report(
        differences,
        summary,
        analysis
    )

    critical_differences = [

        d for d in differences

        if d["severity"] == "CRITICO"
    ]

    print("\n")
    print("=" * 50)
    print("ANALISIS ESTRUCTURADO")
    print("=" * 50)

    print(analysis)

    assert len(critical_differences) == 0