class CoreError(Exception):
    """Base para todos los errores del núcleo de comparación de documentos."""


class ExtractionError(CoreError):
    """La extracción de texto/estructura de un documento falló."""


class VisualUnavailableError(CoreError):
    """La capa visual (conversión a imágenes o veredicto de IA) no pudo completarse."""


class AIProviderError(CoreError):
    """Un proveedor de IA no está configurado correctamente o falló al responder."""
