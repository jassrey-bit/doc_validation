# hybrid/visual_extractor.py
import os
import fitz  # PyMuPDF
from docx2pdf import convert

def convertir_documento_a_imagenes(ruta_archivo: str, carpeta_salida: str = "temp_images") -> list:
    """
    Toma un archivo .pdf o .docx, convierte las páginas a imágenes PNG 
    y devuelve la lista de rutas de esas imágenes.
    """
    os.makedirs(carpeta_salida, exist_ok=True)
    rutas_imagenes = []
    
    nombre_base, extension = os.path.splitext(os.path.basename(ruta_archivo))
    extension = extension.lower()
    
    ruta_pdf_final = ruta_archivo
    archivo_temporal_pdf = None

    # Si es DOCX, se convierte temporalmente a PDF con Word
    if extension == ".docx":
        print(f"📄 Convertiendo DOCX a PDF temporal: {ruta_archivo}")
        archivo_temporal_pdf = os.path.join(carpeta_salida, f"{nombre_base}_temp.pdf")
        convert(ruta_archivo, archivo_temporal_pdf)
        ruta_pdf_final = archivo_temporal_pdf

    # Renderizar el PDF a imágenes PNG
    if os.path.exists(ruta_pdf_final):
        doc = fitz.open(ruta_pdf_final)
        print(f"📸 Generando {len(doc)} capturas de imagen para Gemini...")
        
        for num_pagina in range(len(doc)):
            pagina = doc.load_page(num_pagina)
            # Matrix(2.0, 2.0) da excelente resolución/nitidez para la IA
            pix = pagina.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
            
            ruta_img = os.path.join(carpeta_salida, f"{nombre_base}_pag_{num_pagina + 1}.png")
            pix.save(ruta_img)
            rutas_imagenes.append(ruta_img)
            
        doc.close()

    # Limpieza del PDF temporal
    if archivo_temporal_pdf and os.path.exists(archivo_temporal_pdf):
        os.remove(archivo_temporal_pdf)

    return rutas_imagenes