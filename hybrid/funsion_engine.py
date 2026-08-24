# # hybrid/funsion_engine.py

# from hybrid.field_analyzer import extract_text_from_pdf
# from hybrid.structure_analyzer import identify_document_by_title, analyze_document_structure

# def run_pdf_validation(actual_pdf_path):
#     # 1. Extraer texto del PDF
#     actual_text = extract_text_from_pdf(actual_pdf_path)
#     if not actual_text:
#         return {"error": "El archivo PDF está vacío o no se pudo leer."}
    
#     # 2. Identificar el documento mediante el título
#     titulo_detectado = identify_document_by_title(actual_text)
#     if not titulo_detectado:
#         return {"error": "No se pudo identificar el tipo de documento a través del título."}
        
#     # 3. Correr el análisis estructural de secciones
#     resultado_analisis = analyze_document_structure(actual_text, titulo_detectado)
#     return resultado_analisis


# # hybrid/funsion_engine.py
# from hybrid.field_analyzer import extract_text_from_pdf
# from hybrid.structure_analyzer import identify_document_by_title, analyze_document_structure
# from hybrid.semantic_analyzer import compare_section_content_with_ai

# def run_pdf_validation(actual_pdf_path, expected_pdf_path):
#     # 1. Extraer texto de ambos PDFs
#     actual_text = extract_text_from_pdf(actual_pdf_path)
#     expected_text = extract_text_from_pdf(expected_pdf_path)
    
#     # 2. Identificar el documento (usando el actual)
#     titulo_detectado = identify_document_by_title(actual_text)
#     if not titulo_detectado:
#         return {"error": "No se pudo identificar el tipo de documento por su título."}
        
#     # 3. Analizar estructuras de ambos archivos
#     analisis_actual = analyze_document_structure(actual_text, titulo_detectado)
#     analisis_esperado = analyze_document_structure(expected_text, titulo_detectado)
    
#     # Inicializar reporte de diferencias de contenido
#     resultado_comparativa_contenido = {}
    
#     # 4. Comparar el contenido interno de las secciones encontradas comunes
#     contenido_actual = analisis_actual.get("contenido_secciones", {})
#     contenido_esperado = analisis_esperado.get("contenido_secciones", {})
    
#     for seccion in analisis_actual["secciones_esperadas"]:
#         # Solo comparamos si la sección fue encontrada en ambos documentos
#         if seccion in contenido_actual and seccion in contenido_esperado:
#             print(f"Analizando semánticamente con IA la sección: {seccion}...")
            
#             res_ai = compare_section_content_with_ai(
#                 seccion_nombre=seccion,
#                 texto_actual=contenido_actual[seccion],
#                 texto_esperado=contenido_esperado[seccion]
#             )
#             resultado_comparativa_contenido[seccion] = res_ai

#     # Retornamos el formato final estructurado junto con la revisión de contenido
#     return {
#         "secciones_esperadas": analisis_actual["secciones_esperadas"],
#         "secciones_encontradas": analisis_actual["secciones_encontradas"],
#         "secciones_faltantes": analisis_actual["secciones_faltantes"],
#         "puntuacion_estructura": analisis_actual["puntuacion_estructura"],
#         "analisis_contenido_ia": resultado_comparativa_contenido
#     }

# # hybrid/funsion_engine.py
# from hybrid.field_analyzer import extract_text_from_pdf
# from hybrid.structure_analyzer import discover_sections_with_ai, analyze_document_structure_dynamic
# from hybrid.semantic_analyzer import compare_section_content_with_ai

# def run_pdf_validation(actual_pdf_path, expected_pdf_path, model_name="deepseek-r1:latest"):
#     # 1. Extraer texto plano de ambos PDFs
#     actual_text = extract_text_from_pdf(actual_pdf_path)
#     expected_text = extract_text_from_pdf(expected_pdf_path)
    
#     if not actual_text or not expected_text:
#         return {"error": "No se pudo extraer texto de alguno de los documentos."}
        
#     # 2. AUTOMÁTICO: Descubrir qué secciones componen el documento original (esperado)
#     secciones_esperadas_dinamicas = discover_sections_with_ai(expected_text, model_name=model_name)
    
#     if not secciones_esperadas_dinamicas:
#         return {"error": "La IA no pudo determinar las secciones del documento original."}
    
#     print(f"Secciones descubiertas automáticamente: {secciones_esperadas_dinamicas}")
    
#     # 3. Analizar estructuras basándonos en la lista descubierta
#     analisis_actual = analyze_document_structure_dynamic(actual_text, secciones_esperadas_dinamicas)
#     analisis_esperado = analyze_document_structure_dynamic(expected_text, secciones_esperadas_dinamicas)
    
#     resultado_comparativa_contenido = {}
#     contenido_actual = analisis_actual.get("contenido_secciones", {})
#     contenido_esperado = analisis_esperado.get("contenido_secciones", {})
    
