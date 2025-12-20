"""
ALEGR-IA LLM Adapters
=====================
Adaptadores unificados para diferentes proveedores de LLM.
"""

from .base_adapter import BaseLLMAdapter
from .groq_adapter import GroqAdapter
from .openai_adapter import OpenAIAdapter
from .gemini_adapter import GeminiAdapter
from .ollama_adapter import OllamaAdapter

__all__ = [
    "BaseLLMAdapter",
    "GroqAdapter", 
    "OpenAIAdapter",
    "GeminiAdapter",
    "OllamaAdapter"
]

# Mapa de proveedores
ADAPTER_MAP = {
    "groq": GroqAdapter,
    "openai": OpenAIAdapter,
    "gemini": GeminiAdapter,
    "ollama": OllamaAdapter,
}

def get_adapter(provider_name: str):
    """Obtiene la clase de adaptador para un proveedor."""
    return ADAPTER_MAP.get(provider_name.lower())
