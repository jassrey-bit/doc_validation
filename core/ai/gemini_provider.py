import os
import time
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from core.exceptions import AIProviderError

load_dotenv()

# Cadena de modelos por defecto, del más ligero al más robusto. Si uno falla
# (saturado, deprecado, cuota agotada) se prueba el siguiente automáticamente.
_DEFAULT_TEXT_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-flash-latest",
]
_DEFAULT_VISION_MODELS = list(_DEFAULT_TEXT_MODELS)

# Errores que NO vale la pena reintentar con otro modelo: afectan a la API key
# o a la solicitud en su conjunto, no a un modelo en particular (p.ej. Gemini
# responde 400 INVALID_ARGUMENT para una API key inválida, no 401/403).
_NON_RETRYABLE_CODES = {400, 401, 403}

# Cuántos modelos de la cadena se consultan a la vez: se usa la primera
# respuesta válida. La latencia de Gemini varía muchísimo entre modelos y
# entre minutos (de 1s a 40s, o 503 si está saturado), así que "correr" dos
# modelos en paralelo recorta mucho la espera frente a probarlos uno por uno.
_PARALLEL_MODELS = 2
# Tope por llamada: pasado este tiempo el modelo se da por fallido y su lugar
# lo toma el siguiente de la cadena.
_REQUEST_TIMEOUT_SECONDS = 45
# Si fallan todos los modelos (típicamente 503 generalizado), se espera y se
# recorre la cadena otra vez. La primera vuelta no espera entre modelos.
_ROUNDS = 2
_BACKOFF_SECONDS = 3.0

# Nivel de "thinking" por tipo de tarea. Clasificar discrepancias o extraer
# títulos no necesita razonamiento: con el nivel por defecto el modelo tarda
# decenas de segundos en tareas que resuelve en 1-3s con MINIMAL.
_TEXT_THINKING_LEVEL = types.ThinkingLevel.MINIMAL
_VISION_THINKING_LEVEL = types.ThinkingLevel.LOW


def _parse_model_list(env_value: str | None, default: list[str]) -> list[str]:
    if not env_value:
        return default
    return [m.strip() for m in env_value.split(",") if m.strip()]


class GeminiProvider:
    """
    Implementación de AIProvider sobre la API de Gemini (google-genai), con
    fallback automático a través de una lista de modelos (consultando varios
    en paralelo y usando la primera respuesta): si un modelo
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
            self._client = genai.Client(
                api_key=self._api_key,
                http_options=types.HttpOptions(timeout=_REQUEST_TIMEOUT_SECONDS * 1000),
            )
        except Exception as e:
            raise AIProviderError(f"No se pudo inicializar el cliente de Gemini: {e}") from e

    def _call_model(self, modelo: str, contents: list, config: types.GenerateContentConfig) -> str:
        try:
            response = self._client.models.generate_content(model=modelo, contents=contents, config=config)
        except errors.APIError as e:
            if e.code == 400 and config.thinking_config is not None:
                # No todos los modelos aceptan thinking_level: se reintenta sin él.
                sin_thinking = config.model_copy(update={"thinking_config": None})
                return self._call_model(modelo, contents, sin_thinking)
            if e.code in _NON_RETRYABLE_CODES:
                raise AIProviderError(f"Fallo de autenticación/permisos con Gemini ({modelo}): {e}") from e
            raise
        return response.text.strip()

    def _race_models(
        self, models: list[str], contents: list, config: types.GenerateContentConfig, errores: list[str]
    ) -> str | None:
        """Consulta hasta `_PARALLEL_MODELS` modelos a la vez y devuelve la
        primera respuesta válida; cada fallo libera su lugar para el siguiente
        modelo de la cadena. Devuelve None si fallan todos."""
        pendientes = iter(models)
        executor = ThreadPoolExecutor(max_workers=_PARALLEL_MODELS)
        en_curso: dict[Future, str] = {}

        def lanzar_siguiente() -> None:
            modelo = next(pendientes, None)
            if modelo is not None:
                en_curso[executor.submit(self._call_model, modelo, contents, config)] = modelo

        try:
            for _ in range(_PARALLEL_MODELS):
                lanzar_siguiente()

            while en_curso:
                terminados, _ = wait(en_curso, return_when=FIRST_COMPLETED)
                for future in terminados:
                    modelo = en_curso.pop(future)
                    try:
                        return future.result()
                    except AIProviderError:
                        raise
                    except errors.APIError as e:
                        errores.append(f"{modelo}: {e.code} {e.status}")
                    except Exception as e:
                        errores.append(f"{modelo}: {type(e).__name__} {e}".strip())
                    lanzar_siguiente()
            return None
        finally:
            # Las llamadas más lentas que sigan en vuelo se abandonan: su
            # resultado ya no hace falta.
            executor.shutdown(wait=False, cancel_futures=True)

    def _generate_with_fallback(self, models: list[str], contents: list, config: types.GenerateContentConfig) -> str:
        errores: list[str] = []

        for ronda in range(_ROUNDS):
            if ronda > 0:
                time.sleep(_BACKOFF_SECONDS)
            errores.clear()
            resultado = self._race_models(models, contents, config, errores)
            if resultado is not None:
                return resultado

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
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            thinking_config=types.ThinkingConfig(thinking_level=_TEXT_THINKING_LEVEL),
        )
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

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            thinking_config=types.ThinkingConfig(thinking_level=_VISION_THINKING_LEVEL),
        )
        return self._generate_with_fallback(self._vision_models, contents, config)
