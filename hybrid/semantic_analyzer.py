# # hybrid/semantic_analyzer.py
# import ollama
# import json

# def compare_section_content_with_ai(seccion_nombre, texto_actual, texto_esperado, model_name="deepseek-r1:latest"):
#     """
#     Se usa Ollama para validar si el contenido de una sección coincide semánticamente.
#     """
#     # Validación si ambos textos están vacíos, coinciden perfectamente (ej. solo eran títulos)
#     if not texto_actual.strip() and not texto_esperado.strip():
#         return {"coincide": True, "detalles": "Sección sin contenido de texto adicional."}

#     prompt = f"""
#     Eres un auditor de QA automatizado encargado de validar contratos legales y disposiciones financieras.
#     Analiza y compara el 'Texto Real' contra el 'Texto Esperado' para la sección: "{seccion_nombre}".
    
#     Tu objetivo es reportar si el significado cambia, si faltan datos numéricos, fechas o si se alteraron las condiciones.
#     Ignora por completo diferencias menores de formato, espaciados, saltos de línea o puntuaciones menores.

#     TEXTO ESPERADO:
#     {texto_esperado}

#     TEXTO REAL:
#     {texto_actual}

#     Responde ÚNICAMENTE en un formato JSON plano, sin bloques de código de markdown (NO uses ```json), con esta estructura exacta:
#     {{
#         "coincide": true o false,
#         "detalles": "Explicación breve de las diferencias encontradas o vacío si todo está correcto."
#         "Cambio exacto": "Muestra textualmente donde se encuentra la diferencias"
#     }}
#     """
    
#     try:
#         response = ollama.generate(model=model_name, prompt=prompt)
#         # Limpieza por si el modelo rompe la regla y mete marcas de bloque de código
#         clean_response = response['response'].strip().replace("```json", "").replace("```", "")
#         return json.loads(clean_response)
#     except Exception as e:
#         return {"coincide": False, "detalles": f"Error al procesar con IA: {str(e)}"}


# # hybrid/semantic_analyzer.py

# import difflib
# import re


# def limpiar_texto(texto: str) -> str:
#     """
#     Limpia ruido común en textos extraídos de PDFs/documentos.
#     """
#     if not texto:
#         return ""

#     # Normalizar saltos de línea
#     texto = texto.replace('\r\n', '\n').replace('\r', '\n')

#     # Eliminar múltiples espacios
#     texto = re.sub(r'[ \t]+', ' ', texto)

#     # Eliminar líneas vacías repetidas
#     texto = re.sub(r'\n+', '\n', texto)

#     return texto.strip()


# def compare_section_content_with_ai(
#     seccion_nombre,
#     texto_actual,
#     texto_esperado,
#     model_name=None
# ):
#     """
#     Compara el contenido de dos secciones de forma determinista,
#     rápida y limpia.
#     """

#     # Marcamos la variable como usada
#     _ = seccion_nombre
#     _ = model_name

#     # 1. Limpieza
#     t_actual_limpio = limpiar_texto(texto_actual)
#     t_esperado_limpio = limpiar_texto(texto_esperado)

#     # 2. Comparación exacta
#     if t_actual_limpio == t_esperado_limpio:
#         return {
#             "coincide": True,
#             "detalles": "El texto de la sección es 100% idéntico al esperado.",
#             "discrepancias": []
#         }

#     # 3. Comparación línea por línea
#     diferencias = list(
#         difflib.ndiff(
#             t_esperado_limpio.splitlines(),
#             t_actual_limpio.splitlines()
#         )
#     )

#     cambios = [
#         linea for linea in diferencias
#         if linea.startswith('+ ') or linea.startswith('- ')
#     ]

#     return {
#         "coincide": len(cambios) == 0,
#         "detalles": (
#             f"Se detectaron {len(cambios)} líneas con discrepancias "
#             f"en el documento analizado."
#         ),
#         "discrepancias": cambios[:5]
#     }

# # hybrid/semantic_analyzer.py

# import difflib
# import re


# def limpiar_texto(texto: str) -> str:
#     """
#     Limpia ruido común y unifica el texto en un flujo continuo
#     para ignorar saltos de línea y formateos visuales diferentes.
#     """

#     if not texto:
#         return ""

#     # 1. Eliminar backslashes literales si existen
#     texto = texto.replace("\\", "")

#     # 2. Convertir saltos de línea/tabulaciones en espacios
#     texto = (
#         texto.replace("\r\n", " ")
#         .replace("\r", " ")
#         .replace("\n", " ")
#         .replace("\t", " ")
#     )

#     # 3. Reducir múltiples espacios a uno solo
#     texto = re.sub(r"\s+", " ", texto)

#     return texto.strip()


# def compare_section_content_with_ai(
#     seccion_nombre,
#     texto_actual,
#     texto_esperado,
#     model_name=None
# ):
#     """
#     Compara el contenido de dos secciones enfocándose únicamente
#     en cambios reales de palabras, ignorando estructura visual.
#     """

#     # Evitar warnings de variables no usadas
#     _ = seccion_nombre
#     _ = model_name

#     # 1. Limpieza profunda
#     t_actual_limpio = limpiar_texto(texto_actual)
#     t_esperado_limpio = limpiar_texto(texto_esperado)

#     # 2. Comparación exacta
#     if t_actual_limpio == t_esperado_limpio:
#         return {
#             "coincide": True,
#             "detalles": (
#                 "El texto de la sección es "
#                 "100% idéntico en contenido."
#             ),
#             "discrepancias": []
#         }

#     # 3. Comparación por palabras
#     palabras_esperadas = t_esperado_limpio.split()
#     palabras_actuales = t_actual_limpio.split()

#     diferencias = list(
#         difflib.ndiff(
#             palabras_esperadas,
#             palabras_actuales
#         )
#     )

#     # Solo diferencias reales
#     cambios = [
#         linea for linea in diferencias
#         if linea.startswith("+ ") or linea.startswith("- ")
#     ]

#     return {
#         "coincide": len(cambios) == 0,
#         "detalles": (
#             f"Se detectaron {len(cambios)} "
#             f"palabras con discrepancias."
#         ),
#         "discrepancias": cambios[:10]
#     }


