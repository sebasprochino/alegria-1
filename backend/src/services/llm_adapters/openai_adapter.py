"""
OpenAI Adapter
==============
Adaptador para OpenAI API (GPT-4, GPT-3.5, etc.)
"""

import logging
from typing import List, AsyncGenerator

logger = logging.getLogger("ALEGRIA_OPENAI")

OPENAI_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
]


class OpenAIAdapter:
    """Adaptador para OpenAI."""
    
    provider_name = "openai"
    
    def __init__(self, api_key: str, model: str = None, endpoint: str = None):
        self.api_key = api_key
        self.model = model or "gpt-4o-mini"
        self.endpoint = endpoint
        self.client = None
        self.is_configured = False
        self._setup_client()
    
    def _setup_client(self):
        """Inicializa el cliente OpenAI."""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.is_configured = True
            logger.info(f"✅ OpenAI configurado con modelo: {self.model}")
        except ImportError:
            logger.warning("⚠️ OpenAI SDK no instalado. Usar: pip install openai")
        except Exception as e:
            logger.error(f"❌ Error configurando OpenAI: {e}")
    
    async def generate(self, prompt: str, system_prompt: str = None,
                       temperature: float = 0.7) -> str:
        """Genera respuesta usando OpenAI."""
        if not self.client:
            return "Error: OpenAI no está configurado"
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2048
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Error en OpenAI: {e}")
            return f"Error de OpenAI: {str(e)}"
    
    async def generate_stream(self, prompt: str, system_prompt: str = None,
                              temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """Genera respuesta en streaming."""
        if not self.client:
            yield "Error: OpenAI no está configurado"
            return
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
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
        """Retorna modelos de OpenAI."""
        return OPENAI_MODELS
    
    def validate_connection(self) -> bool:
        """Valida la API key."""
        if not self.client:
            return False
        try:
            self.client.models.list()
            return True
        except:
            return False