#     # 4. Comparar semánticamente el contenido interno descubierto
#     for seccion in analisis_actual["secciones_esperadas"]:
#         if seccion in contenido_actual and seccion in contenido_esperado:
#             print(f" -> Analizando contenido de la sección: '{seccion}'...")
#             res_ai = compare_section_content_with_ai(
#                 seccion_nombre=seccion,
#                 texto_actual=contenido_actual[seccion],
#                 texto_esperado=contenido_esperado[seccion],
#                 model_name=model_name
#             )
#             resultado_comparativa_contenido[seccion] = res_ai

#     return {
#         "secciones_esperadas": analisis_actual["secciones_esperadas"],
#         "secciones_encontradas": analisis_actual["secciones_encontradas"],
#         "secciones_faltantes": analisis_actual["secciones_faltantes"],
#         "puntuacion_estructura": analisis_actual["puntuacion_estructura"],
#         "analisis_contenido_ia": resultado_comparativa_contenido
#     }

# # hybrid/funsion_engine.py
# import os
# from hybrid.field_analyzer import extract_text_from_pdf, convert_pdf_first_page_to_image
# from hybrid.structure_analyzer import discover_sections_with_vision_ai, analyze_document_structure_dynamic
# from hybrid.semantic_analyzer import compare_section_content_with_ai

# def run_pdf_validation(actual_pdf_path, expected_pdf_path, model_vision="minicpm-v", model_text="minicpm-v"):
#     # 1. Convertir el PDF esperado a imagen para extraer las secciones reales
#     img_esperada = "documents/temp_expected.png"
#     if not convert_pdf_first_page_to_image(expected_pdf_path, img_esperada):
#         return {"error": "No se pudo generar la imagen del PDF esperado."}
        
#     # 2. Descubrir las secciones usando el modelo de visión
#     secciones_esperadas_dinamicas = discover_sections_with_vision_ai(img_esperada, model_name=model_vision)
    
#     # Limpiamos la imagen temporal creada
#     if os.path.exists(img_esperada):
#         os.remove(img_esperada)
        
#     if not secciones_esperadas_dinamicas:
#         return {"error": "El modelo de visión no pudo determinar las secciones."}
        
#     # 3. Extraer el texto plano de ambos archivos para hacer los recortes de contenido
#     actual_text = extract_text_from_pdf(actual_pdf_path)
#     expected_text = extract_text_from_pdf(expected_pdf_path)
    
#     # 4. Analizar la estructura usando las secciones descubiertas visualmente
#     analisis_actual = analyze_document_structure_dynamic(actual_text, secciones_esperadas_dinamicas)
#     analisis_esperado = analyze_document_structure_dynamic(expected_text, secciones_esperadas_dinamicas)
    
#     resultado_comparativa_contenido = {}
#     contenido_actual = analisis_actual.get("contenido_secciones", {})
#     contenido_esperado = analisis_esperado.get("contenido_secciones", {})
    
#     # 5. Comparar semánticamente los bloques internos
#     for seccion in analisis_actual["secciones_esperadas"]:
#         if seccion in contenido_actual and seccion in contenido_esperado:
#             print(f"-> Analizando contenido de la sección: '{seccion}'...")
#             res_ai = compare_section_content_with_ai(
#                 seccion_nombre=seccion,
#                 texto_actual=contenido_actual[seccion],
#                 texto_esperado=contenido_esperado[seccion],
#                 model_name=model_text
#             )
#             resultado_comparativa_contenido[seccion] = res_ai

#     return {
#         "secciones_esperadas": analisis_actual["secciones_esperadas"],
#         "secciones_encontradas": analisis_actual["secciones_encontradas"],
#         "secciones_faltantes": analisis_actual["secciones_faltantes"],
#         "puntuacion_estructura": analisis_actual["puntuacion_estructura"],
#         "analisis_contenido_ia": resultado_comparativa_contenido
#     }



# # hybrid/funsion_engine.py
# from hybrid.field_analyzer import extract_text_from_pdf
# from hybrid.structure_analyzer import discover_sections_programmatic, analyze_document_structure_dynamic
# from hybrid.semantic_analyzer import compare_section_content_with_ai

# def run_pdf_validation(actual_pdf_path, expected_pdf_path, model_text="deepseek-r1:7b"):
#     # 1. Extraer el texto plano de ambos archivos para las comparaciones semánticas
#     actual_text = extract_text_from_pdf(actual_pdf_path)
#     expected_text = extract_text_from_pdf(expected_pdf_path)
    
#     if not actual_text or not expected_text:
#         return {"error": "No se pudo extraer texto de alguno de los documentos."}
        
#     # 2. AUTOMÁTICO Y LOCAL: Descubrir secciones analizando las fuentes/TOC del archivo esperado
#     secciones_esperadas_dinamicas = discover_sections_programmatic(expected_pdf_path)
    
#     if not secciones_esperadas_dinamicas:
#         return {"error": "No se pudieron determinar las secciones estructurales del PDF."}
    
#     # 3. Analizar la consistencia de la estructura entre los dos archivos
#     analisis_actual = analyze_document_structure_dynamic(actual_text, secciones_esperadas_dinamicas)
#     analisis_esperado = analyze_document_structure_dynamic(expected_text, secciones_esperadas_dinamicas)
    
#     resultado_comparativa_contenido = {}
#     contenido_actual = analisis_actual.get("contenido_secciones", {})
#     contenido_esperado = analisis_esperado.get("contenido_secciones", {})
    
