import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from core.exceptions import AIProviderError

load_dotenv()

# Cadena de modelos por defecto, del más ligero al más robusto. Si uno falla
# (saturado, deprecado, cuota agotada) se prueba el siguiente automáticamente.
_DEFAULT_TEXT_MODELS = ["gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-flash-latest"]
_DEFAULT_VISION_MODELS = ["gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-flash-latest"]

# Errores que NO vale la pena reintentar con otro modelo: afectan a la API key
# o a la solicitud en su conjunto, no a un modelo en particular (p.ej. Gemini
# responde 400 INVALID_ARGUMENT para una API key inválida, no 401/403).
_NON_RETRYABLE_CODES = {400, 401, 403}


def _parse_model_list(env_value: str | None, default: list[str]) -> list[str]:
    if not env_value:
        return default
    return [m.strip() for m in env_value.split(",") if m.strip()]


class GeminiProvider:
    """
    Implementación de AIProvider sobre la API de Gemini (google-genai), con
    fallback automático a través de una lista de modelos: si el modelo actual
    responde con un error transitorio o específico de ese modelo (saturado,
    cuota agotada, deprecado), se reintenta con el siguiente de la lista
    antes de darse por vencido.
    """

    def __init__(
        self,
        api_key: str | None = None,
        text_models: list[str] | None = None,
        vision_models: list[str] | None = None,
    ):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self._api_key:
            raise AIProviderError(
                "GEMINI_API_KEY no está configurada. Defínela en .env o pásala explícitamente a GeminiProvider."
            )

        self._text_models = text_models or _parse_model_list(os.getenv("GEMINI_TEXT_MODELS"), _DEFAULT_TEXT_MODELS)
        self._vision_models = vision_models or _parse_model_list(
            os.getenv("GEMINI_VISION_MODELS"), _DEFAULT_VISION_MODELS
        )

        try:
            self._client = genai.Client(api_key=self._api_key)
        except Exception as e:
            raise AIProviderError(f"No se pudo inicializar el cliente de Gemini: {e}") from e

    def _generate_with_fallback(self, models: list[str], contents: list, config: types.GenerateContentConfig) -> str:
        errores: list[str] = []

        for modelo in models:
            try:
                response = self._client.models.generate_content(model=modelo, contents=contents, config=config)
                return response.text.strip()
            except errors.APIError as e:
                errores.append(f"{modelo}: {e.code} {e.status}")
                if e.code in _NON_RETRYABLE_CODES:
                    raise AIProviderError(f"Fallo de autenticación/permisos con Gemini ({modelo}): {e}") from e
                continue  # error transitorio o específico del modelo: probar el siguiente
            except Exception as e:
                errores.append(f"{modelo}: {e}")
                continue

        raise AIProviderError(
            f"Todos los modelos de Gemini fallaron ({', '.join(models)}). Detalle: {'; '.join(errores)}"
        )

    def generate_text(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=temperature)
        return self._generate_with_fallback(self._text_models, [prompt], config)

    def generate_multimodal(
        self,
        prompt: str,
        images: list[Path],
        *,
        system_instruction: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        contents: list = [prompt]
        for ruta_img in images:
            if not Path(ruta_img).exists():
                continue
            with open(ruta_img, "rb") as f:
                contents.append(types.Part.from_bytes(data=f.read(), mime_type="image/png"))

        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=temperature)
        return self._generate_with_fallback(self._vision_models, contents, config)
