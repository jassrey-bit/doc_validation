# listar_modelos.py
import os
from google import genai

try:
    print("🔄 Conectando con Google AI Studio y listando modelos disponibles...\n")
    client = genai.Client()
    
    # Listamos todos los modelos vinculados a tu API Key
    modelos = client.models.list()
    
    print(f"{'NOMBRE DEL MODELO':<35} | {'OPERACIONES SOPORTADAS'}")
    print("-" * 75)
    
    for modelo in modelos:
        # Filtramos para mostrar principalmente los que soportan generación de contenido
        if "generateContent" in modelo.supported_methods:
            print(f"{modelo.name:<35} | Soportado")
            
except Exception as e:
    print(f"❌ Error al listar modelos: {str(e)}")
    print("Asegúrate de tener tu GEMINI_API_KEY cargada en la terminal.")