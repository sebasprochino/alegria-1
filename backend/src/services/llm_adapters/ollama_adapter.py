"""
Ollama Adapter
==============
Adaptador para Ollama (modelos locales).
"""

import logging
import httpx
from typing import List, AsyncGenerator

logger = logging.getLogger("ALEGRIA_OLLAMA")


class OllamaAdapter:
    """Adaptador para Ollama (local)."""
    
    provider_name = "ollama"
    
    def __init__(self, api_key: str = None, model: str = None, endpoint: str = None):
        # Ollama no requiere API key
        self.api_key = api_key or ""
        self.model = model or "llama3.2"
        self.endpoint = endpoint or "http://localhost:11434"
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
    
    async def generate(self, prompt: str, system_prompt: str = None,
                       temperature: float = 0.7) -> str:
        """Genera respuesta usando Ollama."""
        if not self.is_configured:
            return "Error: Ollama no está disponible"
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature}
                }
                
                if system_prompt:
                    payload["system"] = system_prompt
                
                response = await client.post(
                    f"{self.endpoint}/api/generate",
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    return response.json().get("response", "")
                else:
                    return f"Error: {response.text}"
                    
        except Exception as e:
            logger.error(f"❌ Error en Ollama: {e}")
            return f"Error de Ollama: {str(e)}"
    
    async def generate_stream(self, prompt: str, system_prompt: str = None,
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
                
                if system_prompt:
                    payload["system"] = system_prompt
                
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
            "llama3.2",
            "llama3.1",
            "mistral",
            "mixtral",
            "codellama",
            "phi3",
        ]
    
    def validate_connection(self) -> bool:
        """Valida que Ollama esté corriendo."""
        try:
            response = httpx.get(f"{self.endpoint}/api/version", timeout=2.0)
            return response.status_code == 200
        except:
            return False
