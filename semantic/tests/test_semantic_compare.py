from extractors.pdf_extractor import PdfExtractor

from semantic.ai.document_ai_comparator import (
    DocumentAIComparator
)

def test_semantic_compare():

    extractor = PdfExtractor()

    ai_comparator = DocumentAIComparator()

    expected_text = extractor.extract_text(
        "documents/expected.pdf"
    )

    actual_text = extractor.extract_text(
        "documents/actual.pdf"
    )

    analysis = ai_comparator.compare(

        expected_text,
        actual_text
    )

    print("\n")
    print("=" * 50)
    print("ANALISIS SEMANTICO DE DOCUMENTO")
    print("=" * 50)

    print(analysis)

    assert analysis is not None