#     # 4. Usar la IA (Ollama) exclusivamente para auditar los textos internos extraídos
#     for seccion in analisis_actual["secciones_esperadas"]:
#         if seccion in contenido_actual and seccion in contenido_esperado:
#             # Si el bloque de texto interno es relevante, se manda a la IA
#             if len(contenido_actual[seccion].strip()) > 5:
#                 print(f" Auditando con IA el contenido de: '{seccion}'...")
#                 res_ai = compare_section_content_with_ai(
#                     seccion_nombre=seccion,
#                     texto_actual=contenido_actual[seccion],
#                     texto_esperado=contenido_esperado[seccion],
#                     model_name=model_text
#                 )
#                 resultado_comparativa_contenido[seccion] = res_ai
#             else:
#                 resultado_comparativa_contenido[seccion] = {
#                     "coincide": True, 
#                     "detalles": "Sección identificada correctamente sin cuerpo de texto adicional."
#                 }

#     return {
#         "secciones_esperadas": analisis_actual["secciones_esperadas"],
#         "secciones_encontradas": analisis_actual["secciones_encontradas"],
#         "secciones_faltantes": analisis_actual["secciones_faltantes"],
#         "puntuacion_estructura": analisis_actual["puntuacion_estructura"],
#         "analisis_contenido_ia": resultado_comparativa_contenido
#     }

# # hybrid/funsion_engine.py
# import re
# from hybrid.field_analyzer import extract_text_from_pdf
# from hybrid.structure_analyzer import discover_sections_programmatic, analyze_document_structure_dynamic
# from hybrid.semantic_analyzer import compare_section_content_with_ai

# def run_pdf_validation(actual_pdf_path, expected_pdf_path, model_text=None):
#     actual_text = extract_text_from_pdf(actual_pdf_path)
#     expected_text = extract_text_from_pdf(expected_pdf_path)
    
#     if not actual_text or not expected_text:
#         return {"error": "No se pudo extraer texto de los documentos."}
        
#     # 1. Extraer e identificar los códigos RECA de las cabeceras
#     reca_actual = re.search(r'RECA:\s*(\S+)', actual_text)
#     reca_esperado = re.search(r'RECA:\s*(\S+)', expected_text)
    
#     val_reca_actual = reca_actual.group(1) if reca_actual else "No encontrado"
#     val_reca_esperado = reca_esperado.group(1) if reca_esperado else "No encontrado"
    
#     # 2. Cargar secciones programáticas (Leyes maestras)
#     secciones_maestras = discover_sections_programmatic()
    
#     # 3. Mapear y segmentar contenido
#     analisis_actual = analyze_document_structure_dynamic(actual_text, secciones_maestras)
    
#     contenido_actual = analisis_actual.get("contenido_secciones", {})
#     analisis_esperado = analyze_document_structure_dynamic(expected_text, secciones_maestras)
#     contenido_esperado = analisis_esperado.get("contenido_secciones", {})
    
#     resultado_comparativa_contenido = {}
    
#     # 4. Comparar contenido de cada sección detectada
#     for seccion in analisis_actual["secciones_encontradas"]:
#         txt_act = contenido_actual.get(seccion, "")
#         txt_esp = contenido_esperado.get(seccion, "")
        
#         res = compare_section_content_with_ai(seccion, txt_act, txt_esp)
#         resultado_comparativa_contenido[seccion] = res

#     return {
#         "codigo_reca_actual": val_reca_actual,
#         "codigo_reca_esperado": val_reca_esperado,
#         "reca_coincide": val_reca_actual == val_reca_esperado,
#         "secciones_esperadas": analisis_actual["secciones_esperadas"],
#         "secciones_encontradas": analisis_actual["secciones_encontradas"],
#         "secciones_faltantes": analisis_actual["secciones_faltantes"],
#         "puntuacion_estructura": analisis_actual["puntuacion_estructura"],
#         "analisis_contenido": resultado_comparativa_contenido
#     }


# # hybrid/funsion_engine.py
# import re
# from hybrid.field_analyzer import extract_text_from_pdf
# from hybrid.structure_analyzer import discover_sections_programmatic, analyze_document_structure_dynamic
# from hybrid.semantic_analyzer import compare_section_content_with_ai

# def run_pdf_validation(actual_pdf_path, expected_pdf_path, model_text=None):
#     actual_text = extract_text_from_pdf(actual_pdf_path)
#     expected_text = extract_text_from_pdf(expected_pdf_path)
    
#     if not actual_text or not expected_text:
#         return {"error": "No se pudo extraer texto de los documentos."}
        
#     # 1. Extraer e identificar los códigos RECA de las cabeceras
#     reca_actual = re.search(r'RECA:\s*(\S+)', actual_text)
#     reca_esperado = re.search(r'RECA:\s*(\S+)', expected_text)
    
#     val_reca_actual = reca_actual.group(1) if reca_actual else "No encontrado"
#     val_reca_esperado = reca_esperado.group(1) if reca_esperado else "No encontrado"
    
#     # 2.  CORREGIDO: Pasar la ruta del PDF esperado para analizar negritas y centrado
#     secciones_maestras = discover_sections_programmatic(expected_pdf_path)
    
