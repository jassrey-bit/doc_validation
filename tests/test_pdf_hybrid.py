# # tests/test_pdf_hybrid.py

# import json
# from hybrid.funsion_engine import run_pdf_validation

# def test_mi_primer_analisis_pdf():
#     # Ruta al PDF relativo a donde estás parado (la raíz del proyecto)
#     ruta_pdf = "documents/actual.pdf"
    
#     # Ejecutamos el motor
#     resultado = run_pdf_validation(ruta_pdf)
    
#     # Imprimimos en consola para ver el JSON estructurado exactamente como lo querías
#     print("\n\n================ RESULTADO DEL PARSEO ================")
#     print(json.dumps(resultado, indent=4, ensure_ascii=False))
#     print("======================================================\n")
    
#     # Aserción de control de calidad
#     assert "error" not in resultado, f"Hubo un error en el pipeline: {resultado.get('error')}"
#     assert resultado["puntuacion_estructura"] == 100.0, "La estructura del PDF no cumple al 100%"

# # tests/test_pdf_hybrid.py
# import json
# from hybrid.funsion_engine import run_pdf_validation

# def test_mi_primer_analisis_pdf():
#     actual = "documents/actual.pdf"
#     expected = "documents/expected.pdf"
    
#     resultado = run_pdf_validation(actual, expected)
    
#     print("\n\n================ RESULTADO FINAL DEL PIPELINE ================")
#     print(json.dumps(resultado, indent=4, ensure_ascii=False))
#     print("==============================================================\n")
    
#     assert resultado["puntuacion_estructura"] == 100.0
#     # Verificamos que ninguna sección analizada por la IA tenga discrepancias graves
#     for seccion, reporte in resultado["analisis_contenido_ia"].items():
#         assert reporte["coincide"] is True, f"Discrepancia en {seccion}: {reporte['detalles']}"


# # tests/test_pdf_hybrid.py
# import json
# from hybrid.funsion_engine import run_pdf_validation

# def test_mi_primer_analisis_pdf():
#     actual = "documents/actual.pdf"
#     expected = "documents/expected.pdf"
    
#     # Configuramos para usar minicpm-v tanto en la visión como en el texto
#     resultado = run_pdf_validation(actual, expected, model_vision="minicpm-v", model_text="minicpm-v")
    
#     print("\n\n================ RESULTADO FINAL DEL PIPELINE ================")
#     print(json.dumps(resultado, indent=4, ensure_ascii=False))
#     print("==============================================================\n")
    
#     assert "error" not in resultado, f"Error: {resultado.get('error')}"
#     assert resultado["puntuacion_estructura"] > 0

# # tests/test_pdf_hybrid.py
# import json
# from hybrid.funsion_engine import run_pdf_validation

# def test_mi_primer_analisis_pdf():
#     actual = "documents/actual.pdf"
#     expected = "documents/expected.pdf"
    
#     # Ejecución apuntando a tu modelo de texto local estable
#     resultado = run_pdf_validation(actual, expected, model_text="deepseek-r1:7b")
    
#     print("\n\n================ RESULTADO FINAL DEL PIPELINE ================")
#     print(json.dumps(resultado, indent=4, ensure_ascii=False))
#     print("==============================================================\n")
    
#     assert "error" not in resultado, f"Error en el motor: {resultado.get('error')}"
#     assert resultado["puntuacion_estructura"] > 0


# # tests/test_pdf_hybrid.py
# import json
# from hybrid.funsion_engine import run_pdf_validation

# def test_mi_primer_analisis_pdf():
#     actual = "documents/actual.pdf"
#     expected = "documents/expected.pdf"
    
#     resultado = run_pdf_validation(actual, expected)
    
#     print("\n\n================ RESULTADO DEL ANALISIS ================")
#     print(json.dumps(resultado, indent=4, ensure_ascii=False))
#     print("==============================================================\n")
    
#     assert "error" not in resultado
#     assert resultado["puntuacion_estructura"] == 100.0

# # tests/test_pdf_hybrid.py
# import os
# from hybrid.funsion_engine import run_pdf_validation

# def test_mi_primer_analisis_pdf():
#     # Obtiene la raíz del proyecto dinámicamente
#     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
#     # CORRECCIÓN: Apuntar al archivo real .docx que tienes en tu carpeta
#     actual = os.path.join(base_dir, "documents", "actual.pdf")
#     expected = os.path.join(base_dir, "documents", "expected.docx")
    
#     # Ejecuta la validación universal
#     resultado = run_pdf_validation(actual, expected)
    
#     # Imprimir el resultado detallado en la consola
#     import json
#     print("\n================ RESULTADO DE LA AUDITORÍA ================")
#     print(json.dumps(resultado, indent=4, ensure_ascii=False))
    
#     # Tu aserción de control
#     assert resultado["resultado_auditoria_texto"]["coincide"] is False

# # tests/test_pdf_hybrid.py
# import os
# import json
# from hybrid.funsion_engine import run_pdf_validation

# def test_mi_primer_analisis_pdf():
#     # Obtiene la raíz del proyecto dinámicamente
#     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
#     # Apuntar a los archivos reales en tu carpeta
#     actual = os.path.join(base_dir, "documents", "actual.pdf")
#     expected = os.path.join(base_dir, "documents", "expected.docx")
    
#     # Ejecuta la validación universal (que ahora incluye la IA)
#     resultado = run_pdf_validation(actual, expected)
    
#     # Imprimir el resultado detallado en la consola
#     print("\n================ RESULTADO DE LA AUDITORÍA ================")
#     print(json.dumps(resultado, indent=4, ensure_ascii=False))
    
