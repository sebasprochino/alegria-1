"""
HuggingFace Adapter
====================
Adaptador para HuggingFace Inference API.
"""

import logging
import requests
from typing import List, AsyncGenerator

from .base_adapter import BaseLLMAdapter

logger = logging.getLogger("ALEGRIA_HUGGINGFACE")

HF_MODELS = [
    "meta-llama/Llama-3.2-3B-Instruct",
    "meta-llama/Llama-3.2-1B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "google/gemma-2-9b-it",
    "microsoft/Phi-3-mini-4k-instruct",
]


class HuggingFaceAdapter(BaseLLMAdapter):
    """Adaptador para HuggingFace Inference API."""
    
    provider_name = "huggingface"
    
    def __init__(self, api_key: str, model: str = None, endpoint: str = None):
        super().__init__(api_key, model or "meta-llama/Llama-3.2-3B-Instruct", endpoint)
        self.endpoint = endpoint or f"https://api-inference.huggingface.co/models/{self.model}"
        self.is_configured = bool(api_key)
        if self.is_configured:
            logger.info(f"✅ HuggingFace configurado con modelo: {self.model}")
    
    async def generate(self, prompt: str, system: str = None,
                       temperature: float = 0.7) -> str:
        """Genera respuesta usando HuggingFace."""
        if not self.is_configured:
            return "Error: HuggingFace no está configurado"
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            # Formatear prompt (HF Inference API espera texto plano o formato específico según el modelo)
            # Para modelos Instruct, intentamos un formato genérico
            full_prompt = ""
            if system:
                full_prompt += f"System: {system}\n"
            full_prompt += f"User: {prompt}\nAssistant:"
            
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 1024,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{self.model}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                return f"Error de HuggingFace ({response.status_code}): {response.text}"
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "Sin respuesta")
            return str(result)
            
        except Exception as e:
            logger.error(f"❌ Error en HuggingFace: {e}")
            return f"Error de HuggingFace: {str(e)}"
    
    async def generate_stream(self, prompt: str, system: str = None,
                               temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """Genera respuesta en streaming (No soportado nativamente en este adaptador simple)."""
        response = await self.generate(prompt, system, temperature)
        yield response
    
    def get_available_models(self) -> List[str]:
        """Retorna modelos de HuggingFace."""
        return HF_MODELS
    
    def validate_connection(self) -> bool:
        """Valida la API key."""
        return bool(self.api_key)