#     if not secciones_maestras:
#         return {"error": "No se detectaron títulos visuales (Negrita + Centrado) en el documento esperado."}
    
#     # 3. Mapear y segmentar contenido basado en la estructura visual descubierta
#     analisis_actual = analyze_document_structure_dynamic(actual_text, secciones_maestras)
#     contenido_actual = analisis_actual.get("contenido_secciones", {})
    
#     analisis_esperado = analyze_document_structure_dynamic(expected_text, secciones_maestras)
#     contenido_esperado = analisis_esperado.get("contenido_secciones", {})
    
#     resultado_comparativa_contenido = {}
    
#     # 4. Comparar contenido de cada sección detectada
#     for seccion in analisis_actual["secciones_encontradas"]:
#         txt_act = contenido_actual.get(seccion, "")
#         txt_esp = contenido_esperado.get(seccion, "")
        
#         res = compare_section_content_with_ai(seccion, txt_act, txt_esp, model_name=model_text)
#         resultado_comparativa_contenido[seccion] = res

#     return {
#         "codigo_reca_actual": val_reca_actual,
#         "codigo_reca_esperado": val_reca_esperado,
#         "reca_coincide": val_reca_actual == val_reca_esperado,
#         "secciones_esperadas": analisis_actual["secciones_esperadas"],
#         "secciones_encontradas": analisis_actual["secciones_encontradas"],
#         "secciones_faltantes": analisis_actual["secciones_faltantes"],
#         "puntuacion_estructura": analisis_actual["puntuacion_estructura"],
#         "analisis_contenido": resultado_comparativa_contenido
#     }

# # hybrid/funsion_engine.py
# import re
# from hybrid.field_analyzer import extract_text_with_page_mapping
# from hybrid.structure_analyzer import discover_sections_programmatic
# from hybrid.semantic_analyzer import compare_global_content

# def run_pdf_validation(actual_pdf_path, expected_pdf_path, model_text=None):
#     _ = model_text # Mantenemos compatibilidad de firma
    
#     # 1. Extraer texto plano y generar el mapa de coordenadas/páginas de las palabras
#     actual_text, mapa_paginas_actual = extract_text_with_page_mapping(actual_pdf_path)
#     expected_text, _ = extract_text_with_page_mapping(expected_pdf_path)
    
#     if not actual_text or not expected_text:
#         return {"error": "No se pudo extraer el contenido de los documentos."}
        
#     # 2. Identificar los códigos RECA de las cabeceras de forma independiente
#     reca_actual = re.search(r'RECA:\s*(\S+)', actual_text)
#     reca_esperado = re.search(r'RECA:\s*(\S+)', expected_text)
    
#     val_reca_actual = reca_actual.group(1) if reca_actual else "No encontrado"
#     val_reca_esperado = reca_esperado.group(1) if reca_esperado else "No encontrado"
    
#     # 3. Detectar títulos de leyes de forma visual (Negrita + Centrado) para control estructural
#     secciones_maestras = discover_sections_programmatic(expected_pdf_path)
    
#     # 4. Comparación global de palabras con localización de página
#     auditoria_texto = compare_global_content(actual_text, expected_text, mapa_paginas_actual)

#     return {
#         "codigo_reca_actual": val_reca_actual,
#         "codigo_reca_esperado": val_reca_esperado,
#         "reca_coincide": val_reca_actual == val_reca_esperado,
#         "secciones_visuales_detectadas": secciones_maestras,
#         "resultado_auditoria_texto": {
#             "coincide": auditoria_texto["coincide"],
#             "detalles": auditoria_texto["detalles"],
#             "discrepancias_detectadas": auditoria_texto["discrepancias"]
#         }
#     }


# # hybrid/funsion_engine.py
# import re
# from hybrid.field_analyzer import extract_text_with_page_mapping
# from hybrid.structure_analyzer import discover_sections_programmatic
# from hybrid.semantic_analyzer import compare_global_content

# def run_pdf_validation(actual_pdf_path, expected_pdf_path, model_text=None):
#     _ = model_text # Mantenemos compatibilidad de firma por si acaso
    
#     # 1. Extraer texto plano y generar el mapa de páginas de las palabras
#     actual_text, mapa_paginas_actual = extract_text_with_page_mapping(actual_pdf_path)
#     expected_text, _ = extract_text_with_page_mapping(expected_pdf_path)
    
#     if not actual_text or not expected_text:
#         return {"error": "No se pudo extraer el contenido de los documentos."}
        
#     # 2. Identificar los códigos RECA de las cabeceras de forma independiente
#     reca_actual = re.search(r'RECA:\s*(\S+)', actual_text)
#     reca_esperado = re.search(r'RECA:\s*(\S+)', expected_text)
    
#     val_reca_actual = reca_actual.group(1) if reca_actual else "No encontrado"
#     val_reca_esperado = reca_esperado.group(1) if reca_esperado else "No encontrado"
    
#     # 3. Detectar títulos de leyes visuales (Negrita + Centrado) en el documento esperado
#     secciones_esperadas = discover_sections_programmatic(expected_pdf_path)
    
