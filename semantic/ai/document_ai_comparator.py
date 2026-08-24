import ollama

class DocumentAIComparator:

    def compare(self, expected_text, actual_text):

        prompt = f"""
        Eres un analista financiero experto
        en validación documental.

        Compara ambos documentos y detecta:

        - diferencias importantes
        - cambios semánticos
        - cambios numéricos
        - riesgos potenciales
        - modificaciones relevantes
        - la cantidad de diferencias

        DOCUMENTO ESPERADO:

        {expected_text}

        DOCUMENTO ACTUAL:

        {actual_text}
    

        Genera:
        1. Resumen ejecutivo
        2. Diferencias encontradas (Muestra entre comillas las diferencias)
        3. Riesgos potenciales 
        4. Conclusión
        """

        response = ollama.chat(

            model="qwen2.5:3b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]