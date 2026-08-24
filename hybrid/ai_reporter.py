# hybrid/ai_reporter.py
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def generar_conclusion_ia_multimodal(
    resultado_analisis: dict, 
    rutas_imagenes_actual: list = None, 
    rutas_imagenes_expected: list = None
) -> str:
    """
    Recibe el análisis de texto y las capturas visuales tanto del documento
    ACTUAL como del EXPECTED para realizar una auditoría visual comparativa.
    """
    # 1. Extracción de discrepancias de texto
    discrepancias = resultado_analisis.get("discrepancias", [])
    if not discrepancias and "resultado_auditoria_texto" in resultado_analisis:
        discrepancias = resultado_analisis["resultado_auditoria_texto"].get("discrepancias", [])

    resumen_tecnico = ""
    for idx, disc in enumerate(discrepancias, 1):
        pagina = disc.get('pagina', 'N/A')
        tipo = disc.get('tipo', 'Desconocido')
        cambios = disc.get('cambios_internos', [])
        
        resumen_tecnico += f"Defecto Técnico #{idx} (Pág: {pagina} - Tipo: {tipo}):\n"
        for cambio in cambios:
            resumen_tecnico += f"  - {cambio}\n"

    if not resumen_tecnico:
        resumen_tecnico = "No se detectaron discrepancias de texto explícitas por el motor de código."

    # 2. Prompt enfocado en COMPARACIÓN VISUAL (ACTUAL VS EXPECTED)
    prompt_sistema = (
        "Eres un Ingeniero de QA Automation Senior y Auditor de Calidad Visual de Documentos.\n"
        "Se te proporciona un reporte técnico de diferencias en texto y las imágenes de dos documentos:\n"
        "- Documento ESPERADO (Template/Expected): La referencia base correcta.\n"
        "- Documento ACTUAL (Generated/Actual): El documento generado bajo prueba.\n\n"
        "TU OBJETIVO DE QA:\n"
        "1. Inicia tu respuesta estrictamente con [STATUS: PASSED] o [STATUS: FAILED].\n"
        "2. Compara visualmente el documento ACTUAL contra el EXPECTED.\n"
        "3. Detecta diferencias de formato visual entre ambos: desalineaciones de tablas, cambios de tipografía/negritas, "
        "márgenes alterados, imágenes/logos movidos o faltantes, y saltos de página feos.\n"
        "4. Evalúa si las diferencias de texto reportadas alteran la validez legal o reglas de negocio.\n"
        "5. Entrega un resumen ejecutivo estructurado: Estado, Severidad (Crítica/Alta/Media) y Hallazgos Visuales Clave."
    )

    prompt_usuario = (
        f"Hola. El motor de comparación de código detectó estas diferencias de texto entre los documentos:\n\n"
        f"{resumen_tecnico}\n\n"
        f"A continuación te adjunto las capturas visuales etiquetadas de ambos documentos para que realices "
        f"la comparación visual detallada. Genera el Dictamen de QA:"
    )

    safe_contents = [prompt_usuario]
    
    # Helper para adjuntar imágenes con etiquetas de texto previas para dar contexto a la IA
    def adjuntar_imagenes(rutas, etiqueta):
        if rutas:
            safe_contents.append(f"\n--- IMÁGENES DEL DOCUMENTO {etiqueta} ---")
            for ruta_img in rutas:
                if os.path.exists(ruta_img):
                    nombre_archivo = os.path.basename(ruta_img)
                    safe_contents.append(f"Página/Captura ({etiqueta}): {nombre_archivo}")
                    with open(ruta_img, "rb") as f:
                        safe_contents.append(
                            types.Part.from_bytes(
                                data=f.read(),
                                mime_type="image/png"
                            )
                        )

    # 3. Adjuntamos primero las de referencia (EXPECTED) y luego las generadas (ACTUAL)
    adjuntar_imagenes(rutas_imagenes_expected, "EXPECTED (REFERENCIA BASE)")
    adjuntar_imagenes(rutas_imagenes_actual, "ACTUAL (BAJO PRUEBA)")

    # 4. Llamar a la API de Gemini
    try:
        client = genai.Client()
        
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=safe_contents,
            config=types.GenerateContentConfig(
                system_instruction=prompt_sistema,
                temperature=0.2,
            )
        )
        
        # Limpieza de imágenes temporales de ambos conjuntos
        todas_las_rutas = (rutas_imagenes_actual or []) + (rutas_imagenes_expected or [])
        for ruta_img in todas_las_rutas:
            if os.path.exists(ruta_img):
                try:
                    os.remove(ruta_img)
                except Exception:
                    pass
                    
        return response.text.strip()
        
    except Exception as e:
        return f"Error en la auditoría multimodal de Gemini: {str(e)}"

# Alias de compatibilidad
generar_conclusion_ia = generar_conclusion_ia_multimodal