# # hybrid/semantic_analyzer.py
# import difflib
# import re

# def limpiar_texto(texto: str) -> str:
#     """Normaliza por completo el texto eliminando ruido visual y saltos de línea."""
#     if not texto:
#         return ""
#     texto = texto.replace("\\", "")
#     texto = texto.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("\t", " ")
#     return re.sub(r"\s+", " ", texto).strip()

# def compare_global_content(texto_actual, texto_esperado, mapa_paginas_actual):
#     """
#     Compara el texto completo palabra por palabra de forma global,
#     detectando cambios textuales exactos y localizando su página.
#     """
#     t_actual_limpio = limpiar_texto(texto_actual)
#     t_esperado_limpio = limpiar_texto(texto_esperado)

#     if t_actual_limpio == t_esperado_limpio:
#         return {
#             "coincide": True,
#             "detalles": "El contenido textual de los documentos es 100% idéntico.",
#             "discrepancias": []
#         }

#     palabras_esperadas = t_esperado_limpio.split()
#     palabras_actuales = t_actual_limpio.split()

#     # Ejecutamos el diff a nivel de palabras individuales
#     diferencias = list(difflib.ndiff(palabras_esperadas, palabras_actuales))

#     cambios_detectados = []
#     idx_actual = 0  # Índice para rastrear la posición en el mapa de páginas

#     for linea in diferencias:
#         if linea.startswith("  "):  # Palabra coincide, avanzamos el puntero del archivo actual
#             idx_actual += 1
#         elif linea.startswith("+ "):  # Palabra extra o cambiada en el actual
#             palabra = linea[2:].strip()
#             # Buscamos de forma segura la página correspondiente en el mapa
#             pagina = mapa_paginas_actual[idx_actual][1] if idx_actual < len(mapa_paginas_actual) else mapa_paginas_actual[-1][1]
#             cambios_detectados.append(f"[Pág {pagina}] Añadido/Modificado: '{palabra}'")
#             idx_actual += 1
#         elif linea.startswith("- "):  # Palabra que faltó en el actual (estaba en el esperado)
#             palabra = linea[2:].strip()
#             # Como faltó en el actual, hacemos referencia a la página actual donde debería ir insertada
#             pagina = mapa_paginas_actual[idx_actual][1] if idx_actual < len(mapa_paginas_actual) else mapa_paginas_actual[-1][1]
#             cambios_detectados.append(f"[Pág {pagina}] Faltante (Esperado): '{palabra}'")

#     return {
#         "coincide": len(cambios_detectados) == 0,
#         "detalles": f"Se detectaron {len(cambios_detectados)} discrepancias de palabras en el texto.",
#         "discrepancias": cambios_detectados[:15]  # Mostramos las primeras 15 discrepancias con su página
#     }

# # hybrid/semantic_analyzer.py
# import difflib
# import re

# def limpiar_texto(texto: str) -> str:
#     """Normaliza por completo el texto eliminando ruido visual y saltos de línea."""
#     if not texto:
#         return ""
#     texto = texto.replace("\\", "")
#     texto = texto.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("\t", " ")
#     return re.sub(r"\s+", " ", texto).strip()

# def compare_global_content(texto_actual, texto_esperado, mapa_paginas_actual):
#     """
#     Compara el texto completo de forma global simulando a Draftable.
#     Agrupa palabras consecutivas modificadas para mostrar el bloque de texto completo.
#     """
#     t_actual_limpio = limpiar_texto(texto_actual)
#     t_esperado_limpio = limpiar_texto(texto_esperado)

#     if t_actual_limpio == t_esperado_limpio:
#         return {
#             "coincide": True,
#             "detalles": "El contenido textual de los documentos es 100% idéntico.",
#             "discrepancias": []
#         }

#     palabras_esperadas = t_esperado_limpio.split()
#     palabras_actuales = t_actual_limpio.split()

#     # Usamos SequenceMatcher para obtener los opcodes (bloques de cambios)
#     matcher = difflib.SequenceMatcher(None, palabras_esperadas, palabras_actuales)
#     opcodes = matcher.get_opcodes()

#     cambios_detectados = []

#     for tag, i1, i2, j1, j2 in opcodes:
#         # tag puede ser: 'replace' (cambio de bloque), 'delete' (se borró texto), 'insert' (se añadió texto)
#         if tag == 'equal':
#             continue

#         # Determinar la página aproximada del cambio usando el mapa de palabras del archivo actual
#         idx_palabra = j1 if j1 < len(mapa_paginas_actual) else len(mapa_paginas_actual) - 1
#         pagina = mapa_paginas_actual[idx_palabra][1] if mapa_paginas_actual else 1

#         # Reconstruir los bloques de texto completos
#         bloque_esperado = " ".join(palabras_esperadas[i1:i2])
#         bloque_actual = " ".join(palabras_actuales[j1:j2])

#         if tag == 'replace':
#             cambios_detectados.append({
#                 "pagina": pagina,
#                 "tipo": "Modificado",
#                 "texto_esperado": bloque_esperado,
#                 "texto_actual": bloque_actual
#             })
            
#         elif tag == 'delete':
#             cambios_detectados.append({
#                 "pagina": pagina,
#                 "tipo": "Faltante (Eliminado)",
#                 "texto_esperado": bloque_esperado,
#                 "texto_actual": ""
#             })
            
#         elif tag == 'insert':
#             cambios_detectados.append({
#                 "pagina": pagina,
#                 "tipo": "Añadido",
#                 "texto_esperado": "",
#                 "texto_actual": bloque_actual
#             })


#     return {
#         "coincide": len(cambios_detectados) == 0,
#         "detalles": f"Se detectaron {len(cambios_detectados)} bloques de texto con discrepancias.",
#         "discrepancias": cambios_detectados
#     }

# # hybrid/semantic_analyzer.py
# import difflib

# def compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map):
#     """
#     Compara las líneas de ambos documentos. Si encuentra diferencias consecutivas,
#     las agrupa en un solo bloque de modificación indicando la página correcta.
#     """
#     # Extraer solo las cadenas de texto para el comparador
#     txt_esperado = [item[0] for item in lineas_esperadas_map]
#     txt_actual = [item[0] for item in lineas_actuales_map]