#     # 4. Verificar cuáles de esas secciones visuales existen en el texto del documento actual
#     secciones_encontradas = []
#     secciones_faltantes = []
    
#     for seccion in secciones_esperadas:
#         # Buscamos la sección de manera insensible a mayúsculas/minúsculas
#         if re.search(re.escape(seccion), actual_text, re.IGNORECASE):
#             secciones_encontradas.append(seccion)
#         else:
#             secciones_faltantes.append(seccion)
            
#     # CALCULAMOS LA PUNTUACIÓN DE LA ESTRUCTURA DETECTADA
#     total_esperadas = len(secciones_esperadas)
#     encontradas = len(secciones_encontradas)
#     puntuacion = (encontradas / total_esperadas) * 100 if total_esperadas > 0 else 0.0
    
#     # 5. Comparación global de palabras con localización de página
#     auditoria_texto = compare_global_content(actual_text, expected_text, mapa_paginas_actual)

#     return {
#         "codigo_reca_actual": val_reca_actual,
#         "codigo_reca_esperado": val_reca_esperado,
#         "reca_coincide": val_reca_actual == val_reca_esperado,
#         "secciones_esperadas": secciones_esperadas,
#         "secciones_encontradas": secciones_encontradas,
#         "secciones_faltantes": secciones_faltantes,
#         "puntuacion_estructura": round(puntuacion, 2),
#         "resultado_auditoria_texto": {
#             "coincide": auditoria_texto["coincide"],
#             "detalles": auditoria_texto["detalles"],
#             "discrepancias_detectadas": auditoria_texto["discrepancias"]
#         }
#     }


# # hybrid/funsion_engine.py
# import re
# from hybrid.field_analyzer import extract_text_with_page_mapping
# from hybrid.structure_analyzer import discover_sections_programmatic
# from hybrid.semantic_analyzer import compare_global_content

# def run_pdf_validation(actual_pdf_path, expected_pdf_path, model_text=None):
#     _ = model_text
    
#     # 1. Extraer texto plano y generar el mapa de páginas de las palabras
#     actual_text, mapa_paginas_actual = extract_text_with_page_mapping(actual_pdf_path)
#     expected_text, _ = extract_text_with_page_mapping(expected_pdf_path)
    
#     if not actual_text or not expected_text:
#         return {"error": "No se pudo extraer el contenido de los documentos."}
        
#     # 2. Identificar los códigos RECA de las cabeceras de forma independiente
#     reca_actual = re.search(r'RECA:\s*(\S+)', actual_text)
#     reca_esperado = re.search(r'RECA:\s*(\S+)', expected_text)
    
#     val_reca_actual = reca_actual.group(1) if reca_actual else "No encontrado"
#     val_reca_esperado = reca_esperado.group(1) if reca_esperado else "No encontrado"
    
#     # 3. Detectar títulos de leyes visuales (Negrita + Centrado) en el documento esperado
#     secciones_esperadas = discover_sections_programmatic(expected_pdf_path)
    
#     # 4. Verificar cuáles de esas secciones visuales existen en el texto del documento actual
#     secciones_encontradas = []
#     secciones_faltantes = []
    
#     for seccion in secciones_esperadas:
#         if re.search(re.escape(seccion), actual_text, re.IGNORECASE):
#             secciones_encontradas.append(seccion)
#         else:
#             secciones_faltantes.append(seccion)
            
#     # Calculamos la puntuación de la estructura detectada
#     total_esperadas = len(secciones_esperadas)
#     encontradas = len(secciones_encontradas)
#     puntuacion = (encontradas / total_esperadas) * 100 if total_esperadas > 0 else 0.0
    
#     # 5. Comparación global por bloques (estilo Draftable)
#     auditoria_texto = compare_global_content(actual_text, expected_text, mapa_paginas_actual)

#     # Formatear el reporte de discrepancias para que sea idéntico a una auditoría visual
#     bloques_reportados = []
#     for disc in auditoria_texto["discrepancias"]:
#         fmt = f"[Pág {disc['pagina']}] Tipo: {disc['tipo']}"
#         if disc['texto_esperado']:
#             fmt += f" | Esperado: \"{disc['texto_esperado']}\""
#         if disc['texto_actual']:
#             fmt += f" | Actual: \"{disc['texto_actual']}\""
#         bloques_reportados.append(fmt)

#     return {
#         "codigo_reca_actual": val_reca_actual,
#         "codigo_reca_esperado": val_reca_esperado,
#         "reca_coincide": val_reca_actual == val_reca_esperado,
#         "secciones_esperadas": secciones_esperadas,
#         "secciones_encontradas": secciones_encontradas,
#         "secciones_faltantes": secciones_faltantes,
#         "puntuacion_estructura": round(puntuacion, 2),
#         "resultado_auditoria_texto": {
#             "coincide": auditoria_texto["coincide"],
#             "detalles": auditoria_texto["detalles"],
#             "discrepancias_detectadas": bloques_reportados[:10]  # Mostramos los primeros 10 bloques modificados
#         }
#     }

# # hybrid/funsion_engine.py
# import re
# from hybrid.field_analyzer import extract_text_with_page_mapping
# from hybrid.structure_analyzer import discover_sections_programmatic
# from hybrid.semantic_analyzer import compare_global_content_blocks

