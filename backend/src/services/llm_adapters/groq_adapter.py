"""
Groq Adapter
============
Adaptador para Groq Cloud - Modelos gratuitos ultrarrápidos.
"""

import logging
from typing import List, AsyncGenerator, Optional

logger = logging.getLogger("ALEGRIA_GROQ")

# Modelos gratuitos conocidos de Groq
GROQ_FREE_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile", 
    "llama-3.2-1b-preview",
    "llama-3.2-3b-preview",
    "llama-3.2-11b-vision-preview",
    "llama-3.2-90b-vision-preview",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]


class GroqAdapter:
    """Adaptador para Groq Cloud."""
    
    provider_name = "groq"
    
    def __init__(self, api_key: str, model: str = None, endpoint: str = None):
        self.api_key = api_key
        self.model = model or "llama-3.1-8b-instant"
        self.endpoint = endpoint or "https://api.groq.com/openai/v1"
        self.client = None
        self.is_configured = False
        self._setup_client()
    
    def _setup_client(self):
        """Inicializa el cliente Groq."""
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            self.is_configured = True
            logger.info(f"✅ Groq configurado con modelo: {self.model}")
        except ImportError:
            logger.warning("⚠️ Groq SDK no instalado. Usar: pip install groq")
        except Exception as e:
            logger.error(f"❌ Error configurando Groq: {e}")
    
    async def generate(self, prompt: str, system_prompt: str = None,
                       temperature: float = 0.7) -> str:
        """Genera respuesta usando Groq."""
        if not self.client:
            return "Error: Groq no está configurado correctamente"
        
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
            logger.error(f"❌ Error en Groq: {e}")
            return f"Error de Groq: {str(e)}"
    
    async def generate_stream(self, prompt: str, system_prompt: str = None,
                              temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """Genera respuesta en streaming."""
        if not self.client:
            yield "Error: Groq no está configurado"
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
        """Retorna modelos gratuitos de Groq."""
        return GROQ_FREE_MODELS
    
    def validate_connection(self) -> bool:
        """Valida la API key de Groq."""
        if not self.client:
            return False
        try:
            # Test simple
            self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except:
            return False
