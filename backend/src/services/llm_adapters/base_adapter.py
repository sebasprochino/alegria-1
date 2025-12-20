"""
Base LLM Adapter
================
Clase abstracta para todos los adaptadores de LLM.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, AsyncGenerator


class BaseLLMAdapter(ABC):
    """Interfaz común para todos los adaptadores de LLM."""
    
    def __init__(self, api_key: str, model: str = None, endpoint: str = None):
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.is_configured = False
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = None, 
                       temperature: float = 0.7) -> str:
        """Genera una respuesta dado un prompt."""
        pass
    
    @abstractmethod
    async def generate_stream(self, prompt: str, system_prompt: str = None,
                              temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """Genera respuesta en streaming."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Retorna lista de modelos disponibles para este proveedor."""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Valida que la conexión/API key funcione."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nombre del proveedor."""
        pass