# def run_pdf_validation(actual_pdf_path, expected_pdf_path, model_text=None):
#     _ = model_text
    
#     # 1. Extraer el texto completo y sus mapas de líneas por página
#     actual_text, lineas_actuales_map = extract_text_with_page_mapping(actual_pdf_path)
#     expected_text, lineas_esperadas_map = extract_text_with_page_mapping(expected_pdf_path)
    
#     if not actual_text or not expected_text:
#         return {"error": "No se pudo extraer el contenido de los documentos."}
        
#     # 2. Identificar códigos RECA
#     reca_actual = re.search(r'RECA:\s*(\S+)', actual_text)
#     reca_esperado = re.search(r'RECA:\s*(\S+)', expected_text)
    
#     val_reca_actual = reca_actual.group(1) if reca_actual else "No encontrado"
#     val_reca_esperado = reca_esperado.group(1) if reca_esperado else "No encontrado"
    
#     # 3. Control estructural de Secciones Visuales (Negrita + Centrado)
#     secciones_esperadas = discover_sections_programmatic(expected_pdf_path)
#     secciones_encontradas = []
#     secciones_faltantes = []
    
#     for seccion in secciones_esperadas:
#         if re.search(re.escape(seccion), actual_text, re.IGNORECASE):
#             secciones_encontradas.append(seccion)
#         else:
#             secciones_faltantes.append(seccion)
            
#     total_esperadas = len(secciones_esperadas)
#     puntuacion = (len(secciones_encontradas) / total_esperadas) * 100 if total_esperadas > 0 else 0.0
    
#     # 4. 🔥 COMPARACIÓN GLOBAL POR BLOQUES (Garantiza ver el 100% de diferencias)
#     auditoria_texto = compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map)

#     # Formatear la salida para el reporte final de QA
#     bloques_reportados = []
#     for disc in auditoria_texto["discrepancias"]:
#         fmt = f"[Pág {disc['pagina']}] {disc['tipo']} ->"
#         if disc['texto_esperado']:
#             fmt += f" Esperado: \"{disc['texto_esperado']}\""
#         if disc['texto_actual']:
#             fmt += f" Actual: \"{disc['texto_actual']}\""
#         bloques_reportados.append(fmt)

#     return {
#         "codigo_reca_actual": val_reca_actual,
#         "codigo_reca_esperado": val_reca_esperado,
#         "reca_coincide": val_reca_actual == val_reca_esperado,
#         "secciones_esperadas": secciones_esperadas,
#         "secciones_encontradas": secciones_encontradas,
#         "secciones_faltantes": secciones_faltantes,
#         "puntuacion_estructura": round(puntuacion, 2),
#         "resultado_auditoria_texto": {
#             "coincide": auditoria_texto["coincide"],
#             "detalles": auditoria_texto["detalles"],
#             "discrepancias_detectadas": bloques_reportados  # Muestra todas las discrepancias de forma consistente
#         }
#     }

# # hybrid/funsion_engine.py
# import re
# from hybrid.field_analyzer import extract_text_with_page_mapping
# from hybrid.structure_analyzer import discover_sections_programmatic
# from hybrid.semantic_analyzer import compare_global_content_blocks

# def run_pdf_validation(actual_pdf_path, expected_pdf_path, model_text=None):
#     _ = model_text
    
#     # 1. Extraer el texto completo y sus mapas de líneas por página
#     actual_text, lineas_actuales_map = extract_text_with_page_mapping(actual_pdf_path)
#     expected_text, lineas_esperadas_map = extract_text_with_page_mapping(expected_pdf_path)
    
#     if not actual_text or not expected_text:
#         return {"error": "No se pudo extraer el contenido de los documentos."}
        
#     # 2. Identificar códigos RECA
#     reca_actual = re.search(r'RECA:\s*(\S+)', actual_text)
#     reca_esperado = re.search(r'RECA:\s*(\S+)', expected_text)
    
#     val_reca_actual = reca_actual.group(1) if reca_actual else "No encontrado"
#     val_reca_esperado = reca_esperado.group(1) if reca_esperado else "No encontrado"
    
#     # 3. Control estructural de Secciones Visuales (Negrita + Centrado)
#     secciones_esperadas = discover_sections_programmatic(expected_pdf_path)
#     secciones_encontradas = []
#     secciones_faltantes = []
    
#     for seccion in secciones_esperadas:
#         if re.search(re.escape(seccion), actual_text, re.IGNORECASE):
#             secciones_encontradas.append(seccion)
#         else:
#             secciones_faltantes.append(seccion)
            
#     total_esperadas = len(secciones_esperadas)
#     puntuacion = (len(secciones_encontradas) / total_esperadas) * 100 if total_esperadas > 0 else 0.0
    
#     # 4. Comparación global por bloques
#     auditoria_texto = compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map)

#     #  FORMATEO VISUAL AVANZADO PARA LA CONSOLA (Estilo Draftable)
#     bloques_reportados = []
    
#     # Códigos de color ANSI básicos para la terminal (opcional pero muy descriptivo)
#     ROJO = "\033[91m"
#     VERDE = "\033[92m"
#     AZUL = "\033[94m"
#     AMARILLO = "\033[93m"
#     RESET = "\033[0m"

