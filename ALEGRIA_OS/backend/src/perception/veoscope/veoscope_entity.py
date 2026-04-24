"""
AGENTE VEOSCOPE — src/perception/veoscope/veoscope_entity.py
==========================================================
El "Ojo Clínico" de ALEGR-IA OS.
Especializado en percepción visual, branding y semiótica.

Traduce imagen/video/marca a lenguaje técnico y sugerencias de identidad.
Soberanía visual activa.
"""

from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("VEOSCOPE")


# ─── Configuración y Prompts de Sistema ───────────────────────────────────────

_SYSTEM_GENERAL = """
Eres VEOSCOPE, el subsistema de percepción visual de ALEGR-IA OS.
Tu función es el 'Análisis Clínico' de estímulos visuales.

REGLAS DE OPERACIÓN:
1. Sé objetivo y descriptivo. No uses placeholders.
2. Identifica: Composición, Iluminación, Texturas, Colores (HEX si es posible) y Estilo.
3. Si se te pide, extrae el ADN de marca o realiza OCR.
4. Mantén un tono técnico, profesional y soberano.
"""

_SYSTEM_OCR = """
Eres el módulo OCR de VEOSCOPE. Tu única misión es extraer texto de imágenes.
No interpretes, solo transcribe con precisión quirúrgica.
"""


# ─── Helpers Multimodales ─────────────────────────────────────────────────────

def _build_vision_content(image_data: Any, prefix: str = "") -> List[Dict[str, Any]]:
    """
    Construye el bloque de contenido multimodal para los proveedores.
    """
    content = []
    if prefix:
        content.append({"type": "text", "text": prefix})
    
    if isinstance(image_data, str):
        # Asumimos que si empieza con data: es base64, si no es una URL/Path
        if image_data.startswith("data:"):
            content.append({
                "type": "image_url",
                "image_url": {"url": image_data}
            })
        else:
            # Podría ser un path local o URL pública
            content.append({
                "type": "image_url",
                "image_url": {"url": image_data}
            })
    return content


async def _call_vision_model(
    image_data: Any,
    prompt: str,
    system: str,
    model: str,
    api_key: str,
    provider: str,
) -> str:
    """
    Llamada genérica a modelos de visión (Gemini, OpenAI, Groq).
    """
    from src.services.provider_registry import provider_registry

    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": _build_vision_content(image_data) + [{"type": "text", "text": prompt}]
        }
    ]

    prov = provider.lower()
    
    # Delegamos al registry/cascade que ya maneja todos los proveedores (Gemini, Groq, OpenAI)
    # de forma unificada usando los adapters correctos (google-genai, etc.)
    return await provider_registry.chat(
        messages=messages,
        system=system,
        model=model
    )


# ─── Entidad Veoscope ─────────────────────────────────────────────────────────