#     # 🚀 AGREGA ESTO: Resalta de forma visual el Dictamen de la IA en consola
#     print("\n================🤖 DICTAMEN EJECUTIVO IA (QA) ================")
#     print(resultado.get("conclusion_ia", "No se generó conclusión de IA."))
#     print("==============================================================\n")
    
#     # Tu aserción de control
#     assert resultado["resultado_auditoria_texto"]["coincide"] is False


# # tests/test_pdf_hybrid.py
# import os
# import glob
# import json
# import pytest
# from hybrid.funsion_engine import run_pdf_validation

# def test_mi_primer_analisis_pdf():
#     # 1. Obtiene la raíz del proyecto dinámicamente
#     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     docs_dir = os.path.join(base_dir, "documents")
    
#     # 2. ESCANEO AUTOMÁTICO INTELIGENTE: Detecta archivos ignorando temporales de Word
#     archivos_actual = [
#         f for f in glob.glob(os.path.join(docs_dir, "*actual*.*"))
#         if not os.path.basename(f).startswith("~$")
#     ]
#     archivos_expected = [
#         f for f in glob.glob(os.path.join(docs_dir, "*expected*.*"))
#         if not os.path.basename(f).startswith("~$")
#     ]
    
#     # 3. CONTROL DE QA: Validar que los archivos existan antes de correr el motor
#     if not archivos_actual:
#         pytest.fail(f"Error de QA: No se encontró ningún archivo 'actual' en la ruta: {docs_dir}")
#     if not archivos_expected:
#         pytest.fail(f"Error de QA: No se encontró ningún archivo 'expected' en la ruta: {docs_dir}")
        
#     # Tomamos el primer archivo que coincida de manera automática
#     actual = archivos_actual[0]
#     expected = archivos_expected[0]
    
#     # Imprimir en consola qué extensiones detectó automáticamente
#     print(f"\n[AUTO-DETECT] 📄 Analizando: {os.path.basename(actual)} VS {os.path.basename(expected)}")
    
#     # 4. Ejecuta la validación universal (el motor ya sabe qué hacer según la extensión)
#     resultado = run_pdf_validation(actual, expected)
    
#     # Imprimir el resultado detallado en la consola
#     print("\n================ RESULTADO DE LA AUDITORÍA ================")
#     print(json.dumps(resultado, indent=4, ensure_ascii=False))
    
#     print("\n================ DICTAMEN EJECUTIVO IA (QA) ================")
#     print(resultado.get("conclusion_ia", "No se generó conclusión de IA."))
#     print("==============================================================\n")
    
#     # Tu aserción de control
#     assert resultado["resultado_auditoria_texto"]["coincide"] is False

# tests/test_pdf_hybrid.py
import os
import glob
import json
import pytest
from hybrid.funsion_engine import run_pdf_validation
from hybrid.visual_extractor import convertir_documento_a_imagenes  # 🚀 Importamos el extractor
from hybrid.ai_reporter import generar_conclusion_ia_multimodal               # 🚀 Importamos el reportero IA

def test_mi_primer_analisis_pdf():
    # 1. Obtiene la raíz del proyecto dinámicamente
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "documents")
    
    # 2. ESCANEO AUTOMÁTICO INTELIGENTE: Detecta archivos ignorando temporales de Word
    archivos_actual = [
        f for f in glob.glob(os.path.join(docs_dir, "*actual*.*"))
        if not os.path.basename(f).startswith("~$")
    ]
    archivos_expected = [
        f for f in glob.glob(os.path.join(docs_dir, "*expected*.*"))
        if not os.path.basename(f).startswith("~$")
    ]
    
    # 3. CONTROL DE QA: Validar que los archivos existan antes de correr el motor
    if not archivos_actual:
        pytest.fail(f"Error de QA: No se encontró ningún archivo 'actual' en la ruta: {docs_dir}")
    if not archivos_expected:
        pytest.fail(f"Error de QA: No se encontró ningún archivo 'expected' en la ruta: {docs_dir}")
        
    # Tomamos el primer archivo que coincida de manera automática
    actual = archivos_actual[0]
    expected = archivos_expected[0]
    
    # Imprimir en consola qué extensiones detectó automáticamente
    print(f"\n[AUTO-DETECT]  Analizando: {os.path.basename(actual)} VS {os.path.basename(expected)}")
    
    # 4. Ejecuta la validación universal de texto
    resultado = run_pdf_validation(actual, expected)
    
    # 5. Extraemos las imágenes del archivo 'actual' (y 'expected' si deseas)
    imagenes_actual = convertir_documento_a_imagenes(actual)
    
    print(f"[VISUAL]  Generando capturas del documento EXPECTED ({os.path.basename(expected)})...")
    imagenes_expected = convertir_documento_a_imagenes(expected)
    
    # 6. Generamos la conclusión de la IA pasándole el análisis de texto Y las imágenes
    conclusion_multimodal = generar_conclusion_ia_multimodal(
        resultado_analisis=resultado,
        rutas_imagenes_actual=imagenes_actual,
        rutas_imagenes_expected=imagenes_expected
    )
    
    # Imprimir el resultado detallado en la consola
    print("\n================ RESULTADO DE LA AUDITORÍA ================")
    print(json.dumps(resultado, indent=4, ensure_ascii=False))
    
    print("\n================ DICTAMEN EJECUTIVO IA (TEXTO + VISUAL) ================")
    print(conclusion_multimodal)
    print("==============================================================\n")
    
    # Tu aserción de control
    # Ajusta según la estructura exacta que retorna tu run_pdf_validation
    assert resultado.get("coincide", False) is False or resultado.get("resultado_auditoria_texto", {}).get("coincide", False) is False