#     # Desactivamos 'autojunk' para obligar a difflib a revisar el 100% de las palabras
#     matcher = difflib.SequenceMatcher(None, txt_esperado, txt_actual, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     cambios_detectados = []

#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         # Obtener la página real usando el mapeo de la línea actual
#         idx_linea = j1 if j1 < len(lineas_actuales_map) else len(lineas_actuales_map) - 1
#         pagina = lineas_actuales_map[idx_linea][1] if lineas_actuales_map else 1

#         # Reconstruir los bloques de texto (frases u oraciones afectadas)
#         bloque_esperado = " ".join(txt_esperado[i1:i2])
#         bloque_actual = " ".join(txt_actual[j1:j2])

#         # Ignorar si el bloque resultante quedó vacío por limpieza
#         if not bloque_esperado.strip() and not bloque_actual.strip():
#             continue

#         if tag == 'replace':
#             cambios_detectados.append({
#                 "pagina": pagina,
#                 "tipo": "Modificado",
#                 "texto_esperado": bloque_esperado,
#                 "texto_actual": bloque_actual
#             })
#         elif tag == 'delete':
#             cambios_detectados.append({
#                 "pagina": pagina,
#                 "tipo": "Faltante (Eliminado)",
#                 "texto_esperado": bloque_esperado,
#                 "texto_actual": ""
#             })
#         elif tag == 'insert':
#             cambios_detectados.append({
#                 "pagina": pagina,
#                 "tipo": "Añadido",
#                 "texto_esperado": "",
#                 "texto_actual": bloque_actual
#             })

#     return {
#         "coincide": len(cambios_detectados) == 0,
#         "detalles": f"Se detectaron {len(cambios_detectados)} bloques de texto con discrepancias.",
#         "discrepancias": cambios_detectados
#     }

# # hybrid/semantic_analyzer.py
# import difflib

# def compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map):
#     """
#     Compara las líneas de ambos documentos. Agrupa diferencias consecutivas,
#     ignorando por completo los bloques dinámicos marcados con '[]'.
#     """
#     txt_esperado = [item[0] for item in lineas_esperadas_map]
#     txt_actual = [item[0] for item in lineas_actuales_map]

#     # Ajuste fino sin autojunk para detectar cambios exactos
#     matcher = difflib.SequenceMatcher(None, txt_esperado, txt_actual, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     cambios_detectados = []

#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         # Reconstruir los bloques de texto afectados
#         bloque_esperado = " ".join(txt_esperado[i1:i2]).strip()
#         bloque_actual = " ".join(txt_actual[j1:j2]).strip()

#         #  REGLA RECIÉN AÑADIDA: Ignorar marcadores de inserción de datos vacíos
#         # Si el bloque esperado es un corchete vacío o la palabra clave contiene '[]'
#         if bloque_esperado == "[]" or "[]" in bloque_esperado:
#             # Si el tipo era 'replace' y solo cambió el valor del RECA/campo, lo ignoramos
#             # porque sabemos que ahí va un dato dinámico modificado.
#             continue

#         # Evitar ruidos si ambos bloques quedaron vacíos tras un strip
#         if not bloque_esperado and not bloque_actual:
#             continue

#         # Obtener la página real del archivo actual
#         idx_linea = j1 if j1 < len(lineas_actuales_map) else len(lineas_actuales_map) - 1
#         pagina = lineas_actuales_map[idx_linea][1] if lineas_actuales_map else 1

#         if tag == 'replace':
#             cambios_detectados.append({
#                 "pagina": pagina,
#                 "tipo": "Modificado",
#                 "texto_esperado": bloque_esperado,
#                 "texto_actual": bloque_actual
#             })
#         elif tag == 'delete':
#             cambios_detectados.append({
#                 "pagina": pagina,
#                 "tipo": "Faltante (Eliminado)",
#                 "texto_esperado": bloque_esperado,
#                 "texto_actual": ""
#             })
#         elif tag == 'insert':
#             cambios_detectados.append({
#                 "pagina": pagina,
#                 "tipo": "Añadido",
#                 "texto_esperado": "",
#                 "texto_actual": bloque_actual
#             })

#     return {
#         "coincide": len(cambios_detectados) == 0,
#         "detalles": f"Se detectaron {len(cambios_detectados)} bloques de texto con discrepancias reales.",
#         "discrepancias": cambios_detectados
#     }


# # hybrid/semantic_analyzer.py
# import difflib

# def compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map):
#     """
#     Compara las líneas de ambos documentos. Identifica los bloques que sufrieron
#     cambios (incluyendo alteraciones de orden) y los reporta íntegros.
#     """
#     txt_esperado = [item[0] for item in lineas_esperadas_map]
#     txt_actual = [item[0] for item in lineas_actuales_map]

#     # autojunk=False garantiza que cambios de orden con palabras comunes se sigan detectando
#     matcher = difflib.SequenceMatcher(None, txt_esperado, txt_actual, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     cambios_detectados = []

#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         bloque_esperado = " ".join(txt_esperado[i1:i2]).strip()
#         bloque_actual = " ".join(txt_actual[j1:j2]).strip()

#         if not bloque_esperado and not bloque_actual:
#             continue

#         # Obtener la página del archivo actual donde impacta el cambio
#         idx_linea = j1 if j1 < len(lineas_actuales_map) else len(lineas_actuales_map) - 1
#         pagina = lineas_actuales_map[idx_linea][1] if lineas_actuales_map else 1

#         # Mapeamos directamente el tipo de cambio del bloque completo
#         if tag == 'replace':
#             tipo_reporte = "Modificado (Contenido o Orden alterado)"
#         elif tag == 'delete':
#             tipo_reporte = "Faltante (Eliminado)"
#         elif tag == 'insert':
#             tipo_reporte = "Añadido"

#         cambios_detectados.append({
#             "pagina": pagina,
#             "tipo": tipo_reporte,
#             "texto_esperado": bloque_esperado,
#             "texto_actual": bloque_actual
#         })