#     for idx, disc in enumerate(auditoria_texto["discrepancias"], start=1):
#         tipo = disc['tipo']
#         pag = disc['pagina']
        
#         # Asignar color según el tipo de discrepancia
#         color_tipo = AMARILLO if tipo == "Modificado" else (ROJO if "Faltante" in tipo else VERDE)
        
#         tarjeta = (
#             f"\n  ┌──  DISCREPANCIA #{idx} ───────────────────────────────────────────\n"
#             f"  │  Página: {AZUL}{pag}{RESET}\n"
#             f"  │   Tipo:   {color_tipo}{tipo}{RESET}\n"
#         )
        
#         if disc['texto_esperado']:
#             tarjeta += f"  │  {ROJO}Esperado:{RESET} \"{disc['texto_esperado']}\"\n"
#         if disc['texto_actual']:
#             tarjeta += f"  │  {VERDE}Actual:{RESET}   \"{disc['texto_actual']}\"\n"
            
#         tarjeta += "  └──────────────────────────────────────────────────────────────────"
#         bloques_reportados.append(tarjeta)

#     return {
#         "codigo_reca_actual": val_reca_actual,
#         "codigo_reca_esperado": val_reca_esperado,
#         "reca_coincide": val_reca_actual == val_reca_esperado,
#         "secciones_esperadas": secciones_esperadas,
#         "secciones_encontradas": secciones_encontradas,
#         "secciones_faltantes": secciones_faltantes,
#         "puntuacion_estructura": round(puntuacion, 2),
#         "resultado_auditoria_texto": {
#             "coincide": auditoria_texto["coincide"],
#             "detalles": auditoria_texto["detalles"],
#             # Pasamos la lista de tarjetas formateadas para la terminal
#             "discrepancias_detectadas": bloques_reportados  
#         }
#     }

# # hybrid/funsion_engine.py
# import re
# from hybrid.field_analyzer import extract_text_with_page_mapping
# from hybrid.structure_analyzer import discover_sections_programmatic
# from hybrid.semantic_analyzer import compare_global_content_blocks

# def run_pdf_validation(actual_pdf_path, expected_pdf_path, model_text=None):
#     _ = model_text
    
#     # 1. Extraer el texto completo y sus mapas de líneas por página
#     actual_text, lineas_actuales_map = extract_text_with_page_mapping(actual_pdf_path)
#     expected_text, lineas_esperadas_map = extract_text_with_page_mapping(expected_pdf_path)
    
#     if not actual_text or not expected_text:
#         return {"error": "No se pudo extraer el contenido de los documentos."}
        
#     # 2. Identificar códigos RECA
#     reca_actual = re.search(r'RECA:\s*(\S+)', actual_text)
#     reca_esperado = re.search(r'RECA:\s*(\S+)', expected_text)
    
#     val_reca_actual = reca_actual.group(1) if reca_actual else "No encontrado"
#     val_reca_esperado = reca_esperado.group(1) if reca_esperado else "No encontrado"
    
#     # 3. Control estructural de Secciones Visuales (Negrita + Centrado)
#     secciones_esperadas = discover_sections_programmatic(expected_pdf_path)
#     secciones_encontradas = []
#     secciones_faltantes = []
    
#     for seccion in secciones_esperadas:
#         if re.search(re.escape(seccion), actual_text, re.IGNORECASE):
#             secciones_encontradas.append(seccion)
#         else:
#             secciones_faltantes.append(seccion)
            
#     total_esperadas = len(secciones_esperadas)
#     puntuacion = (len(secciones_encontradas) / total_esperadas) * 100 if total_esperadas > 0 else 0.0
    
#     # 4. Comparación global por bloques
#     auditoria_texto = compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map)

#     # MAQUETACIÓN ESTRUCTURADA EN TEXTO PLANO (Estilo Reporte Alternativo)
#     # REPORTE DE BLOQUES CON DESGLOSE DETALLADO MULTI-FORMATO
#     bloques_reportados = []

#     for idx, disc in enumerate(auditoria_texto["discrepancias"], start=1):
#         # Si es un número (de PDF) le ponemos el prefijo Página, si es un string (de Word) pasa directo
#         loc = f"Página: {disc['pagina']}" if isinstance(disc['pagina'], int) else f"Ubicación: {disc['pagina']}"
        
#         tarjeta = (
#             f"\n  [ BLOQUE AFECTADO #{idx} ] " + "─" * 48 + "\n"
#             f"  │ 📄 {loc}\n"
#             f"  │ 🛠️  Aviso:  {disc['tipo']}\n"
#             f"  │ 📉 ORIGINAL: \"{disc['texto_esperado']}\"\n"
#             f"  │ 📈 DETECTADO: \"{disc['texto_actual']}\"\n"
#             f"  │ 🔬 DESGLOSE DE CAMBIOS INTERNOS:\n"
#         )
        
#         for cambio in disc["cambios_internos"]:
#             tarjeta += f"  │    • {cambio}\n"
            
#         tarjeta += "  " + "─" * 74
#         bloques_reportados.append(tarjeta)

