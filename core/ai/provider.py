from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class AIProvider(Protocol):
    """
    Contrato mínimo que debe cumplir cualquier proveedor de IA usado por el
    núcleo (descubrimiento de secciones, severidad, veredicto visual). No es
    una clase base: cualquier proveedor futuro (OpenAI, Anthropic, etc.) solo
    necesita implementar estos dos métodos, sin heredar de nada.
    """

    def generate_text(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float = 0.2,
    ) -> str: ...

    def generate_multimodal(
        self,
        prompt: str,
        images: list[Path],
        *,
        system_instruction: str | None = None,
        temperature: float = 0.2,
    ) -> str: ...
