"""
ALEGRIA_OS — src/routes/nexus.py

REST API para NEXUS: autoridad suprema de clasificación y soberanía.

Rutas:
  GET  /nexus/context              → contexto/memoria reciente
  POST /nexus/classify             → clasifica un pedido
  POST /nexus/validate             → valida una acción contra las leyes
  GET  /nexus/laws                 → lista leyes del sistema
  GET  /nexus/lexicon              → léxico del usuario
  POST /nexus/lexicon              → agrega símbolo al léxico
  DELETE /nexus/lexicon/{symbol}   → elimina símbolo
  POST /nexus/session              → crea sesión
  GET  /nexus/session/{id}         → obtiene sesión
  POST /nexus/event                → registra evento semántico

Author: Sebastián Fernández
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.nexus import get_nexus

logger = logging.getLogger("NEXUS_ROUTES")

router = APIRouter(tags=["nexus"])


# ─── Schemas ──────────────────────────────────────────────────────────────────


class ClassifyRequest(BaseModel):
    message: str             = Field(..., description="Pedido del operador a clasificar")
    context: Optional[Dict[str, Any]] = Field(default=None)


class ValidateRequest(BaseModel):
    action:  str             = Field(..., description="Acción a validar")
    context: Optional[Dict[str, Any]] = Field(default=None)


class LexiconAddRequest(BaseModel):
    symbol:  str = Field(..., description="Símbolo cognitivo (ej: 'el limpio')")
    meaning: str = Field(..., description="Significado asignado por el usuario")
    context: str = Field(default="", description="Contexto de uso (opcional)")


class SessionCreateRequest(BaseModel):
    session_id: str                         = Field(..., description="ID único de sesión")
    metadata:   Optional[Dict[str, Any]]    = Field(default=None)


class EventRequest(BaseModel):
    event_type: str              = Field(..., description="Tipo de evento")
    data:       Dict[str, Any]   = Field(default_factory=dict)
    session_id: str              = Field(default="default")


# ─── Endpoints ────────────────────────────────────────────────────────────────


@router.get("/context")
async def get_context(session_id: str = "default", limit: int = 10) -> Dict[str, Any]:
    """
    Contexto/memoria reciente de una sesión.
    Si el MemoryOrchestrator completo está disponible, lo usa;
    si no, usa la memoria semántica liviana del NexusCore.
    """
    nexus = get_nexus()
    try:
        # Intentar usar el MemoryOrchestrator rico si está disponible
        if nexus.memory:
            history = nexus.memory.get_recent(limit)
            return {
                "context": [
                    {
                        "timestamp": e.timestamp,
                        "content":   e.content,
                        "source":    e.source,
                    }
                    for e in history
                ],
                "session_id": session_id,
            }
    except Exception:
        pass

    # Fallback: memoria semántica liviana del core
    events = nexus.core.get_context(session_id, limit)
    return {"context": events, "session_id": session_id}


@router.post("/classify")
async def classify_request(body: ClassifyRequest) -> Dict[str, Any]:
    """
    Clasifica un pedido del operador SIN DEDUCIR.

    Retorna:
     - type: productivo | exploratorio | tecnico | investigacion | visual | ambiguo
     - agent: el agente sugerido para manejar el pedido
     - confidence: high | medium | low
     - question: (solo si ambiguo) pregunta para aclarar
    """
    nexus  = get_nexus()
    result = nexus.classify_request(body.message, body.context)
    # Serializar el enum si viene como objeto
    if hasattr(result.get("type"), "value"):
        result["type"] = result["type"].value
    return result


@router.post("/validate")
async def validate_action(body: ValidateRequest) -> Dict[str, Any]:
    """
    Valida si una acción cumple con las leyes del sistema.
    NEXUS no ejecuta — solo dictamina.
    """
    nexus = get_nexus()
    return nexus.validate_action(body.action, body.context)


@router.get("/laws")
async def get_laws() -> Dict[str, Any]:
    """
    Lista todas las leyes del sistema.
    Las leyes fundamentales son visibles pero no editables.
    """
    nexus = get_nexus()
    return {"laws": nexus.get_laws()}


# ─── Léxico ───────────────────────────────────────────────────────────────────


@router.get("/lexicon")
async def get_lexicon() -> Dict[str, Any]:
    """Retorna el léxico completo del usuario."""
    nexus = get_nexus()
    return {"lexicon": nexus.get_lexicon()}


@router.post("/lexicon")
async def add_to_lexicon(body: LexiconAddRequest) -> Dict[str, Any]:
    """
    Agrega un símbolo al léxico del usuario.
    El lenguaje del usuario no se corrige — se registra tal cual.
    """
    nexus  = get_nexus()
    result = nexus.add_to_lexicon(body.symbol, body.meaning, body.context)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.delete("/lexicon/{symbol}")
async def remove_from_lexicon(symbol: str) -> Dict[str, Any]:
    """Elimina un símbolo del léxico del usuario."""
    nexus  = get_nexus()
    result = nexus.remove_from_lexicon(symbol)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


# ─── Sesiones ─────────────────────────────────────────────────────────────────


@router.post("/session")
async def create_session(body: SessionCreateRequest) -> Dict[str, Any]:
    """Crea una nueva sesión de operador."""
    nexus = get_nexus()
    return nexus.create_session(body.session_id, body.metadata)


@router.get("/session/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    """Obtiene los datos de una sesión activa."""
    nexus   = get_nexus()
    session = nexus.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Sesión '{session_id}' no encontrada")
    return {"session_id": session_id, "data": session}


# ─── Eventos semánticos ───────────────────────────────────────────────────────


@router.post("/event")
async def register_event(body: EventRequest) -> Dict[str, Any]:
    """Registra un evento en la memoria semántica de NEXUS."""
    nexus = get_nexus()
    nexus.register_event(body.event_type, body.data, body.session_id)
    return {"status": "ok", "event_type": body.event_type, "session_id": body.session_id}
