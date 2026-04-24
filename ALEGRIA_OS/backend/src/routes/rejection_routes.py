# -------------------------------------------------------------------------
# ALEGR-IA OS — Sistema Operativo de Coherencia Creativa
# Copyright (c) 2025 Sebastián Fernández & Antigravity AI.
# Todos los derechos reservados.
#
# Este código es CONFIDENCIAL y PROPIETARIO.
# Su copia, distribución o modificación no autorizada está penada por la ley.
# -------------------------------------------------------------------------

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from ..services.rejection_service import service as rejection_service

logger = logging.getLogger("ALEGRIA_API")

router = APIRouter(prefix="/api/rejections", tags=["rejections"])


# --- MODELOS PYDANTIC ---

class RejectionCreate(BaseModel):
    """Modelo para crear un nuevo rechazo."""
    type: str = Field(..., description="Tipo de rechazo: topic, behavior, style, content, language")
    description: str = Field(..., min_length=3, description="Descripción del rechazo")
    severity: str = Field(default="moderate", description="Severidad: strict, moderate, soft")
    active: bool = Field(default=True, description="Si el rechazo está activo")


class RejectionUpdate(BaseModel):
    """Modelo para actualizar un rechazo existente."""
    type: Optional[str] = Field(None, description="Tipo de rechazo")
    description: Optional[str] = Field(None, min_length=3, description="Descripción del rechazo")
    severity: Optional[str] = Field(None, description="Severidad")
    active: Optional[bool] = Field(None, description="Si el rechazo está activo")


class RejectionResponse(BaseModel):
    """Modelo de respuesta para un rechazo."""
    id: str
    type: str
    description: str
    severity: str
    active: bool
    created_at: str
    updated_at: Optional[str] = None


# --- ENDPOINTS ---

@router.get("", response_model=List[RejectionResponse])
async def get_rejections(user_id: str = "default"):
    """
    Obtiene todos los rechazos del usuario.
    
    Args:
        user_id: ID del usuario (default: "default")
        
    Returns:
        Lista de rechazos
    """
    try:
        rejections = await rejection_service.get_user_rejections(user_id)
        return rejections
    except Exception as e:
        logger.error(f"❌ [API] Error obteniendo rechazos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=RejectionResponse, status_code=201)
async def create_rejection(rejection: RejectionCreate, user_id: str = "default"):
    """
    Crea un nuevo rechazo para el usuario.
    
    Args:
        rejection: Datos del rechazo a crear
        user_id: ID del usuario (default: "default")
        
    Returns:
        El rechazo creado
    """
    try:
        new_rejection = await rejection_service.add_rejection(
            user_id=user_id,
            rejection_type=rejection.type,
            description=rejection.description,
            severity=rejection.severity,
            active=rejection.active
        )
        return new_rejection
    except ValueError as e:
        logger.warning(f"⚠️ [API] Validación fallida: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ [API] Error creando rechazo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{rejection_id}", response_model=RejectionResponse)
async def update_rejection(
    rejection_id: str,
    rejection: RejectionUpdate,
    user_id: str = "default"
):
    """
    Actualiza un rechazo existente.
    
    Args:
        rejection_id: ID del rechazo a actualizar
        rejection: Datos a actualizar
        user_id: ID del usuario (default: "default")
        
    Returns:
        El rechazo actualizado
    """
    try:
        # Convertir a diccionario solo con campos no-None
        updates = rejection.model_dump(exclude_none=True)
        
        updated_rejection = await rejection_service.update_rejection(
            user_id=user_id,
            rejection_id=rejection_id,
            updates=updates
        )
        
        if not updated_rejection:
            raise HTTPException(status_code=404, detail="Rechazo no encontrado")
        
        return updated_rejection
    except ValueError as e:
        logger.warning(f"⚠️ [API] Validación fallida: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [API] Error actualizando rechazo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{rejection_id}", status_code=204)
async def delete_rejection(rejection_id: str, user_id: str = "default"):
    """
    Elimina un rechazo.
    
    Args:
        rejection_id: ID del rechazo a eliminar
        user_id: ID del usuario (default: "default")
    """
    try:
        deleted = await rejection_service.delete_rejection(
            user_id=user_id,
            rejection_id=rejection_id
        )
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Rechazo no encontrado")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [API] Error eliminando rechazo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview/prompt")
async def get_rejection_prompt_preview(user_id: str = "default"):
    """
    Obtiene una vista previa del prompt de rechazos que se enviará al LLM.
    
    Args:
        user_id: ID del usuario (default: "default")
        
    Returns:
        Prompt de rechazos formateado
    """
    try:
        prompt = await rejection_service.build_rejection_prompt(user_id)
        
        return {
            "prompt": prompt,
            "has_rejections": bool(prompt.strip())
        }
    except Exception as e:
        logger.error(f"❌ [API] Error generando preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_rejection_types():
    """
    Obtiene los tipos de rechazos disponibles.
    
    Returns:
        Lista de tipos y severidades disponibles
    """
    from ..services.rejection_service import REJECTION_TYPES, SEVERITY_LEVELS
    
    return {
        "types": [
            {"value": "topic", "label": "Tema", "description": "Temas o áreas de conocimiento específicas"},
            {"value": "behavior", "label": "Comportamiento", "description": "Comportamientos o actitudes en las respuestas"},
            {"value": "style", "label": "Estilo", "description": "Estilos de escritura o comunicación"},
            {"value": "content", "label": "Contenido", "description": "Tipos de contenido específicos"},
            {"value": "language", "label": "Lenguaje", "description": "Uso de lenguaje o terminología"}
        ],
        "severities": [
            {"value": "strict", "label": "Estricto", "description": "Cumplimiento obligatorio"},
            {"value": "moderate", "label": "Moderado", "description": "Evitar en lo posible"},
            {"value": "soft", "label": "Suave", "description": "Preferencia del usuario"}
        ]
    }