#     return {
#         "coincide": len(cambios_detectados) == 0,
#         "detalles": f"Se detectaron {len(cambios_detectados)} bloques con discrepancias estructurales o de texto.",
#         "discrepancias": cambios_detectados
#     }

# # hybrid/semantic_analyzer.py
# import difflib
# import re

# def extraer_esqueleto_fijo(texto: str) -> list:
#     """
#     Limpia el texto eliminando corchetes, números, IDs alfanuméricos aislados
#     y signos de puntuación sueltos, devolviendo una lista ordenada con las
#     palabras estáticas reales de la plantilla.
#     """
#     if not texto:
#         return []
        
#     # 1. Eliminar por completo corchetes de plantilla [ ] o []
#     texto = re.sub(r'\[\s*\]', ' ', texto)
#     texto = texto.replace('[', ' ').replace(']', ' ')
    
#     # 2. Separar el texto en palabras individuales
#     palabras = texto.split()
#     palabras_estaticas = []
    
#     for p in palabras:
#         # Limpiar signos de puntuación pegados al final/inicio de la palabra (como ':')
#         p_limpia = re.sub(r'^[^\w\s]|[^\w\s]$', '', p)
        
#         # Saltarse la palabra si quedó vacía
#         if not p_limpia:
#             continue
            
#         # REGLA AUTOMÁTICA: Omitir si la palabra es un dato inyectado:
#         # - Si es un número puro (ej: 14, 607, 1604430833)
#         # - Si es un ID alfanumérico típico de hash/código (ej: J3B94U32)
#         if p_limpia.isdigit():
#             continue
#         if re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]+$', p_limpia):
#             continue
            
#         # Si pasó los filtros, es texto estático del contrato/cabecera
#         palabras_estaticas.append(p_limpia.lower())
        
#     # Ordenamos alfabéticamente para neutralizar los cambios de lectura de PyMuPDF en columnas
#     palabras_estaticas.sort()
#     return palabras_estaticas


# def compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map):
#     """
#     Compara las líneas de ambos documentos de forma global por bloques.
#     Detecta automáticamente cambios en textos legales e ignora el llenado de datos.
#     """
#     txt_esperado = [item[0] for item in lineas_esperadas_map]
#     txt_actual = [item[0] for item in lineas_actuales_map]

#     matcher = difflib.SequenceMatcher(None, txt_esperado, txt_actual, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     cambios_detectados = []

#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         bloque_esperado = " ".join(txt_esperado[i1:i2]).strip()
#         bloque_actual = " ".join(txt_actual[j1:j2]).strip()

#         if not bloque_esperado and not bloque_actual:
#             continue

#         # VERIFICACIÓN AUTOMÁTICA DE PLANTILLA ABSOLUTA
#         # Extraemos las palabras estáticas de ambos bloques. Si los "esqueletos" de texto coinciden,
#         # significa que solo se poblaron datos dinámicos en una estructura idéntica.
#         if extraer_esqueleto_fijo(bloque_esperado) == extraer_esqueleto_fijo(bloque_actual):
#             continue

#         # Obtener la página del archivo actual donde impacta el cambio real
#         idx_linea = j1 if j1 < len(lineas_actuales_map) else len(lineas_actuales_map) - 1
#         pagina = lineas_actuales_map[idx_linea][1] if lineas_actuales_map else 1

#         if tag == 'replace':
#             tipo_reporte = "Modificado (Contenido o Orden alterado)"
#         elif tag == 'delete':
#             tipo_reporte = "Faltante (Eliminado)"
#         elif tag == 'insert':
#             tipo_reporte = "Añadido"

#         cambios_detectados.append({
#             "pagina": pagina,
#             "tipo": tipo_reporte,
#             "texto_esperado": bloque_esperado,
#             "texto_actual": bloque_actual
#         })

#     return {
#         "coincide": len(cambios_detectados) == 0,
#         "detalles": f"Se detectaron {len(cambios_detectados)} bloques con discrepancias estructurales o de texto.",
#         "discrepancias": cambios_detectados
#     }

# # hybrid/semantic_analyzer.py
# import difflib
# import re

# def extraer_esqueleto_fijo(texto: str) -> list:
#     """Elimina datos dinámicos y devuelve palabras estáticas ordenadas."""
#     if not texto:
#         return []
#     texto = re.sub(r'\[\s*\]', ' ', texto)
#     texto = texto.replace('[', ' ').replace(']', ' ')
#     palabras = texto.split()
#     palabras_estaticas = []
#     for p in palabras:
#         p_limpia = re.sub(r'^[^\w\s]|[^\w\s]$', '', p)
#         if not p_limpia:
#             continue
#         if p_limpia.isdigit():
#             continue
#         if re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]+$', p_limpia):
#             continue
#         palabras_estaticas.append(p_limpia.lower())
#     palabras_estaticas.sort()
#     return palabras_estaticas


# def desmenuzar_cambios_bloque(texto_esperado, texto_actual):
#     """
#     Analiza las palabras del bloque y genera una lista secuencial de cambios exactos,
#     mostrando qué partes específicas se reemplazaron, eliminaron o añadieron.
#     """
#     palabras_esp = texto_esperado.split()
#     palabras_act = texto_actual.split()

#     # Comparador por palabras a micro-nivel
#     matcher = difflib.SequenceMatcher(None, palabras_esp, palabras_act, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     desglose = []

#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         sub_esperado = " ".join(palabras_esp[i1:i2])
#         sub_actual = " ".join(palabras_act[j1:j2])

#         if tag == 'replace':
#             desglose.append(f"Cambió: \"{sub_esperado}\" por \"{sub_actual}\"")
#         elif tag == 'delete':
#             desglose.append(f"Eliminó: \"{sub_esperado}\"")
#         elif tag == 'insert':
#             desglose.append(f"Añadió: \"{sub_actual}\"")

#     return desglose


# def compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map):
#     """
#     Compara bloques globales, filtra plantillas dinámicas y desmenuza
#     los cambios internos de las discrepancias reales.
#     """
#     txt_esperado = [item[0] for item in lineas_esperadas_map]
#     txt_actual = [item[0] for item in lineas_actuales_map]

