import ollama

class StructuredAIAnalyzer:

    def analyze(self, differences):

        prompt = f"""
        Eres un auditor financiero.

        Analiza las siguientes discrepancias
        encontradas en un documento estructurado:

        {differences}
        
        Si no encuentras diferencias ignora los puntos 4, 3 y 2

        Genera:

        1. Resumen ejecutivo
        2. Riesgos detectados
        3. Diferencias críticas (Muestra entre comillas las diferencias)
        4. Impacto potencial
        5. Recomendaciones
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