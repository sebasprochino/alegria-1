"""
Ollama Adapter
==============
Adaptador para Ollama (modelos locales).
"""

import logging
import httpx
from typing import List, AsyncGenerator

from .base_adapter import BaseLLMAdapter

logger = logging.getLogger("ALEGRIA_OLLAMA")


class OllamaAdapter(BaseLLMAdapter):
    """Adaptador para Ollama (local)."""
    
    provider_name = "ollama"
    
    def __init__(self, api_key: str = None, model: str = None, endpoint: str = None):
        super().__init__(api_key or "", model or "llama3.1:8b", endpoint or "http://localhost:11434")
        self.is_configured = False
        self._check_connection()
    
    def _check_connection(self):
        """Verifica si Ollama está corriendo."""
        try:
            response = httpx.get(f"{self.endpoint}/api/version", timeout=2.0)
            if response.status_code == 200:
                self.is_configured = True
                logger.info(f"✅ Ollama conectado en {self.endpoint}")
        except:
            logger.warning(f"⚠️ Ollama no disponible en {self.endpoint}")
    
    async def generate(self, prompt: str, system: str = None,
                       temperature: float = 0.7) -> str:
        """Genera respuesta usando Ollama."""
        if not self.is_configured:
            raise RuntimeError("Ollama no está disponible")
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature}
                }
                
                if system:
                    payload["system"] = system
                
                response = await client.post(
                    f"{self.endpoint}/api/generate",
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    return response.json().get("response", "")
                else:
                    raise RuntimeError(f"Ollama error {response.status_code}: {response.text}")
                    
        except Exception as e:
            logger.error(f"❌ Error en Ollama: {e}")
            raise e
    
    async def generate_stream(self, prompt: str, system: str = None,
                              temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """Genera respuesta en streaming."""
        if not self.is_configured:
            yield "Error: Ollama no está disponible"
            return
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {"temperature": temperature}
                }
                
                if system:
                    payload["system"] = system
                
                async with client.stream(
                    "POST",
                    f"{self.endpoint}/api/generate",
                    json=payload,
                    timeout=60.0
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def get_available_models(self) -> List[str]:
        """Retorna modelos instalados en Ollama."""
        try:
            response = httpx.get(f"{self.endpoint}/api/tags", timeout=5.0)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m.get("name", "") for m in models]
        except:
            pass
        
        # Modelos comunes si no podemos consultar
        return [
            "llama3.1:8b",
            "mistral",
            "gemma2",
            "phi3",
            "deepseek-r1",
        ]
    
    def validate_connection(self) -> bool:
        """Valida que Ollama esté corriendo."""
        try:
            response = httpx.get(f"{self.endpoint}/api/version", timeout=2.0)
            return response.status_code == 200
        except:
            return False