#     matcher = difflib.SequenceMatcher(None, txt_esperado, txt_actual, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     cambios_detectados = []

#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         bloque_esperado = " ".join(txt_esperado[i1:i2]).strip()
#         bloque_actual = " ".join(txt_actual[j1:j2]).strip()

#         if not bloque_esperado and not bloque_actual:
#             continue

#         # Filtrar datos de formulario automáticos
#         if extraer_esqueleto_fijo(bloque_esperado) == extraer_esqueleto_fijo(bloque_actual):
#             continue

#         idx_linea = j1 if j1 < len(lineas_actuales_map) else len(lineas_actuales_map) - 1
#         pagina = lineas_actuales_map[idx_linea][1] if lineas_actuales_map else 1

#         #  DESMENUZA EL BLOQUE DETECTADO
#         cambios_internos = desmenuzar_cambios_bloque(bloque_esperado, bloque_actual)

#         if tag == 'replace':
#             tipo_reporte = "Modificado (Contenido o Orden alterado)"
#         elif tag == 'delete':
#             tipo_reporte = "Faltante (Eliminado)"
#         elif tag == 'insert':
#             tipo_reporte = "Añadido"

#         cambios_detectados.append({
#             "pagina": pagina,
#             "tipo": tipo_reporte,
#             "texto_esperado": bloque_esperado,
#             "texto_actual": bloque_actual,
#             "cambios_internos": cambios_internos  # Estructura limpia para mapear en reportes
#         })

#     return {
#         "coincide": len(cambios_detectados) == 0,
#         "detalles": f"Se detectaron {len(cambios_detectados)} bloques con discrepancias estructurales o de texto.",
#         "discrepancias": cambios_detectados
#     }

# # hybrid/semantic_analyzer.py
# import difflib
# import re

# def extraer_esqueleto_fijo(texto: str) -> list:
#     """Elimina datos dinámicos y devuelve palabras estáticas ordenadas."""
#     if not texto:
#         return []
#     texto = re.sub(r'\[\s*\]', ' ', texto)
#     texto = texto.replace('[', ' ').replace(']', ' ')
#     palabras = texto.split()
#     palabras_estaticas = []
#     for p in palabras:
#         p_limpia = re.sub(r'^[^\w\s]|[^\w\s]$', '', p)
#         if not p_limpia:
#             continue
#         if p_limpia.isdigit():
#             continue
#         if re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]+$', p_limpia):
#             continue
#         palabras_estaticas.append(p_limpia.lower())
#     palabras_estaticas.sort()
#     return palabras_estaticas

# def es_bloque_solo_cabecera(texto: str) -> bool:
#     """
#     Detecta de forma agnóstica si un bloque contiene ÚNICAMENTE palabras 
#     asociadas a campos dinámicos de formularios o metadatos de control.
#     """
#     if not texto:
#         return False
#     # Si al extraer el esqueleto, solo quedan palabras de control típicas de tus cabeceras
#     # Puedes añadir palabras clave de tus formularios de forma genérica
#     palabras_cabecera = {'cliente', 'contrato', 'referencia', 'reca', 'número', 'numero'}
#     esqueleto = extraer_esqueleto_fijo(texto)
    
#     # Si el bloque analizado está vacío de palabras contractuales reales, es una cabecera
#     if not esqueleto:
#         return True
        
#     # Si todas las palabras del bloque pertenecen al set de cabecera, se ignora
#     return all(palabra in palabras_cabecera for palabra in esqueleto)

# def desmenuzar_cambios_bloque(texto_esperado, texto_actual):
#     """Analiza las palabras del bloque y genera una lista secuencial de cambios exactos."""
#     palabras_esp = texto_esperado.split()
#     palabras_act = texto_actual.split()

#     matcher = difflib.SequenceMatcher(None, palabras_esp, palabras_act, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     desglose = []
#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         sub_esperado = " ".join(palabras_esp[i1:i2])
#         sub_actual = " ".join(palabras_act[j1:j2])

#         if tag == 'replace':
#             desglose.append(f"Cambió: \"{sub_esperado}\" por \"{sub_actual}\"")
#         elif tag == 'delete':
#             desglose.append(f"Eliminó: \"{sub_esperado}\"")
#         elif tag == 'insert':
#             desglose.append(f"Añadió: \"{sub_actual}\"")
#     return desglose

# def compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map):
#     """
#     Compara bloques globales de forma inteligente, destruyendo falsos positivos 
#     de cabeceras dinámicas provocados por cruces multi-formato.
#     """
#     txt_esperado = [item[0] for item in lineas_esperadas_map]
#     txt_actual = [item[0] for item in lineas_actuales_map]

#     matcher = difflib.SequenceMatcher(None, txt_esperado, txt_actual, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     cambios_detectados = []

#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         bloque_esperado = " ".join(txt_esperado[i1:i2]).strip()
#         bloque_actual = " ".join(txt_actual[j1:j2]).strip()

#         if not bloque_esperado and not bloque_actual:
#             continue

#         # 🔥 NUEVO FILTRO DE ESCAPE SEGURO: 
#         # Si el bloque esperado o el detectado son exclusivamente datos de cabecera/formulario, se ignoran por completo.
#         if es_bloque_solo_cabecera(bloque_esperado) or es_bloque_solo_cabecera(bloque_actual):
#             continue

#         # Validación estándar por comparación de esqueletos idénticos
#         if extraer_esqueleto_fijo(bloque_esperado) == extraer_esqueleto_fijo(bloque_actual):
#             continue

#         idx_linea = j1 if j1 < len(lineas_actuales_map) else len(lineas_actuales_map) - 1
#         pagina = lineas_actuales_map[idx_linea][1] if lineas_actuales_map else 1

#         cambios_internos = desmenuzar_cambios_bloque(bloque_esperado, bloque_actual)

#         if tag == 'replace':
#             tipo_reporte = "Modificado (Contenido o Orden alterado)"
#         elif tag == 'delete':
#             tipo_reporte = "Faltante (Eliminado)"
#         elif tag == 'insert':
#             tipo_reporte = "Añadido"