class VeoscopeAgent:
    """
    Agente de Percepción Visual.
    Responsable de 'ver' y 'entender' assets visuales para el sistema.
    """

    def __init__(self):
        self._history: List[Dict[str, Any]] = []
        logger.info("👁️ [VEOSCOPE] Agente inicializado.")

    async def process(
        self,
        query: str,
        image_data: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Punto de entrada principal para procesos de visión.
        """
        context = context or {}
        image_data = image_data or context.get("image")
        provider_config = self._load_provider_config()

        # Determinar intención del análisis
        q_lower = query.lower()
        
        if "ocr" in q_lower or "extrae texto" in q_lower:
            return await self._extract_text(image_data, provider_config)
        
        if "marca" in q_lower or "branding" in q_lower or "adn visual" in q_lower:
            return await self._analyze_brand(image_data, provider_config)
        
        if "compara" in q_lower or "diferencias" in q_lower:
            return await self._compare_visuals(image_data, context, provider_config)

        # Por defecto: Análisis descriptivo general
        images_list = context.get("images", [])
        video_data = context.get("video")
        
        return await self._analyze_image(
            image_data=image_data,
            query=query,
            provider_config=provider_config,
            images=images_list,
            video=video_data
        )

    # ─── Implementaciones de Modos ────────────────────────────────────────────

    async def _analyze_image(
        self,
        image_data: Any,
        query: str,
        provider_config: Optional[Dict[str, Any]],
        images: Optional[List[Any]] = None,
        video: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Análisis descriptivo completo. Soporta múltiples imágenes y contexto de video.
        """
        model, api_key, provider = self._resolve_vision_model(provider_config)
        if not api_key:
            return self._no_provider_error()

        try:
            combined_content = []
            
            # 1. Agregar imágenes
            target_images = images if images and len(images) > 0 else ([image_data] if image_data else [])
            for i, img in enumerate(target_images):
                combined_content.extend(_build_vision_content(img, f"Referencia Visual {i+1}:"))
            
            # 2. Agregar contexto de video
            if video:
                combined_content.append({"type": "text", "text": "### CONTEXTO DE VIDEO ADJUNTO\nAnaliza la continuidad basándote en este archivo."})

            combined_content.append({"type": "text", "text": query or "Analizá estas referencias en detalle."})

            messages = [
                {"role": "system", "content": _SYSTEM_GENERAL},
                {"role": "user", "content": combined_content},
            ]

            prov = provider.lower()
            result = ""

            # El registry ya maneja Gemini correctamente usando google-genai
            # No duplicamos lógica aquí.
            pass

            if prov == "openai":
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=api_key)
                resp = await client.chat.completions.create(
                    model=model, messages=messages, max_tokens=2048
                )
                result = resp.choices[0].message.content
            
            if not result:
                from src.services.provider_registry import provider_registry
                result = await provider_registry.chat(
                    messages=messages,
                    system=_SYSTEM_GENERAL,
                    model=model
                )

            self._history.append({"role": "assistant", "content": result})
            return {
                "status": "ok",
                "content": result,
                "type": "image_analysis",
                "model_used": model,
            }
        except Exception as e:
            logger.exception("[VEOSCOPE] Error en análisis multimodal")
            return {"status": "error", "content": f"Error analizando referencias: {e}"}

    async def _extract_text(
        self,
        image_data: Any,
        provider_config: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Extrae texto visible de la imagen."""
        model, api_key, provider = self._resolve_vision_model(provider_config)
        if not api_key:
            return self._no_provider_error()
        try:
            raw_text = await _call_vision_model(
                image_data=image_data,
                prompt="Extraé todo el texto visible en esta imagen. Solo el texto, en orden de lectura.",
                system=_SYSTEM_OCR,
                model=model,
                api_key=api_key,
                provider=provider,
            )
            return { "status": "ok", "content": raw_text, "type": "ocr", "model_used": model }
        except Exception as e:
            return {"status": "error", "content": f"Error en OCR: {e}"}

    async def _analyze_brand(
        self,
        image_data: Any,
        provider_config: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Análisis clínico de branding."""
        model, api_key, provider = self._resolve_vision_model(provider_config)
        if not api_key:
            return self._no_provider_error()
        
        try:
            sys_prompt = "Eres el Agente Perceptivo VEOSCOPE. Analizas la identidad y el ADN visual de imágenes. La imagen puede ser un logo corporativo, un diseño gráfico, o una foto de una persona (Personal Branding). DEBES responder ÚNICAMENTE con un objeto JSON válido, sin delimitadores Markdown."
            user_prompt = """Analiza la imagen enviada y extrae su identidad visual (ya sea una persona, un estilo de vida o un logo corporativo). Devuelve ESTRICTAMENTE este JSON:
{
  "adn_visual": {
    "composicion": "Breve análisis de la forma, sujeto o composición",
    "estilo": "Estilo dominante o arquetipo visual",
    "colores": ["#hex1", "#hex2", "#hex3"]
  },
  "contexto_narrativo": {
    "voz": "Si esta marca/persona hablara, ¿cómo sonaría su voz/identidad?",
    "mood": "Emoción principal que evoca"
  },
  "sugerencias_marca": [
    "Sugerencia creativa 1 basada en la imagen",
    "Sugerencia creativa 2 basada en la imagen"
  ]
}"""
            res = await _call_vision_model(
                image_data=image_data,
                prompt=user_prompt,
                system=sys_prompt,
                model=model,
                api_key=api_key,
                provider=provider,
            )
            return {"status": "ok", "content": res, "type": "brand_analysis", "model_used": model}
        except Exception as e:
            return {"status": "error", "content": f"Error en marca: {e}"}

    async def _compare_visuals(
        self,
        image_data: Any,
        context: Dict[str, Any],
        provider_config: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Compara imágenes."""
        second_image = context.get("image_2") or context.get("compare_with")
        return await self._analyze_image(
            image_data=image_data,
            query="Compará estas imágenes.",
            provider_config=provider_config,
            images=[image_data, second_image] if second_image else [image_data]
        )

    def _resolve_vision_model(
        self,
        provider_config: Optional[Dict[str, Any]],
    ) -> tuple[str, str, str]:
        from src.core.modality_router import modality_router
        result = modality_router.detect(
            message="[Análisis Visual Requerido]",
            provider_config=provider_config,
        )
        model = result.get("model_override") or "llama-3.2-90b-vision-preview"
        provider = result.get("provider_type") or "groq"
        api_key = os.getenv(f"{provider.upper()}_API_KEY", "")
        if provider_config and provider_config.get("api_key"):
            api_key = provider_config["api_key"]
        return model, api_key, provider

    def _load_provider_config(self) -> Optional[Dict[str, Any]]:
        try:
            from src.services.provider_registry import provider_registry
            return provider_registry.get_active_config()
        except: return None

    @staticmethod
    def _no_provider_error() -> Dict[str, Any]:
        return {"status": "error", "content": "No hay proveedor configurado."}

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._history)


def create_veoscope() -> VeoscopeAgent:
    return VeoscopeAgent()
