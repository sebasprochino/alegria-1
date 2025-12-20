"""
Gemini Adapter
==============
Adaptador para Google Gemini API.
"""

import logging
from typing import List, AsyncGenerator

logger = logging.getLogger("ALEGRIA_GEMINI")

GEMINI_MODELS = [
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
    "gemini-1.0-pro",
]


class GeminiAdapter:
    """Adaptador para Google Gemini."""
    
    provider_name = "gemini"
    
    def __init__(self, api_key: str, model: str = None, endpoint: str = None):
        self.api_key = api_key
        self.model_name = model or "gemini-2.0-flash-exp"
        self.endpoint = endpoint
        self.model = None
        self.is_configured = False
        self._setup_client()
    
    def _setup_client(self):
        """Inicializa el cliente Gemini."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                self.model_name,
                system_instruction="Eres Anima, un asistente inteligente de ALEGR-IA. Responde con claridad y personalidad."
            )
            self.is_configured = True
            logger.info(f"✅ Gemini configurado con modelo: {self.model_name}")
        except ImportError:
            logger.warning("⚠️ Gemini SDK no instalado. Usar: pip install google-generativeai")
        except Exception as e:
            logger.error(f"❌ Error configurando Gemini: {e}")
    
    async def generate(self, prompt: str, system_prompt: str = None,
                       temperature: float = 0.7) -> str:
        """Genera respuesta usando Gemini."""
        if not self.model:
            return "Error: Gemini no está configurado"
        
        try:
            # Gemini usa system_instruction en el constructor
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nUsuario: {prompt}"
            
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config={"temperature": temperature}
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Error en Gemini: {e}")
            return f"Error de Gemini: {str(e)}"
    
    async def generate_stream(self, prompt: str, system_prompt: str = None,
                              temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """Genera respuesta en streaming."""
        if not self.model:
            yield "Error: Gemini no está configurado"
            return
        
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nUsuario: {prompt}"
            
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config={"temperature": temperature},
                stream=True
            )
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def get_available_models(self) -> List[str]:
        """Retorna modelos de Gemini."""
        return GEMINI_MODELS
    
    def validate_connection(self) -> bool:
        """Valida la API key."""
        if not self.model:
            return False
        try:
            # Test simple síncrono
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            models = genai.list_models()
            return len(list(models)) > 0
        except:
            return False
