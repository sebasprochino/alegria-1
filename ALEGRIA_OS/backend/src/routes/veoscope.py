"""
ALEGRIA_OS — src/routes/veoscope.py

Endpoint REST para VEOSCOPE: el observador visual soberano.

Rutas:
  POST /veoscope/analyze    → análisis general / OCR / marca / comparación
  GET  /veoscope/status     → estado del agente + proveedor de visión activo
  GET  /veoscope/formats    → formatos de imagen soportados

Author: Sebastián Fernández
"""

from __future__ import annotations

import base64
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

logger = logging.getLogger("VEOSCOPE_ROUTES")

router = APIRouter()

# ─── Schemas ──────────────────────────────────────────────────────────────────


class VeoAnalyzeRequest(BaseModel):
    """Cuerpo para análisis visual. La imagen se pasa como URL o base64."""

    message: str = Field(
        default="Analizá esta imagen",
        description="Instrucción del operador para VEOSCOPE.",
    )
    image_url: Optional[str] = Field(
        default=None,
        description="URL pública de la imagen (http/https o data-URI).",
    )
    image_base64: Optional[str] = Field(
        default=None,
        description="Imagen codificada en base64 (sin prefijo data:…).",
    )
    image_2_url: Optional[str] = Field(
        default=None,
        description="Segunda imagen para análisis comparativo.",
    )
    provider_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Override de configuración del proveedor (opcional).",
    )


class VeoAnalyzeResponse(BaseModel):
    status: str
    content: str
    type: Optional[str] = None
    model_used: Optional[str] = None
    raw_text: Optional[str] = None
    requires_input: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None


# ─── Singleton del agente ─────────────────────────────────────────────────────

_veoscope: Any = None


def _get_veoscope():
    global _veoscope
    if _veoscope is None:
        from src.perception.veoscope import create_veoscope
        _veoscope = create_veoscope()
    return _veoscope


# ─── Helper: construir contexto desde request ─────────────────────────────────


def _build_context(req: VeoAnalyzeRequest) -> Dict[str, Any]:
    ctx: Dict[str, Any] = {}

    if req.image_url:
        ctx["image"] = req.image_url
    elif req.image_base64:
        ctx["image"] = req.image_base64

    if req.image_2_url:
        ctx["image_2"] = req.image_2_url

    if req.provider_config:
        ctx["provider_config"] = req.provider_config

    return ctx


# ─── Endpoints ────────────────────────────────────────────────────────────────


@router.post("/analyze", response_model=VeoAnalyzeResponse)
async def analyze_image(req: VeoAnalyzeRequest) -> VeoAnalyzeResponse:
    """
    Análisis visual soberano.

    VEOSCOPE detecta automáticamente el tipo de análisis según el mensaje:
     - OCR → "extrae el texto", "lee esto", "qué dice"
     - Marca → "analiza el logo", "branding", "identidad visual"
     - Comparar → "compara", "diferencia", "versus"
     - General → cualquier otra consulta
    """
    if not req.image_url and not req.image_base64:
        return VeoAnalyzeResponse(
            status="question",
            content=(
                "¿Qué imagen querés que analice? Podés:\n"
                "- Enviar `image_url` con una URL pública\n"
                "- Enviar `image_base64` con la imagen codificada"
            ),
            requires_input="image",
        )

    agent = _get_veoscope()
    context = _build_context(req)

    try:
        result = await agent.process(message=req.message, context=context)
        return VeoAnalyzeResponse(**result)
    except Exception as e:
        logger.exception("[VEOSCOPE_ROUTES] Error inesperado en /analyze")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-upload", response_model=VeoAnalyzeResponse)
async def analyze_image_upload(
    message: str = Form(default="Analizá esta imagen"),
    file: UploadFile = File(...),
) -> VeoAnalyzeResponse:
    """
    Análisis visual vía carga directa de archivo.
    Acepta: image/png, image/jpeg, image/webp, image/gif.
    """
    allowed_mimes = {"image/png", "image/jpeg", "image/webp", "image/gif", "image/bmp"}
    if file.content_type not in allowed_mimes:
        raise HTTPException(
            status_code=415,
            detail=f"Tipo de archivo no soportado: {file.content_type}",
        )

    raw_bytes = await file.read()
    b64 = base64.b64encode(raw_bytes).decode()
    image_str = f"data:{file.content_type};base64,{b64}"

    agent = _get_veoscope()
    context = {"image": image_str}

    try:
        result = await agent.process(query=message, context=context)
        return VeoAnalyzeResponse(**result)
    except Exception as e:
        logger.exception("[VEOSCOPE_ROUTES] Error en /analyze-upload")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def veoscope_status() -> Dict[str, Any]:
    """
    Estado operativo de VEOSCOPE.
    Informa si el proveedor de visión está configurado y cuál modelo usaría.
    """
    import os
    from src.core.modality_router import modality_router

    try:
        # Intentar resolver el proveedor activo
        provider_config = None
        try:
            from src.services.provider_registry import provider_registry
            provider_config = provider_registry.get_active_config()
        except Exception:
            pass

        routing = modality_router.detect(
            message="[Análisis Visual Requerido]",
            provider_config=provider_config,
        )

        # Verificar API key
        provider = routing.get("provider_type", "groq")
        key_map = {
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
        }
        env_key = key_map.get(provider, "GROQ_API_KEY")
        has_key = bool(os.getenv(env_key))

        return {
            "agent": "VEOSCOPE",
            "status": "ready" if has_key else "degraded",
            "vision_available": has_key,
            "model": routing.get("model_override"),
            "provider": provider,
            "missing_key": None if has_key else env_key,
            "capabilities": [
                "analizar_imagen",
                "extraer_texto_ocr",
                "analizar_marca",
                "comparar_visuales",
            ],
        }
    except Exception as e:
        logger.exception("[VEOSCOPE_ROUTES] Error en /status")
        return {"agent": "VEOSCOPE", "status": "error", "error": str(e)}


@router.get("/formats")
async def supported_formats() -> Dict[str, Any]:
    """Formatos de imagen aceptados por VEOSCOPE."""
    return {
        "formats": ["png", "jpg", "jpeg", "gif", "webp", "bmp"],
        "max_size_mb": 20,
        "input_modes": ["url", "base64", "upload"],
    }


# ─── Integración Brand Studio ─────────────────────────────────────────────────

class SaveBrandRequest(BaseModel):
    image: str
    analysis: Dict[str, Any]
    brand_id: str


@router.post("/save-to-brand")
async def save_to_brand(req: SaveBrandRequest):
    """
    Exporta una captura clínica de VeoScope directamente al Brand Studio.
    """
    try:
        from src.services.brand_service import service as brand_service
        
        result = brand_service.add_to_gallery(
            brand_id=req.brand_id,
            image_data=req.image,
            analysis=req.analysis
        )
        
        if result:
            return {"status": "success", "message": "Captura anclada al Brand Studio", "entry": result}
        else:
            raise HTTPException(status_code=400, detail="No se pudo guardar en la galería")
            
    except Exception as e:
        logger.exception("[VEOSCOPE_ROUTES] Error guardando en Brand Studio")
        raise HTTPException(status_code=500, detail=str(e))
