"""
Claude Adapter
==============
Adaptador para Anthropic Claude API.
"""

import logging
import os
from typing import List, AsyncGenerator
from .base_adapter import BaseLLMAdapter

logger = logging.getLogger("ALEGRIA_CLAUDE")

CLAUDE_MODELS = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022",
    "claude-3-opus-20240229",
]

class ClaudeAdapter(BaseLLMAdapter):
    """Adaptador para Anthropic Claude."""
    
    provider_name = "claude"
    
    def __init__(self, api_key: str = None, model: str = None, endpoint: str = None):
        super().__init__(api_key or os.getenv("ANTHROPIC_API_KEY"), model or "claude-3-5-sonnet-20241022", endpoint)
        self.client = None
        self.is_configured = False
        self._setup_client()
    
    def _setup_client(self):
        """Inicializa el cliente Anthropic."""
        try:
            from anthropic import Anthropic
            if self.api_key:
                self.client = Anthropic(api_key=self.api_key)
                self.is_configured = True
                logger.info(f"✅ Claude configurado con modelo: {self.model}")
        except ImportError:
            logger.warning("⚠️ Anthropic SDK no instalado. Usar: pip install anthropic")
        except Exception as e:
            logger.error(f"❌ Error configurando Claude: {e}")
    
    async def generate(self, prompt: str, system: str = None,
                       temperature: float = 0.7) -> str:
        """Genera respuesta usando Claude."""
        if not self.client:
            raise RuntimeError("Claude no está configurado")
        
        try:
            params = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }
            if system:
                params["system"] = system
                
            response = self.client.messages.create(**params)
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"❌ Error en Claude: {e}")
            raise e
    
    async def generate_stream(self, prompt: str, system: str = None,
                               temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """Genera respuesta en streaming."""
        if not self.client:
            yield "Error: Claude no está configurado"
            return
        
        try:
            params = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "stream": True,
            }
            if system:
                params["system"] = system
                
            with self.client.messages.stream(**params) as stream:
                for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def get_available_models(self) -> List[str]:
        """Retorna modelos de Claude."""
        return CLAUDE_MODELS
    
    def validate_connection(self) -> bool:
        """Valida la API key."""
        return self.is_configured
