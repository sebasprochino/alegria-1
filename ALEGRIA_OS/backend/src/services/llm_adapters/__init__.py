"""
ALEGR-IA LLM Adapters
=====================
"""

from .base_adapter import BaseLLMAdapter
from .groq_adapter import GroqAdapter
from .openai_adapter import OpenAIAdapter
from .gemini_adapter import GeminiAdapter
from .ollama_adapter import OllamaAdapter
from .fireworks_adapter import FireworksAdapter
from .huggingface_adapter import HuggingFaceAdapter
from .claude_adapter import ClaudeAdapter

# Mapa de proveedores
ADAPTER_MAP = {
    "groq": GroqAdapter,
    "openai": OpenAIAdapter,
    "gemini": GeminiAdapter,
    "ollama": OllamaAdapter,
    "fireworks": FireworksAdapter,
    "huggingface": HuggingFaceAdapter,
    "claude": ClaudeAdapter,
}

def get_adapter(provider_name: str):
    return ADAPTER_MAP.get(provider_name.lower())

__all__ = ["BaseLLMAdapter", "get_adapter"]