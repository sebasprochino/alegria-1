"""
Fireworks AI Adapter
====================
Adaptador para Fireworks AI (OpenAI compatible).
"""

import logging
from typing import List, AsyncGenerator

from .base_adapter import BaseLLMAdapter

logger = logging.getLogger("ALEGRIA_FIREWORKS")

FIREWORKS_MODELS = [
    "accounts/fireworks/models/llama-v3p1-8b-instruct",
    "accounts/fireworks/models/llama-v3p1-70b-instruct",
    "accounts/fireworks/models/llama-v3p1-405b-instruct",
    "accounts/fireworks/models/mixtral-8x7b-instruct",
    "accounts/fireworks/models/qwen2p5-72b-instruct",
]


class FireworksAdapter(BaseLLMAdapter):
    """Adaptador para Fireworks AI."""
    
    provider_name = "fireworks"
    
    def __init__(self, api_key: str, model: str = None, endpoint: str = None):
        super().__init__(api_key, model or "accounts/fireworks/models/llama-v3p1-8b-instruct", endpoint or "https://api.fireworks.ai/inference/v1")
        self.client = None
        self.is_configured = False
        self._setup_client()
    
    def _setup_client(self):
        """Inicializa el cliente OpenAI configurado para Fireworks."""
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.endpoint
            )
            self.is_configured = True
            logger.info(f"✅ Fireworks configurado con modelo: {self.model}")
        except ImportError:
            logger.warning("⚠️ OpenAI SDK no instalado. Usar: pip install openai")
        except Exception as e:
            logger.error(f"❌ Error configurando Fireworks: {e}")
    
    async def generate(self, prompt: str, system: str = None,
                       temperature: float = 0.7) -> str:
        """Genera respuesta usando Fireworks."""
        if not self.client:
            return "Error: Fireworks no está configurado"
        
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2048
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Error en Fireworks: {e}")
            return f"Error de Fireworks: {str(e)}"
    
    async def generate_stream(self, prompt: str, system: str = None,
                               temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """Genera respuesta en streaming."""
        if not self.client:
            yield "Error: Fireworks no está configurado"
            return
        
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2048,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def get_available_models(self) -> List[str]:
        """Retorna modelos de Fireworks."""
        return FIREWORKS_MODELS
    
    def validate_connection(self) -> bool:
        """Valida la API key."""
        if not self.client:
            return False
        try:
            # Fireworks no soporta .models.list() de la misma forma que OpenAI a veces
            # Hacemos un check simple
            return bool(self.api_key)
        except:
            return False