#         cambios_detectados.append({
#             "pagina": pagina,
#             "tipo": tipo_reporte,
#             "texto_esperado": bloque_esperado,
#             "texto_actual": bloque_actual,
#             "cambios_internos": cambios_internos
#         })

#     return {
#         "coincide": len(cambios_detectados) == 0,
#         "detalles": f"Se detectaron {len(cambios_detectados)} bloques con discrepancias estructurales o de texto.",
#         "discrepancias": cambios_detectados
#     }

# # hybrid/semantic_analyzer.py
# import difflib
# import re

# def extraer_esqueleto_fijo(texto: str) -> list:
#     """Elimina datos dinámicos y devuelve palabras estáticas ordenadas."""
#     if not texto:
#         return []
#     texto = re.sub(r'\[\s*\]', ' ', texto)
#     texto = texto.replace('[', ' ').replace(']', ' ')
#     palabras = texto.split()
#     palabras_estaticas = []
#     for p in palabras:
#         p_limpia = re.sub(r'^[^\w\s]|[^\w\s]$', '', p)
#         if not p_limpia:
#             continue
#         if p_limpia.isdigit():
#             continue
#         if re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]+$', p_limpia):
#             continue
#         palabras_estaticas.append(p_limpia.lower())
#     palabras_estaticas.sort()
#     return palabras_estaticas

# def es_bloque_solo_cabecera(texto: str) -> bool:
#     """
#     Detecta si un texto contiene ÚNICAMENTE palabras de la cabecera dinámica.
#     """
#     texto_limpio = texto.strip()
#     if not texto_limpio:
#         return False
        
#     palabras_cabecera = {'cliente', 'contrato', 'referencia', 'reca', 'número', 'numero'}
#     esqueleto = extraer_esqueleto_fijo(texto_limpio)
    
#     if not esqueleto:
#         # Si tiene texto pero no tiene esqueleto fijo (solo números/hashes), es cabecera pura
#         return True
        
#     return all(palabra in palabras_cabecera for palabra in esqueleto)

# def desmenuzar_cambios_bloque(texto_esperado, texto_actual):
#     """Analiza las palabras del bloque y genera una lista secuencial de cambios exactos."""
#     palabras_esp = texto_esperado.split()
#     palabras_act = texto_actual.split()

#     matcher = difflib.SequenceMatcher(None, palabras_esp, palabras_act, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     desglose = []
#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         sub_esperado = " ".join(palabras_esp[i1:i2])
#         sub_actual = " ".join(palabras_act[j1:j2])

#         if tag == 'replace':
#             desglose.append(f"Cambió: \"{sub_esperado}\" por \"{sub_actual}\"")
#         elif tag == 'delete':
#             desglose.append(f"Eliminó: \"{sub_esperado}\"")
#         elif tag == 'insert':
#             desglose.append(f"Añadió: \"{sub_actual}\"")
#     return desglose

# def compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map):
#     """Compara bloques globales eliminando falsos positivos de formularios."""
#     txt_esperado = [item[0] for item in lineas_esperadas_map]
#     txt_actual = [item[0] for item in lineas_actuales_map]

#     matcher = difflib.SequenceMatcher(None, txt_esperado, txt_actual, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     cambios_detectados = []

#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         bloque_esperado = " ".join(txt_esperado[i1:i2]).strip()
#         bloque_actual = " ".join(txt_actual[j1:j2]).strip()

#         if not bloque_esperado and not bloque_actual:
#             continue

#         # 🔥 FILTRO CORREGIDO: Si cualquiera de los dos lados es detectado como cabecera, se descarta por completo
#         if es_bloque_solo_cabecera(bloque_esperado) or es_bloque_solo_cabecera(bloque_actual):
#             continue

#         if extraer_esqueleto_fijo(bloque_esperado) == extraer_esqueleto_fijo(bloque_actual):
#             continue

#         idx_linea = j1 if j1 < len(lineas_actuales_map) else len(lineas_actuales_map) - 1
#         pagina = lineas_actuales_map[idx_linea][1] if lineas_actuales_map else 1

#         cambios_internos = desmenuzar_cambios_bloque(bloque_esperado, bloque_actual)

#         if tag == 'replace':
#             tipo_reporte = "Modificado (Contenido o Orden alterado)"
#         elif tag == 'delete':
#             tipo_reporte = "Faltante (Eliminado)"
#         elif tag == 'insert':
#             tipo_reporte = "Añadido"

#         cambios_detectados.append({
#             "pagina": pagina,
#             "tipo": tipo_reporte,
#             "texto_esperado": bloque_esperado,
#             "texto_actual": bloque_actual,
#             "cambios_internos": cambios_internos
#         })

#     return {
#         "coincide": len(cambios_detectados) == 0,
#         "detalles": f"Se detectaron {len(cambios_detectados)} bloques con discrepancias estructurales o de texto.",
#         "discrepancias": cambios_detectados
#     }

# # hybrid/semantic_analyzer.py
# import difflib
# import re

# def extraer_esqueleto_fijo(texto: str) -> list:
#     """Elimina datos dinámicos y devuelve palabras estáticas ordenadas."""
#     if not texto:
#         return []
#     # Ignorar también el marcador que inyectamos en la extracción
#     texto = texto.replace("[DATOS_CABECERA_OMITIDOS]", "")
#     texto = re.sub(r'\[\s*\]', ' ', texto)
#     texto = texto.replace('[', ' ').replace(']', ' ')
#     palabras = texto.split()
#     palabras_estaticas = []
#     for p in palabras:
#         p_limpia = re.sub(r'^[^\w\s]|[^\w\s]$', '', p)
#         if not p_limpia:
#             continue
#         if p_limpia.isdigit():
#             continue
#         if re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]+$', p_limpia):
#             continue
#         palabras_estaticas.append(p_limpia.lower())
#     palabras_estaticas.sort()
#     return palabras_estaticas

# def desmenuzar_cambios_bloque(texto_esperado, texto_actual):
#     """Analiza las palabras del bloque y genera una lista secuencial de cambios exactos."""
#     palabras_esp = texto_esperado.split()
#     palabras_act = texto_actual.split()

