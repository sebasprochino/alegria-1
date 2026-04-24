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

    async def execute_with_retry(self, func, *args, **kwargs):
        """Ejecuta una corrutina con política de reintentos soberana (Fix #4)."""
        import asyncio
        import random
        import logging
        
        logger = logging.getLogger("ALEGRIA_ADAPTER_RETRY")
        max_retries = 5
        base_delay = 3 # segundos
        
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                # Detectamos 429 (Rate Limit) o 503 (Unavailable) en el mensaje de error
                if any(kw in error_str for kw in ["429", "rate limit", "too many requests", "503", "unavailable"]):
                    wait_time = (base_delay * (2 ** attempt)) + (random.random() * 1.5)
                    logger.warning(f"⚠️ [RETRY] Rate Limit detectado. Intento {attempt+1}/{max_retries}. Esperando {wait_time:.2f}s...")
                    await asyncio.sleep(wait_time)
                else:
                    # Otros errores se relanzan
                    raise e
        
        # Si agotamos reintentos
        raise RuntimeError(f"Máximo de reintentos ({max_retries}) agotado por Rate Limit. El motor soberano está saturado.")
    
    @abstractmethod
    async def generate(self, prompt: str, system: str = None, 
                       temperature: float = 0.7) -> str:
        """Genera una respuesta dado un prompt."""
        pass
    
    @abstractmethod
    async def generate_stream(self, prompt: str, system: str = None,
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
    def provider_name(self) -> str:
        """Nombre del proveedor (por defecto 'base')."""
        return "base"