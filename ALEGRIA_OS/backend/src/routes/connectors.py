"""
ALEGRIA_OS — src/routes/connectors.py

REST API para el Panel de Conectores.

Rutas:
  GET    /connectors/           → lista todos los conectores
  GET    /connectors/active     → lista solo activos
  GET    /connectors/{id}       → detalle de un conector
  POST   /connectors/{id}/activate    → activa un conector
  POST   /connectors/{id}/deactivate  → desactiva un conector
  POST   /connectors/           → agrega un conector personalizado
  DELETE /connectors/{id}       → elimina un conector
  PATCH  /connectors/{id}/endpoint   → actualiza endpoint
  POST   /connectors/{id}/clone      → clona hacia nuevo id

Author: Sebastián Fernández
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("CONNECTORS_ROUTES")

router = APIRouter()


# ─── Schemas ──────────────────────────────────────────────────────────────────


class AddConnectorRequest(BaseModel):
    connector_id: str = Field(..., description="ID único del conector (ej: 'my_vision')")
    tipo: str        = Field(..., description="Tipo: chat|audio|vision|image|video|tools|memory|search|storage|publish")
    endpoint: str    = Field(..., description="URL o ruta lógica del conector")
    notas: str       = Field(default="", description="Descripción de uso")


class ActivateRequest(BaseModel):
    provider_id: Optional[str] = Field(
        default=None,
        description="ID del proveedor a vincular (opcional)"
    )


class UpdateEndpointRequest(BaseModel):
    endpoint: str = Field(..., description="Nueva URL o ruta del conector")


class CloneRequest(BaseModel):
    new_id: str = Field(..., description="ID para el clon")


# ─── Helper ───────────────────────────────────────────────────────────────────


def _get_registry():
    from src.services.connector_registry import get_connector_registry
    return get_connector_registry()


# ─── Endpoints ────────────────────────────────────────────────────────────────


@router.get("/", summary="Lista todos los conectores")
async def list_all() -> Dict[str, Any]:
    """Retorna el estado completo del Panel de Conectores."""
    return {
        "connectors": _get_registry().list_all(),
        "total": len(_get_registry().connectors),
    }


@router.get("/active", summary="Lista conectores activos")
async def list_active() -> Dict[str, Any]:
    """Retorna solo los conectores en estado ACTIVE."""
    activos = _get_registry().list_active()
    return {"connectors": activos, "total": len(activos)}


@router.get("/{connector_id}", summary="Detalle de un conector")
async def get_connector(connector_id: str) -> Dict[str, Any]:
    """Retorna el detalle de un conector específico."""
    conn = _get_registry().get_connector(connector_id)
    if not conn:
        raise HTTPException(status_code=404, detail=f"Conector '{connector_id}' no encontrado")
    from dataclasses import asdict
    return {**asdict(conn), "tipo": conn.tipo.value, "estado": conn.estado.value}


@router.post("/{connector_id}/activate", summary="Activa un conector")
async def activate(connector_id: str, body: ActivateRequest = None) -> Dict[str, Any]:
    """
    Activa el conector especificado.
    Opcionalmente vincula al proveedor activo.
    """
    provider_id = body.provider_id if body else None
    result = _get_registry().activate(connector_id, provider_id=provider_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.post("/{connector_id}/deactivate", summary="Desactiva un conector")
async def deactivate(connector_id: str) -> Dict[str, Any]:
    """Desactiva el conector especificado."""
    result = _get_registry().deactivate(connector_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.post("/", summary="Agrega un conector personalizado")
async def add_connector(body: AddConnectorRequest) -> Dict[str, Any]:
    """
    Agrega un nuevo conector al Panel.
    Tipos válidos: chat, audio, vision, image, video, tools, memory, search, storage, publish.
    """
    result = _get_registry().add_connector(
        connector_id=body.connector_id,
        tipo=body.tipo,
        endpoint=body.endpoint,
        notas=body.notas,
    )
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.delete("/{connector_id}", summary="Elimina un conector")
async def remove_connector(connector_id: str) -> Dict[str, Any]:
    """Elimina permanentemente un conector del Panel."""
    result = _get_registry().remove_connector(connector_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.patch("/{connector_id}/endpoint", summary="Actualiza el endpoint de un conector")
async def update_endpoint(connector_id: str, body: UpdateEndpointRequest) -> Dict[str, Any]:
    """Actualiza la dirección (endpoint) de un conector existente."""
    result = _get_registry().update_endpoint(connector_id, body.endpoint)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.post("/{connector_id}/clone", summary="Clona un conector")
async def clone_connector(connector_id: str, body: CloneRequest) -> Dict[str, Any]:
    """
    Clona un conector existente bajo un nuevo ID.
    El clon empieza INACTIVE — activarlo es decisión del operador.
    """
    result = _get_registry().clone_connector(connector_id, body.new_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result