#     matcher = difflib.SequenceMatcher(None, palabras_esp, palabras_act, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     desglose = []
#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         sub_esperado = " ".join(palabras_esp[i1:i2])
#         sub_actual = " ".join(palabras_act[j1:j2])

#         if tag == 'replace':
#             desglose.append(f"Cambió: \"{sub_esperado}\" por \"{sub_actual}\"")
#         elif tag == 'delete':
#             desglose.append(f"Eliminó: \"{sub_esperado}\"")
#         elif tag == 'insert':
#             desglose.append(f"Añadió: \"{sub_actual}\"")
#     return desglose

# def compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map):
#     """Compara bloques globales manteniendo compatibilidad total PDF-PDF y DOCX-PDF."""
#     txt_esperado = [item[0] for item in lineas_esperadas_map]
#     txt_actual = [item[0] for item in lineas_actuales_map]

#     matcher = difflib.SequenceMatcher(None, txt_esperado, txt_actual, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     cambios_detectados = []

#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         bloque_esperado = " ".join(txt_esperado[i1:i2]).strip()
#         bloque_actual = " ".join(txt_actual[j1:j2]).strip()

#         if not bloque_esperado and not bloque_actual:
#             continue

#         # Si ambos bloques al quitar datos variables o marcadores son idénticos, se ignoran
#         if extraer_esqueleto_fijo(bloque_esperado) == extraer_esqueleto_fijo(bloque_actual):
#             continue

#         idx_linea = j1 if j1 < len(lineas_actuales_map) else len(lineas_actuales_map) - 1
#         pagina = lineas_actuales_map[idx_linea][1] if lineas_actuales_map else 1

#         cambios_internos = desmenuzar_cambios_bloque(bloque_esperado, bloque_actual)

#         if tag == 'replace':
#             tipo_reporte = "Modificado (Contenido o Orden alterado)"
#         elif tag == 'delete':
#             tipo_reporte = "Faltante (Eliminado)"
#         elif tag == 'insert':
#             tipo_reporte = "Añadido"

#         cambios_detectados.append({
#             "pagina": pagina,
#             "tipo": tipo_reporte,
#             "texto_esperado": bloque_esperado,
#             "texto_actual": bloque_actual,
#             "cambios_internos": cambios_internos
#         })

#     return {
#         "coincide": len(cambios_detectados) == 0,
#         "detalles": f"Se detectaron {len(cambios_detectados)} bloques con discrepancias estructurales o de texto.",
#         "discrepancias": cambios_detectados
#     }

# Modifica solo esta función dentro de hybrid/semantic_analyzer.py

# # hybrid/semantic_analyzer.py
# import difflib
# import re

# def extraer_esqueleto_fijo(texto: str) -> list:
#     """Elimina datos dinámicos, marcas de tablas y devuelve palabras estáticas ordenadas."""
#     if not texto:
#         return []
        
#     # Normalizar strings del texto
#     texto = texto.lower()
#     texto = texto.replace("[datos_cabecera_omitidos]", "")
    
#     # Remover ruido del calendario vacío
#     texto = texto.replace("dd/mm/aaaa", "")
#     texto = texto.replace("pago no.", "").replace("fecha límite de pago", "").replace("monto del pago", "")
    
#     texto = re.sub(r'\[\s*\]', ' ', texto)
#     texto = texto.replace('[', ' ').replace(']', ' ')
    
#     palabras = texto.split()
#     palabras_estaticas = []
#     for p in palabras:
#         p_limpia = re.sub(r'^[^\w\s]|[^\w\s]$', '', p)
#         if not p_limpia:
#             continue
#         if p_limpia.isdigit():
#             continue
#         # Remover signos de pesos sueltos o guiones bajos de firmas
#         if p_limpia == "$" or p_limpia.startswith("_"):
#             continue
#         if re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]+$', p_limpia):
#             continue
#         palabras_estaticas.append(p_limpia)
        
#     palabras_estaticas.sort()
#     return palabras_estaticas

# def desmenuzar_cambios_bloque(texto_esperado, texto_actual):
#     """Analiza las palabras del bloque y genera una lista secuencial de cambios exactos."""
#     palabras_esp = texto_esperado.split()
#     palabras_act = texto_actual.split()

#     matcher = difflib.SequenceMatcher(None, palabras_esp, palabras_act, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     desglose = []
#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         sub_esperado = " ".join(palabras_esp[i1:i2])
#         sub_actual = " ".join(palabras_act[j1:j2])

#         if tag == 'replace':
#             desglose.append(f"Cambió: \"{sub_esperado}\" por \"{sub_actual}\"")
#         elif tag == 'delete':
#             desglose.append(f"Eliminó: \"{sub_esperado}\"")
#         elif tag == 'insert':
#             desglose.append(f"Añadió: \"{sub_actual}\"")
#     return desglose

# def compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map):
#     """Compara bloques globales manteniendo compatibilidad total PDF-PDF y DOCX-PDF."""
#     txt_esperado = [item[0] for item in lineas_esperadas_map]
#     txt_actual = [item[0] for item in lineas_actuales_map]

#     matcher = difflib.SequenceMatcher(None, txt_esperado, txt_actual, autojunk=False)
#     opcodes = matcher.get_opcodes()

#     cambios_detectados = []

#     for tag, i1, i2, j1, j2 in opcodes:
#         if tag == 'equal':
#             continue

#         bloque_esperado = " ".join(txt_esperado[i1:i2]).strip()
#         bloque_actual = " ".join(txt_actual[j1:j2]).strip()

#         if not bloque_esperado and not bloque_actual:
#             continue

#         # Si ambos bloques al quitar datos variables o marcadores son idénticos, se ignoran
#         if extraer_esqueleto_fijo(bloque_esperado) == extraer_esqueleto_fijo(bloque_actual):
#             continue

#         idx_linea = j1 if j1 < len(lineas_actuales_map) else len(lineas_actuales_map) - 1
#         pagina = lineas_actuales_map[idx_linea][1] if lineas_actuales_map else 1

