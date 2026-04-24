import os
import logging
from typing import List, AsyncGenerator, Dict, Any
from .base_adapter import BaseLLMAdapter

logger = logging.getLogger("ALEGRIA_GROQ")

GROQ_FREE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-3.2-90b-vision-preview",
    "meta-llama/llama-4-scout-17b-16e-instruct", # Vision 2026
    "qwen/qwen3-32b",
    "mixtral-8x7b-32768"
]

class GroqAdapter(BaseLLMAdapter):
    provider_name = "groq"
    
    def __init__(self, api_key: str = None, model: str = None, endpoint: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or "llama-3.3-70b-versatile"
        self.endpoint = endpoint
        self.client = None
        self.is_configured = False
        self._setup()
    
    def _setup(self):
        if not self.api_key: return 
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            self.is_configured = True
            logger.info(f"✅ Groq configurado con modelo: {self.model}")
        except ImportError:
            logger.warning("⚠️ Groq SDK no instalado. Usar: pip install groq")
        except Exception as e:
            logger.error(f"❌ Error configurando Groq: {e}")
    
    async def generate(self, prompt: str, system: str = None, temperature: float = 0.7) -> str:
        # Mantener compatibilidad con prompt string
        return await self.chat(messages=[{"role": "user", "content": prompt}], system=system, temperature=temperature)

    async def chat(self, messages: List[Dict[str, Any]], system: str = None, temperature: float = 0.7) -> str:
        if not self.is_configured: return "Error: Groq no configurado"
        try:
            msgs = []
            if system: msgs.append({"role": "system", "content": system})
            
            for m in messages:
                content = m.get("content", "")
                # Soporte para multimodal (Llama 3.2 Vision / Llama 4 Scout)
                if isinstance(content, list):
                    # Ya viene formateado para el SDK
                    msgs.append(m)
                elif isinstance(content, str) and (content.startswith("data:image") or "http" in content):
                    # Si es una URL o base64 directo en content string (legacy/helper)
                    msgs.append({
                        "role": m["role"],
                        "content": [
                            {"type": "text", "text": "Analiza esta imagen:"},
                            {"type": "image_url", "image_url": {"url": content}}
                        ]
                    })
                else:
                    msgs.append(m)
            
            # Helper para reintentos (Fix #4)
            async def _call_groq():
                return self.client.chat.completions.create(
                    model=self.model,
                    messages=msgs,
                    temperature=temperature
                )

            res = await self.execute_with_retry(_call_groq)
            return res.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ [GROQ] Error fatal tras reintentos: {e}")
            raise e

    async def generate_stream(self, *args, **kwargs): yield "Streaming no config"
    def get_available_models(self): return GROQ_FREE_MODELS
    def validate_connection(self): return self.is_configured