#     return {
#         "codigo_reca_actual": val_reca_actual,
#         "codigo_reca_esperado": val_reca_esperado,
#         "reca_coincide": val_reca_actual == val_reca_esperado,
#         "secciones_esperadas": secciones_esperadas,
#         "secciones_encontradas": secciones_encontradas,
#         "secciones_faltantes": secciones_faltantes,
#         "puntuacion_estructura": round(puntuacion, 2),
#         "resultado_auditoria_texto": {
#             "coincide": auditoria_texto["coincide"],
#             "detalles": auditoria_texto["detalles"],
#             "discrepancias_detectadas": bloques_reportados
#         }
#     }


# hybrid/funsion_engine.py
import re
from hybrid.field_analyzer import extract_text_with_page_mapping
from hybrid.structure_analyzer import discover_sections_programmatic
from hybrid.semantic_analyzer import compare_global_content_blocks
from hybrid.ai_reporter import generar_conclusion_ia  # 🚀 1. Importamos el nuevo módulo de IA

def run_pdf_validation(actual_pdf_path, expected_pdf_path, model_text=None):
    _ = model_text
    
    # 1. Extraer el texto completo y sus mapas de líneas por página
    actual_text, lineas_actuales_map = extract_text_with_page_mapping(actual_pdf_path)
    expected_text, lineas_esperadas_map = extract_text_with_page_mapping(expected_pdf_path)
    
    if not actual_text or not expected_text:
        return {"error": "No se pudo extraer el contenido de los documentos."}
        
    # 2. Identificar códigos RECA
    reca_actual = re.search(r'RECA:\s*(\S+)', actual_text)
    reca_esperado = re.search(r'RECA:\s*(\S+)', expected_text)
    
    val_reca_actual = reca_actual.group(1) if reca_actual else "No encontrado"
    val_reca_esperado = reca_esperado.group(1) if reca_esperado else "No encontrado"
    
    # 3. Control estructural de Secciones Visuales (Negrita + Centrado)
    secciones_esperadas = discover_sections_programmatic(expected_pdf_path)
    secciones_encontradas = []
    secciones_faltantes = []
    
    for seccion in secciones_esperadas:
        if re.search(re.escape(seccion), actual_text, re.IGNORECASE):
            secciones_encontradas.append(seccion)
        else:
            secciones_faltantes.append(seccion)
            
    total_esperadas = len(secciones_esperadas)
    puntuacion = (len(secciones_encontradas) / total_esperadas) * 100 if total_esperadas > 0 else 0.0
    
    # 4. Comparación global por bloques
    auditoria_texto = compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map)

    #  5. EJECUCIÓN DE LA IA (Desacoplada del diseño visual)
    # Le pasamos el diccionario nativo de auditoria_texto antes de convertirlo a texto plano
    if not auditoria_texto.get("coincide", False):
        conclusion_ia = generar_conclusion_ia(auditoria_texto)
    else:
        conclusion_ia = "Conclusión de la IA: No se detectaron discrepancias en el contenido crítico del documento."

    # MAQUETACIÓN ESTRUCTURADA EN TEXTO PLANO (Estilo Reporte Alternativo)
    # REPORTE DE BLOQUES CON DESGLOSE DETALLADO MULTI-FORMATO
    bloques_reportados = []

    for idx, disc in enumerate(auditoria_texto["discrepancias"], start=1):
        # Si es un número (de PDF) le ponemos el prefijo Página, si es un string (de Word) pasa directo
        loc = f"Página: {disc['pagina']}" if isinstance(disc['pagina'], int) else f"Ubicación: {disc['pagina']}"
        
        tarjeta = (
            f"\n  [ BLOQUE AFECTADO #{idx} ] " + "─" * 48 + "\n"
            f"  │ 📄 {loc}\n"
            f"  │ 🛠️  Aviso:  {disc['tipo']}\n"
            f"  │ 📉 ORIGINAL: \"{disc['texto_esperado']}\"\n"
            f"  │ 📈 DETECTADO: \"{disc['texto_actual']}\"\n"
            f"  │ 🔬 DESGLOSE DE CAMBIOS INTERNOS:\n"
        )
        
        for cambio in disc["cambios_internos"]:
            tarjeta += f"  │    • {cambio}\n"
            
        tarjeta += "  " + "─" * 74
        bloques_reportados.append(tarjeta)

    # 6. Retornamos la estructura original sumando el nuevo campo de la conclusión
    return {
        "codigo_reca_actual": val_reca_actual,
        "codigo_reca_esperado": val_reca_esperado,
        "reca_coincide": val_reca_actual == val_reca_esperado,
        "secciones_esperadas": secciones_esperadas,
        "secciones_encontradas": secciones_encontradas,
        "secciones_faltantes": secciones_faltantes,
        "puntuacion_estructura": round(puntuacion, 2),
        "conclusion_ia": conclusion_ia,  # Se añade la clave al JSON de salida sin romper la firma previa
        "resultado_auditoria_texto": {
            "coincide": auditoria_texto["coincide"],
            "detalles": auditoria_texto["detalles"],
            "discrepancias_detectadas": bloques_reportados
        }
    }