#         cambios_internos = desmenuzar_cambios_bloque(bloque_esperado, bloque_actual)

#         if tag == 'replace':
#             tipo_reporte = "Modificado (Contenido o Orden alterado)"
#         elif tag == 'delete':
#             tipo_reporte = "Faltante (Eliminado)"
#         elif tag == 'insert':
#             tipo_reporte = "Añadido"

#         cambios_detectados.append({
#             "pagina": pagina,
#             "tipo": tipo_reporte,
#             "texto_esperado": bloque_esperado,
#             "texto_actual": bloque_actual,
#             "cambios_internos": cambios_internos
#         })

#     return {
#         "coincide": len(cambios_detectados) == 0,
#         "detalles": f"Se detectaron {len(cambios_detectados)} bloques con discrepancias estructurales o de texto.",
#         "discrepancias": cambios_detectados
#     }

# hybrid/semantic_analyzer.py
import difflib
import re

def normalizar_texto_bloque(texto: str) -> str:
    """
    Normaliza comillas inteligentes/curvas y remueve marcadores de cabecera
    para asegurar consistencia total entre las comparaciones PDF-PDF y DOCX-PDF.
    """
    if not texto:
        return ""
    # Reemplazar comillas curvas (Word/Nativas) por comillas rectas estándar
    texto = texto.replace('“', '"').replace('”', '"')
    # Quitar los marcadores inyectados de la extracción de PDF en flujos híbridos
    texto = texto.replace("[DATOS_CABECERA_OMITIDOS]", "")
    # Resolver dobles espacios residuales
    return " ".join(texto.split())

def extraer_esqueleto_fijo(texto: str) -> list:
    """Elimina datos dinámicos, marcas de tablas y devuelve palabras estáticas ordenadas."""
    if not texto:
        return []
        
    # Normalizar strings del texto
    texto = texto.lower()
    texto = texto.replace("[datos_cabecera_omitidos]", "")
    
    # Remover ruido del calendario vacío
    texto = texto.replace("dd/mm/aaaa", "")
    texto = texto.replace("pago no.", "").replace("fecha límite de pago", "").replace("monto del pago", "")
    
    texto = re.sub(r'\[\s*\]', ' ', texto)
    texto = texto.replace('[', ' ').replace(']', ' ')
    
    palabras = texto.split()
    palabras_estaticas = []
    for p in palabras:
        p_limpia = re.sub(r'^[^\w\s]|[^\w\s]$', '', p)
        if not p_limpia:
            continue
        if p_limpia.isdigit():
            continue
        # Remover signos de pesos sueltos o guiones bajos de firmas
        if p_limpia == "$" or p_limpia.startswith("_"):
            continue
        if re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]+$', p_limpia):
            continue
        palabras_estaticas.append(p_limpia)
        
    palabras_estaticas.sort()
    return palabras_estaticas

def desmenuzar_cambios_bloque(texto_esperado, texto_actual):
    """Analiza las palabras del bloque normalizado y genera una lista secuencial de cambios exactos."""
    # Normalización previa de comillas y ruidos de formato antes de lanzar el SequenceMatcher
    txt_esp_norm = normalizar_texto_bloque(texto_esperado)
    txt_act_norm = normalizar_texto_bloque(texto_actual)

    palabras_esp = txt_esp_norm.split()
    palabras_act = txt_act_norm.split()

    matcher = difflib.SequenceMatcher(None, palabras_esp, palabras_act, autojunk=False)
    opcodes = matcher.get_opcodes()

    desglose = []
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            continue

        sub_esperado = " ".join(palabras_esp[i1:i2])
        sub_actual = " ".join(palabras_act[j1:j2])

        if tag == 'replace':
            desglose.append(f"Cambió: \"{sub_esperado}\" por \"{sub_actual}\"")
        elif tag == 'delete':
            desglose.append(f"Eliminó: \"{sub_esperado}\"")
        elif tag == 'insert':
            desglose.append(f"Añadió: \"{sub_actual}\"")
    return desglose

def compare_global_content_blocks(lineas_actuales_map, lineas_esperadas_map):
    """Compara bloques globales manteniendo compatibilidad total PDF-PDF y DOCX-PDF."""
    txt_esperado = [item[0] for item in lineas_esperadas_map]
    txt_actual = [item[0] for item in lineas_actuales_map]

    matcher = difflib.SequenceMatcher(None, txt_esperado, txt_actual, autojunk=False)
    opcodes = matcher.get_opcodes()

    cambios_detectados = []

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            continue

        bloque_esperado = " ".join(txt_esperado[i1:i2]).strip()
        bloque_actual = " ".join(txt_actual[j1:j2]).strip()

        if not bloque_esperado and not bloque_actual:
            continue

        # Si ambos bloques al quitar datos variables o marcadores son idénticos, se ignoran
        if extraer_esqueleto_fijo(bloque_esperado) == extraer_esqueleto_fijo(bloque_actual):
            continue

        idx_linea = j1 if j1 < len(lineas_actuales_map) else len(lineas_actuales_map) - 1
        pagina = lineas_actuales_map[idx_linea][1] if lineas_actuales_map else 1

        # Obtener los cambios internos sanitizados
        cambios_internos = desmenuzar_cambios_bloque(bloque_esperado, bloque_actual)

        # Si tras limpiar las comillas y los tokens de cabecera no hay diferencias reales, se omite el bloque
        if not cambios_internos:
            continue

        if tag == 'replace':
            tipo_reporte = "Modificado (Contenido o Orden alterado)"
        elif tag == 'delete':
            tipo_reporte = "Faltante (Eliminado)"
        elif tag == 'insert':
            tipo_reporte = "Añadido"

        cambios_detectados.append({
            "pagina": pagina,
            "tipo": tipo_reporte,
            "texto_esperado": bloque_esperado,
            "texto_actual": bloque_actual,
            "cambios_internos": cambios_internos
        })

    return {
        "coincide": len(cambios_detectados) == 0,
        "detalles": f"Se detectaron {len(cambios_detectados)} bloques con discrepancias estructurales o de texto.",
        "discrepancias": cambios_detectados
    }