"""
Gemini Adapter
==============
Adaptador para Google Gemini API usando la nueva librería `google-genai`.
"""

import logging
import os
from typing import List, AsyncGenerator
from .base_adapter import BaseLLMAdapter

logger = logging.getLogger("ALEGRIA_GEMINI")

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash-preview-09-2025",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview"
]

class GeminiAdapter(BaseLLMAdapter):
    """Adaptador para Google Gemini (google-genai SDK)."""
    
    provider_name = "gemini"
    
    def __init__(self, api_key: str, model: str = None, endpoint: str = None):
        # Usar el modelo solicitado o el default estable
        self.model = model or "gemini-2.5-flash"
        
        # Mapping de compatibilidad mínima
        if self.model == "gemini-2.0-flash":
            self.model = "gemini-2.0-flash-exp"
            
        super().__init__(api_key, self.model, endpoint)
        self.client = None
        self.is_configured = False
        self._setup_client()
    
    def _setup_client(self):
        """Inicializa el cliente Gemini."""
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.is_configured = True
            logger.info(f"✅ Gemini configurado con modelo: {self.model}")
        except ImportError:
            logger.warning("⚠️ google-genai SDK no instalado. Usar: pip install google-genai")
        except Exception as e:
            logger.error(f"❌ Error configurando Gemini: {e}")
    
    async def generate(self, prompt: str, system: str = None,
                       temperature: float = 0.7) -> str:
        """Genera respuesta usando Gemini."""
        return await self.chat([{"role": "user", "content": prompt}], system, temperature)

    async def chat(self, messages: List[dict], system: str = None, temperature: float = 0.7) -> str:
        if not self.client:
            raise RuntimeError("Gemini no está configurado")
        
        try:
            config = {"temperature": temperature}
            if system:
                config["system_instruction"] = system
            
            gemini_contents = []
            for m in messages:
                content = m.get("content", "")
                if isinstance(content, str):
                    gemini_contents.append(content)
                elif isinstance(content, list):
                    for part in content:
                        if part.get("type") == "text":
                            gemini_contents.append(part.get("text", ""))
                        elif part.get("type") == "image_url":
                            # base64 data url
                            url = part["image_url"]["url"]
                            if url.startswith("data:image"):
                                import base64
                                from google.genai import types
                                # data:image/jpeg;base64,XXXX
                                meta, data_b64 = url.split(',', 1)
                                mime_type = meta.split(':')[1].split(';')[0]
                                gemini_contents.append(
                                    types.Part.from_bytes(
                                        data=base64.b64decode(data_b64),
                                        mime_type=mime_type
                                    )
                                )
            
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=gemini_contents,
                config=config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Error en Gemini: {e}")
            raise e
    
    async def generate_stream(self, prompt: str, system: str = None,
                              temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """Genera respuesta en streaming."""
        if not self.client:
            yield "Error: Gemini no está configurado"
            return
        
        try:
            config = {"temperature": temperature}
            if system:
                config["system_instruction"] = system
                
            async for chunk in await self.client.aio.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=config
            ):
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def get_available_models(self) -> List[str]:
        """Retorna modelos de Gemini."""
        return GEMINI_MODELS
    
    async def generate_image(self, prompt: str) -> str:
        """
        Genera una imagen usando Imagen 3 (via google-genai SDK).
        Retorna la imagen en base64 Data URL.
        """
        if not self.client:
            raise RuntimeError("Gemini no está configurado")
        
        try:
            logger.info(f"🎨 [GEMINI IMAGEN] Generando visual: {prompt[:50]}...")
            
            # Imagen 3 usa un método específico en el SDK
            # Nota: Imagen usa sync por ahora en muchas versiones del SDK genai, 
            # pero intentamos delegar a thread si es necesario o usar el método directo.
            import asyncio
            from functools import partial

            # El modelo de imagen suele ser fijo para este propósito
            image_model = "imagen-3.0-generate-001"
            
            # run_in_executor para no bloquear el loop si el SDK es sincrónico para imágenes
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(
                    self.client.models.generate_images,
                    model=image_model,
                    prompt=prompt
                )
            )
            
            # La respuesta contiene una lista de imágenes. Tomamos la primera.
            if not response.generated_images:
                raise RuntimeError("No se generaron imágenes")
            
            image_bytes = response.generated_images[0].image.data
            import base64
            b64_data = base64.b64encode(image_bytes).decode('utf-8')
            return f"data:image/png;base64,{b64_data}"

        except Exception as e:
            logger.error(f"❌ Error en Gemini Imagen: {e}")
            raise e

    def validate_connection(self) -> bool:
        """Valida la API key."""
        if not self.client:
            return False
        try:
            # Test simple síncrono (list models no está en v1alpha? probamos generate simple)
            # O mejor, usamos models.list si existe, o un generate dummy.
            # La nueva lib tiene client.models.list()
            # Pero es paginado.
            # Probamos una generación simple.
            self.client.models.generate_content(
                model=self.model,
                contents="Test",
            )
            return True
        except:
            return False
